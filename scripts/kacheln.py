#!/usr/bin/env python3
"""Schreibt die Städte-Kacheln und das JSON-LD aus staedte.json in site/index.html.

Aufruf:
  python3 scripts/kacheln.py            # index.html aktualisieren
  python3 scripts/kacheln.py --pruefen  # nur prüfen; Fehlercode 1, wenn index.html veraltet ist

Nur Standardbibliothek. Ersetzt den Inhalt zwischen den Markierungen
<!-- kacheln:anfang ... --> / <!-- kacheln:ende --> und <!-- jsonld:anfang ... --> / <!-- jsonld:ende -->.
"""
import html
import json
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
STAEDTE = WURZEL / "staedte.json"
INDEX = WURZEL / "site" / "index.html"
SITE_URL = "https://ratsatlas.de/"

STATUS = {
    "online": ("Online", "status-online"),
    "in Vorbereitung": ("In Vorbereitung", "status-vorbereitung"),
}
PFLICHT = ("id", "titel", "url", "adresse", "beschreibung", "quelle", "status")


def laden():
    daten = json.loads(STAEDTE.read_text(encoding="utf-8"))
    staedte = daten["staedte"]
    ids = set()
    for s in staedte:
        fehlend = [f for f in PFLICHT if not s.get(f)]
        if fehlend:
            sys.exit(f"staedte.json: Eintrag {s.get('id', '?')} ohne {', '.join(fehlend)}")
        if s["status"] not in STATUS:
            sys.exit(f"staedte.json: {s['id']}: Status „{s['status']}“ unbekannt (erlaubt: {', '.join(STATUS)})")
        if not s["url"].startswith("https://"):
            sys.exit(f"staedte.json: {s['id']}: url muss mit https:// beginnen")
        if s["id"] in ids:
            sys.exit(f"staedte.json: id {s['id']} doppelt")
        ids.add(s["id"])
        for t in s.get("themen") or []:
            if not t.get("titel") or not str(t.get("url", "")).startswith("https://"):
                sys.exit(f"staedte.json: {s['id']}: Thema ohne Titel oder ohne https-Adresse")
        if s.get("themen_alle") and not s["themen_alle"].startswith("https://"):
            sys.exit(f"staedte.json: {s['id']}: themen_alle muss mit https:// beginnen")
        bild = s.get("bild")
        if bild and not (WURZEL / "site" / bild).is_file():
            sys.exit(f"staedte.json: {s['id']}: Bild {bild} fehlt in site/")
    return staedte


def themen_html(s):
    """Links auf Themenseiten der Instanz; liegen über der Klickfläche des Knopfs (z-index in style.css)."""
    e = html.escape
    themen = s.get("themen") or []
    if not themen:
        return []
    links = [f'<li><a href="{e(t["url"])}">{e(t["titel"])}</a></li>' for t in themen]
    if s.get("themen_alle"):
        links.append(f'<li><a href="{e(s["themen_alle"])}">Alle Themen</a></li>')
    return [f'    <p class="kachel-themen-titel" id="themen-{e(s["id"])}">Themenseiten</p>',
            f'    <ul class="kachel-themen" aria-labelledby="themen-{e(s["id"])}">',
            *[f'      {l}' for l in links],
            '    </ul>']


def kachel(s, einzug):
    """Stadt mit Status „online“: Kachel mit Bild, Angaben und Knopf. Der Knopf ist der einzige Link
    und deckt die ganze Kachel ab (ein Link je Kachel, keine doppelten Tabstopps)."""
    e = html.escape
    status_text, status_klasse = STATUS[s["status"]]
    if s.get("bild"):
        kopf = f'<img src="{e(s["bild"])}" width="1200" height="630" alt="">'
    else:
        kopf = '<img class="kachel-symbol" src="favicon.svg" width="72" height="72" alt="">'
    zeilen = [
        '<li class="kachel glass kachel-link">',
        f'  <div class="kachel-kopf">{kopf}</div>',
        '  <div class="kachel-inhalt">',
        f'    <h3>{e(s["titel"])}</h3>',
        f'    <p class="kachel-text">{e(s["beschreibung"])}</p>',
        *themen_html(s),
        '    <dl class="kachel-angaben">',
        f'      <dt>Adresse</dt><dd>{e(s["adresse"])}</dd>',
        f'      <dt>Datenquelle</dt><dd>{e(s["quelle"])}</dd>',
        f'      <dt>Status</dt><dd><span class="status {status_klasse}">{status_text}</span></dd>',
        '    </dl>',
        f'    <p class="kachel-aktion"><a class="knopf kachel-knopf" href="{e(s["url"])}">{e(s["titel"])} öffnen'
        '<span class="knopf-pfeil" aria-hidden="true">→</span></a></p>',
        '  </div>',
        '</li>',
    ]
    return "\n".join(einzug + z for z in zeilen)


def vorbereitung(s, einzug):
    """Stadt „in Vorbereitung“: schmale Zeile ohne Bildfläche und ohne Link (nichts zu öffnen)."""
    e = html.escape
    status_text, status_klasse = STATUS[s["status"]]
    return (f'{einzug}<li><strong>{e(s["titel"])}</strong> <span class="status {status_klasse}">{status_text}</span> '
            f'<span class="vorbereitung-angaben">{e(s["adresse"])} · {e(s["quelle"])}</span></li>')


def kacheln_html(staedte, einzug):
    online = [s for s in staedte if s["status"] == "online"]
    spaeter = [s for s in staedte if s["status"] != "online"]
    teile = []
    if online:
        teile.append(einzug + '<ul class="kacheln">')
        teile += [kachel(s, einzug + "  ") for s in online]
        teile.append(einzug + "</ul>")
    if spaeter:
        teile.append(einzug + '<ul class="vorbereitung">')
        teile += [vorbereitung(s, einzug + "  ") for s in spaeter]
        teile.append(einzug + "</ul>")
    return "\n".join(teile)


def jsonld_html(staedte, einzug):
    daten = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Ratsatlas",
        "url": SITE_URL,
        "inLanguage": "de",
        "description": "Der Ratsatlas erschließt öffentliche Vorlagen aus kommunalen Ratsinformationssystemen "
                       "räumlich, zeitlich und nach beteiligten Gremien und Ämtern.",
        "publisher": {"@type": "Person", "name": "Damian Paderta"},
        "sponsor": {"@type": "Organization", "name": "Offene Kommunen.NRW", "url": "https://oknrw.de/"},
        "about": ["Kommunalpolitik", "Ratsinformationssystem", "Transparenz", "Bürgerbeteiligung"],
        "isAccessibleForFree": True,
        "license": "https://opensource.org/licenses/MIT",
        # Nur erreichbare Instanzen; Städte „in Vorbereitung“ erscheinen erst, wenn sie online sind
        "hasPart": [
            {"@type": "WebSite", "name": s["titel"], "url": s["url"].rstrip("/") + "/", "inLanguage": "de"}
            for s in staedte if s["status"] == "online"
        ],
    }
    text = json.dumps(daten, ensure_ascii=False, indent=2).replace("</", "<\\/")
    zeilen = ['<script type="application/ld+json">', *text.splitlines(), "</script>"]
    return "\n".join(einzug + z for z in zeilen)


def ersetzen(quelle, name, inhalt_fn):
    muster = re.compile(
        rf"(?P<einzug>[ \t]*)(?P<anfang><!-- {name}:anfang[^>]*-->)\n.*?(?P<ende>[ \t]*<!-- {name}:ende -->)",
        re.S,
    )
    treffer = muster.search(quelle)
    if not treffer:
        sys.exit(f"site/index.html: Markierungen {name}:anfang/{name}:ende fehlen")
    einzug = treffer.group("einzug")
    neu = f'{einzug}{treffer.group("anfang")}\n{inhalt_fn(einzug)}\n{treffer.group("ende")}'
    return quelle[:treffer.start()] + neu + quelle[treffer.end():]


def main():
    pruefen = "--pruefen" in sys.argv[1:]
    staedte = laden()
    alt = INDEX.read_text(encoding="utf-8")
    neu = ersetzen(alt, "kacheln", lambda e: kacheln_html(staedte, e))
    neu = ersetzen(neu, "jsonld", lambda e: jsonld_html(staedte, e))
    if pruefen:
        if neu != alt:
            sys.exit("site/index.html ist nicht auf dem Stand von staedte.json – bitte scripts/kacheln.py ausführen")
        print("ok  site/index.html entspricht staedte.json")
        return
    if neu != alt:
        INDEX.write_text(neu, encoding="utf-8")
        print("site/index.html aktualisiert")
    else:
        print("site/index.html unverändert")


if __name__ == "__main__":
    main()
