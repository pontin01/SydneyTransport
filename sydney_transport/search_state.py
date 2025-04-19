class SearchState:
    def __init__(self):
        self.db_username = ""
        self.db_password = ""
        self.start_id = ""
        self.end_id = ""
        self.desired_day = ""
        self.desired_time = ""
        self.search_method = ""

        self.searched_stops = {}
        self.searched_paths = {}