import streamlit as st
from kpi_summary import show_kpi_summary
from bike_maintenance import show_bike_maintenance
from station_capacity import show_station_capacity

st.set_page_config(page_title="London Cycle Hire – Operational Insights", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Select a Page",
    ["📊 Overview", "🔧 Bike Maintenance", "🌇️ Station Capacity / Rebalancing"],
)

# Route to selected page
if page == "📊 Overview":
    show_kpi_summary()
elif page == "🔧 Bike Maintenance":
    show_bike_maintenance()
elif page == "🌇️ Station Capacity / Rebalancing":
    show_station_capacity()
