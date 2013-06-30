#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_metadata.py
    ~~~~~~~~~~~~~~~~
    
    metadata generator test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import xml.etree.ElementTree as ET

import tempfile, unittest

from g_sorcery import exceptions, metadata, package_db

class TestXMLGenerator(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate(self):
        schema = [{'name' : 'desc',
                   'subtags' : [],
                   'multiple' : (False, ""),
                   'required' : True},
                   {'name' : 'contact',
                   'multiple' : (False, ""),
                   'required' : False,
                   'subtags' : [
                       {'name' : 'email',
                        'subtags' : [],
                        'multiple' : (False, ""),
                        'required' : True},
                        
                        {'name' : 'phone',
                        'subtags' : [],
                        'multiple' : (False, ""),
                        'required' : False},
                    ]},
                    {'name' : 'multiple',
                     'subtags' : [],
                     'multiple' : (True, ""),
                     'required' : False},
                     {'name' : 'flag',
                     'subtags' : [],
                     'multiple' : (True, "name"),
                     'required' : False},
                   ]
        xg = metadata.XMLGenerator('test_ext', schema)
        self.assertRaises(exceptions.XMLGeneratorError, xg.generate, {})
        tree = xg.generate({'desc' : 'test xml'})
        self.assertEqual(ET.tostring(tree, encoding='unicode'),
                         '<test_ext><desc>test xml</desc></test_ext>')
        tree = xg.generate({'desc' : 'test xml', 
                            'contact' : {'email' : 'test@example.com',
                                         'phone' : '00-0'}})
        self.assertEqual(ET.tostring(tree, encoding='unicode'),
                    '<test_ext><desc>test xml</desc><contact><email>test@example.com\
</email><phone>00-0</phone></contact></test_ext>')
        tree = xg.generate({'desc' : 'test xml', 
                            'multiple' : ['test1', 'test2', 'test3']})
        self.assertEqual(ET.tostring(tree, encoding='unicode'),
                         '<test_ext><desc>test xml</desc><multiple>test1</multiple>\
<multiple>test2</multiple><multiple>test3</multiple></test_ext>')
        tree = xg.generate({'desc' : 'test xml', 
                            'flag' : [('flag1', 'test1'), ('flag2', 'test2')]})
        self.assertEqual(ET.tostring(tree, encoding='unicode'),
                         '<test_ext><desc>test xml</desc><flag name="flag1">test1</flag>\
<flag name="flag2">test2</flag></test_ext>')


class DummyMetadataGenerator(metadata.MetadataGenerator):
    def __init__(self, db):
        super().__init__(db)

package = package_db.Package("app-test", "test", "0.1")

description = {'herd' : ['test'],
               'maintainer' : [{'email' : 'test@example.com', 'name' : 'testor'}],
               'longdescription' : 'test metadata',
               'use' : {'flag' : [('flag1', 'test flag1'), ('flag2', 'test flag2')]},
               'upstream' : {'maintainer' : [{'name' : 'TEST'}], 'remote-id' : '001'}}

class DummyDB(package_db.PackageDB):
    def __init__(self, directory, repo_uri="", db_uri=""):
        super().__init__(directory, repo_uri, db_uri)

    def generate_tree(self):
        self.add_category("app-test")
        self.add_package(package, description)
        

class TestMetadataGenerator(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        del self.tempdir

    def test_process(self):
        mg = DummyMetadataGenerator(None)
        self.assertEqual(ET.tostring(mg.process(None, description), encoding='unicode'),
                         '<pkgmetadata><herd>test</herd><maintainer><email>test@example.com</email>\
<name>testor</name></maintainer><longdescription>test metadata</longdescription><use>\
<flag name="flag1">test flag1</flag><flag name="flag2">test flag2</flag></use>\
<upstream><maintainer><name>TEST</name></maintainer><remote-id>001</remote-id></upstream></pkgmetadata>')

    def test_generate(self):
        db = DummyDB(self.tempdir.name)
        db.generate()
        mg = DummyMetadataGenerator(db)
        metadata = mg.generate(package)
        self.assertEqual(metadata,
                          ['<?xml version="1.0" encoding="utf-8"?>',
                           '<!DOCTYPE pkgmetadata SYSTEM "http://www.gentoo.org/dtd/metadata.dtd">',
                           '<pkgmetadata>', '\t<herd>test</herd>',
                           '\t<maintainer>', '\t\t<email>test@example.com</email>',
                           '\t\t<name>testor</name>', '\t</maintainer>',
                           '\t<longdescription>test metadata</longdescription>',
                           '\t<use>', '\t\t<flag name="flag1">test flag1</flag>',
                           '\t\t<flag name="flag2">test flag2</flag>', '\t</use>',
                           '\t<upstream>', '\t\t<maintainer>', '\t\t\t<name>TEST</name>',
                           '\t\t</maintainer>', '\t\t<remote-id>001</remote-id>',
                           '\t</upstream>', '</pkgmetadata>'])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestXMLGenerator('test_generate'))
    suite.addTest(TestMetadataGenerator('test_process'))
    suite.addTest(TestMetadataGenerator('test_generate'))
    return suite
