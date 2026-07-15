from datetime import datetime, time
import sys
from typing import Tuple


def retrieve_settings(cmd_line_args: list) -> Tuple[dict, dict]:
    """
    Retrieves user database settings and search settings.
    """
    cmd_line_search_options = __extract_cmd_line_options(cmd_line_args)

    try:
        user_settings = {
            "db_username": input("Database Username: "),
            "db_password": input("Database Password: ")
        }
        search_settings = {
            "start_stop_name": input("Start Stop Name: "),
            "end_stop_name": input("End Stop Name: "),
            "start_day": input("Start Day: ").lower(),
            "start_time": __get_start_time(input("Start Time: "))
        } | cmd_line_search_options
    except EOFError:
        print("Exiting!")
        print("utils.py: retrieve_user_settings() failed")
        sys.exit()

    return user_settings, search_settings

def __extract_cmd_line_options(args: list) -> dict:
    """
    Extracts the search options provided as flags in the command line.
    """
    options = {
        "verbose_output": False
    }

    # no flags provided
    if len(args) <= 1:
        return options

    if "-v" in args:
        options["verbose_output"] = True

    return options

def __get_start_time(time: str) -> time:
    """
    Converts inputted time into time object.
    """
    return datetime.strptime(time, "%H:%M").time()