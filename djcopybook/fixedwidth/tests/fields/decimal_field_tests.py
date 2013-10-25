import unittest

from djcopybook.fixedwidth import fields


class DecimalFieldTests(unittest.TestCase):

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

    def test_to_python_returns_none_when_value_is_empty_string(self):
        field = fields.DecimalField(length=5)
        self.assertEqual(None, field.to_python("     "))

    def test_to_python_raises_value_error_when_value_given_has_characters(self):
        field = fields.DecimalField(length=5)
        with self.assertRaises(ValueError):
            self.assertEqual(None, field.to_python("0001A"))
