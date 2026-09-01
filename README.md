# bwl.hockey

Statische Website für die Baden-Württemberg Liga Eishockey. Instagram-Posts
werden über eine einfache Link-Liste eingebunden. Tabellen/Spielplan folgen
später.

## Wie das Posten funktioniert

1. Interessanten Instagram-Post-Link in `posts.txt` eintragen (eine URL pro
   Zeile, optional `| Teamname` anhängen).
2. Commit/Push nach `main` (oder direkt im GitHub-Webinterface editieren).
3. Die GitHub Action `publish-from-links.yml` läuft automatisch an,
   erkennt den neuen Link, holt Bild + Caption per Instagram-oEmbed und
   legt einen Blogpost in `_posts/` an.
4. GitHub Pages baut danach automatisch neu — der Post ist online.

Kein Instagram-Account, keine Meta-App, kein Token nötig: Seit dem
15.06.2026 ist die Instagram-oEmbed-API für öffentliche Posts tokenless
nutzbar (Meta hat die 2020 eingeführte Token-Pflicht wieder aufgehoben).

## Setup

### 1. GitHub Pages

1. Repo unter GitHub anlegen, diesen Ordner pushen.
2. Settings → Pages → Source: "Deploy from a branch" → `main` / `/ (root)`.
   Jekyll wird von GitHub Pages automatisch gebaut (siehe `Gemfile`).
3. Settings → Pages → Custom domain: `bwl.hockey` eintragen (liest die
   `CNAME`-Datei automatisch mit). "Enforce HTTPS" aktivieren, sobald das
   Zertifikat ausgestellt wurde.

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

## Rechtlicher Hinweis

Die Posts werden nicht 1:1 als Instagram-Embed eingebettet, sondern das
Vorschaubild wird heruntergeladen und selbst gehostet. Meta verlangt in
diesem Fall eine klare Zuordnung zum Original — das Skript ergänzt
deshalb automatisch einen Hinweis "Repost von @Account — Original-Post
ansehen" mit Link zurück zu Instagram unter jedem Post. Bei den Teams
kurz Bescheid geben, dass ihr ihre öffentlichen Posts auf diese Weise
verwendet, ist trotzdem empfehlenswert.

## Struktur

```
posts.txt                     hier tragt ihr neue Instagram-Links ein
_config.yml                   Jekyll-Konfiguration
Gemfile                       Ruby-Abhängigkeiten für den GitHub-Pages-Build
index.md                      Startseite, listet alle Posts
_layouts/default.html         Basislayout
_posts/                       wird automatisch von der Action befüllt
assets/instagram/             heruntergeladene Post-Bilder
_data/processed_posts.json    merkt sich bereits verarbeitete Links
scripts/publish_from_links.py holt Bild+Text per oEmbed und erzeugt den Post
.github/workflows/            GitHub Action, die bei Änderung an posts.txt läuft
```
