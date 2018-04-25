import networkx as nx
import os


class GraphDB(nx.DiGraph):

    def __init__(self, gdb_path):
        self.gdb_path = gdb_path
        basename = os.path.basename(gdb_path)
        if not os.path.isfile(gdb_path):
            if not os.path.isdir(basename):
                os.path.mkdir(basename)

    
    def to_json():
        pass



        
    
