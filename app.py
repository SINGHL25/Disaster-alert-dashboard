# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import fetch_usgs_alerts, fetch_nws_alerts, fetch_bom_warnings, fetch_imd_alerts
from utils.parser import unify_alerts_to_df
import json

st.set_page_config(page_title="🌍 Disaster & Emergency Alert Dashboard", layout="wide")

st.title("🌍 Disaster & Emergency Alert Dashboard — USGS · NWS · BOM · IMD")
st.caption("Live feeds + sample data. Filters on the left. Data sources: USGS (earthquakes), NWS (US alerts), BOM (Australia), IMD (India).")

# Sidebar Filters
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start date", datetime.utcnow().date())
end_date = st.sidebar.date_input("End date", datetime.utcnow().date())
min_severity = st.sidebar.selectbox("Minimum severity", ["any", "minor", "moderate", "severe", "extreme"])

# Load alerts with fallbacks
alerts_dict = {}

try:
    alerts_dict["USGS"] = fetch_usgs_alerts()
except Exception as e:
    st.warning(f"USGS fetch failed: {e}")
    alerts_dict["USGS"] = json.load(open("sample_data/sample_usgs.json"))

try:
    alerts_dict["NWS"] = fetch_nws_alerts()
except Exception as e:
    st.warning(f"NWS fetch failed: {e}")
    alerts_dict["NWS"] = json.load(open("sample_data/sample_nws.json"))

try:
    alerts_dict["BOM"] = fetch_bom_warnings()
except Exception as e:
    st.warning(f"BOM fetch failed: {e} — using sample data.")
    alerts_dict["BOM"] = json.load(open("sample_data/sample_bom.json"))

try:
    alerts_dict["IMD"] = fetch_imd_alerts()
except Exception as e:
    st.warning(f"IMD fetch failed: {e} — using sample data.")
    alerts_dict["IMD"] = json.load(open("sample_data/sample_imd.json"))

# Merge into DataFrame
df = unify_alerts_to_df(alerts_dict)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

# Apply filters
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1)
df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]

if min_severity != "any":
    df = df[df["severity"].str.lower() >= min_severity.lower()]

# Summary
st.subheader("Summary of Alerts")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Files processed", len(alerts_dict))
col2.metric("Total alerts", len(df))
col3.metric("Unique areas", df["area"].nunique())
col4.metric("Data period", f"{df['date'].min()} — {df['date'].max()}" if not df.empty else "N/A")

# Table
st.subheader("Event Details Table")
if not df.empty:
    st.dataframe(df)
else:
    st.write("No alerts match the selected filters.")

# Plots
if not df.empty:
    st.subheader("Top Event Counts")
    st.bar_chart(df["category"].value_counts())



