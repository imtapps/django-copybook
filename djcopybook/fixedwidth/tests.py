
from datetime import date, datetime
from unittest import TestCase

from djcopybook import fixedwidth
from djcopybook.fixedwidth import fields

__all__ = (
    'PaddingTests',
    'RecordTests',
    'FixedWidthFieldTests',
    'StringFieldTests',
    'IntegerFieldTests',
    'DecimalFieldTests',
    'DateFieldTests'

)

class RecordOne(fixedwidth.Record):
    field_one = fields.StringField(length=5, default="AA")
    field_two = fields.IntegerField(length=7)


class RecordTwo(RecordOne):
    field_three = fields.DecimalField(length=9)
    field_four = fields.DateField(length=2)


class PaddingTests(TestCase):

    def test_str_padding_pads_right_with_spaces(self):
        self.assertEqual("ALM   ", fields.str_padding(6, "ALM"))
        self.assertEqual("5     ", fields.str_padding(6, 5))

    def test_int_padding_pads_left_with_zeros(self):
        self.assertEqual("000010", fields.int_padding(6, 10))
        self.assertEqual("000010", fields.int_padding(6, "10"))

    def test_float_padding_pads_left_and_decimals_with_zeros(self):
        self.assertEqual("000010", fields.float_padding(6, 10, 0))
        self.assertEqual("000010", fields.float_padding(6, "10", 0))

        self.assertEqual("00300.12", fields.float_padding(8, 300.1234, 2))
        self.assertEqual("010.12", fields.float_padding(6, "10.1234", 2))
        self.assertEqual("010.10", fields.float_padding(6, "10.1", 2))
        self.assertEqual("010.00", fields.float_padding(6, 10, 2))

        self.assertEqual("000010.123", fields.float_padding(10, 10.1234, 3))
        self.assertEqual("0005.123", fields.float_padding(8, "5.1234", 3))

class RecordTests(TestCase):

    def test_keeps_list_of_fields_in_order_when_record_is_instantiated(self):
        r = RecordOne()
        self.assertEqual(['field_one', 'field_two'], r.fields.keys())
        self.assertEqual(['field_one', 'field_two'], r.base_fields.keys())

    def test_record_inheritance_maintains_order(self):
        r = RecordTwo()
        self.assertEqual(['field_one', 'field_two', 'field_three', 'field_four'], r.fields.keys())
        self.assertEqual(['field_one', 'field_two', 'field_three', 'field_four'], r.base_fields.keys())

    def test_fills_attributes_with_values_given_in_init(self):
        r = RecordOne(field_one=10, field_two=5)
        self.assertEqual("10", r.field_one)
        self.assertEqual(5, r.field_two)

    def test_to_record_returns_record_for_each_field(self):
        r = RecordOne(field_one="test", field_two=500)
        self.assertEqual("test 0000500", r.to_record())

    def test_returns_field_default_value_when_not_given(self):
        r = RecordOne(field_two=10)
        self.assertEqual("AA", r.field_one)

    def test_raises_type_error_when_instantiating_record_with_bad_value(self):
        with self.assertRaises(TypeError) as e:
            RecordOne(bad_field="test")
        self.assertEqual("'bad_field' is an invalid keyword argument for this function", e.exception.message)

class FixedWidthFieldTests(TestCase):

    def test_raises_field_length_error_when_value_is_longer_than_allowed(self):
        f = fields.FixedWidthField(length=5)
        f.attname = "field_one" # fake for test... fixedwidth sets this on instantiation
        with self.assertRaises(fields.FieldLengthError) as e:
            f.get_record_value("This is a long")

        msg = "'field_one' value 'This is a long' is longer than 5 chars."
        self.assertEqual(msg, e.exception.message)

    def test_get_default_returns_none_when_no_default(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual(None, field.get_default())

    def test_get_default_returns_default_when_present(self):
        field = fields.FixedWidthField(length=5, default="ABC")
        self.assertEqual("ABC", field.get_default())

    def test_get_default_returns_called_default_when_callable(self):
        def get_default():
            return "Default Value"

        field = fields.FixedWidthField(length=15, default=get_default)
        self.assertEqual("Default Value", field.get_default())

    def test_to_record_returns_string_of_value_padded_to_length(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual("ALM  ", field.to_record("ALM"))

    def test_to_record_returns_padded_blank_string_when_value_is_None(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual("     ", field.to_record(None))

    def test_to_python_turns_value_to_string(self):
        field = fields.FixedWidthField(length=5)
        python_val = field.to_python(10)
        self.assertEqual("10", python_val)
        self.assertIsInstance(python_val, str)

    def test_to_python_returns_none_when_value_is_none(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual(None, field.to_python(None))

class StringFieldTests(TestCase):

    def test_to_record_returns_string_of_value_padded_to_length(self):
        field = fields.StringField(length=5)
        self.assertEqual("AA   ", field.to_record("AA"))

    def test_to_record_returns_padded_blank_string_when_value_is_None(self):
        field = fields.StringField(length=5)
        self.assertEqual("     ", field.to_record(None))

    def test_to_python_turns_value_to_string(self):
        field = fields.StringField(length=5)
        python_val = field.to_python(10)
        self.assertEqual("10", python_val)
        self.assertIsInstance(python_val, str)

    def test_to_python_returns_none_when_value_is_none(self):
        field = fields.StringField(length=5)
        self.assertEqual(None, field.to_python(None))

class IntegerFieldTests(TestCase):

    def test_to_record_returns_string_of_value_padded_to_length(self):
        field = fields.IntegerField(length=5)
        self.assertEqual("00012", field.to_record(12))

    def test_to_record_returns_padded_zeros_when_value_is_None(self):
        field = fields.IntegerField(length=5)
        self.assertEqual("00000", field.to_record(None))

    def test_to_python_turns_value_to_int(self):
        field = fields.IntegerField(length=5)
        python_val = field.to_python("10")
        self.assertEqual(10, python_val)
        self.assertIsInstance(python_val, int)

    def test_to_python_returns_none_when_value_is_none(self):
        field = fields.IntegerField(length=5)
        self.assertEqual(None, field.to_python(None))

class DecimalFieldTests(TestCase):

    def test_to_record_returns_string_value_padded_to_length(self):
        field = fields.DecimalField(length=6, decimals=1)
        self.assertEqual("0010.0", field.to_record(10))

    def test_to_record_returns_padded_zeros_when_value_is_None(self):
        field = fields.DecimalField(length=7, decimals=2)
        self.assertEqual("0000.00", field.to_record(None))

    def test_to_python_turns_value_to_float(self):
        field = fields.DecimalField(length=5)
        python_val = field.to_python("10.12")
        self.assertEqual(10.12, python_val)
        self.assertIsInstance(python_val, float)

    def test_to_python_returns_none_when_value_is_none(self):
        field = fields.DecimalField(length=5)
        self.assertEqual(None, field.to_python(None))

class DateFieldTests(TestCase):

    def test_to_record_returns_formatted_date(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        self.assertEqual("20110831", field.to_record(date(2011,8,31)))

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

    def test_to_python_returns_date_when_already_date(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        expected_date = date(2011,8,31)
        python_val = field.to_python(expected_date)
        self.assertEqual(expected_date, python_val)
        self.assertIsInstance(python_val, date)

    def test_to_python_returns_date_when_given_datetime(self):
        field = fields.DateField(length=8, format="%Y%m%d")
        expected_date = datetime(2011,8,31)
        python_val = field.to_python(expected_date)
        self.assertEqual(expected_date.date(), python_val)
        self.assertIsInstance(python_val, date)

    def test_datefield_should_allow_string_default_date(self):
        class TestRecord(fixedwidth.Record):
            field_one = fields.DateField(length=10, format="%m/%d/%Y", default="08/01/2001")

        c = TestRecord()
        self.assertEqual(date(2001, 8, 1), c.field_one)

    def test_datefield_should_allow_date_default_date(self):
        default_date = date(2001,1,1)

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateField(length=10, format="%m/%d/%Y", default=default_date)

        c = TestRecord()
        self.assertEqual(date(2001, 1, 1), c.field_one)

    def test_datefield_should_allow_callable_date(self):
        def get_date():
            return date(2000,1,1)

        class TestRecord(fixedwidth.Record):
            field_one = fields.DateField(length=10, format="%m/%d/%Y", default=get_date)

        c = TestRecord()
        self.assertEqual(date(2000, 1, 1), c.field_one)