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

class Backend(object):
    """
    Backend for a repository.
    """
    
    def __init__(self, package_db_class, ebuild_generator_class,
                 metadata_generator_class, directory,
                 repo_uri="", db_uri="", sync_db=True, eclass_dir=""):
        self.sync_db = sync_db
        self.repo_uri = repo_uri
        self.db_uri = db_uri
        self.eclass_dir = eclass_dir

        self.directory = directory
        self.backend_data_dir = os.path.join(directory, '.backend_data')
        os.makedirs(self.backend_data_dir)
        db_dir = os.path.join(self.backend_data_dir, 'db')
        self.package_db = package_db_class(db_dir,
                            repo_uri = self.repo_uri,
                            db_uri = self.db_uri)

        self.repo_uri = self.package_db.repo_uri
        self.db_uri = self.package_db.db_uri

        self.ebuild_generator = ebuild_generator_class(self.package_db)
        self.metadata_generator = metadata_generator_class(self.package_db)

    def sync(self):
        """
        Synchronize package database.
        If self.sync_db is set synchronizes with generated database,
        if it is unset synchronizes with a repository.
        """        
        if self.sync_db and not self.db_uri:
            Exception("No uri for syncing provided.")
        if not self.sync_db and not self.repo_uri:
            Exception("No repo uri provided.")
        if self.sync_db:
            self.package_db.sync()
        else:
            self.package_db.generate()

    def list_ebuilds(self):
        """
        List all the packages in a database.

        Returns:
            List of all packages in a databes
            with package_db.Package entries.
        """
        return self.package_db.list_all_packages()

    def generate_ebuild(self, package):
        """
        Generate ebuild for a specified package.

        Args:
            package: package_db.Package instance.

        Returns:
            Ebuild source as a list of strings.
        """
        return self.ebuild_generator.generate(package)

    def list_eclasses(self):
        """
        List all eclasses.

        Returns:
            List of all eclasses with string entries.
        """
        result = []
        if self.eclass_dir:
            for f_name in glob.iglob(os.path.join(self.eclass_dir, '*.eclass')):
                result.append(os.path.basename(f_name)[:-7])
        return result

    def generate_eclass(self, eclass):
        """
        Generate a given eclass.

        Args:
            eclass: String containing eclass name.

        Returns:
            Eclass source as a list of strings.
        """
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
        """
        Generate metadata for a given package.

        Args:
            category: category name
            name: package name

        Returns:
            Generated metadata as a list of strings.
            It uses the most recent version of a package
            to look for data for generation.
        """
        version = self.package_db.get_max_version(category, name)
        metadata = self.metadata_generator.generate(
            Package(category, name, version))
        return metadata

    def __call__(self, args):
        pass
