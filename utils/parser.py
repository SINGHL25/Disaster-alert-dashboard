# utils/parser.py
# utils/parser.py
import pandas as pd
from datetime import datetime

def unify_alerts_to_df(alerts_dict):
    """Unify alerts from multiple sources into one DataFrame."""
    all_rows = []

    for source, data in alerts_dict.items():
        if not data:
            continue

        # USGS Earthquake format
        if source == "USGS" and "features" in data:
            for feat in data["features"]:
                props = feat.get("properties", {})
                all_rows.append({
                    "source": source,
                    "title": props.get("title"),
                    "date": pd.to_datetime(props.get("time"), unit="ms", errors="coerce"),
                    "severity": props.get("alert", "info"),
                    "area": props.get("place"),
                    "category": "earthquake"
                })

        # NWS Alerts
        elif source == "NWS" and "features" in data:
            for feat in data["features"]:
                props = feat.get("properties", {})
                all_rows.append({
                    "source": source,
                    "title": props.get("headline"),
                    "date": pd.to_datetime(props.get("onset"), errors="coerce"),
                    "severity": props.get("severity", "unknown"),
                    "area": props.get("areaDesc"),
                    "category": props.get("event", "weather")
                })

        # BOM (Australia)
        elif source == "BOM" and isinstance(data, dict):
            warnings = data.get("warnings", [])
            for w in warnings:
                all_rows.append({
                    "source": source,
                    "title": w.get("title"),
                    "date": pd.to_datetime(w.get("issue_time_utc"), errors="coerce"),
                    "severity": w.get("severity", "unknown"),
                    "area": w.get("area", "N/A"),
                    "category": w.get("type", "weather")
                })

        # IMD (India)
        elif source == "IMD" and isinstance(data, list):
            for w in data:
                all_rows.append({
                    "source": source,
                    "title": w.get("title"),
                    "date": pd.to_datetime(w.get("date"), errors="coerce"),
                    "severity": w.get("severity", "unknown"),
                    "area": w.get("area", "N/A"),
                    "category": w.get("category", "weather")
                })

    # Create DataFrame
    df = pd.DataFrame(all_rows)

    # Ensure date column exists
    if not df.empty:
        if "date" not in df.columns:
            df["date"] = pd.NaT
        df = df.sort_values("date", ascending=False)

        # Ensure category column exists
        if "category" not in df.columns or df["category"].isnull().all():
            df["category"] = df.get("source", "unknown")

    return df





