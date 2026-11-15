#!/bin/sh
# Beendet das Dashboard und holt die normale Kindle-Oberflaeche zurueck.
pkill -f dashboard.sh
lipc-set-prop com.lab126.powerd preventScreenSaver 0 >/dev/null 2>&1
/mnt/us/extensions/dashboard/bin/fbink -c -f -q
start lab126_gui >/dev/null 2>&1
