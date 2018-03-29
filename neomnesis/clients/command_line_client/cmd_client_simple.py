import os, sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..','..'))


import requests
from neomnesis.common.db.element import Element
from neomnesis.clients.config.client_config import ClientConfig
from neomnesis.task.task import Task
from neomnesis.note.note import Note
from subprocess import call




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
        print(result.text)
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

class ElementBuilder:
    pass


class CommandLineClient:

    def __init__(self, config_file):
        cfg = ClientConfig(config_file)
        print(cfg.cfg_parser._sections)
        self.tmp_file = cfg.cfg_parser.get('main','tmp_file')
        self.server_url = cfg.cfg_parser.get('main','server_url')

    def edit(self):
        r = call(['vim',self.tmp_file],shell=True)
        print(r)
        with open(self.tmp_file,'r') as tmpfile :
            return tmpfile.read()

if __name__ == '__main__' :
    cmd_line_client = CommandLineClient('/home/thomas/Work/Gits/neomnesis/configs/cmd_client_config_local.cfg')
    
    url= cmd_line_client.server_url
    print(url)
    res = OperationHelper.request_insert(url,Note.new_note("a note","something"))
    print(res.text)
    OperationHelper.request_insert(url,Note.new_note("another note","something 2"))
    OperationHelper.request_insert(url,Note.new_note("another note","something 3"))
    res = OperationHelper.request_select_statement(url,"note","select * from notes")
    print(res.text)
