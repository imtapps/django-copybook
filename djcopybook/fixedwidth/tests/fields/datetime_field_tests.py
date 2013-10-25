from datetime import date, datetime
import unittest

from djcopybook.fixedwidth import fields


class DateTimeFieldTests(unittest.TestCase):

    def setUp(self):
        self.sut = fields.DateTimeField(length=14, format="%Y%m%d%H%M%S")

    def test_to_record_returns_formatted_datetime(self):
        self.assertEqual("20120101010101", self.sut.to_record(datetime(2012, 1, 1, 1, 1, 1)))

    def test_to_record_returns_empty_string_of_correct_length_when_none(self):
        self.assertEqual("              ", self.sut.to_record(None))

    def test_to_record_returns_empty_string_of_correct_length_when_empty_string(self):
        self.assertEqual("              ", self.sut.to_record(""))

    def test_to_python_returns_datetime_object(self):
        self.assertEqual(datetime(2012, 1, 1, 1, 1, 1), self.sut.to_python("20120101010101"))

    def test_to_python_returns_datetime_object_when_passed_a_date_object(self):
        self.assertEqual(datetime(2012, 1, 1, 0, 0, 0), self.sut.to_python(date(2012, 1, 1)))

    def test_to_python_returns_datetime_object_when_passed_a_datetime_object(self):
        self.assertEqual(datetime(2012, 1, 1, 1, 1, 1), self.sut.to_python(datetime(2012, 1, 1, 1, 1, 1)))

    def test_to_python_returns_none_when_empty_string(self):
        self.assertEqual(None, self.sut.to_python(""))

    def test_to_python_returns_none_when_none(self):
        self.assertEqual(None, self.sut.to_python(None))

    def test_to_python_returns_datetime_object_when_passed_string(self):
        self.assertEqual(datetime(2012, 1, 1, 1, 1, 1), self.sut.to_python("20120101010101"))

    def test_to_python_returns_datetime_object_when_unicode(self):
        self.assertEqual(datetime(2012, 1, 1, 1, 1, 1), self.sut.to_python(u"20120101010101"))
