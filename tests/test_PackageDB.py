#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_PackageDB.py
    ~~~~~~~~~~~~~~~~
    
    PackageDB test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import time
import unittest

from g_sorcery.compatibility import TemporaryDirectory
from g_sorcery.exceptions import SyncError
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
        orig_db.add_package(Package("app-test1", "test", "1"), ebuild_data)
        orig_db.add_package(Package("app-test1", "test", "2"))
        orig_db.add_package(Package("app-test1", "test1", "1"), ebuild_data)
        orig_db.add_package(Package("app-test2", "test2", "1"), ebuild_data)
        orig_db.write_and_manifest()
        os.system("cd " + orig_tempdir.name + " && tar cvzf dummy.tar.gz db")

        test_db = TestDB(self.tempdir.name)
        self.assertRaises(SyncError, test_db.sync, "127.0.0.1:8080")

        srv = Server(orig_tempdir.name)
        srv.start()
        test_db.sync("127.0.0.1:8080")
        srv.shutdown()
        srv.join()
        

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPackageDB('test_functionality'))
    return suite
