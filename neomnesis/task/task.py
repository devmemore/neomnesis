import sys, os, sqlite3
import pandas as pd
from pandasql import sqldf
import json
import uuid
from enum import Enum
from datetime import datetime, timedelta
from config import NeoMnesisConfig

from typing import List, Dict

APP_NAME = "task"
TASK_TABLE = "task"

SQLITE_TYPE_MAPPING = {str : 'text',
                       int : 'real',
                       datetime : 'text'}

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Priority(Enum):
    deadly = 0
    critical = 1
    important = 2
    medium = 3
    normal = 4
    low = 5
    idle = 6

class Task:

    columns = dict([('title',str), ('description',str), ('priority',int), ('due_date',datetime), ('_uuid',str), ('creation_date',datetime)])

    def __init__(self, title, description: str, priority: int, due_date : datetime = None):
        self.title = title
        self.priority = priority
        self.description = description
        self._uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, ' '.join([self.get_title(), self.get_description(), str(self.get_description())])))
        self.creation_date = datetime.now().strftime(DATETIME_FORMAT)
        self.due_date = due_date.strftime(DATETIME_FORMAT)

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_title(self):
        return self.title

    def create_uuid(self):
        return uuid.uuid3(uuid.NAMESPACE_DNS, ' '.join([self.get_title(), self.get_description(), str(self.get_description())]))

    def to_row(self):
        return self.__dict__


def has_no_modification_statement( statement : str ):
    return not any(list(map(lambda x : x in statement.upper(),['ALTER','DROP', 'INSERT', 'CREATE'])))

class TaskDB:

    def __init__(self, cfg : NeoMnesisConfig):
        self.cfg = cfg
        self.db_file = self.cfg.get_db_filename(APP_NAME)
        self.tmp_db_file = self.cfg.get_tmp_db_filename(APP_NAME)
        if not os.path.exists(os.path.dirname(self.db_file)):
            os.makedirs(os.path.dirname(self.db_file))
        conn = sqlite3.connect(self.db_file)
        tmp_conn = sqlite3.connect(self.tmp_db_file)
        sqlite_cols = ', '.join(list(map(lambda col : col+' '+SQLITE_TYPE_MAPPING[Task.columns[col]], Task.columns)))
        conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (TASK_TABLE,sqlite_cols))
        tmp_conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (TASK_TABLE,sqlite_cols))
        self.conn = conn
        self.tmp_conn = tmp_conn
        self.data_frame = pd.read_sql_query("SELECT * FROM %s" % TASK_TABLE, conn, index_col=None)
        self.data_frame.to_sql(TASK_TABLE,self.tmp_conn, if_exists="replace")

    def commit_to_tmp(self):
        self.data_frame.to_sql(TASK_TABLE, self.tmp_conn, if_exists="replace")

    def insert_task(self,task : Task):
        self.data_frame = self.data_frame.append(pd.DataFrame([task.to_row()],columns=list(Task.columns.keys())))
        self.commit_to_tmp()

    def insert_tasks(self, tasks : List[Task]):
        self.data_frame = self.data_frame.append(pd.DataFrame(list(map(lambda task : task.to_row(),tasks)),columns=list(Task.columns.keys())))
        self.commit_to_tmp()

    def modify_task(self,my_uuid,field,value):
        self.data_frame.loc[self.data_frame['_uuid'] == my_uuid,field] = value
        self.commit_to_tmp()

    def insert_task_row(self,title, description, priority : int, due_date : datetime = None):
        task = Task(title, description, priority , due_date)
        self.data_frame = self.data_frame.append(pd.DataFrame([task.to_row()],columns=list(Task.columns.keys())))
        self.data_frame.to_sql(self.db_file, self.conn, index=False, if_exists="replace")
        self.commit_to_tmp()

    def delete_task_by_uuid(self, uuid : str):
        self.data_frame = self.data_frame[self.data_frame._uuid != uuid]
        self.commit_to_tmp()

    def commit(self,):
        self.data_frame.to_sql(TASK_TABLE, self.conn, if_exists="replace", index=False)

    def purge(self):
        self.data_frame = pd.DataFrame([], columns=list(Task.columns.keys()))
        self.commit_to_tmp()
        self.commit()

    def get_all_tasks(self):
        return self.get_task_from_select('select * from task')


    def get_task_from_select(self, select_statement):
        if has_no_modification_statement(select_statement):
            df_result = pd.read_sql_query(select_statement,self.tmp_conn)
        else :
            raise Exception()
        return df_result


