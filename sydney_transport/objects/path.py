from sydney_transport.objects.stop import Stop

class Path:
    def __init__(self, trip_id, route_id, direction_id):
        self.trip_id = trip_id
        self.route_id = route_id
        self.direction_id = direction_id
        self.stops = []
        self.stop_ids = []

    def add_stop(self, stop: Stop, stop_sequence, arrival_time):
        self.stops.append([stop_sequence, stop, arrival_time])
        self.stop_ids.append(stop.stop_id)

    def print_stops(self):
        # for stop in self.stops:
        #     print(stop.)
        pass