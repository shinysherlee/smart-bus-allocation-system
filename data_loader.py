from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).parent / "data" / "mtc"


def _read_csv_checked(filename, required_columns):
    """Read a GTFS file and validate its required columns."""
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    df = pd.read_csv(path, dtype=str).fillna("")
    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {sorted(missing)}"
        )

    return df


@st.cache_data
def load_routes():
    routes = _read_csv_checked(
        "routes.txt",
        {"route_id", "route_short_name", "route_long_name"},
    )

    routes = routes.drop_duplicates(subset="route_id")
    routes = routes[
        routes["route_id"].str.strip().ne("")
        & routes["route_long_name"].str.strip().ne("")
    ].copy()

    routes["display_name"] = (
        routes["route_short_name"].str.strip()
        + " — "
        + routes["route_long_name"].str.strip()
    )

    return routes.sort_values(
        ["route_short_name", "route_long_name"]
    ).reset_index(drop=True)


@st.cache_data
def load_stops():
    stops = _read_csv_checked(
        "stops.txt",
        {"stop_id", "stop_name"},
    )

    stops = stops.drop_duplicates(subset="stop_id").copy()

    for column in ("stop_lat", "stop_lon"):
        if column not in stops.columns:
            stops[column] = ""
        stops[column] = pd.to_numeric(
            stops[column], errors="coerce"
        )

    return stops.reset_index(drop=True)



@st.cache_data
def load_route_stops(route_id):
    """Return stops from a trip that belongs to the selected route."""

    columns = [
        "stop_id",
        "stop_name",
        "stop_sequence",
        "stop_lat",
        "stop_lon",
    ]

    trips = _read_csv_checked(
        "trips.txt",
        {"trip_id", "route_id"},
    )

    # Normalize IDs before comparing them.
    trips["trip_id"] = trips["trip_id"].str.strip()
    trips["route_id"] = trips["route_id"].str.strip()

    selected_route_id = str(route_id).strip()

    route_trips = trips[
        trips["route_id"] == selected_route_id
    ]

    if route_trips.empty:
        return pd.DataFrame(columns=columns)

    stop_times = _read_csv_checked(
        "stop_times.txt",
        {"trip_id", "stop_id", "stop_sequence"},
    )

    stop_times["trip_id"] = stop_times["trip_id"].str.strip()
    stop_times["stop_id"] = stop_times["stop_id"].str.strip()

    # Keep only trips belonging to this route that have stop records.
    route_stop_times = stop_times[
        stop_times["trip_id"].isin(route_trips["trip_id"])
    ].copy()

    if route_stop_times.empty:
        return pd.DataFrame(columns=columns)

    # Choose the trip with the most recorded stops.
    trip_counts = route_stop_times.groupby("trip_id").size()
    best_trip_id = trip_counts.idxmax()

    trip_stops = route_stop_times[
        route_stop_times["trip_id"] == best_trip_id
    ].copy()

    trip_stops["stop_sequence"] = pd.to_numeric(
        trip_stops["stop_sequence"],
        errors="coerce",
    )

    stops = load_stops()

    result = trip_stops.merge(
        stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]],
        on="stop_id",
        how="left",
    )

    result = result.sort_values("stop_sequence")

    return result[columns].reset_index(drop=True)
