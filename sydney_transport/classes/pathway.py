class Pathway:
    def __init__(self, pathway_id: str, from_stop_id: str, to_stop_id: str,
                 pathway_mode: int, is_bidirectional: bool, traversal_time: int):
        self.pathway_id = pathway_id
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.pathway_mode = pathway_mode
        self.is_bidirectional = is_bidirectional
        self.traversal_time = traversal_time