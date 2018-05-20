import unittest
from neomnesis.common.data_type.text import Text
from neomnesis.common.data_type.date import Date, DateHour


class TestDataType(unittest.TestCase):

    def test_text(self):
        text = Text("Hello") + Text(" ") + Text("World")
        self.assertEqual(text, Text("Hello World"))

    def test_date(self):
        date1 = Date("2017-05-01")
        date2 = Date("2018-05-01")
        self.assertTrue(date1 < date2)


