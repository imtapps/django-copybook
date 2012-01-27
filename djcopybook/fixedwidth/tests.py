
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
    'DateFieldTests',
    'ListFieldTests',
    'FragmentFieldTests',
)

class RecordOne(fixedwidth.Record):
    field_one = fields.StringField(length=5, default="AA")
    field_two = fields.IntegerField(length=7)

class RecordTwo(RecordOne):
    field_three = fields.DecimalField(length=9)
    field_four = fields.DateField(length=2)

class RecordThree(fixedwidth.Record):
    frag = fields.FragmentField(record=RecordOne)
    other_field = fields.StringField(length=3, default="BBB")


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

    def test_ignores_kwarg_value_when_field_not_declared_on_record(self):
        r = RecordOne(field_one="abc", no_field="test")
        self.assertEqual("abc", r.field_one)
        self.assertFalse(hasattr(r, "no_field"))

    def test_len_on_record_returns_total_fixed_width_length(self):
        r = RecordOne()
        self.assertEqual(12, len(r))

    def test_len_on_record_returns_total_amount_with_list_field(self):
        class ListRecord(fixedwidth.Record):
            field_one = fields.StringField(length=1)
            field_two = fields.IntegerField(length=2)

        class TestRecord(fixedwidth.Record):
            name = fields.StringField(length=2)
            list_field = fields.ListField(ListRecord, length=2)
            end = fields.StringField(length=1)

        # should get same len whether using instance or just the class
        r = TestRecord()
        self.assertEqual(9, len(r))
        self.assertEqual(9, len(TestRecord))

    def test_str_on_record_returns_to_record_value(self):
        r = RecordOne(field_one="test", field_two=500)
        self.assertEqual("test 0000500", str(r))

    def test_from_record_turns_fixed_width_string_to_record_object(self):
        r = RecordOne.from_record("test 0000500")
        self.assertEqual("test", r.field_one)
        self.assertEqual(500, r.field_two)

    def test_from_record_turns_fixed_width_string_to_record_with_list_field(self):
        class ListRecord(fixedwidth.Record):
            field_one = fields.StringField(length=1)
            field_two = fields.IntegerField(length=2)

        class TestRecord(fixedwidth.Record):
            name = fields.StringField(length=2)
            list_field = fields.ListField(ListRecord, length=2)
            end = fields.StringField(length=1)

        r = TestRecord.from_record("XXA05B10Z")
        self.assertEqual("XX", r.name)
        self.assertEqual("Z", r.end)

        list_field_one = r.list_field[0]
        self.assertEqual("A", list_field_one.field_one)
        self.assertEqual(5, list_field_one.field_two)

        list_field_two = r.list_field[1]
        self.assertEqual("B", list_field_two.field_one)
        self.assertEqual(10, list_field_two.field_two)

        self.assertEqual("XXA05B10Z", r.to_record())

    def test_from_record_raises_value_error_when_fixed_width_string_less_than_record_length(self):
        with self.assertRaises(ValueError) as e:
            RecordOne.from_record("test 000050")
        self.assertEqual("Fixed width record length is 11 but should be 12.", e.exception.message)

    def test_from_record_raises_value_error_when_fixed_width_string_greater_than_record_length(self):
        with self.assertRaises(ValueError) as e:
            RecordOne.from_record("test 00005000")
        self.assertEqual("Fixed width record length is 13 but should be 12.", e.exception.message)



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

    def test_to_python_strips_extra_padding_from_right(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual("AA", field.to_python("AA   "))

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


class FragmentFieldTests(TestCase):

    def test_to_python_returns_record_instance_when_none_given(self):
        f = fields.FragmentField(record=RecordOne)
        python_val = f.to_python(None)
        self.assertIsInstance(python_val, RecordOne)

    def test_to_python_returns_record_instance_when_given_string(self):
        f = fields.FragmentField(record=RecordOne)
        python_val = f.to_python('AAAAA1111111')
        self.assertIsInstance(python_val, RecordOne)

    def test_to_python_returns_record_instance_when_given_instance(self):
        record = RecordOne()
        f = fields.FragmentField(record=RecordOne)
        python_val = f.to_python(record)
        self.assertIsInstance(python_val, RecordOne)

    def test_to_python_raises_type_error_when_receives_bad_input(self):
        f = fields.FragmentField(record=RecordOne)
        with self.assertRaises(TypeError) as ctx:
            f.to_python(222)
        self.assertEqual("Redefined field must be a string or RecordOne instance.", ctx.exception.message)

    def test_to_record_returns_string_of_record_when_explicitly_set(self):
        r = RecordThree(other_field="ZZZ")
        self.assertEqual("AA   0000000ZZZ", r.to_record())

    def test_to_record_returns_string_of_record_when_has_explicit_values(self):
        my_record = RecordOne(field_one="aa", field_two=999)
        r = RecordThree(frag=my_record, other_field="ZZZ")
        self.assertEqual("aa   0000999ZZZ", r.to_record())

    def test_creates_record_object_properly_from_string(self):
        r = RecordThree.from_record("aaaaa9999999ZZZ")
        self.assertEqual("aaaaa", r.sub_field.field_one)
        self.assertEqual(9999999, r.sub_field.field_two)
        self.assertEqual("ZZZ", r.other_field)
        self.assertIsInstance(r.sub_field, RecordOne)

    def test_creates_record_object_properly_from_string(self):
        r = RecordThree()
        r.frag.field_one = "aaa"
        r.frag.field_two = 999

        self.assertEqual("aaa  0000999BBB", r.to_record())


class ListFieldTests(TestCase):

    def test_to_python_returns_list_of_records(self):
        f = fields.ListField(record=RecordOne, length=2)
        records = [RecordOne(), RecordOne()]
        python_val = f.to_python(records)
        self.assertEqual(records, python_val)
        self.assertIsInstance(python_val, list)

    def test_to_python_returns_list_of_records_when_given_string(self):
        f = fields.ListField(record=RecordOne, length=2)

        records = f.to_python("ABCDE1111111ZYXWV9999999")
        self.assertEqual(len(records), 2)

        record_one = records[0]
        self.assertEqual("ABCDE", record_one.field_one)
        self.assertEqual(1111111, record_one.field_two)

        record_two = records[1]
        self.assertEqual("ZYXWV", record_two.field_one)
        self.assertEqual(9999999, record_two.field_two)

    def test_to_python_raises_type_error_when_not_given_record_class_instances(self):
        f = fields.ListField(record=RecordOne, length=2)
        records = [RecordOne(), fixedwidth.Record()]

        with self.assertRaises(TypeError) as e:
            f.to_python(records)
        self.assertEqual("List field must contain instances of 'RecordOne'.", e.exception.message)

    def test_defaults_field_to_empty_list_when_no_records_initially_given(self):
        class TestRecord(fixedwidth.Record):
            field_one = fields.ListField(RecordOne, length=2)

        r = TestRecord()
        self.assertEqual([], r.field_one)

    def test_to_record_returns_string_of_all_records_from_list_field(self):
        class TestRecord(fixedwidth.Record):
            list_field = fields.ListField(RecordOne, length=2)

        record_one = RecordOne(field_one="AAAAA", field_two=1111111)
        record_two = RecordOne(field_one="BBBBB", field_two=2222222)
        r = TestRecord(list_field=[record_one, record_two])

        self.assertEqual("AAAAA1111111BBBBB2222222", r.to_record())

    def test_to_record_pads_with_empty_records_when_not_all_records_used(self):
        class ListRecord(fixedwidth.Record):
            field_one = fields.StringField(length=5)
            field_two = fields.IntegerField(length=7)

        class TestRecord(fixedwidth.Record):
            list_field = fields.ListField(ListRecord, length=2)

        record_one = ListRecord(field_one="AAAAA", field_two=1111111)
        r = TestRecord(list_field=[record_one])

        self.assertEqual("AAAAA1111111     0000000", r.to_record())

    def test_check_record_length_returns_field_length_error_when_too_many_records_used(self):

        list_field = fields.ListField(RecordOne, length=2)
        list_field.attname = "list_field" # fake for test... fixedwidth sets this on instantiation

        record_one = RecordOne(field_one="AAAAA", field_two=1111111)
        record_two = RecordOne(field_one="BBBBB", field_two=2222222)
        record_three = RecordOne(field_one="CCCCC", field_two=3333333)

        records = [record_one, record_two, record_three]
        with self.assertRaises(fields.FieldLengthError) as e:
            list_field._check_record_length(''.join(r.to_record() for r in records))

        self.assertEqual("'list_field' contains 3 records but can only have 2.", e.exception.message)
