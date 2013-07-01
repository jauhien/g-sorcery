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
        
        binpath = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'bin')
        self.binary = os.path.join(binpath, 'g-sorcery')

    def tearDown(self):
        del self.tempdir

    def test_g_sorcery(self):
        self.assertEqual(subprocess.check_output(self.binary),  b'g-sorcery\n')

    def test_nonexistent_backend(self):
        prev = os.getcwd()
        os.chdir(self.tempdir.name)
        os.system('ln -s ' + self.binary + ' g-nonexistent')
        self.assertRaises(subprocess.CalledProcessError, subprocess.check_output, './g-nonexistent')
        os.chdir(prev)

    def test_empty_config(self):
        prev = os.getcwd()
        os.chdir(self.tempdir.name)
        os.system('ln -s ' + self.binary + ' g-empty')
        os.system('echo {} > ./g-empty.json')
        self.assertRaises(subprocess.CalledProcessError, subprocess.check_output, './g-empty')
        os.chdir(prev)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBin('test_g_sorcery'))
    suite.addTest(TestBin('test_nonexistent_backend'))
    suite.addTest(TestBin('test_empty_config'))
    return suite
