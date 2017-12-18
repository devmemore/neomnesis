import sys, os, sqlite3
import pandas as pd
from pandasql import sqldf
import json
import uuid
from enum import Enum
from datetime import datetime, timedelta
from .config import NeoMnesisConfig

from typing import List, Dict

APP_NAME = "task"
TASK_TABLE = "tasks"
TASK_NAMESPACE_UUID = uuid.UUID(APP_NAME)


class Priority(Enum):
    deadly = 0
    critical = 1
    important = 2
    medium = 3
    normal = 4
    low = 5
    idle = 6

class Task:

    columns = ['title', 'descrition', 'priority', 'due_date', '_uuid', 'creation_date']

    def __init__(self, title, description: str, priority: int, due_date : datetime = None):
        self.title = title
        self.priority = priority
        self.description = description
        self._uuid = uuid.UUID(TASK_NAMESPACE_UUID, ' '.join([self.get_title(), self.get_description(), str(self.get_description())]))
        self.creation_date = datetime.now()
        self.due_date = due_date

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_title(self):
        return self.title

    def create_uuid(self):
        return uuid.UUID(TASK_NAMESPACE_UUID, ' '.join([self.get_title(), self.get_description(), str(self.get_description())]))

    def to_row(self):
        return self.__dict__


def has_no_modification_statement( statement : str ):
    return not any(list(map(lambda x : x in statement.upper(),['ALTER','DROP', 'INSERT', 'CREATE'])))

class TaskDB:
    def __init__(self, cfg : NeoMnesisConfig):
        self.cfg = cfg
        self.db_file = self.cfg.get_db_filename(APP_NAME)
        if not os.path.exists(self.db_file) :
            tmp_df = pd.DataFrame([],columns=Task.columns)

        conn = sqlite3.connect(self.db_file)
        self.conn = conn
        data_frame = pd.read_sql_query("select * from %s" % TASK_TABLE, conn)

    def insert_task(self,title, description, priority : int, due_date : datetime = None):
        task = Task(title, description, priority , due_date)
        self.data_frame.append(task.to_row())

    def delete_task_by_uuid(self, uuid):
        self.data_frame = self.data_frame[self.data_frame.uuid != uuid]

    def commit(self,):
        self.data_frame.to_sql(TASK_TABLE,self.conn, if_exists="replace")

    def get_task_from_select(self, select_statement):
        if has_no_modification_statement(select_statement):
            df_result = sqldf(select_statement,[self.data_frame])
        else :
            raise Exception()
        return df_result


