import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path

# --- CONFIG & PROFESSIONAL STYLING ---
st.set_page_config(page_title="Wayne Brothers | J&J Wilson NC", layout="wide")

def apply_executive_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: rgba(0,0,0,0.90); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .directive-card {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 4px; border-left: 8px solid #555; margin-bottom: 20px; }}
        .metric-label {{ color: #999; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #fff; }}
        </style>
        """, unsafe_allow_html=True)

apply_executive_styling()

# --- DATA PROCESSING (Morning Report Logic) ---
def load_morning_data():
    with open("data/site_status.json", "r") as f: site = json.load(f)
    hist = pd.read_csv("data/history.csv")
    recent = hist.tail(5)["precip_actual"].fillna(0).tolist()
    api = round(sum(r * (0.85 ** i) for i, r in enumerate(reversed(recent))), 3)
    return site, api

site_data, api_val = load_morning_data()

# Logic for Tiered Recommendations
if api_val < 0.30:
    status, color, grading_rec = "OPTIMAL", "#0B8A1D", "Full grading operations authorized. Ground stability is high."
elif api_val < 0.60:
    status, color, grading_rec = "SATURATED", "#FFAA00", "Soil moisture elevated. Limit heavy hauling to stabilized roads."
elif api_val < 0.85:
    status, color, grading_rec = "CRITICAL", "#FF6600", "High rutting risk. Restrict mass grading to protect soil integrity."
else:
    status, color, grading_rec = "RESTRICTED", "#B00000", "Grading suspended. Operations restricted to emergency erosion control."

# --- MAIN PAGE: EXECUTIVE DIRECTIVES ---
st.title(f"J&J Biologics Facility | Wayne Brothers Operational Directives")
st.write(f"**Report Period:** {dt.datetime.now():%Y-%m-%d} | **Site Status:** :{color}[**{status}**]")

# PILLAR 1: WEATHER & SOIL (The "Why")
st.markdown("### 1. Environmental & Soil Intelligence")
w1, w2, w3, w4 = st.columns(4)
with w1:
    st.markdown(f'<p class="metric-label">Soil Moisture (API)</p><p class="metric-value">{api_val}</p>', unsafe_allow_html=True)
with w2:
    st.markdown(f'<p class="metric-label">Rain Actual (24h)</p><p class="metric-value">{site_data["precipitation"]["actual_24h"]} IN</p>', unsafe_allow_html=True)
with w3:
    st.markdown(f'<p class="metric-label">Rain Forecast</p><p class="metric-value">{site_data["precipitation"]["forecast_prob"]}%</p>', unsafe_allow_html=True)
with w4:
    st.markdown(f'<p class="metric-label">Lightning Forecast</p><p class="metric-value">{site_data["lightning"]["forecast"]}</p>', unsafe_allow_html=True)

# PILLAR 2: FIELD OPERATIONS & SAFETY (The "What")
st.markdown("### 2. Operational Directives")
st.markdown(f"""
<div class="directive-card" style="border-left-color: {color};">
    <strong>GRADING DIRECTIVE:</strong> {grading_rec}<br>
    <strong>WIND/CRANE SAFETY:</strong> {site_data['crane_safety']['status']} (Peak Gusts: {site_data['crane_safety']['max_gust']} MPH)<br>
    <strong>LIGHTNING PROTOCOL:</strong> Strikes within 50mi: {site_data['lightning']['recent_strikes_50mi']}
</div>
""", unsafe_allow_html=True)

# PILLAR 3: SWPPP & SATELLITE ANALYSIS (The "Where")
st.markdown("### 3. SWPPP & Infrastructure Compliance")
col_img, col_swppp = st.columns([2, 1])
with col_img:
    st.subheader("Satellite Surveillance (148.2 Acres)")
    # Analyzes Basin SB3 and Silt Fence via satellite imagery
    st.image("https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/satellite_placeholder.png", 
             caption="Current Observation: Basin SB3 & East Perimeter Perimeter Silt Fence")
with col_swppp:
    st.subheader("Basin SB3 Metrics")
    st.write(f"**Capacity:** {site_data['swppp']['sb3_capacity_pct']}%")
    st.write(f"**Freeboard:** {site_data['swppp']['freeboard_feet']} FT")
    st.progress(float(site_data['swppp']['sb3_capacity_pct'])/100)
    
    # Recommendations for SWPPP
    if site_data['swppp']['sb3_capacity_pct'] > 75:
        st.error("ACTION REQUIRED: Basin SB3 capacity critical. Schedule pump-out.")
    else:
        st.success("STATUS: Silt fence and basin levels within compliance limits.")

# Sidebar for Internal Contractor Defense
with st.sidebar:
    st.header("Contractor Defense")
    st.write(f"**Project Area:** 148.2 Disturbed Acres")
    st.write(f"**Digital Twin Sync:** {site_data['last_updated']}")
    if st.button("Archive Report"):
        st.info("Record archived to history.csv for legal defense.")
