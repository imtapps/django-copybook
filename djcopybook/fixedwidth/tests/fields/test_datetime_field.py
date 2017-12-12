import six
from datetime import date, datetime
import unittest

from djcopybook import fixedwidth
from djcopybook.fixedwidth import fields


class DateTimeFieldTests(unittest.TestCase):

    def setUp(self):
        self.sut = fields.DateTimeField(length=14, default=datetime(2012, 1, 1, 1, 1, 1), format="%Y%m%d%H%M%S")

    def test_to_record_returns_formatted_datetime(self):
        self.assertEqual("20120101010101", self.sut.to_record(datetime(2012, 1, 1, 1, 1, 1)))

    def test_to_record_returns_default_formatted_datetime_when_before_1900_on_python2(self):
        if six.PY3:
            self.assertEqual("18990101010101", self.sut.to_record(datetime(1899, 1, 1, 1, 1, 1)))
        if six.PY2:
            self.assertEqual("20120101010101", self.sut.to_record(datetime(1899, 1, 1, 1, 1, 1)))

    def test_to_record_raises_exception_when_error_datetime_not_before_1900(self):
        with self.assertRaises(AttributeError):
            self.sut.to_record('x')

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

    def test_to_record_returns_empty_record_value_when_value_is_none(self):
        field = fields.DateTimeField(length=10, format="%m/%d/%Y", empty_record_value="?" * 10)
        self.assertEqual("?" * 10, field.to_record(None))
