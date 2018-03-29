from datetime import  datetime


SQLITE_TYPE_MAPPING = {str : 'text',
                       int : 'real',
                       datetime : 'text'}

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_NANO_PRECISION_FORMAT = "%Y-%m-%d %H:%M:%S %N"
