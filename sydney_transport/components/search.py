from datetime import timedelta
import pandas
import time
import sys

from sydney_transport.components import SearchState, Stop
import sydney_transport.components.search_utils as su
import sydney_transport.components.stop_creation as sc

from sydney_transport.database import database, stop_db, trip_db

from sydney_transport.map import Map

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
              start_day, start_time, verbose_mode, search_mode, colour_mode):
        """
        Establishes the database connection and retrieves user search settings.
        """
        # establish connection
        self.db_username = db_username
        self.db_password = db_password
        self.db_connection = database.connect(db_username, db_password)

        # search settings
        self.state.start_day = start_day
        self.state.start_time = start_time

        # create start and end stop instances
        self.state.start_stop = su.set_search_stop(start_stop_name, self.db_connection)
        self.state.start_stop.arrival_time = self.state.start_time
        self.state.end_stop = su.set_search_stop(end_stop_name, self.db_connection)

        # A* search information
        self.state.ideal_heuristic_cost = 0

        # modes
        self.state.verbose_mode = verbose_mode
        self.state.search_mode = search_mode
        self.state.colour_mode = colour_mode

    def search(self):
        """
        Continuously searches the closest stop (by travel time) until the end
        stop is reached.
        """
        # time the searching process
        self.timer = time.perf_counter()

        # search start stop
        self._discover_connecting_stops(self.state.start_stop)

        if self.state.verbose_mode:
            print("\n\nSearched Station Order:\n")

        # main search loop
        while self.state.unvisited_stops.root is not None:
            closest_stop = self.state.unvisited_stops.remove_closest_stop()

            if self.state.verbose_mode:
                print(closest_stop.stop_name)

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
        param_parent_station = stop.parent_station or stop.stop_id

        # siblings stops have already been discovered
        if param_parent_station in self.state.parent_station_exclusion_list:
            return

        self.state.parent_station_exclusion_list.append(param_parent_station)

        # get all sibling stops
        result = stop_db.get_sibling_stop_list(param_parent_station, self.db_connection)

        # add all sibling stops to unvisited_stops list
        for record in result:
            # TODO: check why this is here
            # sibling is the same as start_stop
            # if stop_id == self.state.start_stop.stop_id:
            #     arrival_time = stop.arrival_time

            # create and insert sibling stop into avl_tree
            sibling_stop = sc.create_sibling_stop(record, stop)
            self.state.unvisited_stops.insert(sibling_stop, sibling_stop.cumulative_travel_time)

            self.state.add_stop_to_coord_list(sibling_stop, self.timer)

            self.stops_searched += 1

            # final stop encountered
            if record[0] == self.state.end_stop.stop_id:
                self._finish(sibling_stop)

    def _discover_neighbouring_stops(self, stop: Stop):
        """
        Discovers all Stops that can be reached through one Trip, with the ArrivalTime
        of the Trip within the next 10 minutes, limiting results to one stop per Route.
        """
        # stop is the parent station
        if stop.parent_station is None:
            return

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
            sibling_stop_with_trip = sc.create_sibling_stop_with_trip(record, stop)

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
            parent_station = record[4]
            stop_id = record[0]

            # parent stop already explored
            if parent_station in self.state.parent_station_exclusion_list:
                return
            # stop has already been discovered but not searched yet
            if stop_id in self.state.temporary_station_exclusion_list:
                return

            new_stop = sc.create_next_stop_in_trip(record, last_stop)

            # remove stop from being discovered again before it is searched
            self.state.temporary_station_exclusion_list.append(new_stop.stop_id)

            self.state.unvisited_stops.insert(new_stop, new_stop.cumulative_travel_time)

            self.state.add_stop_to_coord_list(new_stop, self.timer)

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
        print("\n\nDone!")

        print(f"\nSearch Time: {total_time}\n")

        print(f"Stops Searched: {self.stops_searched:,} / 161,135\n")

        # print list of stops in order from start to end
        final_stop_order = stop.get_stop_order()
        data = []

        # print stop order for verbose mode
        if self.state.verbose_mode:
            print("\nVerbose Stop Order:\n")

            for temp_stop in final_stop_order:
                item = [temp_stop.stop_id, temp_stop.trip_id, temp_stop.stop_sequence,
                        temp_stop.arrival_time, temp_stop.stop_name]
                data.append(item)

                self.state.end_coord_list.append([temp_stop.stop_lat, temp_stop.stop_lon])

            data_frame = pandas.DataFrame(data, columns=["StopID", "TripID", "Sequence", "ArrivalTime", "Name"])
            print(data_frame)
            print()

        # loop through all stops in final_stop_order
        self._print_route_directions(final_stop_order)

        print(f"{len(self.state.coords_list) = }")
        with open("exploration_route_stops.txt", "w") as f:
            last_timestamp = 0
            for item in self.state.coords_list:
                if item[3] != None:
                    timestamp = item[2] - last_timestamp
                    f.write(f"{item[0]}, {item[1]}, {timestamp}, {item[3]}\n")
                    last_timestamp = item[2]

        with open("optimal_route_stops.txt", "w") as f:
            for item in self.state.end_coord_list:
                f.write(f"{item[0]}, {item[1]}\n")

        map = Map(self.state.colour_mode, self.state.start_stop, self.state.end_stop)
        map.run()

        self.db_connection.close()
        sys.exit(0)

    def _print_route_directions(self, final_stop_order: list):
        current_trip_id = ""
        current_trip_info = ()
        for i in range(len(final_stop_order)):
            current_stop = final_stop_order[i]

            # start stop
            if i == 0:
                arrival_time = su.coloured_text(current_stop.arrival_time, "FFDE21")
                print(f"\n\nStarting from {current_stop.stop_name} at {arrival_time}.\n")
                continue

            # current_stop is sibling without a trip, should be skipped
            if current_stop.stop_sequence is None and current_stop.trip_id is None:
                continue

            # current_stop is the start of a trip
            if current_stop.stop_id == final_stop_order[i - 1].stop_id:
                result = trip_db.get_trip_info_after_search(current_stop.trip_id, self.db_connection)[0]
                route_short_name, route_long_name, route_desc, hex_colour = result

                current_trip_type = su.get_trip_type(route_desc, hex_colour)

                route_short_name, route_long_name = su.clean_route_names(route_short_name,
                                                                         route_long_name,
                                                                         route_desc)

                current_trip_info = (route_short_name, hex_colour)
                current_trip_id = current_stop.trip_id
                arrival_time = su.coloured_text(current_stop.arrival_time, "FFDE21")

                text = f"Go to {current_stop.stop_name} and get on the "
                text += f"{su.coloured_text(route_short_name, hex_colour)} "
                text += f"{current_trip_type} "

                # exclude invalid RouteLongName values for Regional Trains and Coaches Network routes
                if route_long_name is not None:
                    text += f"({route_long_name}) "

                text += f"arriving at {arrival_time}."
                print(text)

                continue

            # current_stop is in a trip, but not the start or end
            if current_stop != final_stop_order[-1]:
                if current_stop.trip_id == current_trip_id and \
                        final_stop_order[i + 1].trip_id == current_trip_id:
                    continue

            # current_stop is the end of a trip (or end stop)
            if current_stop.trip_id is not None:
                is_end_stop = len(final_stop_order) - 1 == i
                is_end_of_trip = False

                if not is_end_stop:
                    if final_stop_order[i + 1].trip_id != current_stop.trip_id:
                        is_end_of_trip = True

                if is_end_stop or is_end_of_trip:
                    arrival_time = su.coloured_text(current_stop.arrival_time, "FFDE21")

                    text = f"The {su.coloured_text(current_trip_info[0], current_trip_info[1])} "
                    text += f"will arrive at {current_stop.stop_name} at {arrival_time}. "
                    text += "Get off here.\n"
                    print(text)

        print("You are now at your destination.\n")