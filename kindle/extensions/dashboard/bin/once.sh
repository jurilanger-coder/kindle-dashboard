#!/bin/sh
# Holt genau ein Bild und zeigt es an. Zum Ausprobieren, ohne Dauerschleife.
EXTDIR=/mnt/us/extensions/dashboard
. "$EXTDIR/config.sh"
OPTS="-q -O $EXTDIR/current.png"
[ "$VERIFY_TLS" = "0" ] && OPTS="$OPTS --no-check-certificate"
wget $OPTS "$IMG_URL" && "$EXTDIR/bin/fbink" -q -g file="$EXTDIR/current.png",halign=center,valign=center
