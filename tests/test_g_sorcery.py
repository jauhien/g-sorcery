#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_g_sorcery.py
    ~~~~~~~~~~~~~~~~~
    
    executable and main module test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os, subprocess, tempfile, unittest

class TestBin(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        del self.tempdir

    def test_g_sorcery(self):
        binpath = os.path.join(os.path.split(
            os.path.dirname(os.path.realpath(__file__)))[0], 'bin')
        binary = os.path.join(binpath, 'g-sorcery')
        self.assertEqual(subprocess.check_output(binary),  b'it works\n')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBin('test_g_sorcery'))
    return suite
