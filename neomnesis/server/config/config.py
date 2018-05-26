from configparser import ConfigParser
from pathlib import Path, PurePath
import os


class NeoMnesisConfig:

    def __init__(self, cfg_filename):
        self.cfg_filename = cfg_filename
        self.cfg_parser = ConfigParser()
        self.cfg_parser.read(self.cfg_filename)
        self.port = '9876'

    def get_db_filename(self, app_name):
        return str(PurePath(Path.home(), self.cfg_parser.get(app_name,'db_filename')))

    def get_tmp_db_filename(self, app_name):
        return str(PurePath(Path.home(), self.cfg_parser.get(app_name,'tmp_db_filename')))
