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
    """
    Convert XML tree to a string.

    Args:
        tree: xml.etree.ElementTree.Element instance

    Returns:
        A string with XML source.
    """
    rough_str = ET.tostring(tree, "utf-8").decode("utf-8")
    reparsed = minidom.parseString(rough_str)
    return reparsed.toprettyxml(encoding="utf-8").decode("utf-8")

class XMLGenerator(object):
    """
    XML generator. Generates an XML tree according a given
    schema using a dict as a source of data.

    Schema format.
    ~~~~~~~~~~~~~~
    Schema is a list of entries. Each entry describes one XML tag.
    Entry is a dict. dict keys are:
        name: Name of a tag
        multiple: Defines if a given tag can be used more
                  then one time. It is a tuple. First element
                  of a tuple is boolean. If it is set a tag can be
                  repeated. Second element is a string. If it is not
                  empty, it defines a name for an attribute
                  that will distinguish different entries of a tag.
        required: Boolean that defines if a given tag is required.
        subtags: List of subtags.

    Data dictinonary format.
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Keys correspond to tags from a schema with the same name.
    If a tag is not multiple without subkeys value is just a
    string with text for the tag.
    If tag is multiple value is a list with entries
    corresponding to a single tag.
    If tag has subtags value is a dictionary with entries
    corresponding to subkeys and 'text' entry corresponding
    to text for the tag.
    If tag should have attributes value is a tuple or list with
    0 element containing an attribute and 1 element containing
    a value for the tag as described previously.
    """
    def __init__(self, external, schema):
        """
        Args:
            external: Name of an outermost tag.
            schema: XML schema.
        """
        self.external = external
        self.schema = schema        

    def generate(self, values):
        """
        Generate an XML tree filled with values from
        a given dictionary.

        Args:
            values: Data dictionary.

        Returns:
            XML tree being an istance of
            xml.etree.ElementTree.Element
        """
        root = ET.Element(self.external)
        for tag in self.schema:
            self.add_tag(root, tag, values)
        return root

    def add_tag(self, root, tag, values):
        """
        Add a tag.

        Args:
            root: A parent tag.
            tag: Tag from schema to be added.
            values: Data dictionary.
        """
        name = tag['name']
        if not name in values:
            if tag['required']:
                raise XMLGeneratorError('Required tag not found: ' + name)
            return
        value = values[name]
        multiple, attr = tag['multiple']
        if multiple:
            for val in value:
                self.add_single_tag(root, name, tag, val, attr)
        else:
            self.add_single_tag(root, name, tag, value)
            
    def add_single_tag(self, root, name, tag, value, attr=None):
        """
        Add a single tag.

        Args:
            root: A parent tag.
            name: Name of tag to be added.
            tag: Tag from schema to be added.
            value: Entry of a data dictionary
                   corresponding to the tag.
            attr: An attribute of the tag.
        """
        child = ET.SubElement(root, name)
        if attr:
            child.set(attr, value[0])
            value = value[1]
        subtags = tag['subtags']
        if subtags:
            if 'text' in value:
                child.text = value['text']
            for child_tag in subtags:
                self.add_tag(child, child_tag, value)
        else:
            child.text = value


# A default schema describing metadata.xml
# See http://devmanual.gentoo.org/ebuild-writing/misc-files/metadata/
default_schema = [{'name' : 'herd',
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
            

class MetadataGenerator(object):
    """
    Metada generator. Generates metadata for a given package.
    """
    def __init__(self, package_db, schema = None):
        """
        Args:
            package_db: Package database.
            schema: Schema of an XML tree.
        """
        if not schema:
            schema = default_schema
        self.package_db = package_db
        self.xmlg = XMLGenerator('pkgmetadata', schema)
        
    def generate(self, package):
        """
        Generate metadata for a package.

        Args:
            package: package_db.Package instance.

        Returns:
            Metadata source as a list of strings.
        """
        description = self.package_db.get_package_description(package)
        metadata = self.process(package, description)
        metadata = self.postprocess(package, description, metadata)
        metadata = prettify(metadata)
        metadata = metadata.split('\n')
        if metadata[-1] == '':
            metadata = metadata[:-1]
        dtp = '<!DOCTYPE pkgmetadata SYSTEM "http://www.gentoo.org/dtd/metadata.dtd">'
        metadata.insert(1, dtp)
        return metadata

    def process(self, package, description):
        """
        Generate metadata using values from a description.

        Args:
            package: package_db.Package instance.
            description: Package description (see package_db module).

        Returns:
            Metadata source as a list of strings.
            DOCTYPE missing.
        """
        metadata = self.xmlg.generate(description)
        return metadata
        
    def postprocess(self, package, description, metadata):
        """
        Postprocess generated metadata. Can be overrided.

        Args:
            package: package_db.Package instance.
            description: Package description (see package_db module).
            metadata: xml.etree.ElementTree.Element instance

        Returns:
            Metadata source as a list of strings.
            DOCTYPE missing.
        """
        return metadata
