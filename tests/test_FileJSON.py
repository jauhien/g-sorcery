#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_FileJSON.py
    ~~~~~~~~~~~~~~~~

    FileJSON test suite

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json
import os
import unittest

from g_sorcery.fileutils import FileJSON
from g_sorcery.exceptions import FileJSONError
from g_sorcery.g_collections import serializable_elist

from tests.base import BaseTest
from tests.serializable import NonSerializableClass, SerializableClass, DeserializableClass

class TestFileJSON(BaseTest):
    def setUp(self):
        super(TestFileJSON, self).setUp()
        self.directory = os.path.join(self.tempdir.name, 'tst')
        self.name = 'tst.json'
        self.path = os.path.join(self.directory, self.name)

    def test_read_nonexistent(self):
        fj = FileJSON(self.directory, self.name, [])
        content = fj.read()
        self.assertEqual(content, {})
        self.assertTrue(os.path.isfile(self.path))

    def test_read_nonexistent_mandatory_key(self):
        fj = FileJSON(self.directory, self.name, ["mandatory1", "mandatory2"])
        content = fj.read()
        self.assertEqual(content, {"mandatory1":"", "mandatory2":""})
        self.assertTrue(os.path.isfile(self.path))

    def test_read_luck_of_mandatory_key(self):
        fj = FileJSON(self.directory, self.name, ["mandatory"])
        os.makedirs(self.directory)
        with open(self.path, 'w') as f:
            json.dump({"test":"test"}, f)
        self.assertRaises(FileJSONError, fj.read)

    def test_write_luck_of_mandatory_key(self):
        fj = FileJSON(self.directory, self.name, ["mandatory"])
        self.assertRaises(FileJSONError, fj.write, {"test":"test"})

    def test_write_read(self):
        fj = FileJSON(self.directory, self.name, ["mandatory"])
        content = {"mandatory":"1", "test":"2"}
        fj.write(content)
        content_r = fj.read()
        self.assertEqual(content, content_r)

    def test_serializable(self):
        fj = FileJSON(self.directory, self.name, [])
        content = SerializableClass("1", "2")
        fj.write(content)
        content_r = fj.read()
        self.assertEqual(content_r, {"field1":"1", "field2":"2"})
        self.assertRaises(TypeError, fj.write, NonSerializableClass())

    def test_deserializable(self):
        fj = FileJSON(self.directory, self.name, [])
        content = DeserializableClass("1", "2")
        fj.write(content)
        content_r = fj.read()
        self.assertEqual(content, content_r)

    def test_deserializable_collection(self):
        fj = FileJSON(self.directory, self.name, [])
        content1 = DeserializableClass("1", "2")
        content2 = DeserializableClass("3", "4")
        content = serializable_elist([content1, content2])
        fj.write(content)
        content_r = fj.read()
        self.assertEqual(content, content_r)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestFileJSON('test_read_nonexistent'))
    suite.addTest(TestFileJSON('test_read_nonexistent_mandatory_key'))
    suite.addTest(TestFileJSON('test_read_luck_of_mandatory_key'))
    suite.addTest(TestFileJSON('test_write_luck_of_mandatory_key'))
    suite.addTest(TestFileJSON('test_write_read'))
    suite.addTest(TestFileJSON('test_serializable'))
    suite.addTest(TestFileJSON('test_deserializable'))
    suite.addTest(TestFileJSON('test_deserializable_collection'))
    return suite
