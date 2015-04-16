#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    db_layout.py
    ~~~~~~~~~~~~

    package database file layout

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import hashlib
import os
import shutil

from .exceptions import DBLayoutError, DBStructureError, FileJSONError, IntegrityError
from .fileutils import FileJSON, hash_file

CATEGORIES_FILE_NAME = 'categories'
MANIFEST_FILE_NAME = 'manifest'
METADATA_FILE_NAME = 'metadata'
PACKAGES_FILE_NAME = 'packages'

JSON_FILE_SUFFIX = 'json'
BSON_FILE_SUFFIX = 'bson'

class CategoryJSON(FileJSON):
    """
    Category file in JSON format.
    """
    def __init__(self, directory, category):
        super(CategoryJSON, self).__init__(os.path.join(os.path.abspath(directory), category),
                                           file_name(PACKAGES_FILE_NAME, JSON_FILE_SUFFIX))


SUPPORTED_FILE_FORMATS = {JSON_FILE_SUFFIX: CategoryJSON}


# bson module is optional, we should check if it is installed
try:
    from g_sorcery.bson.bson import FileBSON

    class CategoryBSON(FileBSON):
        """
        Category file in BSON format.
        """
        def __init__(self, directory, category):
            super(CategoryBSON, self).__init__(os.path.join(os.path.abspath(directory), category),
                                               file_name(PACKAGES_FILE_NAME, BSON_FILE_SUFFIX))

    SUPPORTED_FILE_FORMATS[BSON_FILE_SUFFIX] = CategoryBSON

except ImportError as e:
    pass


def file_name(name, suffix=JSON_FILE_SUFFIX):
    """
    Return file name based on name and suffix.
    """
    return name + '.' + suffix


class Manifest(FileJSON):
    """
    Manifest file.
    """

    def __init__(self, directory):
        super(Manifest, self).__init__(os.path.abspath(directory), file_name(MANIFEST_FILE_NAME))

    def check(self):
        """
        Check manifest.
        """
        manifest = self.read()

        result = True
        errors = []

        names = [file_name(CATEGORIES_FILE_NAME)]
        for name in names:
            if not name in manifest:
                raise DBLayoutError('Bad manifest: no ' + name + ' entry')

        for name, value in manifest.items():
            if hash_file(os.path.join(self.directory, name), hashlib.md5()) != \
                value:
                errors.append(name)

        if errors:
            result = False

        return (result, errors)

    def digest(self, mandatory_files):
        """
        Generate manifest.
        """
        if not file_name(CATEGORIES_FILE_NAME) in mandatory_files:
            raise DBLayoutError('Categories file: ' + file_name(CATEGORIES_FILE_NAME) \
                                + ' is not in the list of mandatory files')

        categories = Categories(self.directory)
        categories = categories.read()

        manifest = {}

        for name in mandatory_files:
            manifest[name] = hash_file(os.path.join(self.directory, name),
                                       hashlib.md5())

        for category in categories:
            category_path = os.path.join(self.directory, category)
            if not os.path.isdir(category_path):
                raise DBStructureError('Empty category: ' + category)
            for root, _, files in os.walk(category_path):
                for f in files:
                    manifest[os.path.join(root[len(self.directory)+1:], f)] = \
                    hash_file(os.path.join(root, f), hashlib.md5())

        self.write(manifest)


class Metadata(FileJSON):
    """
    Metadata file.
    """
    def __init__(self, directory):
        super(Metadata, self).__init__(os.path.abspath(directory),
                                       file_name(METADATA_FILE_NAME),
                                       ['db_version', 'layout_version', 'category_format'])

    def read(self):
        """
        Read metadata file.

        If file doesn't exist, we have a legacy DB
        with DB layout v. 0. Fill metadata appropriately.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        content = {}
        if not os.path.isfile(self.path):
            content = {'db_version': 0, 'layout_version': 0, 'category_format': JSON_FILE_SUFFIX}
        else:
            content = self.read_content()
            for key in self.mandatories:
                if not key in content:
                    raise FileJSONError('lack of mandatory key: ' + key)

        return content


class Categories(FileJSON):
    """
    Categories file.
    """
    def __init__(self, directory):
        super(Categories, self).__init__(os.path.abspath(directory),
                                         file_name(CATEGORIES_FILE_NAME))


def get_layout(metadata):
    """
    Get layout parameters based on metadata.
    """
    layout_version = metadata['layout_version']
    if layout_version == 0:
        return (CategoryJSON, [file_name(CATEGORIES_FILE_NAME)])
    elif layout_version == 1:
        category_format = metadata['category_format']
        try:
            category_cls = SUPPORTED_FILE_FORMATS[category_format]
        except KeyError:
            raise DBLayoutError("unsupported packages file format: " + category_format)
        return (category_cls, [file_name(CATEGORIES_FILE_NAME), file_name(METADATA_FILE_NAME)])
    else:
        raise DBLayoutError("unsupported DB layout version: " + layout_version)


class DBLayout(object):
    """
    Filesystem DB layout.

    Directory layout.
    ~~~~~~~~~~~~~~~~~

    For legacy DB layout v. 0:

    db dir
        manifest.json: database manifest
        categories.json: information about categories
        category1
            packages.json: information about available packages
        category2
        ...

    For DB layout v. 1:

    db dir
        manifest.json: database manifest
        categories.json: information about categories
        metadata.json: DB metadata
        category1
            packages.[b|j]son: information about available packages
        category2
        ...

    Packages file can be in json or bson formats.
    """

    def __init__(self, directory):
        self.directory = os.path.abspath(directory)
        self.manifest = Manifest(self.directory)

    def check_manifest(self):
        """
        Check manifest.
        """
        sane, errors = self.manifest.check()
        if not sane:
            raise IntegrityError('Manifest error: ' + str(errors))

    def clean(self):
        """
        Remove DB files.
        """
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)

    def read(self):
        """
        Read DB files.

        Returns a tuple with metadata, list of categories
        and categories dictionary.
        """
        self.check_manifest()

        metadata_f = Metadata(self.directory)
        metadata = metadata_f.read()

        category_cls, _ = get_layout(metadata)

        categories_f = Categories(self.directory)
        categories = categories_f.read()

        packages = {}
        for category in categories:
            category_path = os.path.join(self.directory, category)
            if not os.path.isdir(category_path):
                raise DBLayoutError('Empty category: ' + category)
            category_f = category_cls(self.directory, category)
            pkgs = category_f.read()
            if not pkgs:
                raise DBLayoutError('Empty category: ' + category)
            packages[category] = pkgs

        return (metadata, categories, packages)

    def write(self, metadata, categories, packages):
        """
        Write DB files.
        """
        category_cls, mandatory_files = get_layout(metadata)

        self.clean()

        if file_name(METADATA_FILE_NAME) in mandatory_files:
            metadata_f = Metadata(self.directory)
            metadata_f.write(metadata)

        categories_f = Categories(self.directory)
        categories_f.write(categories)

        for category in categories:
            category_f = category_cls(self.directory, category)
            category_f.write(packages[category])

        self.manifest.digest(mandatory_files)
