
from decimal import Decimal
from unittest import TestCase
from djcopybook.fixedwidth import fields


class ImpliedDecimalFieldTests(TestCase):

    def test_subclasses_decimal_field(self):
        self.assertTrue(issubclass(fields.ImpliedDecimalField, fields.DecimalField))

    def test_pads_number_when_zero_decimal(self):
        f = fields.ImpliedDecimalField(length=5, decimals=0)
        self.assertEqual('00300', f.to_record(300))

    def test_pads_number_when_two_decimals(self):
        f = fields.ImpliedDecimalField(length=7, decimals=2)
        self.assertEqual('0030025', f.to_record(300.25))

    def test_truncates_number_when_too_many_decimals(self):
        f = fields.ImpliedDecimalField(length=12, decimals=2)
        self.assertEqual('000003050025', f.to_record(30500.25325))

    def test_pads_decimal_number_type_appropriately(self):
        f = fields.ImpliedDecimalField(length=10, decimals=2)
        self.assertEqual('0007500075', f.to_record(Decimal("75000.75")))

    def test_value_of_none_is_all_zeros(self):
        f = fields.ImpliedDecimalField(length=8, decimals=2)
        self.assertEqual('00000000', f.to_record(None))

    def test_to_python_returns_decimal_type(self):
        f = fields.ImpliedDecimalField(length=10, decimals=2)
        self.assertEqual(Decimal("7500.33"), f.to_python("0000750033"))

    def test_to_python_returns_decimal_of_value_when_already_not_a_string(self):
        f = fields.ImpliedDecimalField(length=10, decimals=2)
        self.assertEqual(Decimal("750.33"), f.to_python(750.33))

    def test_to_python_returns_decimal_type_when_no_decimals_declared(self):
        f = fields.ImpliedDecimalField(length=10, decimals=0)
        self.assertEqual(Decimal("750033"), f.to_python("000750033"))

    def test_to_python_returns_None_when_value_is_None(self):
        f = fields.ImpliedDecimalField(length=10, decimals=2)
        self.assertEqual(None, f.to_python(None))

    def test_to_python_returns_None_when_value_is_empty_string(self):
        f = fields.ImpliedDecimalField(length=10, decimals=2)
        self.assertEqual(None, f.to_python("          "))
