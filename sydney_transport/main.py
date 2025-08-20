from datetime import datetime, time
import sys
import mysql.connector.errors

from components.search import Search

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

def extract_cmd_line_options(args: list) -> tuple[bool, str, str]:
    verbose_mode = False
    search_mode = "A*"
    colour_mode = "STATIC"

    if len(args) > 1:
        # print help information
        if "-h" in args or "--help" in args:
            print("HELP")
            sys.exit(0)
        if "-v" in args:
            verbose_mode = True
            print("Verbose Mode On\n")
        if "-d" in args:
            search_mode = "DIJKSTRA"
        if "-c" in args:
            try:
                colour_mode: str = args[args.index("-c") + 1].upper()

                if colour_mode not in ("STATIC", "TIME", "DISTANCE"):
                    raise ValueError

            except (ValueError, IndexError):
                print("You must enter a valid Colour Mode (STATIC, TIME, DISTANCE)\n")
                sys.exit(0)

    if verbose_mode:
        print(f"Search Mode: {search_mode}")
        print(f"Colour Mode: {colour_mode}\n\n")

    return verbose_mode, search_mode, colour_mode



def main(args: list):
    print()

    # check command line options
    verbose_mode, search_mode, colour_mode = extract_cmd_line_options(args)

    search = Search()

    user_settings = retrieve_user_settings()

    search.setup(
        user_settings["db_username"],
        user_settings["db_password"],
        user_settings["start_stop_name"],
        user_settings["end_stop_name"],
        user_settings["start_day"],
        user_settings["start_time"],
        verbose_mode,
        search_mode,
        colour_mode
    )

    search.search()



if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("\n\nForce Exited.\n")
    except mysql.connector.errors.InternalError:
        print("\n\nForce Exited.\n")
