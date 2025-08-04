import pytest

from tests.avl_tree_tests.conftest import create_test_stop_and_travel_time

@pytest.mark.parametrize(
    "node_number, expected",
    [
        (32, ['6', '16', '21', '27', '32', '33', '35', '38', '53', '62', '67']),
        (69, ['6', '16', '21', '27', '33', '35', '38', '53', '62', '67', '69']),
        (37, ['6', '16', '21', '27', '33', '35', '37', '38', '53', '62', '67'])
    ]
)
def test_insert_basic(node_number, expected, testing_avl_tree):
    """
    Inserts one number into the AVL Tree.
    """
    stop, travel_duration = create_test_stop_and_travel_time(node_number)
    testing_avl_tree.insert(stop, travel_duration)

    result = testing_avl_tree.inorder_traversal(testing_avl_tree.root)

    assert expected == result

@pytest.mark.parametrize(
    "node_numbers, expected",
    [
        (
            [96, 69, 28, 77, 36, 9, 40, 81, 62, 20],
            ['6', '9', '16', '20', '21', '27', '28', '33', '35', '36', '38',
             '40', '53', '62', '67', '69', '77', '81', '96']
        ),
        (
            [66, 68, 72, 10, 56, 50, 82, 46, 41, 76],
            ['6', '10', '16', '21', '27', '33', '35', '38', '41', '46', '50',
             '53', '56', '62', '66', '67', '68', '72', '76', '82']
        ),
        (
            [39, 59, 97, 22, 88, 26, 96, 63, 56, 54],
            ['6', '16', '21', '22', '26', '27', '33', '35', '38', '39', '53',
             '54', '56', '59', '62', '63', '67', '88', '96', '97']
        )
    ]
)
def test_insert_multiple(node_numbers, expected, testing_avl_tree):
    """
    Inserts multiple numbers into the AVL Tree.
    """
    for num in node_numbers:
        stop, travel_duration = create_test_stop_and_travel_time(num)
        testing_avl_tree.insert(stop, travel_duration)

    result = testing_avl_tree.inorder_traversal(testing_avl_tree.root)

    assert expected == result



















