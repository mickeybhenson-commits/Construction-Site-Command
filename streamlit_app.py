import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(page_title="J&J Site Oversight", layout="wide")

# --- FILE PATH PATHING ---
# This ensures Streamlit finds the data whether running locally or on the web
DATA_JSON = 'data/site_status.json'
DATA_CSV = 'data/history.csv'

def load_data():
    if os.path.exists(DATA_JSON):
        with open(DATA_JSON, 'r') as f:
            return json.load(f)
    return None

def load_history():
    if os.path.exists(DATA_CSV):
        return pd.read_csv(DATA_CSV)
    return None

site_data = load_data()
history_df = load_history()

# --- ERROR HANDLING ---
if not site_data:
    st.error("🏗️ **Site Data Initialization in Progress...**")
    st.info("The weather station is currently syncing. Please refresh this page in 1 minute.")
    st.stop()

# --- THE BEST IN USA DASHBOARD START ---
st.title(f"🏗️ {site_data['project_name']}")
st.write(f"**Last Updated:** {site_data['last_updated']}")

# Now you can safely use site_data['precipitation']
precip = site_data['precipitation']
st.metric("24h Actual Rain", f"{precip['actual_24h']} in", delta=precip['soil_status'])
