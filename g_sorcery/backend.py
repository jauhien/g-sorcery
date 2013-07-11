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

    def sync(self, args):
        pass

    def list(self, args):
        pass

    def generate(self, args):
        pass

    def generate_tree(self, args):
        pass

    def install(self,args):
        pass
        
    def __call__(self, args):
        pass
