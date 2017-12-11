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

    def test_to_record_handles_non_date_str_default(self):

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateTimeField(length=10, format="%m/%d/%Y", default="?" * 10)

        c = TestRecord()
        self.assertEqual('?' * 10, c.field_one)

    def test_to_record_handles_string_date(self):

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateTimeField(length=10, format="%m/%d/%Y")

        c = TestRecord()
        c.field_one = "04/05/2010"
        self.assertEqual(datetime(2010, 4, 5), c.field_one)

    def test_raises_error_if_bad_data_is_put_in_datetimefield(self):

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateTimeField(length=10, format="%m/%d/%Y")

        c = TestRecord()
        with self.assertRaises(ValueError):
            c.field_one = 'BADDATA'

    def test_raises_error_if_bad_data_is_put_in_datetimefield_even_with_default(self):

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateTimeField(length=10, format="%m/%d/%Y", default='?' * 10)

        c = TestRecord()
        with self.assertRaises(ValueError):
            c.field_one = 'BADDATA'

    def test_to_python_returns_default_even_if_not_convertable_to_datetime(self):
        field = fields.DateTimeField(length=8, format="%Y%m%d", default='?' * 8)
        expected_date = '?' * 8
        python_val = field.to_python(expected_date)
        self.assertEqual(expected_date, python_val)
