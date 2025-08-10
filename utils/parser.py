# utils/parser.py
import pandas as pd
from pathlib import Path
import json

def load_file(file_path: Path) -> pd.DataFrame:
    """
    Load a file into a DataFrame based on extension.
    Supports JSON, CSV, XLS/XLSX, TXT/LOG.
    """
    ext = file_path.suffix.lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    elif ext in [".json"]:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    elif ext in [".txt", ".log"]:
        # Treat as generic log lines
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return pd.DataFrame({"raw_text": [l.strip() for l in lines if l.strip()]})
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def clean_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize alert/event DataFrame columns.
    Ensures required columns exist.
    """
    required_cols = [
        "id", "title", "description", "category", "severity",
        "urgency", "area", "coordinates", "source", "date"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df[required_cols]

def unify_alerts_to_df(alert_sources: dict) -> pd.DataFrame:
    """
    Merge multiple alert DataFrames into one unified DataFrame.
    alert_sources: dict { "source_name": df, ... }
    """
    all_frames = []
    for source, df in alert_sources.items():
        if not df.empty:
            df["source"] = source
            all_frames.append(df)
    if not all_frames:
        return pd.DataFrame(columns=[
            "id", "title", "description", "category", "severity",
            "urgency", "area", "coordinates", "source", "date"
        ])
    return pd.concat(all_frames, ignore_index=True)

def filter_alerts(df: pd.DataFrame, start_date=None, end_date=None, severity=None) -> pd.DataFrame:
    """
    Filter alerts by date range and severity.
    """
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]
    if severity and len(severity) > 0:
        df = df[df["severity"].isin(severity)]
    return df



