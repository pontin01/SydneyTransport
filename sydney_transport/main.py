from datetime import datetime, timedelta
import sys
import time

from components.search import Search
from components.stop import Stop
from binary_tree.avl_tree import AvlTree

def retrieve_user_settings() -> dict:
    """
    Retrieves user database settings and search settings.
    :return: Dict with all user settings.
    """
    user_settings = {}

    try:
        # get database information
        user_settings["db_username"] = input("Database Username: ")
        user_settings["db_password"] = input("Database Password: ")

        # get search settings
        user_settings["start_stop_name"] = input("Start Stop Name: ")
        user_settings["end_stop_name"] = input("End Stop Name: ")
        user_settings["start_day"] = get_start_day()
        user_settings["start_time"] = get_start_time()
    except EOFError:
        print("Exiting!")
        print("main.py: retrieve_user_settings() failed")
        sys.exit(0)

    return user_settings

def get_start_day() -> str:
    """
    Gets starting day for the search; verifies input is a day of the week.
    """
    # loop until valid day inputted
    while True:
        desired_day = input("Start Day: ")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                "sunday"]
        if desired_day.lower() not in days:
            print("Enter a valid day of the week.")
            continue
        break

    return desired_day

def get_start_time() -> time:
    """
    Gets starting time for the search; converts inputted time into time object.
    """
    start_time = input("Start Time: ")
    return datetime.strptime(start_time, "%H:%M").time()

def main():
    # temp_test()

    search = Search()

    user_settings = retrieve_user_settings()

    search.setup(
        user_settings["db_username"],
        user_settings["db_password"],
        user_settings["start_stop_name"],
        user_settings["end_stop_name"],
        user_settings["start_day"],
        user_settings["start_time"]
    )
    search.search()

def temp_test():
    avl = AvlTree()

    # test_numbers = [19, 48, 22, 24, 25, 45, 30, 23, 28, 31]
    test_numbers = [80, 67, 78, 25, 58, 21, 31, 14, 33, 96]

    for num in test_numbers:
        xtime = datetime.strptime("15:00", "%H:%M").time()

        stop = Stop(
            stop_id=str(num),
            stop_name=f"{num}",
            stop_lat=0.1,
            stop_lon=0.1,
            parent_station=str(num),
            trip_id=str(num),
            arrival_time=xtime,
            stop_sequence=num
        )
        avl.insert(stop, timedelta(minutes=num))

    inorder = avl.inorder_traversal(avl.root)

    print(inorder)

    sys.exit(0)


if __name__ == '__main__':
    main()
