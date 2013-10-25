import unittest

from djcopybook.fixedwidth import fields


class StringFieldTests(unittest.TestCase):

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

    def test_to_python_returns_empty_string_when_received_all_blanks(self):
        field = fields.StringField(length=5)
        self.assertEqual("", field.to_python("     "))
