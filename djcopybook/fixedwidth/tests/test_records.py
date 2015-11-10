import unittest

from djcopybook import fixedwidth
from djcopybook.fixedwidth import fields
from djcopybook.fixedwidth.tests import record_helper


class RecordTests(unittest.TestCase):

    def test_keeps_list_of_fields_in_order_when_record_is_instantiated(self):
        r = record_helper.RecordOne()
        self.assertEqual(['field_one', 'field_two'], list(r.fields.keys()))
        self.assertEqual(['field_one', 'field_two'], list(r.base_fields.keys()))

    def test_sets_auto_truncate_field_on_fields_when_instantiated(self):
        r = record_helper.RecordOne()

        self.assertEqual(2, len(r.fields))
        for field in r.fields.values():
            self.assertEqual(False, field.auto_truncate)

    def test_sets_auto_truncate_field_on_fields_when_turned_on(self):
        r = record_helper.RecordTwo()

        self.assertEqual(4, len(r.fields))
        for field in r.fields.values():
            self.assertEqual(True, field.auto_truncate)

    def test_record_inheritance_maintains_order(self):
        r = record_helper.RecordTwo()
        self.assertEqual(['field_one', 'field_two', 'field_three', 'field_four'], list(r.fields.keys()))
        self.assertEqual(['field_one', 'field_two', 'field_three', 'field_four'], list(r.base_fields.keys()))

    def test_fills_attributes_with_values_given_in_init(self):
        r = record_helper.RecordOne(field_one=10, field_two=5)
        self.assertEqual("10", r.field_one)
        self.assertEqual(5, r.field_two)

    def test_to_record_returns_record_for_each_field(self):
        r = record_helper.RecordOne(field_one="test", field_two=500)
        self.assertEqual("test 0000500", r.to_record())

    def test_returns_field_default_value_when_not_given(self):
        r = record_helper.RecordOne(field_two=10)
        self.assertEqual("AA", r.field_one)

    def test_ignores_kwarg_value_when_field_not_declared_on_record(self):
        r = record_helper.RecordOne(field_one="abc", no_field="test")
        self.assertEqual("abc", r.field_one)
        self.assertFalse(hasattr(r, "no_field"))

    def test_len_on_record_returns_total_fixed_width_length(self):
        r = record_helper.RecordOne()
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
        r = record_helper.RecordOne(field_one="test", field_two=500)
        self.assertEqual("test 0000500", str(r))

    def test_from_record_turns_fixed_width_string_to_record_object(self):
        r = record_helper.RecordOne.from_record("test 0000500")
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
            record_helper.RecordOne.from_record("test 000050")
        self.assertEqual("Fixed width record length is 11 but should be 12.", str(e.exception))

    def test_from_record_raises_value_error_when_fixed_width_string_greater_than_record_length(self):
        with self.assertRaises(ValueError) as e:
            record_helper.RecordOne.from_record("test 00005000")
        self.assertEqual("Fixed width record length is 13 but should be 12.", str(e.exception))

    def test_truncates_each_field_when_auto_truncate(self):

        class TruncRecord(fixedwidth.Record):
            auto_truncate = True

            char = fields.StringField(length=2)
            integer = fields.IntegerField(length=3)

        r = TruncRecord(char="Too long", integer=12345)
        record = r.to_record()
        self.assertEqual("To123", record)
