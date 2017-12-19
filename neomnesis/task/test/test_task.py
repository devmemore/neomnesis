import sys, os


local_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(local_dir,'..','..'))
sys.path.append(os.path.join(local_dir,'..'))

import unittest
from task.task import Task, TaskDB, TASK_TABLE
import config

from datetime import datetime


class TaskDBUnitTest(unittest.TestCase):

    unittest_task_cfg = os.path.join(local_dir,'unittest_task_config.cfg')

    def setUp(self):
        cfg = config.NeoMnesisConfig(self.unittest_task_cfg)
        self.tdb = TaskDB(cfg)

    def test_insert_row(self):
        self.setUp()
        my_task = Task('do this shit','don\'t procrastinate budy!', 0, datetime(2017,1,1))
        self.tdb.insert_task(my_task)
        task_result = self.tdb.get_task_from_select("select * from %s" % TASK_TABLE)
        print(task_result)
        return

if __name__ == '__main__' :
    unittest.main()

