from sydney_transport.map.drawing_utils import *

from sydney_transport.search_components import Stop

class ExplorationRoutes:
    def __init__(self, scale: float, colour_mode: str, start_stop: Stop, end_stop: Stop):
        self.SCALE = scale
        self.COLOUR_MODE = colour_mode

        self.exploration_stops = extract_stops("exploration_route_stops.txt")
        self.stop_count = 0
        self.last_point_by_trip: dict[str, Point] = {}
        self.line_hex_colour = "#00FF00"

        if self.COLOUR_MODE == "STATIC":
            self.line_hex_colour = "#FF0000"

        # variables for colouring by DISTANCE
        self.start_point: Point = coordinates_to_pixels(start_stop.stop_lat, start_stop.stop_lon)
        self.end_point: Point = coordinates_to_pixels(end_stop.stop_lat, end_stop.stop_lon)
        self.furthest_distance_from_end = get_furthest_distance_from_point(self.end_point, self.SCALE)

    def draw_next_line(self, transparent_layer: pygame.Surface) -> bool:
        # all stops have been drawn
        if self.stop_count >= len(self.exploration_stops):
            return False

        end_y, end_x, end_timestamp, end_trip_id = self._get_stop_information()
        end_point: Point = (end_y, end_x)

        # a stop from this trip has not been encountered
        if end_trip_id not in self.last_point_by_trip.keys():
            self.last_point_by_trip[end_trip_id] = end_point
            self.stop_count += 1

            return True

        # increment line hex colour if coloured by TIME
        if self.COLOUR_MODE == "TIME" and self.stop_count % (int(len(self.exploration_stops) / 510)) == 0:
            self.line_hex_colour = increment_line_hex_colour(self.line_hex_colour)

        # calculate line colour if coloured by DISTANCE
        if self.COLOUR_MODE == "DISTANCE":
            self.line_hex_colour = calculate_distance_hex_colour(end_point, self.start_point,
                                                                 self.furthest_distance_from_end,
                                                                 self.SCALE)

        start_point: Point = self.last_point_by_trip[end_trip_id]

        draw_line(transparent_layer, self.SCALE, self.line_hex_colour,
                  start_point, end_point, 2)

        self.last_point_by_trip[end_trip_id] = end_point
        pygame.time.wait(int(end_timestamp * 1000))

        self.stop_count += 1

        return True

    def _get_stop_information(self) -> tuple[int, int, float, str]:
        lat, lon, timestamp, trip_id = self.exploration_stops[self.stop_count].strip().split(", ")
        y, x = coordinates_to_pixels(lat, lon)
        return y, x, float(timestamp), trip_id
