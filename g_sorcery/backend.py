#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    backend.py
    ~~~~~~~~~~

    base class for backends

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import argparse
import sys
import os

import portage

from .compatibility import configparser
from .g_collections import Package, elist
from .fileutils import fast_manifest, FileJSON
from .exceptions import DependencyError, DigestError, InvalidKeyError
from .logger import Logger
from .mangler import package_managers
from .package_db import PackageDB

class Backend(object):
    """
    Backend for a repository.

    Command format is as follows:
    g-backend [-o overlay_dir] [-r repository] command

    where command is one of the following:
    sync
    list
    search word
    generate package_name
    generate-tree [-d --digest]
    install package_name [portage flags]

    If no overlay directory is given the default one from backend config is used.
    """

    def __init__(self, package_db_generator_class,
                 ebuild_g_with_digest_class, ebuild_g_without_digest_class,
                 eclass_g_class, metadata_g_class,
                 package_db_class=PackageDB, sync_db=False):
        self.sorcery_dir = '.g-sorcery'
        self.sync_db = sync_db
        self.package_db_generator = package_db_generator_class(package_db_class)
        self.ebuild_g_with_digest_class = ebuild_g_with_digest_class
        self.ebuild_g_without_digest_class = ebuild_g_without_digest_class
        self.eclass_g_class = eclass_g_class
        self.metadata_g_class = metadata_g_class

        self.parser = \
            argparse.ArgumentParser(description='Automatic ebuild generator.')
        self.parser.add_argument('-o', '--overlay')
        self.parser.add_argument('-r', '--repository')

        subparsers = self.parser.add_subparsers()

        p_sync = subparsers.add_parser('sync')
        p_sync.set_defaults(func=self.sync)

        p_list = subparsers.add_parser('list')
        p_list.set_defaults(func=self.list)

        p_generate = subparsers.add_parser('generate')
        p_generate.add_argument('pkgname')
        p_generate.set_defaults(func=self.generate)

        p_generate_tree = subparsers.add_parser('generate-tree')
        p_generate_tree.add_argument('-d', '--digest', action='store_true')
        p_generate_tree.set_defaults(func=self.generate_tree)

        p_install = subparsers.add_parser('install')
        p_install.add_argument('pkgname')
        p_install.add_argument('pkgmanager_flags', nargs=argparse.REMAINDER)
        p_install.set_defaults(func=self.install)

        self.logger = Logger()

    def _get_overlay(self, args, config, global_config):
        """
        Get an overlay directory.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Overlay directory.
        """
        overlay = args.overlay
        if not overlay:
            if not 'default_overlay' in config:
                self.logger.error("no overlay given, exiting.")
                return None
            else:
                overlay = config['default_overlay']
        overlay = args.overlay
        overlay = os.path.abspath(overlay)
        return overlay

    def _get_package_db(self, args, config, global_config):
        """
        Get package database object.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Package database object.
        """
        overlay = self._get_overlay(args, config, global_config)
        backend_path = os.path.join(overlay,
                            self.sorcery_dir, config["package"])
        repository = args.repository
        pkg_db = self.package_db_generator(backend_path,
                                    repository, generate=False)
        return pkg_db

    def sync(self, args, config, global_config):
        """
        Synchronize or generate local database.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Exit status.
        """
        overlay = self._get_overlay(args, config, global_config)
        backend_path = os.path.join(overlay,
                            self.sorcery_dir, config["package"])
        repository = args.repository
        repository_config = {}

        if "common_config" in config:
            common_config = config["common_config"]
        else:
            common_config = {}

        if repository:
            if not "repositories" in config:
                self.logger.error("repository " + repository +
                    " specified, but there is no repositories entry in config")
                return -1
            repositories = config["repositories"]
            if not repository in repositories:
                self.logger.error("repository " + repository + " not found")
                return -1
            repository_config = repositories[repository]
        else:
            self.logger.error('no repository given\n')
            return -1

        try:
            sync_method = repository_config["sync_method"]
        except KeyError:
            sync_method = "tgz"
        if self.sync_db:
            pkg_db = self.package_db_generator(backend_path, repository,
                            common_config, repository_config, generate=False)
            pkg_db.sync(repository_config["db_uri"], repository_config=repository_config, sync_method=sync_method)
        else:
            pkg_db = self.package_db_generator(backend_path,
                            repository, common_config, repository_config)
        return 0

    def list(self, args, config, global_config):
        """
        List all available packages.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Exit status.
        """
        pkg_db = self._get_package_db(args, config, global_config)
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
                    desc = pkg_db.get_package_description(Package(category,
                                                            pkg, max_ver))
                    print('  ' + pkg + ': ' + desc['description'])
                    print('    Available versions: ' + ' '.join(versions))
                    print('\n')
        except Exception as e:
            self.logger.error('list failed: ' + str(e) + '\n')
            return -1
        return 0

    def generate(self, args, config, global_config):
        """
        Generate ebuilds for a given package and all its dependecies.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Exit status.
        """
        overlay = self._get_overlay(args, config, global_config)
        pkg_db = self._get_package_db(args, config, global_config)
        pkg_db.read()

        pkgname = args.pkgname

        try:
            dependencies = self.get_dependencies(pkg_db, pkgname)
        except Exception as e:
            self.logger.error('dependency solving failed: ' + str(e) + '\n')
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
        """
        Generate ebuilds for given packages.

        Args:
            package_db: Package database
            overlay: Overlay directory.
            packages: List of packages.
            digest: whether sources should be digested in Manifest.
        """

        self.logger.info("ebuild generation")
        if digest:
            ebuild_g = self.ebuild_g_with_digest_class(package_db)
        else:
            ebuild_g = self.ebuild_g_without_digest_class(package_db)
        for package in packages:
            category = package.category
            name = package.name
            version = package.version
            self.logger.info("    generating " +
                        category + '/' + name + '-' + version)
            path = os.path.join(overlay, category, name)
            if not os.path.exists(path):
                os.makedirs(path)
            source = ebuild_g.generate(package)
            with open(os.path.join(path,
                        name + '-' + version + '.ebuild'), 'w') as f:
                f.write('\n'.join(source))


    def generate_metadatas(self, package_db, overlay, packages):
        """
        Generate metada files for given packages.

        Args:
            package_db: Package database
            overlay: Overlay directory.
            packages: List of packages.
        """
        self.logger.info("metadata generation")
        metadata_g = self.metadata_g_class(package_db)
        for package in packages:
            path = os.path.join(overlay, package.category, package.name)
            if not os.path.exists(path):
                os.makedirs(path)
            source = metadata_g.generate(package)
            with open(os.path.join(path, 'metadata.xml'), 'w') as f:
                f.write('\n'.join(source))

    def generate_eclasses(self, overlay, eclasses):
        """
        Generate given eclasses.

        Args:
            overlay: Overlay directory.
            eclasses: List of eclasses.
        """
        self.logger.info("eclasses generation")
        eclass_g = self.eclass_g_class()
        path = os.path.join(overlay, 'eclass')
        if not os.path.exists(path):
            os.makedirs(path)
        for eclass in eclasses:
            self.logger.info("    generating " + eclass + " eclass")
            source = eclass_g.generate(eclass)
            with open(os.path.join(path, eclass + '.eclass'), 'w') as f:
                f.write('\n'.join(source))


    def get_dependencies(self, package_db, pkgname):
        """
        Get dependencies for a given package.

        Args:
            package_db: Database.
            pkgname: package name (string).

        Returns:
            A set containing dependencies (instances of Package).
        Package version is ignored currently and a returned set contains all
        the versions of packages pkgname depends on.
        """
        parts = pkgname.split('/')
        category = None
        if len(parts) == 1:
            name = parts[0]
        elif len(parts) == 2:
            category = parts[0]
            name = parts[1]
        else:
            error = 'bad package name: ' + pkgname
            self.logger.error(error + '\n')
            raise DependencyError(error)

        if not category:
            all_categories = package_db.list_categories()
            categories = []
            for cat in all_categories:
                if package_db.in_category(cat, name):
                    categories.append(cat)

            if not len(categories):
                error = 'no package with name ' \
                                  + pkgname + ' found'
                self.logger.error(error + '\n')
                raise DependencyError(error)

            if len(categories) > 1:
                self.logger.error('ambiguous packagename: ' + pkgname + '\n')
                self.logger.error('please select one of' \
                                  + 'the following packages:\n')
                for cat in categories:
                    self.logger.error('    ' + cat + '/' + pkgname + '\n')
                raise DependencyError("ambiguous packagename")

            category = categories[0]
        versions = package_db.list_package_versions(category, name)
        dependencies = set()
        for version in versions:
            dependencies |= self.solve_dependencies(package_db,
                                    Package(category, name, version))[0]
        return dependencies

    def solve_dependencies(self, package_db, package,
                           solved_deps=None, unsolved_deps=None):
        """
        Solve dependencies.

        Args:
            package_db: Package database.
            package: A package we want to solve dependencies for.
            solved_deps: List of solved dependencies.
            unsolved_deps: List of dependencies to be solved.

        Returns:
            A pair (solved_deps, unsolved_deps).

        Note:
            Each dependency is an object of class g_collections.Dependency.
        """
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
        except KeyError:
            found = False
        if not found:
            error = "package " + package.category + '/' + \
                package.name + '-' + package.version + " not found"
            self.logger.error(error)
            # at the moment ignore unsolved dependencies, as those deps can be in other repo
            # or can be external: portage will catch it
            unsolved_deps.remove(package)
            return (solved_deps, unsolved_deps)

        dependencies = desc["dependencies"]
        for pkg in dependencies:
            try:
                versions = package_db.list_package_versions(pkg.category,
                                                        pkg.package)
                for version in versions:
                    solved_deps, unsolved_deps = self.solve_dependencies(package_db,
                                    Package(pkg.category, pkg.package, version),
                                    solved_deps, unsolved_deps)
            except InvalidKeyError:
                # ignore non existing packages
                continue

        solved_deps.add(package)
        unsolved_deps.remove(package)

        return (solved_deps, unsolved_deps)


    def digest(self, overlay):
        """
        Digest an overlay using repoman.

        Args:
            overlay: Overlay directory.
        """
        self.logger.info("digesting overlay")
        prev = os.getcwd()
        os.chdir(overlay)
        if os.system("repoman manifest"):
            raise DigestError('repoman manifest failed')
        os.chdir(prev)

    def fast_digest(self, overlay, pkgnames):
        """
        Digest an overlay using custom method faster than repoman.

        Args:
            overlay: Overlay directory.
            pkgnames: List of full package names (category/package).
        """
        self.logger.info("fast digesting overlay")
        for pkgname in pkgnames:
            directory = os.path.join(overlay, pkgname)
            fast_manifest(directory)

    def generate_tree(self, args, config, global_config):
        """
        Generate entire overlay.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Exit status.
        """
        try:
            packages = global_config.get(config["backend"], args.repository + "_packages").split(" ")
        except Exception:
            packages = []

        self.logger.info("tree generation")
        overlay = self._get_overlay(args, config, global_config)
        pkg_db = self._get_package_db(args, config, global_config)
        pkg_db.read()

        os.system('rm -rf ' + overlay + '/*')
        os.makedirs(os.path.join(overlay, 'profiles'))
        os.system("echo " + os.path.basename(overlay) + '>' + \
                  os.path.join(overlay, 'profiles', 'repo_name'))

        os.makedirs(os.path.join(overlay, 'metadata'))
        if not "masters" in config["repositories"][args.repository]:
            masters = elist(["gentoo"])
        else:
            masters = elist(config["repositories"][args.repository]["masters"])

        overlays = FileJSON(os.path.join(sys.prefix, 'var', 'lib', 'g-sorcery'), "overlays.json", [])
        overlays_old_info = overlays.read()
        overlays_info = {}
        masters_overlays = elist()
        portage_overlays = [repo.location for repo in portage.settings.repositories]

        for repo, info in overlays_old_info.items():
            if info["path"] in portage_overlays:
                overlays_info[repo] = info

        overlays.write(overlays_info)

        for repo in masters:
            if repo != "gentoo":
                if not repo in overlays_info:
                    self.logger.error("Master repository " + repo + " not available on your system")
                    self.logger.error("Please, add it with layman -a " + repo)
                    return -1
                masters_overlays.append(overlays_info[repo]["repo-name"])

        masters_overlays.append("gentoo")

        overlays_info[args.repository] = {"repo-name": os.path.basename(overlay), "path": overlay}
        with open(os.path.join(overlay, 'metadata', 'layout.conf'), 'w') as f:
            f.write("repo-name = %s\n" % os.path.basename(overlay))
            f.write("masters = %s\n" % masters_overlays)

        if args.digest:
            ebuild_g = self.ebuild_g_with_digest_class(pkg_db)
        else:
            ebuild_g = self.ebuild_g_without_digest_class(pkg_db)
        metadata_g = self.metadata_g_class(pkg_db)

        packages_iter = pkg_db
        catpkg_names = pkg_db.list_catpkg_names()
        if packages:
            dependencies = set()
            catpkg_names = set()
            packages_dict = {}
            for pkg in packages:
                dependencies |= self.get_dependencies(pkg_db, pkg)

            for pkg in dependencies:
                catpkg_names |= set([pkg.category + '/' + pkg.name])
                packages_dict[pkg] = pkg_db.get_package_description(pkg)
            packages_iter = packages_dict.items()

        for package, ebuild_data in packages_iter:
            category = package.category
            name = package.name
            version = package.version
            self.logger.info("    generating " +
                             category + '/' + name + '-' + version)
            path = os.path.join(overlay, category, name)
            if not os.path.exists(path):
                os.makedirs(path)
            source = ebuild_g.generate(package, ebuild_data)
            with open(os.path.join(path,
                        name + '-' + version + '.ebuild'),
                      'wb') as f:
                f.write('\n'.join(source).encode('utf-8'))

            source = metadata_g.generate(package)
            with open(os.path.join(path, 'metadata.xml'), 'wb') as f:
                f.write('\n'.join(source).encode('utf-8'))

        eclass_g = self.eclass_g_class()
        path = os.path.join(overlay, 'eclass')
        if not os.path.exists(path):
            os.makedirs(path)

        for eclass in eclass_g.list():
            source = eclass_g.generate(eclass)
            with open(os.path.join(path, eclass + '.eclass'), 'w') as f:
                f.write('\n'.join(source))

        if args.digest:
            self.digest(overlay)
        else:
            pkgnames = catpkg_names
            self.fast_digest(overlay, pkgnames)
        overlays.write(overlays_info)

        try:
            clean_db = config["repositories"][args.repository]["clean_db"]
        except KeyError:
            clean_db = False
        if clean_db:
            pkg_db.clean()

    def install(self, args, config, global_config):
        """
        Install a package.

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Exit status.
        """
        self.generate(args, config, global_config)
        try:
            package_manager = global_config.get("main", "package_manager")
        except configparser.NoOptionError:
            package_manager_class = package_managers["portage"]
            package_manager = None
        if  package_manager:
            if not package_manager in package_managers:
                self.logger.error('not supported package manager: ' \
                                + package_manager + '\n')
                return -1
            package_manager_class = package_managers[package_manager]
        package_manager = package_manager_class()
        package_manager.install(args.pkgname, *args.pkgmanager_flags)

    def __call__(self, args, config, global_config):
        """
        Execute a command

        Args:
            args: Command line arguments.
            config: Backend config.
            global_config: g-sorcery config.

        Returns:
            Exit status.
        """
        args = self.parser.parse_args(args)
        info_f = FileJSON(os.path.join(args.overlay, self.sorcery_dir),
                          "info.json", ["repositories"])
        self.info = info_f.read()
        repos = self.info["repositories"]
        if args.repository:
            if not repos:
                repos = {}
            back = config["package"]
            if back in repos:
                brepos = set(repos[back])
            else:
                brepos = set()
            brepos.add(args.repository)
            repos[back] = list(brepos)
            self.info["repositories"] = repos
            info_f.write(self.info)
        else:
            back = config["package"]
            if back in repos:
                brepos = repos[back]
                if len(brepos) == 1:
                    args.repository = brepos[0]
                else:
                    self.logger.error("No repository specified," \
                                      + " possible values:")
                    for repo in brepos:
                        print("    " + repo)
                    return -1
            else:
                self.logger.error("No repository for backend " \
                                  + back + " in overlay " + args.overlay)
                return -1
        return args.func(args, config, global_config)
