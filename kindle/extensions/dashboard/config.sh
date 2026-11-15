# Konfiguration des Kindle-Dashboards.
# Die URL bekommst du nach dem ersten GitHub-Pages-Lauf.
IMG_URL="https://DEINBENUTZERNAME.github.io/kindle-dashboard/dashboard.png"

# Sekunden zwischen zwei Aktualisierungen. 1800 = halbe Stunde.
INTERVAL=1800

# Nach wie vielen Durchlaeufen ein vollstaendiger Bildaufbau erfolgt.
# Raeumt Schatten frueherer Bilder ab (Ghosting). 12 = etwa alle 6 Stunden.
FULL_REFRESH_EVERY=12

# Zertifikatspruefung beim Herunterladen.
# Alte Kindles haben einen veralteten Zertifikatsspeicher und scheitern sonst
# an GitHub Pages. Das Bild ist oeffentlich und enthaelt nichts Schuetzenswertes,
# deshalb ist das hier vertretbar. Auf 1 setzen, wenn du die Pruefung willst.
VERIFY_TLS=0
