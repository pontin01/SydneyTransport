from datetime import datetime, time
import sys

def extract_cmd_line_options(args: list) -> dict:
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

def retrieve_user_settings() -> dict:
    """
    Retrieves user database settings and search settings.
    :return:
    """
    try:
        user_settings = {
            "db_username": input("Database Username: "),
            "db_password": input("Database Password: "),
            "start_stop_name": input("Start Stop Name: "),
            "end_stop_name": input("End Stop Name: "),
            "start_day": input("Start Day: ").lower(),
            "start_time": __get_start_time(input("Start Time: "))
        }
    except EOFError:
        print("Exiting!")
        print("utils.py: retrieve_user_settings() failed")
        sys.exit()

    return user_settings

def __get_start_time(time: str) -> time:
    """
    Converts inputted time into time object.
    """
    return datetime.strptime(time, "%H:%M").time()