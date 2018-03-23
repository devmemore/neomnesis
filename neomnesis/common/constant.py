from datetime import  datetime


SQLITE_TYPE_MAPPING = {str : 'text',
                       int : 'real',
                       datetime : 'text'}

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
