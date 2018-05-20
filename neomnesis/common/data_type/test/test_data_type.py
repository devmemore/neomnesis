import unittest
from neomnesis.common.data_type.text import Text
from neomnesis.common.data_type.date import Date


class TestDataType(unittest.TestCase):

    def test_text(self):
        text = Text("Hello") + Text(" ") + Text("World")
        self.assertEquals(text == Text("Hello World"))


