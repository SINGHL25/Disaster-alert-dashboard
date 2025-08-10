# utils/api.py
import requests
from datetime import datetime, timedelta
import json
from pathlib import Path

# ---------- USGS (Earthquakes) ----------
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_usgs_alerts():
    """Return raw feature list from USGS GeoJSON (earthquakes)."""
    resp = requests.get(USGS_URL, timeout=15)
    resp.raise_for_status()
    obj = resp.json()
    features = obj.get("features", [])
    return features

# ---------- NWS (US Weather Alerts) ----------
NWS_URL = "https://api.weather.gov/alerts"

def fetch_nws_alerts(area=None):
    """
    Fetch NWS alerts. Optionally filter by area/state code (e.g., 'CA').
    Returns list of features (GeoJSON-like).
    """
    params = {}
    if area:
        params["area"] = area
    resp = requests.get(NWS_URL, params=params, timeout=15, headers={"User-Agent":"disaster-dashboard/1.0"})
    resp.raise_for_status()
    obj = resp.json()
    features = obj.get("features", [])
    return features

# ---------- BOM Australia (STUB / sample) ----------
# BOM does not publish a single universal JSON feed publicly with stable endpoints.
# Users often use BOM XML/RSS or government data services. We include a sample loader fallback:
BOM_SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_bom.json"

def fetch_bom_warnings():
    """
    Attempt to fetch BOM warnings. By default this function will try well-known BOM endpoints,
    but also falls back to sample JSON in /data.
    If you have a BOM endpoint (e.g. FWO feed), replace or extend this function.
    """
    # Try a few heuristic endpoints (may fail)
    candidate_urls = [
        "http://www.bom.gov.au/fwo/IDN10001/IDN10001.json",  # example (may 404)
    ]
    for url in candidate_urls:
        try:
            r = requests.get(url, timeout=10)
            if r.ok:
                try:
                    return r.json()
                except Exception:
                    continue
        except Exception:
            continue

    # fallback: load sample JSON shipped with repo
    if BOM_SAMPLE.exists():
        with open(BOM_SAMPLE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ---------- IMD India (STUB / sample) ----------
IMD_SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_imd.json"

def fetch_imd_alerts():
    """
    IMD doesn't offer a widely documented public JSON API; many integrations require scraping or RSS.
    This function falls back to sample data. If you have a specific IMD feed endpoint, plug it in here.
    """
    # If you know an IMD endpoint, try it here (example left empty)
    # e.g. url = "https://mausam.imd.gov.in/some-endpoint.json"
    # try:
    #     r = requests.get(url, timeout=10)
    #     r.raise_for_status()
    #     return r.json()
    # except Exception:
    #     pass

    if IMD_SAMPLE.exists():
        import json
        with open(IMD_SAMPLE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

