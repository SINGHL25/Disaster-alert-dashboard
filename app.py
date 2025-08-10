# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.api import (
    fetch_usgs_alerts,
    fetch_nws_alerts,
    fetch_bom_warnings,
    fetch_imd_alerts
)
from utils.parser import unify_alerts_to_df

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="🌍 Disaster & Emergency Alert Dashboard",
    layout="wide"
)

st.title("🌍 Disaster & Emergency Alert Dashboard — USGS · NWS · BOM · IMD")
st.caption("Live feeds + sample data. Filters on the left. Data sources: USGS (earthquakes), NWS (US alerts), BOM (Australia), IMD (India).")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

default_end = datetime.utcnow()
default_start = default_end - timedelta(days=1)

start_date = st.sidebar.date_input("Start date", default_start.date())
end_date = st.sidebar.date_input("End date", default_end.date())

min_severity = st.sidebar.selectbox(
    "Minimum severity",
    ["any", "minor", "moderate", "severe", "extreme"]
)

# --- FETCH ALERT DATA ---
st.sidebar.subheader("Fetching data...")
try:
    alerts_dict = {
        "USGS": fetch_usgs_alerts(),
        "NWS": fetch_nws_alerts(),
        "BOM": fetch_bom_warnings(),
        "IMD": fetch_imd_alerts()
    }
except Exception as e:
    st.error(f"Error fetching alerts: {e}")
    alerts_dict = {}

# --- MERGE DATA ---
df = unify_alerts_to_df(alerts_dict)

# Ensure 'date' is datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

# --- APPLY FILTERS ---
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]

if min_severity != "any":
    df = df[df["severity"].str.lower() >= min_severity.lower()]

# --- DISPLAY SUMMARY ---
st.subheader("Summary of Alerts")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Files processed", len(alerts_dict))
col2.metric("Total alerts", len(df))
col3.metric("Unique areas", df["area"].nunique() if not df.empty else 0)
col4.metric("Data period", f"{df['date'].min().date()} → {df['date'].max().date()}" if not df.empty else "N/A")

# --- DISPLAY TABLE ---
st.subheader("Event Details Table")
if not df.empty:
    st.dataframe(df.sort_values("date"), use_container_width=True)
else:
    st.warning("No alerts match the selected filters.")

# --- PLOTS ---
if not df.empty:
    import plotly.express as px

    st.subheader("Alert Timeline")
    fig_timeline = px.scatter(
        df, x="date", y="severity", color="source",
        hover_data=["title", "area", "category"],
        title="Alerts Over Time"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.subheader("Alerts by Source")
    fig_counts = px.histogram(
        df, x="source", color="severity", barmode="group",
        title="Count of Alerts per Source"
    )
    st.plotly_chart(fig_counts, use_container_width=True)
else:
    st.info("No plots generated due to empty filtered data.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "App built for real-time disaster monitoring. "
    "Extendable to other data feeds. "
    "GitHub-ready folder structure."
)


