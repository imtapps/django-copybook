import unittest

from djcopybook.fixedwidth import fields


class PaddingTests(unittest.TestCase):

    def test_str_padding_pads_right_with_spaces(self):
        self.assertEqual("ALM   ", fields.str_padding(6, "ALM"))
        self.assertEqual("5     ", fields.str_padding(6, 5))

    def test_int_right_padding_pads_right_with_zeros(self):
        self.assertEqual("110000", fields.int_padding(6, 11, "<"))
        self.assertEqual("110000", fields.int_padding(6, "11", "<"))

    def test_int_padding_pads_left_with_zeros(self):
        self.assertEqual("000010", fields.int_padding(6, 10))
        self.assertEqual("000010", fields.int_padding(6, "10"))

    def test_float_padding_pads_left_and_decimals_with_zeros(self):
        self.assertEqual("000010", fields.float_padding(6, 10, 0))
        self.assertEqual("000010", fields.float_padding(6, "10", 0))

        self.assertEqual("00300.12", fields.float_padding(8, 300.1234, 2))
        self.assertEqual("010.12", fields.float_padding(6, "10.1234", 2))
        self.assertEqual("010.10", fields.float_padding(6, "10.1", 2))
        self.assertEqual("010.00", fields.float_padding(6, 10, 2))

        self.assertEqual("000010.123", fields.float_padding(10, 10.1234, 3))
        self.assertEqual("0005.123", fields.float_padding(8, "5.1234", 3))
