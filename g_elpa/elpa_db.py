#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    elpa_db.py
    ~~~~~~~~~~
    
    ELPA package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os, tempfile, urllib.parse

from g_sorcery.package_db import PackageDB
from g_sorcery.fileutils import wget

class ElpaDB(PackageDB):
    def __init__(self, directory, repo_uri="", db_uri=""):
        super().__init__(directory, repo_uri, db_uri)

    def generate_tree(self):
        tempdir = tempfile.TemporaryDirectory()
        
        ac_uri = urllib.parse.urljoin(self.repo_uri, 'archive-contents')
        wget(ac_uri, tempdir.name)

        os.system('ls -l ' + tempdir.name)
        os.system('less ' + tempdir.name + '/archive-contents')
        
        del tempdir

    def get_parser(self):
        pass
