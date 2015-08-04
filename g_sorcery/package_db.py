#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    package_db.py
    ~~~~~~~~~~~~~

    package database

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

import portage

from .compatibility import basestring, py2k

from .db_layout import DBLayout, JSON_FILE_SUFFIX, SUPPORTED_DB_LAYOUTS, SUPPORTED_FILE_FORMATS
from .exceptions import DBError, DBLayoutError, DBStructureError, InvalidKeyError, SyncError
from .fileutils import FileJSON, load_remote_file, copy_all
from .g_collections import Package
from .logger import Logger
from .syncer import SUPPORTED_SYNCERS

SUPPORTED_DB_STRUCTURES=[0, 1]

class PackageDB(object):
    """
    Package database.
    It uses DBLayout class to manipulate files that
    contain DB stored on disk.

    There are two versions of DB layout now:
        0 -- legacy version
        1 -- new version that supports DB structure versioning

    DB structure itself has two versions:
        0 -- legacy version, categories contain dictionary package name: versions dict
        1 -- actual version, corresponds to the DB in memory:
            DB is a dictionary with categories as keys.
            Each category contains a dictionary with two entries:
                common_data -- fields common to all the packages
                packages -- dictionary with packages (content of category dictionary in v. 0)

    For DB layout v. 0 only DB structure v. 0 is possible.
    """

    class Iterator(object):
        """
        Iterator class over the package database.
        """
        def __init__(self, package_db):
            self.cats_iter = iter(package_db.database.items())
            try:
                self.cat_name, self.cat_data = next(self.cats_iter)
            except StopIteration:
                self.set_to_end()
                return

            if not self.cat_data:
                self.set_to_end()
                return

            self.pkgs_iter = iter(self.cat_data['packages'].items())
            try:
                self.pkg_name, self.pkg_data = next(self.pkgs_iter)
            except StopIteration:
                self.set_to_end()
                return

            if not self.pkg_data:
                self.set_to_end()
                return

            self.vers_iter = iter(self.pkg_data.items())

        def set_to_end(self):
            self.cat_name, self.cat_data = None, None
            self.pkgs_iter = None
            self.pkg_name, self.pkg_data = None, None
            self.vers_iter = None

        def __iter__(self):
            return self

        if py2k:
            def next(self):
                if not self.vers_iter or not self.pkgs_iter:
                    raise StopIteration

                ver, ebuild_data = None, None
                while not ver:
                    try:
                        ver, ebuild_data = next(self.vers_iter)
                    except StopIteration:
                        ver, ebuild_data = None, None
                    if not ver:
                        try:
                            self.pkg_name, self.pkg_data = next(self.pkgs_iter)
                            self.vers_iter = iter(self.pkg_data.items())
                        except StopIteration:
                            self.cat_name, self.cat_data = next(self.cats_iter)
                            self.pkgs_iter = iter(self.cat_data['packages'].items())
                            self.pkg_name, self.pkg_data = next(self.pkgs_iter)
                            self.vers_iter = iter(self.pkg_data.items())

                ebuild_data = dict(ebuild_data)
                ebuild_data.update(self.cat_data['common_data'])
                return (Package(self.cat_name, self.pkg_name, ver), ebuild_data)

        else:
            def __next__(self):
                if not self.vers_iter or not self.pkgs_iter:
                    raise StopIteration

                ver, ebuild_data = None, None
                while not ver:
                    try:
                        ver, ebuild_data = next(self.vers_iter)
                    except StopIteration:
                        ver, ebuild_data = None, None
                    if not ver:
                        try:
                            self.pkg_name, self.pkg_data = next(self.pkgs_iter)
                            self.vers_iter = iter(self.pkg_data.items())
                        except StopIteration:
                            self.cat_name, self.cat_data = next(self.cats_iter)
                            self.pkgs_iter = iter(self.cat_data['packages'].items())
                            self.pkg_name, self.pkg_data = next(self.pkgs_iter)
                            self.vers_iter = iter(self.pkg_data.items())

                ebuild_data = dict(ebuild_data)
                ebuild_data.update(self.cat_data['common_data'])
                return (Package(self.cat_name, self.pkg_name, ver), ebuild_data)


    def __init__(self, directory,
                 persistent_datadir = None,
                 preferred_layout_version=1,
                 preferred_db_version=1,
                 preferred_category_format=JSON_FILE_SUFFIX):

        if preferred_layout_version == 0 \
           and preferred_db_version != 0:
            raise DBStructureError("Wrong DB version: " + str(preferred_db_version) + \
                                   ", with DB layout version 0 it can be only 0")

        if not preferred_db_version in SUPPORTED_DB_STRUCTURES:
            raise DBStructureError("Unsupported DB version: " + str(preferred_db_version))

        if not preferred_layout_version in SUPPORTED_DB_LAYOUTS:
            raise DBLayoutError("unsupported DB layout version: " + str(preferred_layout_version))

        if not preferred_category_format in SUPPORTED_FILE_FORMATS:
            raise DBLayoutError("unsupported packages file format: " + preferred_category_format)

        self.logger = Logger()
        self.directory = os.path.abspath(directory)

        self.persistent_datadir = persistent_datadir
        if self.persistent_datadir is not None:
            self.persistent_datadir = os.path.abspath(self.persistent_datadir)

        self.preferred_layout_version = preferred_layout_version
        self.preferred_db_version = preferred_db_version
        self.preferred_category_format = preferred_category_format
        self.db_layout = DBLayout(self.directory)
        self.reset_db()


    def __iter__(self):
        return PackageDB.Iterator(self)


    def reset_db(self):
        """
        Reset database.
        """
        self.database = {}
        self.categories = {}


    def sync(self, db_uri, repository_config = None, sync_method="tgz"):
        """
        Synchronize local database with remote database.

        Args:
            db_uri: URI for synchronization with remote database.
            repository_config: repository config.
            sync_method: sync method (tgz or git).
        """
        if repository_config is None:
            repository_config = {}

        try:
            syncer_cls = SUPPORTED_SYNCERS[sync_method]
        except KeyError:
            raise SyncError('unsupported sync method: ' + sync_method)
        if self.persistent_datadir is not None:
            remotedb_dir = os.path.join(self.persistent_datadir, 'remote')
        else:
            remotedb_dir = None
        syncer = syncer_cls(remotedb_dir)
        synced_data = syncer.sync(db_uri, repository_config)

        tempdb_dir = synced_data.get_path()
        tempdb = PackageDB(tempdb_dir)

        tempdb.db_layout.check_manifest()

        self.logger.info("copy files to an actual database")
        self.clean()
        copy_all(tempdb_dir, self.directory)

        self.db_layout.check_manifest()

        del synced_data


    def clean(self):
        """
        Clean database.
        """
        self.db_layout.clean()
        self.reset_db()


    def write(self):
        """
        Write and digest database.
        """
        if self.database:
            self.logger.info("writing database...")

        metadata = {'db_version': self.preferred_db_version,
                    'layout_version': self.preferred_layout_version,
                    'category_format': self.preferred_category_format}

        if self.preferred_db_version == 0:
            packages = dict(self.database)
            for category, cat_data in packages.items():
                for _, versions in cat_data['packages'].items():
                    for version, ebuild_data in versions.items():
                        ebuild_data.update(cat_data['common_data'])
                packages[category] = cat_data['packages']
        else:
            packages = dict(self.database)

        self.db_layout.write(metadata, self.categories, packages)

        if self.database:
            self.logger.info("database written")


    def read(self):
        """
        Read database.
        """
        metadata, self.categories, packages = self.db_layout.read()

        db_version = metadata['db_version']
        self.database = packages
        if db_version == 0:
            for category, cat_data in self.database.items():
                self.database[category] = {'common_data': {}, 'packages': cat_data}
        elif db_version == 1:
            pass
        else:
            raise DBStructureError("Unsupported DB version: " + str(db_version))


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


    def set_common_data(self, category, common_data):
        """
        Set common data for a category.

        Args:
            category: Category name.
            common_data: Category common data.
        """
        if not category in self.categories:
            raise InvalidKeyError('Non-existent category: ' + category)

        if not category in self.database:
            self.database[category] = {'common_data': common_data, 'packages': {}}
        else:
            self.database[category]['common_data'] = common_data


    def get_common_data(self, category):
        """
        Get common data for a category.

        Args:
            category: Category name.

        Returns:
            Dictionary with category common data.
        """
        if not category in self.categories:
            raise InvalidKeyError('Non-existent category: ' + category)

        if not category in self.database:
            return {}
        else:
            return self.database[category]['common_data']


    def add_package(self, package, ebuild_data=None):
        """
        Add a package.

        Args:
            package: g_collections.Package instance.
            ebuild_data: Dictionary with package description.
        """
        if not ebuild_data:
            ebuild_data = {}

        category = package.category
        name = package.name
        version = package.version

        if not category or not name or not version:
            raise DBError("wrong package: " + str(package))

        if not category in self.categories:
            raise InvalidKeyError('Non-existent category: ' + category)

        if not category in self.database:
            self.database[category] = {'common_data': {}, 'packages': {}}

        if not name in self.database[category]['packages']:
            self.database[category]['packages'][name] = {}

        self.database[category]['packages'][name][version] = ebuild_data


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

        if not category in self.database:
            return False

        return name in self.database[category]['packages']


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

        if not category in self.database:
            return []

        return list(self.database[category]['packages'])


    def list_catpkg_names(self):
        """
        List category/package entries.

        Returns:
            List with category/package entries.
        """
        result = []
        for category, cat_data in self.database.items():
            for name in cat_data['packages']:
                result.append(category + '/' + name)
        return result


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

        if not category in self.database \
           or not name in self.database[category]['packages']:
            raise InvalidKeyError('No such package: ' + category + '/' + name)

        return list(self.database[category]['packages'][name])


    def list_all_packages(self):
        """
        List all packages in a database.

        Returns:
            List of g_collections.Package instances.
        """
        result = []
        for category, cat_data in self.database.items():
            for name, versions in cat_data['packages'].items():
                for version in versions:
                    result.append(Package(category, name, version))
        return result


    def get_package_description(self, package):
        """
        Get package ebuild data.

        Args:
            package: g_collections.Package instance.

        Returns:
            Dictionary with package ebuild data.
        """
        #a possible exception should be catched in the caller
        desc = dict(self.database[package.category]['packages']\
                    [package.name][package.version])
        desc.update(self.database[package.category]['common_data'])
        return desc


    def get_max_version(self, category, name):
        """
        Get the recent available version of a package.

        Args:
            category: Category name.
            name: package name.

        Returns:
            The recent version of a package.
        """
        if not category or (not category in self.categories):
            raise InvalidKeyError('No such category: ' + category)

        if not category in self.database \
           or not name in self.database[category]['packages']:
            raise InvalidKeyError('No such package: ' + category + '/' + name)

        pkgname = category + '/' + name
        versions = list(self.database[category]['packages'][name])
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

    def __init__(self, package_db_class=PackageDB,
                 preferred_layout_version=1,
                 preferred_db_version=1,
                 preferred_category_format=JSON_FILE_SUFFIX):
        self.package_db_class = package_db_class
        self.preferred_layout_version = preferred_layout_version
        self.preferred_db_version = preferred_db_version
        self.preferred_category_format = preferred_category_format


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
        persistent_datadir = os.path.join(directory, repository, "persistent")
        pkg_db = self.package_db_class(db_path,
                                       preferred_layout_version=self.preferred_layout_version,
                                       preferred_db_version=self.preferred_db_version,
                                       preferred_category_format=self.preferred_category_format,
                                       persistent_datadir=persistent_datadir)

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
            pkg_db.write()
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
