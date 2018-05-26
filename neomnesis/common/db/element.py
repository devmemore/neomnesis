from typing import Dict
from neomnesis.common.constant import sqlite_type_convertion

class Element(object):

    on_creation_columns = {'class_id' : str,'_uuid' : str}
    columns = dict(**on_creation_columns)

    def __init__(self,class_id, _uuid):
        self.class_id = class_id
        self._uuid = _uuid

    def to_row(self):
        return dict([(k, sqlite_type_convertion(self.__dict__[k])) for k in self.__dict__.keys()])

    @classmethod
    def from_data(self, data : Dict):
        return Element(data['class_id'], data['uuid'])


