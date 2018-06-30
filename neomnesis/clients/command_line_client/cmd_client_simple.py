import os, sys
import cmd
import os
import re
from subprocess import call
from neovim import attach
import neovim
import tempfile
import psutil
import time
import pandas as pd
from functools import partial
import json

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
    """
    Returns the pid of the nvim process based on the following logic :
    1) the process is a child of gnome-terminal
    2) the process has started close to starting_time
    3) Take the  in case there are multiple
    """
    #'gnome-terminal' in process.parent().name()
    process_list = list(psutil.process_iter())
    nvim_candidate_processes = list(filter(lambda process :
        'nvim' == process.name(),
            process_list))
    #TODO : find why starting_time < p.create_time
    #print([(p.name(),p.create_time() - starting_time,p.name() == 'nvim',p.create_time() >= starting_time,
    #        False if not p.parent() else ('gnome-terminal' in p.parent().name(),p.parent().name())) for p in nvim_candidate_processes])
    if len(nvim_candidate_processes) == 1 :
        nvim_process = nvim_candidate_processes[0]
    elif len(nvim_candidate_processes) == 0 :
        print("no editor found")
        nvim_process = None
    else :
        nvim_process = sorted(nvim_candidate_processes,key=lambda p : - p.create_time())[0]
    return nvim_process

def view_in_nvim(wkdirectory, initializer):
    tmp_file = tempfile.NamedTemporaryFile(prefix='tmp_element_building',dir=wkdirectory,delete=False)
    initializer(tmp_file.name)
    current_time = time.time()
    os.system('gnome-terminal --full-screen -x nvim -R {0}'.format(
        os.path.join(wkdirectory,tmp_file.name))
    )
    nvim_process = get_editor_pid(current_time)
    nvim_process.wait()


def edit_in_nvim(wkdirectory, initializer):
    """
    Edit all non Text and non on creation date fields using vim at the same time
    :param working directory as a string
    :initilizer function with a filename as an argument that initialize the file
    with a initial text like e.g. a form (fieldname= )
    """
    if not os.path.isdir(os.path.dirname(wkdirectory)):
        os.makedirs(os.path.dirname(wkdirectory))

    tmp_file = tempfile.NamedTemporaryFile(prefix='tmp_element_building',dir=wkdirectory,delete=False)
    initializer(tmp_file.name)
    #call(['gnome-terminal --full-screen -x nvim --listen {1} {0}'.format(tmp_file, self.socket_url)], shell=True)
    current_time = time.time()
    os.system('gnome-terminal --full-screen -x nvim {0}'.format(
        os.path.join(wkdirectory,tmp_file.name))
        )
    time.sleep(1)
    nvim_process = get_editor_pid(current_time)
    nvim_process.wait()
    with open(os.path.join(wkdirectory,tmp_file.name),'r') as f :
        return f.read()

def initialize_file(content,filename):
    with open(filename,'w') as f : 
        f.write(content)

class ElementModifier(cmd.Cmd):
    QUERY_TEMPLATE="select * from {0}s where _uuid = '{1}'"

    def __init__(self, data_type, tmp_files, _uuid, server_url):
        cmd.Cmd.__init__(self)
        if not data_type in DATA_TYPE_MAPPING.keys():
            print("data_type must be in {0}".format(list(DATA_TYPE_MAPPING.keys())))
            pass
        self.class_id = data_type
        self.data_type = DATA_TYPE_MAPPING[data_type]
        self._uuid = _uuid
        self.server_url = server_url
        request_json_result = OperationHelper.request_select_statement(self.server_url, self.QUERY_TEMPLATE.format(data_type, self._uuid))
        request_json_result = json.loads(request_json_result.text)
        df_request_result = pd.DataFrame(request_json_result)
        if df_request_result.shape[0] != 1 :
            print("number of rows : {0} for uuid {1}".format(df_request_result.shape[0], _uuid))
        self.past_data_element = df_request_result.iloc[0].to_dict()
        self.current_data_element = self.past_data_element.copy()
        self.tmp_files = tmp_files

    def do_done(self, arg):
        """
        Element modification is finished, then update
        :param arg:
        """
        results = list()
        for colname in filter(lambda colname : colname not in self.data_type.on_creation_columns, self.current_data_element):
            if self.current_data_element[colname] != self.past_data_element[colname] :
                res = OperationHelper.request_modify(self.server_url, self.class_id, self._uuid, colname, self.current_data_element[colname])
                print("modify {0} is {1}".format(colname,res))
                results.append(res)
        return True 

    def do_get_state(self, arg):
        print(self.current_data_element)

    def do_edit_field(self, args):
        argsp = args.split(' ')
        parsed_argsp = ( argsp[0],' '.join(argsp[1:]) ) if len(argsp) >= 2 else (argsp[0], None) 
        fieldname, value = parsed_argsp
        if fieldname in self.data_type.columns :
            if self.data_type.columns[fieldname] == Text :
                tmp_value = self.current_data_element[fieldname] if fieldname in self.current_data_element else "" 
                tmp_value = edit_in_nvim(self.tmp_files,partial(initialize_file,tmp_value))
                print(tmp_value)
                self.current_data_element[fieldname] = self.data_type.columns[fieldname](tmp_value)
            elif value == None or value == "": 
                print("No value given and field is not a Text")
            else :    
                self.current_data_element[fieldname] = self.data_type.columns[fieldname](value)

    def initialize_element_file(self, filepath):
        with open(filepath,'w') as f :
            field_initializer='\n'.join(
                    list(map(lambda colname : colname+'\t'+str(self.current_data_element[colname])+'\t'+'#'+str(self.data_type.columns[colname]),
                [col for col in self.data_type.columns.keys() if not col in self.data_type.on_creation_columns.keys() and not self.data_type.columns[col] is Text])))
            f.write(field_initializer)
            f.close()

    def parse_data(self, data_str) -> Dict :
            lines = data_str.splitlines()
            splitted_lines = list(map(lambda line : line.split('\t'), lines))
            splitted_lines = list(map(lambda line : (line[0],self.data_type.columns[line[0]](line[1])), splitted_lines))
            dictified_data = dict(list(splitted_lines))
            return dictified_data

    def do_edit_all(self, arg):
        if not os.path.isdir(os.path.dirname(self.tmp_files)):
            os.makedirs(os.path.dirname(self.tmp_files))
        data_str = edit_in_nvim(self.tmp_files, self.initialize_element_file)
        self.current_data_element.update(self.parse_data(data_str))

    def exit(self, arg):
        return None


class ElementBuilder(cmd.Cmd):

    def __init__(self, data_type, tmp_files, server_url):
        cmd.Cmd.__init__(self)
        self.data_type = DATA_TYPE_MAPPING[data_type]
        self.data_element = dict()
        self.server_url = server_url
        self.tmp_files = tmp_files

    def do_fields(self, arg):
        print([ col for col in self.data_type.columns if col not in self.data_type.on_creation_columns])

    def do_done(self, arg):
        try :
            new_element = self.data_type.new(**self.data_element)
        except Exception as e :
            print(e)
        else :
            print('a new {0} is born'.format(new_element.class_id))
            inserted = OperationHelper.request_insert(self.server_url, new_element)
            print('insertion of {0} is {1}'.format(new_element._uuid, inserted))
            return True 

    def do_get_state(self,arg):
        print(self.data_element)

    def do_edit_field(self, args):
        argsp = args.split(' ')
        parsed_argsp = ( argsp[0],' '.join(argsp[1:]) ) if len(argsp) >= 2 else (argsp[0], None) 
        fieldname, value = parsed_argsp
        if fieldname in self.data_type.columns.keys() :
            if self.data_type.columns[fieldname] == Text :
                tmp_value = self.data_element[fieldname] if fieldname in self.data_element else "" 
                tmp_value = edit_in_nvim(self.tmp_files,partial(initialize_file,tmp_value))
                self.data_element[fieldname] = self.data_type.columns[fieldname](tmp_value)
            elif value == None or value == "":
                print("No value given and field is not a Text")
            else :    
                self.data_element[fieldname] = self.data_type.columns[fieldname](value)
          
    def do_edit_all(self, arg):
        if not os.path.isdir(os.path.dirname(self.tmp_files)):
            os.makedirs(os.path.dirname(self.tmp_files))
        data_str = edit_in_nvim(self.tmp_files, self.initialize_element_file)
        self.data_element.update(self.parse_data(data_str))

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
                [col for col in self.data_type.columns.keys() if not col in self.data_type.on_creation_columns.keys() and not self.data_type.columns[col] is Text ])))
            f.write(field_initializer)
            f.close()

    def do_exit(self, arg):
        return None


class CommandLineClient(cmd.Cmd):

    def __init__(self, config_file):
        cmd.Cmd.__init__(self)
        self.intro = "Welcome to Neomnesis commandline client"
        self.prompt = "neomnesis_"+'\u039E' + " "
        cfg = ClientConfig(config_file)
        self.server_url = cfg.get_server_url()
        self.tmp_files = cfg.get_tmp_file()
        self.operation_list = list()
        if not os.path.isdir(self.tmp_files):
            os.makedirs(self.tmp_files)

    def do_beep(self, arg):
        """
        Make a beep with a timer
        uses : beep 1h50m3s 3 => make three beeps in 1 hour 50 minutes and 3 seconds
        uses : beep 1m => make one beeps in 1 minutes
        """
        beep_cmd = "play --no-show-progress --null --channels 1 synth {0} sine {1}".format(1,150)  
        arg_splitted = arg.split(' ')
        if len(arg_splitted) < 3 :
            try :
                duration = arg_splitted[0]
                retry = int(arg_splitted[1]) if len(arg_splitted) == 2 else 1
                d,h,m,s = list(map(lambda dur : re.compile("[0-9].*"+dur).findall(duration),["d","h","m","s"]))
                d = 0 if not d else int(d[0][:-1])*24*3600
                h = 0 if not h else int(h[0][:-1])*3600
                m = 0 if not m else int(m[0][:-1])*60
                s = 0 if not s else int(s[0][:-1])
                total_sleep_time = sum([d,h,m,s])
                cmd_to_perform = 'sleep {0} &&'.format(total_sleep_time) +'&& sleep 1 &&'.join([beep_cmd]*retry)
                call(cmd_to_perform+" &",shell=True)
            except Exception as e :
                print(e)
        else :
            print("malformed")
        


    def do_create(self, data_type):
        """
        starts a "create" command shell interface, usage:
        create <class_id> 
        """
        if data_type in ['note', 'task']:
            elem_builder = ElementBuilder(data_type, self.tmp_files, self.server_url)
            elem_builder.prompt = self.prompt[:-1] + 'create_'+ '\u039E' + " "
            res = elem_builder.cmdloop()
        else:
            print('/!\ Unknown data type {0}'.format(data_type))
            print("Known data types are "+' '.join(['note','task']))

    def do_query(self, select_statement):
        """
        performs a query using sql query statement
        
        """
        result_json = OperationHelper.request_select_statement(self.server_url, select_statement)
        result = pd.read_json(result_json.text)
        print(result.to_string())

    def do_show(self,args):
        """
        Show entire field (Use full for text field)
        show <class_id> <_uuid> <fieldname>
        """
        argsp = args.split(' ')
        if not len(argsp) == 3 :
            print("usage : show <class_id> <_uuid> <fieldname>")
            pass
        if not argsp[0] in ['note','task']:
            print("usage : show <class_id> <_uuid> <fieldname>")
            pass
        class_id, _uuid, fieldname = argsp
        select_statement = "select {0} from {1}s where _uuid = '{2}'".format( fieldname, class_id, _uuid)
        print(select_statement)
        result_json = OperationHelper.request_select_statement(self.server_url, select_statement)
        df_result = pd.read_json(result_json.text)
        print(df_result)
        print(df_result.iloc[0][fieldname])



    def do_cancel(self,arg):
        """
        cancel non commited changes, no arguments
        """
        OperationHelper.request_cancel(self.server_url) 

    def do_modify(self,arg):
        """
        starts a modify command shell interface, usage:
        modify <class_id> <_uuid>
        """
        argsp = arg.split(' ')
        if not len(argsp) == 2 :
            print("modify takes 2 parameters, usage :\n" 
                + "modify <class_id> <_uuis>")
        data_type, _uuid = argsp
        if data_type in ['note', 'task']:
            elem_modifier = ElementModifier(data_type, self.tmp_files, _uuid, self.server_url)
            elem_modifier.prompt = self.prompt[:-1] + 'modify_'+ '\u039E' + " "
            elem_modifier.cmdloop()
        else:
            print('/!\ Unknown data type {0}'.format(data_type))
            print("Known data types are "+' '.join(['note','task']))

    def do_commit(self, class_id):
        """
        commit changes on DB and save it, usage : 
        commit <class_id>
        """
        if not class_id in DATA_TYPE_MAPPING:
            print("No implemented class_id provided : {0}, expected {1}".format(class_id, list(DATA_TYPE_MAPPING.keys())))
        else :
            OperationHelper.request_commit(self.server_url, class_id)

    def do_delete(self, arg):
        """
        delete element, usage :
        delete <class_id> <_uuid>
        """
        argsp = arg.split(' ')
        if not len(argsp) == 2 :
            print("modify takes 2 parameters, usage :\n" 
                + "delete <class_id> <_uuis>")
        data_type, _uuid = argsp
        OperationHelper.request_delete(self.server_url, data_type, _uuid)

    def do_purge(self, arg):
        """
        purge everything on DB 
        no arguments
        """
        answer = None
        while answer not in ["Y","n"] :
            answer = input("Are you sure you want to purge everything ? Y/n")
        if answer == "n":
            print("I guess you were joking") 
        else :
            OperationHelper.request_purge(self.server_url) 

    def do_cancel_all(self, arg):
        OperationHelper.request_cancel(self.server_url) 
        pass

    def do_exit(self, arg):
        return True


if __name__ == '__main__':
    cmd_line_client = CommandLineClient(CONFIG_FILE)
    cmd_line_client.cmdloop()
