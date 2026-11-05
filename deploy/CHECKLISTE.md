# Checkliste Umstellung ratsatlas.de (manuell, Damian)

Stand 04.11.2026. Ausgangslage: `ratsatlas.de` liefert bereits über netcup (nginx) eine Platzhalterseite „Hier entsteht eine neue Webseite“, mit Zertifikat; `http://` leitet schon auf `https://` weiter. `www.ratsatlas.de` antwortet mit 200 statt mit einer Weiterleitung.

## GitHub

- [ ] Nur der Workflow „Seite veröffentlichen“ liefert an GitHub Pages aus. Keine weitere Pages-Vorlage („Static HTML“, `static.yml`) anlegen: Sie veröffentlicht das ganze Repository und überschreibt je nach Laufreihenfolge die Seite.
- [ ] Pull Request zusammenführen; der Workflow „Seite veröffentlichen“ schreibt danach den Branch `deploy`.
- [ ] Settings → Pages → Source: **GitHub Actions** (Ausweichadresse `https://daimpad.github.io/ratsatlas/`). Läuft der Job `pages` vor dieser Einstellung, schlägt er fehl; danach Workflow unter Actions neu starten.

## Plesk (netcup)

- [ ] Domain `ratsatlas.de` vorhanden; Dokumentenverzeichnis z. B. `httpdocs`. Platzhalterdateien darin entfernen (sie würden sonst neben der Seite liegen bleiben).
- [ ] Hosting-Einstellungen: **Bevorzugte Domain: `ratsatlas.de`**. Ist die Auswahl ausgegraut (Stand 04.11.2026), übernimmt `deploy/htaccess` die Weiterleitung von `www`.
- [ ] SSL/TLS: Let's-Encrypt-Zertifikat für `ratsatlas.de` **und** `www.ratsatlas.de`; „Permanente SEO-sichere 301-Weiterleitung von HTTP zu HTTPS“ an.
- [ ] Git: Repository `https://github.com/daimpad/ratsatlas.git`, Branch **`deploy`**, automatische Bereitstellung in das Dokumentenverzeichnis.
- [ ] Der Branch `deploy` wird fortlaufend geschrieben (kein Force-Push), weil der Plesk-Webhook nur anschließende Stände abruft (Befund 04.11.2026). Nach der Umstellung einmal „Jetzt Pull ausführen“, danach ruft Plesk selbst ab. Ob der Stand angekommen ist, prüft die Live-Prüfung über `version.txt`.
- [ ] Kopfzeilen: Unter „Apache- & nginx-Einstellungen“ **„Intelligente Bearbeitung statischer Dateien“ und „Statische Dateien direkt durch nginx bedienen“ abschalten** (Proxymodus bleibt an). Sonst liefert nginx die Dateien ohne die Kopfzeilen und Weiterleitungen aus `.htaccess` aus (Befund 04.11.2026, wie in Bonn). Alternative nur für die Kopfzeilen: `deploy/nginx-zusatz.conf` als zusätzliche nginx-Anweisungen – nicht beides.

## GitHub-Webhook

- [ ] Plesk → Git → Repository-Einstellungen: Webhook-URL kopieren.
- [ ] GitHub → Settings → Webhooks → Add webhook: Payload-URL aus Plesk, Content type `application/json`, Ereignis „Just the push event“.

## DNS

- [ ] A-Eintrag (und ggf. AAAA) von `ratsatlas.de` und `www` auf das Webhosting. Nach der Ausgangslage zeigt er bereits dorthin; nur prüfen.
- [ ] **MX- und TXT-Einträge nicht verändern.**

## Danach

- [ ] GitHub → Actions → „Live-Prüfung“ → Run workflow. Alle Zeilen müssen bestehen; das Ergebnis steht in der Zusammenfassung des Laufs und wird in `pruefung.tsv` übernommen.
- [x] Datenschutzseite geprüft und freigegeben (04.11.2026).

## Suchmaschinen

- [ ] Google Search Console: Domain-Eigenschaft `ratsatlas.de` (erfasst auch `bonn.` und `koeln.`), Bestätigung über einen **neuen** DNS-TXT-Eintrag `google-site-verification=…` (bestehende MX- und TXT-Einträge bleiben unverändert).
- [ ] Search Console → Sitemaps: `https://ratsatlas.de/sitemap.xml` einreichen.
- [ ] Search Console → URL-Prüfung: `https://ratsatlas.de/` prüfen, „Indexierung beantragen“.
- [ ] Bing Webmaster Tools: „Aus Google Search Console importieren“ (deckt auch DuckDuckGo und Ecosia ab).
- [ ] GitHub → Repository → „About“ (Zahnrad): Website `https://ratsatlas.de` eintragen.
- [ ] Nach vier bis sechs Wochen: Bericht „Leistung“ (Suchanfragen, Seiten) auswerten.
