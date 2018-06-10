from configparser import ConfigParser
from pathlib import Path, PurePath
import os


class NeoMnesisConfig:

    def __init__(self, cfg_filename, all_path_prefix=None):
        self.cfg_filename = cfg_filename
        self.cfg_parser = ConfigParser()
        self.cfg_parser.read(self.cfg_filename)
        self.port = '9876'
        self.all_path_prefix = all_path_prefix

    def get_db_filename(self, app_name):
        return str(PurePath(Path.home() if not self.all_path_prefix else self.all_path_prefix , self.cfg_parser.get(app_name,'db_filename')))

    def get_tmp_db_filename(self, app_name):
        return str(PurePath(Path.home() if not self.all_path_prefix else self.all_path_prefix, self.cfg_parser.get(app_name,'tmp_db_filename')))

    def get_backup(self):
        return str(PurePath(Path.home() if not self.all_path_prefix else self.all_path_prefix , self.cfg_parser.get('sync','backup')))

    def get_archive(self):
        return str(PurePath(Path.home() if not self.all_path_prefix else self.all_path_prefix, self.cfg_parser.get('sync','archive')))

    def get_domain(self):
        return self.cfg_parser.get('main','domain')
