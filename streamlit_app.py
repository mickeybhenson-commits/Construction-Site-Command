import pandas as pd
import streamlit as st

# 1. Calculate the Soil Saturation (API Index)
try:
    df = pd.read_csv('data/history.csv')
    k = 0.85  # Soil drying constant for NC Clay
    api = 0
    # Math: Today's wetness = (Yesterday's wetness * drying factor) + New Rain
    for rain in df.tail(5)['actual_rain']:
        api = (api * k) + rain
    
    # 2. Assign a Workability Status
    if api < 0.25:
        work_status, work_color, advice = "OPTIMAL", "green", "All equipment cleared for site-wide use."
    elif api < 0.80:
        work_status, work_color, advice = "CAUTION", "orange", "Heavy hauling restricted to stabilized pads."
    else:
        work_status, work_color, advice = "RESTRICTED", "red", "Stand down heavy equipment to prevent rutting."
except:
    api, work_status, work_color, advice = 0, "INITIALIZING", "gray", "Awaiting data history..."

# 3. Display the "Command Center" Header
st.markdown("---")
st.header("🏗️ Construction Site Workability")
c1, c2 = st.columns([1, 2])

with c1:
    st.metric("Soil Saturation Index", f"{round(api, 2)}", help="Calculated using 5-day Antecedent Precipitation Index")

with c2:
    st.markdown(f"### Status: :{work_color}[{work_status}]")
    st.info(f"**Field Guidance:** {advice}")
