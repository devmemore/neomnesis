import uuid
from datetime import datetime
from enum import Enum

import pandas as pd
from dataclasses import dataclass
from typing import Dict

from neomnesis.common.constant import DATETIME_FORMAT, DATETIME_NANO_PRECISION_FORMAT
from neomnesis.common.db.data_base import PandasSQLDB
from neomnesis.common.db.element import Element
from neomnesis.server.config.config import NeoMnesisConfig
from neomnesis.common.data_type.date import DateHour
from werkzeug.datastructures import MultiDict

APP_NAME = "task"
APP_UUID = uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}')
TASK_TABLE = "tasks"


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
    on_creation_columns = dict([('creation_date', datetime)],**Element.on_creation_columns)
    columns = dict(Element.columns,
                   **dict([('title', str), ('description', str), ('priority', int), ('due_date', DateHour)],
                   **on_creation_columns))
    

    def __init__(self, title: str, description: str, priority: int, _uuid: str, creation_date: datetime,
                 due_date: DateHour):
        Element.__init__(self, 'task', _uuid)
        self.title = title
        self.priority = priority
        self.description = description
        self.creation_date = creation_date
        self.due_date = due_date

    @classmethod
    def new(cls, title, description, priority, due_date : DateHour):
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

    @classmethod
    def from_data(self, data: MultiDict):
        if 'class_id' in data :
            data_strict = data.copy().to_dict()
            data_strict.pop('class_id')
            data_strict['creation_date'] = datetime.strptime(data_strict['creation_date'],DATETIME_NANO_PRECISION_FORMAT)
            data_strict['due_date'] = DateHour(data_strict['due_date'])
            return Task(**data_strict)
        return Task.new(**data)


def has_no_modification_statement(statement: str):
    return not any(list(map(lambda x: x in statement.upper(), ['ALTER', 'DROP', 'INSERT', 'CREATE'])))


class TaskDB(PandasSQLDB):

    def __init__(self, cfg: NeoMnesisConfig):
        PandasSQLDB.__init__(self, cfg, TASK_TABLE, Task)

    def insert_row(self, title, description, priority: int, due_date: datetime = None):
        task = Task.new(title, description, priority, due_date)
        self.data_frame = self.data_frame.append(pd.DataFrame([task.to_row()], columns=list(Task.columns.keys())))
        with self.create_cursor() as conn :
            self.data_frame.to_sql(self.db_file, conn, index=False, if_exists="replace")
        self.commit_to_tmp()
