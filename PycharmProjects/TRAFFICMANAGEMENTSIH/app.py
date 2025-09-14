import streamlit as st
import pandas as pd, numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="Traffic Thing", layout="wide")
st.title("🚦 Traffic Dashboard")

# some places in bhopal
locs = {
    "LALGHATI": [23.2599, 77.4126], "KAROND": [23.2728, 77.4579],
    "BAIRAGARH": [23.2156, 77.3539], "INDRAPURI": [23.2156, 77.3825]
}

np.random.seed(42)
hour = datetime.now().hour
rush_mult=2.5 if hour in [8, 9, 17, 18, 19] else 1.0

data_list = []
for loc, coords in locs.items():
    base_val = np.random.randint(20, 40)
    num_cars = int(base_val*rush_mult * np.random.uniform(0.8, 1.2))
    spd = max(10, 55 - num_cars * 0.6 + np.random.uniform(-5, 5))
    data_list.append({"location": loc, "num_cars": num_cars, "speed": round(spd, 1), 
                   "lat": coords[0], "lon": coords[1]})

frame = pd.DataFrame(data_list)

thresh = st.sidebar.slider("Congestion Threshold", 20, 80, 50)
if st.sidebar.checkbox("Auto Refresh"):
    st.rerun()

c1, c2, c3 = st.columns(3)
c1.metric("Max Traffic", f"{frame['num_cars'].max()} cars")
c2.metric("Avg Speed", f"{frame['speed'].mean():.1f} km/h")
c3.metric("Congested", f"{len(frame[frame['num_cars'] >= thresh])}/{len(frame)}")

st.subheader("🗺️ Traffic Map")
m = folium.Map(location=[23.2599, 77.4126], zoom_start=12)

for i, row in frame.iterrows():
    color = 'red' if row['num_cars'] >= thresh*1.2 else 'orange' if row['num_cars'] >= thresh else 'green'
    folium.CircleMarker(
        [row['lat'], row['lon']],
        radius=max(8, row['num_cars']/3),
        popup=f"<b>{row['location']}</b><br>Cars: {row['num_cars']}<br>Speed: {row['speed']} km/h",
        color='black', weight=2, fillColor=color, 
        fillOpacity=0.8,
        tooltip=f"{row['location']}: {row['num_cars']} cars"
    ).add_to(m)

st_folium(m, height=400)

col1, col2 = st.columns(2)
col1.subheader("Traffic by Location")
col1.bar_chart(frame.set_index('location')['num_cars'])
    
col2.subheader("Current Data")
col2.dataframe(frame[['location', 'num_cars', 'speed']], hide_index=True)

st.subheader("🚨 Alerts")
crit_jams = frame[frame['num_cars'] >= thresh*1.2]
mod_jams = frame[(frame['num_cars'] >= thresh) & (frame['num_cars'] < thresh*1.2)]

if not crit_jams.empty:
    st.error("🔴 CRITICAL: " + ", ".join(crit_jams['location']))
if not mod_jams.empty:
    st.warning("🟡 MODERATE: " + ", ".join(mod_jams['location']))
if crit_jams.empty and mod_jams.empty:
    st.success("✅ All traffic flowing normally!")

st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
