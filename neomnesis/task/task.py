import os, sqlite3
import pandas as pd
import uuid
from enum import Enum
from datetime import datetime
from neomnesis.common.config import NeoMnesisConfig
from neomnesis.common.constant import DATETIME_FORMAT, SQLITE_TYPE_MAPPING
from typing import List
from neomnesis.common.db.data_base import PandasSQLDB

APP_NAME = "task"
TASK_TABLE = "task"



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
        self._uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, ' '.join([self.get_title(), self.get_description(), str(self.get_description()),"TASK"])))
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



class TaskDB(PandasSQLDB):

    def __init__(self, cfg : NeoMnesisConfig):
        PandasSQLDB.__init__(self,cfg,APP_NAME,TASK_TABLE,Task)

    def insert_task(self,task : Task):
        """
        Inserts a task to the taskDB's dataframe object and commit the changes on the df to the tmp task table
        :param task: a Task object
        :return:
        """
        self.insert_obj(task)

    def insert_tasks(self, tasks : List[Task]):
        """Inserts several tasks and then commit
        :param tasks: a list of Task objects
        """
        self.insert_objs(tasks)

    def modify_task(self,my_uuid,field : str,value):
        """
        Modifies a task of a given uuid, by setting a value for a specified field
        :param my_uuid: the uuid of the task as a string
        :param field: the field's name as a string
        :param value:
        :return: None
        """
        self.modify_obj(my_uuid,field,value)

    def insert_task_row(self,title, description, priority : int, due_date : datetime = None):
        task = Task(title, description, priority , due_date)
        self.data_frame = self.data_frame.append(pd.DataFrame([task.to_row()],columns=list(Task.columns.keys())))
        self.data_frame.to_sql(self.db_file, self.conn, index=False, if_exists="replace")
        self.commit_to_tmp()

    def delete_task_by_uuid(self, uuid : str):
        self.delete_obj_by_uuid(uuid)


    def get_all_tasks(self):
        return self.get_task_from_select('select * from task')

    def get_task_from_select(self, select_statement):
        """
        Performs a select (sql) statement on the temporary data base and returns the result
        :param select_statement:
        :return: dataframe result
        """
        return self.get_obj_from_select(select_statement)


