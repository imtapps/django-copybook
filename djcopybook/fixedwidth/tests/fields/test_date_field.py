from datetime import date, datetime
import unittest

from djcopybook import fixedwidth
from djcopybook.fixedwidth import fields


class DateFieldTests(unittest.TestCase):

    def test_to_record_returns_formatted_date(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        self.assertEqual("20110831", field.to_record(date(2011, 8, 31)))

    def test_to_record_returns_padded_spaces_when_value_is_None(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        self.assertEqual("        ", field.to_record(None))

    def test_to_record_returns_padded_spaces_when_value_is_empty_string(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        self.assertEqual("        ", field.to_record(''))

    def test_to_python_turns_string_to_date_field(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        expected_date = date(2011, 8, 31)
        python_val = field.to_python("20110831")
        self.assertEqual(expected_date, python_val)
        self.assertIsInstance(python_val, date)

    def test_to_python_returns_none_when_no_value_given(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        self.assertEqual(None, field.to_python(None))

    def test_to_python_returns_none_when_empty_string_given(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        self.assertEqual(None, field.to_python("        "))

    def test_to_python_returns_date_when_already_date(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        expected_date = date(2011, 8, 31)
        python_val = field.to_python(expected_date)
        self.assertEqual(expected_date, python_val)
        self.assertIsInstance(python_val, date)

    def test_to_python_returns_date_when_given_datetime(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        expected_date = datetime(2011, 8, 31)
        python_val = field.to_python(expected_date)
        self.assertEqual(expected_date.date(), python_val)
        self.assertIsInstance(python_val, date)

    def test_to_python_raises_value_error_when_value_given_has_characters(self):
        field = fields.DateField(length=5)
        with self.assertRaises(ValueError):
            self.assertEqual(None, field.to_python("0001A"))

    def test_datefield_should_allow_string_default_date(self):
        class TestRecord(fixedwidth.Record):
            field_one = fields.DateField(length=10, format="%m/%d/%Y", default="08/01/2001")

        c = TestRecord()
        self.assertEqual(date(2001, 8, 1), c.field_one)

    def test_datefield_should_allow_date_default_date(self):
        default_date = date(2001, 1, 1)

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateField(length=10, format="%m/%d/%Y", default=default_date)

        c = TestRecord()
        self.assertEqual(date(2001, 1, 1), c.field_one)

    def test_datefield_should_allow_callable_date(self):
        def get_date():
            return date(2000, 1, 1)

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateField(length=10, format="%m/%d/%Y", default=get_date)

        c = TestRecord()
        self.assertEqual(date(2000, 1, 1), c.field_one)
