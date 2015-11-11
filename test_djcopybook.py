#!/usr/bin/env python

import sys
import unittest
from xmlrunner import XMLTestRunner


if __name__ == "__main__":
    test_suite = unittest.TestLoader().discover("djcopybook")
    runner = XMLTestRunner(verbosity=2, output="jenkins_reports")
    result = runner.run(test_suite)

    sys.exit(not result.wasSuccessful)
