# J-J-LMDS-WILSON-NC
**Project:** Johnson & Johnson Biologics Manufacturing Campus  
**Location:** Wilson Corporate Park, Wilson, NC  

## Overview
This repository automates the daily environmental and construction status monitoring for the J&J Wilson site. The project tracks a 176-acre site with approximately 148.2 acres of active land disturbance.

## Areas of Interest
1. **Precipitation:** HRRR-based forecasts cross-referenced with real-time USGS rain data.
2. **SWPPP:** Detailed monitoring of Sediment Basins (SB-1, SB-2, SB-3), drainage channels, and silt fence integrity.
3. **Wind:** Monitoring gusts and sustained speeds for safe tower crane operations.
4. **Lightning:** Forecast and actual strike detection within a 50-mile radius.

## System Components
- **Dashboard:** Streamlit app for data visualization.
- **Automation:** GitHub Actions (`update_data.yml`) runs the `updater.py` script daily at 07:00 AM.
- **Data Storage:** Current site metrics stored in `data/site_status.json`.
