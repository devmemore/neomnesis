import os
from flask import Flask
from flask import request
from neomnesis.common.config import NeoMnesisConfig
from neomnesis.common.db.element import Element
from neomnesis.task.task import Task, TaskDB
from neomnesis.note.note import Note, NoteDB

local_dir = os.path.dirname(__file__)
cfg_path = os.path.join(local_dir, '..', '..', 'config.cfg')

app = Flask('task')

cfg = NeoMnesisConfig(cfg_path)
tdb = TaskDB(cfg)
ndb = NoteDB(cfg)

sub_db = {'task': tdb,
          'note': ndb}

elements_mapping = {'task': Task,
                    'note': Note}


class ElementHandler:

    @classmethod
    def from_data(cls, data):
        class_id = data['class_id']
        return elements_mapping[class_id].from_data(data)


def perform_insert_element(element: Element):
    sub_db[element.class_id].insert(element)


def perform_delete_element(uuid: str, class_id: str):
    sub_db[class_id].delete_by_uuid(uuid)


def perform_modify_field_element(uuid: str, class_id: str, field, value):
    sub_db[class_id].modify(uuid, field, value)


def perform_select_elements(class_id,select_statement):
    return sub_db[class_id].get_from_select(select_statement)


@app.route('/insert', methods=['POST'])
def insert_element():
    element = ElementHandler.from_data(request)
    perform_insert_element(element)
    return 'OK'


@app.route('/delete_<class_id>', methods=['POST'])
def delete_element(class_id):
    uuid = request['_uuid']
    perform_delete_element(uuid,class_id)
    return 'OK'


@app.route('/modify_<class_id>', methods=['POST'])
def modify_element(class_id):
    for key in ['value', 'field', 'uuid']:
        if not key in request:
            raise Exception()
    value = request['value']
    field = request['field']
    _uuid = request['_uuid']
    perform_modify_field_element(_uuid, class_id, field, value)
    return 'OK'


@app.route('/select_<class_id>', methods=['POST'])
def select_elements(class_id):
    if not 'select_statement':
        raise Exception()
    select_statement = request['select_statement']
    res = perform_select_elements(class_id,select_statement)
    return str(res)


@app.route('/commit', methods=['POST'])
def commit():
    tdb.commit()
