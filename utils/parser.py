# utils/parser.py
# utils/parser.py
import pandas as pd
from datetime import datetime

def unify_alerts_to_df(alerts_dict):
    """
    Convert alerts from multiple APIs (USGS, NWS, BOM, IMD) into one DataFrame.
    """
    records = []

    # USGS feed
    if "USGS" in alerts_dict and alerts_dict["USGS"]:
        for feat in alerts_dict["USGS"].get("features", []):
            props = feat.get("properties", {})
            records.append({
                "source": "USGS",
                "title": props.get("title"),
                "area": props.get("place"),
                "severity": props.get("alert") or "N/A",
                "date": datetime.utcfromtimestamp(props.get("time", 0) / 1000) if props.get("time") else None,
                "details": props.get("url")
            })

    # NWS feed
    if "NWS" in alerts_dict and alerts_dict["NWS"]:
        for feat in alerts_dict["NWS"].get("features", []):
            props = feat.get("properties", {})
            records.append({
                "source": "NWS",
                "title": props.get("headline"),
                "area": props.get("areaDesc"),
                "severity": props.get("severity"),
                "date": pd.to_datetime(props.get("effective")),
                "details": props.get("description")
            })

    # BOM feed
    if "BOM" in alerts_dict and alerts_dict["BOM"]:
        # Adapt to BOM JSON structure
        if isinstance(alerts_dict["BOM"], dict) and "warnings" in alerts_dict["BOM"]:
            for w in alerts_dict["BOM"]["warnings"]:
                records.append({
                    "source": "BOM",
                    "title": w.get("title"),
                    "area": w.get("area", {}).get("description"),
                    "severity": w.get("severity", "N/A"),
                    "date": pd.to_datetime(w.get("issued_at")),
                    "details": w.get("description")
                })

    # IMD feed
    if "IMD" in alerts_dict and alerts_dict["IMD"]:
        if isinstance(alerts_dict["IMD"], list):
            for alert in alerts_dict["IMD"]:
                records.append({
                    "source": "IMD",
                    "title": alert.get("title"),
                    "area": alert.get("area"),
                    "severity": alert.get("severity", "N/A"),
                    "date": pd.to_datetime(alert.get("date")),
                    "details": alert.get("details")
                })

    # Build DataFrame
    df = pd.DataFrame(records)

    # Ensure datetime conversion
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values("date", ascending=False)

    return df



