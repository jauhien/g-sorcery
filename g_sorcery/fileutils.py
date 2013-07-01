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

class FileJSON:
    def __init__(self, directory, name, mandatories):
        """
        Initialize

        mandatories -- list of mandatory keys
        """
        self.directory = os.path.abspath(directory)
        self.name = name
        self.path = os.path.join(directory, name)
        self.mandatories = mandatories

    def read(self):
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
        return content

    def write(self, content):
        for key in self.mandatories:
            if not key in content:
                raise FileJSONError('lack of mandatory key: ' + key)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(self.path, 'w') as f:
            json.dump(content, f, indent=2, sort_keys=True)


def hash_file(name, hasher, blocksize=65536):
    with open(name, 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
    return hasher.hexdigest()

def copy_all(src, dst):
    for f_name in os.listdir(src):
        src_name = os.path.join(src, f_name)
        dst_name = os.path.join(dst, f_name)
        if os.path.isdir(src_name):
            shutil.copytree(src_name, dst_name)
        else:
            shutil.copy2(src_name, dst_name)
