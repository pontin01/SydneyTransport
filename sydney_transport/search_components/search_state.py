import sys
import time
from typing import Optional

from sydney_transport.binary_tree.avl_tree import AvlTree
from sydney_transport.database import stop_db
from sydney_transport.search_components import Stop, search_utils
from sydney_transport.search_components.search2 import Search


class SearchState:
    """
    Information about the current state of the Search.

    Attributes:
        unvisited_stops (AvlTree): An AVL Binary tree of the stops that haven't
                                   been searched yet.
        parent_station_exclusion_list (list): All parent stations that have been
                                              visited.
        start_stop (Stop): The Stop the search is starting from.
        end_stop (Stop): The Stop the search is ending at.
        start_day (string): The day the search is starting on.
        start_time (time): The time the search is starting on.
    """
    def __init__(self, search_settings: dict):
        # modes
        self._verbose_mode = search_settings["verbose_mode"]

        # search information
        self._start_day = search_settings["start_day"]
        self._start_time = search_settings["start_time"]

        self._start_stop: Stop = self.__set_search_stop(search_settings["start_stop_name"])
        self._start_stop.arrival_time = self.start_time
        self._end_stop: Stop = self.__set_search_stop(search_settings["end_stop_name"])

        # search tracking information
        self._unvisited_stop_tree: AvlTree = AvlTree()
        self._parent_station_exclusion_list = []
        self._temporary_station_exclusion_list = []
        self._ideal_heuristic_cost = 1
        self._stops_searched = 0

        # map drawing information
        self._coords_list = []
        self._end_coord_list = []

    def add_stop_to_coord_list(self, stop: Stop, timer):
        self._coords_list.append([
            stop.stop_lat,
            stop.stop_lon,
            time.perf_counter() - timer,
            stop.trip_id,
        ])

    def stop_is_temp_excluded_station(self, stop_id: int) -> bool:
        return stop_id in self._temporary_station_exclusion_list

    def add_temp_excluded_station(self, stop_id: int) -> None:
        self._temporary_station_exclusion_list.append(stop_id)

    def remove_temp_excluded_station(self, stop: Stop) -> None:
        if stop.stop_id in self._temporary_station_exclusion_list:
            self._temporary_station_exclusion_list.remove(stop.stop_id)

    def stop_is_excluded_parent_station(self, parent_stop_id: int) -> bool:
        return parent_stop_id in self._parent_station_exclusion_list

    def add_excluded_parent_station(self, stop_id: int) -> None:
        self._parent_station_exclusion_list.append(stop_id)

    def increment_stops_searched(self) -> None:
        self._stops_searched += 1

    def is_final_stop(self, stop_id: int) -> bool:
        return stop_id == self.end_stop.stop_id

    def __set_search_stop(self, stop_name: str) -> Stop:
        """
        Checks whether the entered stop_name is valid and prompts the user with
        alternatives if it is not.
        """
        stop_name = search_utils.clean_stop_name(stop_name)

        db_conn = Search().db_conn
        stop = Stop.stop_name_to_stop(stop_name, db_conn)

        # prompt for alternative stop names
        if stop is None:
            stop = self.__suggest_alternative_stops(stop_name)

        return stop

    def __suggest_alternative_stops(self, stop_name: str) -> Stop:
        """
        Prompt for alternative stop names if the entered stop does not exist.
        """
        result = stop_db.get_stop_name_from_typo(stop_name, Search().db_conn)

        print(f"\n{stop_name} was not found.")
        print("Did you mean one of these? (press ENTER to skip)\n")

        print("1. " + result[0][0])
        print("2. " + result[1][0])
        print("3. " + result[2][0])
        print("4. " + result[3][0])
        print("5. " + result[4][0])

        answer = input("\n")

        if answer == "":
            print("\nExiting.\n")
            sys.exit()

        return Stop.stop_name_to_stop(result[int(answer)][0], Search().db_conn)

    @property
    def verbose_mode(self) -> bool:
        return self._verbose_mode

    @property
    def start_day(self) -> str:
        return self._start_day

    @property
    def start_stop(self) -> Stop:
        return self._start_stop

    @property
    def end_stop(self) -> Stop:
        return self._end_stop

    @property
    def unvisited_stop_tree(self) -> AvlTree:
        return self._unvisited_stop_tree

    @property
    def stops_searched(self) -> int:
        return self._stops_searched
