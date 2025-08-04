from datetime import time, timedelta, datetime
import sys
from typing import Optional, TYPE_CHECKING

import sydney_transport.database.stop_db as stop_db

if TYPE_CHECKING:
    from sydney_transport.components.connection import Connection

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
        self.arrival_time: time = self.set_arrival_time(arrival_time)
        self.stop_sequence = stop_sequence
        self.prev_connection: Optional[Connection] = None
        self.cumulative_travel_time: timedelta = timedelta(minutes=0)

    def __repr__(self):
        return self.stop_name

    def __str__(self):
        return self.stop_name

    @staticmethod
    def set_arrival_time(arrival_time) -> Optional[time]:
        if arrival_time is None:
            return None

        if isinstance(arrival_time, time):
            return arrival_time
        elif isinstance(arrival_time, datetime):
            return arrival_time.time()
        elif isinstance(arrival_time, timedelta):
            return (datetime.min + arrival_time).time()

        if not isinstance(arrival_time, time):
            print("Error: stop.py: set_arrival_time()")
            sys.exit(0)

        return arrival_time

    @staticmethod
    def stop_name_to_stop(stop_name: str, db_connection) -> 'Stop':
        """
        Creates a Stop instance based on a stop_name.
        """
        result = stop_db.get_stop_information_from_name(stop_name, db_connection)

        new_stop = Stop(
            stop_id=result[0][0],
            stop_name=stop_name,
            stop_lat=result[0][1],
            stop_lon=result[0][2],
            parent_station=result[0][3],
            trip_id=None,
            arrival_time=None,
            stop_sequence=None
        )
        new_stop.cumulative_travel_time = timedelta(minutes=0)

        return new_stop

    def get_stop_order(self):
        """
        Recursively creates a list of Stops from this Stop till the start_stop.
        """
        if self.prev_connection is None:
            return [self]

        return self.prev_connection.start_stop.get_stop_order() + [self]























