import pytest

from tests.avl_tree_tests.conftest import create_test_stop_and_travel_time, create_custom_avl_tree

@pytest.mark.parametrize(
    "stops_removed_beforehand, inserted_nodes, expected_stop, expected_order",
    [
        (
            0, [6], '6', ['6', '16', '21', '27', '33', '35', '38', '53', '62', '67']
        ),
        (
            2, [], '21', ['27', '33', '35', '38', '53', '62', '67']
        ),
        (
            6, [], '38', ['53', '62', '67']
        )
    ]
)
def test_remove_closest_stop(stops_removed_beforehand, inserted_nodes, expected_stop,
                             expected_order, testing_avl_tree):
    """
    ...
    """
    # remove stops beforehand
    for i in range(stops_removed_beforehand):
        testing_avl_tree.remove_closest_stop()

    # insert some stops
    if inserted_nodes:
        stop, travel_duration = create_test_stop_and_travel_time(inserted_nodes[0])
        testing_avl_tree.insert(stop, travel_duration)

    closest_stop = testing_avl_tree.remove_closest_stop()
    result_stop = closest_stop.stop_name

    assert expected_stop == result_stop

    result_order = testing_avl_tree.inorder_traversal(testing_avl_tree.root)

    assert expected_order == result_order

def test_inorder_traversal():
    pass

def test_check_avl_quality():
    pass