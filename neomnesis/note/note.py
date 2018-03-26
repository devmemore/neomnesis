from __future__ import dataclasses
from datetime import datetime
import uuid
from common.config import NeoMnesisConfig
import sqlite3
import pandas as pd
import os

from neomnesis.common.constant import DATETIME_FORMAT, SQLITE_TYPE_MAPPING
from neomnesis.common.db.data_base import PandasSQLDB

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
    _uuid : UUID
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


    def insert_note(self, note : Note):
        """
        Inserts a note to the noteDB's dataframe object and commit the changes on the df to the tmp note table
        :param note: a Note object
        :return:
        """
        self.insert_obj(note)

    def insert_notes(self, notes : List[Note]):
        """Inserts several notes and then commit
        :param notes: a list of Note objects
        """
        self.insert_objs(notes)

    def modify_note(self,my_uuid,field : str,value):
        """
        Modifies a note of a given uuid, by setting a value for a specified field
        :param my_uuid: the uuid of the note as a string
        :param field: the field's name as a string
        :param value:
        :return: None
        """
        self.modify_obj(my_uuid,field,value)

    def insert_note_row(self,title, content):
        note = Note(title,content)
        self.data_frame = self.data_frame.append(pd.DataFrame([note.to_row()],columns=list(Note.columns.keys())))
        self.data_frame.to_sql(self.db_file, self.conn, index=False, if_exists="replace")
        self.commit_to_tmp()

    def delete_note_by_uuid(self, uuid : str):
        self.delete_obj_by_uuid(uuid)


    def get_all_notes(self):
        return self.get_note_from_select('select * from {0}'.format(self.table_name))

    def get_note_from_select(self, select_statement):
        """
        Performs a select (sql) statement on the temporary data base and returns the result
        :param select_statement:
        :return: dataframe result
        """
        return self.get_obj_from_select(select_statement)

