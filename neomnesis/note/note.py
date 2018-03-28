from __future__ import dataclasses
from datetime import datetime
import uuid
from common.config import NeoMnesisConfig
import sqlite3
import pandas as pd
import os

from neomnesis.common.constant import DATETIME_FORMAT, SQLITE_TYPE_MAPPING
from neomnesis.common.db.data_base import PandasSQLDB
from neomnesis.common.db.element import Element 

from typing import List

APP_NAME='note'
NOTE_TABLE='notes'


class Note:

    columns = dict([('title',str), ('content',str), ('last_modification_date',datetime), ('_uuid',str), ('creation_date',datetime)])

    def __init__(self, title : str, content : str):
        self.title = title
        self.content = content
        self.creation_date = datetime.now().strftime(DATETIME_FORMAT)
        self._uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, ' '.join([self.title, self.creation_date])))
        self.last_modification_date = datetime.now().strftime(DATETIME_FORMAT)

    def to_row(self):
        return self.__dict__

    def get_tags(self):
        # TODO : To implement, Lucene ?
        pass

@dataclass
class NoteRow:
    title : str
    content : str
    creation_date : datetime
    _uuid : uuid.UUID
    last_modification_date : datetime


class NoteDB(PandasSQLDB):

    def __init__(self, cfg : NeoMnesisConfig):
        PandasSQLDB.__init__(cfg, APP_NAME, NOTE_TABLE, Note)

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

