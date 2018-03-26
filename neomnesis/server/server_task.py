import os
from flask import Flask
from flask import request
from neomnesis.task.task import Task, TaskDB, NeoMnesisConfig

local_dir = os.path.dirname(__file__)
cfg_path = os.path.join(local_dir,'..','..','config.cfg')


app = Flask('task')

cfg = NeoMnesisConfig(cfg_path)
tdb = TaskDB(cfg)


@app.route('/insert_task',methods=['POST'])
def insert_task():
    request_prop = dict([(prop, request.form[prop]) for prop in Task.columns.keys()])
    title = request_prop['title']
    description = request_prop['description']
    priority = request_prop['priority']
    due_date = request_prop['due_date']
    task = Task(title,description,priority,due_date)
    tdb.insert(task)
    return 'Hello, World!'


@app.route('/delete_task',methods=['POST'])
def delete_task():
    uuid = request['uuid']
    tdb.delete_by_uuid(uuid)


@app.route('/modify_task',methods=['POST'])
def modify_task():
    for key in ['value','field','uuid']:
        if not key in request :
            raise Exception()
    value = request['value']
    field = request['field']
    _uuid = request['uuid']
    tdb.modify(_uuid,field,value)


@app.route('/select_tasks',methods=['POST'])
def select_tasks():
    if not 'select_statement':
        raise Exception()
    select_statement = request['select_statement']
    res = tdb.get_from_select(select_statement)
    return res


@app.route('/commit',methods=['POST'])
def commit():
    tdb.commit()



