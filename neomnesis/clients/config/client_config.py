import os, sys
from configparser import ConfigParser


class ClientConfig:

    def __init__(self, cfg_filename):
        self.cfg_filename = cfg_filename
        self.cfg_parser = ConfigParser()
        self.cfg_parser.read(cfg_filename)
        self.cfg_parser.read(self.cfg_filename)

    def get_server_url(self):
        return self.cfg_parser.get('main','server_url')

    def get_tmp_file(self):
        return self.cfg_parser.get('main','tmp_file')
