# Kindle-Dashboard

Verwandelt einen Kindle Paperwhite 3 (7. Generation) in ein Wand-Dashboard mit
Wetter und Nachrichten. GitHub Actions erzeugt stuendlich ein Bild, GitHub Pages
liefert es aus, der Kindle holt es ab und zeigt es im Vollbild.

Kein eigener Server noetig. Kosten: null.

```
GitHub Actions (stuendlich)          GitHub Pages            Kindle
  generate.py                          dashboard.png   <--   dashboard.sh
  Open-Meteo + RSS  -->  Pillow  -->   1072x1448 PNG         wget + FBInk
```

## Teil 1 - GitHub einrichten

1. **Neues oeffentliches Repository** anlegen, z. B. `kindle-dashboard`.
   Oeffentlich ist Pflicht: GitHub Pages gibt es im kostenlosen Tarif nur fuer
   oeffentliche Repositories. Dein Bild ist damit unter seiner URL fuer jeden
   erreichbar, der sie kennt - deshalb steht in `config.json` nur eine grobe
   Koordinate und sonst nichts Persoenliches.
2. Den Inhalt dieses Ordners hineinkopieren (ohne `kindle/`, das kommt spaeter
   auf das Geraet).
3. `config.json` anpassen: `location` auf deinen Ort.
4. **Settings -> Pages -> Source: GitHub Actions** einstellen.
5. **Actions -> Dashboard bauen und veroeffentlichen -> Run workflow** druecken.
6. Nach etwa einer Minute liegt das Bild unter
   `https://DEINNAME.github.io/kindle-dashboard/dashboard.png`.
   Im Browser oeffnen und pruefen.

Der Workflow laeuft danach stuendlich zur Minute 17 von selbst.

### Warum die Keepalive-Stufe drin ist

GitHub schaltet geplante Workflows in oeffentlichen Repositories ab, wenn
60 Tage lang nichts im Repository passiert - ohne Benachrichtigung. Dein
Dashboard wuerde also nach zwei Monaten einfrieren. Die letzte Stufe im
Workflow setzt deshalb regelmaessig einen Commit. Sollte es doch einmal
stehenbleiben: Actions-Tab -> Workflow -> **Enable workflow**.

## Teil 2 - Kindle vorbereiten

Voraussetzung ist ein Jailbreak. Reihenfolge, die funktioniert:

1. **Flugmodus an**, bevor irgendetwas anderes passiert.
2. Modell und Firmware unter *Einstellungen -> Geraeteoptionen -> Geraeteinfo*
   ablesen und auf **kindlemodding.org** die passende Methode nachschlagen.
3. **Speicher fuellen.** Der Jailbreak will nur noch etwa 50 bis 90 MB frei
   haben, damit sich waehrend des Vorgangs kein Update einschiebt. Bei 2,9 GB
   frei heisst das: grosse Dateien aufspielen, bis es passt.
4. Jailbreak durchfuehren, danach **OTA-Updates sperren** (Schritt aus der
   Anleitung nicht ueberspringen).
5. **KUAL** und **MRPI** installieren.
6. **FBInk** besorgen (Releases von NiLuJe auf GitHub) und die Datei `fbink`
   nach `extensions/dashboard/bin/` legen.

## Teil 3 - Dashboard auf den Kindle

1. Kindle per USB anschliessen.
2. Den Ordner `kindle/extensions/dashboard` nach `extensions/dashboard` auf das
   Kindle-Laufwerk kopieren.
3. `extensions/dashboard/config.sh` oeffnen und `IMG_URL` auf deine
   GitHub-Pages-Adresse setzen.
4. Sicher auswerfen, KUAL oeffnen, **Dashboard** erscheint im Menue.
5. Zuerst **Verbindung testen** druecken. Der Test sagt dir, ob Netz, HTTPS und
   FBInk stimmen, bevor du die Dauerschleife startest.
6. Dann **Jetzt einmal aktualisieren**, und wenn das Bild steht:
   **Dashboard starten**.

Zurueck zur normalen Oberflaeche: **Dashboard beenden** im KUAL-Menue, oder
Power-Taste 20 Sekunden halten und neu starten.

## Das HTTPS-Problem, und warum `VERIFY_TLS=0` voreingestellt ist

Ein Paperwhite 3 ist von 2015. Sein Zertifikatsspeicher kennt neuere
Wurzelzertifikate nicht, deshalb scheitert `wget` oft an GitHub Pages, obwohl
die Seite im Browser des Geraets laedt. Die Skripte laden das Bild daher
standardmaessig ohne Zertifikatspruefung.

Das ist hier vertretbar: es wird ein oeffentliches PNG heruntergeladen, es
werden keine Zugangsdaten uebertragen und nichts Vertrauliches gelesen. Wer es
sauber will, spielt auf dem gejailbreakten Geraet einen aktuellen
Zertifikatsspeicher ein und setzt `VERIFY_TLS=1`.

## Lokal ausprobieren

```bash
pip install pillow
python3 generate.py --mock          # Layout ohne Netz ansehen
python3 generate.py                 # echte Daten
```

Das Ergebnis liegt in `out/dashboard.png`.

## Boersenkurse nachruesten

Standardmaessig aus. Zum Einschalten in `config.json` `"enabled": true` setzen
und einen Anbieter waehlen:

| Anbieter | Schluessel | Frei | Taugt fuer |
| --- | --- | --- | --- |
| `twelvedata` | ja | 800 Abfragen/Tag | Indizes, Devisen, Krypto |
| `finnhub` | ja | 60 Abfragen/Minute | vor allem US-Aktien |
| `coingecko` | **nein** | grosszuegig | nur Kryptowaehrungen |

Den Schluessel nicht in `config.json` schreiben, sondern unter
*Settings -> Secrets and variables -> Actions* als `STOCKS_API_KEY` hinterlegen.
Das Repository ist oeffentlich.

## Wenn etwas nicht geht

| Symptom | Ursache |
| --- | --- |
| Bild bleibt stehen | Workflow nach 60 Tagen abgeschaltet, Actions-Tab pruefen |
| Kindle zeigt altes Bild | Download scheitert, `dashboard.log` auf dem Geraet lesen |
| Download scheitert nur mit Pruefung | Zertifikatsspeicher zu alt, `VERIFY_TLS=0` |
| Schatten im Bild | `FULL_REFRESH_EVERY` kleiner setzen |
| Nach Neustart weg | KUAL-Eintrag erneut starten, es gibt keinen Autostart |

## Datenquellen

- Wetter: Open-Meteo, kein Schluessel, frei fuer private Nutzung
- Nachrichten: RSS der jeweiligen Redaktionen. Angezeigt werden nur
  Schlagzeilen mit Quellenangabe, keine Artikeltexte.
