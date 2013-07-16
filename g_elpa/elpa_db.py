#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    elpa_db.py
    ~~~~~~~~~~
    
    ELPA package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

import sexpdata

from g_sorcery.compatibility import py2k, TemporaryDirectory

if py2k:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

from g_sorcery.g_collections import Package
from g_sorcery.package_db import PackageDB
from g_sorcery.fileutils import wget
from g_sorcery.exceptions import SyncError

class ElpaDB(PackageDB):
    def __init__(self, directory, repo_uri="", db_uri=""):
        super(ElpaDB, self).__init__(directory, repo_uri, db_uri)

    def generate_tree(self):
        tempdir = TemporaryDirectory()
        
        ac_uri = urljoin(self.repo_uri, 'archive-contents')
        if wget(ac_uri, tempdir.name):
            raise SyncError('sync failed: ' + self.repo_uri)

        try:
            with open(os.path.join(tempdir.name, 'archive-contents')) as f:
                archive_contents = sexpdata.load(f)
        except Exception as e:
            raise SyncError('sync failed: ' + self.repo_uri + ': ' + str(e))

        del tempdir
        
        if sexpdata.car(archive_contents) != 1:
            raise SyncError('sync failed: ' + self.repo_uri + ' bad archive contents format')

        self.add_category('app-emacs')

        PKG_INFO = 2
        PKG_NAME = 0

        INFO_VERSION = 0
        INFO_DEPENDENCIES = 1
        INFO_DESCRIPTION = 2
        INFO_SRC_TYPE = 3

        DEP_NAME = 0
        DEP_VERSION = 1
        
        for entry in sexpdata.cdr(archive_contents):
            desc = entry[PKG_INFO].value()
            pkg = self._s_get_package(entry[PKG_NAME], desc[INFO_VERSION])
            source_type = desc[INFO_SRC_TYPE].value()

            allowed_ords = set(range(ord('a'), ord('z'))) | set(range(ord('A'), ord('Z'))) | \
              set(range(ord('0'), ord('9'))) | set(list(map(ord,
                    ['+', '_', '-', ' ', '.', '(', ')', '[', ']', '{', '}', ','])))            
            description = "".join([x for x in desc[INFO_DESCRIPTION] if ord(x) in allowed_ords])
            
            deps = desc[INFO_DEPENDENCIES]
            dependencies = []
            depend = []
            realname = entry[PKG_NAME].value()
            for dep in deps:
                dep_pkg = self._s_get_package(dep[DEP_NAME], dep[DEP_VERSION])
                dependencies.append(dep_pkg)
                depend.append(dep_pkg.category + '/' + dep_pkg.name)
                
            properties = {'source_type' : source_type,
                          'description' : description,
                          'dependencies' : dependencies,
                          'depend' : depend,
                          'rdepend' : depend,
                          'homepage' : self.repo_uri,
                          'repo_uri' : self.repo_uri,
                          'realname' : realname,
            #eclass entry
                          'eclasses' : ['g-elpa'],
            #metadata entries
                          'maintainer' : [{'email' : 'piatlicki@gmail.com',
                                           'name' : 'Jauhien Piatlicki'}],
                          'longdescription' : description
                          }
            self.add_package(pkg, properties)
            
    
    def _s_get_package(self, name, version):
        category = 'app-emacs'
        version = '.'.join(map(str, version))
        return Package(category, name.value(), version)
