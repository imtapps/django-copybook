import unittest

from djcopybook.fixedwidth import fields, Record
from djcopybook.fixedwidth.tests import record_helper


class BooleanFieldTests(unittest.TestCase):

    def test_to_record_returns_y_when_value_is_true(self):
        field = fields.BooleanField()
        self.assertEqual('Y', field.to_record(True))

    def test_to_record_returns_false_when_string_is_n(self):
        field = fields.BooleanField()
        self.assertEqual('N', field.to_record(False))

    def test_to_record_returns_when_string_is_empty_space(self):
        field = fields.BooleanField()
        self.assertEqual('N', field.to_record(' '))

    def test_to_record_returns_python_false_when_empty_string_is_empty(self):
        field = fields.BooleanField()
        self.assertEqual('N', field.to_record(''))

    def test_to_record_will_raise_exception_when_value_is_none(self):
        field = fields.BooleanField()
        with self.assertRaises(ValueError):
            field.to_record(field.to_record())

    def test_to_record_will_raise_exception_when_value_is_not_y_or_n(self):
        field = fields.BooleanField()
        with self.assertRaises(ValueError):
            field.to_record("X")

    def test_to_record_defaults_to_N(self):
        class SampleRecord(Record):
            indicator = fields.BooleanField()

        r = SampleRecord()
        self.assertEqual("N", r.to_record())

    def test_to_record_allows_default_override(self):
        class SampleRecord(Record):
            indicator = fields.BooleanField(default=True)

        r = SampleRecord()
        self.assertEqual("Y", r.to_record())

    def test_from_record_will_return_the_correct_boolean_values(self):
        r = record_helper.RecordSix.from_record("YN ")
        self.assertEqual(True, r.first)
        self.assertEqual(False, r.second)
        self.assertEqual(False, r.third)
