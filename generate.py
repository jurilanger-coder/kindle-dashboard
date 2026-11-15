# -*- coding: utf-8 -*-
"""Erzeugt dashboard.png. Holt die Daten, faellt bei Ausfall auf den Cache zurueck.

  python3 generate.py                    # normaler Lauf
  python3 generate.py --mock             # ohne Netz, mit Beispieldaten
  python3 generate.py --config meine.json --out out/dashboard.png
"""
import argparse
import datetime
import json
import os
import sys

import render
from sources import weather as src_weather
from sources import stocks as src_stocks
from sources import news as src_news

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "out", "cache.json")

MOCK = {
    "weather": {
        "place": "Berlin", "temp": 7, "feels": 4, "humidity": 81, "wind": 14,
        "text": "Teils wolkig", "icon": "partly",
        "days": [
            {"date": "2026-11-15", "tmax": 8, "tmin": 3, "rain": 20, "icon": "partly", "text": "Teils wolkig"},
            {"date": "2026-11-16", "tmax": 6, "tmin": 1, "rain": 70, "icon": "rain", "text": "Regen"},
            {"date": "2026-11-17", "tmax": 5, "tmin": 0, "rain": 40, "icon": "cloud", "text": "Bedeckt"},
            {"date": "2026-11-18", "tmax": 4, "tmin": -2, "rain": 10, "icon": "sun", "text": "Klar"},
        ],
    },
    "stocks": [],
    "news": [
        {"source": "Tagesschau", "title": "Bundesrat billigt Reform der Netzentgelte für Ladeinfrastruktur"},
        {"source": "Tagesschau", "title": "Tarifverhandlungen im öffentlichen Dienst gehen in die dritte Runde"},
        {"source": "Tagesschau", "title": "Neue Zahlen zum Ausbau der Schnellladersäulen an Autobahnen veröffentlicht"},
        {"source": "Tagesschau", "title": "Wetterdienst warnt vor Sturmböen im Nordosten"},
        {"source": "heise", "title": "Schwachstelle in verbreiteter Open-Source-Bibliothek geschlossen"},
        {"source": "heise", "title": "Neue Generation von E-Ink-Displays kommt mit schnellerem Bildaufbau"},
    ],
}


def load_config(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_cache():
    try:
        with open(CACHE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def write_cache(data):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def collect(cfg):
    """Holt alle Quellen. Jede einzeln abgesichert: faellt eine aus, bleibt der
    Rest stehen und die ausgefallene kommt aus dem Cache."""
    cache = read_cache()
    data, problems = {}, []

    for name, fn in (("weather", src_weather.fetch),
                     ("stocks", src_stocks.fetch),
                     ("news", src_news.fetch)):
        try:
            data[name] = fn(cfg)
        except Exception as exc:
            problems.append("{}: {}".format(name, exc))
            data[name] = cache.get(name)
            print("WARNUNG {} fehlgeschlagen: {}".format(name, exc), file=sys.stderr)

    keep = {k: v for k, v in data.items() if v}
    if keep:
        write_cache({**cache, **keep})

    quellen = "Wetter: Open-Meteo"
    if data.get("stocks"):
        quellen += "   Kurse: {}".format(cfg["stocks"]["provider"])
    if problems:
        quellen += "   (teilweise aus Zwischenspeicher)"
    data["footer"] = quellen
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "dashboard.png"))
    ap.add_argument("--mock", action="store_true", help="Beispieldaten statt echter Abfragen")
    args = ap.parse_args()

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(HERE, "config.example.json")
        print("Hinweis: benutze {}".format(os.path.basename(cfg_path)), file=sys.stderr)
    cfg = load_config(cfg_path)

    # Schluessel nie im oeffentlichen Repository: Umgebungsvariable schlaegt Datei.
    env_key = os.environ.get("STOCKS_API_KEY")
    if env_key and cfg.get("stocks"):
        cfg["stocks"]["api_key"] = env_key

    if args.mock:
        data = dict(MOCK)
        data["footer"] = "Beispieldaten - Layoutvorschau"
        stand = datetime.datetime(2026, 11, 15, 17, 20)
    else:
        data = collect(cfg)
        stand = None

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    img = render.compose(data, cfg, stand=stand)
    render.save(img, args.out)
    print("{} geschrieben: {}x{}".format(args.out, img.width, img.height))


if __name__ == "__main__":
    main()
