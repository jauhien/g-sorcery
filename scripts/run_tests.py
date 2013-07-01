#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    run_tests.py
    ~~~~~~~~~~~~
    
    a simple script that runs all the tests from the *tests* directory
    (.py files)
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import sys
import unittest

root_dir = os.path.realpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'
))

tests_dir = os.path.join(root_dir, 'tests')

# adding the tests directory to the top of the PYTHONPATH
sys.path = [root_dir, tests_dir] + sys.path

os.environ["PYTHONPATH"] = ':'.join([root_dir, tests_dir])

suites = []

# getting the test suites from the python modules (files that ends whit .py)
for f in os.listdir(tests_dir):
    if not f.endswith('.py') or not f.startswith('test_'):
        continue
    try:
        my_test = __import__(f[:-len('.py')])
    except ImportError:
        continue
    
    # all the python modules MUST have a 'suite' method, that returns the
    # test suite of the module
    suites.append(my_test.suite())

# unifying all the test suites in only one
suites = unittest.TestSuite(suites)

# creating the Test Runner object
test_runner = unittest.TextTestRunner(descriptions=2, verbosity=2)

# running the tests
result = test_runner.run(suites)

if result.failures or result.errors:
    sys.exit(1)
