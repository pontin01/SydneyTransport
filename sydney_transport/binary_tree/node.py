from datetime import timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sydney_transport.search_components import Stop

class Node:
    """
    A Node of the AVL Binary Tree which contains one or more Stops.

    Attributes:
        weight (timedelta): Cumulative travel time from start stop to all Stops
            in this Node. If search_method == "A*", this will be multiplied by
            the heuristic_cost.
        stops (list[Stop]): Stops that are stored in this Node.

        height (int): Maximum number of nodes along the longest path from this Node.
        balance_factor (int):
        left (Node | None):
        right (Node | None):
    """
    def __init__(self, stop, cumulative_travel_time: timedelta):
        self.cumulative_travel_time = cumulative_travel_time
        self.stops: list[Stop] = [stop]

        self.height = 0
        self.balance_factor = 0
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def __repr__(self):
        return self.stops[0].stop_name
