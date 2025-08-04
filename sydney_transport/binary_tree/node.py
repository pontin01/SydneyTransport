from datetime import timedelta
from typing import Optional

from sydney_transport.components.stop import Stop

class Node:
    """
    A Node of the AVL Binary Tree which contains one or more Stops.

    Attributes:
        travel_duration (...): Duration of travel from a searched Stop to some Stops in this Node.
        stops (list[Stop]): Stops that are stored in this Node.

        height (int): Maximum number of nodes along the longest path from this Node.
        balance_factor (int):
        left (Node | None):
        right (Node | None):
    """
    def __init__(self, stop: Stop, travel_duration: timedelta):
        self.travel_duration = travel_duration
        self.stops: list[Stop] = [stop]

        self.height = 0
        self.balance_factor = 0
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def __repr__(self):
        return self.stops[0].stop_name
        # stop_names = ""
        # for stop in self.stops:
        #     stop_names += stop.stop_name + ", "
        # stop_names = stop_names.strip(", ")
        # return f"(stops = {stop_names}, travel_duration = {self.travel_duration})"