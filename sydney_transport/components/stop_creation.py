from datetime import timedelta

from sydney_transport.components import Stop, Connection
from sydney_transport.database import stop_db
from sydney_transport.components.search_utils import *


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
    new_stop.cumulative_travel_time = timedelta(minutes=0)

    return new_stop

def create_sibling_stop(record: tuple, stop: Stop) -> Stop:
    sibling_travel_duration = timedelta(minutes=1)
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
