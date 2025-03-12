class Route:
    def __init__(self, route_id: str, agency_id: str, route_short_name: str,
                 route_long_name: str, route_desc: str, route_type: int,
                 route_colour: str, route_text_colour: str, exact_times: bool):
        self.route_id = route_id
        self.agency_id = agency_id
        self.route_short_name = route_short_name
        self.route_long_name = route_long_name
        self.route_desc = route_desc
        self.route_type = route_type
        self.route_colour = route_colour
        self.route_text_colour = route_text_colour
        self.exact_times = exact_times

    def __repr__(self):
        return (f"RouteID={self.route_id}, AgencyID={self.agency_id}, "
                f"RouteShortName={self.route_short_name}, "
                f"RouteLongName={self.route_long_name}, "
                f"RouteDesc={self.route_desc}, RouteType={self.route_type}, "
                f"RouteColour={self.route_colour}, RouteTextColour={self.route_text_colour}, "
                f"ExactTimes={self.exact_times}")