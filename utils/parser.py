# utils/parser.py
import pandas as pd
from datetime import datetime
import pytz

def _usgs_feature_to_row(f):
    prop = f.get("properties", {})
    geom = f.get("geometry", {}) or {}
    coords = geom.get("coordinates") or [None, None, None]
    lon, lat = coords[0], coords[1] if len(coords) >= 2 else (None, None)
    mag = prop.get("mag")
    place = prop.get("place")
    time_ms = prop.get("time")
    ts = datetime.utcfromtimestamp(time_ms/1000) if time_ms else None
    return {
        "id": f.get("id"),
        "title": f"{'Earthquake'}: M{mag} {place}" if place else f"Earthquake M{mag}",
        "description": prop.get("title") or prop.get("detail") or "",
        "category": "earthquake",
        "severity": "warning" if (mag and mag >= 5.0) else "advisory",
        "urgency": None,
        "area": place,
        "lat": lat,
        "lon": lon,
        "source": "USGS",
        "date": ts,
        "raw": f
    }

def _nws_feature_to_row(f):
    prop = f.get("properties", {})
    title = prop.get("headline") or prop.get("event") or prop.get("headline")
    desc = prop.get("description") or prop.get("instruction") or ""
    severity = prop.get("severity") or ""
    area = prop.get("areaDesc") or prop.get("affectedZones") or ""
    sent = prop.get("sent")
    try:
        ts = pd.to_datetime(sent)
    except Exception:
        ts = None
    geom = prop.get("geometry") or {}
    # if geometry present: get a coordinate
    lat = lon = None
    if geom:
        coords = geom.get("coordinates")
        if isinstance(coords, list) and len(coords) >= 2:
            lon, lat = coords[0], coords[1]
    return {
        "id": prop.get("id") or prop.get("@id"),
        "title": title,
        "description": desc,
        "category": prop.get("event") or "weather",
        "severity": severity,
        "urgency": prop.get("urgency"),
        "area": area,
        "lat": lat,
        "lon": lon,
        "source": "NWS",
        "date": ts,
        "raw": f
    }

def _bom_to_rows(raw):
    """
    raw: sample JSON structure for BOM. This is a heuristic parser for sample data.
    If your BOM source differs, modify this function accordingly.
    """
    rows = []
    if not raw:
        return rows
    # If raw contains 'warnings' or similar key
    items = None
    if isinstance(raw, dict):
        if "features" in raw:
            items = raw["features"]
            # treat like geojson
            for f in items:
                prop = f.get("properties", {})
                rows.append({
                    "id": prop.get("id"),
                    "title": prop.get("headline") or prop.get("type") or "BOM warning",
                    "description": prop.get("description") or "",
                    "category": prop.get("type") or "bom",
                    "severity": prop.get("severity") or "",
                    "urgency": prop.get("urgency") or "",
                    "area": prop.get("areaName") or prop.get("areaDesc") or "",
                    "lat": None,
                    "lon": None,
                    "source": "BOM",
                    "date": pd.to_datetime(prop.get("issueTime")) if prop.get("issueTime") else None,
                    "raw": f
                })
            return rows
    # generic fallback: try to flatten dict
    if isinstance(raw, list):
        for r in raw:
            rows.append({
                "id": r.get("id") if isinstance(r, dict) else None,
                "title": r.get("title") if isinstance(r, dict) else str(r),
                "description": r.get("description") if isinstance(r, dict) else "",
                "category": "bom",
                "severity": r.get("severity") if isinstance(r, dict) else "",
                "urgency": None,
                "area": r.get("area") if isinstance(r, dict) else "",
                "lat": None,
                "lon": None,
                "source": "BOM",
                "date": pd.to_datetime(r.get("date")) if isinstance(r, dict) and r.get("date") else None,
                "raw": r
            })
    return rows

def _imd_to_rows(raw):
    # IMD sample parsing stub
    rows = []
    if not raw:
        return rows
    if isinstance(raw, list):
        for r in raw:
            rows.append({
                "id": r.get("id"),
                "title": r.get("title"),
                "description": r.get("desc") or r.get("description") or "",
                "category": r.get("category") or "imd",
                "severity": r.get("severity") or "",
                "urgency": r.get("urgency") or "",
                "area": r.get("area") or "",
                "lat": r.get("lat"),
                "lon": r.get("lon"),
                "source": "IMD",
                "date": pd.to_datetime(r.get("date")) if r.get("date") else None,
                "raw": r
            })
    elif isinstance(raw, dict):
        # try common keys
        for k, v in raw.items():
            rows.extend(_imd_to_rows(v))
    return rows

def unify_alerts_to_df(sources: dict):
    """
    Input: dict returned from utils.api.fetch_all-like functions
    Output: pandas DataFrame with unified schema:
      id,title,description,category,severity,urgency,area,lat,lon,source,date,raw
    """
    rows = []
    # USGS
    usgs = sources.get("USGS")
    if usgs:
        for f in usgs:
            try:
                rows.append(_usgs_feature_to_row(f))
            except Exception:
                continue
    nws = sources.get("NWS")
    if nws:
        for f in nws:
            try:
                rows.append(_nws_feature_to_row(f))
            except Exception:
                continue
    bom = sources.get("BOM")
    if bom:
        try:
            rows.extend(_bom_to_rows(bom))
        except Exception:
            pass
    imd = sources.get("IMD")
    if imd:
        try:
            rows.extend(_imd_to_rows(imd))
        except Exception:
            pass

    # If sources includes raw sample lists (like dict keys), also try to parse them:
    # if user passed features under other keys: try to auto-detect features key
    for k,v in sources.items():
        if k in ("USGS","NWS","BOM","IMD"):
            continue
        if isinstance(v, dict) and "features" in v:
            for f in v.get("features", []):
                # guess USGS-like
                try:
                    rows.append(_usgs_feature_to_row(f))
                except Exception:
                    pass

    df = pd.DataFrame(rows)
    # Ensure required columns exist
    for c in ["id","title","description","category","severity","urgency","area","lat","lon","source","date","raw"]:
        if c not in df.columns:
            df[c] = None
    # Normalize date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

