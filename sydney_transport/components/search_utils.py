import datetime as dt

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
