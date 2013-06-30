#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    metadata.py
    ~~~~~~~~~~~
    
    metadata generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

from .exceptions import XMLGeneratorError

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def prettify(tree):
    rough_str = ET.tostring(tree, 'unicode')
    reparsed = minidom.parseString(rough_str)
    return reparsed.toprettyxml()

class XMLGenerator:
    def __init__(self, external, schema):
        self.external = external
        self.schema = schema        

    def generate(self, values):
        root = ET.Element(self.external)
        for tag in self.schema:
            self.add_tag(root, tag, values)
        return root

    def add_tag(self, root, tag, values):
        name = tag['name']
        if not name in values:
            if tag['required']:
                raise XMLGeneratorError('Required tag not found: ' + name)
            return
        value = values[name]
        multiple, attr = tag['multiple']
        if multiple:
            for v in value:
                self.add_single_tag(root, name, tag, v, attr)
        else:
            self.add_single_tag(root, name, tag, value)
            
    def add_single_tag(self, root, name, tag, value, attr=None):
        child = ET.SubElement(root, name)
        if attr:
            child.set(attr, value[0])
            value = value[1]
        subtags = tag['subtags']
        if subtags:
            if 'text' in value:
                child.text = value[text]
            for child_tag in subtags:
                self.add_tag(child, child_tag, value)
        else:
            child.text = value
        

class MetadataGenerator:
    def __init__(self, db):
        self.db = db
        schema = [{'name' : 'herd',
                   'multiple' : (True, ""),
                   'required' : False,
                   'subtags' : []},
                   
                   {'name' : 'maintainer',
                   'multiple' : (True, ""),
                   'required' : False,
                   'subtags' : [{'name' : 'email',
                                 'multiple' : (False, ""),
                                 'required' : True,
                                 'subtags' : []},
                                 {'name' : 'name',
                                 'multiple' : (False, ""),
                                 'required' : False,
                                 'subtags' : []},
                                 {'name' : 'description',
                                 'multiple' : (False, ""),
                                 'required' : False,
                                 'subtags' : []},
                                 ]
                    },

                    {'name' : 'longdescription',
                     'multiple' : (False, ""),
                     'required' : False,
                     'subtags' : []},

                     {'name' : 'use',
                     'multiple' : (False, ""),
                     'required' : False,
                     'subtags' : [{'name' : 'flag',
                                 'multiple' : (True, "name"),
                                 'required' : True,
                                 'subtags' : []}]
                     },

                     {'name' : 'upstream',
                     'multiple' : (False, ""),
                     'required' : False,
                     'subtags' : [{'name' : 'maintainer',
                                 'multiple' : (True, ""),
                                 'required' : False,
                                 'subtags' : [{'name' : 'name',
                                               'multiple' : (False, ""),
                                               'required' : True,
                                               'subtags' : []},
                                               {'name' : 'email',
                                               'multiple' : (False, ""),
                                               'required' : False,
                                               'subtags' : []}]},
                                {'name' : 'changelog',
                                 'multiple' : (False, ""),
                                 'required' : False,
                                 'subtags' : []},
                                 {'name' : 'doc',
                                 'multiple' : (False, ""),
                                 'required' : False,
                                 'subtags' : []},
                                 {'name' : 'bugs-to',
                                 'multiple' : (False, ""),
                                 'required' : False,
                                 'subtags' : []},
                                 {'name' : 'remote-id',
                                 'multiple' : (False, ""),
                                 'required' : False,
                                 'subtags' : []},
                                ]
                        },
                   ]
        self.xmlg = XMLGenerator('pkgmetadata', schema)
        
    def generate(self, package):
        description = self.db.get_package_description(package)
        metadata = self.process(package, description)
        metadata = self.postprocess(package, description, metadata)
        return metadata

    def process(self, package, description):
        pass
        
    def postprocess(self, package, description, metadata):
        return metadata
