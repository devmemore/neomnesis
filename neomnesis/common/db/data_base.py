import os
import sqlite3

import pandas as pd
from typing import List

from neomnesis.common.constant import SQLITE_TYPE_MAPPING
from neomnesis.common.db.element import Element
from neomnesis.server.config.config import NeoMnesisConfig


def has_no_modification_statement( statement : str ):
    return not any(list(map(lambda x : x in statement.upper(),['ALTER','DROP', 'INSERT', 'CREATE'])))

class PandasSQLDB:

    def __init__(self, cfg : NeoMnesisConfig, app_name : str, table_name: str, class_obj):
        self.cfg = cfg
        self.app_name = app_name
        self.table_name = table_name
        self.class_obj = class_obj
        self.db_file = self.cfg.get_db_filename(app_name)
        self.tmp_db_file = self.cfg.get_tmp_db_filename(app_name)
        if not os.path.exists(os.path.dirname(self.db_file)):
            os.makedirs(os.path.dirname(self.db_file))
        conn = sqlite3.connect(self.db_file)
        tmp_conn = sqlite3.connect(self.tmp_db_file)
        sqlite_cols = ', '.join(list(map(lambda col : col+' '+SQLITE_TYPE_MAPPING[class_obj.columns[col]], class_obj.columns)))
        conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (table_name,sqlite_cols))
        tmp_conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (table_name,sqlite_cols))
        self.conn = conn
        self.tmp_conn = tmp_conn
        self.data_frame = pd.read_sql_query("SELECT * FROM %s" % table_name, conn, index_col=None)
        self.data_frame.to_sql(table_name,self.tmp_conn, if_exists="replace")

    def commit_to_tmp(self):
        """
        commit changes to a tmp object table
        :return: None
        """
        self.data_frame.to_sql(self.table_name, self.tmp_conn, if_exists="replace")

    def insert(self,obj : Element):
        """
        Inserts a object to the objectDB's dataframe object and commit the changes on the df to the tmp object table
        :param object: a class_obj object
        :return:
        """
        self.data_frame = self.data_frame.append(pd.DataFrame([obj.to_row()],columns=list(self.class_obj.columns.keys())))
        self.commit_to_tmp()

    def insert_list(self, obj_list : List[Element]):
        """Inserts several objects and then commit
        :param objects: a list of class_obj objects
        """
        self.data_frame = self.data_frame.append(pd.DataFrame(list(map(lambda object : object.to_row(),obj_list)),
                                                              columns=list(self.class_obj.columns.keys())))
        self.commit_to_tmp()

    def modify(self,my_uuid,field : str,value):
        """
        Modifies a object of a given uuid, by setting a value for a specified field
        :param my_uuid: the uuid of the object as a string
        :param field: the field's name as a string
        :param value:
        :return: None
        """
        self.data_frame.loc[self.data_frame['_uuid'] == my_uuid,field] = value
        self.commit_to_tmp()


    def delete_by_uuid(self, uuid : str):
        self.data_frame = self.data_frame[self.data_frame._uuid != uuid]
        self.commit_to_tmp()

    def commit(self,):
        self.data_frame.to_sql(self.table_name, self.conn, if_exists="replace", index=False)

    def purge(self):
        self.data_frame = pd.DataFrame([], columns=list(self.class_obj.columns.keys()))
        self.commit_to_tmp()
        self.commit()

    def get_all(self):
        return self.get_from_select('select * from {0}'.format(self.table_name))


    def get_from_select(self, select_statement):
        """
        Performs a select (sql) statement on the temporary data base and returns the result
        :param select_statement:
        :return: dataframe result
        """
        if has_no_modification_statement(select_statement):
            df_result = pd.read_sql_query(select_statement,self.tmp_conn)
        else :
            raise Exception()
        return df_result

    def rebase(self):
        self.data_frame = pd.read_sql_query("select * from {0}".format(self.table_name), self.conn)
        self.commit_to_tmp()
