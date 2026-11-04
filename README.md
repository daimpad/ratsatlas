<div align="center">

<img src="site/favicon.svg" width="72" height="72" alt="">

# Ratsatlas

**Öffentliche Vorlagen aus kommunalen Ratsinformationssystemen – räumlich, zeitlich und nach Gremien und Ämtern erschlossen.**

[ratsatlas.de](https://ratsatlas.de) · [Technik](TECHNIK.md) · [Prüfprotokoll](pruefung.tsv)

[![Seite veröffentlichen](https://github.com/daimpad/ratsatlas/actions/workflows/veroeffentlichen.yml/badge.svg)](https://github.com/daimpad/ratsatlas/actions/workflows/veroeffentlichen.yml)
[![Prüfen](https://github.com/daimpad/ratsatlas/actions/workflows/pruefen.yml/badge.svg)](https://github.com/daimpad/ratsatlas/actions/workflows/pruefen.yml)
[![Live-Prüfung](https://github.com/daimpad/ratsatlas/actions/workflows/live.yml/badge.svg)](https://github.com/daimpad/ratsatlas/actions/workflows/live.yml)
[![ratsatlas.de](https://img.shields.io/website?url=https%3A%2F%2Fratsatlas.de&label=ratsatlas.de&up_message=online&down_message=nicht%20erreichbar)](https://ratsatlas.de)

[![Lizenz: MIT](https://img.shields.io/github/license/daimpad/ratsatlas?label=Code)](LICENSE)
[![Schrift: SIL OFL 1.1](https://img.shields.io/badge/Schrift-Inter%20%C2%B7%20SIL%20OFL%201.1-6d28d9)](site/fonts/LICENSE-Inter.txt)
[![WCAG 2.1 AA geprüft](https://img.shields.io/badge/WCAG%202.1%20AA-gepr%C3%BCft%20mit%20axe--core-1f7a4d)](pruefung.tsv)
![Tracking: keins](https://img.shields.io/badge/Tracking-keins-1f7a4d)
![Cookies: keine](https://img.shields.io/badge/Cookies-keine-1f7a4d)
![JavaScript: keins](https://img.shields.io/badge/JavaScript-keins-1f7a4d)

<br>

<a href="https://ratsatlas.de"><img src="docs/startseite.webp" width="860" alt="Startseite ratsatlas.de: Einleitung und zwei Kacheln, Ratsatlas Bonn (online) und Ratsatlas Köln (in Vorbereitung)"></a>

</div>

## Worum es geht

Der Ratsatlas erschließt öffentliche Vorlagen aus kommunalen Ratsinformationssystemen räumlich, zeitlich und nach beteiligten Gremien und Ämtern. Jede Angabe ist auf ihre Quelle im Ratsinformationssystem rückführbar; abgeleitete Informationen sind gekennzeichnet.

Dieses Repository ist der **gemeinsame Kern**: Es trägt die Startseite [ratsatlas.de](https://ratsatlas.de) und die Gestaltungsgrößen (`site/tokens.css`), Schrift und Symbole, die die Stadtinstanzen übernehmen. Jede Stadt läuft unter einer eigenen Subdomain aus einem eigenen Repository.

## Städte

| Stadt | Adresse | Datenquelle | Repository | Status |
|---|---|---|---|---|
| Bonn | [bonn.ratsatlas.de](https://bonn.ratsatlas.de) | OParl-Schnittstelle der Stadt Bonn | [daimpad/allris-test](https://github.com/daimpad/allris-test) | ![online](https://img.shields.io/badge/-online-1f7a4d) |
| Köln | koeln.ratsatlas.de | OParl-Schnittstelle der Stadt Köln | offen | ![in Vorbereitung](https://img.shields.io/badge/-in%20Vorbereitung-9a5200) |

## Vom Commit zur Seite

Jede Änderung durchläuft dieselben Stationen. Die Badges oben zeigen den aktuellen Zustand jeder Station.

```mermaid
flowchart LR
    PR["Pull Request"] -->|Prüfen| P{"Kacheln =<br>staedte.json?"}
    P -->|ja| M["main"]
    M --> V["Seite veröffentlichen"]
    V -->|Branch deploy<br>mit .htaccess| D["netcup / Plesk<br>(Webhook)"]
    V -->|site/| G["GitHub Pages<br>(Ausweichadresse)"]
    D --> R(["ratsatlas.de"])
    G --> A(["daimpad.github.io/ratsatlas"])
    L["Live-Prüfung<br>(auf Knopfdruck)"] -.->|Status, Kopfzeilen, Weiterleitungen,<br>Zertifikat, version.txt| R
```

| Workflow | Wann | Was er prüft oder tut |
|---|---|---|
| **Prüfen** | jeder Pull Request | Kacheln und JSON-LD in `site/index.html` entsprechen `staedte.json` |
| **Seite veröffentlichen** | jeder Push auf `main` | prüft erneut, schreibt `site/` als Branch `deploy` für das Webhosting und liefert an GitHub Pages aus |
| **Live-Prüfung** | auf Knopfdruck | Status 200, fünf Sicherheitskopfzeilen, Weiterleitungen von `http` und `www`, eigene 404-Seite, Zertifikat und ob `ratsatlas.de/version.txt` dem Branch `deploy` entspricht |

## Eine Stadt hinzufügen

1. Eintrag in [`staedte.json`](staedte.json) ergänzen – Status `in Vorbereitung` ergibt eine Kachel ohne Link, `online` eine verlinkte Kachel.
2. `python3 scripts/kacheln.py` ausführen; das Skript schreibt Kacheln und JSON-LD in `site/index.html`.
3. Pull Request öffnen – „Prüfen“ stellt sicher, dass HTML und Liste übereinstimmen.

## Grundsätze

- **Ohne Tracking und ohne fremde Server:** keine Cookies, keine Reichweitenmessung, keine CDN; auch die Schrift liegt auf dem eigenen Server.
- **Barrierearm:** axe-core ohne Verstöße bei 360, 768 und 1280 px, Kontraste nachgerechnet, vollständig per Tastatur bedienbar, Rücksicht auf reduzierte Bewegung.
- **Klein:** rund 65 KB ohne Vorschaubild, kein JavaScript, kein Build-Werkzeug.
- **Nachvollziehbar:** jede Prüfung mit Werkzeug, Erwartung und Ergebnis in [`pruefung.tsv`](pruefung.tsv).

Aufbau, Sicherheitskopfzeilen, Deployment und Prüfwerkzeuge im Einzelnen: **[TECHNIK.md](TECHNIK.md)**.

## Lizenzen

Code unter [MIT](LICENSE) · Schrift Inter unter [SIL Open Font License 1.1](site/fonts/LICENSE-Inter.txt) · [Impressum](https://nozilla.de/impressum/) · [Datenschutz](https://ratsatlas.de/datenschutz.html)
