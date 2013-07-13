#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    fileutils.py
    ~~~~~~~~~~~~
    
    file utilities
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json, os, shutil

from .exceptions import FileJSONError
from .collections import Package, elist

class FileJSON(object):
    """
    Class for JSON files.
    """
    def __init__(self, directory, name, mandatories, loadconv=None):
        """
        Args:
            directory: File directory.
            name: File name.
            mandatories: List of requiered keys.
            loadconv: Type change values on loading.
        """
        self.directory = os.path.abspath(directory)
        self.name = name
        self.path = os.path.join(directory, name)
        self.mandatories = mandatories
        self.loadconv = loadconv

    def read(self):
        """
        Read JSON file.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        content = {}
        if not os.path.isfile(self.path):
            for key in self.mandatories:
                content[key] = ""
            with open(self.path, 'w') as f:
                json.dump(content, f, indent=2, sort_keys=True)
        else:
            with open(self.path, 'r') as f:
                content = json.load(f)
            for key in self.mandatories:
                if not key in content:
                    raise FileJSONError('lack of mandatory key: ' + key)
                
        if self.loadconv:
            for key, conv in self.loadconv.items():
                if key in content:
                    content[key] = conv(content[key])
        
        return content

    def write(self, content):
        """
        Write JSON file.
        """
        for key in self.mandatories:
            if not key in content:
                raise FileJSONError('lack of mandatory key: ' + key)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(self.path, 'w') as f:
            json.dump(content, f, indent=2, sort_keys=True)

            
def package_conv(lst):
    return Package(lst[0], lst[1], lst[2])

def dependencies_conv(dependencies):
    result = []
    for dependency in dependencies:
        result.append(package_conv(dependency))
    return result

def depend_conv(depend):
    return elist(depend, separator='\n\t')
            
class FilePkgDesc(FileJSON):
    def __init__(self, directory, name, mandatories):
        loadconv = {'dependencies' : dependencies_conv,
                    'depend' : depend_conv,
                    'rdepend' : depend_conv}
        super(FilePkgDesc, self).__init__(directory, name, mandatories, loadconv)


def hash_file(name, hasher, blocksize=65536):
    """
    Get a file hash.

    Args:
        name: file name.
        hasher: Hasher.
        blocksize: Blocksize.

    Returns:
        Hash value.
    """
    with open(name, 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
    return hasher.hexdigest()

def copy_all(src, dst):
    """
    Copy entire tree.

    Args:
       src: Source.
       dst: Destination.
    """
    for f_name in os.listdir(src):
        src_name = os.path.join(src, f_name)
        dst_name = os.path.join(dst, f_name)
        if os.path.isdir(src_name):
            shutil.copytree(src_name, dst_name)
        else:
            shutil.copy2(src_name, dst_name)

def wget(uri, directory):
    """
    Fetch a file.

    Args:
        uri: URI.
        directory: Directory where file should be saved.

    Returns:
        Nonzero in case of a failure.
    """
    return os.system('wget -P ' + directory + ' ' + uri)

def get_pkgpath(root = None):
    """
    Get package path.

    Returns:
        Package path.
    """
    if not root:
        root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))
