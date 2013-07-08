#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_elpa_metadata.py
    ~~~~~~~~~~~~~~~~~~~~~
    
    ELPA metadata generator test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os, unittest

from g_sorcery import package_db, metadata

from g_elpa import elpa_db

from tests.base import BaseTest

from tests.test_elpa_db import fill_database, packages

class TestElpaEbuildGenerator(BaseTest):

    def test_generate(self):
        edb = elpa_db.ElpaDB(os.path.join(self.tempdir.name, 'db'),
                             repo_uri = 'http://127.0.0.1:8080')
        fill_database(edb, packages, self.tempdir.name)
        metadata_generator = metadata.MetadataGenerator(edb)
        mdxml = metadata_generator.generate(package_db.Package('app-emacs', 'ack', '1.2'))
        self.assertEqual(mdxml,
                ['<?xml version="1.0" encoding="utf-8"?>',
                '<!DOCTYPE pkgmetadata SYSTEM "http://www.gentoo.org/dtd/metadata.dtd">',
                '<pkgmetadata>',
                '\t<maintainer>',
                '\t\t<email>piatlicki@gmail.com</email>',
                '\t\t<name>Jauhien Piatlicki</name>',
                '\t</maintainer>',
                '\t<longdescription>Interface to ack-like source code search tools</longdescription>',
                '</pkgmetadata>'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestElpaEbuildGenerator('test_generate'))
    return suite
