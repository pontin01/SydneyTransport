class Service:
    def __init__(self, service_id: str, monday: bool, tuesday: bool, wednesday: bool,
                 thursday: bool, friday: bool, saturday: bool, sunday: bool,
                 start_date, end_date):
        self.service_id = service_id
        self.monday = monday
        self.tuesday = tuesday
        self.wendesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        self.start_date = start_date
        self.end_date = end_date
