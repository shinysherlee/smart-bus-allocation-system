
import unittest

from allocation import allocate_spare_buses
from allocation_heap import allocate_spare_buses_heap


# ---------------------------------------------------------------------------
# Helper: run the same logical test against both algorithm implementations.
# ---------------------------------------------------------------------------

ALGORITHMS = [
    ("greedy", allocate_spare_buses),
    ("heap", allocate_spare_buses_heap),
]


class TestBusAllocation(unittest.TestCase):
    """Tests for the greedy allocation algorithm (allocation.py)."""

    # ------------------------------------------------------------------
    # Requirement 8a: normal allocation — bus goes to highest-priority route
    # ------------------------------------------------------------------

    def test_bus_goes_to_higher_priority_route(self):
        """
        Route A: 60 passengers, cost 100 → unmet = 20, score = 20/100 = 0.2
        Route B: 70 passengers, cost 300 → unmet = 30, score = 30/300 = 0.1
        Route A has a higher score so it should receive the spare bus.
        """
        routes = {
            "Route A": {
                "passengers": 60,
                "assigned_buses": 1,
                "cost_per_bus": 100
            },
            "Route B": {
                "passengers": 70,
                "assigned_buses": 1,
                "cost_per_bus": 300
            }
        }

        assignments, decisions, unused = allocate_spare_buses(
            routes, capacity=40, spare_buses=1
        )

        self.assertEqual(assignments["Route A"], 2)
        self.assertEqual(assignments["Route B"], 1)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(unused, 0)

    # ------------------------------------------------------------------
    # Requirement 8b: no spare buses available
    # ------------------------------------------------------------------

    def test_no_spare_buses(self):
        """
        When spare_buses=0, nothing should change and decisions should be empty.
        """
        routes = {
            "Route A": {
                "passengers": 100,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }

        assignments, decisions, unused = allocate_spare_buses(
            routes, capacity=40, spare_buses=0
        )

        self.assertEqual(assignments["Route A"], 1)
        self.assertEqual(decisions, [])
        self.assertEqual(unused, 0)

    # ------------------------------------------------------------------
    # Requirement 8c: demand already satisfied — no extra bus needed
    # ------------------------------------------------------------------

    def test_no_extra_bus_needed(self):
        """
        30 passengers with capacity=40 → 1 bus is enough.
        The 2 spare buses should all remain unused.
        """
        routes = {
            "Route A": {
                "passengers": 30,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }

        assignments, decisions, unused = allocate_spare_buses(
            routes, capacity=40, spare_buses=2
        )

        self.assertEqual(assignments["Route A"], 1)
        self.assertEqual(decisions, [])
        self.assertEqual(unused, 2)

    # ------------------------------------------------------------------
    # Requirement 8d: multiple spare buses — allocate until demand is met
    # ------------------------------------------------------------------

    def test_unused_buses_remain_when_demand_is_met(self):
        """
        100 passengers, capacity=40, 1 bus already assigned.
        Buses needed = ceil(100/40) = 3, so 2 spare buses are used.
        With 3 spare buses, 1 should remain unused after demand is met.
        """
        routes = {
            "Route A": {
                "passengers": 100,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }

        assignments, decisions, unused = allocate_spare_buses(
            routes, capacity=40, spare_buses=3
        )

        self.assertEqual(assignments["Route A"], 3)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(unused, 1)

    # ------------------------------------------------------------------
    # Requirement 8e: invalid inputs raise errors
    # ------------------------------------------------------------------

    def test_invalid_capacity_zero_raises(self):
        """capacity=0 must raise ValueError."""
        with self.assertRaises(ValueError):
            allocate_spare_buses({}, capacity=0, spare_buses=1)

    def test_invalid_capacity_negative_raises(self):
        """capacity=-1 must raise ValueError."""
        with self.assertRaises(ValueError):
            allocate_spare_buses({}, capacity=-1, spare_buses=1)

    def test_invalid_spare_buses_negative_raises(self):
        """spare_buses=-1 must raise ValueError."""
        routes = {
            "Route A": {
                "passengers": 50,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }
        with self.assertRaises(ValueError):
            allocate_spare_buses(routes, capacity=40, spare_buses=-1)

    # ------------------------------------------------------------------
    # Extra: priority recalculation — multi-bus, multi-route scenario
    # ------------------------------------------------------------------

    def test_priority_recalculates_after_each_bus(self):
        """
        Both routes start with unmet demand.  After Route A gets a bus its
        unmet demand drops, so Route B may become higher priority.
        This verifies the greedy loop re-evaluates scores each iteration.

        Route A: 80 pax, 1 bus, cap 40 → unmet=40, cost=100, score=0.40
        Route B: 50 pax, 0 bus, cap 40 → unmet=50, cost=200, score=0.25

        Iteration 1: A wins (0.40 > 0.25) → A gets bus 2,
                     A's new unmet = max(0, 80 - 2*40) = 0
        Iteration 2: only B has unmet (50), so B gets a bus.
        """
        routes = {
            "Route A": {
                "passengers": 80,
                "assigned_buses": 1,
                "cost_per_bus": 100
            },
            "Route B": {
                "passengers": 50,
                "assigned_buses": 0,
                "cost_per_bus": 200
            }
        }

        assignments, decisions, unused = allocate_spare_buses(
            routes, capacity=40, spare_buses=2
        )

        self.assertEqual(decisions[0]["route"], "Route A")
        self.assertEqual(decisions[1]["route"], "Route B")
        self.assertEqual(assignments["Route A"], 2)
        self.assertEqual(assignments["Route B"], 1)
        self.assertEqual(unused, 0)


# ---------------------------------------------------------------------------
# Heap algorithm tests — mirror every test above for allocation_heap.py
# ---------------------------------------------------------------------------

class TestBusAllocationHeap(unittest.TestCase):
    """Tests for the heap-based allocation algorithm (allocation_heap.py)."""

    def test_bus_goes_to_higher_priority_route_heap(self):
        routes = {
            "Route A": {
                "passengers": 60,
                "assigned_buses": 1,
                "cost_per_bus": 100
            },
            "Route B": {
                "passengers": 70,
                "assigned_buses": 1,
                "cost_per_bus": 300
            }
        }

        assignments, decisions, unused = allocate_spare_buses_heap(
            routes, capacity=40, spare_buses=1
        )

        self.assertEqual(assignments["Route A"], 2)
        self.assertEqual(assignments["Route B"], 1)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(unused, 0)

    def test_no_spare_buses_heap(self):
        routes = {
            "Route A": {
                "passengers": 100,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }

        assignments, decisions, unused = allocate_spare_buses_heap(
            routes, capacity=40, spare_buses=0
        )

        self.assertEqual(assignments["Route A"], 1)
        self.assertEqual(decisions, [])
        self.assertEqual(unused, 0)

    def test_no_extra_bus_needed_heap(self):
        routes = {
            "Route A": {
                "passengers": 30,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }

        assignments, decisions, unused = allocate_spare_buses_heap(
            routes, capacity=40, spare_buses=2
        )

        self.assertEqual(assignments["Route A"], 1)
        self.assertEqual(decisions, [])
        self.assertEqual(unused, 2)

    def test_unused_buses_remain_when_demand_is_met_heap(self):
        routes = {
            "Route A": {
                "passengers": 100,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }

        assignments, decisions, unused = allocate_spare_buses_heap(
            routes, capacity=40, spare_buses=3
        )

        self.assertEqual(assignments["Route A"], 3)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(unused, 1)

    def test_invalid_capacity_zero_raises_heap(self):
        with self.assertRaises(ValueError):
            allocate_spare_buses_heap({}, capacity=0, spare_buses=1)

    def test_invalid_capacity_negative_raises_heap(self):
        with self.assertRaises(ValueError):
            allocate_spare_buses_heap({}, capacity=-1, spare_buses=1)

    def test_invalid_spare_buses_negative_raises_heap(self):
        routes = {
            "Route A": {
                "passengers": 50,
                "assigned_buses": 1,
                "cost_per_bus": 100
            }
        }
        with self.assertRaises(ValueError):
            allocate_spare_buses_heap(routes, capacity=40, spare_buses=-1)

    def test_priority_recalculates_after_each_bus_heap(self):
        """
        Same scenario as the greedy version: confirms the heap re-pushes
        updated scores and picks the currently highest-priority route each time.
        """
        routes = {
            "Route A": {
                "passengers": 80,
                "assigned_buses": 1,
                "cost_per_bus": 100
            },
            "Route B": {
                "passengers": 50,
                "assigned_buses": 0,
                "cost_per_bus": 200
            }
        }

        assignments, decisions, unused = allocate_spare_buses_heap(
            routes, capacity=40, spare_buses=2
        )

        self.assertEqual(decisions[0]["route"], "Route A")
        self.assertEqual(decisions[1]["route"], "Route B")
        self.assertEqual(assignments["Route A"], 2)
        self.assertEqual(assignments["Route B"], 1)
        self.assertEqual(unused, 0)


if __name__ == "__main__":
    unittest.main()
