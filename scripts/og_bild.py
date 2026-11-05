#!/usr/bin/env python3
"""Erzeugt site/og-image.png (1200 × 630) aus scripts/og-bild.html mit Playwright/Chromium.

Aufruf: python3 scripts/og_bild.py   (braucht Node mit Playwright und Pillow; nicht Teil des Workflows)
"""
import http.server
import subprocess
import threading
from functools import partial
from pathlib import Path

from PIL import Image

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "site" / "og-image.png"

JS = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto(process.argv[1], { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: process.argv[2] });
  await b.close();
})();
"""


def main():
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(WURZEL))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    roh = ZIEL.with_suffix(".roh.png")
    try:
        url = f"http://127.0.0.1:{server.server_port}/scripts/og-bild.html"
        subprocess.run(["node", "-e", JS, url, str(roh)], check=True)
    finally:
        server.shutdown()
    Image.open(roh).convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                                            dither=Image.Dither.NONE).save(ZIEL, optimize=True)
    roh.unlink()
    print(f"{ZIEL.relative_to(WURZEL)} geschrieben ({ZIEL.stat().st_size} Byte)")


if __name__ == "__main__":
    main()
