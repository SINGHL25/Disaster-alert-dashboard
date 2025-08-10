# utils/api.py
import json
import requests
from pathlib import Path
import pandas as pd
from .parser import load_file, clean_events

def fetch_bom_alerts():
    """
    Fetch BOM Australia alerts from the official GeoJSON feed.
    Returns DataFrame.
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
        return pd.DataFrame()


def fetch_imd_alerts():
    """
    Fetch IMD India alerts from live API if available.
    Fallback to sample_imd.json in /data if fetch fails.
    """
    # Hypothetical IMD API endpoint (real ones often require scraping or RSS)
    imd_url = "https://internal-imd.gov.in/api/alerts"  # Replace with actual
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


def fetch_local_samples():
    """
    Load both BOM and IMD sample files from /data.
    """
    data_dir = Path(__file__).parent.parent / "data"
    dfs = []
    for file in data_dir.glob("*.json"):
        df = load_file(file)
        if not df.empty:
            dfs.append(clean_events(df))
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


