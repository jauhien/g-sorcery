#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_ebuild.py
    ~~~~~~~~~~~~~~~~~~
    
    ebuild generator test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os, tempfile, unittest

from g_sorcery import ebuild, package_db, exceptions

from tests.base import BaseTest

package = package_db.Package("app-test", "test", "0.1")
package2 = package_db.Package("app-test", "tst", "1")

class DummyDB(package_db.PackageDB):
    def __init__(self, directory, repo_uri="", db_uri=""):
        super(DummyDB, self).__init__(directory, repo_uri, db_uri)

    def generate_tree(self):
        self.add_category("app-test")
        self.add_package(package,
                         {"author" : "jauhien", "homepage" : "127.0.0.1"})
        self.add_package(package2,
                         {"author" : "unknown", "homepage" : "example.com"})


class DummyEbuildGenerator(ebuild.EbuildGenerator):
    def get_template(self, ebuild, description):
        tmpl = ["test", "author: $author", "homepage: $homepage", "var: $$var"]
        return tmpl


class TestEbuildGenerator(BaseTest):

    def test_process(self):
        eg = DummyEbuildGenerator(None)
        tst_dict = {"a" : "d", "b" : "e", "c" : "f"}
        ebuild = ["$a", "$b", "$c"]
        ebuild = eg.process(ebuild, tst_dict)
        self.assertEqual(ebuild, ["d", "e", "f"])

    def test_generate(self):
        db = DummyDB(self.tempdir.name)
        db.generate()
        eg = DummyEbuildGenerator(db)
        ebuild = eg.generate(package)
        self.assertEqual(ebuild, ['test', 'author: jauhien',
                                  'homepage: 127.0.0.1', 'var: $var'])


class DummyEbuildGeneratorFromFile(ebuild.EbuildGeneratorFromFile):
    def __init__(self, db, path):
        super(DummyEbuildGeneratorFromFile, self).__init__(db)
        self.path = path
    
    def get_template_file(self, package, description):
        return self.path


class TestEbuildGeneratorFromFile(BaseTest):

    def test_generate(self):
        db = DummyDB(os.path.join(self.tempdir.name, 'tstdb'))
        db.generate()
        tmpl = os.path.join(self.tempdir.name, 'tst.tmpl')
        with open(tmpl, 'w') as f:
            f.write("""test
author: $author
homepage: $homepage
var: $$var""")
        eg = DummyEbuildGeneratorFromFile(db, tmpl)
        ebuild = eg.generate(package)
        self.assertEqual(ebuild, ['test', 'author: jauhien',
                                  'homepage: 127.0.0.1', 'var: $var'])
        

class TestSubstituteList(BaseTest):

    def test_substitute_list(self):
        text = ['a', 'test', 'DEPEND="#n#depend#"', 'IUSE="# #iuse#"']
        desc = {'depend' : ['app-test/test1', 'app-test/test2'],
                'iuse' : ['test', 'check']}
        result = ['a', 'test', 'DEPEND="app-test/test1\napp-test/test2"', 'IUSE="test check"']
        self.assertEqual(ebuild.substitute_list(text, desc), result)
        self.assertRaises(exceptions.DescriptionError, ebuild.substitute_list, text, {})

        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestEbuildGenerator('test_process'))
    suite.addTest(TestEbuildGenerator('test_generate'))
    suite.addTest(TestEbuildGeneratorFromFile('test_generate'))
    suite.addTest(TestSubstituteList('test_substitute_list'))
    return suite
