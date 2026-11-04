# Checkliste Umstellung ratsatlas.de (manuell, Damian)

Stand 04.11.2026. Ausgangslage: `ratsatlas.de` liefert bereits über netcup (nginx) eine Platzhalterseite „Hier entsteht eine neue Webseite“, mit Zertifikat; `http://` leitet schon auf `https://` weiter. `www.ratsatlas.de` antwortet mit 200 statt mit einer Weiterleitung.

## GitHub

- [ ] Pull Request zusammenführen; der Workflow „Seite veröffentlichen“ schreibt danach den Branch `deploy`.
- [ ] Settings → Pages → Source: **GitHub Actions** (Ausweichadresse `https://daimpad.github.io/ratsatlas/`). Läuft der Job `pages` vor dieser Einstellung, schlägt er fehl; danach Workflow unter Actions neu starten.

## Plesk (netcup)

- [ ] Domain `ratsatlas.de` vorhanden; Dokumentenverzeichnis z. B. `httpdocs`. Platzhalterdateien darin entfernen (sie würden sonst neben der Seite liegen bleiben).
- [ ] Hosting-Einstellungen: **Bevorzugte Domain: `ratsatlas.de`** (leitet `www.ratsatlas.de` mit 301 auf `https://ratsatlas.de` um).
- [ ] SSL/TLS: Let's-Encrypt-Zertifikat für `ratsatlas.de` **und** `www.ratsatlas.de`; „Permanente SEO-sichere 301-Weiterleitung von HTTP zu HTTPS“ an.
- [ ] Git: Repository `https://github.com/daimpad/ratsatlas.git`, Branch **`deploy`**, automatische Bereitstellung in das Dokumentenverzeichnis.
- [ ] Der Branch `deploy` wird bei jeder Veröffentlichung ohne Historie neu geschrieben (Force-Push). Nach dem ersten Abruf prüfen, ob Plesk einen neu geschriebenen Branch übernimmt (zweite Veröffentlichung abwarten, dann Live-Prüfung). Falls nicht: „Abrufen“ in Plesk, oder Workflow auf fortlaufende Historie umstellen (wie in allris-test).
- [ ] Kopfzeilen: In Bonn liefert nginx statische Dateien ohne die Kopfzeilen aus `.htaccess` aus. Entweder unter „Apache- & nginx-Einstellungen“ **„Statische Dateien direkt durch nginx bereitstellen“ abschalten**, oder den Inhalt von `deploy/nginx-zusatz.conf` unter „Zusätzliche nginx-Anweisungen“ eintragen – nicht beides.

## GitHub-Webhook

- [ ] Plesk → Git → Repository-Einstellungen: Webhook-URL kopieren.
- [ ] GitHub → Settings → Webhooks → Add webhook: Payload-URL aus Plesk, Content type `application/json`, Ereignis „Just the push event“.

## DNS

- [ ] A-Eintrag (und ggf. AAAA) von `ratsatlas.de` und `www` auf das Webhosting. Nach der Ausgangslage zeigt er bereits dorthin; nur prüfen.
- [ ] **MX- und TXT-Einträge nicht verändern.**

## Danach

- [ ] GitHub → Actions → „Live-Prüfung“ → Run workflow. Alle Zeilen müssen bestehen; das Ergebnis steht in der Zusammenfassung des Laufs und wird in `pruefung.tsv` übernommen.
- [ ] Datenschutzseite prüfen und den Hinweis „Entwurf“ entfernen (`site/datenschutz.html`).
