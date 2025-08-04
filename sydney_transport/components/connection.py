from datetime import datetime, timedelta
import math

from sydney_transport.components.stop import Stop

class Connection:
    """
    Represents the connection between two Stops.

    Attributes:
        start_stop (Stop): Stop where the connection will start from.
        end_stop (Stop): Stop where the connection will end.
        travel_duration (timedelta): Time to get from the start_stop to end_stop.
        coordinate_distance (float): Euclidian distance from start_stop to end_stop.
    """
    def __init__(self, start_stop: Stop, end_stop: Stop):
        self.start_stop = start_stop
        self.end_stop = end_stop

        self.travel_duration = self.calculate_travel_time()
        self.coordinate_distance = self.calculate_coordinate_distance()

    def calculate_travel_time(self) -> timedelta:
        """
        Calculates the difference between the start_stop arrival time and the
        end_stop arrival time.
        """
        start_time = self.start_stop.arrival_time
        end_time = self.end_stop.arrival_time

        start_datetime = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)

        return end_datetime - start_datetime

    def calculate_coordinate_distance(self) -> float:
        """
        Calculates the Euclidian distance between start_stop and end_stop.
        """
        x1 = self.start_stop.stop_lat
        y1 = self.start_stop.stop_lon
        x2 = self.end_stop.stop_lat
        y2 = self.end_stop.stop_lon

        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    def get_cumulative_weight(self):
        # TODO: can be fixed, is recursive
        if self.start_stop.prev_connection is None:
            return self.travel_duration

        return self.start_stop.prev_connection.get_cumulative_weight() + self.travel_duration
