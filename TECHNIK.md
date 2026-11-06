# Technik

[← Zurück zur Übersicht](README.md)

- [Aufbau](#aufbau)
- [Gestaltung](#gestaltung)
- [Kacheln aus der Städteliste](#kacheln-aus-der-städteliste)
- [Sicherheit und Datenschutz](#sicherheit-und-datenschutz)
- [Workflows](#workflows)
- [Deployment](#deployment)
- [Prüfung](#prüfung)
- [Lokal ansehen](#lokal-ansehen)

## Aufbau

```
ratsatlas/
├── site/                  ausgelieferte Dateien (relativ verlinkt)
│   ├── index.html         Startseite; Kacheln und JSON-LD aus staedte.json
│   ├── datenschutz.html
│   ├── 404.html           wurzelrelative Pfade, weil unter beliebigen Adressen ausgeliefert
│   ├── tokens.css         gemeinsame Gestaltungsgrößen des Kerns
│   ├── style.css          Seitenlayout, Kacheln, Textseiten
│   ├── fonts/             Inter (variabel, woff2) mit Lizenzdatei
│   ├── vorschau/          Vorschaubilder der Kacheln
│   ├── partner/           Logo Offene Kommunen.NRW (Farben als Attribute, wegen CSP)
│   └── …                  Favicons, App-Symbole, site.webmanifest, robots.txt, sitemap.xml
├── staedte.json           Städteliste
├── scripts/
│   ├── kacheln.py         schreibt Kacheln und JSON-LD; --pruefen für CI
│   ├── sitemap.py         schreibt sitemap.xml mit lastmod aus der Git-Historie (im Workflow)
│   ├── og_bild.py         erzeugt site/og-image.png aus og-bild.html (von Hand, Playwright)
│   └── live_pruefen.sh    prüft die ausgelieferte Seite
├── deploy/
│   ├── htaccess           wird im Branch deploy zu .htaccess
│   ├── nginx-zusatz.conf  Alternative, falls nginx die .htaccess umgeht
│   └── CHECKLISTE.md      Einrichtung in Plesk, DNS und GitHub
├── pruefung.tsv           Prüfprotokoll
├── pruefung/              Bildschirmfotos der Prüfung
└── .github/workflows/     pruefen.yml, veroeffentlichen.yml, live.yml
```

Die Pfade in `site/` sind durchgehend relativ, damit dieselben Dateien unter `ratsatlas.de/` und unter `daimpad.github.io/ratsatlas/` funktionieren. Einzige Ausnahme ist `404.html`.

## Gestaltung

Die Gestaltung stammt aus der RIS-Karte Bonn ([allris-test](https://github.com/daimpad/allris-test), `site/style.css` und `site/page.css`), kopiert und nicht verlinkt. `site/tokens.css` fasst die gemeinsamen Größen zusammen und ist die maßgebliche Quelle für die Stadtinstanzen:

| Größe | Wert | Verwendung |
|---|---|---|
| `--bg` + `--bg-gradient` | `#fafaff`, drei radiale Verläufe (rosa, hellblau, lavendel) | Seitenhintergrund |
| `--surface-strong` | `rgba(255,255,255,0.85)`, `blur(20px) saturate(160%)` | Glasflächen; Fallback ohne `backdrop-filter` |
| `--text` / `--text-muted` | `#0f0f14` / `#5a5a68` | Text |
| `--accent-ink` / `--accent-fill` | `#6d28d9` / `#7c3aed` | Links, Wortmarke, Fokusrahmen (statt `#8b5cf6`, wegen WCAG-AA-Kontrast) |
| `--cta` | Verlauf `#7c3aed → #5b21b6`, 135° | Schaltflächen |
| `--ok` / `--warn` | `#1f7a4d` / `#9a5200` | Status „Online“ / „In Vorbereitung“ |

Maßsystem in `tokens.css`: Schriftskala mit sieben Stufen (`--text-xs` bis `--text-3xl`), Abstände im 4-px-Raster (`--space-1` bis `--space-8`), Radien (`--radius-s`, `--radius`, `--radius-pill`), Mindestgröße für Bedienflächen `--tap` (44 px); `style.css` verwendet nur diese Werte. Mobile First: Grundregeln für das Telefon, Erweiterungen ab 720 px (Tablet: Karten zweispaltig, Stadt-Kachel waagerecht) und 1000 px (Desktop: Stadt-Grafik neben dem Einstieg, Schritte als Zeitstrahl). Auf dem Telefon ist die Sprungleiste einzeilig und waagerecht scrollbar. Nur helles Farbschema (`color-scheme: light`), Schrift Inter mit `font-display: swap`. Bei `prefers-reduced-motion` entfallen Anhebung und Pfeilbewegung.

## Kacheln aus der Städteliste

`scripts/kacheln.py` (nur Standardbibliothek) liest `staedte.json`, prüft Pflichtfelder, Status, `https`-Adresse und vorhandene Bilder und ersetzt in `site/index.html` den Inhalt zwischen den Markierungen `kacheln:anfang/ende` und `jsonld:anfang/ende`.

- `online` → Kachel mit Bild, Angaben und Knopf „<Titel> öffnen“; der Knopf ist der einzige Link und deckt die ganze Kachel ab (`.kachel-knopf::after`)
- `in Vorbereitung` → schmale Zeile ohne Link und ohne Bildfläche, Status als Text, nicht nur als Farbe
- JSON-LD `WebSite` mit `hasPart` nur für Städte mit Status `online`

`python3 scripts/kacheln.py --pruefen` endet mit Fehlercode 1, wenn das HTML nicht zur Liste passt.

## Sicherheit und Datenschutz

Content-Security-Policy, als `<meta>` in jeder Seite und als Kopfzeile aus `.htaccess` (dort zusätzlich `frame-ancestors 'none'`):

```
default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:;
object-src 'none'; base-uri 'self'; form-action 'none'
```

Weitere Kopfzeilen aus `deploy/htaccess`: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (Kamera, Mikrofon, Standort, Zahlung, USB, Topics aus), `Strict-Transport-Security: max-age=31536000` (ohne `includeSubDomains`, weil die Subdomains eigenständig betrieben werden). Dazu Weiterleitung `www` → `ratsatlas.de`, Caching für Schrift und Bilder, `ErrorDocument 404`, `.git` gesperrt.

Keine Cookies, kein lokaler Speicher, keine Anfragen an fremde Server. Die Datenschutzerklärung steht unter [`site/datenschutz.html`](site/datenschutz.html).

## Workflows

| Datei | Auslöser | Jobs |
|---|---|---|
| `pruefen.yml` | Pull Request | `kacheln`: `scripts/kacheln.py --pruefen` |
| `veroeffentlichen.yml` | Push auf `main`, manuell | `pruefen` → `deploy` (Sitemap mit `lastmod`, neuer Commit auf dem Branch `deploy`, mit `.htaccess` und `version.txt`) und `pages` (GitHub Pages aus `site/`, ohne `.htaccess`, jede Seite mit `noindex`) |
| `live.yml` | manuell | `scripts/live_pruefen.sh https://ratsatlas.de` (auch: Stand von `version.txt` = Branch `deploy`), Ergebnis in der Zusammenfassung des Laufs |

Alle Actions sind auf Commit-Hashes festgelegt; Schreibrechte gelten nur in den Jobs, die sie brauchen.

## Suchmaschinen

- Eine Adresse je Seite: `/index.html` leitet mit 301 auf `/` (`.htaccess`), `www` auf `ratsatlas.de`; Canonical in jeder Seite.
- Die Ausweichadresse auf GitHub Pages trägt `noindex` (gesetzt im Workflow), damit sie nicht mit ratsatlas.de konkurriert.
- `sitemap.xml` mit `lastmod` je Seite, erzeugt von `scripts/sitemap.py` im Workflow; `robots.txt` verweist darauf.
- Vorschau für geteilte Links: `og-image.png` (1200 × 630), Twitter-Karte `summary_large_image`.
- JSON-LD `WebSite` mit `publisher` (Damian Paderta), `sponsor` (Offene Kommunen.NRW), `about` und `hasPart` (Städte mit Status `online`).
- Keine Reichweitenmessung; Auswertung über Google Search Console (Domain-Eigenschaft) und Bing Webmaster Tools.

## Deployment

```
main ──► Seite veröffentlichen ──► Branch deploy ──(Webhook)──► Plesk-Git ──► httpdocs ──► ratsatlas.de
                              └──► GitHub Pages ─────────────────────────────────────────► daimpad.github.io/ratsatlas
```

Einrichtung Schritt für Schritt: [`deploy/CHECKLISTE.md`](deploy/CHECKLISTE.md). Befunde vom 04.11.2026:

- In Plesk muss **„Intelligente Bearbeitung statischer Dateien“** aus sein (Proxymodus bleibt an). Sonst liefert nginx die Dateien selbst aus, und Kopfzeilen wie Weiterleitungen aus `.htaccess` fehlen bei GET – HEAD-Anfragen zeigen sie trotzdem. Daher prüft `live_pruefen.sh` mit GET.
- „Bevorzugte Domain“ ist in Plesk nicht wählbar; die Weiterleitung von `www` steht deshalb in `.htaccess`.
- Der Webhook-Abruf von Plesk übernimmt nur Stände, die an den vorhandenen anschließen: Bei einem ohne Historie neu geschriebenen Branch (Force-Push) antwortete Plesk mit 204, rief aber nicht ab. `deploy` wird deshalb fortlaufend geschrieben. Nur „Jetzt Pull ausführen“ von Hand übernimmt auch unverbundene Stände.
- `version.txt` enthält den Commit von `main`; die Live-Prüfung vergleicht `https://ratsatlas.de/version.txt` mit dem Branch `deploy` und meldet einen nicht abgeholten Stand.
- Nur ein Workflow darf an GitHub Pages ausliefern; die GitHub-Vorlage „Static HTML“ würde das ganze Repository veröffentlichen.

## Prüfung

| Bereich | Werkzeug |
|---|---|
| Barrierefreiheit | axe-core 4.10.3 über Playwright/Chromium, Regeln WCAG 2.0/2.1 A und AA und Best Practice; Kontraste nach WCAG nachgerechnet |
| Tastatur, Fokus, reduzierte Bewegung | Playwright |
| HTML und CSS | Nu Html Checker (vnu-jar 24.10.17) |
| Links | lychee 0.18.1 |
| Ausgelieferte Seite | `scripts/live_pruefen.sh` (curl mit GET, openssl) |

Ergebnisse mit Datum in [`pruefung.tsv`](pruefung.tsv), Bildschirmfotos bei 360, 768 und 1280 px in [`pruefung/`](pruefung/).

## Lokal ansehen

```bash
python3 -m http.server 8000 --directory site
```

Danach `http://localhost:8000/` öffnen. Ein Build-Schritt ist nicht nötig; nach Änderungen an `staedte.json`:

```bash
python3 scripts/kacheln.py
```
