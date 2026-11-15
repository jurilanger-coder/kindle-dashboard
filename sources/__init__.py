"""Datenquellen fuer das Kindle-Dashboard. Nur Standardbibliothek."""
import json
import urllib.request
import urllib.error

USER_AGENT = "kindle-dashboard/1.0 (privates Dashboard)"
TIMEOUT = 20


def http_get(url, as_json=True):
    """Holt eine URL. Wirft bei Fehlern eine Exception - der Aufrufer faengt sie."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
    if as_json:
        return json.loads(raw.decode("utf-8"))
    return raw.decode("utf-8", errors="replace")
