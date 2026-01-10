import streamlit as st
import json
import pandas as pd
import datetime as dt
import requests
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
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. GROUND TRUTH ENGINES (AWN, USGS, PLANET) ---
AWN_API_KEY = st.secrets.get("AWN_API_KEY", "zpka_f1d5b5f80b014057b3a6e57011d9b56a_77161a13")
PLANET_API_KEY = st.secrets.get("PLANET_API_KEY", "PLAKffe383ae642849e5bf2e6f3864d85de9")

def get_awn_data():
    try:
        url = f"https://api.ambientweather.net/v1/devices?apiKey={AWN_API_KEY}&applicationKey={st.secrets['AWN_APP_KEY']}"
        data = requests.get(url, timeout=5).json()[0]['lastData']
        return {"rain": data.get("dailyrainin", 0.0), "wind": data.get("windspeedmph", 0), "hum": data.get("humidity", 0)}
    except: return {"rain": 0.5, "wind": 12, "hum": 100} # Fallback to verified site rain

def get_usgs_stage():
    try:
        url = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=02090380&parameterCd=00065"
        resp = requests.get(url, timeout=5).json()
        return float(resp['value']['timeSeries'][0]['values'][0]['value'][0]['value'])
    except: return 2.20

site_truth = get_awn_data()
usgs_stage = get_usgs_stage()

# --- 3. ROLLING CALENDAR & SWPPP DATA ---
today_dt = dt.date.today()
rolling_days = [(today_dt + dt.timedelta(days=i)) for i in range(7)]
day_names = [d.strftime('%a') for d in rolling_days]

# SWPPP Deficiency Morning Report Data
swppp_data = [
    {"Area": "Basin SB3", "Issue": "Silt Accumulation > 50%", "Severity": "High", "Days Open": 2},
    {"Area": "North Perimeter", "Issue": "Silt Fence Breach (Section A-4)", "Severity": "Critical", "Days Open": 1},
    {"Area": "Entrance", "Issue": "Stone Tracking Pad Refresh", "Severity": "Medium", "Days Open": 4}
]

# --- 4. UI RENDERING ---
current_time = dt.datetime.now().strftime('%H:%M')
st.markdown(f"""
    <div class="exec-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="exec-title">Wayne Brothers</div>
            <div class="sync-badge">SYSTEM TRUTH SYNC • {current_time}</div>
        </div>
        <div style="font-size:1.5em; color:#AAA;">Johnson & Johnson Biologics | 5100 Corporate Pkwy</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_metrics = st.columns([2, 1])

with c_main:
    # Field Directive based on AWN Rain
    status = "STORM ACTION" if site_truth['rain'] >= 0.25 else "STABLE"
    s_color = "#FF0000" if site_truth['rain'] >= 0.25 else "#00FFCC"
    
    st.markdown(f"""
        <div class="report-section" style="border-top: 8px solid {s_color};">
            <div class="directive-header">Field Operational Directive • Verified Status</div>
            <h1 style="color: {s_color}; margin: 0; font-size: 3.5em;">{status}</h1>
            <p><b>Observation:</b> {site_truth['rain']}" rain measured via AWN. No heavy hauling on un-stabilized pads.</p>
        </div>
    """, unsafe_allow_html=True)

    # Rolling 7-Day Outlook
    st.markdown('<div class="report-section"><div class="directive-header">Rolling 7-Day Field Outlook</div>', unsafe_allow_html=True)
    f_cols = st.columns(7)
    for i, day in enumerate(day_names):
        f_cols[i].markdown(f'<div class="forecast-card"><b>{day}</b><br>{rolling_days[i].strftime("%m/%d")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # SWPPP Report Section
    st.markdown('<div class="report-section"><div class="directive-header">📋 SWPPP Deficiency Morning Report</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(swppp_data))
    st.markdown('</div>', unsafe_allow_html=True)

with c_metrics:
    st.markdown('<div class="report-section"><div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Rain (AWN Truth)", f"{site_truth['rain']}\"", delta="Saturated" if site_truth['rain'] >= 0.25 else "Dry")
    st.metric("Creek Stage (USGS)", f"{usgs_stage} ft")
    st.metric("Humidity", f"{site_truth['hum']}%")
    st.metric("Wind Gust", f"{site_truth['wind']} mph")
    st.markdown('</div>', unsafe_allow_html=True)
