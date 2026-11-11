#!/usr/bin/env bash
# Prüft die ausgelieferte Seite nach der Umstellung: Status, Zertifikat, Weiterleitungen, Sicherheitskopfzeilen.
# Kopfzeilen mit GET wie ein Browser, nicht mit HEAD: netcup/nginx beantwortet HEAD auf anderem Weg (Befund Bonn).
# Aufruf: scripts/live_pruefen.sh [https://ratsatlas.de]   Ausgabe: TSV-Zeilen für pruefung.tsv
set -uo pipefail
BASIS="${1:-https://ratsatlas.de}"
HOST="${BASIS#https://}"
DATUM="$(date +%F)"
fehler=0
WERKZEUG="curl (GET)"
zeile() { printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$WERKZEUG" "$2" "$3" "$DATUM"; [ "$4" = ok ] || fehler=1; }

kopf=$(curl -sS --max-time 20 -D - -o /dev/null "$BASIS/" | tr -d '\r')
status=$(printf '%s\n' "$kopf" | awk 'NR==1{print $2}')
zeile "Status $BASIS/" "200" "$status" "$([ "$status" = 200 ] && echo ok)"

for k in Content-Security-Policy X-Content-Type-Options Referrer-Policy Permissions-Policy Strict-Transport-Security; do
  wert=$(printf '%s\n' "$kopf" | grep -i "^$k:" | head -1 | cut -d' ' -f2-)
  zeile "Kopfzeile $k" "vorhanden" "${wert:-fehlt}" "$([ -n "$wert" ] && echo ok)"
done

# Weiterleitungen: ohne -L, nur erste Antwort
weiter() {  # Adresse, erwartetes Ziel
  read -r code ziel < <(curl -sS --max-time 20 -o /dev/null -w '%{http_code} %{redirect_url}' "$1")
  zeile "Weiterleitung $1" "301 → $2" "$code → ${ziel:-keine}" "$([ "$code" = 301 ] && [ "${ziel%/}" = "${2%/}" ] && echo ok)"
}
weiter "http://$HOST/" "https://$HOST/"
weiter "https://www.$HOST/" "https://$HOST/"
# http://www zuerst auf https://www (gleicher Name, wie für HSTS empfohlen), dann auf die Hauptadresse
weiter "http://www.$HOST/" "https://www.$HOST/"
ende=$(curl -sS -L --max-time 20 -o /dev/null -w '%{url_effective} %{num_redirects}' "http://www.$HOST/")
zeile "Ziel von http://www.$HOST/" "https://$HOST/ nach höchstens 2 Weiterleitungen" "$ende" "$( set -- $ende; [ "${1%/}" = "https://$HOST" ] && [ "$2" -le 2 ] && echo ok)"

# Stand: Hat das Webhosting den letzten Commit des Branch deploy abgeholt? (version.txt, geschrieben vom Workflow)
soll=""
if git rev-parse --git-dir > /dev/null 2>&1 && git fetch -q --depth 1 origin deploy 2> /dev/null; then
  soll=$(git show FETCH_HEAD:version.txt 2> /dev/null | tr -d '[:space:]')
fi
[ -n "$soll" ] || soll=$(curl -fsS --max-time 20 https://raw.githubusercontent.com/daimpad/ratsatlas/deploy/version.txt 2> /dev/null | tr -d '[:space:]')
ist=$(curl -fsS --max-time 20 "$BASIS/version.txt" 2> /dev/null | tr -d '[:space:]')
zeile "Stand $BASIS/version.txt = Branch deploy" "${soll:0:7}" "${ist:0:7}" "$([ -n "$soll" ] && [ "$ist" = "$soll" ] && echo ok)"

# Suchmaschinen: robots.txt, Sitemap, Canonical, eine Adresse je Seite, Vorschaubild
robots=$(curl -fsS --max-time 20 "$BASIS/robots.txt" 2> /dev/null)
zeile "robots.txt nennt die Sitemap" "Sitemap: $BASIS/sitemap.xml" "$(printf '%s' "$robots" | grep -i '^Sitemap:' | head -1)" "$(printf '%s' "$robots" | grep -qi "^Sitemap: $BASIS/sitemap.xml" && echo ok)"
sitemap=$(curl -fsS --max-time 20 "$BASIS/sitemap.xml" 2> /dev/null)
anzahl=$(printf '%s' "$sitemap" | grep -c '<loc>')
zeile "sitemap.xml" "<urlset> mit <loc> und <lastmod>" "$anzahl Adressen, lastmod: $(printf '%s' "$sitemap" | grep -c '<lastmod>')" "$([ "$anzahl" -gt 0 ] && printf '%s' "$sitemap" | grep -q '<lastmod>' && echo ok)"
canon=$(curl -fsS --max-time 20 "$BASIS/" 2> /dev/null | grep -o '<link rel="canonical" href="[^"]*"' | head -1 | sed 's/.*href="//;s/"$//')
zeile "Canonical der Startseite" "$BASIS/" "${canon:-fehlt}" "$([ "$canon" = "$BASIS/" ] && echo ok)"
weiter "$BASIS/index.html" "$BASIS/"
og=$(curl -fsS --max-time 20 -o /dev/null -w '%{http_code} %{content_type}' "$BASIS/og-image.png" 2> /dev/null)
zeile "Vorschaubild $BASIS/og-image.png" "200 image/png" "${og:-keine Antwort}" "$(case "$og" in "200 image/png"*) echo ok;; esac)"

# IndexNow: Schlüsseldatei erreichbar und gleich ihrem Namen
key=$(ls "$(dirname "$0")/../site" 2>/dev/null | grep -E '^[0-9a-f]{32}\.txt$' | head -1 | sed 's/\.txt$//')
if [ -n "$key" ]; then
  inhalt=$(curl -fsS --max-time 20 "$BASIS/$key.txt" 2> /dev/null | tr -d '[:space:]')
  zeile "IndexNow-Schlüssel $BASIS/$key.txt" "200, Inhalt = Schlüssel" "${inhalt:+gefunden}${inhalt:-fehlt}" "$([ "$inhalt" = "$key" ] && echo ok)"
fi

# 404-Seite
code=$(curl -sS --max-time 20 -o /tmp/live404.html -w '%{http_code}' "$BASIS/gibt-es-nicht")
eigene=$(grep -c 'Diese Seite gibt es nicht' /tmp/live404.html 2>/dev/null || true)
zeile "404 unter $BASIS/gibt-es-nicht" "404 mit eigener Seite" "$code, eigene Seite: $([ "${eigene:-0}" -gt 0 ] && echo ja || echo nein)" "$([ "$code" = 404 ] && [ "${eigene:-0}" -gt 0 ] && echo ok)"

# .htaccess und .git nicht abrufbar
code=$(curl -sS --max-time 20 -o /dev/null -w '%{http_code}' "$BASIS/.htaccess")
zeile "$BASIS/.htaccess nicht abrufbar" "403 oder 404" "$code" "$( { [ "$code" = 403 ] || [ "$code" = 404 ]; } && echo ok)"

# Zertifikat (beide Namen); hinter einem TLS-Proxy nicht aussagekräftig, daher im Workflow live.yml ausführen
WERKZEUG="openssl s_client"
for n in "$HOST" "www.$HOST"; do
  info=$(echo | openssl s_client -connect "$n:443" -servername "$n" 2>/dev/null | openssl x509 -noout -enddate -ext subjectAltName 2>/dev/null | tr '\n' ' ')
  gueltig=$(echo | openssl s_client -connect "$n:443" -servername "$n" -verify_return_error 2>&1 | grep -c 'Verify return code: 0 (ok)')
  zeile "Zertifikat $n" "gültig, Name enthalten" "${info:-keine Antwort}" "$([ "$gueltig" -gt 0 ] && echo ok)"
done

exit $fehler
