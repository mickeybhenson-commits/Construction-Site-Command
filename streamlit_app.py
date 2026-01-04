import streamlit as st
import json
import pandas as pd
import os
import datetime
from fpdf import FPDF

# --- 1. PAGE CONFIG & BACKGROUND ---
st.set_page_config(page_title="J&J Contractor Defense Portal", layout="wide")

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png");
             background-attachment: fixed;
             background-size: cover;
         }}
         /* Dim the background for readability */
         .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.6);
            z-index: -1;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

# --- 2. DATA LOADING & API CALCULATION ---
# We define 'api' here so the NameError disappears
def load_all_data():
    site_json, history_df, api_val = None, None, 0.0
    
    if os.path.exists('data/site_status.json'):
        with open('data/site_status.json', 'r') as f:
            site_json = json.load(f)
            
    if os.path.exists('data/history.csv'):
        history_df = pd.read_csv('data/history.csv')
        # Calculate 5-Day Soil Saturation (API)
        k = 0.85
        temp_api = 0
        for rain in history_df.tail(5)['precip_actual']:
            temp_api = (temp_api * k) + float(rain)
        api_val = temp_api
        
    return site_json, history_df, api_val

site_data, history, api = load_all_data()

if not site_data:
    st.error("Waiting for initial data update...")
    st.stop()

# --- 3. THE 4-TIER CYA LOGIC ---
if api < 0.30:
    work_status, work_color = "OPTIMAL", "green"
    legal_basis = "Site conditions are optimal. Ground stability sufficient for full production."
elif api < 0.60:
    work_status, work_color = "SATURATED", "yellow"
    legal_basis = "Soil moisture elevated. Limit heavy hauling to stabilized roads to prevent subgrade damage."
elif api < 0.85:
    work_status, work_color = "CRITICAL", "orange"
    legal_basis = "High rutting risk. Grading restricted to protect 148.2-acre soil integrity."
else:
    work_status, work_color = "RESTRICTED", "red"
    legal_basis = "OFFICIAL NOTICE: Soil saturation exceeds trafficability limits. Operations suspended."

# --- 4. THE CONTRACTOR COMMAND CENTER ---
st.title(f"🛡️ {site_data['project_name']}")
st.write(f"**Verification Timestamp:** {site_data['last_updated']}")

# High-Visibility Risk Cards
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Soil Saturation Index", f"{round(api, 2)}", delta=work_status, delta_color="inverse")
with c2:
    st.metric("SB3 Capacity", f"{site_data['swppp']['sb3_capacity_pct']}%")
with c3:
    st.metric("Wind Max", f"{site_data['crane_safety']['max_gust']} mph", delta=site_data['crane_safety']['status'])

# The Official Recommendation Box
st.markdown(f"### Status: :{work_color}[{work_status}]")
if work_status == "OPTIMAL": st.success(legal_basis)
elif work_status == "SATURATED": st.warning(legal_basis)
else: st.error(legal_basis)

# --- 5. PDF GENERATOR ---
st.markdown("---")
field_notes = st.text_area("Superintendent Daily Field Notes", placeholder="Log inspections or Engineer directives here...")

def create_pdf(notes, api_val, status, basis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="DAILY CONTRACTOR COMPLIANCE LOG", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Date: {datetime.date.today()} | Saturation Index: {api_val}", ln=True)
    pdf.cell(0, 10, f"Site Status: {status}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Legal Basis: {basis}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Field Observations: {notes}")
    return pdf.output(dest='S').encode('latin-1')

if st.button("Generate Official CYA Report"):
    pdf_bytes = create_pdf(field_notes, round(api, 2), work_status, legal_basis)
    st.download_button("💾 Download Signed PDF", pdf_bytes, f"JJ_Report_{datetime.date.today()}.pdf", "application/pdf")
