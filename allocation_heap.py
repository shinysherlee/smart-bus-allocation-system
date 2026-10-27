
import heapq


def allocate_spare_buses_heap(routes, capacity, spare_buses):
    """
    Allocate spare buses using a max-priority queue (heap).

    Priority score = unmet passenger demand / cost per bus.
    Higher scores are served first.

    The heap uses lazy re-evaluation: after each bus is assigned,
    the route's updated score is re-pushed so the next iteration
    always picks the currently highest-priority route.

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
    heap = []

    # Seed the heap with every route that currently has unmet demand.
    for route, data in routes.items():
        unmet = max(
            0,
            data["passengers"] - assignments[route] * capacity
        )
        cost = data["cost_per_bus"]

        if unmet > 0 and cost > 0:
            score = unmet / cost
            # Python's heapq is a min-heap, so we negate the score
            # to simulate a max-heap (highest score comes out first).
            heapq.heappush(heap, (-score, route))

    while spare_buses > 0 and heap:
        negative_score, route = heapq.heappop(heap)

        # Recalculate unmet demand NOW (assignments may have changed
        # since this entry was pushed — lazy-deletion pattern).
        unmet_before = max(
            0,
            routes[route]["passengers"]
            - assignments[route] * capacity
        )

        # If this heap entry is stale (demand was already met by an
        # earlier allocation), discard it and move on.
        if unmet_before <= 0:
            continue

        # Recalculate the score from live data so the logged value
        # always reflects the moment of allocation, not push time.
        cost = routes[route]["cost_per_bus"]
        current_score = unmet_before / cost

        assignments[route] += 1
        spare_buses -= 1

        decisions.append({
            "route": route,
            "unmet_before": unmet_before,
            "priority_score": round(current_score, 3)
        })

        # Re-push this route with its updated (lower) unmet demand
        # so it can receive another bus in a future iteration if needed.
        unmet_after = max(
            0,
            routes[route]["passengers"]
            - assignments[route] * capacity
        )

        if unmet_after > 0 and cost > 0:
            new_score = unmet_after / cost
            heapq.heappush(heap, (-new_score, route))

    return assignments, decisions, spare_buses
