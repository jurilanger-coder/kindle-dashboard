#!/bin/sh
# Prueft die drei Dinge, an denen es erfahrungsgemaess scheitert:
# Netz, HTTPS-Zertifikate und FBInk. Ergebnis erscheint auf dem Display.
EXTDIR=/mnt/us/extensions/dashboard
. "$EXTDIR/config.sh"
FBINK="$EXTDIR/bin/fbink"
OUT="$EXTDIR/selftest.txt"

{
  echo "--- Selbsttest $(date) ---"
  echo "URL: $IMG_URL"
  echo
  echo "1) Netz erreichbar?"
  ping -c 1 -W 3 1.1.1.1 >/dev/null 2>&1 && echo "   ja" || echo "   NEIN - WLAN pruefen"
  echo "2) Download MIT Zertifikatspruefung:"
  wget -q -O /dev/null "$IMG_URL" 2>&1 && echo "   klappt" || echo "   scheitert (alter Zertifikatsspeicher - VERIFY_TLS=0 setzen)"
  echo "3) Download OHNE Zertifikatspruefung:"
  wget -q --no-check-certificate -O "$EXTDIR/test.png" "$IMG_URL" 2>&1 && echo "   klappt" || echo "   scheitert auch - URL falsch?"
  if [ -s "$EXTDIR/test.png" ]; then
     echo "   Groesse: $(wc -c < "$EXTDIR/test.png") Bytes"
     head -c 4 "$EXTDIR/test.png" | grep -q PNG && echo "   Datei ist ein PNG" || echo "   Datei ist KEIN PNG"
  fi
  echo "4) FBInk vorhanden?"
  [ -x "$FBINK" ] && echo "   ja, $($FBINK -v 2>&1 | head -1)" || echo "   NEIN"
} > "$OUT" 2>&1

"$FBINK" -c -q
"$FBINK" -q -y 2 "$(cat "$OUT" | head -30)"
