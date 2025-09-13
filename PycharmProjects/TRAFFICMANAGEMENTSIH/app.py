import streamlit as st
import pandas as pd
import numpy as np
import time

# Set page layout
st.set_page_config(page_title="Smart Traffic Dashboard", layout="wide")
st.title("🚦 Smart Traffic Management Dashboard (Demo)")

# Generate fake data for demo
np.random.seed(42)
locations = ["LALGHATI", "KAROND", "BAIRAGARH", "INDRAPURI"]
latitudes = [28.6139, 28.6270, 28.6200, 28.6300]
longitudes = [77.2090, 77.2167, 77.2000, 77.2300]

# Create a random dataset
df = pd.DataFrame({
    "location": np.random.choice(locations, 20),
    "vehicle_count": np.random.randint(10, 70, 20),
    "avg_speed": np.random.uniform(10, 50, 20).round(2),
    "lat": np.random.choice(latitudes, 20),
    "lon": np.random.choice(longitudes, 20),
    "timestamp": pd.date_range("2025-09-13 10:00", periods=20, freq="min")
})

# Sidebar controls
st.sidebar.header("Filters")
threshold = st.sidebar.slider("Congestion Alert Threshold (vehicles)", 10, 80, 40)

# Layout: Metrics
st.subheader("Live Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Latest Vehicle Count", int(df["vehicle_count"].iloc[-1]))
col2.metric("Average Speed (km/h)", df["avg_speed"].mean().round(1))
col3.metric("Total Intersections", df["location"].nunique())

# Chart - traffic over time
st.subheader("Traffic Flow Over Time")
st.line_chart(df.set_index("timestamp")["vehicle_count"])

# Map visualization
st.subheader("Traffic Map (Intersections)")
st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"}))

# Table of latest data
st.subheader("Recent Traffic Data")
st.dataframe(df.tail(10))

# Alerts
st.subheader("🚨 Alerts")
latest_count = int(df["vehicle_count"].iloc[-1])
if latest_count >= threshold:
    st.error(f"High congestion at {latest_count} vehicles! (Threshold {threshold})")
else:
    st.success(f"Traffic is normal (latest: {latest_count} vehicles)")


