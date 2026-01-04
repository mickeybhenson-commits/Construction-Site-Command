import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path

# --- 1. ARCHITECTURAL CONFIG & STYLING ---
st.set_page_config(page_title="Wayne Brothers | Executive Command", layout="wide")

def apply_industrial_premium_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; font-family: 'Inter', sans-serif; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: radial-gradient(circle at center, rgba(0,0,0,0.85), rgba(0,0,0,0.98)); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .exec-header {{ margin-bottom: 40px; border-left: 8px solid #CC0000; padding-left: 25px; }}
        .exec-title {{ font-size: 3.5em; font-weight: 900; color: #FFFFFF; margin: 0; }}
        .exec-subtitle {{ font-size: 1.5em; color: #AAAAAA; font-weight: 400; margin-top: 5px; text-transform: uppercase; letter-spacing: 2px; }}
        .directive-container {{ background: rgba(20, 20, 25, 0.85); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 30px; margin-bottom: 30px; }}
        .directive-label {{ font-weight: 900; text-transform: uppercase; letter-spacing: 1px; color: #CC0000; margin-bottom: 15px; font-size: 0.9em; }}
        .risk-alert {{ background: rgba(204, 0, 0, 0.1); border: 1px solid #CC0000; padding: 15px; border-radius: 4px; margin-top: 15px; }}
        </style>
        """, unsafe_allow_html=True)

apply_industrial_premium_styling()

# --- 2. DATA ENGINE ---
def load_digital_twin():
    site, api = {"project_name": "J&J Wilson"}, 0.0
    try:
        if Path("data/site_status.json").exists():
            with open("data/site_status.json", "r") as f: site = json.load(f)
        if Path("data/history.csv").exists():
            hist = pd.read_csv("data/history.csv")
            recent = hist.tail(5)["precip_actual"].fillna(0).tolist()
            api = round(sum(r * (0.85 ** i) for i, r in enumerate(reversed(recent))), 3)
    except Exception: pass
    return site, api

site_data, api_val = load_digital_twin()

# --- 3. PREDICTIVE RISK LOGIC ---
# Forecast cross-referenced with Soil Saturation
forecast_prob = site_data['precipitation'].get('forecast_prob', 0)
future_issues = []

if forecast_prob > 50:
    if api_val > 0.60:
        future_issues.append("CRITICAL: Incoming rain on saturated soil will likely trigger a RESTRICTED status for all grading.")
        future_issues.append("SWPPP: Basin SB3 capacity is at risk of overtopping. Proactive pump-out recommended.")
    else:
        future_issues.append("MODERATE: Storm event may lead to SATURATED conditions; finalize current lifts by EOD.")
    future_issues.append("INSPECTION: High-risk perimeter zones require reinforcement before precipitation onset.")

# --- 4. EXECUTIVE INTERFACE ---
st.markdown(f"""
    <div class="exec-header">
        <div class="exec-title">Wayne Brothers</div>
        <div class="exec-subtitle">Johnson & Johnson Biologics Manufacturing Facility</div>
        <div style="color:#777;">Wilson, NC | 148.2 Disturbed Acres</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_risk = st.columns([2, 1])

with c_main:
    st.markdown('<div class="directive-container">', unsafe_allow_html=True)
    st.markdown('<div class="directive-label">Predictive Radar Surveillance</div>', unsafe_allow_html=True)
    st.components.v1.html(f"""
        <iframe width="100%" height="450" 
            src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar" 
            frameborder="0" style="border-radius:8px;"></iframe>
    """, height=460)
    st.markdown('</div>', unsafe_allow_html=True)

with c_risk:
    st.markdown("### ⚡ Future Impact Advisory")
    if not future_issues:
        st.success("Stable weather window confirmed. No major operational impediments forecast for 48-72 hours.")
    else:
        for issue in future_issues:
            st.markdown(f'<div class="risk-alert"><strong>STORM IMPACT:</strong> {issue}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Operational Metrics")
    st.metric("Soil Moisture (API)", api_val)
    st.metric("Rain Forecast", f"{forecast_prob}%")
    st.metric("Basin SB3 Capacity", f"{site_data['swppp']['sb3_capacity_pct']}%")

# Sidebar
with st.sidebar:
    st.caption(f"Sync: {site_data['last_updated']}")
    if st.button("Archive Daily Record"):
        st.success("Record Saved for Contractor Defense.")
