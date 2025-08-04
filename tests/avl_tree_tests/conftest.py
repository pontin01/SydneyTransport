import pytest
from datetime import datetime, timedelta

from sydney_transport.binary_tree.avl_tree import AvlTree
from sydney_transport.binary_tree.node import Node
from sydney_transport.components.stop import Stop

def create_test_stop_and_travel_time(num: int):
    """
    Creates a test node.
    """
    stop = Stop(
        stop_id=str(num),
        stop_name=f"{num}",
        stop_lat=0.1,
        stop_lon=0.1,
        parent_station=str(num),
        trip_id=str(num),
        arrival_time=datetime.strptime("15:00", "%H:%M"),
        stop_sequence=num
    )
    travel_duration = timedelta(minutes=num)

    return stop, travel_duration

def create_custom_avl_tree(number_list: list) -> AvlTree:
    pass

@pytest.fixture(scope="function")
def testing_avl_tree():
    """
    Replicating an AVL Tree which has the numbers 62, 38, 27, 33, 21, 6, 35, 16, 53, 67
    inserted in that order.
    Inorder Traversal: 6, 16, 21, 27, 33, 35, 38, 53, 62, 67
    """
    avl_tree = AvlTree()

    # number, height, balance_factor
    test_numbers = [(62, 1, 0),
                    (38, 2, 0),
                    (27, 3, 0),
                    (33, 1, 0),
                    (21, 0, 0),
                    (6, 0, 0),
                    (35, 0, 0),
                    (16, 1, 0),
                    (53, 0, 0),
                    (67, 0, 0)]

    # create Node objects
    node_list = {}

    for node_data in test_numbers:
        stop, travel_duration = create_test_stop_and_travel_time(node_data[0])

        new_node = Node(stop, travel_duration)
        new_node.height = node_data[1]
        new_node.balance_factor = node_data[2]

        node_list[node_data[0]] = new_node

    avl_tree.root = node_list[27]
    node_list[27].left = node_list[16]
    node_list[27].right = node_list[38]

    node_list[16].left = node_list[6]
    node_list[16].right = node_list[21]

    node_list[38].left = node_list[33]
    node_list[38].right = node_list[62]

    node_list[33].right = node_list[35]

    node_list[62].left = node_list[53]
    node_list[62].right = node_list[67]

    return avl_tree