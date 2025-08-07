from datetime import datetime, timedelta, time
import pandas
import sys
import time

from sydney_transport.components.search_state import SearchState
from sydney_transport.components.stop import Stop
from sydney_transport.components.connection import Connection

from sydney_transport.database import database
from sydney_transport.database import stop_db
from sydney_transport.database import trip_db

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
              start_day, start_time, verbose_mode):
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
        self.state.start_stop = Stop.stop_name_to_stop(start_stop_name,
                                                       self.db_connection)
        self.state.start_stop.arrival_time = self.state.start_time
        self.state.end_stop = Stop.stop_name_to_stop(end_stop_name,
                                                     self.db_connection)

        # other settings
        if verbose_mode:
            self.state.verbose_mode = True

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

        # loop through searching stops till end stop is reached
        while self.state.unvisited_stops.root is not None:
            closest_stop = self.state.unvisited_stops.remove_closest_stop()

            if self.state.verbose_mode:
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

            data_frame = pandas.DataFrame(data, columns=["StopID", "TripID", "Sequence", "ArrivalTime", "Name"])
            print(data_frame)
            print()

        # loop through all stops in final_stop_order
        current_trip_id = ""
        current_trip_info = ()
        for i in range(len(final_stop_order)):
            current_stop = final_stop_order[i]

            # start stop
            if i == 0:
                arrival_time = self._coloured_text(current_stop.arrival_time, "FFDE21")
                print(f"\n\nStarting from {current_stop.stop_name} at {arrival_time}.\n")
                continue

            # current_stop is sibling without a trip, should be skipped
            if current_stop.stop_sequence is None and current_stop.trip_id is None:
                continue

            # current_stop is the start of a trip
            if current_stop.stop_id == final_stop_order[i-1].stop_id:
                result = trip_db.get_trip_info_after_search(current_stop.trip_id, self.db_connection)[0]
                route_short_name, route_long_name, route_desc, hex_colour = result

                current_trip_type = self._get_trip_type(route_desc, hex_colour)

                route_short_name, route_long_name = self._clean_route_names(route_short_name,
                                                                            route_long_name,
                                                                            route_desc)

                current_trip_info = (route_short_name, hex_colour)
                current_trip_id = current_stop.trip_id
                arrival_time = self._coloured_text(current_stop.arrival_time, "FFDE21")

                text = f"Go to {current_stop.stop_name} and get on the "
                text += f"{self._coloured_text(route_short_name, hex_colour)} "
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
                        final_stop_order[i+1].trip_id == current_trip_id:
                    continue

            # current_stop is the end of a trip (or end stop)
            if current_stop.trip_id is not None:
                is_end_stop = len(final_stop_order) - 1 == i
                is_end_of_trip = False

                if not is_end_stop:
                    if final_stop_order[i+1].trip_id != current_stop.trip_id:
                        is_end_of_trip = True

                if is_end_stop or is_end_of_trip:
                    arrival_time = self._coloured_text(current_stop.arrival_time, "FFDE21")

                    text = f"The {self._coloured_text(current_trip_info[0], current_trip_info[1])} "
                    text += f"will arrive at {current_stop.stop_name} at {arrival_time}. "
                    text += "Get off here.\n"
                    print(text)

        print("You are now at your destination.\n")

        self.db_connection.close()
        sys.exit(0)

    @staticmethod
    def _coloured_text(text, hex_code):
        """
        Converts the text into a coloured text in the colour of the hex_code.
        """
        r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

    def _get_trip_type(self, route_desc: str, route_colour: str):
        """
        Takes the RouteDesc and RouteColour of a Trip and determines whether it is a
        bus, train, ferry, metro, coach or light rail service.
        """
        if route_desc.lower().__contains__("bus") or route_desc in (
                "New England North West Network",
                "Central West and Orana Network",
                "Newcastle and Hunter Network",
                "North Coast Network",
                "South East and Tablelands Network",
                "Sydney and Surrounds Network",
                "Riverina Murray Network"
        ):
            return "Bus"

        if route_desc.lower().__contains__("trains") and route_colour != "732A82":
            return "Train"

        if route_desc.lower().__contains__("ferr"):
            return "Ferry"

        if route_desc.lower().__contains__("metro"):
            return "Metro"

        if route_desc.lower().__contains__("coach"):
            return "Coach"

        if route_desc.lower().__contains__("light rail"):
            return "Light Rail"

    def _clean_route_names(self, route_short_name: str, route_long_name: str,
                           route_desc: str) -> tuple:
        """
        Clean the RouteShortName and RouteLongName to fit a standardised form.
        """
        # make bus route_short_names lower case
        if route_desc.lower().__contains__("bus"):
            route_short_name = route_short_name.lower()

        # invalid RouteDesc
        if route_short_name == route_long_name:
            return route_short_name, None

        # Zebra Bus for "School buses" RouteDesc
        if route_desc == "School buses" and "Zebra Bus - " in route_long_name:
            return route_short_name, route_long_name[12:]

        # "Newcastle Ferries" RouteDesc
        if route_desc == "Newcastle Ferries":
            return route_short_name.upper(), route_long_name[5:],

        # exclude first route_long_name word
        if route_desc in (
            "Sydney Ferries Network",
            "Private ferry and fast ferry services",
            "Sydney Light Rail Network",
            "Parramatta Light Rail Network",
            "Sydney Trains Network"
        ):
            return route_short_name, ' '.join(route_long_name.split()[1:])

        # exclude first two route_long_name words
        if route_desc == "Sydney Metro Network":
            return route_short_name, ' '.join(route_long_name.split()[2:])

        return route_short_name, route_long_name
