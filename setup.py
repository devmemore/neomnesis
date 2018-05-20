from setuptools import setup, find_packages
import os

local_dir = os.path.dirname(os.path.realpath(__file__))

requirement_file = os.path.join(local_dir,'scripts/requirements.txt')
requirements = []
#with open(requirement_file,'r') as req_file :
#    requirements = req_file.read().splitlines()

setup(name='neomnesis',
      version='0.0.0',  
      description='a personnal Python project',
      packages=find_packages(),
      install_requires=[] #requirements,
      )


