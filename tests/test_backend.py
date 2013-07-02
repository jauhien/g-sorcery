#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_backend.py
    ~~~~~~~~~~~~~~~
    
    backend test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os, tempfile, unittest

from g_sorcery import backend, ebuild, metadata, package_db

from tests import test_ebuild, test_metadata

from tests.base import BaseTest

class DummyBackend(backend.Backend):
    def __init__(self, PackageDB, EbuildGenrator, MetadataGenerator, directory,
                 sync_db=True, eclass_dir=""):
        super(DummyBackend, self).__init__(PackageDB, EbuildGenrator, MetadataGenerator, directory,
                         sync_db=sync_db, eclass_dir=eclass_dir)


class TestBackend(BaseTest):
    
    def test_list_eclasses(self):
        backend = DummyBackend(package_db.PackageDB, ebuild.EbuildGenerator,
                               metadata.MetadataGenerator,
                               self.tempdir.name, eclass_dir = self.tempdir.name)
        self.assertEqual(backend.list_eclasses(), [])
        lst = ['test', 'supertest', 'anothertest']
        for f_name in lst:
            with open(os.path.join(self.tempdir.name, f_name + '.eclass'), 'w') as f:
                f.write("test")
        self.assertEqual(set(backend.list_eclasses()), set(lst))

    def test_generate_eclass(self):
        backend = DummyBackend(package_db.PackageDB, ebuild.EbuildGenerator,
                               metadata.MetadataGenerator,
                               self.tempdir.name, eclass_dir = self.tempdir.name)
        eclass = ["testing eclass", "nothing interesting here"]
        eclass_name = "test"
        with open(os.path.join(self.tempdir.name, eclass_name + '.eclass'), 'w') as f:
            for line in eclass:
                f.write(line + '\n')
        g_eclass = backend.generate_eclass(eclass_name)
        self.assertEqual(eclass, g_eclass)

    def test_list_ebuilds(self):
        backend = DummyBackend(test_ebuild.DummyDB, test_ebuild.DummyEbuildGenerator,
                               metadata.MetadataGenerator,
                               self.tempdir.name, eclass_dir = self.tempdir.name, sync_db = False)
        backend.sync()
        ebuilds = backend.list_ebuilds()
        self.assertEqual(set(ebuilds), set([test_ebuild.package, test_ebuild.package2]))

    def test_generate_ebuild(self):
        backend = DummyBackend(test_ebuild.DummyDB, test_ebuild.DummyEbuildGenerator,
                               metadata.MetadataGenerator,
                               self.tempdir.name, eclass_dir = self.tempdir.name, sync_db = False)
        backend.sync()
        ebuild = backend.generate_ebuild(test_ebuild.package)
        self.assertEqual(ebuild, ['test', 'author: jauhien',
                                  'homepage: 127.0.0.1', 'var: $var'])

    def test_generate_metadata(self):
        backend = DummyBackend(test_metadata.DummyDB, ebuild.EbuildGenerator,
                               metadata.MetadataGenerator,
                               self.tempdir.name, eclass_dir = self.tempdir.name, sync_db = False)
        backend.sync()
        self.assertEqual(backend.generate_metadata("app-test", "test"),
                         test_metadata.resulting_metadata)
                         
        

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBackend('test_list_eclasses'))
    suite.addTest(TestBackend('test_generate_eclass'))
    suite.addTest(TestBackend('test_list_ebuilds'))
    suite.addTest(TestBackend('test_generate_ebuild'))
    suite.addTest(TestBackend('test_generate_metadata'))
    return suite
