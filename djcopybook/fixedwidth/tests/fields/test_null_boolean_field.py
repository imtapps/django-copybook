
from unittest import TestCase
from djcopybook.fixedwidth import fields, Record


class NullBooleanFieldTests(TestCase):

    def test_subclasses_BooleanField(self):
        self.assertTrue(issubclass(fields.NullBooleanField, fields.BooleanField))

    def test_to_record_returns_y_when_value_is_true(self):
        field = fields.NullBooleanField()
        self.assertEqual('Y', field.to_record(True))

    def test_to_record_returns_n_when_value_is_false(self):
        field = fields.NullBooleanField()
        self.assertEqual('N', field.to_record(False))

    def test_to_record_returns_empty_when_string_is_empty_space(self):
        field = fields.NullBooleanField()
        self.assertEqual(' ', field.to_record(' '))

    def test_to_record_returns_empty_when_value_is_None(self):
        field = fields.NullBooleanField()
        self.assertEqual(' ', field.to_record(None))

    def test_to_record_defaults_to_empty(self):
        class SampleRecord(Record):
            indicator = fields.NullBooleanField()

        r = SampleRecord()
        self.assertEqual(" ", r.to_record())

    def test_to_record_allows_default_override(self):
        class SampleRecord(Record):
            indicator = fields.NullBooleanField(default=True)

        r = SampleRecord()
        self.assertEqual("Y", r.to_record())

    def test_to_record_raises_value_error_when_data_type_invalid(self):
        field = fields.NullBooleanField()
        with self.assertRaises(ValueError) as e:
            field.to_record("My Cat")
        self.assertEqual("Value Must be Boolean or None. You gave 'My Cat'", str(e.exception))

    def test_to_python_returns_True_when_value_is_Y(self):
        field = fields.NullBooleanField()
        self.assertEqual(True, field.to_python("Y"))

    def test_to_python_returns_False_when_value_is_N(self):
        field = fields.NullBooleanField()
        self.assertEqual(False, field.to_python("N"))

    def test_to_python_returns_None_when_value_is_empty(self):
        field = fields.NullBooleanField()
        self.assertEqual(None, field.to_python(" "))

    def test_to_python_returns_value_when_already_boolean(self):
        field = fields.NullBooleanField()
        self.assertEqual(True, field.to_python(True))
