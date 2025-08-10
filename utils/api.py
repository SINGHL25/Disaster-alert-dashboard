# utils/api.py
import requests

def fetch_usgs_alerts():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    data = requests.get(url, timeout=10).json()
    alerts = []
    for feature in data["features"]:
        alerts.append({
            "date": feature["properties"]["time"],
            "source": "USGS",
            "area": feature["properties"]["place"],
            "severity": "moderate",
            "category": "earthquake",
            "title": feature["properties"]["title"],
            "description": feature["properties"]["title"]
        })
    return alerts

def fetch_nws_alerts():
    url = "https://api.weather.gov/alerts/active"
    data = requests.get(url, timeout=10).json()
    alerts = []
    for feature in data["features"]:
        alerts.append({
            "date": feature["properties"]["sent"],
            "source": "NWS",
            "area": feature["properties"]["areaDesc"],
            "severity": feature["properties"]["severity"].lower(),
            "category": feature["properties"]["event"],
            "title": feature["properties"]["headline"],
            "description": feature["properties"]["description"]
        })
    return alerts

def fetch_bom_warnings():
    url = "https://reg.bom.gov.au/fwo/IDZ00054.warnings.json"
    try:
        return requests.get(url, timeout=10).json()["warnings"]
    except Exception:
        raise

def fetch_imd_alerts():
    url = "https://mausam.imd.gov.in/api/alerts"  # Example placeholder
    try:
        return requests.get(url, timeout=10).json()["alerts"]
    except Exception:
        raise


