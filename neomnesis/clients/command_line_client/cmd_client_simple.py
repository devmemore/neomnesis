import os, sys
import requests
import cmd
import os
from subprocess import call
from neovim import attach
import neovim
import tempfile
import psutil
import time

from datetime import datetime
from neomnesis.common.db.element import Element
from neomnesis.clients.config.client_config import ClientConfig
from neomnesis.task.task import Task
from neomnesis.note.note import Note
from neomnesis.common.constant import DATETIME_FORMAT


LOCAL_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(LOCAL_DIR, 'cmd_client_config_local.cfg')

DATA_TYPE_MAPPING = {"note": Note, "task": Task}


class OperationHelper:

    @staticmethod
    def request_modify(server_url, class_id, uuid, field, value):
        url_command = server_url + '/modify_' + class_id
        result = requests.post(url_command, data={'_uuid': uuid, 'field': field, 'value': value})
        return result

    @staticmethod
    def request_insert(server_url, element: Element):
        url_command = server_url + '/insert'
        result = requests.post(url_command, data=element.to_row())
        return result

    @staticmethod
    def request_delete(server_url, class_id, uuid):
        url_command = server_url + '/delete_' + class_id
        result = requests.post(url_command, data={'_uuid': uuid})
        return result

    @staticmethod
    def request_select_statement(server_url, class_id, select_statement):
        url_command = server_url + '/select_' + class_id
        result = requests.post(url_command, data={'select_statement': select_statement})
        return result

def get_editor_pid(starting_time):
    nvim_candidate_processes = list(filter(lambda process : 
        'nvim' in process.name() and \
        process.create_time() >= starting_time and \
        process.parent().name() == 'gnome-terminal-server',
            psutil.process_iter()))
    if len(nvim_candidate_processes) == 1 :
        nvim_process = nvim_candidate_processes[0]
    elif len(nvim_candidate_processes) == 0 :
        nvim_process = None
    else :
        nvim_process = sorted(nvim_candidate_processes,key=lambda p : p.create_time())
    return nvim_process

class ElementBuilder(cmd.Cmd):

    def __init__(self, data_type, tmp_files, socket_url):
        cmd.Cmd.__init__(self)
        self.data_type = DATA_TYPE_MAPPING[data_type]
        self.data_element = dict()
        self.tmp_files = tmp_files
        self.socket_url = socket_url
        self.current_fieldname = None
        self.current_fieldtype = None

    def do_field(self, field_name):
        self.current_fieldname = field_name
        if field_name in self.data_type.editable:
            self.edit()

    def do_value(self, field_value):
        # TODO: implement custom exception for client
        try:
            field_type_parser = self.get_field_type(self.current_fieldname)
        except Exception as e:
            raise Exception(e)
        try:
            self.data_element[self.current_fieldname] = field_type_parser(field_value)
        except Exception as e:
            raise Exception(e)
        self.current_fieldname = None
        self.current_fieldtype = None

    def do_done(self):
        return self.data_type.new(**self.data_element)

    def get_field_type(self, field_name):
        return self.data_type.columns[field_name]

    def edit(self, nothing):
        # nvim = attach('child', argv=["/bin/env", "nvim", "--embed"])
        r = call(['nvim', self.tmp_file], shell=True)
        with open(self.tmp_file, 'r') as tmpfile:
            return tmpfile.read()

    def from_file_to_element(self, filepath) -> Element :
        with open(filepath,'r') as f :
            lines = f.read().splitlines()
            splitted_lines = map(lambda line : line.split('\t'), lines)
            splitted_lines = map(lambda line : (line[0],self.data_type.columns[line[0]](lines[1])), splitted_lines)
            dictified_data = dict(list(splitted_lines))  
            element = self.data_type.from_data(dictified_data)
            return element


    def initialize_element_file(self, filepath):
        with open(filepath,'w') as f :
            field_initializer='\n'.join(list(map(lambda colname : colname+'\t\t'+'#'+str(self.data_type.columns[colname]),
                self.data_type.columns.keys())))
            f.write(field_initializer)
            f.close()
    

    def do_edit_all(self, unused):
        print(unused)
        # nvim = attach('child', argv=["/usr/bin/env", "nvim"])
        if not os.path.isdir(os.path.dirname(self.tmp_files)):
            os.makedirs(os.path.dirname(self.tmp_files))

        tmp_file = tempfile.NamedTemporaryFile(prefix='tmp_element_building',dir=self.tmp_files,delete=False)
        self.initialize_element_file(tmp_file.name)
        #call(['gnome-terminal --full-screen -x nvim --listen {1} {0}'.format(tmp_file, self.socket_url)], shell=True)
        current_time = time.time()
        os.system('gnome-terminal --full-screen -x nvim --listen {1} {0}'.format(tmp_file, self.socket_url))
        nvim_process = get_editor_pid(current_time)
        psutil.wait()
        element = self.from_file_to_element(tmp_file.name)
        print(element.__dict___)
        # with open(self.tmp_file,'r') as tmpfile :
        #    return tmpfile.read()

    def define_field(self, field_type):
        if field_type == datetime:
            return lambda str_date: datetime.strptime(str_date, DATETIME_FORMAT)
        elif field_type in [int, str, float]:
            return lambda field_value: field_type(field_value)
        else:
            return lambda field_value: field_type(field_value)

    def do_exit(self):
        return None


class CommandLineClient(cmd.Cmd):

    def __init__(self, config_file):
        cmd.Cmd.__init__(self)
        self.intro = "Welcome to Neomnesis commandline client"
        self.prompt = "neomnesis_"+'\u039E'
        cfg = ClientConfig(config_file)
        self.server_url = cfg.cfg_parser.get('main', 'server_url')
        self.socket_url = cfg.cfg_parser.get('main', 'NVIM_LISTEN_ADDRESS')
        self.neomnesis_folder = cfg.cfg_parser.get('main', 'neomnesis_folder')
        self.tmp_files = os.path.join(self.neomnesis_folder,cfg.cfg_parser.get('main', 'tmp_files'))
        self.operation_list = list()
        if not os.path.isdir(self.neomnesis_folder):
            os.makedirs(self.neomnesis_folder)
        if not os.path.isdir(self.tmp_files):
            os.makedirs(self.tmp_files)


    def do_create(self, data_type):
        if data_type in ['note', 'task']:
            elem_builder = ElementBuilder(data_type, self.tmp_files, self.socket_url)
            elem_builder.prompt = self.prompt[:-1] + 'create '
            new_note = elem_builder.cmdloop()
            print('a new {0} is born'.format(data_type))
        else:
            print('/!\ Unknown data type {0}'.format(data_type))

    def do_query(self, select_statement):
        result = OperationHelper.request_select_statement(self.server_url, select_statement)
        print(result)

    def do_cancel(self):
        pass

    def do_cancel_all(self):
        pass

    def do_exit(self):
        return True


if __name__ == '__main__':
    cmd_line_client = CommandLineClient(CONFIG_FILE)
    cmd_line_client.cmdloop()
