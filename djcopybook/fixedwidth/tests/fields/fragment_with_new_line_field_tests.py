import unittest

from djcopybook.fixedwidth import fields
from djcopybook.fixedwidth.tests import record_helper


class FragmentWithNewlineFieldTests(unittest.TestCase):

    def test_is_subclass_of_fragment_field(self):
        self.assertTrue(issubclass(fields.FragmentWithNewlineField, fields.FragmentField))

    def test_to_python_returns_record_instance_when_given_string(self):
        f = fields.FragmentWithNewlineField(record=record_helper.RecordOne)
        python_val = f.to_python('AAAAA1111111')
        self.assertIsInstance(python_val, record_helper.RecordOne)

    def test_to_record_returns_record_class_defaults_when_value_is_None(self):
        f = fields.FragmentWithNewlineField(record=record_helper.RecordOne)
        self.assertEqual("AA   0000000\n", f.to_record(None))

    def test_to_record_will_modify_the_length_by_one_to_account_for_newline(self):
        my_record = record_helper.RecordOne(field_one="aa", field_two=999)
        r = record_helper.RecordFour(frag=my_record, other_field="ZZZ")
        self.assertEqual(16, len(str(r)))

    def test_to_record_returns_string_of_record_when_has_explicit_values(self):
        my_record = record_helper.RecordOne(field_one="aa", field_two=999)
        r = record_helper.RecordFour(frag=my_record, other_field="ZZZ")
        self.assertEqual("aa   0000999\nZZZ", r.to_record())

    def test_to_record_returns_string_of_record_when_explicitly_set(self):
        r = record_helper.RecordFour(other_field="ZZZ")
        self.assertEqual("AA   0000000\nZZZ", r.to_record())

    def test_creates_record_object_properly_from_string(self):
        r = record_helper.RecordFour.from_record("aaaaa9999999ZZZ")
        self.assertEqual("aaaaa", r.frag.field_one)
        self.assertEqual(9999999, r.frag.field_two)
        self.assertEqual("ZZZ", r.other_field)
        self.assertIsInstance(r.frag, record_helper.RecordOne)

    def test_creates_record_object_properly_from_string_with_multiple_values(self):
        r = record_helper.RecordFour()
        r.frag.field_one = "aaa"
        r.frag.field_two = 999

        self.assertEqual("aaa  0000999\nEEE", r.to_record())
