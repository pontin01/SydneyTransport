from typing import Optional

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
