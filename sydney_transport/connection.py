from datetime import datetime, time, timedelta
import math

from stop import Stop

class Connection:
    def __init__(self, start_stop: Stop, end_stop: Stop):
        self.start_stop = start_stop
        self.end_stop = end_stop

        self.travel_time = self.calculate_travel_time()
        self.coordinate_distance = self.calculate_coordinate_distance()

    def __str__(self):
        return f"\n({self.start_stop = },\n {self.end_stop = },\n {self.travel_time = }," \
              f" {self.coordinate_distance = }\n"

    def calculate_travel_time(self) -> timedelta:
        start_time = self.start_stop.arrival_time
        end_time = self.end_stop.arrival_time

        start_datetime = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)

        return end_datetime - start_datetime

    def calculate_coordinate_distance(self) -> float:
        x1 = self.start_stop.stop_lat
        y1 = self.start_stop.stop_lon
        x2 = self.end_stop.stop_lat
        y2 = self.end_stop.stop_lon

        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    def get_weight(self):
        return self.travel_time.total_seconds()

    def get_cumulative_weight(self):
        if self.start_stop.prev_connection is None:
            return self.travel_time

        return self.start_stop.prev_connection.get_cumulative_weight() + self.travel_time