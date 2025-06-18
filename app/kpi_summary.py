import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from utils.data_loader import load_trips_data, load_stations_data
from utils.helper import (
    dq_validity_bike_hire,
    get_bikes_at_station_right_now,
)


def show_kpi_summary():
    st.subheader("📊 KPI Summary")

    # Fake refresh button
    colA, colB = st.columns([6, 1])
    with colB:
        if st.button("🔄 Refresh"):
            st.experimental_rerun()

    # Load trip data and station data
    trips_df = load_trips_data()
    stations_df = load_stations_data()

    # Convert start_date to London timezone (BST-aware)
    trips_df["start_date"] = pd.to_datetime(
        trips_df["start_date"], utc=True
    ).dt.tz_convert("Europe/London")

    # Get current time in BST and simulate that time on 17 June 2022
    uk_tz = pytz.timezone("Europe/London")
    now_uk = datetime.now(uk_tz)
    hour_minute = now_uk.strftime("%H:%M")

    # Simulate 17 June 2022 with "now" time and related references
    reference_date_now = pd.Timestamp(f"2022-06-17 {hour_minute}", tz=uk_tz)
    reference_date_full = pd.Timestamp("2022-06-17", tz=uk_tz)
    start_of_month = reference_date_full.replace(day=1)
    yesterday = reference_date_full - timedelta(days=1)

    # Today's data (simulated for 17 June 2022)
    today_df = trips_df[
        (trips_df["start_date"] >= reference_date_full)
        & (trips_df["start_date"] < reference_date_now)
    ]

    # KPI Display
    st.markdown(
        f"### \U00002705 Today's Activity (17 June 2022 – up to {hour_minute} BST)"
    )
    trips_today = len(today_df)
    unique_bikes_today = today_df["bike_id"].nunique()
    stations_used_today = pd.concat(
        [today_df["start_station_id"], today_df["end_station_id"]]
    ).nunique()
    busiest_start_today = (
        today_df["start_station_name"].value_counts().idxmax()
        if not today_df.empty
        else "N/A"
    )
    busiest_end_today = (
        today_df["end_station_name"].value_counts().idxmax()
        if not today_df.empty
        else "N/A"
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])
    col1.metric("Trips Today", f"{trips_today:,}")
    col2.metric("Unique Bikes", f"{unique_bikes_today:,}")
    col3.metric("Stations Used", f"{stations_used_today:,}")

    col4, col5 = st.columns(2)
    col4.metric("Busiest Start Station", busiest_start_today)
    col5.metric("Busiest End Station", busiest_end_today)

    if not today_df.empty:
        bike_counts = today_df["bike_id"].value_counts()
        top_bike_today = bike_counts.idxmax()
        trips_top_bike_today = bike_counts.max()

        # Run data quality check
        _, dq_masks_today = dq_validity_bike_hire(today_df, return_masks=True)
        issue_mask_today = pd.concat(dq_masks_today.values(), axis=1).any(
            axis=1
        )  # add the mask values as a column
        bikes_with_issues_today = today_df.loc[issue_mask_today, "bike_id"].nunique()

        # Identify top faulty bike
        bikes_with_issues_df = today_df[issue_mask_today].copy()
        bikes_with_issues_df["bike_id"] = bikes_with_issues_df["bike_id"].astype(str)
        if not bikes_with_issues_df.empty:
            top_faulty_bike = bikes_with_issues_df["bike_id"].value_counts().idxmax()
            top_faulty_bike_issues = (
                bikes_with_issues_df["bike_id"].value_counts().max()
            )
        else:
            top_faulty_bike = "N/A"
            top_faulty_bike_issues = 0
    else:
        top_bike_today = "N/A"
        trips_top_bike_today = 0
        bikes_with_issues_today = 0
        top_faulty_bike = "N/A"
        top_faulty_bike_issues = 0

    # Display Top Bike
    st.markdown("#### \U0001f6b2 Top Bike Today")
    st.metric("Bike ID", top_bike_today, f"{trips_top_bike_today} trips")

    # Display Bike with Most Issues
    st.markdown("#### \U0001f527 Bike with Most Issues Today")
    st.metric("Bike ID", top_faulty_bike, f"{top_faulty_bike_issues} issues")

    # Display Total Bikes with Issues
    st.metric("\u26a0\ufe0f Bikes with Issues Today", f"{bikes_with_issues_today:,}")

    st.markdown("---")

    # SECTION 2: MONTHLY SUMMARY
    month_df = trips_df[
        (trips_df["start_date"] >= start_of_month)
        & (trips_df["start_date"] < reference_date_full)
    ]

    st.markdown("### \U0001f4c5 Monthly Summary – June (up to 17th)")

    # Same summary metrics for monthly too
    total_trips = len(month_df)
    total_bikes = month_df["bike_id"].nunique()
    total_stations = pd.concat(
        [month_df["start_station_id"], month_df["end_station_id"]]
    ).nunique()
    busiest_start = (
        month_df["start_station_name"].value_counts().idxmax()
        if not month_df.empty
        else "N/A"
    )
    busiest_end = (
        month_df["end_station_name"].value_counts().idxmax()
        if not month_df.empty
        else "N/A"
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])
    col1.metric("Total Trips", f"{total_trips:,}")
    col2.metric("Unique Bikes", f"{total_bikes:,}")
    col3.metric("Stations Used", f"{total_stations:,}")

    col4, col5 = st.columns(2)
    col4.metric("Busiest Start Station", busiest_start)
    col5.metric("Busiest End Station", busiest_end)

    # Identify top-performing bike and issues
    if not month_df.empty:
        month_bike_counts = month_df["bike_id"].value_counts()
        top_bike_month = month_bike_counts.idxmax()
        trips_top_bike_month = month_bike_counts.max()

        # Data quality
        _, dq_masks_month = dq_validity_bike_hire(month_df, return_masks=True)
        issue_mask_month = pd.concat(dq_masks_month.values(), axis=1).any(axis=1)
        bikes_with_issues_month = month_df.loc[issue_mask_month, "bike_id"].nunique()

        bikes_with_issues_df = month_df[issue_mask_month].copy()
        bikes_with_issues_df["bike_id"] = bikes_with_issues_df["bike_id"].astype(str)

        if not bikes_with_issues_df.empty:
            top_faulty_bike_month = (
                bikes_with_issues_df["bike_id"].value_counts().idxmax()
            )
            top_faulty_bike_issues_month = (
                bikes_with_issues_df["bike_id"].value_counts().max()
            )
        else:
            top_faulty_bike_month = "N/A"
            top_faulty_bike_issues_month = 0
    else:
        top_bike_month = "N/A"
        trips_top_bike_month = 0
        bikes_with_issues_month = 0
        top_faulty_bike_month = "N/A"
        top_faulty_bike_issues_month = 0

    # Display bike KPIs for the month
    st.markdown("#### \U0001f6b2 Top Bike This Month")
    st.metric("Bike ID", top_bike_month, f"{trips_top_bike_month} trips")

    st.markdown("#### \U0001f527 Bike with Most Issues This Month")
    st.metric(
        "Bike ID", top_faulty_bike_month, f"{top_faulty_bike_issues_month} issues"
    )

    st.metric(
        "\u26a0\ufe0f Bikes with Issues This Month", f"{bikes_with_issues_month:,}"
    )

    st.markdown("---")

    # Redistribution KPIs
    st.markdown("### \U0001f500 Station Summary")
    bikes_present_df = get_bikes_at_station_right_now(trips_df)
    station_status = stations_df.merge(
        bikes_present_df, how="left", left_on="id", right_on="end_station_id"
    )
    station_status["bikes_present"] = station_status["bikes_present"].fillna(0)
    station_status["capacity_pct"] = (
        (station_status["bikes_present"] / station_status["docks_count"]) * 100
    ).round(2).astype(str) + "%"

    over_capacity = station_status[
        station_status["bikes_present"] / station_status["docks_count"] >= 0.75
    ]
    under_capacity = station_status[
        station_status["bikes_present"] / station_status["docks_count"] < 0.25
    ]

    col1, col2 = st.columns(2)
    col1.metric("\U0001f6a7 Stations >75% Capacity", len(over_capacity))
    col2.metric("\U0001f4e6 Stations <25% Capacity", len(under_capacity))

    if not over_capacity.empty:
        st.markdown("#### Top 3 Overloaded Stations")
        st.dataframe(
            over_capacity.sort_values("capacity_pct", ascending=False)[
                ["name", "bikes_present", "docks_count", "capacity_pct"]
            ].head(3)
        )

    if not under_capacity.empty:
        st.markdown("#### Top 3 Underused Stations")
        st.dataframe(
            under_capacity.sort_values("capacity_pct", ascending=True)[
                ["name", "bikes_present", "docks_count", "capacity_pct"]
            ].head(3)
        )
