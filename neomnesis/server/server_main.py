import os

from flask import Flask
from flask import request
import pandas as pd
import re

from neomnesis.common.db.element import Element
from neomnesis.note.note import Note, NoteDB
from neomnesis.task.task import Task, TaskDB
from neomnesis.server.config.config import NeoMnesisConfig

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

def parse_db_type(select_statement):
    #TODO : Make it better
    pattern = "({0})".format('|'.join(map(lambda k : k+"s",list(sub_db.keys()))))
    pattern = re.compile(pattern)
    match = re.findall(pattern,select_statement)
    if len(match) != 0:
        return match[0][:-1]
    return None


def perform_insert_element(element: Element):
    sub_db[element.class_id].insert(element)


def perform_delete_element(uuid: str, class_id: str):
    sub_db[class_id].delete_by_uuid(uuid)


def perform_modify_field_element(uuid: str, class_id: str, field, value):
    sub_db[class_id].modify(uuid, field, value)


def perform_select_elements(select_statement):
    try :
        class_id = parse_db_type(select_statement)
        result = sub_db[class_id].get_from_select(select_statement)
        return result
    except Exception as e :
        return pd.DataFrame([{"result" : str(e)}])

@app.route('/insert', methods=['POST'])
def insert_element():
    data = request.form
    element = ElementHandler.from_data(data)
    perform_insert_element(element)
    return 'OK'


@app.route('/delete_<class_id>', methods=['POST'])
def delete_element(class_id):
    uuid = request.form['_uuid']
    perform_delete_element(uuid,class_id)
    return 'OK'


@app.route('/modify_<class_id>', methods=['POST'])
def modify_element(class_id):
    data = request.form.to_dict()
    for key in ['value', 'field', '_uuid']:
        if not key in data:
            raise Exception()
    value = data['value']
    field = data['field']
    _uuid = data['_uuid']
    perform_modify_field_element(_uuid, class_id, field, value)
    return 'OK'


@app.route('/select', methods=['POST'])
def select_elements():
    select_statement = request.form['select_statement']
    res = perform_select_elements(select_statement)
    return res.to_json()


@app.route('/commit_<class_id>', methods=['POST'])
def commit(class_id):
    sub_db[class_id].commit()
    return 'OK'

@app.route('/cancel', methods=['POST'])
def cancel():
    tdb.rebase()
    ndb.rebase()
    return 'OK'

@app.route('/purge', methods=['POST'])
def purge():
    tdb.purge()
    ndb.purge()
    return 'OK'

if __name__ == '__main__' :
    app.run()
