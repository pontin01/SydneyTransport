from typing import Optional

from sydney_transport.binary_tree.avl_tree import AvlTree
from sydney_transport.components.stop import Stop

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
    def __init__(self):
        self.unvisited_stops: AvlTree = AvlTree()
        self.parent_station_exclusion_list = []
        self.temporary_station_exclusion_list = []

        self.start_stop: Optional[Stop] = None
        self.end_stop: Optional[Stop] = None

        self.start_day = ""
        self.start_time = None
