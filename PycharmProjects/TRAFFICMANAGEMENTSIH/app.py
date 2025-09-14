import streamlit as st
import pandas as pd, numpy as np
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime

# page setup
st.set_page_config(layout="wide", page_title="Traffic Dashboard")
st.title("🚦 Smart Traffic Dashboard")

np.random.seed(42)

# locations in bhopal
bhopal_locs = {
    "LALGHATI": {"lat": 23.2599, "lon": 77.4126, "type": "major"},
    "KAROND": {"lat": 23.2728, "lon": 77.4579, "type": "residential"},
    "BAIRAGARH": {"lat": 23.2156, "lon": 77.3539, "type": "industrial"},
    "INDRAPURI": {"lat": 23.2156, "lon": 77.3825, "type": "commercial"},
    "NEW MARKET": {"lat": 23.2590, "lon": 77.4030, "type": "commercial"},
    "MP NAGAR": {"lat": 23.2420, "lon": 77.4270, "type": "commercial"}
}

def get_traffic_color(v_count, thresh):
    if v_count >= thresh * 1.2:
        return 'red'
    elif v_count >= thresh:
        return 'orange'
    elif v_count >= thresh * 0.7:
        return 'yellow'
    else:
        return 'green'

def get_traffic_status(v_count, thresh):
    if v_count >= thresh * 1.2:
        return "Heavy Traffic"
    elif v_count >= thresh:
        return "Moderate Traffic"
    elif v_count >= thresh * 0.7:
        return "Light Traffic"
    else:
        return "Free Flow"

# make some fake data
now = datetime.now()
locations = list(bhopal_locs.keys())
data_list = []

for loc in locations:
    hour=now.hour
    base_val = np.random.randint(15, 45)

    if hour in [7, 8, 9]:
        multiplier = np.random.uniform(1.8, 2.5)
    elif hour in [17, 18, 19, 20]:
        multiplier = np.random.uniform(2.0, 3.0)
    elif hour in [12, 13]:
        multiplier = np.random.uniform(1.3, 1.7)
    else:
        multiplier = np.random.uniform(0.8, 1.2)

    v_count = int(base_val * multiplier)
    avg_spd = max(5, 60 - (v_count * 0.8) + np.random.uniform(-5, 5))
    
    data_list.append({
        "location": loc, "vehicle_count": v_count,
        "avg_speed": round(avg_spd, 1),
        "lat": bhopal_locs[loc]["lat"], "lon": bhopal_locs[loc]["lon"],
        "type": bhopal_locs[loc]["type"], "timestamp": now,
        "wait_time": max(0, round((70 - avg_spd) * 0.5, 1))
    })

data = pd.DataFrame(data_list)

# sidebar
st.sidebar.header("Controls")
thresh = st.sidebar.slider("Congestion Threshold", 10, 100, 40)
show_speed = st.sidebar.checkbox("Show Speed Data", True)
show_wait_time = st.sidebar.checkbox("Show Wait Time", True)
auto_refresh = st.sidebar.checkbox("Auto Refresh (2s)")

if auto_refresh:
    time.sleep(2)
    st.rerun()

st.subheader("Live Traffic Metrics")
col1, col2, col3, col4 = st.columns(4)

max_v = data["vehicle_count"].max()
max_id = data["vehicle_count"].idxmax()
max_loc = data.loc[max_id, "location"]
col1.metric("Highest Traffic", f"{max_v} vehicles", f"at {max_loc}")

avg_s = data["avg_speed"].mean()
col2.metric("Average Speed", f"{avg_s:.1f} km/h")

congested= len(data[data["vehicle_count"] >= thresh])
col3.metric("Congested Jams", f"{congested}/{len(data)}")

avg_w = data["wait_time"].mean()
col4.metric("Avg Wait Time", f"{avg_w:.1f} min")

st.subheader("Traffic Map")
map_center = [23.2599, 77.4126]
m = folium.Map(location=map_center, zoom_start=12, tiles='OpenStreetMap')

for i, row in data.iterrows():
    col = get_traffic_color(row['vehicle_count'], thresh)
    stat = get_traffic_status(row['vehicle_count'], thresh)
    
    popup_html = f"""
    <h4>{row['location']}</h4>
    <b>Status:</b> {stat}<br>
    <b>Vehicles:</b> {row['vehicle_count']}<br>
    <b>Avg Speed:</b> {row['avg_speed']} km/h
    """
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=max(8, row['vehicle_count'] / 4),
        popup=folium.Popup(popup_html, max_width=250),
        color='black', weight=2,
        fillColor=col, fillOpacity=0.8,
        tooltip=f"{row['location']}: {row['vehicle_count']} cars"
    ).add_to(m)

st_folium(m, width=700, height=500)

c1, c2 = st.columns(2)
c1.subheader("Traffic by Location")
c_data = data.set_index('location')['vehicle_count']
c1.bar_chart(c_data)

c2.subheader("Speed vs Traffic")
scat_data = data[['vehicle_count', 'avg_speed']]
scat_data.columns = ['Traffic', 'Speed']
c2.scatter_chart(scat_data.set_index('Traffic'))

st.subheader("Detailed Info")
def style_table(val):
    color = ''
    if val >= thresh * 1.2:
        color = 'background-color: #ffcccc'
    elif val >= thresh:
        color = 'background-color: #ffe6cc'
    return color

df2 = data[['location', 'vehicle_count', 'avg_speed', 'wait_time']]
st.dataframe(
    df2.style.apply(lambda x: x.map(style_table) if x.name == 'vehicle_count' else [''] * len(x)),
    use_container_width=True
)

st.subheader("Alerts")
crit_locs = data[data['vehicle_count'] >= thresh * 1.2]
mod_locs = data[(data['vehicle_count'] >= thresh) & (data['vehicle_count'] < thresh * 1.2)]

if not crit_locs.empty:
    st.error("CRITICAL CONGESTION!")
    for i, loc in crit_locs.iterrows():
        st.error(f"-> {loc['location']}: {loc['vehicle_count']} vehicles")

if not mod_locs.empty:
    st.warning("Moderate Traffic")
    for i, loc in mod_locs.iterrows():
        st.warning(f"-> {loc['location']}: {loc['vehicle_count']} vehicles")

if crit_locs.empty and mod_locs.empty:
    st.success("All clear!")

st.markdown("---")
st.caption(f"Last updated: {now.strftime('%H:%M:%S')}")
