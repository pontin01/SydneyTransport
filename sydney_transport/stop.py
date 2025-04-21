import datetime
from typing import Optional, TYPE_CHECKING

import sydney_transport.database as database

if TYPE_CHECKING:
    from sydney_transport.connection import Connection

class Stop:
    def __init__(self, stop_id, stop_name, stop_lat, stop_lon, parent_station,
                 trip_id, arrival_time, stop_sequence):
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.parent_station = parent_station

        self.trip_id = trip_id
        self.arrival_time: datetime.time = self.set_arrival_time(arrival_time)
        self.stop_sequence = stop_sequence
        self.prev_connection: Optional[Connection] = None

    def __str__(self):
        return f"({self.stop_id = }, {self.stop_name = }, {self.stop_lat = }, {self.stop_lon = }, " \
              f"{self.parent_station = }, {self.trip_id = }, {self.arrival_time = }," \
              f" {self.stop_sequence = })"

    def __repr__(self):
        return f"({self.stop_id = }, {self.stop_name = }, {self.stop_lat = }, {self.stop_lon = }, " \
               f"{self.parent_station = }, {self.trip_id = }, {self.arrival_time = }," \
               f" {self.stop_sequence = })"


    @staticmethod
    def set_arrival_time(arrival_time) -> datetime.time:
        if arrival_time is None:
            return None

        if type(arrival_time) == datetime.time:
            return arrival_time

        return datetime.strptime(arrival_time, "%H:%M").time()

    @staticmethod
    def stop_name_to_stop(stop_name: str, db_username, db_password) -> 'Stop':
        sql = """
            SELECT StopID, StopLat, StopLon, ParentStation
              FROM Stop
             WHERE StopName = %s;
        """
        params = (stop_name,)

        result = database.query(sql, params, db_username, db_password)[0]

        return Stop(
            stop_id=result[0],
            stop_name=stop_name,
            stop_lat=result[1],
            stop_lon=result[2],
            parent_station=result[3],
            trip_id=None,
            arrival_time=None,
            stop_sequence=None
        )






























