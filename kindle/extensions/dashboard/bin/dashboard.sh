#!/bin/sh
# Kindle-Dashboard: laedt regelmaessig ein Bild und zeigt es im Vollbild.
# Getestet gedacht fuer Kindle Paperwhite 3 (7. Gen), Firmware 5.13.x.

EXTDIR=/mnt/us/extensions/dashboard
. "$EXTDIR/config.sh"

FBINK="$EXTDIR/bin/fbink"
IMG="$EXTDIR/current.png"
TMP="$EXTDIR/current.tmp"
LOG="$EXTDIR/dashboard.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; }

if [ ! -x "$FBINK" ]; then
    echo "FBInk fehlt unter $FBINK" >&2
    exit 1
fi

# Oberflaeche anhalten und Bildschirmschoner unterbinden, damit uns nichts
# dazwischenfunkt. Beendet wird das ueber restore.sh oder einen Neustart.
log "Dashboard startet"
stop lab126_gui >/dev/null 2>&1
lipc-set-prop com.lab126.powerd preventScreenSaver 1 >/dev/null 2>&1

cleanup() {
    log "Dashboard endet, Oberflaeche zurueck"
    lipc-set-prop com.lab126.powerd preventScreenSaver 0 >/dev/null 2>&1
    start lab126_gui >/dev/null 2>&1
    exit 0
}
trap cleanup INT TERM

"$FBINK" -c -f -q

COUNT=0
while true; do
    WGET_OPTS="-q -O $TMP"
    [ "$VERIFY_TLS" = "0" ] && WGET_OPTS="$WGET_OPTS --no-check-certificate"

    if wget $WGET_OPTS "$IMG_URL" 2>>"$LOG"; then
        # Nur uebernehmen, wenn wirklich ein PNG ankam. Ein Fehlerdokument
        # vom Server wuerde sonst das letzte gute Bild zerstoeren.
        if [ -s "$TMP" ] && head -c 4 "$TMP" | grep -q "PNG"; then
            mv "$TMP" "$IMG"
            log "Bild aktualisiert ($(wc -c < "$IMG") Bytes)"
        else
            log "Antwort war kein PNG, behalte altes Bild"
            rm -f "$TMP"
        fi
    else
        log "Download fehlgeschlagen, behalte altes Bild"
        rm -f "$TMP"
    fi

    if [ -f "$IMG" ]; then
        COUNT=$((COUNT + 1))
        if [ "$COUNT" -ge "$FULL_REFRESH_EVERY" ]; then
            "$FBINK" -c -f -q          # vollstaendiger Aufbau gegen Ghosting
            COUNT=0
        fi
        "$FBINK" -q -g file="$IMG",halign=center,valign=center
    fi

    sleep "$INTERVAL"
done
