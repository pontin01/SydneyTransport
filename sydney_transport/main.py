import sys

from modes.trains import run_trains

"""
Checks if a mode was entered as a command line argument. If not, prompts user to
insert a mode.
"""
def get_mode(args: list, available_modes: list):
    modes = ["trains"]

    if len(args) > 3:
        if args[3] == "-m":
            if args[4] in modes:
                return args[4]

    print("Available Modes: trains, ...")
    while True:
        try:
            mode = input("Please Enter A Mode: ")
            if mode in available_modes:
                return mode
        except EOFError:
            return None
        print("Sorry, that is not a valid mode.")


def main(args: list):
    db_username = args[1]
    db_password = args[2]

    available_modes = ["trains"]

    # check for cmd line entered mode
    mode = get_mode(args, available_modes)
    if mode is None:
        print("Goodbye!")
        sys.exit()

    # load func
    mode_funcs = {
        "trains": run_trains(db_username, db_password)
    }
    mode_funcs[mode]()


if __name__ == "__main__":
    main(sys.argv)
