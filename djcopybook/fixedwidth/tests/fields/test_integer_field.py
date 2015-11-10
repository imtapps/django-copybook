import unittest

from djcopybook.fixedwidth import fields


class IntegerFieldTests(unittest.TestCase):

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

    def test_to_python_returns_none_when_value_is_empty_string(self):
        field = fields.IntegerField(length=5)
        self.assertEqual(None, field.to_python("     "))

    def test_to_python_raises_value_error_when_value_given_has_characters(self):
        field = fields.IntegerField(length=5)
        with self.assertRaises(ValueError):
            self.assertEqual(None, field.to_python("0001A"))
