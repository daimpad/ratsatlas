#!/usr/bin/env python3
"""Meldet geänderte Seiten von ratsatlas.de an IndexNow (Bing, Yandex, Seznam, Naver; über Bing auch DuckDuckGo
und Ecosia). Google nutzt IndexNow nicht.

Aufruf im Workflow nach dem Fortschreiben des Branch deploy:
  python3 scripts/indexnow.py --deploy _deploy --sha "$GITHUB_SHA"
  python3 scripts/indexnow.py --trocken ...   # nur anzeigen, nichts senden

- Geänderte Seiten: HTML-Dateien im letzten Commit von deploy (ohne 404.html); Gestaltung, Bilder, Sitemap und
  version.txt ändern keinen Inhalt und werden nicht gemeldet.
- Gemeldet wird erst, wenn https://ratsatlas.de/version.txt den neuen Stand zeigt (Plesk holt per Webhook ab),
  sonst würde der Crawler den alten Inhalt lesen.
- Der Schlüssel ist öffentlich (Datei <schlüssel>.txt in site/), wie es das Verfahren vorsieht.
- Fehler bei IndexNow sind Warnungen, keine Abbrüche: die Veröffentlichung ist zu diesem Zeitpunkt bereits erfolgt.
Nur Standardbibliothek.
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
HOST = "ratsatlas.de"
BASIS = f"https://{HOST}/"
ENDPUNKT = "https://api.indexnow.org/indexnow"
OHNE = {"404.html"}


def warnung(text):
    print(f"::warning::IndexNow: {text}")


def schluessel():
    dateien = [p for p in (WURZEL / "site").glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(dateien) != 1:
        sys.exit(f"IndexNow: genau eine Schlüsseldatei <32 hex>.txt in site/ erwartet, gefunden {len(dateien)}")
    key = dateien[0].read_text(encoding="utf-8").strip()
    if key != dateien[0].stem:
        sys.exit("IndexNow: Inhalt der Schlüsseldatei entspricht nicht ihrem Namen")
    return key


def geaenderte_seiten(deploy):
    """HTML-Dateien des letzten deploy-Commits als Adressen; ohne Vorgänger alle Seiten."""
    def git(*args):
        return subprocess.run(["git", "-C", str(deploy), *args], capture_output=True, text=True)
    if git("rev-parse", "--verify", "-q", "HEAD~1").returncode == 0:
        dateien = git("diff", "--name-only", "HEAD~1", "HEAD").stdout.split()
    else:
        dateien = git("ls-files").stdout.split()
    urls = []
    for d in sorted(dateien):
        if not d.endswith(".html") or Path(d).name in OHNE:
            continue
        pfad = d[: -len("index.html")] if d.endswith("index.html") else d
        urls.append(BASIS + pfad)
    return urls


def warte_auf_stand(sha, sekunden=300):
    ende = time.time() + sekunden
    while time.time() < ende:
        try:
            with urllib.request.urlopen(BASIS + f"version.txt?pruefung={int(time.time())}", timeout=20) as r:
                if r.read().decode().strip() == sha:
                    return True
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(10)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True, help="Arbeitskopie des Branch deploy")
    ap.add_argument("--sha", required=True, help="Commit von main, der ausgeliefert wird")
    ap.add_argument("--trocken", action="store_true", help="nur anzeigen, nichts senden")
    a = ap.parse_args()

    key = schluessel()
    urls = geaenderte_seiten(Path(a.deploy))
    if not urls:
        print("IndexNow: keine geänderten Seiten, nichts zu melden")
        return
    nutzlast = {"host": HOST, "key": key, "keyLocation": f"{BASIS}{key}.txt", "urlList": urls}
    print("IndexNow:", json.dumps(nutzlast, ensure_ascii=False))
    if a.trocken:
        return
    if not warte_auf_stand(a.sha):
        warnung(f"ratsatlas.de zeigt nach 5 Minuten nicht den Stand {a.sha[:7]} – nicht gemeldet")
        return
    anfrage = urllib.request.Request(ENDPUNKT, data=json.dumps(nutzlast).encode(), method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(anfrage, timeout=30) as r:
            print(f"IndexNow: {r.status} – {len(urls)} Adresse(n) gemeldet")
    except urllib.error.HTTPError as f:
        warnung(f"Antwort {f.code} {f.reason}")
    except (urllib.error.URLError, TimeoutError) as f:
        warnung(f"nicht erreichbar ({f})")


if __name__ == "__main__":
    main()
