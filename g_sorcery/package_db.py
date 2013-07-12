#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    package_db.py
    ~~~~~~~~~~~~~
    
    package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

from .compatibility import TemporaryDirectory

from .exceptions import DBStructureError, IntegrityError, \
     InvalidKeyError, SyncError

from .fileutils import FileJSON, hash_file, copy_all, wget

import portage

import collections, glob, hashlib, os, shutil, tarfile

Package = collections.namedtuple("Package", "category name version")

class PackageDB(object):
    """
    Package database.
    Database is a directory and related data structure.

    Directory layout.
    ~~~~~~~~~~~~~~~~~
    db dir
        manifest.json: database manifest
        uri.json: URIes
        info.json: information about database
        categories.json: information about categories
        category1
            packages.json: list of packages
            package1
                versions.json: list of versions
                version1.json: description of a package
                version2.json: description of a package
                ...
            package2
            ...
        category2
        ...
    
    """
    def __init__(self, directory, repo_uri="", db_uri=""):
        """
        Args:
            directory: database directory.
            repo_uri: Repository URI.
            db_uri: URI for synchronization with remote database.
        """
        self.URI_NAME = 'uri.json'
        self.INFO_NAME = 'info.json'
        self.CATEGORIES_NAME = 'categories.json'
        self.PACKAGES_NAME = 'packages.json'
        self.VERSIONS_NAME = 'versions.json'
        self.directory = os.path.abspath(directory)
        self.reset_uri(repo_uri, db_uri)
        self.reset_db()

    def reset_uri(self, repo_uri="", db_uri=""):
        """
        Reset URI information.

        Args:
            repo_uri: Repository URI.
            db_uri: URI for synchronization with remote database.
        """
        uri_f = FileJSON(self.directory, self.URI_NAME, ['repo_uri', 'db_uri'])
        uri = uri_f.read()
        if not repo_uri:
            self.repo_uri = uri['repo_uri']
        else:
            self.repo_uri = repo_uri
        if not db_uri:
            self.db_uri = uri['db_uri']
        else:
            self.db_uri = db_uri
        uri['repo_uri'] = self.repo_uri
        uri['db_uri'] = self.db_uri
        uri_f.write(uri)

    def reset_db(self):
        """
        Reset database.
        """
        self.database = {}
        self.info = {}
        self.categories = {}

    def generate(self, repo_uri=""):
        """
        Generate new package database

        Args:
            repo_uri: Repository URI
        """
        if repo_uri:
            self.repo_uri = repo_uri
        self.clean()
        self.generate_tree()
        self.write()
        self.manifest()

    def generate_tree(self):
        """
        Generate tree

        Should be implemented in a subclass
        """
        pass

    def sync(self, db_uri=""):
        """
        Synchronize local database with remote database.

        Args:
            db_uri: URI for synchronization with remote database.
        """
        if db_uri:
            self.db_uri = db_uri
        self.clean()
        real_db_uri = self.get_real_db_uri()
        download_dir = TemporaryDirectory()
        if wget(real_db_uri, download_dir.name):
            raise SyncError('sync failed: ' + real_db_uri)
        
        temp_dir = TemporaryDirectory()
        for f_name in glob.iglob(os.path.join(download_dir.name, '*.tar.gz')):
            with tarfile.open(f_name) as f:
                f.extractall(temp_dir.name)

        tempdb_dir = TemporaryDirectory()
        tempdb = PackageDB(tempdb_dir.name)

        for d_name in os.listdir(temp_dir.name):
            current_dir = os.path.join(temp_dir.name, d_name)
            if not os.path.isdir(current_dir):
                continue
            copy_all(current_dir, tempdb_dir.name)

        if not tempdb.check_manifest():
            raise IntegrityError('Manifest check failed.')

        self.clean()
        copy_all(tempdb_dir.name, self.directory)
        
        if not self.check_manifest():
            raise IntegrityError('Manifest check failed, db inconsistent.')
                
        del download_dir
        del temp_dir
        del tempdb_dir
        
        self.read()

    def get_real_db_uri(self):
        """
        Convert self.db_uri to URI where remote database can be
        fetched from.

        Returns:
            URI of remote database file.
        """
        return self.db_uri
            
    def manifest(self):
        """
        Generate database manifest.
        """
        categories = FileJSON(self.directory, self.CATEGORIES_NAME, [])
        categories = categories.read()
        manifest = {}
        names = [self.INFO_NAME, self.CATEGORIES_NAME, self.URI_NAME]
        for name in names:
            manifest[name] = hash_file(os.path.join(self.directory, name),
                                      hashlib.md5())
        for category in categories:
            category_path = os.path.join(self.directory, category)
            if not os.path.isdir(category_path):
                raise DBStructureError('Empty category: ' + category)
            for root, dirs, files in os.walk(category_path):
                for f in files:
                    manifest[os.path.join(root[len(self.directory)+1:], f)] = \
                    hash_file(os.path.join(root, f), hashlib.md5())
        m_f = FileJSON(self.directory, 'manifest.json', [])
        m_f.write(manifest)

    def check_manifest(self):
        """
        Check database manifest.

        Returns:
            Tuple with first element containing result of manifest check
            as boolean and second element containing list of files with errors.
        """
        m_f = FileJSON(self.directory, 'manifest.json', [])
        manifest = m_f.read()
        
        result = True
        errors = []
        
        names = [self.INFO_NAME, self.CATEGORIES_NAME, self.URI_NAME]
        for name in names:
            if not name in manifest:
                raise DBStructureError('Bad manifest: no ' + name + ' entry')

        for name, value in manifest.items():
            if hash_file(os.path.join(self.directory, name), hashlib.md5()) != \
                value:
                result = False
                errors.append(name)

        return (result, errors)

    def clean(self):
        """
        Clean database.
        """
        shutil.rmtree(self.directory)
        self.reset_uri(self.repo_uri, self.db_uri)
        self.reset_db()

    def write(self):
        """
        Write database.
        """
        info_f = FileJSON(self.directory, self.INFO_NAME, [])
        categories_f = FileJSON(self.directory, self.CATEGORIES_NAME, [])
        info_f.write(self.info)
        categories_f.write(self.categories)

        for pkgname, versions in self.database.items():
            category, name = pkgname.split('/')
            if not category or (not category in self.categories):
                raise DBStructureError('Non existent: ' + category)
            for version, content in versions.items():
                f = FileJSON(os.path.join(self.directory, category, name),
                    version + '.json', [])
                f.write(content)
                self.additional_write_version(category, name, version)
            f = FileJSON(os.path.join(self.directory, category, name),
                self.VERSIONS_NAME, [])
            f.write(list(versions))
            self.additional_write_package(category, name)
            f = FileJSON(os.path.join(self.directory, category),
                self.PACKAGES_NAME, [])
            pkgs = f.read()
            if not pkgs:
                pkgs = []
            pkgs.append(name)
            f.write(pkgs)

        for category in self.categories:
            self.additional_write_category(category)
            
        self.additional_write()

    def additional_write_version(self, category, package, version):
        """
        Hook to be overrided.
        """
        pass

    def additional_write_package(self, category, package):
        """
        Hook to be overrided.
        """
        pass

    def additional_write_category(self, category):
        """
        Hook to be overrided.
        """
        pass

    def additional_write(self):
        """
        Hook to be overrided.
        """
        pass

    def read(self):
        """
        Read database.
        """
        sane, errors = self.check_manifest()
        if not sane:
            raise IntegrityError('Manifest error: ' + str(errors))
        info_f = FileJSON(self.directory, self.INFO_NAME, [])
        categories_f = FileJSON(self.directory, self.CATEGORIES_NAME, [])
        self.info = info_f.read()
        self.categories = categories_f.read()
        for category in self.categories:
            category_path = os.path.join(self.directory, category)
            if not os.path.isdir(category_path):
                raise DBStructureError('Empty category: ' + category)
            
            f = FileJSON(category_path, self.PACKAGES_NAME, [])
            packages = f.read()
            if not packages:
                raise DBStructureError('Empty category: ' + category)
            
            for name in packages:
                package_path = os.path.join(category_path, name)
                if not os.path.isdir(category_path):
                    error_msg = 'Empty package: ' + category + '/' + name
                    raise DBStructureError(error_msg)
                
                f = FileJSON(package_path, self.VERSIONS_NAME, [])
                versions = f.read()
                if not versions:
                    error_msg = 'Empty package: ' + category + '/' + name
                    raise DBStructureError(error_msg)

                pkgname = category + '/' + name
                self.database[pkgname] = {}
                for version in versions:
                    f = FileJSON(package_path, version + '.json', [])
                    description = f.read()
                    self.database[pkgname][version] = description
                    self.additional_read_version(category, name, version)
                self.additional_read_package(category, name)
            self.additional_read_category(category)
        self.additional_read()

    def additional_read_version(self, category, package, version):
        """
        Hook to be overrided.
        """
        pass

    def additional_read_package(self, category, package):
        """
        Hook to be overrided.
        """
        pass

    def additional_read_category(self, category):
        """
        Hook to be overrided.
        """
        pass

    def additional_read(self):
        """
        Hook to be overrided.
        """
        pass
        
    def add_category(self, category, description=None):
        """
        Add a category.

        Args:
            category: Category name.
            description: Category description.
        """
        if not description:
            description = {}
        self.categories[category] = description

    def add_package(self, package, description=None):
        """
        Add a package.

        Args:
            package: package_db.Package instance.
            description: Dictionary with package description.
        """
        if not description:
            description = {}
        category = package.category
        name = package.name
        version = package.version
        pkgname = category + '/' + name
        if category and not category in self.categories:
            raise InvalidKeyError('Non-existent category: ' + category)
        if pkgname and not pkgname in self.database:
            self.database[pkgname] = {}
        self.database[pkgname][version] = description

    def list_categories(self):
        """
        List all categories.

        Returns:
            List with category names.
        """
        return list(self.categories)

    def in_category(self, category, name):
        """
        Tests whether a package is in a given category.

        Args:
            category: Category name.
            name: Package name.

        Returns:
            Boolean value.
        """
        if not category or (not category in self.categories):
            raise InvalidKeyError('No such category: ' + category)
        return (category + '/' + name) in self.database

    def list_package_names(self, category):
        """
        List package names in a category.

        Args:
            category: Category name.

        Returns:
            List of package names.
        """
        if not category or (not category in self.categories):
            raise InvalidKeyError('No such category: ' + category)
        res = [x.split('/')[1] for x in self.database if x.split('/')[0] == category]
        return res

    def list_package_versions(self, category, name):
        """
        List package versions.

        Args:
            category: Category name.
            name: package name.

        Returns:
            List of package versions.
        """
        if not category or (not category in self.categories):
            raise InvalidKeyError('No such category: ' + category)
        pkgname = category + '/' + name
        if not pkgname in self.database:
            raise InvalidKeyError('No such package: ' + pkgname)
        return list(self.database[pkgname])

    def list_all_packages(self):
        """
        List all packages in a database.

        Returns:
            List of package_db.Package instances.
        """
        result = []
        for pkgname, versions in self.database.items():
            for version in versions:
                category, name = pkgname.split('/')
                result.append(Package(category, name, version))
        return result

    def get_package_description(self, package):
        """
        Get package description.

        Args:
            package: package_db.Package instance.

        Returns:
            Dictionary with package description.
        """
        #a possible exception should be catched in the caller
        return self.database[package.category + '/' + package.name][package.version]

    def get_max_version(self, category, name):
        """
        Get the recent available version of a package.

        Args:
            category: Category name.
            name: package name.

        Returns:
            The recent version of a package.
        """
        pkgname = category + '/' + name
        if not pkgname in self.database:
            raise InvalidKeyError('No such package: ' + pkgname)
        versions = list(self.database[pkgname])
        max_ver = versions[0]
        for version in versions[1:]:
            if portage.pkgcmp(portage.pkgsplit(pkgname + '-' + version),
                              portage.pkgsplit(pkgname + '-' + max_ver)) > 0:
                max_ver = version
        return max_ver
