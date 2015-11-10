#!/usr/bin/env python

import sys
import unittest


if __name__ == "__main__":
    test_suite = unittest.TestLoader().discover("djcopybook")
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)

    sys.exit(not result.wasSuccessful)
