from sydney_transport.stop import Stop
from typing import Optional

class Node:
    def __init__(self, stops, travel_time):
        self.travel_time = travel_time
        self.stops: list[Stop] = [stops]

        self.height = 0
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def __repr__(self):
        stop_names = ""
        for stop in self.stops:
            stop_names += stop.stop_name + ", "
        stop_names = stop_names.strip(", ")
        return f"(stops = {stop_names}, travel_time = {self.travel_time})"