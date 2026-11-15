"""Boersenkurse - OPTIONAL und standardmaessig abgeschaltet.

Drei Anbieter zur Wahl:
  twelvedata - ein Schluessel fuer Indizes, Devisen und Krypto, 800 Abfragen/Tag frei
  finnhub    - 60 Abfragen/Minute frei, stark bei US-Aktien, schwach bei Indizes
  coingecko  - KEIN Schluessel noetig, aber nur Kryptowaehrungen
"""
from . import http_get


def _twelvedata(cfg):
    key = cfg["stocks"]["api_key"]
    out = []
    for item in cfg["stocks"]["symbols"]:
        url = "https://api.twelvedata.com/quote?symbol={s}&apikey={k}".format(
            s=urlquote(item["symbol"]), k=key)
        d = http_get(url)
        if d.get("status") == "error":
            raise RuntimeError("{}: {}".format(item["symbol"], d.get("message")))
        out.append({
            "label": item["label"],
            "value": float(d["close"]),
            "change_pct": float(d.get("percent_change") or 0.0),
        })
    return out


def _finnhub(cfg):
    key = cfg["stocks"]["api_key"]
    out = []
    for item in cfg["stocks"]["symbols"]:
        url = "https://finnhub.io/api/v1/quote?symbol={s}&token={k}".format(
            s=urlquote(item["symbol"]), k=key)
        d = http_get(url)
        if d.get("c") in (None, 0):
            raise RuntimeError("{}: keine Daten".format(item["symbol"]))
        out.append({
            "label": item["label"],
            "value": float(d["c"]),
            "change_pct": float(d.get("dp") or 0.0),
        })
    return out


def _coingecko(cfg):
    ids = ",".join(i["symbol"] for i in cfg["stocks"]["symbols"])
    url = ("https://api.coingecko.com/api/v3/simple/price"
           "?ids={ids}&vs_currencies=eur&include_24hr_change=true").format(ids=ids)
    d = http_get(url)
    out = []
    for item in cfg["stocks"]["symbols"]:
        row = d.get(item["symbol"])
        if not row:
            raise RuntimeError("{}: unbekannte Coin-ID".format(item["symbol"]))
        out.append({
            "label": item["label"],
            "value": float(row["eur"]),
            "change_pct": float(row.get("eur_24h_change") or 0.0),
        })
    return out


def urlquote(s):
    from urllib.parse import quote
    return quote(str(s), safe="")


PROVIDERS = {
    "twelvedata": _twelvedata,
    "finnhub": _finnhub,
    "coingecko": _coingecko,
}


def fetch(cfg):
    sc = cfg.get("stocks") or {}
    if not sc.get("enabled"):
        return []
    name = sc.get("provider", "twelvedata")
    if name not in PROVIDERS:
        raise RuntimeError("Unbekannter Anbieter: {}".format(name))
    return PROVIDERS[name](cfg)
