#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_package_db.py
    ~~~~~~~~~~~~~~~~~~
    
    package database test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json, http.server, os, shutil, tempfile, threading, \
  unittest

from g_sorcery import package_db, exceptions


class Server(threading.Thread):
    def __init__(self):
        super().__init__()
        server_address = ('127.0.0.1', 8080)
        self.httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    
    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        self.httpd.shutdown()


class TestFileJSON(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tempdir.name, 'tst')
        self.name = 'tst.json'

    def tearDown(self):
        del self.tempdir

    def do_test_read_ok(self, mandatories, value_suffix=""):
        f = package_db.FileJSON(self.path, self.name, mandatories)
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
        f = package_db.FileJSON(self.path, self.name, mandatories)
        mandatories.append("tst4")
        self.assertRaises(exceptions.FileJSONError, f.read)

    def do_test_write_ok(self):
        mandatories = ['tst1', 'tst2', 'tst3']
        content = {}
        for key in mandatories:
            content[key] = key + '_v'
        f = package_db.FileJSON(self.path, self.name, mandatories)
        f.write(content)
        self.assertTrue(os.path.isfile(os.path.join(self.path, self.name)))
        with open(os.path.join(self.path, self.name), 'r') as f:
            content_f = json.load(f)
        self.assertEqual(content, content_f)

    def test_write_missing_keys(self):
        content = {'tst1' : '', 'tst2' : ''}
        mandatories = ['tst1', 'tst2', 'tst3']
        f = package_db.FileJSON(self.path, self.name, mandatories)
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


class DummyDB(package_db.PackageDB):
    def __init__(self, directory, packages):
        super().__init__(directory)
        self.packages = packages

    def generate_tree(self):
        for category in [x.category for x in self.packages]:
            self.add_category(category)
        for package in self.packages:
            self.add_package(package)

    def get_real_db_uri(self):
        print(self.db_uri)
        return self.db_uri + '/dummy.tar.gz'


class TestDummyDB(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        category1 = 'app-test'
        category2 = 'dev-test'
        self.packages = [package_db.Package(category1, 'test', '0.2'),
            package_db.Package(category1, 'tst', '0.1'),
            package_db.Package(category1, 'dummy', '1'),
            package_db.Package(category2, 'test', '0.1'),
            package_db.Package(category2, 'test', '0.2'),
            package_db.Package(category2, 'tst', '0.1')]

    def tearDown(self):
        del self.tempdir

    def test_manifest(self):
        db = DummyDB(self.tempdir.name, self.packages)
        db.generate()
        self.assertEqual(db.check_manifest(), (True, []))

    def test_read(self):
        db = DummyDB(self.tempdir.name, self.packages)
        db.generate()
        db2 = DummyDB(self.tempdir.name, self.packages)
        db2.read()
        self.assertEqual(db.db, db2.db)

    def test_list_categories(self):
        db = DummyDB(self.tempdir.name, self.packages)
        db.generate()
        categories = list(set([x.category for x in self.packages]))
        self.assertEqual(categories, db.list_categories())

    def test_list_package_names(self):
        db = DummyDB(self.tempdir.name, self.packages)
        db.generate()
        categories = list(set([x.category for x in self.packages]))
        for category in categories:
            package_names = list(set([x.name for x in self.packages if x.category == category]))
            self.assertEqual(package_names, db.list_package_names(category))
        self.assertRaises(exceptions.InvalidKeyError, db.list_package_names, 'no_such_category')

    def test_list_package_versions(self):
        db = DummyDB(self.tempdir.name, self.packages)
        db.generate()
        categories = list(set([x.category for x in self.packages]))
        for category in categories:
            package_names = list(set([x.name for x in self.packages if x.category == category]))
            for name in package_names:
                versions = [x.version for x in self.packages if x.category == category and x.name == name]
                self.assertEqual(versions, db.list_package_versions(category, name))
        self.assertRaises(exceptions.InvalidKeyError, db.list_package_versions, 'no_such_category', 'a')
        self.assertRaises(exceptions.InvalidKeyError, db.list_package_versions,
                          categories[0], 'no_such_package')

    def test_sync(self):
        src_db = DummyDB(os.path.join(self.tempdir.name, 'src_testdb'), self.packages)
        src_db.generate()

        prev = os.getcwd()
        os.chdir(self.tempdir.name)
        os.system('tar cvzf dummy.tar.gz src_testdb')
        
        server = Server()
        server.start()

        db = DummyDB(os.path.join(self.tempdir.name, 'testdb'), self.packages)
        db.sync(db_uri='127.0.0.1:8080')
        
        server.shutdown()
        server.join()

        os.chdir(prev)

        self.assertEqual(src_db.db, db.db)

    def test_sync_fail(self):
        db = DummyDB(os.path.join(self.tempdir.name, 'testdb'), self.packages)
        self.assertRaises(exceptions.SyncError, db.sync, db_uri='127.0.0.1:8080')

    def test_get_max_version(self):
        db = DummyDB(os.path.join(self.tempdir.name, 'testdb'), self.packages)
        db.generate()
        self.assertEqual(db.get_max_version('dev-test', 'test'), '0.2')

            
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
    suite.addTest(TestDummyDB('test_manifest'))
    suite.addTest(TestDummyDB('test_read'))
    suite.addTest(TestDummyDB('test_list_categories'))
    suite.addTest(TestDummyDB('test_list_package_names'))
    suite.addTest(TestDummyDB('test_list_package_versions'))
    suite.addTest(TestDummyDB('test_sync'))
    suite.addTest(TestDummyDB('test_sync_fail'))
    suite.addTest(TestDummyDB('test_get_max_version'))
    return suite
