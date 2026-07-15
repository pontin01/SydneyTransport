import sys
import time
from smtplib import SMTP

from sydney_transport.database import database, stop_db
from sydney_transport.search_components import SearchState, Stop, stop_creation, search_utils


class Search:
    """
    A Singleton class that represents a search from a start Stop to an End stop.

    Attributes:
        db_username (str): Username for the Database.
        db_password (str): Password for the Database.
        state (SearchState): Information about the current state of the search.
        db_connection (MySQLConnectionAbstract):
        timer (float):
        stops_searched (int):
    """
    _instance = None
    _db_conn: SMTP = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Search, cls).__new__(cls)
        return cls._instance

    def __init__(self, user_settings=None, search_settings=None):
        if getattr(self, "_initialised", False):
            return
        if not user_settings or search_settings:
            return

        self._initialised = True

        # usre settings
        self._db_username = user_settings["db_username"]
        self._db_password = user_settings["db_password"]

        self._db_conn = database.connect(self._db_username, self._db_password)
        self._state: SearchState = SearchState(search_settings)

        self._timer = None

    @property
    def db_conn(self) -> SMTP:
        assert self._db_conn
        return self._db_conn

    def search(self):
        """
        Continuously searches the closest stop (by travel time) until the end
        stop is reached.
        """
        # time the searching process
        self._timer = time.perf_counter()

        # search start stop
        self._discover_connecting_stops(self._state.start_stop)

        if self._state.verbose_mode: print("\n\nSearched Station Order:\n")

        # main search loop
        while not self._state.unvisited_stop_tree.is_empty():
            closest_stop: Stop = self._state.unvisited_stop_tree.pop_closest_stop()

            if self._state.verbose_mode:
                print(closest_stop.stop_name)

            if closest_stop is None:
                continue

            self._discover_connecting_stops(closest_stop)

        # search finished; unvisited_stop_tree is empty
        if self._state.unvisited_stop_tree.is_empty():
            print("Done!")
            print("search.py: search() failed, unvisited_stops is empty")
            sys.exit(0)

    def _discover_connecting_stops(self, stop: Stop) -> None:
        """
        Retrieves all types of connected stops.
        :param stop: Stop to be searched.
        """
        self._state.remove_temp_excluded_station(stop)

        self._discover_sibling_stops(stop)
        self._discover_neighbouring_stops(stop)

    def _discover_sibling_stops(self, stop: Stop) -> None:
        """
        Retrieves all stops that are within the same station, i.e. have the same
        ParentStationID.
        :param stop: Stop to be searched.
        """
        param_parent_station = stop.parent_station or stop.stop_id

        # siblings have already been discovered
        if self._state.stop_is_excluded_parent_station(param_parent_station):
            return

        self._state.add_excluded_parent_station(param_parent_station)

        # sibling stops
        result = stop_db.get_sibling_stop_list(param_parent_station, self.db_conn)

        # add all sibling stops to unvisited_stop_tree
        for record in result:
            # TODO: check why this is here
            # sibling is the same as start_stop
            # if stop_id == self.state.start_stop.stop_id:
            #     arrival_time = stop.arrival_time

            # create and insert sibling stop into unvisited_stop_tree
            sibling_stop = Stop.create_sibling_stop(record, stop)
            self._state.unvisited_stop_tree.insert(sibling_stop, sibling_stop)

            self._state.add_stop_to_coord_list(sibling_stop, self._timer)

            self._state.increment_stops_searched()

            # final stop encountered
            if self._state.is_final_stop(sibling_stop.stop_id):
                self._finish(sibling_stop)

    def _discover_neighbouring_stops(self, stop: Stop) -> None:
        """
        Discovers all Stops that can be reached through one Trip, with the ArrivalTime
        of the Trip within the next 10 minutes, limiting results to one stop per Route.
        """
        # stop is the parent station
        if stop.parent_station is None:
            return

        sibling_stops_with_trips = self._discover_trips_from_stops(stop)
        for connecting_stop in sibling_stops_with_trips:
            self._discover_next_stop_in_trip(connecting_stop)

    def _discover_trips_from_stop(self, stop: Stop) -> list:
        """
        Discovers the Trips that are associated with a Stop.
        :return: A list of sibling stops which have a trip.
        """
        result = stop_db.get_trips_from_stop(stop.stop_id, stop.arrival_time,
                                             self._state.start_day, self.db_conn)

        # create list of sibling stops of the stop being searched that have a trip
        sibling_stops_with_trips = []
        for record in result:
            sibling_stop_with_trip = Stop.create_sibling_stop_with_trip(record, stop)
            sibling_stops_with_trips.append(sibling_stop_with_trip)

            if self._state.is_final_stop(stop.stop_id):
                self._finish(stop)

        return sibling_stops_with_trips

    def _discover_next_stop_in_trip(self, stop: Stop) -> None:
        """
        Discovers the next Stop within a Trip.
        """
        result = stop_db.get_all_following_stops_in_trip(stop.trip_id, stop.stop_sequence, self.db_conn)

        # current stop is last stop
        if not result:
            return

        # add all upcoming stops in trip
        last_stop: Stop = stop
        for record in result:
            parent_station = record[4]
            stop_id = record[0]

            # parent stop already explored
            if self._state.stop_is_excluded_parent_station(parent_station):
                return
            # stop has already been discovered but not searched yet
            if self._state.stop_is_temp_excluded_station(stop_id):
                return

            new_stop = Stop.create_next_stop_in_trip(record, last_stop)

            # remove stop from being discovered again before it is searched
            self._state.add_temp_excluded_station(new_stop.stop_id)
            self._state.unvisited_stop_tree.insert(new_stop)
            self._state.add_stop_to_coord_list(new_stop, self._timer)
            self._state.increment_stops_searched()

            if self._state.is_final_stop(stop_id):
                self._finish(new_stop)

            last_stop = new_stop

    def _finish(self, stop: Stop) -> None:
        """
        Completes all finishing procedures when the last stop is discovered.
        Prints the time to complete the search and the inorder list of stops from
        the start to the end.
        :param stop: Last stop discovered, is the same as the end_stop.
        """
        total_time = time.perf_counter() - self._timer

        print("\n\nDone!")
        print(f"\nSearch Time: {total_time}\n")
        print(f"Stops Searched: {self._state.stops_searched:,} / 161,135\n")

        final_stop_order = stop.get_stop_order()

        if self._state.verbose_mode:
            search_utils.print_stop_order(final_stop_order)