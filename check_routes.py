
import pandas as pd
from pathlib import Path

folder = Path("data/mtc")

trips = pd.read_csv(folder / "trips.txt", dtype=str).fillna("")
stop_times = pd.read_csv(
    folder / "stop_times.txt", dtype=str
).fillna("")

for column in ["route_id", "trip_id"]:
    trips[column] = trips[column].str.strip()

stop_times["trip_id"] = stop_times["trip_id"].str.strip()

print("ROUTE ID | TRIPS | STOP-TIME ROWS")

for route_id in ["23249", "23247", "18327"]:
    route_trips = trips[trips["route_id"] == route_id]
    trip_ids = set(route_trips["trip_id"])

    matching_stops = stop_times[
        stop_times["trip_id"].isin(trip_ids)
    ]

    print(
        f"{route_id} | {len(route_trips)} | "
        f"{len(matching_stops)}"
    )

