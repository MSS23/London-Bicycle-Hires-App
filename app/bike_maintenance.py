import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
import pydeck as pdk
from utils.data_loader import load_trips_data, load_stations_data
from utils.helper import dq_validity_bike_triage


def show_bike_maintenance():
    st.subheader("🔧 Bike Maintenance Dashboard")

    # Load data
    trips_df = load_trips_data()
    stations_df = load_stations_data()

    # Convert dates to London timezone
    trips_df["start_date"] = pd.to_datetime(
        trips_df["start_date"], utc=True
    ).dt.tz_convert("Europe/London")
    trips_df["end_date"] = pd.to_datetime(trips_df["end_date"], utc=True).dt.tz_convert(
        "Europe/London"
    )

    # Simulate "now" on 17 June 2022 using current London time
    uk_tz = pytz.timezone("Europe/London")
    now_uk = datetime.now(uk_tz)
    hour_minute = now_uk.strftime("%H:%M")
    reference_date_now = pd.Timestamp(f"2022-06-17 {hour_minute}", tz=uk_tz)
    reference_date_full = pd.Timestamp("2022-06-17", tz=uk_tz)
    start_of_month = reference_date_full.replace(day=1)

    # Filter for June 2022 data up to simulated "now"
    trips_df = trips_df[
        (trips_df["start_date"] >= start_of_month)
        & (trips_df["end_date"] <= reference_date_now)
    ]

    # Run data quality checks with operationally meaningful labels
    dq_summary, dq_masks = dq_validity_bike_triage(trips_df, return_masks=True)

    # Combine all masks into one issue mask
    issue_mask = pd.concat(dq_masks.values(), axis=1).any(axis=1)
    triage_df = trips_df[issue_mask].copy()

    # Add issue labels to the triage DataFrame
    triage_df["bike_issue"] = ""
    for rule, mask in dq_masks.items():
        triage_df.loc[mask, "bike_issue"] += rule + "; "

    triage_df["bike_id"] = triage_df["bike_id"].astype(str)

    # --- NEW: Filter by fault type ---
    all_faults = list(dq_masks.keys())
    selected_faults = st.multiselect(
        "🔍 Filter by Fault Type:",
        options=all_faults,
        default=all_faults,
        help="Select one or more fault types to filter flagged bikes",
    )

    fault_filter_mask = triage_df["bike_issue"].apply(
        lambda x: any(fault in x for fault in selected_faults)
    )
    triage_df = triage_df[fault_filter_mask]
    # ----------------------------------

    st.metric("🤖 Bikes flagged for triage (June)", len(triage_df))

    if triage_df.empty:
        st.success("No bikes currently flagged for the selected fault types.")
        return

    # Find bike with most issues
    most_errors_bike = triage_df["bike_id"].value_counts().idxmax()
    st.markdown(f"#### The Bike ID with Most Errors: `{most_errors_bike}`")

    unique_bikes = list(triage_df["bike_id"].unique())
    selected_bike = st.selectbox(
        "Select a flagged bike to inspect:",
        unique_bikes,
        index=unique_bikes.index(most_errors_bike),
    )

    bike_details = (
        triage_df[triage_df["bike_id"] == selected_bike]
        .sort_values("end_date", ascending=False)
        .head(1)
    )

    st.markdown("### 💼 Bike Metadata")
    st.json(
        {
            "Bike ID": selected_bike,
            "Issue(s)": bike_details["bike_issue"].values[0],
            "Start Station": bike_details["start_station_name"].values[0],
            "End Station": bike_details["end_station_name"].values[0],
            "Start Date": str(bike_details["start_date"].values[0]),
            "End Date": str(bike_details["end_date"].values[0]),
            "Duration": int(bike_details["duration"].values[0]),
        }
    )

    st.markdown("---")
    st.markdown("### 📈 All Flagged Rides for this Bike (Last 5)")
    st.dataframe(
        triage_df[triage_df["bike_id"] == selected_bike][
            [
                "start_date",
                "end_date",
                "start_station_name",
                "end_station_name",
                "duration",
                "bike_issue",
            ]
        ]
        .sort_values("end_date", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    # Map of most recent ride’s end location
    st.markdown("### 🗺️ Most Recent Ride Destination")
    if not bike_details.empty:
        end_station = bike_details["end_station_name"].values[0]
        end_info = stations_df[stations_df["name"] == end_station][
            ["latitude", "longitude"]
        ]
        if not end_info.empty:
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=pdk.ViewState(
                        latitude=end_info["latitude"].values[0],
                        longitude=end_info["longitude"].values[0],
                        zoom=13,
                        pitch=50,
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=end_info,
                            get_position="[longitude, latitude]",
                            get_color="[255, 0, 0, 160]",
                            get_radius=100,
                        )
                    ],
                )
            )
        else:
            st.info("End station location not found in station dataset.")
