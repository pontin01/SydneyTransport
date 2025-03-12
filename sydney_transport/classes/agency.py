class Agency:
    def __init__(self, agency_id: str, agency_name: str, agency_url: str,
                 agency_timezone: str, agency_lang: str, agency_phone: str):
        self.agency_id = agency_id
        self.agency_name = agency_name
        self.agency_url = agency_url
        self.agency_timezone = agency_timezone
        self.agency_lang = agency_lang
        self.agency_phone = agency_phone