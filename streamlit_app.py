import streamlit as st
import pandas as pd

# 1. GROUND TRUTH OVERRIDE (Input Section)
st.sidebar.header("📍 Site Verification")
# Your site truth: override regional reports here
site_rain = st.sidebar.number_input("Measured Site Rain (in)", min_value=0.0, value=0.5, step=0.1)
site_humidity = st.sidebar.slider("Current Site Humidity (%)", 0, 100, 72)

# This simulates the "Forecast" that failed (showing 0.0" rain)
forecast_rain = 0.0 

# 2. SITE STATUS LOGIC: Ground Truth Trumps Forecast
# Threshold for construction hold: 0.25 inches
if site_rain >= 0.25:
    site_color = "#FF4B4B"  # Red for Alert
    site_status = "🔴 STORM ACTION: SITE SATURATED"
    safety_directive = "HOLD: Subgrade is soft. No heavy equipment or mass grading."
elif site_rain == 0.0 and forecast_rain > 0.1:
    site_color = "#28A745"  # Green for Clear
    site_status = "✅ STABLE: PROCEED WITH WORK"
    safety_directive = "Forecast rain missed. Site is dry. Resume standard grading."
else:
    site_color = "#31333F"  # Neutral
    site_status = "NOMINAL CONDITIONS"
    safety_directive = "Standard erosion control inspections and maintenance."

# 3. DASHBOARD UI
st.markdown(f"<h1 style='text-align: center; color: {site_color};'>{site_status}</h1>", unsafe_allow_html=True)

# Display the variance clearly so stakeholders see the forecast error
st.metric(
    label="Verified Site Rainfall", 
    value=f"{site_rain}\"", 
    delta=f"{site_rain - forecast_rain}\" Over Regional Forecast",
    delta_color="inverse" if site_rain > 0 else "normal"
)

st.warning(f"**Current Tactical Priority:** {safety_directive}")

# 4. EXECUTIVE ADVISORY (Forced by today's 0.5" rain)
st.subheader("Revised Site Advisory: Weekly Plan")
advisory_df = pd.DataFrame({
    "Day": ["Wed (Today)", "Thu", "Fri", "Sat"],
    "Condition": ["STORM ACTION", "SATURATED", "DRYING", "RECOVERY"],
    "Action Required": ["Runoff Management", "Limit Heavy Hauling", "Inspect Silt Fences", "Resume Grading"]
})
st.table(advisory_df)

st.caption("Site-Verified data always overrides regional NWS API reports for safety.")
