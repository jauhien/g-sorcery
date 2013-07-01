#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    backend.py
    ~~~~~~~~~~
    
    base class for backends
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import glob, os

from .package_db import Package

class Backend:
    def __init__(self, PackageDB, EbuildGenrator, MetadataGenerator, directory,
                 repo_uri="", db_uri="", sync_db=True, eclass_dir=""):
        self.sync_db = sync_db
        self.repo_uri = repo_uri
        self.db_uri = db_uri
        self.eclass_dir = eclass_dir

        self.directory = directory
        self.backend_data_dir = os.path.join(directory, '.backend_data')
        os.makedirs(self.backend_data_dir)
        self.db = PackageDB(os.path.join(self.backend_data_dir, 'db'),
                            repo_uri = self.repo_uri,
                            db_uri = self.db_uri)

        self.repo_uri = self.db.repo_uri
        self.db_uri = self.db.db_uri

        self.eg = EbuildGenrator(self.db)
        self.mg = MetadataGenerator(self.db)

    def sync(self):
        if self.sync_db and not self.db_uri:
            Exception("No uri for syncing provided.")
        if not self.sync_db and not self.repo_uri:
            Exception("No repo uri provided.")
        if self.sync_db:
            self.db.sync()
        else:
            self.db.generate()

    def list_ebuilds(self):
        return self.db.list_all_packages()

    def generate_ebuild(self, package):
        return self.eg.generate(package)

    def list_eclasses(self):
        result = []
        if self.eclass_dir:
            for f_name in glob.iglob(os.path.join(self.eclass_dir, '*.eclass')):
                result.append(os.path.basename(f_name)[:-7])
        return result

    def generate_eclass(self, eclass):
        if not self.eclass_dir:
            Exception('No eclass dir')
        f_name = os.path.join(self.eclass_dir, eclass + '.eclass')
        if not os.path.isfile(f_name):
            Exception('No eclass ' + eclass)
        with open(f_name, 'r') as f:
            eclass = f.read().split('\n')
            if eclass[-1] == '':
                eclass = eclass[:-1]
        return eclass

    def generate_metadata(self, category, name):
        version = self.db.get_max_version(category, name)
        metadata = self.mg.generate(Package(category, name, version))
        return metadata
