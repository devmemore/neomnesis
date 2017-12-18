from flask import Flask
from flask import request
app = Flask('task')

@app.route('/insert_task',methods=['POST'])
def insert_task():
    title = request['title']
    description = request['description']
    due_date = request['due_date']
    return 'Hello, World!'