# utils/api.py
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

from utils.api import fetch_usgs_alerts, fetch_nws_alerts, fetch_bom_warnings, fetch_imd_alerts
from utils.parser import unify_alerts_to_df

st.set_page_config(page_title="🌍 Disaster & Emergency Alert Dashboard", layout="wide")

st.title("🌍 Disaster & Emergency Alert Dashboard — USGS · NWS · BOM · IMD")
st.caption("Live feeds + sample data. Filters on the left. Data sources: USGS (earthquakes), "
           "NWS (US alerts), BOM (Australia), IMD (India).")

# --------------------------
#  SAMPLE DATA PATHS
# --------------------------
BASE_DIR = Path(__file__).parent
SAMPLE_DATA = {
    "USGS": BASE_DIR / "sample_data" / "sample_usgs.json",
    "NWS": BASE_DIR / "sample_data" / "sample_nws.json",
    "BOM": BASE_DIR / "sample_data" / "sample_bom.json",
    "IMD": BASE_DIR / "sample_data" / "sample_imd.json"
}

# --------------------------
#  LOAD ALERTS
# --------------------------
alerts_dict = {}

# USGS
try:
    alerts_dict["USGS"] = fetch_usgs_alerts()
except Exception as e:
    st.warning(f"USGS fetch failed: {e} — using sample data.")
    if SAMPLE_DATA["USGS"].exists():
        alerts_dict["USGS"] = json.load(open(SAMPLE_DATA["USGS"], "r", encoding="utf-8"))
    else:
        alerts_dict["USGS"] = []

# NWS
try:
    alerts_dict["NWS"] = fetch_nws_alerts()
except Exception as e:
    st.warning(f"NWS fetch failed: {e} — using sample data.")
    if SAMPLE_DATA["NWS"].exists():
        alerts_dict["NWS"] = json.load(open(SAMPLE_DATA["NWS"], "r", encoding="utf-8"))
    else:
        alerts_dict["NWS"] = []

# BOM
try:
    alerts_dict["BOM"] = fetch_bom_warnings()
except Exception as e:
    st.warning(f"BOM fetch failed: {e} — using sample data.")
    if SAMPLE_DATA["BOM"].exists():
        alerts_dict["BOM"] = json.load(open(SAMPLE_DATA["BOM"], "r", encoding="utf-8"))
    else:
        alerts_dict["BOM"] = []

# IMD
try:
    alerts_dict["IMD"] = fetch_imd_alerts()
except Exception as e:
    st.warning(f"IMD fetch failed: {e} — using sample data.")
    if SAMPLE_DATA["IMD"].exists():
        alerts_dict["IMD"] = json.load(open(SAMPLE_DATA["IMD"], "r", encoding="utf-8"))
    else:
        alerts_dict["IMD"] = []

# --------------------------
#  UNIFY ALERTS INTO DF
# --------------------------
df = unify_alerts_to_df(alerts_dict)

# --------------------------
#  FILTER SIDEBAR
# --------------------------
st.sidebar.header("Filters")
today = datetime.utcnow().date()
start_date = st.sidebar.date_input("Start date", today - timedelta(days=1))
end_date = st.sidebar.date_input("End date", today)
min_severity = st.sidebar.selectbox("Minimum severity", ["any", "moderate", "severe"])

# --------------------------
#  APPLY FILTERS
# --------------------------
if not df.empty:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    if min_severity != "any":
        mask &= (df["severity"].str.lower() == min_severity.lower())
    df_filtered = df[mask]
else:
    df_filtered = pd.DataFrame()

# --------------------------
#  SUMMARY
# --------------------------
st.subheader("Summary of Alerts")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Files processed", len(alerts_dict))
col2.metric("Total alerts", len(df_filtered))
col3.metric("Unique areas", df_filtered["area"].nunique() if not df_filtered.empty else 0)
if not df_filtered.empty:
    col4.metric("Data period", f"{df_filtered['date'].min().date()} → {df_filtered['date'].max().date()}")
else:
    col4.metric("Data period", "N/A")

# --------------------------
#  EVENT DETAILS
# --------------------------
st.subheader("Event Details Table")
if not df_filtered.empty:
    st.dataframe(df_filtered, use_container_width=True)
else:
    st.info("No alerts match the selected filters.")

# --------------------------
#  FUTURE: MAP PLOTTING
# --------------------------
# We can add map visuals here for BOM & IMD alerts if lat/lon data is available.



