from datetime import date, datetime

class Date(date):
    date_format="%Y-%m-%d"
    
    def __init__(self, str_date : str):
        super(Date,self).__init__(datetime.strptime(str_date, date_format).date)

class DateHour(datetime):
    date_format="%Y-%m-%d %H"

    def __init__(self, str_date : str):
        datetime.__init__(self)
        self = datetime.strptime(str_date, date_format)

