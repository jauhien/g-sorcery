#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
    
    base class for tests
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import unittest

from g_sorcery.compatibility import TemporaryDirectory

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = TemporaryDirectory()

    def tearDown(self):
        del self.tempdir
