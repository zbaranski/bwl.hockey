#!/usr/bin/env python3
"""
Liest posts.txt (Instagram-Post-URL, optional "| Team | Titel"), prüft
gegen _data/processed_posts.json und legt für neue Links einen Jekyll-Post
an, der den Post per offiziellem Instagram-oEmbed-HTML LIVE einbettet.

Wichtig: seit 03.11.2025 liefert die oEmbed-API kein thumbnail_url/
author_name mehr, und Instagrams oEmbed-Nutzungsbedingungen verbieten es
ausdrücklich, Bild/Text dauerhaft zu speichern ("persisting the metadata
and media content" ist untersagt) – erlaubt ist nur eine Live-Einbettung.
Deshalb: kein Bild-Download mehr, stattdessen das offizielle Embed-HTML
(<blockquote> + embed.js, das den Post beim Seitenaufruf live lädt).
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

OEMBED_ENDPOINT = "https://graph.facebook.com/v25.0/instagram_oembed"

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_TXT = REPO_ROOT / "posts.txt"
POSTS_DIR = REPO_ROOT / "_posts"
PROCESSED_FILE = REPO_ROOT / "_data" / "processed_posts.json"


def load_links() -> list[tuple[str, str, str]]:
    """Gibt Liste von (url, team, titel) zurück; leer wenn nicht angegeben."""
    if not POSTS_TXT.exists():
        return []
    links = []
    for line in POSTS_TXT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        url = parts[0]
        team = parts[1] if len(parts) > 1 else ""
        titel = parts[2] if len(parts) > 2 else ""
        links.append((url, team, titel))
    return links


def load_processed() -> set[str]:
    if PROCESSED_FILE.exists():
        return set(json.loads(PROCESSED_FILE.read_text()).get("processed_urls", []))
    return set()


def save_processed(urls: set[str]) -> None:
    PROCESSED_FILE.write_text(
        json.dumps({"processed_urls": sorted(urls)}, indent=2, ensure_ascii=False) + "\n"
    )


def fetch_oembed_html(post_url: str) -> str:
    """Holt nur das offizielle Embed-HTML (funktioniert weiterhin tokenless)."""
    query = urllib.parse.urlencode({"url": post_url, "omitscript": "true"})
    with urllib.request.urlopen(f"{OEMBED_ENDPOINT}?{query}") as resp:
        data = json.load(resp)
    return data.get("html", "")


def extract_post_id(post_url: str) -> str:
    match = re.search(r"/(p|reel|tv)/([\w-]+)", post_url)
    return match.group(2) if match else re.sub(r"\W+", "-", post_url)[:40]


def build_post(post_url: str, team: str, titel: str, embed_html: str, post_id: str) -> str:
    title = titel or f"Instagram-Post{f' – {team}' if team else ''}"
    title = title.replace('"', "'")[:100]

    front_matter = [
        "---",
        "layout: default",
        f'title: "{title}"',
        f'team: "{team}"',
        f'instagram_permalink: "{post_url}"',
        "---",
        "",
    ]

    # Rohes Embed-HTML direkt einbetten — embed.js (im Layout eingebunden)
    # rendert Bild+Caption beim Seitenaufruf live von Instagram.
    body = [embed_html, ""]

    return "\n".join(front_matter + body)


def main() -> None:
    links = load_links()
    processed = load_processed()

    new_links = [(url, team, titel) for url, team, titel in links if url not in processed]
    if not new_links:
        print("Keine neuen Links in posts.txt.")
        return

    POSTS_DIR.mkdir(exist_ok=True)

    for url, team, titel in new_links:
        post_id = extract_post_id(url)
        try:
            embed_html = fetch_oembed_html(url)
        except Exception as exc:  # noqa: BLE001
            print(f"Fehler bei {url}: {exc}", file=sys.stderr)
            continue

        if not embed_html:
            print(f"Kein Embed-HTML für {url} erhalten — übersprungen.", file=sys.stderr)
            continue

        content = build_post(url, team, titel, embed_html, post_id)
        filename = f"{date.today().isoformat()}-{post_id}.md"
        (POSTS_DIR / filename).write_text(content, encoding="utf-8")
        print(f"Neuer Post angelegt: {filename}")

        processed.add(url)

    save_processed(processed)


if __name__ == "__main__":
    main()
