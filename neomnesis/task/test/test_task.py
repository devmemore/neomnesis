import os
import sys
import unittest
import pandas as pd

local_dir = os.path.dirname(__file__)
#sys.path.append(os.path.join(local_dir,'..','..','..'))
#sys.path.append(os.path.join(local_dir,'..','..'))
#sys.path.append(os.path.join(local_dir,'..'))

from neomnesis.task.task import Task, TaskDB, TASK_TABLE, DATETIME_FORMAT, DateHour
import neomnesis.server.config.config as config

from datetime import datetime, timedelta


class TaskDBUnitTest(unittest.TestCase):

    unittest_task_cfg = os.path.join(local_dir,'unittest_task_config.cfg')

    def setUp(self):
        cfg = config.NeoMnesisConfig(self.unittest_task_cfg)
        self.cfg = cfg
        self.tdb = TaskDB(cfg)
        self.tdb.purge()

    def deleteDBfiles(self,cfg):
        os.remove(cfg.get_db_filename('task'))
        os.remove(cfg.get_tmp_db_filename('task'))

    def test_insert_row(self):
        self.setUp()
        my_task = Task.new('do this shit','don\'t procrastinate budy!', 0, DateHour.from_datetime(datetime(2017,1,1)))
        self.tdb.insert(my_task)
        task_result = self.tdb.get_from_select("select * from %s" % TASK_TABLE)
        columns_to_compare = ['title', 'description', 'priority','due_date']
        self.assertTrue(
            all(
                task_result[columns_to_compare]
                        ==
                pd.DataFrame([{'title': 'do this shit',
                                          'description' : 'don\'t procrastinate budy!',
                                          'priority' : 0,
                                          'due_date' : datetime(2017,1,1).strftime(DATETIME_FORMAT),
                                          }])[columns_to_compare]
            )
        )

    def test_delete_row(self):
        self.setUp()
        tasks = [Task.new('task %d' % i,'yet another task', i, DateHour.from_datetime(datetime(2017,1,1,5)+ timedelta(days=i))) for i in range(10)]
        self.tdb.insert_list(tasks)
        result = self.tdb.get_from_select("select * from tasks order by title desc")
        to_delete = result.iloc[5:10]
        for my_uuid in to_delete._uuid.tolist() :
            self.tdb.delete_by_uuid(my_uuid)
        result_2 = self.tdb.get_from_select("select * from tasks")
        self.assertEqual(result_2.title.tolist(), ['task %d'% i for i in range(5,10)])

    def test_modify_take(self):
        message = "let's describe it better"
        self.setUp()
        tasks = [Task.new('task %d' % i,'yet another task', i, DateHour.from_datetime(datetime(2017,1,1,5)+ timedelta(days=i))) for i in range(10)]
        self.tdb.insert_list(tasks)
        result_title_is_like_5 = self.tdb.get_from_select("select * from {0} where title like 'task 5'".format(TASK_TABLE))
        self.tdb.modify(result_title_is_like_5.iloc[0]._uuid, "description",message)
        result = self.tdb.get_from_select("select * from tasks")
        self.assertEqual(result[result.title == "task 5"].iloc[0].description, message)

    def test_commit(self):
        self.setUp()
        # CREATE 10 tasks
        tasks = [Task.new('task %d' % i,'yet another task', i, DateHour.from_datetime(datetime(2017,1,1,5)+ timedelta(days=i))) for i in range(10)]
        self.tdb.insert_list(tasks)
        # Commit it
        self.tdb.commit()
        # Remove one task from tmp dataframe and commit to tmp sqlite db
        result_select =self.tdb.get_from_select('select _uuid from tasks where priority = 1')
        muuid = result_select.iloc[0]._uuid
        result_select =self.tdb.get_from_select('select * from tasks')
        self.tdb.delete_by_uuid(muuid)
        # we haven't commit the delete so there must be 10 tasks if we reset it up
        self.assertEqual(self.tdb.get_all().shape[0], 9)
        self.tdb.rebase()
        self.assertEqual(self.tdb.get_all().shape[0], 10)
        self.tdb.delete_by_uuid(muuid)
        self.tdb.commit()
        self.tdb.rebase()
        self.assertEqual(self.tdb.get_all().shape[0], 9)
        # let's purge
        self.tdb.purge()
        # there is then no tasks in main db
        self.assertEqual(self.tdb.get_all().shape[0], 0)
        self.deleteDBfiles(self.cfg)

    def test_consistency_over_updates(self):
        self.setUp()
        self.tdb.purge()
        self.tdb.insert_row('ha','ho',5,datetime(2017,1,1))
        self.tdb.commit()
        self.assertEqual(self.tdb.get_all().iloc[0].title, 'ha')
        self.tdb.insert_row('hey','lol',3,datetime(2017,1,12))
        self.assertEqual(self.tdb.get_all().iloc[1].title, 'hey')
        self.tdb.rebase()
        self.assertEqual(self.tdb.get_all().shape[0], 1)
        self.assertEqual(self.tdb.get_all().iloc[0].title, 'ha')
        self.tdb.purge()
        self.assertEqual(self.tdb.get_all().shape[0], 0)
        self.tdb.commit()
        self.deleteDBfiles(self.cfg)




if __name__ == '__main__' :
    unittest.main()

