#!/usr/bin/env python

import sys
import unittest
from xmlrunner import XMLTestRunner

if __name__ == "__main__":
    py_version = "v{0}{1}".format(*sys.version_info[:2])
    test_suite = unittest.TestLoader().discover("djcopybook")
    runner = XMLTestRunner(verbosity=2, output="jenkins_reports", outsuffix=py_version)
    result = runner.run(test_suite)

    sys.exit(not result.wasSuccessful)
