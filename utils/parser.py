# utils/parser.py
import pandas as pd

def unify_alerts_to_df(alert_dict):
    rows = []
    for source, alerts in alert_dict.items():
        for alert in alerts:
            rows.append({
                "date": alert.get("date"),
                "source": alert.get("source", source),
                "area": alert.get("area", ""),
                "severity": alert.get("severity", "unknown"),
                "category": alert.get("category", "general"),
                "title": alert.get("title", ""),
                "description": alert.get("description", "")
            })
    return pd.DataFrame(rows)



