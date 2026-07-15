import datetime as dt
import sys
from typing import Optional, TYPE_CHECKING

from sydney_transport.database import stop_db

if TYPE_CHECKING:
    from sydney_transport.components import Connection

class Stop:
    """
    Represents one Stop within the search.

    Attributes:
        stop_id (str): ID of the Stop.
        stop_name (str): Name of the Stop.
        stop_lat (float): Latitude of the Stop.
        stop_lon (float): Longitude of the Stop.
        parent_station (str): StopID of the parent Stop.

        trip_id (str): ID of the Trip the Stop is a part of.
        arrival_time (time): Time the Trip reaches the Stop.
        stop_sequence (int): The position number of the Stop.
        prev_connection (Connection): The Connection to the previous Stop.
        cumulative_travel_time (Connection): Travel time from start_stop to this Stop.
    """
    def __init__(self, stop_id, stop_name, stop_lat, stop_lon, parent_station,
                 trip_id, arrival_time, stop_sequence):
        # basic stop information
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.parent_station = parent_station

        # other information
        self.trip_id = trip_id
        self.arrival_time: dt.time = arrival_time
        self.stop_sequence = stop_sequence
        self.prev_connection: Optional[Connection] = None
        self.cumulative_travel_time: dt.timedelta = dt.timedelta(minutes=0)

    @property
    def arrival_time(self) -> dt.time:
        return self.arrival_time

    @property.setter
    def arrival_time(self, arrival_time):
        if not isinstance(arrival_time, dt.time):
            print("Error: stop.py: set_arrival_time()")
            sys.exit(0)

        if isinstance(arrival_time, dt.time):
            self.arrival_time = arrival_time
        elif isinstance(arrival_time, dt.datetime):
            self.arrival_time = arrival_time.time()
        elif isinstance(arrival_time, dt.timedelta):
            self.arrival_time = (dt.datetime.min + arrival_time).time()