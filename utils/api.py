# utils/api.py
import json
import requests
import pandas as pd
from pathlib import Path
from .parser import load_file, clean_events

# ========================
# USGS Earthquake Alerts
# ========================
def fetch_usgs_alerts():
    """
    Fetch recent earthquake data from USGS.
    Returns standardized DataFrame.
    """
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rows = []
        for feat in data.get("features", []):
            props = feat["properties"]
            coords = feat["geometry"]["coordinates"]
            rows.append({
                "id": feat["id"],
                "title": props.get("title", "Earthquake"),
                "description": f"Magnitude {props.get('mag', 'N/A')} earthquake",
                "category": "Earthquake",
                "severity": "Moderate" if props.get("mag", 0) < 6 else "Severe",
                "urgency": "Immediate",
                "area": props.get("place", ""),
                "coordinates": [coords[0], coords[1]],
                "source": "USGS",
                "date": pd.to_datetime(props.get("time"), unit="ms")
            })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"USGS fetch error: {e}")
        return pd.DataFrame()

# ========================
# NWS (US National Weather Service)
# ========================
def fetch_nws_alerts():
    """
    Fetch US weather alerts from NWS API.
    """
    url = "https://api.weather.gov/alerts/active"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rows = []
        for feat in data.get("features", []):
            props = feat["properties"]
            area_desc = props.get("areaDesc", "")
            coords = None
            if "geometry" in feat and feat["geometry"]:
                coords = feat["geometry"]["coordinates"][0][0] if feat["geometry"]["coordinates"] else None
            rows.append({
                "id": props.get("id", ""),
                "title": props.get("headline", "Weather Alert"),
                "description": props.get("description", ""),
                "category": props.get("event", "Weather"),
                "severity": props.get("severity", "Unknown"),
                "urgency": props.get("urgency", "Expected"),
                "area": area_desc,
                "coordinates": coords,
                "source": "NWS",
                "date": pd.to_datetime(props.get("sent"))
            })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"NWS fetch error: {e}")
        return pd.DataFrame()

# ========================
# BOM Australia Warnings
# ========================
def fetch_bom_warnings():
    """
    Fetch BOM Australia warnings (demo feed).
    """
    url = "https://api.weather.bom.gov.au/v1/warnings"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        tmp = Path("/tmp/bom.json")
        tmp.write_text(resp.text, encoding="utf-8")
        df = load_file(tmp)
        return clean_events(df)
    except Exception as e:
        print(f"BOM fetch error: {e}")
        sample_path = Path(__file__).parent.parent / "data" / "sample_bom.json"
        if sample_path.exists():
            return clean_events(load_file(sample_path))
        return pd.DataFrame()

# ========================
# IMD India Alerts
# ========================
def fetch_imd_alerts():
    """
    Fetch IMD India alerts from API or fallback to sample file.
    """
    imd_url = "https://internal-imd.gov.in/api/alerts"  # placeholder, needs replacement
    try:
        resp = requests.get(imd_url, timeout=10)
        resp.raise_for_status()
        tmp = Path("/tmp/imd.json")
        tmp.write_text(resp.text, encoding="utf-8")
        df = load_file(tmp)
        return clean_events(df)
    except Exception as e:
        print(f"IMD fetch failed, using sample file: {e}")
        sample_path = Path(__file__).parent.parent / "data" / "sample_imd.json"
        if sample_path.exists():
            return clean_events(load_file(sample_path))
        return pd.DataFrame()


