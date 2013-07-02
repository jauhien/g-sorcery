#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_elpa_db.py
    ~~~~~~~~~~~~~~~
    
    ELPA package database test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import http.server, tempfile, threading, unittest

from g_elpa import elpa_db

class TestElpaDB(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        del self.tempdir

    def test_generate(self):
        edb = elpa_db.ElpaDB(self.tempdir.name, repo_uri = 'http://elpa.gnu.org/packages/')
        edb.generate_tree()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestElpaDB('test_generate'))
    return suite
