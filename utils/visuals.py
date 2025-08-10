# utils/visuals.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_map(df: pd.DataFrame):
    if df.empty:
        st.info("No data for map.")
        return
    mdf = df.dropna(subset=["lat","lon"])
    if mdf.empty:
        # Try cluster by area: fallback to st.map using lat/lon if present
        st.info("No geo coordinates available for these events.")
        return
    fig = px.scatter_mapbox(
        mdf,
        lat="lat",
        lon="lon",
        hover_name="title",
        hover_data=["source","category","severity","date","area"],
        color="severity",
        zoom=1,
        height=450,
    )
    fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

def render_timeline(df: pd.DataFrame):
    if df.empty:
        st.info("No events to show in timeline.")
        return
    tdf = df.copy()
    tdf = tdf.dropna(subset=["date"])
    if tdf.empty:
        st.info("No timestamped events to show.")
        return
    # Count per hour/day
    tdf["date_h"] = tdf["date"].dt.floor("H")
    counts = tdf.groupby("date_h").size().reset_index(name="count")
    fig = px.bar(counts, x="date_h", y="count", labels={"date_h":"Time","count":"Events"}, height=300)
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

def render_counts(df: pd.DataFrame):
    if df.empty:
        st.info("No events.")
        return
    cat_counts = df["category"].fillna("unknown").value_counts().reset_index()
    cat_counts.columns = ["category","count"]
    fig = px.pie(cat_counts, names="category", values="count", title="Events by category", height=300)
    st.plotly_chart(fig, use_container_width=True)
    # severity counts
    sev_counts = df["severity"].fillna("unknown").value_counts().reset_index()
    sev_counts.columns = ["severity","count"]
    fig2 = px.bar(sev_counts, x="severity", y="count", title="By severity", height=250)
    st.plotly_chart(fig2, use_container_width=True)

