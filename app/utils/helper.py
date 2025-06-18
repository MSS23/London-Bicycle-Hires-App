import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import pydeck as pdk
from sklearn.neighbors import BallTree


EARTH_RADIUS_M = 6_371_000


# --------------------------------------------------------------------------------------------#
def non_numeric_mask(series):
    return ~series.astype(str).str.isnumeric()


def dq_validity_bike_hire(df, return_masks=False):
    df = df.copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

    # Define all validation rules
    masks = {
        "Year not 2015-2023": ~df["start_date"].dt.year.between(2015, 2023),
        "Duration ≤ 0 OR ≥ 86400": (df["duration"] <= 0) | (df["duration"] >= 86400),
        "bike_id non-numeric": non_numeric_mask(df["bike_id"]),
        "start_station_id non-numeric": non_numeric_mask(df["start_station_id"]),
        "end_station_id non-numeric": non_numeric_mask(df["end_station_id"]),
        "rental_id non-numeric": non_numeric_mask(df["rental_id"]),
    }

    # Build summary table
    summary = pd.DataFrame(
        {
            "rule": list(masks.keys()),
            "invalid_rows": [mask.sum() for mask in masks.values()],
        }
    )
    summary["total_rows"] = len(df)
    summary["invalid_%"] = (
        summary["invalid_rows"] / summary["total_rows"] * 100
    ).round(2)

    return (summary, masks) if return_masks else summary


# ------------------------------------------------------------------------------------------------#

#
# Bike Maintenance
#


def bikes_flagged_for_service(df, min_issues=3):
    fault_mask = df["invalid_duration"] | df["invalid_bike_id"]
    return (
        df[fault_mask]
        .groupby("bike_id")
        .size()
        .reset_index(name="issues")
        .query("issues >= @min_issues")
        .sort_values("issues", ascending=False)
    )


def bikes_to_be_concerned(df, speed_kmh=15.0):
    df = df.copy()
    if "distance_m" not in df.columns:
        if all(
            col in df.columns
            for col in ["start_lat", "start_lon", "end_lat", "end_lon"]
        ):
            lat1, lon1, lat2, lon2 = map(
                np.radians,
                [df["start_lat"], df["start_lon"], df["end_lat"], df["end_lon"]],
            )
            a = (
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
            )
            df["distance_m"] = 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))
        else:
            df["distance_m"] = df["duration"] * (speed_kmh * 1000 / 3600)
    total_dist = (
        df.groupby("bike_id")["distance_m"].sum().reset_index(name="total_distance_m")
    )
    median_dist = total_dist["total_distance_m"].median()
    return total_dist[total_dist["total_distance_m"] > median_dist].assign(
        flag_reason="Above median distance travelled"
    )


def dq_validity_bike_triage(df, return_masks=False):
    masks = {
        "⚠️ Year not in 2015–2023 (possible test/faulty clock)": ~df[
            "start_date"
        ].dt.year.between(2015, 2023),
        "⏱️ Duration ≤ 0 or > 24h (possible logging or docking error)": (
            df["duration"] <= 0
        )
        | (df["duration"] >= 86400),
        "🔧 Bike ID not recognised (likely unregistered or test bike)": non_numeric_mask(
            df["bike_id"]
        ),
        "📍 Start station invalid (bike may not have docked in)": non_numeric_mask(
            df["start_station_id"]
        ),
        "📍 End station invalid (bike may not have docked out)": non_numeric_mask(
            df["end_station_id"]
        ),
        "🧾 Rental session corrupt or missing ID": non_numeric_mask(df["rental_id"]),
    }

    summary = {rule: mask.sum() for rule, mask in masks.items()}
    summary_df = pd.DataFrame.from_dict(
        summary, orient="index", columns=["Flagged Records"]
    )
    summary_df.index.name = "Validation Rule"
    summary_df = summary_df.reset_index()

    if return_masks:
        return summary_df, masks
    return summary_df


# ------------------------------------------------------------------------------------------------------------------------------#

#
# Station Capacity
#


def get_bikes_at_station_date(df, start_dt, end_dt):
    df_window = df[(df["end_date"] >= start_dt) & (df["end_date"] < end_dt)]
    return (
        df_window.groupby("end_station_id")["bike_id"]
        .nunique()
        .reset_index(name="bikes_present")
    )


def get_bikes_at_station_right_now(df):
    """
    Returns number of bikes at each end station up to the simulated current time (17 June 2022 with today's clock).
    """
    uk_tz = pytz.timezone("Europe/London")
    now_uk = datetime.now(uk_tz)
    hour_minute = now_uk.strftime("%H:%M")
    reference_now = pd.Timestamp(f"2022-06-17 {hour_minute}", tz=uk_tz)
    one_hour_ago = reference_now - timedelta(hours=1)

    df_filtered = df[
        (df["end_date"] >= one_hour_ago) & (df["end_date"] < reference_now)
    ]

    # Count unique bike IDs per end station
    return (
        df_filtered.groupby("end_station_id")["bike_id"]
        .nunique()
        .reset_index(name="bikes_present")
    )


def merge_station_status(stations, bikes, thresh=0.75):
    merged = stations.merge(bikes, left_on="id", right_on="end_station_id", how="left")
    merged["bikes_present"] = merged["bikes_present"].fillna(0).astype(int)
    merged["capacity_pct"] = merged["bikes_present"] / merged["docks_count"]
    merged["at_capacity"] = merged["capacity_pct"] >= thresh
    return merged


def build_ball_tree(df):
    coords = np.radians(df[["latitude", "longitude"]].to_numpy())
    return BallTree(coords, metric="haversine"), coords


def get_nearest_stations(tree, coords, df, idx, k=5):
    dist, ids = tree.query(coords[idx].reshape(1, -1), k=k + 1)
    dists_m = dist[0][1:] * EARTH_RADIUS_M
    return (
        df.iloc[ids[0][1:]].assign(distance_m=dists_m.round(1)).reset_index(drop=True)
    )


def get_under_capacity_stations(df, capacity_threshold=0.25):
    return df[df["capacity_pct"] < capacity_threshold].sort_values("capacity_pct")


def find_suitable_rebalance_target(tree, coords, df, idx, k=5):
    """
    Returns up to k nearest stations (excluding self) that have at least 50% dock availability.
    """

    EARTH_RADIUS_M = 6_371_000

    # Find k+1 because the first result is the origin station itself
    dist, ids = tree.query(coords[idx].reshape(1, -1), k=k + 1)
    dists_m = dist[0][1:] * EARTH_RADIUS_M  # exclude self
    nearest_ids = ids[0][1:]

    # Get candidate stations
    candidates = df.iloc[nearest_ids].copy()
    candidates["distance_m"] = dists_m.round(1)

    # Calculate available docks and ratio
    candidates["available_docks"] = (
        candidates["docks_count"] - candidates["bikes_present"]
    )
    candidates["available_ratio"] = (
        candidates["available_docks"] / candidates["docks_count"]
    )

    # Filter for stations with at least 50% dock availability
    return (
        candidates[candidates["available_ratio"] >= 0.5]
        .sort_values("available_ratio", ascending=False)
        .reset_index(drop=True)
    )
