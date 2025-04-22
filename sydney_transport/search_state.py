from typing import Optional
from datetime import timedelta

from sydney_transport.stop import Stop
from sydney_transport.connection import Connection

class SearchState:
    def __init__(self):
        self.connections = []
        self.unvisited_stops = []

        self.start_stop: Optional[Stop] = None
        self.end_stop: Optional[Stop] = None

        self.start_day = ""
        self.start_time = None

    def add_unvisited_stop(self, stop: Stop):
        self.unvisited_stops.append(stop)

    def add_connection(self, start_stop: Stop, end_stop: Stop) -> Connection:
        connection = Connection(start_stop, end_stop)
        self.connections.append(connection)
        return connection

    def find_next_closest_stop(self):
        closest_stop = None
        closest_stop_length = timedelta(days=99)

        for stop in self.unvisited_stops:
            stop_length = stop.prev_connection.get_cumulative_weight()

            if stop_length < closest_stop_length:
                closest_stop = stop
                closest_stop_length = stop_length

        return closest_stop

