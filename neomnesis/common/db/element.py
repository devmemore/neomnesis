from typing import Dict

class Element(object):

    on_creation_columns = {'class_id' : str,'_uuid' : str}
    columns = dict(**on_creation_columns)

    def __init__(self,class_id, _uuid):
        self.class_id = class_id
        self._uuid = _uuid

    def to_row(self):
        return {}

    @classmethod
    def from_data(self, data : Dict):
        return Element(data['class_id'], data['uuid'])


