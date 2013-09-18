#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_DBGenerator.py
    ~~~~~~~~~~~~~~~~~~~
    
    DBGenerator test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest

from g_sorcery.compatibility import TemporaryDirectory
from g_sorcery.exceptions import InvalidKeyError
from g_sorcery.g_collections import Package
from g_sorcery.package_db import DBGenerator

from tests.base import BaseTest
from tests.server import Server


class TestingDBGenerator(DBGenerator):
    def get_download_uries(self, common_config, config):
        return [config["repo_uri"] + "/repo.data"]

    def parse_data(self, data_f):
        content = data_f.read()
        content = content.split("packages\n")
        ebuild_data_lines = content[0].split("\n")
        packages_lines = content[1].split("\n")
        ebuild_data = {}
        packages = []
        for line in ebuild_data_lines:
            if line:
                data = line.split(" ")
                ebuild_data[data[0]] = data[1]
        for line in packages_lines:
            if line:
                data = line.split(" ")
                packages.append(Package(data[0], data[1], data[2]))
        return {"ebuild_data": ebuild_data, "packages": packages}


    def process_data(self, pkg_db, data, common_config, config):
        data = data["repo.data"]
        ebuild_data = data["ebuild_data"]
        for package in data["packages"]:
            pkg_db.add_category(package.category)
            pkg_db.add_package(package, ebuild_data)


class TestDBGenerator(BaseTest):

    def test_functionality(self):
        db_generator = TestingDBGenerator()
        common_config = {}
        config = {"repo_uri": "127.0.0.1:8080"}

        packages = [Package("app-test1", "test", "1"), Package("app-test1", "test", "2"),
                    Package("app-test1", "test1", "1"), Package("app-test2", "test2", "1")]
        ebuild_data = {"test1": "test1", "test2": "test2"}

        orig_tempdir = TemporaryDirectory()
        with open(os.path.join(orig_tempdir.name, "repo.data"), "w") as f:
            for key, value in ebuild_data.items():
                f.write(key + " " + value + "\n")
            f.write("packages\n")
            for package in packages:
                f.write(package.category + " " +  package.name + " " + package.version + "\n")

        srv = Server(orig_tempdir.name)
        srv.start()

        pkg_db = db_generator(self.tempdir.name, "test_repo",
                              common_config = common_config, config = config)

        srv.shutdown()
        srv.join()

        self.assertEqual(set(pkg_db.list_categories()), set(["app-test1", "app-test2"]))
        self.assertTrue(pkg_db.in_category("app-test1", "test"))
        self.assertFalse(pkg_db.in_category("app-test2", "test"))
        self.assertRaises(InvalidKeyError, pkg_db.in_category, "app-test3", "test")
        self.assertEqual(set(pkg_db.list_package_names("app-test1")), set(['test', 'test1']))
        self.assertEqual(set(pkg_db.list_catpkg_names()),set(['app-test1/test', 'app-test1/test1', 'app-test2/test2']))
        self.assertRaises(InvalidKeyError, pkg_db.list_package_versions, "invalid", "test")
        self.assertRaises(InvalidKeyError, pkg_db.list_package_versions, "app-test1", "invalid")
        self.assertEqual(set(pkg_db.list_package_versions("app-test1", "test")), set(['1', '2']))
        self.assertEqual(set(pkg_db.list_all_packages()), set(packages))
        self.assertEqual(pkg_db.get_package_description(packages[0]), ebuild_data)
        self.assertRaises(KeyError, pkg_db.get_package_description, Package("invalid", "invalid", "1"))
        self.assertEqual(pkg_db.get_max_version("app-test1", "test"), "2")
        self.assertEqual(pkg_db.get_max_version("app-test1", "test1"), "1")
        self.assertRaises(InvalidKeyError, pkg_db.get_max_version, "invalid", "invalid")
        pkg_set = set(packages)
        for package, data in pkg_db:
            self.assertTrue(package in pkg_set)
            self.assertEqual(data, ebuild_data)
            pkg_set.remove(package)
        self.assertTrue(not pkg_set)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDBGenerator('test_functionality'))
    return suite
