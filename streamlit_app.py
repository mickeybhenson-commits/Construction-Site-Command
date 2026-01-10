import streamlit as st
import pandas as pd
import datetime as dt
import requests
from streamlit_autorefresh import st_autorefresh 

# --- 1. CONFIG & SYSTEM TRUTH ---
st.set_page_config(page_title="Wayne Brothers | Universal Command", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") # 5-Min Sync

# --- 2. DYNAMIC ROLLING CALENDAR LOGIC ---
today_dt = dt.date.today()
# Generate the next 7 days starting from Today
rolling_days = [(today_dt + dt.timedelta(days=i)) for i in range(7)]
day_names = [d.strftime('%a') for d in rolling_days]

# Mock data for the new upcoming days (In production, this pulls from your Forecast API)
forecast_data = {
    "Mon": {"status": "STABLE", "color": "#00FFCC", "hi": 58, "lo": 34, "pop": "1%", "in": "0.00\""},
    "Tue": {"status": "STABLE", "color": "#00FFCC", "hi": 63, "lo": 42, "pop": "2%", "in": "0.00\""},
    "Wed": {"status": "STORM ACTION", "color": "#FF0000", "hi": 72, "lo": 38, "pop": "100%", "in": "0.50\""},
    "Thu": {"status": "SATURATED", "color": "#FF8C00", "hi": 63, "lo": 42, "pop": "0%", "in": "0.00\""},
    "Fri": {"status": "DRYING", "color": "#FFFF00", "hi": 74, "lo": 57, "pop": "25%", "in": "0.02\""},
    "Sat": {"status": "RECOVERY", "color": "#00FFCC", "hi": 76, "lo": 57, "pop": "49%", "in": "0.15\""},
    "Sun": {"status": "STABLE", "color": "#00FFCC", "hi": 61, "lo": 30, "pop": "25%", "in": "0.05\""}
}

# --- 3. SWPPP DEFICIENCY DATA (Detailed Morning Report Style) ---
swppp_deficiencies = [
    {"Area": "Basin SB3", "Issue": "Silt Accumulation > 50%", "Severity": "High", "Status": "Open", "Days": 2},
    {"Area": "North Perimeter", "Issue": "Silt Fence Breach (Section A-4)", "Severity": "Critical", "Status": "Immediate", "Days": 1},
    {"Area": "Construction Entrance", "Issue": "Stone Refresh Needed", "Severity": "Medium", "Status": "Pending", "Days": 4},
    {"Area": "Stockpile 2", "Issue": "Temporary Seeding Failed", "Severity": "Low", "Status": "Monitor", "Days": 7}
]
df_swppp = pd.DataFrame(swppp_deficiencies)

# --- 4. UI RENDERING ---
st.markdown('<div class="exec-title">Wayne Brothers Universal Command</div>', unsafe_allow_html=True)

# ROLLING 7-DAY OUTLOOK SECTION
st.markdown('<div class="report-section"><div class="directive-header">Rolling 7-Day Field Outlook</div>', unsafe_allow_html=True)
cols = st.columns(7)
for i, day in enumerate(day_names):
    d = forecast_data.get(day, forecast_data["Sun"])
    cols[i].markdown(f"""
        <div class="forecast-card" style="border-top: 4px solid {d['color']}; background: rgba(255,255,255,0.05); padding:10px; border-radius:8px;">
            <b style="color:#00FFCC;">{day}</b><br>
            <span style="font-size:0.8em;">{rolling_days[i].strftime('%m/%d')}</span><br>
            <div style="margin:5px 0;">{d['hi']}° / {d['lo']}°</div>
            <div style="color:{d['color']}; font-weight:bold; font-size:0.8em;">{d['status']}</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# DETAILED SWPPP REPORT SECTION
st.header("📋 SWPPP Inspection & Deficiency Report")
col_table, col_summary = st.columns([2, 1])

with col_table:
    st.markdown("### Active Corrective Actions")
    # Styling the dataframe for the dashboard
    st.dataframe(df_swppp.style.set_properties(**{'background-color': '#0f0f14', 'color': 'white', 'border-color': '#333'}))

with col_summary:
    st.markdown("### SWPPP Health Summary")
    st.metric("Total Open Items", len(df_swppp), delta="2 New Since Monday", delta_color="inverse")
    st.metric("Avg. Resolution Time", "3.2 Days", delta="-0.5 Days", delta_color="normal")
    st.info("**Alert:** Perimeter Fence Section A-4 must be repaired before Wed Storm Event.")

# (Rest of your AWN and USGS logic remains below)
