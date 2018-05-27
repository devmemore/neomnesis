import shutil
import tempfile
import pathlib
import json
from datetime import datetime
from neomnsis.server.config.config import NeoMnesisConfig
import os

class NeomnesisArchive(object):

    def __init__(self, creation_date, cfg : NeoMnesisConfig):
        self.creation_date = creation_date
        self.domain = cfg.get_domaine() 
        self.table_paths_list = \
        [cfg.get_db_filename(appname) for appname in ['task','note']] + \
        [cfg.get_tmp_db_filename(appname) for appname in ['task','note']]

    def get_archive_basename(self):
        return "archive_{0}_{1}".format(self.domain, self.creation_date.strftime("%Y_%m_%d_%H%M%S_%N"))

    def add_metadata(self, aggdir_path):
        metadata_filepath=Path(aggdir_path, PurePath('.metadata'))
        metadata_dict = {'creation_date' : self.creation_date,
                         'domain' : self.domain,
                         'table_paths_list' : self.table_paths_list}
        with open(metadata_filepath,'w') as f :
            f.write(json.dumps(metadata_dict))

    def create_archive(self, output_path):
        tmpdir = tempfile.mkdtemp()
        tmpdir = pathlib.PurePath(tmpdir)
        agg_name = pathlib.PurePath(self.get_archive_basename()) 
        aggdir_path = pathlib.Path(tmpdir, agg_name)
        for table_path in self.table_paths_list :
            shutil.copyfile(table_path,str(aggdir_path))
        self.add_metadata(aggdir_path)
        shutil.make_archive(tmpdir,base_dir=str(aggdir_path))
        

    @staticmethod
    def new(cfg : NeoMnesisConfig):
        creation_date = datetime.now()
        return NeomnesisArchive(creation_date, cfg)

    @classmethod
    def from_archive(cls, archive_path):
        cls.new()

    @staticmethod
    def cypher(secret_key):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        backend = default_backend()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(secret_key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(b"a secret message") + encryptor.finalize()
        decryptor = cipher.decryptor()
        decryptor.update(ct) + decryptor.finalize()


        

