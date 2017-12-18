import os, sys
from configparser import ConfigParser

class NeoMnesisConfig:

    def __init__(self, cfg_filename):
        self.cfg_filename = cfg_filename
        self.cfg_parser = ConfigParser()
        self.cfg_parser.read(self.cfg_filename)

    def get_db_filename(self, app_name):
        return self.cfg_parser.get(app_name,'db_filename')
