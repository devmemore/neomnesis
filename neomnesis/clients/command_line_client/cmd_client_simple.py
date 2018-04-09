import os, sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..','..'))


import requests
import cmd
from datetime import datetime
from neomnesis.common.db.element import Element
from neomnesis.clients.config.client_config import ClientConfig
from neomnesis.task.task import Task
from neomnesis.note.note import Note
from neomnesis.common.constant import DATETIME_FORMAT
from subprocess import call
from neovim import attach
import neovim


LOCAL_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(LOCAL_DIR, 'cmd_client_config_local.cfg')

DATA_TYPE_MAPPING = {"note" : Note, "task" : Task}


class OperationHelper:

    @staticmethod
    def request_modify(server_url, class_id, uuid, field, value):
        url_command = server_url + '/modify_' + class_id
        result = requests.post(url_command, data={'_uuid' : uuid, 'field' : field, 'value' : value})
        return result

    @staticmethod
    def request_insert(server_url, element : Element):
        url_command = server_url + '/insert'
        result = requests.post(url_command, data=element.to_row())
        return result

    @staticmethod
    def request_delete(server_url, class_id, uuid):
        url_command = server_url + '/delete_' + class_id
        result = requests.post(url_command, data={'_uuid' : uuid})
        return result

    @staticmethod
    def request_select_statement(server_url, class_id, select_statement):
        url_command = server_url + '/select_' + class_id
        result = requests.post(url_command, data={'select_statement' : select_statement})
        return result


class ElementBuilder(cmd.Cmd):

    def __init__(self, data_type):
        cmd.Cmd.__init__(self)
        self.data_type = DATA_TYPE_MAPPING[data_type]
        self.data_element = dict()
        self.current_fieldname = None
        self.current_fieldtype = None

    def do_field(self,field_name):
        self.current_fieldname = field_name
        if field_name in self.data_type.editable
            self.edit()

    def do_value(self,field_value):
        # TODO: implement custom exception for client
        try :
            field_type_parser = self.get_field_type(self.current_fieldname)
        except Exception as e:
            raise Exception(e)
        try :
            self.data_element[self.current_fieldname] = field_type_parser(field_value)
        except Exception as e:
            raise Exception(e)
        self.current_fieldname = None
        self.current_fieldtype = None

    def do_done(self):
        return self.data_type.new(**self.data_element)

    def do_cancel(self):
        pass

    def do_cancel_all(self):
        pass

    def get_field_type(self,field_name):
        return self.data_type.columns[field_name]

    def edit(self):
        #nvim = attach('child', argv=["/bin/env", "nvim", "--embed"])
        r = call(['nvim',self.tmp_file],shell=True)
        with open(self.tmp_file,'r') as tmpfile :
            return tmpfile.read()

    def define_field(self,field_type):
        if field_type == datetime :
            return lambda str_date : datetime.strptime(str_date, DATETIME_FORMAT)
        elif field_type in [int,str,float]:
            return lambda field_value : field_type(field_value)
        else :
            return lambda field_value : field_type(field_value)


class CommandLineClient(cmd.Cmd):

    def __init__(self, config_file):
        cmd.Cmd.__init__(self)
        self.intro = "Welcome to Neomnesis commandline client"
        self.prompt = "neomnesis_£ "
        cfg = ClientConfig(config_file)
        self.tmp_file = cfg.cfg_parser.get('main','tmp_file')
        self.server_url = cfg.cfg_parser.get('main','server_url')

    def do_create(self, data_type):
        if data_type == 'note' :
            elem_builder = ElementBuilder(data_type)
            elem_builder.prompt = self.prompt[:-1] + ElementBuilder.prompt
            print('a new note')
        elif data_type == 'task' :
            elem_builder = ElementBuilder(data_type)
            elem_builder.prompt = self.prompt[:-1] + ElementBuilder.prompt
            print('a new task')

    def do_query(self, select_statement):
        result = OperationHelper.request_select_statement(self.server_url, select_statement)
        print(result)



if __name__ == '__main__' :
    cmd_line_client = CommandLineClient(CONFIG_FILE)
    cmd_line_client.cmdloop()
