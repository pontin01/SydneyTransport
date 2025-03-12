class Shape:
    def __init__(self, shape_id: str, shape_pt_lat: float, shape_pt_lon: float,
                 shape_pt_sequence: int, shape_dist_traveled: float, prev_shape: tuple,
                 next_shape: tuple):
        self.shape_id = shape_id
        self.shape_pt_lat = shape_pt_lat
        self.shape_pt_lon = shape_pt_lon
        self.shape_pt_sequence = shape_pt_sequence
        self.shape_dist_traveled = shape_dist_traveled
        self.prev_shape = prev_shape
        self.next_shape = next_shape