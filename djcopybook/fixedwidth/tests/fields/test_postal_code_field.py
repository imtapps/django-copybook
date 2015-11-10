import unittest

from djcopybook.fixedwidth import fields


class PostalCodeFieldTests(unittest.TestCase):

    def setUp(self):
        self.field = fields.PostalCodeField()

    def test_postal_code_field_length_is_set_to_nine(self):
        self.assertEqual(9, self.field.length)

    def test_to_record_returns_string_of_value_padded_to_length_if_string(self):
        self.assertEqual("AA       ", self.field.to_record("AA"))

    def test_to_record_returns_padded_blank_string_when_value_is_None(self):
        self.assertEqual("         ", self.field.to_record(None))

    def test_to_record_returns_number_of_value_padded_to_right_of_length_if_number(self):
        self.assertEqual("990000000", self.field.to_record(99))
        self.assertEqual("990000000", self.field.to_record("99"))

    def test_to_python_turns_value_to_string(self):
        python_val = self.field.to_python("K1A XXX")
        self.assertEqual("K1A XXX", python_val)
        self.assertIsInstance(python_val, str)

    def test_to_python_turns_value_to_string_if_integer(self):
        python_val = self.field.to_python(50401)
        self.assertEqual("50401", python_val)
        self.assertIsInstance(python_val, str)
