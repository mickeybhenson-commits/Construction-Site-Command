import streamlit as st
import json
import pandas as pd
import os
import datetime
from fpdf import FPDF

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Contractor Defense Portal", layout="wide", page_icon="🛡️")

def add_industrial_design():
    # Utilizing the uploaded diamond-plate background
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{bg_url}");
             background-attachment: fixed;
             background-size: cover;
         }}
         .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.75);
            z-index: -1;
         }}
         .stMetric {{
            background-color: rgba(40, 40, 40, 0.8);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #555;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_industrial_design()

# --- 2. DATA LOADING & ANALYSIS ---
def load_digital_twin():
    site_json, history_df, api_val = None, None, 0.0
    
    # Load Current Snapshot
    if os.path.exists('data/site_status.json'):
        with open('data/site_status.json', 'r') as f:
            site_json = json.load(f)
            
    # Load Historical Ledger
    if os.path.exists('data/history.csv'):
        history_df = pd.read_csv('data/history.csv')
        # Calculate 5-Day Soil Saturation Index (API)
        k = 0.85
        temp_api = 0
        for rain in history_df.tail(5)['precip_actual']:
            temp_api = (temp_api * k) + float(rain)
        api_val = temp_api
        
    return site_json, history_df, api_val

site_data, history, api = load_digital_twin()

if not site_data:
    st.error("🏗️ System Syncing... Please verify 'data/site_status.json' is present.")
    st.stop()

# --- 3. CONTRACTOR DEFENSE LOGIC ---
# Standardizing the four-tier status for the 148.2 disturbed acres
if api < 0.30:
    work_status, work_color = "OPTIMAL", "green"
    defense_statement = "Site conditions are optimal. Ground stability sufficient for scheduled production."
elif api < 0.60:
    work_status, work_color = "SATURATED", "yellow"
    defense_statement = "Soil moisture elevated. Hauling restricted to stabilized roads to prevent subgrade damage."
elif api < 0.85:
    work_status, work_color = "CRITICAL", "orange"
    defense_statement = "High rutting risk detected. Mass grading restricted to protect soil structure integrity."
else:
    work_status, work_color = "RESTRICTED", "red"
    defense_statement = "OFFICIAL NOTICE: Soil saturation exceeds trafficability limits. Operations suspended."

# --- 4. DASHBOARD HEADER ---
st.title(f"🛡️ {site_data['project_name']} - Contractor Defense")
st.write(f"**Verification Timestamp:** {site_data['last_updated']}")

# High-Level Metric Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Soil Saturation (API)", f"{round(api, 2)}", delta=work_status, delta_color="inverse")
with c2:
    st.metric("Rain (24h Actual)", f"{site_data['precipitation']['actual_24h']} in")
with c3:
    st.metric("SB3 Basin Capacity", f"{site_data['swppp']['sb3_capacity_pct']}%")
with c4:
    st.metric("Max Wind Gust", f"{site_data['crane_safety']['max_gust']} mph", delta=site_data['crane_safety']['status'])

# Official Status Box
st.markdown(f"### Site Status: :{work_color}[{work_status}]")
if work_status == "OPTIMAL": st.success(defense_statement)
elif work_status == "SATURATED": st.warning(defense_statement)
else: st.error(f"🚨 {defense_statement}")

# --- 5. INTERACTIVE TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Defense Reporting", "🚜 SWPPP & Grading", "🏗️ Safety & Concrete", "🔗 Data Archive"])

with tab1:
    st.subheader("Contractor Defense Report Generator")
    st.info("Generate a timestamped record of site conditions to document production delays or maintenance.")
    
    field_notes = st.text_area("Field Observations", placeholder="Enter specific field directives or site observations here.")

    def create_pdf(notes, api_val, status, basis):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="DAILY CONTRACTOR DEFENSE LOG", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(0, 10, f"Project: J&J LMDS Wilson, NC | Date: {datetime.date.today()}", ln=True)
        pdf.cell(0, 10, f"Soil Saturation Index: {api_val} ({status})", ln=True)
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.multi_cell(0, 10, f"Workability Statement: {basis}", border=1, fill=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Field Notes: {notes}")
        pdf.ln(20)
        pdf.cell(0, 10, "Signed: __________________________", ln=True)
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 Generate Defense Report"):
        pdf_bytes = create_pdf(field_notes, round(api, 2), work_status, defense_statement)
        st.download_button("💾 Download PDF", pdf_bytes, f"JJ_Defense_Log_{datetime.date.today()}.pdf", "application/pdf")

with tab2:
    st.subheader("SWPPP & Grading Status")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Disturbed Acres:** {site_data['swppp']['disturbed_acres']}")
        st.write(f"**Silt Fence Status:** {site_data['swppp']['silt_fence_integrity']}")
    with col_b:
        st.write(f"**SB3 Freeboard:** {site_data['swppp']['freeboard_feet']} ft")
        st.progress(site_data['swppp']['sb3_capacity_pct'] / 100)

with tab3:
    st.subheader("Safety & Pour Conditions")
    if site_data['crane_safety']['max_gust'] > 25:
        st.error(f"WIND ALERT: Gusts at {site_data['crane_safety']['max_gust']} mph.")
    else:
        st.success("WIND CONDITIONS: Within safe limits.")
    st.write(f"**Lightning Forecast:** {site_data['lightning']['forecast']}")

with tab4:
    st.subheader("Database Record Verification")
    col_j, col_h = st.columns(2)
    with col_j:
        st.caption("Live Status (site_status.json)")
        st.json(site_data)
    with col_h:
        st.caption("Audit Trail (history.csv)")
        if history is not None:
            st.dataframe(history.tail(10))
