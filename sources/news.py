"""Schlagzeilen aus RSS- und Atom-Feeds. Nur Titel, keine Artikeltexte."""
import re
import xml.etree.ElementTree as ET
from . import http_get

NS = {"atom": "http://www.w3.org/2005/Atom"}


def _clean(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&amp;", "&").replace("&quot;", '"')
                .replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&apos;", "'").replace("&nbsp;", " "))
    return " ".join(text.split())


def _titles(xml_text, limit):
    root = ET.fromstring(xml_text)
    titles = []
    # RSS 2.0
    for item in root.iter("item"):
        t = item.find("title")
        if t is not None and t.text:
            titles.append(_clean(t.text))
        if len(titles) >= limit:
            return titles
    # Atom
    for entry in root.findall(".//atom:entry", NS):
        t = entry.find("atom:title", NS)
        if t is not None and t.text:
            titles.append(_clean(t.text))
        if len(titles) >= limit:
            return titles
    return titles


def fetch(cfg):
    nc = cfg.get("news") or {}
    out = []
    for feed in nc.get("feeds", []):
        try:
            xml_text = http_get(feed["url"], as_json=False)
            for title in _titles(xml_text, int(feed.get("max", 3))):
                out.append({"source": feed["label"], "title": title})
        except Exception as exc:
            out.append({"source": feed["label"], "title": "[nicht erreichbar: {}]".format(exc.__class__.__name__)})
    return out[: int(nc.get("max_items", 6))]
