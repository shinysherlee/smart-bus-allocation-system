
import streamlit as st
import pandas as pd

from data_loader import load_routes, load_route_stops
from allocation import allocate_spare_buses
from allocation_heap import allocate_spare_buses_heap


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Bus Allocation",
    page_icon="🚌",
    layout="wide",
)

st.title("🚌 Smart Bus Allocation System")

st.write(
    "A prototype that allocates spare buses across selected Chennai "
    "bus routes using passenger-demand estimates and assumed costs."
)

st.info(
    "Route names and stop information come from a community-maintained "
    "Chennai GTFS dataset. Passenger demand, existing bus assignments, "
    "spare fleet availability, and operating costs are simulated. "
    "This app does not use live passenger counts or live bus locations."
)


# --------------------------------------------------
# Load route data
# --------------------------------------------------

try:
    route_df = load_routes()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Could not load route data: {exc}")
    st.stop()

route_df = route_df[
    route_df["route_short_name"].str.strip().ne("")
].copy()

if route_df.empty:
    st.error("No routes with route short names were found.")
    st.stop()

route_labels = {}

for _, row in route_df.iterrows():
    label = (
        f"{row['route_short_name']} — {row['route_long_name']} "
        f"(ID: {row['route_id']})"
    )
    route_labels[label] = row["route_id"]

all_labels = list(route_labels.keys())


# --------------------------------------------------
# 1. Select routes
# --------------------------------------------------

st.subheader("1. Select Chennai bus routes")

st.caption(
    f"{len(all_labels):,} route records with route short names are "
    "available. Select a small group for this demonstration."
)

default_labels = all_labels[:3]

selected_labels = st.multiselect(
    "Routes to include in the allocation",
    options=all_labels,
    default=default_labels,
    help="Route names are from the dataset; demand and costs are simulated.",
    key="selected_route_labels",
)

selected_route_ids = [
    route_labels[label] for label in selected_labels
]

if not selected_labels:
    st.warning("Select at least one route to configure allocation.")


# --------------------------------------------------
# 2. Fleet settings
# --------------------------------------------------

st.subheader("2. Fleet settings")

col1, col2, col3 = st.columns(3)

with col1:
    capacity = st.number_input(
        "Passenger capacity per bus (assumed)",
        min_value=1,
        value=40,
        step=1,
    )

with col2:
    spare_buses = st.number_input(
        "Available spare buses (simulated)",
        min_value=0,
        value=1,
        step=1,
    )

with col3:
    algorithm = st.selectbox(
        "Allocation algorithm",
        options=[
            "Greedy (linear scan)",
            "Heap (priority queue)",
        ],
        help=(
            "Greedy scans routes for the highest priority. Heap uses "
            "a priority queue to select the highest-priority route."
        ),
    )


# --------------------------------------------------
# 3. Simulated crowd-report session state
# --------------------------------------------------

if "reported_extra" not in st.session_state:
    st.session_state["reported_extra"] = {}

if "crowd_report_history" not in st.session_state:
    st.session_state["crowd_report_history"] = []

for route_id in selected_route_ids:
    st.session_state["reported_extra"].setdefault(route_id, 0)


# --------------------------------------------------
# 4. Route demand and costs
# --------------------------------------------------

st.subheader("3. Route demand and costs (simulated)")

st.caption(
    "These are editable demonstration values, not measured passenger "
    "counts or verified route-level operating costs."
)

routes = {}

default_values = [
    {"passengers": 90, "assigned_buses": 2, "cost_per_bus": 120},
    {"passengers": 25, "assigned_buses": 1, "cost_per_bus": 80},
    {"passengers": 70, "assigned_buses": 2, "cost_per_bus": 100},
]

columns = st.columns(3)

for i, label in enumerate(selected_labels):
    route_id = route_labels[label]
    defaults = default_values[i % len(default_values)]

    with columns[i % 3]:
        st.markdown(f"**{label}**")

        passengers = st.number_input(
            "Base waiting passengers (simulated)",
            min_value=0,
            value=defaults["passengers"],
            step=1,
            key=f"passengers_{route_id}",
        )

        assigned = st.number_input(
            "Buses currently assigned (simulated)",
            min_value=0,
            value=defaults["assigned_buses"],
            step=1,
            key=f"buses_{route_id}",
        )

        cost = st.number_input(
            "Cost per bus (assumed units)",
            min_value=1,
            value=defaults["cost_per_bus"],
            step=10,
            key=f"cost_{route_id}",
        )

        extra = int(
            st.session_state["reported_extra"].get(route_id, 0)
        )
        effective_passengers = int(passengers) + extra

        routes[label] = {
            "route_id": route_id,
            "passengers": effective_passengers,
            "assigned_buses": int(assigned),
            "cost_per_bus": int(cost),
        }

        st.caption(
            f"Effective demand: {effective_passengers} "
            f"({int(passengers)} base + {extra} reported)"
        )


# --------------------------------------------------
# 5. Simulated crowd reports
# --------------------------------------------------

st.subheader("📢 Simulated public crowd reports")

st.write(
    "Submit a demonstration report to add waiting passengers to a "
    "selected route. This does not send or receive real-time data."
)

if selected_labels:
    with st.form("crowd_report_form"):
        report_label = st.selectbox(
            "Select route for the report",
            options=selected_labels,
        )

        additional_passengers = st.number_input(
            "Additional waiting passengers",
            min_value=1,
            value=20,
            step=5,
        )

        submit_report = st.form_submit_button("Submit crowd report")

    if submit_report:
        report_id = route_labels[report_label]
        added = int(additional_passengers)

        st.session_state["reported_extra"][report_id] = (
            int(st.session_state["reported_extra"].get(report_id, 0))
            + added
        )

        st.session_state["crowd_report_history"].append(
            {
                "Route": report_label,
                "Additional passengers": added,
            }
        )

        st.success(
            f"Added {added} simulated passengers to {report_label}."
        )
        st.rerun()
else:
    st.caption("Select at least one route to submit a crowd report.")

if st.session_state["crowd_report_history"]:
    st.write("Crowd report history")

    st.dataframe(
        pd.DataFrame(st.session_state["crowd_report_history"]),
        hide_index=True,
        use_container_width=True,
    )

if st.button("Reset all crowd reports"):
    st.session_state["reported_extra"] = {
        route_id: 0
        for route_id in st.session_state["reported_extra"]
    }
    st.session_state["crowd_report_history"] = []
    st.rerun()


# --------------------------------------------------
# 6. Calculate allocation
# --------------------------------------------------

st.divider()

calculate = st.button(
    "Calculate bus allocation",
    type="primary",
    disabled=not routes,
)

if calculate:
    allocation_input = {
        label: {
            "passengers": data["passengers"],
            "assigned_buses": data["assigned_buses"],
            "cost_per_bus": data["cost_per_bus"],
        }
        for label, data in routes.items()
    }

    if algorithm.startswith("Heap"):
        assignments, decisions, unused = allocate_spare_buses_heap(
            allocation_input,
            int(capacity),
            int(spare_buses),
        )
        algo_label = "Heap (priority queue)"
    else:
        assignments, decisions, unused = allocate_spare_buses(
            allocation_input,
            int(capacity),
            int(spare_buses),
        )
        algo_label = "Greedy (linear scan)"

    st.subheader(f"📊 Allocation results — {algo_label}")

    rows = []

    for label, data in allocation_input.items():
        buses_before = data["assigned_buses"]
        buses_after = assignments[label]
        passengers = data["passengers"]
        cost_per_bus = data["cost_per_bus"]

        rows.append(
            {
                "Route": label,
                "Route ID": routes[label]["route_id"],
                "Passenger demand (simulated)": passengers,
                "Buses before": buses_before,
                "Buses after": buses_after,
                "Seats after": buses_after * int(capacity),
                "Unmet demand": max(
                    0, passengers - buses_after * int(capacity)
                ),
                "Cost per bus (assumed units)": cost_per_bus,
                "Total cost after (assumed units)": (
                    buses_after * cost_per_bus
                ),
            }
        )

    results = pd.DataFrame(rows)

    st.dataframe(
        results,
        hide_index=True,
        use_container_width=True,
    )

    initial_cost = sum(
        data["assigned_buses"] * data["cost_per_bus"]
        for data in allocation_input.values()
    )

    final_cost = sum(
        assignments[label] * allocation_input[label]["cost_per_bus"]
        for label in allocation_input
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Initial operating cost (assumed)",
        f"{initial_cost} units",
    )

    col2.metric(
        "Cost after allocation (assumed)",
        f"{final_cost} units",
        delta=f"{final_cost - initial_cost} units",
    )

    col3.metric("Spare buses unused", unused)

    st.subheader("🧠 Allocation decisions")

    if decisions:
        for number, decision in enumerate(decisions, start=1):
            st.write(
                f"**{number}. {decision['route']}** received one spare bus. "
                f"Unmet demand before allocation: "
                f"{decision['unmet_before']} passengers. "
                f"Priority score: {decision['priority_score']}."
            )
    else:
        st.success(
            "No additional buses were allocated for the current inputs."
        )

    total_unmet = int(results["Unmet demand"].sum())

    st.metric(
        "Passengers still exceeding available capacity",
        total_unmet,
    )

    st.caption(
        "Prototype limitation: route names come from a community-maintained "
        "transit feed. Demand and costs are simulated, and the priority score "
        "is a heuristic rather than a validated real-world operating model."
    )


# --------------------------------------------------
# 7. Route stops and map
# --------------------------------------------------

st.divider()
st.header("🗺️ Route Stops and Map")

st.caption(
    "Choose a route to inspect stops from one representative trip. "
    "The map shows dataset stop coordinates, not live bus locations."
)

map_route_label = st.selectbox(
    "Choose a route to view its stops",
    options=all_labels,
    key="map_route_selector",
)

map_route_id = route_labels[map_route_label]

try:
    route_stops = load_route_stops(map_route_id)

    if route_stops.empty:
        st.warning(
            "No stops were found for the representative trip of this route."
        )
    else:
        st.subheader(f"Stops: {map_route_label}")

        st.dataframe(
            route_stops[["stop_sequence", "stop_name", "stop_id"]],
            use_container_width=True,
            hide_index=True,
        )

        map_points = route_stops.dropna(
            subset=["stop_lat", "stop_lon"]
        ).copy()

        map_points = map_points[
            map_points["stop_lat"].between(-90, 90)
            & map_points["stop_lon"].between(-180, 180)
        ]

        if not map_points.empty:
            map_points = map_points.rename(
                columns={
                    "stop_lat": "latitude",
                    "stop_lon": "longitude",
                }
            )

            st.map(map_points[["latitude", "longitude"]])
        else:
            st.info(
                "No valid coordinates are available for these stops."
            )

except (
    FileNotFoundError,
    ValueError,
    KeyError,
    pd.errors.ParserError,
) as exc:
    st.error(f"Could not load route stops: {exc}")
