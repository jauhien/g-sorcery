#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_PackageDB.py
    ~~~~~~~~~~~~~~~~

    PackageDB test suite

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import time
import unittest

from g_sorcery.compatibility import TemporaryDirectory
from g_sorcery.exceptions import IntegrityError, InvalidKeyError, SyncError
from g_sorcery.g_collections import Package
from g_sorcery.package_db import PackageDB

from tests.base import BaseTest
from tests.server import Server


class TestDB(PackageDB):
    def get_real_db_uri(self, db_uri):
        return db_uri + "/dummy.tar.gz"


class TestPackageDB(BaseTest):

    def test_functionality(self):
        orig_tempdir = TemporaryDirectory()
        orig_path = os.path.join(orig_tempdir.name, "db")
        os.makedirs(orig_path)
        orig_db = PackageDB(orig_path)
        orig_db.add_category("app-test1")
        orig_db.add_category("app-test2")
        ebuild_data = {"test1": "test1", "test2": "test2"}
        packages = [Package("app-test1", "test", "1"), Package("app-test1", "test", "2"),
                    Package("app-test1", "test1", "1"), Package("app-test2", "test2", "1")]
        for package in packages:
            orig_db.add_package(package, ebuild_data)

        orig_db.write()
        os.system("cd " + orig_tempdir.name + " && tar cvzf good.tar.gz db")
        os.system("echo invalid >> " + orig_tempdir.name + "/db/app-test1/packages.json")
        os.system("cd " + orig_tempdir.name + " && tar cvzf dummy.tar.gz db")

        test_db = TestDB(self.tempdir.name)
        self.assertRaises(SyncError, test_db.sync, "127.0.0.1:8080")

        srv = Server(orig_tempdir.name)
        srv.start()
        self.assertRaises(IntegrityError, test_db.sync, "127.0.0.1:8080")
        os.system("cd " + orig_tempdir.name + " && mv good.tar.gz dummy.tar.gz")
        test_db.sync("127.0.0.1:8080")
        srv.shutdown()
        srv.join()
        test_db.read()
        self.assertEqual(orig_db.database, test_db.database)
        self.assertEqual(set(test_db.list_categories()), set(["app-test1", "app-test2"]))
        self.assertTrue(test_db.in_category("app-test1", "test"))
        self.assertFalse(test_db.in_category("app-test2", "test"))
        self.assertRaises(InvalidKeyError, test_db.in_category, "app-test3", "test")
        self.assertEqual(set(test_db.list_package_names("app-test1")), set(['test', 'test1']))
        self.assertEqual(set(test_db.list_catpkg_names()),set(['app-test1/test', 'app-test1/test1', 'app-test2/test2']))
        self.assertRaises(InvalidKeyError, test_db.list_package_versions, "invalid", "test")
        self.assertRaises(InvalidKeyError, test_db.list_package_versions, "app-test1", "invalid")
        self.assertEqual(set(test_db.list_package_versions("app-test1", "test")), set(['1', '2']))
        self.assertEqual(set(test_db.list_all_packages()), set(packages))
        self.assertEqual(test_db.get_package_description(packages[0]), ebuild_data)
        self.assertRaises(KeyError, test_db.get_package_description, Package("invalid", "invalid", "1"))
        self.assertEqual(test_db.get_max_version("app-test1", "test"), "2")
        self.assertEqual(test_db.get_max_version("app-test1", "test1"), "1")
        self.assertRaises(InvalidKeyError, test_db.get_max_version, "invalid", "invalid")
        pkg_set = set(packages)
        for package, data in test_db:
            self.assertTrue(package in pkg_set)
            self.assertEqual(data, ebuild_data)
            pkg_set.remove(package)
        self.assertTrue(not pkg_set)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPackageDB('test_functionality'))
    return suite
