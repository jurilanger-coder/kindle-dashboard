"""Wetter von Open-Meteo. Kein API-Schluessel noetig."""
from . import http_get

API = "https://api.open-meteo.com/v1/forecast"

# WMO-Wettercodes -> deutscher Text + Icon-Kuerzel
WMO = {
    0: ("Klar", "sun"),
    1: ("Überwiegend klar", "sun"),
    2: ("Teils wolkig", "partly"),
    3: ("Bedeckt", "cloud"),
    45: ("Nebel", "fog"),
    48: ("Reifnebel", "fog"),
    51: ("Leichter Nieselregen", "drizzle"),
    53: ("Nieselregen", "drizzle"),
    55: ("Starker Nieselregen", "drizzle"),
    56: ("Gefrierender Niesel", "drizzle"),
    57: ("Gefrierender Niesel", "drizzle"),
    61: ("Leichter Regen", "rain"),
    63: ("Regen", "rain"),
    65: ("Starker Regen", "rain"),
    66: ("Gefrierender Regen", "rain"),
    67: ("Gefrierender Regen", "rain"),
    71: ("Leichter Schneefall", "snow"),
    73: ("Schneefall", "snow"),
    75: ("Starker Schneefall", "snow"),
    77: ("Schneegriesel", "snow"),
    80: ("Leichte Schauer", "rain"),
    81: ("Schauer", "rain"),
    82: ("Starke Schauer", "rain"),
    85: ("Schneeschauer", "snow"),
    86: ("Schneeschauer", "snow"),
    95: ("Gewitter", "storm"),
    96: ("Gewitter mit Hagel", "storm"),
    99: ("Gewitter mit Hagel", "storm"),
}


def describe(code):
    return WMO.get(code, ("Unbekannt", "cloud"))


def fetch(cfg):
    loc = cfg["location"]
    url = (
        "{api}?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,apparent_temperature,weather_code,relative_humidity_2m,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max"
        "&forecast_days=4&timezone={tz}"
    ).format(api=API, lat=loc["latitude"], lon=loc["longitude"], tz=loc["timezone"])

    data = http_get(url)
    cur = data["current"]
    day = data["daily"]

    text, icon = describe(int(cur["weather_code"]))
    out = {
        "place": loc["name"],
        "temp": round(float(cur["temperature_2m"])),
        "feels": round(float(cur["apparent_temperature"])),
        "humidity": round(float(cur["relative_humidity_2m"])),
        "wind": round(float(cur["wind_speed_10m"])),
        "text": text,
        "icon": icon,
        "days": [],
    }
    for i in range(min(4, len(day["time"]))):
        d_text, d_icon = describe(int(day["weather_code"][i]))
        out["days"].append({
            "date": day["time"][i],
            "tmax": round(float(day["temperature_2m_max"][i])),
            "tmin": round(float(day["temperature_2m_min"][i])),
            "rain": int(day["precipitation_probability_max"][i] or 0),
            "icon": d_icon,
            "text": d_text,
        })
    return out
