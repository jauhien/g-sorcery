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

from g_sorcery import g_sorcery

from tests.dummy_backend import backend as dummyBackend

from tests.base import BaseTest

class TestBin(BaseTest):
    def setUp(self):
        super().setUp()
        
        binpath = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'bin')
        self.binary = os.path.join(binpath, 'g-sorcery')

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

    def test_config(self):
        prev = os.getcwd()
        os.chdir(self.tempdir.name)
        os.system('ln -s ' + self.binary + ' g-dummy')
        os.system('echo {\\"package\\": \\"dummy_backend\\"} > ./g-dummy.json')
        self.assertEqual(subprocess.check_output('./g-dummy').decode("utf-8")[:-1],
                         dummyBackend.instance.test())
        os.chdir(prev)

class TestGSorcery(BaseTest):

    def test_get_backend(self):
        self.assertEqual(g_sorcery.get_backend('nonexistent_backend'), None)
        self.assertEqual(g_sorcery.get_backend('dummy_backend'), dummyBackend.instance)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBin('test_g_sorcery'))
    suite.addTest(TestBin('test_nonexistent_backend'))
    suite.addTest(TestBin('test_empty_config'))
    suite.addTest(TestBin('test_config'))
    suite.addTest(TestGSorcery('test_get_backend'))
    return suite
