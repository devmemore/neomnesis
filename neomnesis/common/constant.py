from datetime import  datetime
from neomnesis.common.data_type.text import Text
from neomnesis.common.data_type.date import Date, DateHour, DateTime 


SQLITE_TYPE_MAPPING = {str : 'text',
                       int : 'real',
                       datetime : 'text',
                       Text : 'text',
                       Date : 'text',
                       DateHour : 'text',
                       DateTime : 'text'}

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_NANO_PRECISION_FORMAT = "%Y-%m-%d %H:%M:%S %N"
