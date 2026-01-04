import streamlit as st
import json
import pandas as pd
import os
import datetime
from fpdf import FPDF

# --- INITIAL SETUP ---
st.set_page_config(page_title="Contractor Defense Portal", layout="wide")

# Custom CSS for the "Dimmed" look you requested
st.markdown("""
    <style>
    .main { background-color: #1e1e1e; color: #dcdcdc; }
    .stMetric { background-color: #2d2d2d; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
def get_data():
    if os.path.exists('data/site_status.json'):
        with open('data/site_status.json', 'r') as f:
            return json.load(f)
    return None

data = get_data()
if not data:
    st.error("Site Data Syncing...")
    st.stop()

# --- SOIL SATURATION (API) LOGIC ---
# Using the 5-day history to calculate the "CYA" Workability Index
try:
    df = pd.read_csv('data/history.csv')
    k = 0.85 
    api = 0
    for rain in df.tail(5)['precip_actual']:
        api = (api * k) + rain
except:
    api = 0

work_status = "RESTRICTED" if api > 0.75 else "OPTIMAL"
work_color = "red" if api > 0.75 else "green"

# --- DASHBOARD HEADER ---
st.title(f"🛡️ Contractor Defense Portal: {data['project_name']}")
st.write(f"**Verification Timestamp:** {data['last_updated']}")

# --- SECTION 1: EXECUTIVE CYA (THE "WHY WE AREN'T GRADING" SECTION) ---
st.header("🚜 Schedule & Workability Defense")
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Soil Saturation Index", f"{round(api, 2)}", delta=work_status, delta_color="inverse")

with col2:
    st.subheader(f"Status: :{work_color}[{work_status}]")
    st.info(f"**Legal Basis:** Soil moisture exceeds trafficability limits for the 148.2-acre disturbed area. Heavy equipment operation suspended to prevent unrecoverable soil damage.")

# --- SECTION 2: THE FIELD NOTE & PDF GENERATOR ---
st.header("📄 Daily Compliance Report")
field_notes = st.text_area("Superintendent Field Notes", placeholder="e.g., Verified Basin SB3 baffles, skimmer clear of debris.")

def create_pdf(notes, api_val, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="DAILY CONTRACTOR COMPLIANCE LOG", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Date: {datetime.date.today()} | Project: J&J LMDS", ln=True)
    pdf.cell(0, 10, f"Soil Saturation Index: {api_val} ({status})", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Field Observations: {notes}")
    return pdf.output(dest='S').encode('latin-1')

if st.button("Generate Official CYA PDF"):
    pdf_output = create_pdf(field_notes, round(api, 2), work_status)
    st.download_button(
        label="💾 Download Signed Report",
        data=pdf_output,
        file_name=f"JJ_Contractor_Log_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )

# --- SECTION 3: TECHNICAL DEPTH (SWPPP & BASIN) ---
st.header("🌧️ SWPPP & SB3 Intelligence")
t1, t2 = st.tabs(["Basin Status", "Perimeter Integrity"])

with t1:
    st.write(f"**SB3 Capacity:** {data['swppp']['sb3_capacity_pct']}%")
    st.write(f"**Skimmer Freeboard:** {data['swppp']['freeboard_feet']} ft")
    st.progress(data['swppp']['sb3_capacity_pct'] / 100)

with t2:
    st.write(f"**Perimeter Inspection:** {data['swppp']['silt_fence_integrity']}")
    st.write(f"**Current Wind Gusts:** {data['crane_safety']['max_gust']} mph")
