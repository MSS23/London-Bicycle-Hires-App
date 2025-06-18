import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from utils.data_loader import load_trips_data, load_stations_data
from utils.helper import (
    get_bikes_at_station_date,
    merge_station_status,
    build_ball_tree,
    get_nearest_stations,
    get_under_capacity_stations,
    find_suitable_rebalance_target,
)


def show_station_capacity():
    st.subheader("🌇 Station Capacity & Rebalancing")

    # Load data
    trips_df = load_trips_data()
    stations_df = load_stations_data()

    # Time window selection
    st.sidebar.header("Time Window")
    uk_tz = pytz.timezone("Europe/London")
    current_hour = datetime.now(uk_tz).hour
    selected_hour = st.sidebar.slider("Select hour of day (BST)", 0, 23, current_hour)

    # Define 3-hour historical window ending at selected hour
    end_dt = uk_tz.localize(datetime(2022, 6, 17, selected_hour, 0))
    start_dt = end_dt - timedelta(hours=3)
    st.caption(
        f"3-hour window: {start_dt.strftime('%H:%M')} to {end_dt.strftime('%H:%M')} on 17 June 2022"
    )

    # Merge bike usage with station data
    bikes_present = get_bikes_at_station_date(trips_df, start_dt, end_dt)
    station_status = merge_station_status(stations_df, bikes_present)

    # Rebalance suggestion from any station
    st.markdown("### 🔁 Find Nearest Station to Redistribute From Selected Station")
    station_options = station_status.set_index("name")
    selected_station_name = st.selectbox(
        "Choose a station to redistribute from:", station_options.index.tolist()
    )

    origin_row = station_options.loc[selected_station_name]
    origin_station_id = origin_row["id"]

    # Convert station ID to index in stations_df for spatial lookup
    origin_idx = stations_df[stations_df["id"] == origin_station_id].index[0]

    # Build spatial tree and find nearest stations with ≥50% available docks
    tree, latlon_rad = build_ball_tree(stations_df)
    candidates = find_suitable_rebalance_target(
        tree, latlon_rad, station_status, idx=origin_idx
    )

    if candidates.empty:
        st.warning(
            f"No nearby stations with 50%+ dock availability found from `{selected_station_name}`."
        )
    else:
        st.markdown(
            f"**Best nearby stations to offload bikes from `{selected_station_name}`:**"
        )
        st.dataframe(
            candidates[
                [
                    "name",
                    "docks_count",
                    "bikes_present",
                    "available_docks",
                    "available_ratio",
                    "distance_m",
                ]
            ]
            .rename(
                columns={
                    "name": "Candidate Station",
                    "docks_count": "Docks",
                    "bikes_present": "Current Bikes",
                    "available_docks": "Free Docks",
                    "available_ratio": "Availability %",
                    "distance_m": "Distance (m)",
                }
            )
            .style.format({"Availability %": "{:.0%}", "Distance (m)": "{:.0f}"})
        )

    # Show overutilised stations
    st.markdown("### 🚧 Stations Above 75% Capacity")
    high_util = station_status[station_status["at_capacity"]]
    if high_util.empty:
        st.info("No stations above 75% capacity.")
    else:
        st.dataframe(
            high_util[["name", "docks_count", "bikes_present", "capacity_pct"]]
            .rename(
                columns={
                    "name": "Station",
                    "docks_count": "Docks",
                    "bikes_present": "Bikes",
                    "capacity_pct": "% Capacity",
                }
            )
            .sort_values("% Capacity", ascending=False)
            .style.format({"% Capacity": "{:.0%}"})
        )

    # Show underutilised stations
    st.markdown("### 📉 Underutilised Stations (< 25% Capacity)")
    underutilised = get_under_capacity_stations(station_status, capacity_threshold=0.25)
    if underutilised.empty:
        st.info("No underutilised stations found.")
    else:
        st.dataframe(
            underutilised[["name", "docks_count", "bikes_present", "capacity_pct"]]
            .rename(
                columns={
                    "name": "Station",
                    "docks_count": "Docks",
                    "bikes_present": "Bikes",
                    "capacity_pct": "% Capacity",
                }
            )
            .style.format({"% Capacity": "{:.0%}"})
        )
