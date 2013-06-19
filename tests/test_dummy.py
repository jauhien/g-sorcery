#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_dummy.py
    ~~~~~~~~~~~~~
    
    dummy test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import unittest

class TestDummy(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_dummy(self):
        self.assertEqual('works', 'works')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDummy('test_dummy'))
    return suite
