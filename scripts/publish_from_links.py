#!/usr/bin/env python3
"""
Liest posts.txt (eine Instagram-Post-URL pro Zeile, optional "| Team"),
prüft gegen _data/processed_posts.json, welche Links neu sind, holt für
diese per Instagram-oEmbed (seit 15.06.2026 tokenless, kein Meta-App/Token
nötig) das Vorschaubild + Caption und legt daraus einen Jekyll-Post in
_posts/ an. Das Bild wird lokal ins Repo heruntergeladen, damit die Seite
nicht von ablaufenden Instagram-CDN-Links abhängt.

Wichtig (Meta-Vorgabe): wer statt des vollen oEmbed-<blockquote>-Embeds
nur das thumbnail_url-Bild separat anzeigt, muss klar auf den
Original-Autor + Instagram + den Original-Post verlinken. Das übernimmt
dieses Skript automatisch in der Post-Fußzeile.
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
IMAGES_DIR = REPO_ROOT / "assets" / "instagram"
PROCESSED_FILE = REPO_ROOT / "_data" / "processed_posts.json"


def load_links() -> list[tuple[str, str]]:
    """Gibt Liste von (url, team) zurück; team ist '' wenn nicht angegeben."""
    if not POSTS_TXT.exists():
        return []
    links = []
    for line in POSTS_TXT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            url, team = line.split("|", 1)
            links.append((url.strip(), team.strip()))
        else:
            links.append((line, ""))
    return links


def load_processed() -> set[str]:
    if PROCESSED_FILE.exists():
        return set(json.loads(PROCESSED_FILE.read_text()).get("processed_urls", []))
    return set()


def save_processed(urls: set[str]) -> None:
    PROCESSED_FILE.write_text(
        json.dumps({"processed_urls": sorted(urls)}, indent=2, ensure_ascii=False) + "\n"
    )


def fetch_oembed(post_url: str) -> dict:
    query = urllib.parse.urlencode({"url": post_url, "omitscript": "true"})
    with urllib.request.urlopen(f"{OEMBED_ENDPOINT}?{query}") as resp:
        return json.load(resp)


def extract_post_id(post_url: str) -> str:
    match = re.search(r"/(p|reel|tv)/([\w-]+)", post_url)
    return match.group(2) if match else re.sub(r"\W+", "-", post_url)[:40]


def download_image(image_url: str, dest: Path) -> None:
    req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        dest.write_bytes(resp.read())


def build_post(post_url: str, team: str, oembed: dict, post_id: str, image_rel_path: str) -> str:
    author = oembed.get("author_name", "")
    caption = (oembed.get("title") or "").strip()
    today = date.today().isoformat()

    title = caption.splitlines()[0] if caption else f"Instagram-Post von {author or 'BWL'}"
    title = title.replace('"', "'")[:100]

    front_matter = [
        "---",
        "layout: default",
        f'title: "{title}"',
        f'team: "{team}"',
        f'source_author: "{author}"',
        f'instagram_permalink: "{post_url}"',
        "---",
        "",
    ]

    body = [f"![]({image_rel_path})", ""]
    if caption:
        body.append(caption)
        body.append("")
    body.append(f"*Repost von [@{author}]({post_url}) auf Instagram — [Original-Post ansehen]({post_url})*")

    return "\n".join(front_matter + body)


def main() -> None:
    links = load_links()
    processed = load_processed()

    new_links = [(url, team) for url, team in links if url not in processed]
    if not new_links:
        print("Keine neuen Links in posts.txt.")
        return

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    POSTS_DIR.mkdir(exist_ok=True)

    for url, team in new_links:
        post_id = extract_post_id(url)
        try:
            oembed = fetch_oembed(url)
        except Exception as exc:  # noqa: BLE001
            print(f"Fehler bei {url}: {exc}", file=sys.stderr)
            continue

        thumbnail_url = oembed.get("thumbnail_url")
        image_rel_path = ""
        if thumbnail_url:
            image_filename = f"{post_id}.jpg"
            download_image(thumbnail_url, IMAGES_DIR / image_filename)
            image_rel_path = f"/assets/instagram/{image_filename}"

        content = build_post(url, team, oembed, post_id, image_rel_path)
        filename = f"{date.today().isoformat()}-{post_id}.md"
        (POSTS_DIR / filename).write_text(content, encoding="utf-8")
        print(f"Neuer Post angelegt: {filename}")

        processed.add(url)

    save_processed(processed)


if __name__ == "__main__":
    main()
