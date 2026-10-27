
import math


def buses_needed(passengers, capacity):
    """Calculate buses needed to carry the passenger demand."""
    if capacity <= 0:
        raise ValueError("Bus capacity must be greater than zero.")

    return math.ceil(passengers / capacity)


def allocate_spare_buses(routes, capacity, spare_buses):
    """
    Allocate available spare buses to routes with unmet demand.

    Priority score = unmet passenger demand / cost per bus.

    Routes remain fixed. Only the number of buses changes.
    """
    if capacity <= 0:
        raise ValueError("Bus capacity must be greater than zero.")

    if spare_buses < 0:
        raise ValueError("Spare buses cannot be negative.")

    assignments = {
        route: data["assigned_buses"]
        for route, data in routes.items()
    }

    decisions = []

    while spare_buses > 0:
        best_route = None
        best_score = -1

        for route, data in routes.items():
            passengers = data["passengers"]
            buses = assignments[route]

            unmet = max(0, passengers - buses * capacity)

            if unmet > 0:
                cost = data["cost_per_bus"]

                if cost <= 0:
                    continue

                score = unmet / cost

                if score > best_score:
                    best_score = score
                    best_route = route

        # Stop if no route needs another bus.
        if best_route is None:
            break

        unmet_before = max(
            0,
            routes[best_route]["passengers"]
            - assignments[best_route] * capacity
        )

        assignments[best_route] += 1

        decisions.append({
            "route": best_route,
            "unmet_before": unmet_before,
            "priority_score": round(best_score, 3)
        })

        spare_buses -= 1

    return assignments, decisions, spare_buses
