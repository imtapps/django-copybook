import unittest

from djcopybook.fixedwidth import fields
from djcopybook.fixedwidth.tests.record_helper import RecordOne


class FixedWidthFieldTests(unittest.TestCase):

    def get_field(self, auto_truncate=False, **kwargs):
        f = fields.FixedWidthField(**kwargs)
        f.attname = "field_one"
        f.auto_truncate = auto_truncate
        return f

    def test_raises_field_length_error_when_value_is_longer_than_allowed(self):
        f = self.get_field(length=5)
        with self.assertRaises(fields.FieldLengthError) as e:
            f.get_record_value("This is a long")

        msg = "'field_one' value 'This is a long' is longer than 5 chars."
        self.assertEqual(msg, str(e.exception))

    def test_truncates_field_length_when_has_auto_truncate_on(self):
        f = self.get_field(auto_truncate=True, length=5)
        val = f.get_record_value("This is too long")
        self.assertEqual("This ", val)

    def test_get_default_returns_none_when_no_default(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual(None, field.get_default())

    def test_get_default_returns_default_when_present(self):
        field = fields.FixedWidthField(length=5, default="ABC")
        self.assertEqual("ABC", field.get_default())

    def test_get_default_returns_called_default_when_callable(self):
        def get_default():
            return "Default Value"

        field = fields.FixedWidthField(length=15, default=get_default)
        self.assertEqual("Default Value", field.get_default())

    def test_to_record_returns_string_of_value_padded_to_length(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual("ALM  ", field.to_record("ALM"))

    def test_to_record_returns_padded_blank_string_when_value_is_None(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual("     ", field.to_record(None))

    def test_to_python_turns_value_to_string(self):
        field = fields.FixedWidthField(length=5)
        python_val = field.to_python(10)
        self.assertEqual("10", python_val)
        self.assertIsInstance(python_val, str)

    def test_to_python_strips_extra_padding_from_right(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual("AA", field.to_python("AA   "))

    def test_to_python_returns_none_when_value_is_none(self):
        field = fields.FixedWidthField(length=5)
        self.assertEqual(None, field.to_python(None))

    def test_returns_default_when_removed_from_record(self):
        record = RecordOne()
        record_dir = dir(record)
        for item in record_dir:
            if item.startswith('field_one'):
                field_name = item
        delattr(record, field_name)
        self.assertEqual('AA', record.field_one)
