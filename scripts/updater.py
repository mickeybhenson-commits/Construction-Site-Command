import json
from datetime import datetime

# CONFIGURATION: Site-specific sensors and file paths
# The '../' tells the script to look for the data folder outside of the scripts folder
SITES = [
    {
        "name": "Wilson - J&J LMDS",
        "file": "../data/wilson_site.json",
        "usgs_id": "02091500",
        "icao": "KRWI",
        "location": "Wilson, NC"
    },
    {
        "name": "Charlotte - South Blvd",
        "file": "../data/charlotte_site.json",
        "usgs_id": "02146409",
        "icao": "KCLT",
        "location": "Charlotte, NC"
    }
]

def get_rain(usgs_id):
    # Simulated rain values based on current site triggers
    return 0.74 if usgs_id == "02146409" else 0.05

for site in SITES:
    print(f"Updating data for {site['name']}...")
    rain_val = get_rain(site['usgs_id'])
    
    new_data = {
        "project_name": site['name'],
        "location": site['location'],
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M EST"),
        "swppp": {
            "risk": "HIGH" if rain_val >= 0.5 else "LOW",
            "rain_24h": rain_val,
            "notes": "Triggered inspection required." if rain_val >= 0.5 else "Site stable."
        },
        "concrete": { "temp_low": 42, "blankets_required": False, "notes": "Curing monitor active." },
        "crane": { "wind_speed": 12, "status": "GO" }
    }
    
    # Save the data
    try:
        with open(site['file'], 'w') as f:
            json.dump(new_data, f, indent=2)
    except FileNotFoundError:
        # If running from the root instead of the scripts folder, try without the '../'
        with open(site['file'].replace('../', ''), 'w') as f:
            json.dump(new_data, f, indent=2)

print("All site updates complete.")
