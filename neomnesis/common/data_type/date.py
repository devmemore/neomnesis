from datetime import date, datetime

class Date(date):
    date_format="%Y-%m-%d"
    
    def __new__(cls, str_date):
        mdate = datetime.strptime(str_date,cls.date_format).date()
        instance = super().__new__(cls,mdate.year,mdate.month,mdate.day)
        return instance

class DateHour(datetime):
    date_format="%Y-%m-%d %H"

    def __new__(cls, str_datehour):
        mdatehour = datetime.strptime(str_datehour,cls.date_format)
        instance = super().__new__(cls,mdatehour.year,mdatehour.month,mdatehour.day, mdatehour.hour)
        return instance
