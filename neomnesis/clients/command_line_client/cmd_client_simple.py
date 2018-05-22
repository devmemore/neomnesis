import os, sys
import cmd
import os
from subprocess import call
from neovim import attach
import neovim
import tempfile
import psutil
import time
import pandas as pd

from datetime import datetime
from neomnesis.common.db.element import Element
from neomnesis.clients.config.client_config import ClientConfig
from neomnesis.task.task import Task
from neomnesis.note.note import Note
from neomnesis.common.constant import DATETIME_FORMAT
from neomnesis.common.data_type.text import Text
from neomnesis.clients.common.operation_helper import OperationHelper

from typing import Dict


LOCAL_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(LOCAL_DIR, 'cmd_client_config_local.cfg')

DATA_TYPE_MAPPING = {"note": Note, "task": Task}




def get_editor_pid(starting_time):
    nvim_candidate_processes = list(filter(lambda process : 
        'nvim' in process.name() and \
        process.create_time() >= starting_time and \
        process.parent().name() == 'gnome-terminal-server',
            psutil.process_iter()))
    if len(nvim_candidate_processes) == 1 :
        nvim_process = nvim_candidate_processes[0]
    elif len(nvim_candidate_processes) == 0 :
        print("no editor found")
        nvim_process = None
    else :
        nvim_process = sorted(nvim_candidate_processes,key=lambda p : p.create_time())
    return nvim_process


def edit_in_nvim(wkdirectory, initializer):
    if not os.path.isdir(os.path.dirname(wkdirectory)):
        os.makedirs(os.path.dirname(wkdirectory))

    tmp_file = tempfile.NamedTemporaryFile(prefix='tmp_element_building',dir=wkdirectory,delete=False)
    initializer(tmp_file.name)
    #call(['gnome-terminal --full-screen -x nvim --listen {1} {0}'.format(tmp_file, self.socket_url)], shell=True)
    current_time = time.time()
    os.system('gnome-terminal --full-screen -x nvim {0}'.format(
        os.path.join(wkdirectory,tmp_file.name))
        )

    nvim_process = get_editor_pid(current_time)
    nvim_process.wait()
    with open(os.path.join(wkdirectory,tmp_file.name),'r') as f :
        return f.read()
    return None 



class ElementModifier(cmd.Cmd):
    
    QUERY_TEMPLATE="select * from {0} where uuid = '{1}'"

    def __init__(self, data_type, tmp_files, _uuid, server_url):
        cmd.Cmd.__init__(self)
        self.data_type = DATA_TYPE_MAPPING[data_type]
        request_json_result = OperationHelper.request_select_statement(self.server_url, QUERY_TEMPLATE.format(self.data_type, self._uuid))
        df_request_result = pd.read_json(request_result) 
        if df_request_result.shape[0] != 1 :
            print("number of rows : {0} for uuid {1}".format(df_request_result.shape[0]),
                                                             _uuid)
        self.past_data_element = df_request_result.iloc[0].to_dict()
        self.current_data_element = self.past_data_element 
        self.tmp_files = tmp_files
        self._uuid = _uuid
        self.server_url = server_url

    def do_done(self, unused):
        for colname in self.current_data_element :
            if self.current_data_element[colname] != self.past_data_element[colname] :
                res = OperationHelper.request_modify(self.server_url, self.data_type.class_id, _uuid, colname, self.current_data_element[colname])
                print("modify {0} is {1}".format(colname,res))

    def do_get_state(self,unused):
        print(self.cuurent_data_element)

    def do_edit_field(self, fieldname, value=None):
        if fieldname in self.data_type.columns :
            if type(self.data_type.columns[fieldname]) is Text and value == None :
                tmp_value = edit_in_nvim(self.tmp_files)
                if tmp_value != None :
                    value = tmp_value
            elif value == None :
                print("No value given and field is not a Text")
            else :    
                self.data_element[fieldname] = self.data_type.columns[fieldname](value)

    def initialize_element_file(self, filepath):
        with open(filepath,'w') as f :
            field_initializer='\n'.join(
                    list(map(lambda colname : colname+'\t'+str(self.current_data_element[colname])+'\t'+'#'+str(self.data_type.columns[colname]),
                [col for col in self.data_type.columns.keys() if not col in self.data_type.on_creation_columns.keys()])))
            f.write(field_initializer)
            f.close()

    def parse_data(self, data_str) -> Dict :
            lines = data_str.splitlines()
            splitted_lines = list(map(lambda line : line.split('\t'), lines))
            splitted_lines = list(map(lambda line : (line[0],self.data_type.columns[line[0]](line[1])), splitted_lines))
            dictified_data = dict(list(splitted_lines))
            return dictified_data

    def do_edit_all(self, unused):
        print(unused)
        if not os.path.isdir(os.path.dirname(self.tmp_files)):
            os.makedirs(os.path.dirname(self.tmp_files))
        current_time = time.time()
        data_str = edit_in_nvim(self.tmp_files, self.initialize_element_file)
        self.current_data_element = self.parse_data(data_str)

    def exit(self):
        return None


class ElementBuilder(cmd.Cmd):

    def __init__(self, data_type, tmp_files, server_url):
        cmd.Cmd.__init__(self)
        self.data_type = DATA_TYPE_MAPPING[data_type]
        self.data_element = dict()
        self.server_url = server_url
        self.tmp_files = tmp_files

    def do_done(self, unused):
        new_element = self.data_type.new(**self.data_element)
        print('a new {0} is born'.format(new_element.class_id))
        inserted = OperationHelper.request_insert(self.server_url, new_element)
        print('insertion of {0} is {1}'.format(new_element._uuid, inserted))
        return True 

    def do_get_state(self,unused):
        print(self.data_element)


    def do_edit_field(self, fieldname, value=None):
        if fieldname in self.data_type.columns :
            if type(self.data_type.columns[fieldname]) is Text and value == None :
                tmp_value = edit_in_nvim(self.tmp_files)
                if tmp_value != None :
                    value = tmp_value
            elif value == None :
                print("No value given and field is not a Text")
            else :    
                self.data_element[fieldname] = self.data_type.columns[fieldname](value)
          
    def do_edit_all(self, unused):
        print(unused)
        if not os.path.isdir(os.path.dirname(self.tmp_files)):
            os.makedirs(os.path.dirname(self.tmp_files))
        current_time = time.time()
        data_str = edit_in_nvim(self.tmp_files, self.initialize_element_file)
        nvim_process = get_editor_pid(current_time)
        nvim_process.wait()
        self.data_element = self.parse_data(data_str)

    def parse_data(self, data_str) -> Dict :
            lines = data_str.splitlines()
            splitted_lines = list(map(lambda line : line.split('\t'), lines))
            splitted_lines = list(map(lambda line : (line[0],self.data_type.columns[line[0]](line[1])), splitted_lines))
            dictified_data = dict(list(splitted_lines))
            return dictified_data

    def initialize_element_file(self, filepath):
        with open(filepath,'w') as f :
            field_initializer='\n'.join(
                    list(map(lambda colname : colname+'\t\t'+'#'+str(self.data_type.columns[colname]),
                [col for col in self.data_type.columns.keys() if not col in self.data_type.on_creation_columns.keys() ])))
            f.write(field_initializer)
            f.close()

    def do_edit_all(self, unused):
        print(unused)
        # nvim = attach('child', argv=["/usr/bin/env", "nvim"])
        if not os.path.isdir(os.path.dirname(self.tmp_files)):
            os.makedirs(os.path.dirname(self.tmp_files))
        #call(['gnome-terminal --full-screen -x nvim --listen {1} {0}'.format(tmp_file, self.socket_url)], shell=True)
        current_time = time.time()
        data_str = edit_in_nvim(self.tmp_files, self.initialize_element_file)
        self.data_element = self.parse_data(data_str)

    def do_exit(self):
        return None


class CommandLineClient(cmd.Cmd):

    def __init__(self, config_file):
        cmd.Cmd.__init__(self)
        self.intro = "Welcome to Neomnesis commandline client"
        self.prompt = "neomnesis_"+'\u039E' + " "
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
            elem_builder = ElementBuilder(data_type, self.tmp_files, self.server_url)
            elem_builder.prompt = self.prompt[:-1] + 'create_'+ '\u039E' + " "
            new_element = elem_builder.cmdloop()
        else:
            print('/!\ Unknown data type {0}'.format(data_type))
            print("Known data types are "+' '.join(['note','task']))

    def do_query(self, select_statement):
        result_json = OperationHelper.request_select_statement(self.server_url, select_statement)
        print(result_json.text)
        result = pd.read_json(result_json.text)
        print(result)

    def do_cancel(self,arg):
        OperationHelper.request_cancel(self.server_url) 

    def do_modify(self,arg):
        data_type, _uuid = arg
        if data_type in ['note', 'task']:
            elem_modifier = ElemModifier(data_type, self.tmp_files, _uuid, self.server_url)
            elem_modifier.prompt = self.prompt[:-1] + 'modify_'+ '\u039E' + " "
            elem_modify.cmdloop()
        else:
            print('/!\ Unknown data type {0}'.format(data_type))
            print("Known data types are "+' '.join(['note','task']))

    def do_commit(self):
        OperationHelper.request_commit(self.server_url) 

    def do_purge(self):
        answer = None
        while answer not in ["Y","n"] :
            answer = input("Are you sure you want to purge everything ? Y/n")
        if answer == "n":
            print("I guess you were joking") 
        else :
            OperationHelper.request_purge(self.server_url) 

    def do_cancel_all(self):
        OperationHelper.request_cancel(self.server_url) 
        pass

    def do_exit(self):
        return True


if __name__ == '__main__':
    cmd_line_client = CommandLineClient(CONFIG_FILE)
    cmd_line_client.cmdloop()
