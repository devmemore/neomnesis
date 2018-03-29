import os
import sqlite3
import uuid
from datetime import datetime
from dataclasses import dataclass

import pandas as pd
from typing import Dict

from neomnesis.common.constant import DATETIME_FORMAT, SQLITE_TYPE_MAPPING
from neomnesis.common.db.data_base import PandasSQLDB
from neomnesis.common.db.element import Element
from neomnesis.server.config.config import NeoMnesisConfig
from werkzeug.datastructures import MultiDict

APP_NAME='note'
NOTE_TABLE='notes'


class Note(Element):

    columns = Element.columns.copy().update(dict([('title',str), ('content',str), ('last_modification_date',datetime), ('_uuid',str), ('creation_date',datetime)]))

    def __init__(self,_uuid, title : str, content : str, creation_date : datetime, last_modification_date : datetime):
        Element.__init__(self,"note",_uuid)
        self.title = title
        self.content = content
        self.creation_date = creation_date.strftime(DATETIME_FORMAT)
        self.last_modification_date = last_modification_date.strftime(DATETIME_FORMAT)

    @classmethod
    def new_note(self, title, content):
        creation_date = datetime.now()
        _uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, ' '.join([title, creation_date.strftime(DATETIME_FORMAT),str(creation_date.time().microsecond)])))
        return Note(_uuid, title, content, creation_date, creation_date)

    def to_row(self):
        return self.__dict__

    def get_tags(self):
        # TODO : To implement, Lucene ?
        pass

    @classmethod
    def from_data(self, data : MultiDict):
        if 'class_id' in data :
            data_strict = data.copy().to_dict()
            data_strict.pop('class_id')
            data_strict['creation_date'] = datetime.strptime(data_strict['creation_date'],DATETIME_FORMAT)
            data_strict['last_modification_date'] = datetime.strptime(data_strict['last_modification_date'],DATETIME_FORMAT)
            return Note(**data_strict)
        return Note(**data)

@dataclass
class NoteRow:
    title : str
    content : str
    creation_date : datetime
    _uuid : uuid.UUID
    last_modification_date : datetime


class NoteDB(PandasSQLDB):

    def __init__(self, cfg : NeoMnesisConfig):
        PandasSQLDB.__init__(self,cfg, APP_NAME, NOTE_TABLE, Note)

        self.db_file = self.cfg.get_db_filename(APP_NAME)
        self.tmp_db_file = self.cfg.get_tmp_db_filename(APP_NAME)
        if not os.path.exists(os.path.dirname(self.db_file)):
            os.makedirs(os.path.dirname(self.db_file))
        conn = sqlite3.connect(self.db_file)
        tmp_conn = sqlite3.connect(self.tmp_db_file)
        sqlite_cols = ', '.join(list(map(lambda col : col+' '+SQLITE_TYPE_MAPPING[Note.columns[col]], Note.columns)))
        conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (NOTE_TABLE,sqlite_cols))
        tmp_conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (NOTE_TABLE,sqlite_cols))
        self.conn = conn
        self.tmp_conn = tmp_conn
        self.data_frame = pd.read_sql_query("SELECT * FROM %s" % NOTE_TABLE, conn, index_col=None)
        self.data_frame.to_sql(NOTE_TABLE,self.tmp_conn, if_exists="replace")

