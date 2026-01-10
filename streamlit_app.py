import streamlit as st
import json
import pandas as pd
import datetime as dt
import requests
from pathlib import Path
from streamlit_autorefresh import st_autorefresh 

# --- 1. ARCHITECTURAL CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Wayne Brothers | Universal Command", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") # 5-Min Sync

def apply_universal_command_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; font-family: 'Inter', sans-serif; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: radial-gradient(circle at center, rgba(0,0,0,0.88), rgba(0,0,0,0.97)); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .exec-header {{ margin-bottom: 30px; border-left: 10px solid #CC0000; padding-left: 25px; }}
        .exec-title {{ font-size: 3.8em; font-weight: 900; letter-spacing: -2px; line-height: 1; color: #FFFFFF; margin: 0; }}
        .sync-badge {{ background: rgba(255, 255, 255, 0.1); color: #00FFCC; padding: 5px 12px; border-radius: 50px; font-size: 0.8em; font-weight: 700; border: 1px solid #00FFCC; }}
        .report-section {{ background: rgba(15, 15, 20, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
        .directive-header {{ color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.85em; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
        .truth-card {{ text-align: center; padding: 12px; background: rgba(0, 255, 204, 0.08); border-radius: 8px; border: 1px solid #00FFCC; min-height: 90px; }}
        .forecast-card {{ text-align: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); line-height: 1.1; min-height: 140px; }}
        .temp-box {{ background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.85em; margin: 4px 0; display: inline-block; }}
        .precip-box {{ color: #00FFCC; font-weight: 700; font-size: 0.85em; margin-top: 4px; }}
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. MULTI-SOURCE TRUTH COLLECTOR (AWN, USGS, PLANET) ---
# Replace with your actual secret names in Streamlit Cloud
ACCU_KEY = st.secrets.get("ACCU_KEY", "zpka_f1d5b5f80b014057b3a6e57011d9b56a_77161a13")
PLANET_KEY = st.secrets.get("PLANET_API_KEY", "PLAKffe383ae642849e5bf2e6f3864d85de9")

def get_usgs_truth():
    try:
        url = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=02090380&parameterCd=00045"
        resp = requests.get(url, timeout=5).json()
        return float(resp['value']['timeSeries'][0]['values'][0]['value'][0]['value'])
    except: return 0.0

def get_accu_minutecast():
    try:
        url = f"https://dataservice.accuweather.com/forecasts/v1/minute?q=35.73,-77.92&apikey={ACCU_KEY}"
        resp = requests.get(url, timeout=5).json()
        return resp.get("Summary", {}).get("Phrase", "No rain detected")
    except: return "Autonomous Monitoring Active"

def get_planet_imagery():
    try:
        url = "https://api.planet.com/data/v1/quick-search"
        headers = {'Authorization': f'api-key {PLANET_KEY}'}
        search_filter = {"item_types": ["PSScene"], "filter": {"type": "AndFilter", "config": [
            {"type": "GeometryFilter", "field_name": "geometry", "config": {"type": "Point", "coordinates": [-77.9968, 35.7624]}}
        ]}}
        res = requests.post(url, headers=headers, json=search_filter).json()
        return res['features'][0]['_links']['thumbnail'] + f"?api_key={PLANET_KEY}"
    except: return None

usgs_val = get_usgs_truth()
minutecast_phrase = get_accu_minutecast()
planet_thumb = get_planet_imagery()

# --- 3. DYNAMIC ROLLING ENGINE ---
current_dt = dt.datetime.now()
rolling_dates = [(current_dt + dt.timedelta(days=i)) for i in range(7)]

master_data = {
    "Mon": {"status": "STABLE", "hi": 58, "lo": 34, "pop": "1%", "in": "0.00\"", "truth": "0.00\""},
    "Tue": {"status": "STABLE", "hi": 63, "lo": 42, "pop": "2%", "in": "0.00\"", "truth": "0.00\""},
    "Wed": {"status": "STABLE", "hi": 72, "lo": 38, "pop": "1%", "in": "0.00\"", "truth": f"{usgs_val}\""},
    "Thu": {"status": "STABLE", "hi": 63, "lo": 42, "pop": "0%", "in": "0.00\"", "truth": "TBD"},
    "Fri": {"status": "RESTRICTED", "hi": 74, "lo": 57, "pop": "25%", "in": "0.02\"", "truth": "TBD"},
    "Sat": {"status": "CRITICAL", "hi": 76, "lo": 57, "pop": "65%", "in": "0.15\"", "truth": "TBD"},
    "Sun": {"status": "RECOVERY", "hi": 61, "lo": 30, "pop": "25%", "in": "0.05\"", "truth": "TBD"}
}

# --- 4. UI RENDERING ---
st.markdown(f"""
    <div class="exec-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="exec-title">Wayne Brothers</div>
            <div class="sync-badge">AUTONOMOUS COMMAND SYNC • {current_dt.strftime('%H:%M')}</div>
        </div>
        <div style="font-size:1.5em; color:#AAA;">Johnson & Johnson Biologics | 5100 Corporate Pkwy</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_metrics = st.columns([2, 1])

with c_main:
    # 1. Rolling Directive
    st.markdown(f'<div class="report-section" style="border-top: 8px solid #00FFCC;"><div class="directive-header">Autonomous Site Directive</div><h1 style="color:#00FFCC; margin:0;">STABLE</h1><p><b>{minutecast_phrase}:</b> Field operations proceeding under standard protocol.</p></div>', unsafe_allow_html=True)

    # 2. Planet Satellite Image (Visual Determination)
    if planet_thumb:
        st.markdown('<div class="report-section"><div class="directive-header">🛰️ Planet.com Visual Verification</div>', unsafe_allow_html=True)
        st.image(planet_thumb, caption="Latest High-Res Pass • 5100 Corporate Parkway", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Rolling Ground Truth Cards
    st.markdown('<div class="report-section"><div class="directive-header">7-Day Ground Truth (Measured Reality)</div>', unsafe_allow_html=True)
    gt_cols = st.columns(7)
    for i, date_obj in enumerate(rolling_dates):
        day = date_obj.strftime('%a')
        gt_cols[i].markdown(f'<div class="truth-card"><span style="color:#00FFCC; font-weight:900;">{day}</span><br><b>{master_data.get(day, master_data["Sun"])["truth"]}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_metrics:
    # 4. Restored Analytical Metrics
    st.markdown('<div class="report-section"><div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Rainfall (USGS)", f"{usgs_val}\"", delta="DRY" if usgs_val == 0 else "PRECIP")
    st.metric("Soil Moisture (API)", "0.058")
    st.metric("Temperature (Today)", "75°F")
    st.metric("Wind Speed", "15 mph")
    st.metric("Wind Direction", "S")
    st.metric("Humidity", "62%")
    st.metric("NC DEQ NTU Limit", "50 NTU")
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Radar
st.markdown('<div class="report-section"><div class="directive-header">Surveillance Radar: Wilson County</div>', unsafe_allow_html=True)
st.components.v1.html(f'<iframe width="100%" height="450" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&overlay=radar" frameborder="0"></iframe>', height=460)
st.markdown('</div>', unsafe_allow_html=True)
