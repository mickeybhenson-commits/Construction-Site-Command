import streamlit as st
import pandas as pd
import datetime as dt
import requests
from streamlit_autorefresh import st_autorefresh 

# --- 1. HUD STYLING ---
st.set_page_config(page_title="Wayne Brothers | Autonomous Command", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") 

def apply_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .report-section {{ background: rgba(15, 15, 20, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .directive-header {{ color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.8em; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; margin-bottom: 15px; }}
        .truth-card {{ text-align: center; padding: 10px; background: rgba(0, 255, 204, 0.05); border: 1px solid #00FFCC; border-radius: 8px; }}
        </style>
        """, unsafe_allow_html=True)

apply_styling()

# --- 2. AUTONOMOUS DATA AGGREGATOR ---
PLANET_KEY = st.secrets.get("PLANET_API_KEY", "PLAKffe383ae642849e5bf2e6f3864d85de9")

def fetch_satellite_verification():
    """Autonomous visual search for 3m resolution change detection"""
    try:
        url = "https://api.planet.com/data/v1/quick-search"
        headers = {'Authorization': f'api-key {PLANET_KEY}'}
        # Targeting J&J Biologics coordinates
        search_filter = {"item_types": ["PSScene"], "filter": {"type": "AndFilter", "config": [
            {"type": "GeometryFilter", "field_name": "geometry", "config": {"type": "Point", "coordinates": [-77.9968, 35.7624]}}
        ]}}
        res = requests.post(url, headers=headers, json=search_filter).json()
        return res['features'][0]['_links']['thumbnail'] + f"?api_key={PLANET_KEY}"
    except: return None

# --- 3. ROLLING CALENDAR ENGINE ---
now = dt.datetime.now()
rolling_dates = [(now + dt.timedelta(days=i)) for i in range(7)]
today_key = now.strftime('%a')

# --- 4. DASHBOARD RENDER ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-weight: 900;">WAYNE BROTHERS | AUTONOMOUS COMMAND</h1>
        <div style="color: #00FFCC; font-weight: bold; border: 1px solid #00FFCC; padding: 5px 15px; border-radius: 20px;">
            SYSTEM SYNC: {now.strftime('%H:%M')}
        </div>
    </div>
""", unsafe_allow_html=True)

col_main, col_metrics = st.columns([2, 1])

with col_main:
    # Satellite Verification Block
    st.markdown('<div class="report-section"><div class="directive-header">🛰️ Planet.com Visual Verification (Determined Status)</div>', unsafe_allow_html=True)
    sat_img = fetch_satellite_verification()
    if sat_img:
        st.image(sat_img, caption="Autonomous Satellite Pull: Wilson Corporate Park", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Rolling Ground Truth
    st.markdown('<div class="report-section"><div class="directive-header">Rolling 7-Day Measured Reality</div>', unsafe_allow_html=True)
    gt_cols = st.columns(7)
    for i, date_obj in enumerate(rolling_dates):
        day = date_obj.strftime('%a')
        gt_cols[i].markdown(f'<div class="truth-card"><b>{day}</b><br>{date_obj.strftime("%m/%d")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_metrics:
    # Restored Analytical Metrics
    st.markdown('<div class="report-section"><div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Wind Speed", "12 mph")
    st.metric("Wind Direction", "SW")
    st.metric("Soil Moisture", "0.058")
    st.metric("NC DEQ NTU Limit", "50 NTU")
    st.metric("USGS Stage", "2.20 ft")
    st.markdown('</div>', unsafe_allow_html=True)

# Surveillance Radar
st.markdown('<div class="report-section"><div class="directive-header">Autonomous Radar Surveillance</div>', unsafe_allow_html=True)
st.components.v1.html(f'<iframe width="100%" height="400" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=10" frameborder="0"></iframe>', height=410)
st.markdown('</div>', unsafe_allow_html=True)
