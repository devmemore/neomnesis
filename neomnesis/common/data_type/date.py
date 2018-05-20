from datetime import date, datetime

class Date(date)
    
    def __init__(self,str_date):
        date.__init__(self)
        self = datetime.strptime(str_date, "%Y-%m-%d")
