from datetime import datetime, timedelta, time
import pandas
import sys
import time

from sydney_transport.components.search_state import SearchState
from sydney_transport.components.stop import Stop
from sydney_transport.components.connection import Connection

from sydney_transport.database import database
from sydney_transport.database import stop_db

class Search:
    """
    Represents a search from a start Stop to an End stop.

    Attributes:
        db_username (str): Username for the Database.
        db_password (str): Password for the Database.
        state (SearchState): Information about the current state of the search.
        db_connection (MySQLConnectionAbstract):
        timer (float):
        stops_searched (int):
    """
    def __init__(self):
        self.db_username = ""
        self.db_password = ""

        self.state: SearchState = SearchState()
        self.db_connection = None

        self.timer = None
        self.stops_searched = 0

    def setup(self, db_username, db_password, start_stop_name, end_stop_name,
              start_day, start_time):
        """
        Establishes the database connection and retrieves user search settings.
        """
        # establish connection
        self.db_username = db_username
        self.db_password = db_password
        self.db_connection = database.connect(db_username, db_password)

        self.state.start_day = start_day
        self.state.start_time = start_time

        # create start and end stop instances
        self.state.start_stop = Stop.stop_name_to_stop(start_stop_name,
                                                       self.db_connection)
        self.state.start_stop.arrival_time = self.state.start_time
        self.state.end_stop = Stop.stop_name_to_stop(end_stop_name,
                                                     self.db_connection)

    def search(self):
        """
        Continuously searches the closest stop (by travel time) until the end
        stop is reached.
        """
        # time the searching process
        self.timer = time.perf_counter()

        # search start stop
        self._discover_connecting_stops(self.state.start_stop)

        # loop through searching stops till end stop is reached
        while self.state.unvisited_stops.root is not None:
            closest_stop = self.state.unvisited_stops.remove_closest_stop()

            print(closest_stop.stop_name)

            # TODO: check why this is here
            if closest_stop is None:
                continue

            self._discover_connecting_stops(closest_stop)

        # search finished; unvisited_stops is empty
        if self.state.unvisited_stops.root is None:
            print("Done!")
            print("search.py: search() failed, unvisited_stops is empty")
            sys.exit(0)

    def _discover_connecting_stops(self, stop: Stop):
        """
        Retrieves all types of connected stops.
        :param stop: Stop to be searched.
        """
        # remove from temporary exclusion list
        if stop.stop_id in self.state.temporary_station_exclusion_list:
            self.state.temporary_station_exclusion_list.remove(stop.stop_id)

        self._discover_sibling_stops(stop)
        self._discover_neighbouring_stops(stop)

    def _discover_sibling_stops(self, stop: Stop):
        """
        Retrieves all stops that are within the same station, i.e. have the same
        ParentStationID.
        :param stop: Stop to be searched.
        """
        SIBLING_TRAVEL_DURATION = timedelta(minutes=1)

        param_parent_station = stop.parent_station or stop.stop_id

        # siblings stops have already been discovered
        if param_parent_station in self.state.parent_station_exclusion_list:
            return

        self.state.parent_station_exclusion_list.append(param_parent_station)

        # get all sibling stops
        result = stop_db.get_sibling_stop_list(param_parent_station, self.db_connection)

        # add all sibling stops to unvisited_stops list
        for record in result:
            stop_id = record[0]
            arrival_time = self._add_time(stop.arrival_time, SIBLING_TRAVEL_DURATION)

            # TODO: not sure why this is here
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
            sibling_stop.prev_connection = Connection(stop, sibling_stop)
            sibling_stop.cumulative_travel_time = stop.cumulative_travel_time + SIBLING_TRAVEL_DURATION
            self.state.unvisited_stops.insert(sibling_stop, sibling_stop.cumulative_travel_time)

            self.stops_searched += 1

            # final stop encountered
            if stop_id == self.state.end_stop.stop_id:
                self._finish(sibling_stop)

    @staticmethod
    def _add_time(arrival_time: time, difference: timedelta) -> time:
        datetime_object = datetime.combine(datetime.today(), arrival_time)
        new_datetime = datetime_object + difference
        return new_datetime.time()

    def _discover_neighbouring_stops(self, stop: Stop):
        """
        Discovers all Stops that can be reached through one Trip, with the ArrivalTime
        of the Trip within the next 10 minutes, limiting results to one stop per Route.
        """
        # stop is the parent station
        if stop.parent_station is None:
            return

        # TODO: check why name is sibling_stops_with_trips
        sibling_stops_with_trips = self._discover_trips_from_stop(stop)
        for connecting_stop in sibling_stops_with_trips:
            self._discover_next_stop_in_trip(connecting_stop)

    def _discover_trips_from_stop(self, stop: Stop) -> list:
        """
        Discovers the Trips that are associated with a Stop.
        :return: A list of sibling stops which have a trip.
        """
        result = stop_db.get_trips_from_stop(stop.stop_id, stop.arrival_time,
                                             self.state.start_day, self.db_connection)

        # create list of sibling stops of the stop being searched that have a trip
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

            sibling_stop_with_trip.prev_connection = Connection(stop, sibling_stop_with_trip)
            sibling_stop_with_trip.cumulative_travel_time = stop.cumulative_travel_time + \
                sibling_stop_with_trip.prev_connection.calculate_travel_time()

            sibling_stops_with_trips.append(sibling_stop_with_trip)

            # final stop encountered
            if stop.stop_id == self.state.end_stop.stop_id:
                self._finish(stop)

        return sibling_stops_with_trips

    def _discover_next_stop_in_trip(self, stop: Stop):
        """
        Discovers the next Stop within a Trip.
        """
        result = stop_db.get_all_following_stops_in_trip(stop.trip_id, stop.stop_sequence,
                                                         self.db_connection)

        # current stop is last stop
        if not result:
            return

        last_stop: Stop = stop

        # add all upcoming stops in trip
        for record in result:
            new_stop = Stop(
                stop_id=record[0],
                stop_name=record[1],
                stop_lat=record[2],
                stop_lon=record[3],
                parent_station=record[4],
                trip_id=stop.trip_id,
                arrival_time=record[5],
                stop_sequence=record[6]
            )

            # parent stop already explored
            if new_stop.parent_station in self.state.parent_station_exclusion_list:
                return

            # stop has already been discovered but not searched yet
            if new_stop.stop_id in self.state.temporary_station_exclusion_list:
                return

            # remove stop from being discovered again before it is searched
            self.state.temporary_station_exclusion_list.append(new_stop.stop_id)

            new_stop.prev_connection = Connection(last_stop, new_stop)
            new_stop.cumulative_travel_time = last_stop.cumulative_travel_time + \
                new_stop.prev_connection.calculate_travel_time()
            self.state.unvisited_stops.insert(new_stop, new_stop.cumulative_travel_time)

            self.stops_searched += 1

            # final stop encountered
            if new_stop.stop_id == self.state.end_stop.stop_id:
                self._finish(new_stop)

            last_stop = new_stop

    def _finish(self, stop: Stop):
        """
        Completes all finishing procedures when the last stop is discovered.
        Prints the time to complete the search and the inorder list of stops from
        the start to the end.
        :param stop: Last stop discovered, is the same as the end_stop.
        """
        total_time = time.perf_counter() - self.timer
        print("Done!")
        print(f"{total_time = }\n")

        # print list of stops in order from start to end
        final_stop_order = stop.get_stop_order()
        data = []
        for temp_stop in final_stop_order:
            item = [temp_stop.stop_id, temp_stop.stop_sequence,
                    temp_stop.arrival_time, temp_stop.stop_name]
            data.append(item)

        data_frame = pandas.DataFrame(data, columns=["ID", "Sequence", "ArrivalTime", "Name"])
        print(data_frame)

        self.db_connection.close()
        sys.exit(0)



























