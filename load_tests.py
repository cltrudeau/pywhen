#!/usr/bin/env python
import unittest, sys
from waelstow import discover_tests, list_tests

def get_suite(labels=[]):
    return discover_tests('unittests', labels)


if __name__ == '__main__':
    suite = get_suite(sys.argv[1:])
    unittest.TextTestRunner(verbosity=1).run(suite)
