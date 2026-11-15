# -*- coding: utf-8 -*-
"""Zeichnet das Dashboard-Bild. Reines Pillow, kein Browser - laeuft auf einem Pi Zero."""
import datetime
from PIL import Image, ImageDraw, ImageFont

BLACK, WHITE, GRAY = 0, 255, 128

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/dejavu/",
]

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
WT_KURZ = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]


def _font(name, size):
    import os
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise RuntimeError("Schriftart nicht gefunden: " + name + " - bitte fonts-dejavu installieren")


def fonts():
    return {
        "huge":    _font("DejaVuSans-Bold.ttf", 150),
        "h1":      _font("DejaVuSans-Bold.ttf", 46),
        "h2":      _font("DejaVuSans-Bold.ttf", 34),
        "day":     _font("DejaVuSans-Bold.ttf", 32),
        "tmax":    _font("DejaVuSans-Bold.ttf", 40),
        "body":    _font("DejaVuSans.ttf", 36),
        "news":    _font("DejaVuSans.ttf", 34),
        "cond":    _font("DejaVuSans.ttf", 42),
        "small":   _font("DejaVuSans.ttf", 30),
        "tiny":    _font("DejaVuSans.ttf", 24),
        "tag":     _font("DejaVuSans-Bold.ttf", 23),
    }


# ---------------------------------------------------------------- Wetter-Icons

def icon(d, x, y, s, kind):
    """Zeichnet ein Wettersymbol der Groesse s mit linker oberer Ecke (x, y)."""
    w = max(3, s // 22)

    def sun(cx, cy, r):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLACK, width=w)
        import math
        for i in range(8):
            a = math.radians(i * 45)
            d.line([cx + math.cos(a) * (r + r * 0.28), cy + math.sin(a) * (r + r * 0.28),
                    cx + math.cos(a) * (r + r * 0.62), cy + math.sin(a) * (r + r * 0.62)],
                   fill=BLACK, width=w)

    def cloud(cx, cy, cw):
        r1, r2, r3 = cw * 0.26, cw * 0.34, cw * 0.22
        d.ellipse([cx - cw * 0.42, cy - r1, cx - cw * 0.42 + 2 * r1, cy + r1], outline=BLACK, width=w, fill=WHITE)
        d.ellipse([cx - cw * 0.12, cy - r2 * 1.25, cx - cw * 0.12 + 2 * r2, cy + r2 * 0.75], outline=BLACK, width=w, fill=WHITE)
        d.ellipse([cx + cw * 0.18, cy - r3, cx + cw * 0.18 + 2 * r3, cy + r3], outline=BLACK, width=w, fill=WHITE)
        d.rectangle([cx - cw * 0.42, cy + r1 - w, cx + cw * 0.18 + 2 * r3, cy + r1], fill=WHITE)
        d.line([cx - cw * 0.40, cy + r1, cx + cw * 0.60, cy + r1], fill=BLACK, width=w)

    cx, cy = x + s / 2, y + s / 2

    if kind == "sun":
        sun(cx, cy, s * 0.26)
    elif kind == "partly":
        sun(cx + s * 0.18, cy - s * 0.18, s * 0.18)
        cloud(cx - s * 0.06, cy + s * 0.10, s * 0.78)
    elif kind == "cloud":
        cloud(cx, cy, s * 0.86)
    elif kind in ("rain", "drizzle"):
        cloud(cx, cy - s * 0.12, s * 0.80)
        for i in range(3):
            lx = cx - s * 0.22 + i * s * 0.22
            if kind == "rain":
                d.line([lx, cy + s * 0.20, lx - s * 0.05, cy + s * 0.40], fill=BLACK, width=w)
            else:
                d.ellipse([lx - w, cy + s * 0.26, lx + w, cy + s * 0.26 + 2 * w], fill=BLACK)
    elif kind == "snow":
        cloud(cx, cy - s * 0.12, s * 0.80)
        for i in range(3):
            lx = cx - s * 0.22 + i * s * 0.22
            ly = cy + s * 0.30
            for a in (0, 60, 120):
                import math
                r = math.radians(a)
                d.line([lx - math.cos(r) * s * 0.06, ly - math.sin(r) * s * 0.06,
                        lx + math.cos(r) * s * 0.06, ly + math.sin(r) * s * 0.06], fill=BLACK, width=w)
    elif kind == "fog":
        for i in range(4):
            yy = cy - s * 0.18 + i * s * 0.14
            inset = s * (0.10 if i % 2 == 0 else 0.20)
            d.line([x + inset, yy, x + s - inset, yy], fill=BLACK, width=w)
    elif kind == "storm":
        cloud(cx, cy - s * 0.14, s * 0.80)
        d.line([cx + s * 0.02, cy + s * 0.14, cx - s * 0.10, cy + s * 0.30], fill=BLACK, width=w)
        d.line([cx - s * 0.10, cy + s * 0.30, cx + s * 0.06, cy + s * 0.30], fill=BLACK, width=w)
        d.line([cx + s * 0.06, cy + s * 0.30, cx - s * 0.06, cy + s * 0.46], fill=BLACK, width=w)
    else:
        cloud(cx, cy, s * 0.86)


# ------------------------------------------------------------------- Texthilfe

def wrap(d, text, font, max_w, max_lines=2):
    words, lines, cur = text.split(), [], ""
    for word in words:
        probe = (cur + " " + word).strip()
        if d.textlength(probe, font=font) <= max_w:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words:
        while lines and d.textlength(lines[-1] + " ...", font=font) > max_w and len(lines[-1]) > 4:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-2]
        joined = " ".join(lines)
        if len(joined) < len(text) - 1:
            lines[-1] = lines[-1] + " ..."
    return lines


# --------------------------------------------------------------- Gesamtlayout

def compose(data, cfg, stand=None):
    W = cfg["display"]["width"]
    H = cfg["display"]["height"]
    M = 44
    img = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    f = fonts()
    now = stand or datetime.datetime.now()

    # ---- Kopfzeile
    y = M
    datum = "{wt}, {t}. {mon}".format(wt=WOCHENTAGE[now.weekday()], t=now.day, mon=MONATE[now.month - 1])
    d.text((M, y), datum, font=f["h1"], fill=BLACK)
    stand_txt = "Stand {:%H:%M}".format(now)
    d.text((W - M - d.textlength(stand_txt, font=f["small"]), y + 12), stand_txt, font=f["small"], fill=BLACK)
    y += 72
    d.line([M, y, W - M, y], fill=BLACK, width=3)

    # ---- Wetter gross
    w = data.get("weather")
    y += 34
    if w:
        icon(d, M, y, 200, w["icon"])
        tx = M + 240
        temp = "{}°".format(w["temp"])
        d.text((tx, y - 26), temp, font=f["huge"], fill=BLACK)
        tw = d.textlength(temp, font=f["huge"])
        d.text((tx, y + 150), w["text"], font=f["cond"], fill=BLACK)
        detail = "gefühlt {f}°   {h}% Luftf.   {wd} km/h   {place}".format(
            f=w["feels"], h=w["humidity"], wd=w["wind"], place=w["place"])
        d.text((tx, y + 206), detail, font=f["tiny"], fill=BLACK)
        y += 262

        # ---- 4-Tage-Streifen
        d.line([M, y, W - M, y], fill=GRAY, width=2)
        y += 26
        colw = (W - 2 * M) / 4.0
        for i, day in enumerate(w["days"]):
            cx = M + colw * i
            dt = datetime.date.fromisoformat(day["date"])
            label = "heute" if i == 0 else WT_KURZ[dt.weekday()]
            lw = d.textlength(label, font=f["day"])
            d.text((cx + colw / 2 - lw / 2, y), label, font=f["day"], fill=BLACK)
            icon(d, cx + colw / 2 - 46, y + 44, 92, day["icon"])
            t_txt = "{}°".format(day["tmax"])
            t2_txt = " / {}°".format(day["tmin"])
            t_w = d.textlength(t_txt, font=f["tmax"])
            t2_w = d.textlength(t2_txt, font=f["small"])
            start = cx + colw / 2 - (t_w + t2_w) / 2
            d.text((start, y + 148), t_txt, font=f["tmax"], fill=BLACK)
            d.text((start + t_w, y + 158), t2_txt, font=f["small"], fill=BLACK)
            r_txt = "{}%".format(day["rain"])
            rw = d.textlength(r_txt, font=f["tiny"])
            d.text((cx + colw / 2 - rw / 2, y + 198), r_txt, font=f["tiny"], fill=BLACK)
            if i < 3:
                d.line([cx + colw, y + 10, cx + colw, y + 220], fill=GRAY, width=1)
        y += 250

    # ---- Boerse (nur wenn aktiviert und Daten vorhanden)
    stocks = data.get("stocks") or []
    if stocks:
        d.line([M, y, W - M, y], fill=BLACK, width=3)
        y += 22
        for s in stocks:
            d.text((M, y), s["label"], font=f["body"], fill=BLACK)
            val = "{:,.2f}".format(s["value"]).replace(",", ".")
            arrow = "+" if s["change_pct"] >= 0 else "-"
            chg = "{}{:.2f}%".format(arrow, abs(s["change_pct"]))
            cw_ = d.textlength(chg, font=f["body"])
            d.text((W - M - cw_, y), chg, font=f["body"], fill=BLACK)
            vw = d.textlength(val, font=f["small"])
            d.text((W - M - cw_ - 30 - vw, y + 6), val, font=f["small"], fill=BLACK)
            y += 54
        y += 10

    # ---- Nachrichten
    d.line([M, y, W - M, y], fill=BLACK, width=3)
    y += 24
    d.text((M, y), "NACHRICHTEN", font=f["h2"], fill=BLACK)
    y += 54

    footer_y = H - M - 30
    for item in data.get("news") or []:
        lines = wrap(d, item["title"], f["news"], W - 2 * M, max_lines=2)
        needed = 38 + len(lines) * 42 + 14
        if y + needed > footer_y - 16:
            # Passt die zweizeilige Meldung nicht mehr, aber eine einzeilige schon,
            # dann gekuerzt setzen statt Leerraum zu lassen.
            if len(lines) == 2 and y + 38 + 42 + 14 <= footer_y - 16:
                lines = wrap(d, item["title"], f["news"], W - 2 * M, max_lines=1)
            else:
                break
        tag = item["source"].upper()
        d.text((M, y), tag, font=f["tag"], fill=BLACK)
        d.line([M, y + 32, M + d.textlength(tag, font=f["tag"]), y + 32], fill=BLACK, width=2)
        y += 38
        for line in lines:
            d.text((M, y), line, font=f["news"], fill=BLACK)
            y += 42
        y += 14

    # ---- Fusszeile
    d.line([M, footer_y - 10, W - M, footer_y - 10], fill=GRAY, width=1)
    note = data.get("footer", "Wetter: Open-Meteo")
    d.text((M, footer_y), note, font=f["tiny"], fill=GRAY)
    return img


def save(img, path):
    img.save(path, "PNG", optimize=True)
    return path
