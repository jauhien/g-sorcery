#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    package_db.py
    ~~~~~~~~~~~~~
    
    package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import glob
import hashlib
import os
import shutil
import sys

import portage

from .compatibility import basestring, py2k, TemporaryDirectory

from .exceptions import DBStructureError, IntegrityError, \
     InvalidKeyError, SyncError
from .fileutils import FileJSON, hash_file, load_remote_file, copy_all, wget
from .g_collections import Package
from .logger import Logger, ProgressBar


class PackageDB(object):
    """
    Package database.
    Database is a directory and related data structure.

    Directory layout.
    ~~~~~~~~~~~~~~~~~
    db dir
        manifest.json: database manifest
        categories.json: information about categories
        category1
            packages.json: information about available packages
        category2
        ...
    
    """

    class Iterator(object):
        """
        Iterator class over the package database.
        """
        def __init__(self, package_db):
            self.pkg_iter = iter(package_db.database.items())
            try:
                self.pkgname, self.vers_dict = next(self.pkg_iter)
            except StopIteration:
                self.pkgname, self.vers_dict = None, None
            if self.vers_dict:
                self.vers_iter = iter(self.vers_dict.items())
            else:
                self.vers_iter = None

        def __iter__(self):
            return self

        if py2k:
            def next(self):
                if not self.vers_iter:
                    raise StopIteration
                ver, ebuild_data = None, None
                while not ver:
                    try:
                        ver, ebuild_data = next(self.vers_iter)
                    except StopIteration:
                        ver, ebuild_data = None, None

                    if not ver:
                        self.pkgname, self.vers_dict = next(self.pkg_iter)
                        self.vers_iter = iter(self.vers_dict.items())

                category, name = self.pkgname.split('/')
                return (Package(category, name, ver), ebuild_data)
        else:
            def __next__(self):
                if not self.vers_iter:
                    raise StopIteration
                ver, ebuild_data = None, None
                while not ver:
                    try:
                        ver, ebuild_data = next(self.vers_iter)
                    except StopIteration:
                        ver, ebuild_data = None, None

                    if not ver:
                        self.pkgname, self.vers_dict = next(self.pkg_iter)
                        self.vers_iter = iter(self.vers_dict.items())

                category, name = self.pkgname.split('/')
                return (Package(category, name, ver), ebuild_data)


    def __init__(self, directory):
        """
        Args:
            directory: database directory.
        """
        self.logger = Logger()
        self.CATEGORIES_NAME = 'categories.json'
        self.PACKAGES_NAME = 'packages.json'
        self.directory = os.path.abspath(directory)
        self.reset_db()

    def __iter__(self):
        return(PackageDB.Iterator(self))

    def reset_db(self):
        """
        Reset database.
        """
        self.database = {}
        self.categories = {}

    def sync(self, db_uri):
        """
        Synchronize local database with remote database.

        Args:
            db_uri: URI for synchronization with remote database.
        """
        real_db_uri = self.get_real_db_uri(db_uri)
        download_dir = TemporaryDirectory()
        if wget(real_db_uri, download_dir.name):
            raise SyncError('sync failed: ' + real_db_uri)
        
        temp_dir = TemporaryDirectory()
        for f_name in glob.iglob(os.path.join(download_dir.name, '*.tar.gz')):
            self.logger.info("unpacking " + f_name)
            os.system("tar -xvzf " + f_name + " -C " + temp_dir.name)

        tempdb_dir = os.path.join(temp_dir.name, os.listdir(temp_dir.name)[0])
        tempdb = PackageDB(tempdb_dir)

        if not tempdb.check_manifest()[0]:
            raise IntegrityError('Manifest check failed.')

        self.logger.info("copy files to an actual database")
        self.clean()
        copy_all(tempdb_dir, self.directory)
        
        if not self.check_manifest()[0]:
            raise IntegrityError('Manifest check failed, db inconsistent.')
                
        del download_dir
        del temp_dir

    def get_real_db_uri(self, db_uri):
        """
        Convert self.db_uri to URI where remote database can be
        fetched from.

        Returns:
            URI of remote database file.
        """
        return db_uri
            
    def manifest(self):
        """
        Generate database manifest.
        """
        categories = FileJSON(self.directory, self.CATEGORIES_NAME, [])
        categories = categories.read()
        manifest = {}
        names = [self.CATEGORIES_NAME]
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
        self.logger.info("checking manifest")
        m_f = FileJSON(self.directory, 'manifest.json', [])
        manifest = m_f.read()

        result = True
        errors = []

        names = [self.CATEGORIES_NAME]
        for name in names:
            if not name in manifest:
                raise DBStructureError('Bad manifest: no ' + name + ' entry')

        for name, value in manifest.items():
            if hash_file(os.path.join(self.directory, name), hashlib.md5()) != \
                value:
                errors.append(name)

        if errors:
            result = False

        return (result, errors)

    def clean(self):
        """
        Clean database.
        """
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
        self.reset_db()
        self.write_and_manifest()

    def write_and_manifest(self):
        """
        Write and digest database.
        """
        self.write()
        self.manifest()

    def write(self):
        """
        Write database.
        """
        categories_f = FileJSON(self.directory, self.CATEGORIES_NAME, [])
        categories_f.write(self.categories)

        if self.database:
            self.logger.info("writing database")

        progress_bar = ProgressBar(20, len(list(self.database)))
        if self.database:
            progress_bar.begin()

        categories_content = {}
        for category in self.categories:
            categories_content[category] = {}
        
        for pkgname, versions in self.database.items():
            category, name = pkgname.split('/')
            if not category or (not category in self.categories):
                raise DBStructureError('Non existent: ' + category)
            categories_content[category][name] = {}
            for version, content in versions.items():
                categories_content[category][name][version] = content
                self.additional_write_version(category, name, version)
            self.additional_write_package(category, name)
            progress_bar.increment()

        for category in self.categories:
            f = FileJSON(os.path.join(self.directory, category), self.PACKAGES_NAME, [])
            f.write(categories_content[category])
            self.additional_write_category(category)

        self.additional_write()

        if self.database:
            progress_bar.end()
            print("")

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
        categories_f = FileJSON(self.directory, self.CATEGORIES_NAME, [])
        self.categories = categories_f.read()
        for category in self.categories:
            category_path = os.path.join(self.directory, category)
            if not os.path.isdir(category_path):
                raise DBStructureError('Empty category: ' + category)
            
            f = FileJSON(category_path, self.PACKAGES_NAME, [])
            packages = f.read()
            if not packages:
                raise DBStructureError('Empty category: ' + category)
            
            for name, versions in packages.items():
                
                if not versions:
                    error_msg = 'Empty package: ' + category + '/' + name
                    raise DBStructureError(error_msg)
                
                pkgname = category + '/' + name
                self.database[pkgname] = versions
                for version in versions:
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

    def add_package(self, package, ebuild_data=None):
        """
        Add a package.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with package description.
        """
        if not ebuild_data:
            ebuild_data = {}
        category = package.category
        name = package.name
        version = package.version
        pkgname = category + '/' + name
        if category and not category in self.categories:
            raise InvalidKeyError('Non-existent category: ' + category)
        if pkgname and not pkgname in self.database:
            self.database[pkgname] = {}
        self.database[pkgname][version] = ebuild_data

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
        res = [x.split('/')[1] for x in self.database
               if x.split('/')[0] == category]
        return res

    def list_catpkg_names(self):
        """
        List category/package entries.

        Returns:
            List with category/package entries.
        """
        return list(self.database)

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
        Get package ebuild data.

        Args:
            package: package_db.Package instance.

        Returns:
            Dictionary with package ebuild data.
        """
        #a possible exception should be catched in the caller
        return self.database[package.category \
                             + '/' + package.name][package.version]

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


class DBGenerator(object):
    """
    Generator for package databases.
    Creates new databases or syncs with existing.
    """

    __slots__ = ('package_db_class')

    def __init__(self, package_db_class=PackageDB):
        self.package_db_class = package_db_class

    def __call__(self, directory, repository,
                 common_config=None, config=None, generate=True):
        """
        Get a package database.

        A directory layout looks like:
        backend directory
            config.json
            repo1 dir
                config.json
                db - directory with database
            repo2 dir
                config.json
                db - directory with database

        Args:
            directory: Directory for package databases (backend directory).
            repository: Repository name.
            common_config: Backend config.
            config: Repository config.
            generate: Whether package tree should be generated.

        Returns:
            Package database.
        """
        db_path = os.path.join(directory, repository, "db")
        pkg_db = self.package_db_class(db_path)

        config_f = FileJSON(os.path.join(directory, repository),
                            "config.json", [])
        if config:
            config_f.write(config)
        else:
            config = config_f.read()

        common_config_f = FileJSON(directory, "config.json", [])
        if common_config:
            common_config_f.write(common_config)
        else:
            common_config = common_config_f.read()

        if generate:
            pkg_db.clean()
            self.generate_tree(pkg_db, common_config, config)
            pkg_db.write_and_manifest()
        return pkg_db

    def generate_tree(self, pkg_db, common_config, config):
        """
        Generate package entries.

        Args:
            pkg_db: Package database.
            common_config: Backend config.
            config: Repository config.
        """
        data = self.download_data(common_config, config)
        self.process_data(pkg_db, data, common_config, config)

    def download_data(self, common_config, config):
        """
        Obtain data for database generation.

        Args:
            common_config: Backend config.
            config: Repository config.

        Returns:
            Downloaded data.
        """
        uries = self.get_download_uries(common_config, config)
        uries = self.decode_download_uries(uries)
        data = {}
        for uri in uries:
            self.process_uri(uri, data)
        return data

    def process_uri(self, uri, data):
        """
        Download and parse data from a given URI.

        Args:
            uri: URI.
            data: Data dictionary.
        """
        data.update(load_remote_file(**uri))

    def get_download_uries(self, common_config, config):
        """
        Get uries to download from.

        Args:
            common_config: Backend config.
            config: Repository config.

        Returns:
            List with URI entries.
            Each entry has one of the following formats:
            1. String with URI.
            2. A dictionary with entries:
                - uri: URI.
                - parser: Parser to be applied to downloaded data.
                - open_file: Whether parser accepts file objects.
                - open_mode: Open mode for a downloaded file.
                The only mandatory entry is uri.
        """
        return [config["repo_uri"]]

    def decode_download_uries(self, uries):
        """
        Convert URI list with incomplete and string entries
        into list with complete dictionary entries.

        Args:
            uries: List of URIes.

        Returns:
            List of URIes with dictionary entries.
        """
        decoded = []
        for uri in uries:
            decuri = {}
            if isinstance(uri, basestring):
                decuri["uri"] = uri
                decuri["parser"] = self.parse_data
                decuri["open_file"] = True
                decuri["open_mode"] = "r"
            else:
                decuri = uri
                if not "parser" in decuri:
                    decuri["parser"] = self.parse_data
                if not "open_file" in decuri:
                    decuri["open_file"] = True
                if not "open_mode" in decuri:
                    decuri["open_mode"] = "r"
            decoded.append(decuri)
        return decoded

    def parse_data(self, data_file):
        """
        Parse downloaded data.

        Args:
            data_file: File name of open file object.

        Returns:
            Parsed data.
        """
        #todo: implement reasonable default
        pass

    def process_data(self, pkg_db, data, common_config, config):
        """
        Process downloaded data and fill database.

        Args:
            pkg_db: Package database.
            data: Dictionary with data, keys are file names.
            common_config; Backend config.
            config: Repository config.
        """
        pass

    def convert(self, configs, dict_name, value):
        """
        Convert a value using configs.
        This function is aimed to be used for conversion
        of values such as license or package names.

        Args:
            configs: List of configs.
            dict_name: Name of a dictionary in config
        that should be used for conversion.
            value: Value to convert.

        Returns:
            Converted value.
        """
        result = value
        for config in configs:
            if config:
                if dict_name in config:
                    transform = config[dict_name]
                    if value in transform:
                        result = transform[value]
        return result

    def convert_dependency(self, configs, dependency, external=True):
        """
        Convert dependency.

        Args:
            configs: List of configs.
            dependency: Dependency to be converted.
            external: Whether external deps should be keeped.

        Returns:
            Right dependency name or None if dependency is external and
        external == False.
        """
        external_dep = ""
        for config in configs:
            if config:
                if "external" in config:
                    ext_deps = config["external"]
                    if dependency in ext_deps:
                        external_dep = ext_deps[dependency]
        if external_dep:
            if external:
                return self.convert_external_dependency(configs, external_dep)
            else:
                return None
        else:
            return self.convert_internal_dependency(configs, dependency)

    def convert_internal_dependency(self, configs, dependency):
        """
        Hook to convert internal dependencies.
        """
        return dependency

    def convert_external_dependency(self, configs, dependency):
        """
        Hook to convert external dependencies.
        """
        return dependency
        
    def in_config(self, configs, list_name, value):
        """
        Check whether value is in config.

        Args:
            configs: List of configs.
            list_name: Name of a list in config
        that should be used for checking.
            value: Value to look for.

        Returns:
            Boolean.
        """
        result = False
        for config in configs:
            if config:
                if list_name in config:
                    if value in config[list_name]:
                        result = True
                        break
        return result
