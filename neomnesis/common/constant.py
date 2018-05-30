from datetime import  datetime
from neomnesis.common.data_type.text import Text
from neomnesis.common.data_type.date import Date, DateHour, DateTime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

SQLITE_TYPE_MAPPING = {str : 'text',
                       int : 'real',
                       datetime : 'text',
                       Text : 'text',
                       Date : 'text',
                       DateHour : 'text',
                       DateTime : 'text'}


def sqlite_type_convertion(data_element):
    if isinstance(data_element, Text) :
        return data_element.to_str()
    elif isinstance(data_element, Date) :
        return data_element.to_str()
    elif isinstance(data_element, DateHour) :
        return data_element.to_str()
    elif isinstance(data_element, DateTime) :
        return data_element.to_str()
    else :
        return data_element



DATETIME_NANO_PRECISION_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
