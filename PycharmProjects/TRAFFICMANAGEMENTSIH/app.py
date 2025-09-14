import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from datetime import datetime

# Page setup
st.set_page_config(page_title="Smart Traffic Dashboard", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login credentials (demo purposes)
USERS = {
    "admin": "sih123",
    "Kuldeep": "jainz",
    "Prakarsh": "batman"
}

def login_page():
    st.title("🚦 Smart Traffic Management System")
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password!")

def dashboard():
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🚦 Smart Traffic Management Dashboard")
    with col2:
        st.write(f"Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Traffic locations with real Bhopal coordinates
    locations = {
        "LALGHATI": [23.2599, 77.4126], "KAROND": [23.2728, 77.4579],
        "BAIRAGARH": [23.2156, 77.3539], "INDRAPURI": [23.2156, 77.3825]
    }
    
    # Generate realistic traffic data with rush hour simulation
    np.random.seed(42)
    hour = datetime.now().hour
    rush_multiplier = 2.5 if hour in [8, 9, 17, 18, 19] else 1.0
    data = []
    for loc, coords in locations.items():
        base_traffic = np.random.randint(20, 40)
        vehicles = int(base_traffic * rush_multiplier * np.random.uniform(0.8, 1.2))
        speed = max(10, 55 - vehicles * 0.6 + np.random.uniform(-5, 5))
        data.append({"location": loc, "vehicles": vehicles, "speed": round(speed, 1), 
                     "lat": coords[0], "lon": coords[1]})
    df = pd.DataFrame(data)
    
    # Sidebar
    threshold = st.sidebar.slider("Congestion Threshold", 20, 80, 50)
    auto_refresh = st.sidebar.checkbox("Auto Refresh")
    if auto_refresh:
        st.rerun()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Traffic", f"{df['vehicles'].max()} vehicles")
    col2.metric("Avg Speed", f"{df['speed'].mean():.1f} km/h")
    col3.metric("Congested", f"{len(df[df['vehicles'] >= threshold])}/{len(df)}")
    
    # Interactive Map with Circles + Heatmap
    st.subheader("🗺️ Traffic Map & Heatmap")
    m = folium.Map(location=[23.2599, 77.4126], zoom_start=12)

    # Circle Markers
    for _, row in df.iterrows():
        color = 'red' if row['vehicles'] >= threshold*1.2 else 'orange' if row['vehicles'] >= threshold else 'green'
        folium.CircleMarker(
            [row['lat'], row['lon']],
            radius=max(8, row['vehicles']/3),
            popup=f"<b>{row['location']}</b><br>Vehicles: {row['vehicles']}<br>Speed: {row['speed']} km/h",
            color='black', weight=2, fillColor=color, fillOpacity=0.8,
            tooltip=f"{row['location']}: {row['vehicles']} vehicles"
        ).add_to(m)

    # Heatmap Layer
    heat_data = [[row['lat'], row['lon'], row['vehicles']] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=25, blur=15, max_zoom=12).add_to(m)

    st_folium(m, height=450, width=750)
    
    # Traffic Camera Feed Placeholder
    st.subheader("🎥 Traffic Camera Feed")
    st.info("📹 Live camera feed would appear here\n\n(OpenCV integration requires opencv-python package)")
    
    # Charts and IoT Data
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Traffic by Location")
        st.bar_chart(df.set_index('location')['vehicles'])
        
    with col2:
        st.subheader("📡 IoT Sensor Data (Demo)")
        sensor_df = pd.DataFrame({
            "Sensor": ["Temperature", "Humidity", "Air Quality", "Noise Level"],
            "Value": [round(np.random.uniform(25, 40), 1),
                      round(np.random.uniform(40, 80), 1),
                      round(np.random.uniform(50, 120), 1),
                      round(np.random.uniform(30, 90), 1)],
            "Unit": ["°C", "%", "AQI", "dB"]
        })
        st.dataframe(sensor_df, hide_index=True)
    
    # Current Traffic Data
    st.subheader("Current Traffic Data")
    st.dataframe(df[['location', 'vehicles', 'speed']], hide_index=True)
    
    # Alerts
    st.subheader("🚨 Alerts")
    critical = df[df['vehicles'] >= threshold*1.2]
    moderate = df[(df['vehicles'] >= threshold) & (df['vehicles'] < threshold*1.2)]
    if len(critical) > 0:
        st.error("🔴 CRITICAL: " + ", ".join([f"{row['location']} ({row['vehicles']})" for _, row in critical.iterrows()]))
    if len(moderate) > 0:
        st.warning("🟡 MODERATE: " + ", ".join([f"{row['location']} ({row['vehicles']})" for _, row in moderate.iterrows()]))
    if len(critical) == 0 and len(moderate) == 0:
        st.success("✅ All traffic flowing normally!")

# Main app logic
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
