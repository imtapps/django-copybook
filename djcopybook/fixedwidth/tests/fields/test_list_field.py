import unittest

from djcopybook import fixedwidth
from djcopybook.fixedwidth import fields
from djcopybook.fixedwidth.tests import record_helper


class ListFieldTests(unittest.TestCase):

    def test_to_python_returns_list_of_records(self):
        f = fields.ListField(record=record_helper.RecordOne, length=2)
        records = [record_helper.RecordOne(), record_helper.RecordOne()]
        python_val = f.to_python(records)
        self.assertEqual(records, python_val)
        self.assertIsInstance(python_val, list)

    def test_to_python_returns_list_of_records_when_given_string(self):
        f = fields.ListField(record=record_helper.RecordOne, length=2)

        records = f.to_python("ABCDE1111111ZYXWV9999999")
        self.assertEqual(len(records), 2)

        record_one = records[0]
        self.assertEqual("ABCDE", record_one.field_one)
        self.assertEqual(1111111, record_one.field_two)

        record_two = records[1]
        self.assertEqual("ZYXWV", record_two.field_one)
        self.assertEqual(9999999, record_two.field_two)

    def test_to_python_returns_list_of_records_when_given_unicode(self):
        f = fields.ListField(record=record_helper.RecordOne, length=2)

        records = f.to_python(u"ABCDE1111111ZYXWV9999999")
        self.assertEqual(len(records), 2)

        record_one = records[0]
        self.assertEqual("ABCDE", record_one.field_one)
        self.assertEqual(1111111, record_one.field_two)

        record_two = records[1]
        self.assertEqual("ZYXWV", record_two.field_one)
        self.assertEqual(9999999, record_two.field_two)

    def test_to_python_raises_type_error_when_not_given_record_class_instances(self):
        f = fields.ListField(record=record_helper.RecordOne, length=2)
        records = [record_helper.RecordOne(), fixedwidth.Record()]

        with self.assertRaises(TypeError) as e:
            f.to_python(records)
        self.assertEqual("List field must contain instances of 'RecordOne'.", str(e.exception))

    def test_defaults_field_to_empty_list_when_no_records_initially_given(self):
        class TestRecord(fixedwidth.Record):
            field_one = fields.ListField(record_helper.RecordOne, length=2)

        r = TestRecord()
        self.assertEqual([], r.field_one)

    def test_to_record_returns_string_of_all_records_from_list_field(self):
        class TestRecord(fixedwidth.Record):
            list_field = fields.ListField(record_helper.RecordOne, length=2)

        record_one = record_helper.RecordOne(field_one="AAAAA", field_two=1111111)
        record_two = record_helper.RecordOne(field_one="BBBBB", field_two=2222222)
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

        list_field = fields.ListField(record_helper.RecordOne, length=2)
        list_field.attname = "list_field"

        record_one = record_helper.RecordOne(field_one="AAAAA", field_two=1111111)
        record_two = record_helper.RecordOne(field_one="BBBBB", field_two=2222222)
        record_three = record_helper.RecordOne(field_one="CCCCC", field_two=3333333)

        records = [record_one, record_two, record_three]
        with self.assertRaises(fields.FieldLengthError) as e:
            list_field._check_record_length(''.join(r.to_record() for r in records))

        self.assertEqual("'list_field' contains 3 records but can only have 2.", str(e.exception))

    def test_populates_list_field_with_nested_dictionaries(self):
        input_data = {'threeve': [
            {'other_field': 'xyz', 'frag': {'field_one': 1, 'field_two': 2}},
            {'other_field': 'abc', 'frag': {'field_one': 3, 'field_two': 4}}
        ]}
        record = record_helper.RecordFive(**input_data)
        self.assertEqual('xyz', record.threeve[0].other_field)
        self.assertEqual('abc', record.threeve[1].other_field)
        self.assertEqual('1', record.threeve[0].frag.field_one)
        self.assertEqual('3', record.threeve[1].frag.field_one)
        self.assertEqual(2, record.threeve[0].frag.field_two)
        self.assertEqual(4, record.threeve[1].frag.field_two)
