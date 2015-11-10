import unittest

from djcopybook.fixedwidth import fields


class NewLineFieldTests(unittest.TestCase):

    def test_to_record_returns_new_line_character(self):
        field = fields.NewLineField()
        self.assertEqual("\n", field.to_record("\n"))

    def test_to_python_turns_value_to_string(self):
        field = fields.NewLineField()
        python_val = field.to_python("\n")
        self.assertEqual("\n", python_val)
        self.assertIsInstance(python_val, str)
