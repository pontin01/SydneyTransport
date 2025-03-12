class Stop:
    def __init__(self, stop_id, stop_code, stop_name, stop_lat, stop_lon,
                 location_type, parent_station, wheelchair_boarding, level_id,
                 platform_code):
        self.stop_id = stop_id
        self.stop_code = stop_code
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.location_type = location_type
        self.parent_station = parent_station
        self.wheelchair_boarding = wheelchair_boarding
        self.level_id = level_id
        self.platform_code = platform_code

    def __str__(self):
        return (f"(StopID={self.stop_id}, StopCode={self.stop_code}, "
                f"StopName={self.stop_name}, StopLat={self.stop_lat}, "
                f"StopLon={self.stop_lon}, LocationType={self.location_type}, "
                f"ParentStation={self.parent_station}, WheelchairBoarding={self.wheelchair_boarding}, "
                f"LevelID={self.level_id}, PlatformCode={self.platform_code}")

    def __repr__(self):
        return (f"(StopID={self.stop_id}, StopCode={self.stop_code}, "
                f"StopName={self.stop_name}, StopLat={self.stop_lat}, "
                f"StopLon={self.stop_lon}, LocationType={self.location_type}, "
                f"ParentStation={self.parent_station}, WheelchairBoarding={self.wheelchair_boarding}, "
                f"LevelID={self.level_id}, PlatformCode={self.platform_code}\n")