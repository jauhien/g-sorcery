#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    backend.py
    ~~~~~~~~~~
    
    base class for backends
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import argparse
import glob
import os
import sys

from .package_db import Package

class Backend(object):
    """
    Backend for a repository.

    Command format is as follows:
    g-backend [-o overlay_dir] command
    
    where command is one of the following:
    sync [-u url]
    list
    search word
    generate package_name
    generate-tree [-d --digest]
    install package_name [portage flags]
    
    If no overlay directory is given the default one from backend config is used.
    """
    
    def __init__(self, package_db_class,
                 ebuild_g_with_digest_class, ebuild_g_without_digest_class,
                 metadata_g_class, sync_db=True):
        self.db_dir = '.db'
        self.sync_db = sync_db
        self.package_db_class = package_db_class
        self.ebuild_g_with_digest_class = ebuild_g_with_digest_class
        self.ebuild_g_without_digest_class = ebuild_g_without_digest_class
        self.metadata_g_class = metadata_g_class

        self.parser = argparse.ArgumentParser(description='Automatic ebuild generator.')
        self.parser.add_argument('-o', '--overlay')

        subparsers = self.parser.add_subparsers()

        p_sync = subparsers.add_parser('sync')
        p_sync.add_argument('-u', '--url')
        p_sync.set_defaults(func=self.sync)

        p_list = subparsers.add_parser('list')
        p_list.set_defaults(func=self.list)

        p_generate = subparsers.add_parser('generate')
        p_generate.add_argument('pkgname')
        p_generate.set_defaults(func=self.generate)

        p_generate_tree = subparsers.add_parser('generate-tree')
        p_generate_tree.set_defaults(func=self.generate_tree)
        
        p_install = subparsers.add_parser('install')
        p_install.add_argument('pkgname')
        p_install.set_defaults(func=self.install)

    def get_db_path(self, args, config):
        overlay = args.overlay
        if not overlay:
            if not 'default_overlay' in config:
               print("No overlay given, exiting.")
               return None
            else:
                overlay = config['default_overlay']
        overlay = args.overlay
        db_path = os.path.join(overlay, self.db_dir)
        return db_path

    def sync(self, args, config):
        db_path = self.get_db_path(args, config)
        if not db_path:
            return -1
        url = args.url
        if self.sync_db:
            pkg_db = self.package_db_class(db_path, db_uri=url)
            if not pkg_db.db_uri:
                sys.stderr.write('No url given\n')
                return -1
        else:
            pkg_db = self.package_db_class(db_path, repo_uri=url)
            if not pkg_db.repo_uri:
                sys.stderr.write('No url given\n')
                return -1

        if self.sync_db:
            try:
                pkg_db.sync(db_uri=url)
            except Exception as e:
                sys.stderr.write('Sync failed: ' + str(e) + '\n')
                return -1
        else:
            try:
                pkg_db.generate(repo_uri=url)
            except Exception as e:
                sys.stderr.write('Sync failed: ' + str(e) + '\n')
                return -1
        return 0

    def list(self, args, config):
        db_path = self.get_db_path(args, config)
        if not db_path:
            return -1
        pkg_db = self.package_db_class(db_path)
        pkg_db.read()
        try:
            categories = pkg_db.list_categories()
            for category in categories:
                print('Category ' + category + ':')
                print()
                packages = pkg_db.list_package_names(category)
                for pkg in packages:
                    max_ver = pkg_db.get_max_version(category, pkg)
                    versions = pkg_db.list_package_versions(category, pkg)
                    desc = pkg_db.get_package_description(Package(category, pkg, max_ver))
                    print('  ' + pkg + ': ' + desc['description'])
                    print('    Available versions: ' + ' '.join(versions))
                    print()
        except Exception as e:
            sys.stderr.write('List failed: ' + str(e) + '\n')
            return -1
        return 0

    def generate(self, args, config):
        db_path = self.get_db_path(args, config)
        if not db_path:
            return -1
        pkg_db = self.package_db_class(db_path)
        pkg_db.read()
        

    def generate_tree(self, args, config):
        pass

    def install(self, args, config):
        pass
        
    def __call__(self, args, config):
        args = self.parser.parse_args(args)
        return args.func(args, config)
