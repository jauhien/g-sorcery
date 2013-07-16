#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ctan_db.py
    ~~~~~~~~~~
    
    CTAN package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

from g_sorcery.compatibility import TemporaryDirectory
from g_sorcery.g_collections import Package
from g_sorcery.package_db import PackageDB
from g_sorcery.fileutils import wget
from g_sorcery.exceptions import SyncError

class CtanDB(PackageDB):
    def __init__(self, directory, repo_uri="", db_uri=""):
        super(CtanDB, self).__init__(directory, repo_uri, db_uri)

    def generate_tree(self):
        tempdir = TemporaryDirectory()

        print(self.repo_uri)
        tlpdb_uri = self.repo_uri + '/tlpkg/texlive.tlpdb.xz'
        if wget(tlpdb_uri, tempdir.name):
            raise SyncError('sync failed: ' + self.repo_uri)

        del tempdir

        print("works")
