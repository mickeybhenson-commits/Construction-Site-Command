import streamlit as st
import pandas as pd
import json

# App Configuration
st.set_page_config(page_title="J&J LMDS - Project Command", layout="wide")
st.title("🚧 J&J LMDS Project Dashboard")
st.markdown("Wilson, NC | Neuse River Watershed")

# Load Latest Data
with open('data/site_status.json') as f:
    data = json.load(f)

# Sidebar - Project Snapshot
st.sidebar.header("Site Quick-Look")
st.sidebar.metric("Rainfall (24h)", f"{data['swppp']['rain_24h']}\"")
st.sidebar.metric("Wind Speed", f"{data['crane']['wind_speed']} mph")
st.sidebar.markdown(f"**Last Sync:** {data['last_updated']}")

# Tab Navigation
tab1, tab2, tab3, tab4 = st.tabs(["🌧️ SWPPP", "🧱 Concrete", "🚜 Grading", "🏗️ Crane/Wind"])

with tab1:
    st.header("Stormwater & Satellite Compliance")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Soil Stability Index")
        moisture = data['swppp']['stability_index']
        st.progress(int(moisture * 100))
        st.write(f"Saturation: {moisture*100}%")
    with col2:
        st.subheader("USGS Monitoring")
        st.write("Source: Station 02091500 (Contentnea Creek)")
        st.metric("Risk Level", data['swppp']['risk'])

with tab4:
    st.header("Crane Safety & Wind Forecast")
    st.write(f"Current Gusts: {data['crane']['max_gust']} mph")
    if data['crane']['wind_speed'] > 20:
        st.error("⚠️ CAUTION: Winds exceeding safety thresholds.")
    else:
        st.success("✅ Winds within safe operating limits.")
