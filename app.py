# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.api import fetch_usgs_alerts, fetch_nws_alerts, fetch_bom_warnings, fetch_imd_alerts
from utils.parser import unify_alerts_to_df
from utils.visuals import render_map, render_timeline, render_counts

st.set_page_config(page_title="Global Disaster & Emergency Alert System", layout="wide")

st.title("🌍 Disaster & Emergency Alert Dashboard — USGS · NWS · BOM · IMD")
st.markdown("Live feeds + sample data. Filters on the left. Data sources: USGS (earthquakes), NWS (US alerts). BOM & IMD helpers included (see README).")

# Sidebar: options
with st.sidebar:
    st.header("Data sources")
    use_usgs = st.checkbox("USGS (Earthquakes)", value=True)
    use_nws = st.checkbox("NWS (US Weather Alerts)", value=True)
    use_bom = st.checkbox("BOM Australia (sample/stub)", value=False)
    use_imd = st.checkbox("IMD India (sample/stub)", value=False)

    st.markdown("---")
    st.header("Filters")
    days = st.slider("Show last N days", min_value=0, max_value=30, value=1)
    start_dt = st.date_input("Start date", value=(datetime.utcnow().date() - timedelta(days=days)))
    end_dt = st.date_input("End date", value=datetime.utcnow().date())
    min_severity = st.selectbox("Minimum severity", options=["any","advisory","watch","warning","severe","critical"], index=0)

    st.markdown("---")
    st.header("Actions")
    refresh = st.button("Fetch / Refresh feeds")

# Fetch / load data
@st.cache_data(ttl=60)
def fetch_all(use_usgs, use_nws, use_bom, use_imd):
    sources = {}
    if use_usgs:
        try:
            sources["USGS"] = fetch_usgs_alerts()
        except Exception as e:
            sources["USGS_error"] = f"USGS fetch failed: {e}"
    if use_nws:
        try:
            sources["NWS"] = fetch_nws_alerts()
        except Exception as e:
            sources["NWS_error"] = f"NWS fetch failed: {e}"
    if use_bom:
        try:
            sources["BOM"] = fetch_bom_warnings()
        except Exception as e:
            sources["BOM_error"] = f"BOM fetch failed: {e}"
    if use_imd:
        try:
            sources["IMD"] = fetch_imd_alerts()
        except Exception as e:
            sources["IMD_error"] = f"IMD fetch failed: {e}"
    return sources

if refresh:
    st.info("Fetching data from selected sources...")
sources = fetch_all(use_usgs, use_nws, use_bom, use_imd)

# Parse / unify
df = unify_alerts_to_df(sources)

if df.empty:
    st.warning("No events available. Toggle data sources or upload sample data in the 'data/' folder. See README for BOM/IMD instructions.")
    st.stop()

# Filter DataFrame by date and severity
df["date"] = pd.to_datetime(df["date"], errors="coerce")
start_ts = pd.to_datetime(start_dt)
end_ts = pd.to_datetime(end_dt) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]

if min_severity != "any":
    df = df[df["severity"].str.lower().fillna("").str.contains(min_severity.lower())]

# Top row metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Files / Sources", len(sources))
col2.metric("Total events", len(df))
col3.metric("Unique areas", df["area"].nunique() if "area" in df.columns else 0)
critical_count = df[df["severity"].str.lower().str.contains("critical", na=False)].shape[0]
col4.metric("Critical / Severe", critical_count)

st.markdown("---")

# Layout for visuals and table
left, right = st.columns([2,1])

with left:
    st.subheader("Map")
    render_map(df)

    st.subheader("Timeline")
    render_timeline(df)

with right:
    st.subheader("Counts & Categories")
    render_counts(df)
    st.markdown("---")
    st.subheader("Events table")
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True), use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="alerts_export.csv", mime="text/csv")

st.markdown("### Source fetch diagnostics")
for k,v in sources.items():
    if isinstance(v, str) and v.endswith("failed"):
        st.error(f"{k}: {v}")
    else:
        st.write(f"- {k}: {len(v) if hasattr(v, '__len__') else 'OK'} items")

st.info("Notes: USGS and NWS are fetched live. BOM/IMD require site-specific endpoints/feeds — see README for setup & sample data.")

