# utils/api.py
# utils/api.py
import requests
import json

# ----------------------------
# USGS Earthquake Alerts
# ----------------------------
def fetch_usgs_alerts():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

# ----------------------------
# NWS Weather Alerts (USA)
# ----------------------------
def fetch_nws_alerts():
    url = "https://api.weather.gov/alerts/active"
    headers = {"User-Agent": "DisasterDashboard/1.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

# ----------------------------
# BOM Weather Warnings (Australia)
# ----------------------------
def fetch_bom_warnings():
    url = "https://api.weather.bom.gov.au/v1/warnings"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

# ----------------------------
# IMD Weather Alerts (India) - Example Static Feed
# ----------------------------
def fetch_imd_alerts():
    # IMD does not have an official public API; replace with real feed if available.
    # For demo, load from GitHub raw or local sample file
    try:
        url = "https://raw.githubusercontent.com/yourusername/disaster-alert-dashboard/main/sample_data/sample_imd.json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []




