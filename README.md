# Ratsatlas

Der Ratsatlas erschließt öffentliche Vorlagen aus kommunalen Ratsinformationssystemen räumlich, zeitlich und nach beteiligten Gremien und Ämtern.

Dieses Repository ist der gemeinsame Kern des Ratsatlas. Es enthält:

- die Startseite unter <https://ratsatlas.de> (Verzeichnis `site/`),
- die gemeinsamen Gestaltungsgrößen (`site/tokens.css`), Schrift und Symbole, die die Stadtinstanzen übernehmen.

Die Stadtinstanzen liegen in eigenen Repositorys und unter eigenen Subdomains:

| Stadt | Adresse | Repository | Status |
|---|---|---|---|
| Bonn | <https://bonn.ratsatlas.de> | [daimpad/allris-test](https://github.com/daimpad/allris-test) | online |
| Köln | <https://koeln.ratsatlas.de> | offen | in Vorbereitung |

Die Liste wird in `staedte.json` gepflegt; eine neue Stadt ist ein neuer Eintrag. Danach schreibt

```
python3 scripts/kacheln.py
```

die Kacheln und das JSON-LD in `site/index.html`; `python3 scripts/kacheln.py --pruefen` meldet einen Fehler, wenn beides nicht übereinstimmt. Status `online` ergibt eine verlinkte Kachel, `in Vorbereitung` eine Kachel ohne Link.

## Lizenzen

- Code: MIT, siehe `LICENSE`
- Schrift Inter: SIL Open Font License 1.1, siehe `site/fonts/LICENSE-Inter.txt`

## Deployment

Bei jedem Push auf `main` wird der Inhalt von `site/` als Branch `deploy` geschrieben. Das Webhosting (Plesk) holt diesen Branch ab. GitHub Pages dient als Ausweichadresse.
