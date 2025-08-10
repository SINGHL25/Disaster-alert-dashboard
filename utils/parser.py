# utils/parser.py
import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path

def load_file(file_path):
    """
    Load and parse a file (JSON, CSV, TXT, LOG).
    Detects source type (BOM, IMD, generic logs).
    Returns DataFrame with unified schema.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix in [".json"]:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)

            # Detect IMD
            if _is_imd_json(raw):
                rows = _imd_to_rows(raw)
                return pd.DataFrame(rows)

            # Detect BOM
            if _is_bom_json(raw):
                rows = _bom_to_rows(raw)
                return pd.DataFrame(rows)

            # Unknown JSON -> flatten
            return pd.json_normalize(raw)

        elif suffix in [".csv", ".xls", ".xlsx"]:
            df = pd.read_csv(path) if suffix == ".csv" else pd.read_excel(path)
            return _normalize_csv(df)

        elif suffix in [".txt", ".log"]:
            return _parse_generic_log(path)

        else:
            print(f"Unsupported file type: {suffix}")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return pd.DataFrame()


def _is_imd_json(raw):
    """Detect if JSON is in IMD-like format."""
    if isinstance(raw, list):
        for r in raw:
            if isinstance(r, dict) and (
                "phenomenon" in r or "event_type" in r or "headline" in r
            ):
                return True
    if isinstance(raw, dict):
        for k in raw.keys():
            if "bulletin" in k.lower() or "imd" in k.lower():
                return True
    return False


def _is_bom_json(raw):
    """Detect if JSON is in BOM-like format."""
    if isinstance(raw, list):
        for r in raw:
            if isinstance(r, dict) and ("geometry" in r or "properties" in r):
                return True
    if isinstance(raw, dict):
        if "features" in raw and isinstance(raw["features"], list):
            return True
    return False


def _imd_to_rows(raw):
    """
    Robust IMD JSON parser for the sample structure above.
    Converts IMD entries (list or dict) into unified row dicts.
    """
    rows = []
    if not raw:
        return rows

    if isinstance(raw, list):
        for r in raw:
            _id = r.get("id") or r.get("bulletinId") or None
            title = r.get("headline") or r.get("event_type") or r.get("title") or ""
            description = r.get("description") or r.get("desc") or ""
            instruction = r.get("instruction") or r.get("advice") or ""
            severity = r.get("severity") or ""
            area = r.get("area") or r.get("region") or r.get("areaName") or ""
            lat = r.get("lat")
            lon = r.get("lon")
            issued = r.get("issued") or r.get("issueTime") or r.get("effective") or None

            try:
                date = pd.to_datetime(issued) if issued else None
            except Exception:
                date = None

            rows.append({
                "id": _id,
                "title": title,
                "description": description,
                "instruction": instruction,
                "category": r.get("phenomenon") or r.get("event_type") or "imd",
                "severity": severity,
                "urgency": r.get("urgency") or "",
                "area": area,
                "lat": lat,
                "lon": lon,
                "source": "IMD",
                "date": date,
                "raw": r
            })
        return rows

    if isinstance(raw, dict):
        for key in ("bulletins", "alerts", "warnings", "data", "items"):
            if key in raw and isinstance(raw[key], list):
                return _imd_to_rows(raw[key])
        for k, v in raw.items():
            if isinstance(v, list):
                rows.extend(_imd_to_rows(v))
        return rows

    return rows


def _bom_to_rows(raw):
    """
    Convert BOM GeoJSON or alert JSON to unified schema.
    """
    rows = []
    if isinstance(raw, dict) and "features" in raw:
        for feat in raw["features"]:
            props = feat.get("properties", {})
            coords = None
            if "geometry" in feat and feat["geometry"]:
                coords = feat["geometry"].get("coordinates")
            lat = lon = None
            if coords and isinstance(coords, (list, tuple)):
                lon, lat = coords[:2]

            title = props.get("headline") or props.get("event") or ""
            desc = props.get("description") or ""
            date_str = props.get("sent") or props.get("onset") or None
            try:
                date = pd.to_datetime(date_str) if date_str else None
            except Exception:
                date = None

            rows.append({
                "id": props.get("id") or props.get("event_id") or None,
                "title": title,
                "description": desc,
                "instruction": props.get("instruction") or "",
                "category": props.get("event") or "bom",
                "severity": props.get("severity") or "",
                "urgency": props.get("urgency") or "",
                "area": props.get("areaDesc") or "",
                "lat": lat,
                "lon": lon,
                "source": "BOM",
                "date": date,
                "raw": props
            })
    return rows


def _normalize_csv(df):
    """
    Try to standardize CSV to unified schema columns.
    """
    cols = [c.lower() for c in df.columns]
    mapping = {}
    for col in df.columns:
        lc = col.lower()
        if "title" in lc or "event" in lc:
            mapping[col] = "title"
        elif "desc" in lc:
            mapping[col] = "description"
        elif "severity" in lc:
            mapping[col] = "severity"
        elif "lat" in lc:
            mapping[col] = "lat"
        elif "lon" in lc or "long" in lc:
            mapping[col] = "lon"
        elif "area" in lc:
            mapping[col] = "area"
        elif "date" in lc or "time" in lc:
            mapping[col] = "date"
    df = df.rename(columns=mapping)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["source"] = "CSV"
    return df


def _parse_generic_log(path):
    """
    Parse TXT/LOG file with regex for datetime + severity + message.
    """
    rows = []
    pattern = re.compile(
        r'(?P<date>\d{4}[-/]\d{2}[-/]\d{2}[\sT]\d{2}:\d{2}:\d{2})'
        r'.*?(?P<severity>INFO|WARN|WARNING|ERROR|CRITICAL|ALARM)'
        r'.*?(?P<msg>.+)', re.IGNORECASE
    )

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                try:
                    date = pd.to_datetime(m.group("date"))
                except Exception:
                    date = None
                rows.append({
                    "id": None,
                    "title": m.group("msg").strip()[:50],
                    "description": m.group("msg").strip(),
                    "instruction": "",
                    "category": "log",
                    "severity": m.group("severity"),
                    "urgency": "",
                    "area": "",
                    "lat": None,
                    "lon": None,
                    "source": "LOG",
                    "date": date,
                    "raw": {"line": line.strip()}
                })
    return pd.DataFrame(rows)


def clean_events(df):
    """
    Standardize DataFrame columns and drop empty rows.
    """
    expected_cols = ["id","title","description","instruction","category",
                     "severity","urgency","area","lat","lon","source","date","raw"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    df = df[expected_cols]
    df = df.dropna(subset=["title", "date"], how="any")
    return df


def generate_summary(df):
    """
    Generate summary stats text for display.
    """
    if df.empty:
        return "No events found."
    total = len(df)
    critical_count = len(df[df["severity"].str.contains("Severe|Critical|Warning", case=False, na=False)])
    unique_categories = df["category"].nunique()
    period = f"{df['date'].min().date()} to {df['date'].max().date()}"
    return f"Period: {period}\nTotal Events: {total}\nCritical Events: {critical_count}\nUnique Categories: {unique_categories}"


