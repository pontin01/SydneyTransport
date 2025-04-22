import sys
from datetime import datetime, timedelta
import time
import pandas as pd

from sydney_transport import database
from sydney_transport.search_state import SearchState
from sydney_transport.stop import Stop


def get_start_day():
    while True:
        desired_day = input("Start Day: ")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                "sunday"]
        if desired_day.lower() not in days:
            print("Enter a valid day of the week.")
            continue
        break

    return desired_day


def get_start_time():
    start_time = input("Start Time: ")
    return datetime.strptime(start_time, "%H:%M").time()


def add_time(time: datetime.time, difference: timedelta):
    datetime_object = datetime.combine(datetime.today(), time)
    new_datetime = datetime_object + difference
    return new_datetime.time()


class App:
    def __init__(self):
        self.db_username = ""
        self.db_password = ""

        self.state = SearchState()
        self.db_connection = None
        self.timer = None

    def setup(self):
        try:
            # get database information
            self.db_username = input("Database Username: ")
            self.db_password = input("Database Password: ")

            # get search settings
            start_stop_name = input("Start Stop Name: ")
            end_stop_name = input("End Stop Name: ")
            self.state.start_day = get_start_day()
            self.state.start_time = get_start_time()
        except EOFError:
            print("Exiting!")
            sys.exit(0)

        self.db_connection = database.connect(self.db_username, self.db_password)

        # create start and end stop instances
        self.state.start_stop = Stop.stop_name_to_stop(start_stop_name,
                                                       self.db_connection)
        self.state.start_stop.arrival_time = self.state.start_time
        self.state.end_stop = Stop.stop_name_to_stop(end_stop_name,
                                                     self.db_connection)


    def search(self):
        self.timer = time.perf_counter()

        self.discover_connecting_stops(self.state.start_stop)

        while self.state.unvisited_stops.root is not None:
            closest_stop = self.state.unvisited_stops.get_shortest_stop()
            self.discover_connecting_stops(closest_stop)

        if self.state.unvisited_stops.root is None:
            print("Done! (search)")
            sys.exit(0)

    def discover_connecting_stops(self, stop: Stop):
        self.discover_sibling_stops(stop)
        self.discover_neighbouring_stops(stop)


    def discover_sibling_stops(self, stop: Stop):
        sql = """
            SELECT StopID, StopName, StopLat, StopLon, ParentStation
              FROM Stop
             WHERE ParentStation = %s
                   AND LocationType IS NULL;
        """
        param_parent_station = stop.parent_station
        # stop is the parent station
        if stop.parent_station is None:
            param_parent_station = stop.stop_id
        # siblings have already been discovered
        if param_parent_station in self.state.parent_station_exclusion_list:
            return
        else:
            self.state.parent_station_exclusion_list.append(param_parent_station)

        params = (param_parent_station,)

        result = database.query(sql, params, self.db_connection)

        for record in result:
            stop_id = record[0]
            arrival_time = add_time(stop.arrival_time, timedelta(minutes=1))

            # sibling is the same as start_stop
            if stop_id == self.state.start_stop.stop_id:
                arrival_time = stop.arrival_time

            sibling_stop = Stop(
                stop_id=stop_id,
                stop_name=record[1],
                stop_lat=record[2],
                stop_lon=record[3],
                parent_station=record[4],
                trip_id=None,
                arrival_time=arrival_time,
                stop_sequence=None
            )
            connection = self.state.add_connection(stop, sibling_stop)
            sibling_stop.prev_connection = connection
            sibling_stop.cumulative_travel_time = stop.cumulative_travel_time + timedelta(minutes=1)
            self.state.add_unvisited_stop(sibling_stop)

            # final stop encountered
            if stop_id == self.state.end_stop.stop_id:
                self.finish(sibling_stop)


    def discover_neighbouring_stops(self, stop: Stop):
        # stop is the parent station
        if stop.parent_station is None:
            return

        sibling_stops_with_trips = self.discover_trips_from_stop(stop)
        for temp_stop in sibling_stops_with_trips:
            self.discover_next_stop_in_trip(temp_stop)


    def discover_trips_from_stop(self, stop: Stop):
        sql = f"""
            WITH RankedDepartures AS (
	            SELECT ST.StopID, T.DirectionID, T.TripID, ST.StopSequence,
                       ST.ArrivalTime, R.RouteID,
		               ROW_NUMBER() OVER (
		   		           PARTITION BY ST.StopID, T.DirectionID, R.RouteID
		   		           ORDER BY ST.ArrivalTime ASC
		               ) AS RowNumber
	              FROM StopTime ST
	                   INNER JOIN Trip T ON ST.TripID = T.TripID
   	                   INNER JOIN Route R ON T.RouteID = R.RouteID
	                   INNER JOIN Service S ON T.ServiceID = S.ServiceID
	             WHERE ST.StopID = %s
                       AND ST.ArrivalTime > %s
                       AND S.{self.state.start_day} = 1
            )
              SELECT TripID, ArrivalTime, StopSequence
                FROM RankedDepartures
               WHERE RowNumber = 1
                     AND ArrivalTime <= ADDTIME(%s, "00:10:00")
            ORDER BY ArrivalTime ASC;
        """
        params = (stop.stop_id, stop.arrival_time, stop.arrival_time)

        result = database.query(sql, params, self.db_connection)

        sibling_stops_with_trips = []

        for record in result:
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
            connection = self.state.add_connection(stop, sibling_stop_with_trip)
            sibling_stop_with_trip.prev_connection = connection
            sibling_stop_with_trip.cumulative_travel_time = stop.cumulative_travel_time + \
                sibling_stop_with_trip.prev_connection.calculate_travel_time()
            sibling_stops_with_trips.append(sibling_stop_with_trip)

            # final stop encountered
            if stop.stop_id == self.state.end_stop.stop_id:
                self.finish(stop)

        return sibling_stops_with_trips

    def discover_next_stop_in_trip(self, stop: Stop):
        sql = """
            SELECT StopID, StopName, StopLat, StopLon, ParentStation,
                   ArrivalTime, StopSequence
              FROM StopInformation
             WHERE TripID = %s
                   AND StopSequence = %s + 1;
        """
        params = (stop.trip_id, stop.stop_sequence)

        result = database.query(sql, params, self.db_connection)

        # current stop is last stop
        if result == [] or result is None:
            return
        else:
            result = result[0]

        new_stop = Stop(
            stop_id=result[0],
            stop_name=result[1],
            stop_lat=result[2],
            stop_lon=result[3],
            parent_station=result[4],
            trip_id=stop.trip_id,
            arrival_time=result[5],
            stop_sequence=result[6]
        )
        connection = self.state.add_connection(stop, new_stop)
        new_stop.prev_connection = connection
        new_stop.cumulative_travel_time = stop.cumulative_travel_time + \
            new_stop.prev_connection.calculate_travel_time()
        self.state.add_unvisited_stop(new_stop)

        # final stop encountered
        if new_stop.stop_id == self.state.end_stop.stop_id:
            self.finish(new_stop)

    def finish(self, stop: Stop):
        end_time = time.perf_counter()
        total_time = end_time - self.timer
        print("Done!")
        print(f"{total_time = }\n")

        final_stop_order = stop.get_stop_order()
        data = []
        for temp_stop in final_stop_order:
            item = [temp_stop.stop_id, temp_stop.stop_sequence,
                    temp_stop.arrival_time, temp_stop.stop_name]
            data.append(item)

        data_frame = pd.DataFrame(data, columns=["ID", "Sequence", "ArrivalTime", "Name"])
        print(data_frame)

        self.db_connection.close()
        sys.exit(0)




















