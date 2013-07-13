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

from .g_collections import Package
from .exceptions import DependencyError, DigestError

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
                 eclass_g_class, metadata_g_class, sync_db=True):
        self.db_dir = '.db'
        self.sync_db = sync_db
        self.package_db_class = package_db_class
        self.ebuild_g_with_digest_class = ebuild_g_with_digest_class
        self.ebuild_g_without_digest_class = ebuild_g_without_digest_class
        self.eclass_g_class = eclass_g_class
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

    def get_overlay(self, args, config):
        overlay = args.overlay
        if not overlay:
            if not 'default_overlay' in config:
               print("No overlay given, exiting.")
               return None
            else:
                overlay = config['default_overlay']
        overlay = args.overlay
        return overlay

    def sync(self, args, config):
        db_path = os.path.join(self.get_overlay(args, config), self.db_dir)
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
        db_path = os.path.join(self.get_overlay(args, config), self.db_dir)
        if not db_path:
            return -1
        pkg_db = self.package_db_class(db_path)
        pkg_db.read()
        try:
            categories = pkg_db.list_categories()
            for category in categories:
                print('Category ' + category + ':')
                print('\n')
                packages = pkg_db.list_package_names(category)
                for pkg in packages:
                    max_ver = pkg_db.get_max_version(category, pkg)
                    versions = pkg_db.list_package_versions(category, pkg)
                    desc = pkg_db.get_package_description(Package(category, pkg, max_ver))
                    print('  ' + pkg + ': ' + desc['description'])
                    print('    Available versions: ' + ' '.join(versions))
                    print('\n')
        except Exception as e:
            sys.stderr.write('List failed: ' + str(e) + '\n')
            return -1
        return 0

    def generate(self, args, config):
        overlay = self.get_overlay(args, config)
        db_path = os.path.join(overlay, self.db_dir)
        if not db_path:
            return -1
        pkg_db = self.package_db_class(db_path)
        pkg_db.read()

        pkgname = args.pkgname

        parts = pkgname.split('/')

        category = None
        
        if len(parts) == 1:
            name = parts[0]
        elif len(parts) == 2:
            category = parts[0]
            name = parts[1]
        else:
            sys.stderr.write('Bad package name: ' + pkgname + '\n')
            return -1

        if not category:
            all_categories = pkg_db.list_categories()
            categories = []
            for cat in all_categories:
                if pkg_db.in_category(cat, name):
                    categories.append(cat)

            if not len(categories):
                sys.stderr.write('No package with name ' + pkgname + ' found\n')
                return -1
                    
            if len(categories) > 1:
                sys.stderr.write('Ambiguous packagename: ' + pkgname + '\n')
                sys.stderr.write('Please select one of the following packages:\n')
                for cat in categories:
                    sys.stderr.write('    ' + cat + '/' + pkgname + '\n')
                return -1
                
            category = categories[0]
        versions = pkg_db.list_package_versions(category, name)
        dependencies = set()
        try:
            for version in versions:
                dependencies |= self.solve_dependencies(pkg_db, Package(category, name, version))[0]
        except Exception as e:
            sys.stderr.write('Dependency solving failed: ' + str(e) + '\n')
            return -1
        
        eclasses = []
        for package in dependencies:
            eclasses += pkg_db.get_package_description(package)['eclasses']
        eclasses = list(set(eclasses))
        self.generate_eclasses(overlay, eclasses)
        self.generate_ebuilds(pkg_db, overlay, dependencies, True)
        self.generate_metadatas(pkg_db, overlay, dependencies)
        self.digest(overlay)
        return 0

    def generate_ebuilds(self, package_db, overlay, packages, digest=False):
        if digest:
            ebuild_g = self.ebuild_g_with_digest_class(package_db)
        else:
            ebuild_g = self.ebuild_g_without_digest_class(package_db)
        for package in packages:
            category = package.category
            name = package.name
            version = package.version
            path = os.path.join(overlay, category, name)
            if not os.path.exists(path):
                os.makedirs(path)
            source = ebuild_g.generate(package)
            with open(os.path.join(path, name + '-' + version + '.ebuild'), 'w') as f:
                for line in source:
                    f.write(line + '\n')


    def generate_metadatas(self, package_db, overlay, packages):
        metadata_g = self.metadata_g_class(package_db)
        for package in packages:
            path = os.path.join(overlay, package.category, package.name)
            if not os.path.exists(path):
                os.makedirs(path)
            source = metadata_g.generate(package)
            with open(os.path.join(path, 'metadata.xml'), 'w') as f:
                for line in source:
                    f.write(line + '\n')

    def generate_eclasses(self, overlay, eclasses):
        eclass_g = self.eclass_g_class()
        path = os.path.join(overlay, 'eclass')
        if not os.path.exists(path):
            os.makedirs(path)
        for eclass in eclasses:
            source = eclass_g.generate(eclass)
        with open(os.path.join(path, eclass + '.eclass'), 'w') as f:
            for line in source:
                f.write(line + '\n')


    def solve_dependencies(self, package_db, package, solved_deps=None, unsolved_deps=None):
        if not solved_deps:
            solved_deps = set()
        if not unsolved_deps:
            unsolved_deps = set()
        if package in solved_deps:
            return solved_deps
        if package in unsolved_deps:
            error = 'circular dependency for ' + package.category + '/' + \
              package.name + '-' + package.version
            raise DependencyError(error)
        unsolved_deps.add(package)
        found = True
        try:
            desc = package_db.get_package_description(package)
        except KeyError as e:
            found = False
        if not found:
            error = "package " + package.category + '/' + \
                package.name + '-' + package.version + " not found"
            raise DependencyError(error)
        
        dependencies = desc["dependencies"]
        for pkg in dependencies:
            solved_deps, unsolved_deps = self.solve_dependencies(package_db,
                                                                 pkg,
                                                                 solved_deps, unsolved_deps)
        
        solved_deps.add(package)
        unsolved_deps.remove(package)
        
        return (solved_deps, unsolved_deps)


    def digest(self, overlay):
        prev = os.getcwd()
        os.chdir(overlay)
        if os.system("repoman manifest"):
            raise DigestError('repoman manifest failed')
        os.chdir(prev)
        
    def generate_tree(self, args, config):
        pass

    def install(self, args, config):
        pass
        
    def __call__(self, args, config):
        args = self.parser.parse_args(args)
        return args.func(args, config)
