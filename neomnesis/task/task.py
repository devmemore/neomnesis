import uuid
from datetime import datetime
from enum import Enum

import pandas as pd
from dataclasses import dataclass
from typing import Dict

from neomnesis.common.constant import DATETIME_FORMAT
from neomnesis.common.db.data_base import PandasSQLDB
from neomnesis.common.db.element import Element
from neomnesis.server.config.config import NeoMnesisConfig

APP_NAME = "task"
APP_UUID = uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}')
TASK_TABLE = "task"
DATETIME_FORMAT = "%Y-Ym-%d %H:%M:%M"


class Priority(Enum):
    deadly = 0
    critical = 1
    important = 2
    medium = 3
    normal = 4
    low = 5
    idle = 6


@dataclass
class TaskRow:
    title: str
    priority: Priority
    description: str
    _uuid: uuid.UUID  # uuid.uuid5(APP_UUID, ' '.join([self.get_title(), self.get_description(), str(self.get_description())]))
    creation_date: datetime  # datetime.now()
    due_date: datetime  # due_date


class Task(Element):
    columns = dict([('title', str), ('description', str), ('priority', int), ('due_date', datetime), ('_uuid', str),
                    ('creation_date', datetime)])

    def __init__(self, title: str, description: str, priority: int, new_uuid: str, creation_date: datetime,
                 due_date: datetime = None):
        Element.__init__(self, 'task',new_uuid)
        self.title = title
        self.priority = priority
        self.description = description
        self.creation_date = creation_date
        self.due_date = due_date.strftime(DATETIME_FORMAT) if due_date is not None else ""

    @classmethod
    def new_task(cls, title, description, priority, due_date):
        my_uuid = str(
            uuid.uuid5(APP_UUID, ' '.join([title, description, str(priority), due_date.strftime(DATETIME_FORMAT)])))
        creation_date = datetime.now()
        return Task(title, description, priority, my_uuid, creation_date, due_date)

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_title(self):
        return self.title

    def create_uuid(self):
        return uuid.uuid5(APP_UUID, ' '.join([self.get_title(), self.get_description(), str(self.get_description())]))

    def to_row(self):
        return self.__dict__

    @classmethod
    def from_data(self, data: Dict):
        if 'class_id' in data :
            data_strict = data.copy()
            data_strict.pop('class_id')
            data_strict['creation_date'] = datetime.strptime(data_strict['creation_date'],DATETIME_FORMAT)
            data_strict['due_date'] = datetime.strptime(data_strict['due_date'],DATETIME_FORMAT)
            return Note(**data_strict)
        return Task(**data)


def has_no_modification_statement(statement: str):
    return not any(list(map(lambda x: x in statement.upper(), ['ALTER', 'DROP', 'INSERT', 'CREATE'])))


class TaskDB(PandasSQLDB):

    def __init__(self, cfg: NeoMnesisConfig):
        PandasSQLDB.__init__(self, cfg, APP_NAME, TASK_TABLE, Task)

    def insert_row(self, title, description, priority: int, due_date: datetime = None):
        task = Task(title, description, priority, due_date)
        self.data_frame = self.data_frame.append(pd.DataFrame([task.to_row()], columns=list(Task.columns.keys())))
        self.data_frame.to_sql(self.db_file, self.conn, index=False, if_exists="replace")
        self.commit_to_tmp()
