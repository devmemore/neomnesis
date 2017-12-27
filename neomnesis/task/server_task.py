from flask import Flask, current_app
from flask import request
import os
from task.task import Task, TaskDB, NeoMnesisConfig
local_dir = os.path.dirname(__file__)
cfg_path = os.path.join(local_dir,'..','..','config.cfg')


app = Flask('task')

cfg = NeoMnesisConfig(cfg_path)
tdb = TaskDB(cfg)


@app.route('/insert_task',methods=['POST'])
def insert_task():
    request_prop = dict([(prop, request[prop]) for prop in Task.columns.keys()])
    title = request_prop['title']
    description = request_prop['description']
    priority = request_prop['priority']
    due_date = request_prop['due_date']
    task = Task(title,description,priority,due_date)
    tdb.insert_task(task)
    return 'Hello, World!'


@app.route('/delete_task',methods=['POST'])
def delete_task():
    uuid = request['uuid']
    tdb.delete_task_by_uuid(uuid)


@app.route('/commit',methods=['POST'])
def commit():
    tdb.commit()



