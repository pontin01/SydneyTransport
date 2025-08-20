from sydney_transport.map.drawing_utils import *

class OptimalRoute:
    def __init__(self, scale: float):
        self.SCALE = scale

        self.optimal_stops = extract_stops("optimal_route_stops.txt")
        self.stop_count = 0
        self.last_optimal_route_point: Point = (-1, -1)
        self.LINE_HEX_COLOUR = "#0000FF"

    def draw_next_line(self, transparent_layer: pygame.Surface) -> bool:
        # all stops have been drawn
        if self.stop_count >= len(self.optimal_stops):
            return False

        end_point: Point = self._get_optimal_route_information()

        # first stop to be drawn
        if self.last_optimal_route_point == (-1, -1):
            self.last_optimal_route_point = end_point
            self.stop_count += 1
            return True

        draw_line(transparent_layer, self.SCALE, self.LINE_HEX_COLOUR,
                  self.last_optimal_route_point, end_point, 3)

        self.last_optimal_route_point = end_point
        self.stop_count += 1
        return True

    def _get_optimal_route_information(self) -> tuple[int, int]:
        lat, lon = self.optimal_stops[self.stop_count].strip().split(", ")
        y, x = coordinates_to_pixels(lat, lon)
        return y, x
