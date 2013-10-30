import unittest

from djcopybook.fixedwidth import fields
from djcopybook.fixedwidth.tests import record_helper


class FragmentFieldTests(unittest.TestCase):

    def test_to_record_returns_record_class_defaults_when_value_is_None(self):
        field = fields.FragmentField(record=record_helper.RecordOne)
        self.assertEqual("AA   0000000", field.to_record(None))

    def test_to_python_returns_record_instance_when_none_given(self):
        f = fields.FragmentField(record=record_helper.RecordOne)
        python_val = f.to_python(None)
        self.assertIsInstance(python_val, record_helper.RecordOne)

    def test_to_python_returns_record_instance_when_given_string(self):
        f = fields.FragmentField(record=record_helper.RecordOne)
        python_val = f.to_python('AAAAA1111111')
        self.assertIsInstance(python_val, record_helper.RecordOne)

    def test_to_python_returns_record_instance_when_given_instance(self):
        record = record_helper.RecordOne()
        f = fields.FragmentField(record=record_helper.RecordOne)
        python_val = f.to_python(record)
        self.assertIsInstance(python_val, record_helper.RecordOne)

    def test_to_python_raises_type_error_when_receives_bad_input(self):
        f = fields.FragmentField(record=record_helper.RecordOne)
        with self.assertRaises(TypeError) as ctx:
            f.to_python(222)
        self.assertEqual("Redefined field must be a string or RecordOne instance.", str(ctx.exception))

    def test_to_record_returns_string_of_record_when_explicitly_set(self):
        r = record_helper.RecordThree(other_field="ZZZ")
        self.assertEqual("AA   0000000ZZZ", r.to_record())

    def test_to_record_returns_string_of_record_when_has_explicit_values(self):
        my_record = record_helper.RecordOne(field_one="aa", field_two=999)
        r = record_helper.RecordThree(frag=my_record, other_field="ZZZ")
        self.assertEqual("aa   0000999ZZZ", r.to_record())

    def test_creates_record_object_properly_from_string(self):
        r = record_helper.RecordThree.from_record("aaaaa9999999ZZZ")
        self.assertEqual("aaaaa", r.frag.field_one)
        self.assertEqual(9999999, r.frag.field_two)
        self.assertEqual("ZZZ", r.other_field)
        self.assertIsInstance(r.frag, record_helper.RecordOne)

    def test_creates_record_object_properly_from_unicode(self):
        r = record_helper.RecordThree.from_record(u"aaaaa9999999ZZZ")
        self.assertEqual("aaaaa", r.frag.field_one)
        self.assertEqual(9999999, r.frag.field_two)
        self.assertEqual("ZZZ", r.other_field)
        self.assertIsInstance(r.frag, record_helper.RecordOne)

    def test_creates_record_object_properly_from_string_with_multiple_values(self):
        r = record_helper.RecordThree()
        r.frag.field_one = "aaa"
        r.frag.field_two = 999

        self.assertEqual("aaa  0000999BBB", r.to_record())

    def test_populates_nested_dictionaries(self):
        input_data = {'garf': {'frag': {'field_one': 'abc', 'field_two': 100}}}
        my_record = record_helper.RecordFive(**input_data)
        self.assertEqual(my_record.garf.frag.field_one, 'abc')
        self.assertEqual(my_record.garf.frag.field_two, 100)
        self.assertEqual('abc  0000100\nEEE\nAA   0000000BBBAA   0000000BBB', str(my_record))
