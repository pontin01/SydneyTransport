class Trip:
    def __init__(self, route_id: str, service_id: str, trip_id: str, shape_id: str,
                 trip_headsign: str, direction_id: bool, block_id: str, wheelchair_accessible: int,
                 route_direction: str, trip_note: str, bikes_allowed: str):
        self.route_id = route_id
        self.service_id = service_id
        self.trip_id = trip_id
        self.shape_id = shape_id
        self.trip_headsign = trip_headsign
        self.direction_id = direction_id
        self.block_id = block_id
        self.wheelchair_accessible = wheelchair_accessible
        self.route_direction = route_direction
        self.trip_note = trip_note
        self.bikes_allowed = bikes_allowed
