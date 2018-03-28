import requests
import os, sys
from neomnesis.common.db.element import Element
from neomnesis.clients.config.client_config import ClientConfig
from enum import Enum


class Operation:
    operation_prefix = ''


class InsertOpration(Operation):

    operation_prefix = 'insert'

    @classmethod
    def insert_command(cls, server_url, element : Element):
        pass

    @classmethod
    def perform_insert(cls, server_url, element : Element):
        url_command = 'insert'
        result = requests.post(server_url + '/' + url_command, data=element.to_row())
        return result

    @classmethod
    def object_insertion(cls,):
        pass

class Operations:
    insertion = InsertOpration


class CommandLineClient:

    def __init__(self, cfg : ClientConfig):
        pass

if __name__ == '__main__' :
    pass
