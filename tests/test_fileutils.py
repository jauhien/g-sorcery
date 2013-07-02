#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    fileutils.py
    ~~~~~~~~~~~~
    
    file utilities test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json, os, shutil, tempfile, unittest

from g_sorcery import exceptions, fileutils

from tests.base import BaseTest

class TestFileJSON(BaseTest):
    
    def setUp(self):
        super().setUp()
        self.path = os.path.join(self.tempdir.name, 'tst')
        self.name = 'tst.json'

    def do_test_read_ok(self, mandatories, value_suffix=""):
        f = fileutils.FileJSON(self.path, self.name, mandatories)
        content = f.read()
        for key in mandatories:
            self.assertTrue(key in content)
            if value_suffix:
                value = key + value_suffix
            else:
                value = ""
            self.assertEqual(content[key], value)
        self.assertTrue(os.path.isfile(os.path.join(self.path, self.name)))
        with open(os.path.join(self.path, self.name), 'r') as f:
            content_f = json.load(f)
        self.assertEqual(content, content_f)
        
    def test_read_dir_does_not_exist(self):
        mandatories = ['tst1', 'tst2', 'tst3']
        self.do_test_read_ok(mandatories)

    def test_read_file_does_not_exist(self):
        os.makedirs(self.path)
        mandatories = ['tst1', 'tst2', 'tst3']
        self.do_test_read_ok(mandatories)

    def test_read_all_keys(self):
        os.makedirs(self.path)
        mandatories = ['tst1', 'tst2', 'tst3']
        content = {}
        for key in mandatories:
            content[key] = key + "_v"
        with open(os.path.join(self.path, self.name), 'w') as f:
            json.dump(content, f)
        self.do_test_read_ok(mandatories, "_v")

    def test_read_missing_keys(self):
        os.makedirs(self.path)
        mandatories = ['tst1', 'tst2', 'tst3']
        content = {}
        for key in mandatories:
            content[key] = key + "_v"
        with open(os.path.join(self.path, self.name), 'w') as f:
            json.dump(content, f)
        f = fileutils.FileJSON(self.path, self.name, mandatories)
        mandatories.append("tst4")
        self.assertRaises(exceptions.FileJSONError, f.read)

    def do_test_write_ok(self):
        mandatories = ['tst1', 'tst2', 'tst3']
        content = {}
        for key in mandatories:
            content[key] = key + '_v'
        f = fileutils.FileJSON(self.path, self.name, mandatories)
        f.write(content)
        self.assertTrue(os.path.isfile(os.path.join(self.path, self.name)))
        with open(os.path.join(self.path, self.name), 'r') as f:
            content_f = json.load(f)
        self.assertEqual(content, content_f)

    def test_write_missing_keys(self):
        content = {'tst1' : '', 'tst2' : ''}
        mandatories = ['tst1', 'tst2', 'tst3']
        f = fileutils.FileJSON(self.path, self.name, mandatories)
        self.assertRaises(exceptions.FileJSONError, f.write, content)

    def test_write_dir_does_not_exist(self):
        self.do_test_write_ok()

    def test_write_file_does_not_exist(self):
        os.makedirs(self.path)
        self.do_test_write_ok()

    def test_write_all_keys(self):
        os.makedirs(self.path)
        mandatories = ['tst11', 'tst12']
        content = {}
        for key in mandatories:
            content[key] = key + "_v"
        with open(os.path.join(self.path, self.name), 'w') as f:
            json.dump(content, f)
        self.do_test_write_ok()

        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestFileJSON('test_read_dir_does_not_exist'))
    suite.addTest(TestFileJSON('test_read_file_does_not_exist'))
    suite.addTest(TestFileJSON('test_read_all_keys'))
    suite.addTest(TestFileJSON('test_read_missing_keys'))
    suite.addTest(TestFileJSON('test_write_missing_keys'))
    suite.addTest(TestFileJSON('test_write_dir_does_not_exist'))
    suite.addTest(TestFileJSON('test_write_file_does_not_exist'))
    suite.addTest(TestFileJSON('test_write_all_keys'))
    return suite
