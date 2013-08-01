#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    elpa_db.py
    ~~~~~~~~~~
    
    ELPA package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import sexpdata

from g_sorcery.compatibility import py2k

if py2k:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

from g_sorcery.g_collections import Dependency, Package, serializable_elist
from g_sorcery.package_db import DBGenerator
from g_sorcery.exceptions import SyncError

class ElpaDBGenerator(DBGenerator):
    """
    Implementation of database generator for ELPA backend.
    """
    def get_download_uries(self, common_config, config):
        """
        Download database file from REPO_URI/archive-contents
        and parse it with sexpdata.

        Args:
            common_config: Backend config.
            config: Repository config.

        Returns:
            List with one URI entry.
        """
        ac_uri = urljoin(config["repo_uri"], 'archive-contents')
        return [{"uri" : ac_uri, "parser" : sexpdata.load}]

    def process_data(self, pkg_db, data, common_config, config):
        """
        Process downloaded and parsed data and generate tree.

        Args:
            pkg_db: Package database.
            data: Dictionary with data, keys are file names.
            common_config; Backend config.
            config: Repository config.
        """
        archive_contents = data['archive-contents']
        repo_uri = config["repo_uri"]

        if sexpdata.car(archive_contents) != 1:
            raise SyncError('sync failed: ' \
                        + repo_uri + ' bad archive contents format')

        pkg_db.add_category('app-emacs')

        PKG_INFO = 2
        PKG_NAME = 0

        INFO_VERSION = 0
        INFO_DEPENDENCIES = 1
        INFO_DESCRIPTION = 2
        INFO_SRC_TYPE = 3

        DEP_NAME = 0
        #DEP_VERSION = 1 #we do not use it at the moment
        
        for entry in sexpdata.cdr(archive_contents):
            desc = entry[PKG_INFO].value()
            realname = entry[PKG_NAME].value()

            if self.in_config([common_config, config], "exclude", realname):
                continue

            pkg = Package("app-emacs", realname,
                          '.'.join(map(str, desc[INFO_VERSION])))
            source_type = desc[INFO_SRC_TYPE].value()

            allowed_ords = set(range(ord('a'), ord('z'))) \
                    | set(range(ord('A'), ord('Z'))) | \
                    set(range(ord('0'), ord('9'))) | set(list(map(ord,
                    ['+', '_', '-', ' ', '.', '(', ')', '[', ']', '{', '}', ','])))            
            description = "".join([x for x in desc[INFO_DESCRIPTION] if ord(x) in allowed_ords])
            
            deps = desc[INFO_DEPENDENCIES]
            dependencies = serializable_elist(separator="\n\t")
            for dep in deps:
                dep = self.convert_dependency([common_config, config],
                                    dep[DEP_NAME].value(), external = False)
                if dep:
                    dependencies.append(dep)
                
            properties = {'source_type' : source_type,
                          'description' : description,
                          'dependencies' : dependencies,
                          'depend' : dependencies,
                          'rdepend' : dependencies,
                          'homepage' : repo_uri,
                          'repo_uri' : repo_uri,
                          'realname' : realname,
            #eclass entry
                          'eclasses' : ['g-elpa'],
            #metadata entries
                          'maintainer' : [{'email' : 'piatlicki@gmail.com',
                                           'name' : 'Jauhien Piatlicki'}],
                          'longdescription' : description
                          }
            pkg_db.add_package(pkg, properties)

    def convert_internal_dependency(self, configs, dependency):
        """
        At the moment we have only internal dependencies, each of them
        is just a package name.

        Args:
            configs: Backend and repo configs.
            dependency: Package name.

        Returns:
            Dependency instance with category="app-emacs", package="dependency".
        """
        return Dependency("app-emacs", dependency)
