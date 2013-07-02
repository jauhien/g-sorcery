#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_package_db.py
    ~~~~~~~~~~~~~~~~~~
    
    package database test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json, os, shutil, tempfile, unittest

from g_sorcery import package_db, exceptions

from tests.server import Server

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
    suite.addTest(TestDummyDB('test_manifest'))
    suite.addTest(TestDummyDB('test_read'))
    suite.addTest(TestDummyDB('test_list_categories'))
    suite.addTest(TestDummyDB('test_list_package_names'))
    suite.addTest(TestDummyDB('test_list_package_versions'))
    suite.addTest(TestDummyDB('test_sync'))
    suite.addTest(TestDummyDB('test_sync_fail'))
    suite.addTest(TestDummyDB('test_get_max_version'))
    return suite
