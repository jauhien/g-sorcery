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

from g_sorcery import exceptions, metadata

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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestXMLGenerator('test_generate'))
    return suite
