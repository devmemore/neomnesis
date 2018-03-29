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
from subprocess import call


DATA_TYPE_MAPPING = {"note" : Note, "task" : Task}


class OperationHelper:

    @classmethod
    def request_modify(cls, server_url, class_id, uuid, field, value):
        url_command = server_url + '/modify_' + class_id
        result = requests.post(url_command, data={'_uuid' : uuid, 'field' : field, 'value' : value})
        return result

    @classmethod
    def request_insert(cls, server_url, element : Element):
        url_command = server_url + '/insert'
        result = requests.post(url_command, data=element.to_row())
        return result

    @classmethod
    def request_delete(cls, server_url, class_id, uuid):
        url_command = server_url + '/delete_' + class_id
        result = requests.post(url_command, data={'_uuid' : uuid})
        return result

    @classmethod
    def request_select_statement(cls, server_url, class_id, select_statement):
        url_command = server_url + '/select_' + class_id
        result = requests.post(url_command, data={'select_statement' : select_statement})
        return result


class ElementBuilder(cmd.Cmd):

    def __init__(self, data_type):
        cmd.Cmd(self)
        self.data_type = DATA_TYPE_MAPPING[data_type]

    def do_field(self,field_name):
        pass


    def define_field(self,field_type):
        if field_type == datetime :
            pass


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
            print('a new task')



    def edit(self):
        r = call(['vim',self.tmp_file],shell=True)
        with open(self.tmp_file,'r') as tmpfile :
            return tmpfile.read()

if __name__ == '__main__' :
    cmd_line_client = CommandLineClient('/home/thomas/Projects/Gits/neomnesis/configs/cmd_client_config_local.cfg')
    cmd_line_client.cmdloop()
    
