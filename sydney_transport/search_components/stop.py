import datetime as dt
import sys
from typing import Optional, TYPE_CHECKING

from sydney_transport.database import stop_db
from sydney_transport.search_components.search_utils import add_time

if TYPE_CHECKING:
    from sydney_transport.search_components import Connection

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
                 trip_id=None, arrival_time=None, stop_sequence=None):
        # basic stop information
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.parent_station = parent_station

        # other information
        self.trip_id = trip_id
        self.arrival_time: dt.time = self.set_arrival_time(arrival_time)
        self.stop_sequence = stop_sequence
        self.prev_connection: Optional[Connection] = None
        self.cumulative_travel_time: dt.timedelta = dt.timedelta(minutes=0)

    def __repr__(self):
        return self.stop_name

    def __str__(self):
        return self.stop_name

    def get_stop_order(self):
        """
        Recursively creates a list of Stops from this Stop till the start_stop.
        """
        if self.prev_connection is None:
            return [self]

        return self.prev_connection.start_stop.get_stop_order() + [self]

    @staticmethod
    def set_arrival_time(arrival_time) -> Optional[dt.time]:
        if arrival_time is None:
            return None

        if isinstance(arrival_time, dt.time):
            return arrival_time
        elif isinstance(arrival_time, dt.datetime):
            return arrival_time.time()
        elif isinstance(arrival_time, dt.timedelta):
            return (dt.datetime.min + arrival_time).time()

        if not isinstance(arrival_time, dt.time):
            print("Error: stop.py: set_arrival_time()")
            sys.exit(0)

        return arrival_time

    @staticmethod
    def stop_name_to_stop(stop_name: str, db_connection):
        """
        Creates a Stop instance based on a stop_name.
        """
        result = stop_db.get_stop_information_from_name(stop_name, db_connection)

        if not result:
            return None

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
        new_stop.cumulative_travel_time = dt.timedelta(minutes=0)

        return new_stop

    @staticmethod
    def create_sibling_stop(record: tuple, stop: Stop) -> Stop:
        """
        Creates a sibling stop for the given Stop.
        """
        sibling_travel_duration = dt.timedelta(minutes=1)
        arrival_time = add_time(stop.arrival_time, sibling_travel_duration)

        # stop creation
        sibling_stop = Stop(
            stop_id=record[0],
            stop_name=record[1],
            stop_lat=record[2],
            stop_lon=record[3],
            parent_station=record[4],
            trip_id=None,
            arrival_time=arrival_time,
            stop_sequence=None
        )
        sibling_stop.cumulative_travel_time = stop.cumulative_travel_time + sibling_travel_duration

        # create connection
        sibling_stop.prev_connection = Connection(stop, sibling_stop)

        return sibling_stop

    @staticmethod
    def create_sibling_stop_with_trip(record: tuple, stop: Stop) -> Stop:
        # stop creation
        sibling_stop_with_trip = Stop(
            stop_id=stop.stop_id,
            stop_name=stop.stop_name,
            stop_lat=stop.stop_lat,
            stop_lon=stop.stop_lon,
            parent_station=stop.parent_station,
            trip_id=record[0],
            arrival_time=record[1],
            stop_sequence=record[2]
        )

        # create connection and calculate cumulative travel time
        sibling_stop_with_trip.prev_connection = Connection(stop, sibling_stop_with_trip)
        sibling_stop_with_trip.cumulative_travel_time = stop.cumulative_travel_time + \
                                                        sibling_stop_with_trip.prev_connection.calculate_travel_time()

        return sibling_stop_with_trip

    @staticmethod
    def create_next_stop_in_trip(record: tuple, last_stop: Stop) -> Stop:
        # stop creation
        new_stop = Stop(
            stop_id=record[0],
            stop_name=record[1],
            stop_lat=record[2],
            stop_lon=record[3],
            parent_station=record[4],
            trip_id=last_stop.trip_id,
            arrival_time=record[5],
            stop_sequence=record[6]
        )

        # create connection
        new_stop.prev_connection = Connection(last_stop, new_stop)
        new_stop.cumulative_travel_time = last_stop.cumulative_travel_time + \
                                          new_stop.prev_connection.calculate_travel_time()

        return new_stop