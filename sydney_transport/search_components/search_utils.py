import datetime as dt

import pandas

from sydney_transport.database import trip_db
from sydney_transport.search_components.search2 import Search


def add_time(arrival_time: dt.time, difference: dt.timedelta) -> dt.time:
    datetime_object = dt.datetime.combine(dt.datetime.today(), arrival_time)
    new_datetime = datetime_object + difference
    return new_datetime.time()

def coloured_text(text, hex_code):
    """
    Converts the text into a coloured text in the colour of the hex_code.
    """
    r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def get_trip_type(route_desc: str, route_colour: str):
    """
    Takes the RouteDesc and RouteColour of a Trip and determines whether it is a
    bus, train, ferry, metro, coach or light rail service.
    """
    if route_desc.lower().__contains__("bus") or route_desc in (
            "New England North West Network",
            "Central West and Orana Network",
            "Newcastle and Hunter Network",
            "North Coast Network",
            "South East and Tablelands Network",
            "Sydney and Surrounds Network",
            "Riverina Murray Network"
    ):
        return "Bus"

    if route_desc.lower().__contains__("trains") and route_colour != "732A82":
        return "Train"

    if route_desc.lower().__contains__("ferr"):
        return "Ferry"

    if route_desc.lower().__contains__("metro"):
        return "Metro"

    if route_desc.lower().__contains__("coach"):
        return "Coach"

    if route_desc.lower().__contains__("light rail"):
        return "Light Rail"

def clean_stop_name(stop_name: str) -> str:
    """
    Cleans the stop_name input provided to better match the database.

    Ave     --> Av
    at      --> At
    before  --> Before
    """
    if "Ave" in stop_name:
        stop_name = stop_name.replace("Ave", "Av")
    if "at" in stop_name:
        stop_name = stop_name.replace("at", "At")
    if "before" in stop_name:
        stop_name = stop_name.replace("before", "Before")

    return stop_name

def clean_route_names(route_short_name: str, route_long_name: str, route_desc: str) -> tuple:
    """
    Clean the RouteShortName and RouteLongName to fit a standardised form.
    """
    # make bus route_short_names lower case
    if route_desc.lower().__contains__("bus"):
        route_short_name = route_short_name.lower()

    # invalid RouteDesc
    if route_short_name == route_long_name:
        return route_short_name, None

    # Zebra Bus for "School buses" RouteDesc
    if route_desc == "School buses" and "Zebra Bus - " in route_long_name:
        return route_short_name, route_long_name[12:]

    # "Newcastle Ferries" RouteDesc
    if route_desc == "Newcastle Ferries":
        return route_short_name.upper(), route_long_name[5:],

    # exclude first route_long_name word
    if route_desc in (
        "Sydney Ferries Network",
        "Private ferry and fast ferry services",
        "Sydney Light Rail Network",
        "Parramatta Light Rail Network",
        "Sydney Trains Network"
    ):
        return route_short_name, ' '.join(route_long_name.split()[1:])

    # exclude first two route_long_name words
    if route_desc == "Sydney Metro Network":
        return route_short_name, ' '.join(route_long_name.split()[2:])

    return route_short_name, route_long_name

def print_stop_order(final_stop_order: list) -> None:
    """
    Print Stop order for verbose mode.
    """
    print("\nVerbose Stop Order:\n")

    data = []
    for stop in final_stop_order:
        item = [stop.stop_id, stop.trip_id, stop.stop_sequence,
                stop.arrival_time, stop.stop_name]
        data.append(item)

        stop.state.end_coord_list.append([stop.stop_lat, stop.stop_lon])

    data_frame = pandas.DataFrame(data, columns=["StopID", "TripID", "Sequence", "ArrivalTime", "Name"])

    print(data_frame + "\n")

def print_route_directions(final_stop_order: list) -> None:
    """
    Prints a summary of the route information.
    """
    current_trip_id = ""
    current_trip_info = ()
    for i in range(len(final_stop_order)):
        current_stop = final_stop_order[i]

        # start stop
        if i == 0:
            arrival_time = coloured_text(current_stop.arrival_time, "FFDE21")
            print(f"\n\nStarting from {current_stop.stop_name} at {arrival_time}.\n")
            continue

        # current_stop is sibling without a trip, should be skipped
        if current_stop.stop_sequence is None and current_stop.trip_id is None:
            continue

        # current_stop is the start of a trip
        if current_stop.stop_id == final_stop_order[i - 1].stop_id:
            result = trip_db.get_trip_info_after_search(current_stop.trip_id, Search().db_conn)[0]
            route_short_name, route_long_name, route_desc, hex_colour = result

            current_trip_type = get_trip_type(route_desc, hex_colour)

            route_short_name, route_long_name = clean_route_names(route_short_name,
                                                                     route_long_name,
                                                                     route_desc)

            current_trip_info = (route_short_name, hex_colour)
            current_trip_id = current_stop.trip_id
            arrival_time = coloured_text(current_stop.arrival_time, "FFDE21")

            text = f"Go to {current_stop.stop_name} and get on the "
            text += f"{coloured_text(route_short_name, hex_colour)} "
            text += f"{current_trip_type} "

            # exclude invalid RouteLongName values for Regional Trains and Coaches Network routes
            if route_long_name is not None:
                text += f"({route_long_name}) "

            text += f"arriving at {arrival_time}."
            print(text)

            continue

        # current_stop is in a trip, but not the start or end
        if current_stop != final_stop_order[-1]:
            if current_stop.trip_id == current_trip_id and \
                    final_stop_order[i + 1].trip_id == current_trip_id:
                continue

        # current_stop is the end of a trip (or end stop)
        if current_stop.trip_id is not None:
            is_end_stop = len(final_stop_order) - 1 == i
            is_end_of_trip = False

            if not is_end_stop:
                if final_stop_order[i + 1].trip_id != current_stop.trip_id:
                    is_end_of_trip = True

            if is_end_stop or is_end_of_trip:
                arrival_time = coloured_text(current_stop.arrival_time, "FFDE21")

                text = f"The {coloured_text(current_trip_info[0], current_trip_info[1])} "
                text += f"will arrive at {current_stop.stop_name} at {arrival_time}. "
                text += "Get off here.\n"
                print(text)

    print("You are now at your destination.\n")