# bwl.hockey

Statische Website für die Baden-Württemberg Liga Eishockey. Instagram-Posts
werden über eine einfache Link-Liste live eingebettet. Tabellen/Spielplan
folgen später.

## Wie das Posten funktioniert

1. Instagram-Post-Link in `posts.txt` eintragen — eine URL pro Zeile,
   optional `| Team | Titel` anhängen, z.B.:
   ```
   https://www.instagram.com/p/ABC123/ | SERC04 Firewings | Kaderupdate: Adam Spurny
   ```
2. Commit/Push nach `main` (oder direkt im GitHub-Webinterface editieren).
3. Die GitHub Action `publish-from-links.yml` erkennt den neuen Link, holt
   das offizielle Embed-HTML per Instagram-oEmbed und legt einen Blogpost
   in `_posts/` an.
4. GitHub Pages baut neu — der Post ist online, das eingebettete Bild wird
   beim Seitenaufruf live von Instagram geladen.

### Warum "live eingebettet" statt "heruntergeladen"?

Ursprünglich war geplant, Bild und Caption herunterzuladen und selbst zu
hosten. Das funktioniert nicht mehr:

- **Technisch:** Seit dem 3.11.2025 liefert die oEmbed-API `thumbnail_url`
  und `author_name` gar nicht mehr zurück — dauerhaft entfernt.
- **Rechtlich:** Instagrams oEmbed-Nutzungsbedingungen verbieten es
  ausdrücklich, Bild/Text dauerhaft zu speichern ("persisting the
  metadata and media content" ist untersagt) — erlaubt ist nur eine
  Live-Einbettung.

Die Live-Einbettung (offizielles `<blockquote>` + `embed.js`, seit
15.06.2026 tokenless nutzbar) ist deshalb der einzige zuverlässige und
regelkonforme Weg. Titel/Team tragt ihr von Hand in `posts.txt` ein, da
die Caption nicht mehr automatisch abrufbar ist.

## Setup

### 1. GitHub Pages

1. Repo unter GitHub anlegen, diesen Ordner pushen.
2. Settings → Pages → Source: "Deploy from a branch" → `main` / `/ (root)`.
   Jekyll wird von GitHub Pages automatisch gebaut (siehe `Gemfile`).
3. Settings → Pages → Custom domain: `bwl.hockey` eintragen (liest die
   `CNAME`-Datei automatisch mit). "Enforce HTTPS" aktivieren, sobald das
   Zertifikat ausgestellt wurde.

**Hinweis Vorschau-URL:** Solange die Custom Domain noch nicht via
Cloudflare-DNS aktiv ist, läuft die Vorschau unter
`https://<user>.github.io/<repo>/` (Projekt-Unterpfad). `_config.yml`
ist aktuell auf die künftige Root-Domain (`baseurl: ""`) eingestellt —
das passt automatisch, sobald `bwl.hockey` live ist.

### 2. Cloudflare DNS

Bei Cloudflare für `bwl.hockey`:

- 4x `A`-Record auf die GitHub-Pages-IPs:
  `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- Optional `www` als `CNAME` auf `<dein-github-user>.github.io`
- **Wichtig:** Proxy-Status auf "DNS only" (graue Wolke) stellen, bis das
  GitHub-Zertifikat ausgestellt ist — sonst schlägt die Zertifikatsprüfung
  bei GitHub fehl.

### 3. Posts hinzufügen

Einfach `posts.txt` bearbeiten und pushen — siehe oben. Kein weiteres
Setup nötig.

## Struktur

```
posts.txt                     hier tragt ihr neue Instagram-Links ein
_config.yml                   Jekyll-Konfiguration
Gemfile                       Ruby-Abhängigkeiten für den GitHub-Pages-Build
index.md                      Startseite, listet alle Posts
_layouts/default.html         Basislayout, bindet embed.js einmalig ein
_posts/                       wird automatisch von der Action befüllt
_data/processed_posts.json    merkt sich bereits verarbeitete Links
scripts/publish_from_links.py holt das Embed-HTML per oEmbed und erzeugt den Post
.github/workflows/            GitHub Action, die bei Änderung an posts.txt läuft
```
