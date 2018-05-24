from datetime import date, datetime

class Date(date):
    date_format="%Y-%m-%d"
    
    def __new__(cls, str_date):
        mdate = datetime.strptime(str_date,cls.date_format).date()
        instance = super().__new__(cls,mdate.year,mdate.month,mdate.day)
        return instance

    @classmethod
    def from_datetime(cls, dt : datetime):
        return Date(dt.strftime(cls.date_format))

class DateHour(datetime):
    date_format="%Y-%m-%d %H"

    def __new__(cls, str_datehour):
        mdatehour = datetime.strptime(str_datehour,cls.date_format)
        instance = super().__new__(cls,mdatehour.year,mdatehour.month,mdatehour.day, mdatehour.hour)
        return instance

    @classmethod
    def from_datetime(cls, dt : datetime):
        return DateHour(dt.strftime(cls.date_format))


class DateTime(datetime):
    date_format="%Y-%m-%d %H:%M:%S"

    def __new__(cls, str_datehour):
        mdatehour = datetime.strptime(str_datehour,cls.date_format)
        instance = super().__new__(cls,mdatehour.year,mdatehour.month,mdatehour.day, mdatehour.hour)
        return instance

    @classmethod
    def from_datetime(cls, dt : datetime):
        return DateTime(dt.strftime(cls.date_format))
