#!/usr/bin/env python3
"""Schreibt site/sitemap.xml mit dem Datum der letzten Änderung je Seite (lastmod aus der Git-Historie).

Aufruf: python3 scripts/sitemap.py
Läuft im Workflow „Seite veröffentlichen“ vor der Auslieferung; dort ist die volle Historie ausgecheckt
(fetch-depth: 0), sonst trüge jede Seite das Datum des letzten Commits. Nur Standardbibliothek.
"""
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

WURZEL = Path(__file__).resolve().parent.parent
SITE_URL = "https://ratsatlas.de/"
# Seite im Verzeichnis site/ → Adresse relativ zu SITE_URL; 404.html bleibt außen vor (noindex)
SEITEN = [
    ("index.html", ""),
    ("datenschutz.html", "datenschutz.html"),
]
# Änderungen an diesen Dateien betreffen jede Seite (Gestaltung, Städteliste)
GEMEINSAM = ["site/tokens.css", "site/style.css", "staedte.json"]


def letzte_aenderung(*pfade):
    aus = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *pfade],
                         cwd=WURZEL, capture_output=True, text=True, check=True).stdout.strip()
    return aus or None


def main():
    zeilen = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for datei, pfad in SEITEN:
        datum = letzte_aenderung(f"site/{datei}", *GEMEINSAM)
        lastmod = f"<lastmod>{datum}</lastmod>" if datum else ""
        zeilen.append(f"  <url><loc>{escape(SITE_URL + pfad)}</loc>{lastmod}</url>")
    zeilen.append("</urlset>")
    (WURZEL / "site" / "sitemap.xml").write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print("site/sitemap.xml geschrieben")


if __name__ == "__main__":
    main()
