#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_metadata.py
    ~~~~~~~~~~~~~~~~
    
    metadata test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest

from g_sorcery.compatibility import TemporaryDirectory
from g_sorcery.g_collections import Package
from g_sorcery.metadata import MetadataGenerator
from g_sorcery.package_db import PackageDB

from tests.base import BaseTest


class TestMetadataGenerator(BaseTest):

    def test_metadata(self):
        pkg_db = PackageDB(self.tempdir.name)
        pkg_db.add_category("app-test")
        ebuild_data = {"herd": ["testers", "crackers"],
                       'maintainer': [{'email': 'test@example.com',
                                         'name': 'tux'}],
                       "longdescription": "very long description here",
                       "use": {"flag": {"use1": "testing use1", "use2": "testing use2"}}}
        package = Package("app-test", "metadata_tester", "0.1")
        pkg_db.add_package(package, ebuild_data)
        metadata_g = MetadataGenerator(pkg_db)
        metadata = metadata_g.generate(package)
        self.assertEqual(metadata,
                         ['<?xml version="1.0" encoding="utf-8"?>',
                          '<!DOCTYPE pkgmetadata SYSTEM "http://www.gentoo.org/dtd/metadata.dtd">',
                          '<pkgmetadata>',
                          '\t<herd>testers</herd>', '\t<herd>crackers</herd>',
                          '\t<maintainer>', '\t\t<email>test@example.com</email>', '\t\t<name>tux</name>', '\t</maintainer>',
                          '\t<longdescription>very long description here</longdescription>',
                          '\t<use>', '\t\t<flag name="u">s</flag>', '\t\t<flag name="u">s</flag>', '\t</use>',
                          '</pkgmetadata>'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestMetadataGenerator('test_metadata'))
    return suite
