#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    gs_db_tool.py
    ~~~~~~~~~~~~~

    CLI to manipulate package DB

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import argparse
import sys

from g_sorcery.package_db import PackageDB

def main():
    parser = \
            argparse.ArgumentParser(description='Package DB manipulation tool')
    parser.add_argument('db_dir')

    subparsers = parser.add_subparsers()

    p_ebuild_data = subparsers.add_parser('ebuild_data')
    p_ebuild_data_subparsers = p_ebuild_data.add_subparsers()

    p_ebuild_data_rename = p_ebuild_data_subparsers.add_parser('add_var')
    p_ebuild_data_rename.set_defaults(func=add_var)
    p_ebuild_data_rename.add_argument('name')
    p_ebuild_data_rename.add_argument('-f', '--function')
    p_ebuild_data_rename.add_argument('-l', '--lambda_function')
    p_ebuild_data_rename.add_argument('-v', '--value')

    p_ebuild_data_rename = p_ebuild_data_subparsers.add_parser('rename_var')
    p_ebuild_data_rename.set_defaults(func=rename_var)
    p_ebuild_data_rename.add_argument('old_name')
    p_ebuild_data_rename.add_argument('new_name')

    p_ebuild_data_show_all = p_ebuild_data_subparsers.add_parser('show_all')
    p_ebuild_data_show_all.set_defaults(func=show_all)

    p_ebuild_data_for_all = p_ebuild_data_subparsers.add_parser('for_all')
    p_ebuild_data_for_all.add_argument('function')
    p_ebuild_data_for_all.set_defaults(func=for_all)

    p_sync = subparsers.add_parser('sync')
    p_sync.set_defaults(func=sync)
    p_sync.add_argument('uri')

    args = parser.parse_args()
    pkg_db = PackageDB(args.db_dir)
    return args.func(pkg_db, args)


def transform_db(function):
    """
    Decorator for functions that change database.
    """
    def transformator(pkg_db, args):
        pkg_db.read()
        function(pkg_db, args)
        pkg_db.write()
    return transformator


def read_db(function):
    """
    Decorator for functions that read from database.
    """
    def reader(pkg_db, args):
        pkg_db.read()
        function(pkg_db, args)
    return reader


@read_db
def for_all(pkg_db, args):
    """
    Execute a given python code for all DB entries.
    """
    for package, ebuild_data in pkg_db:
        exec(args.function)


@transform_db
def add_var(pkg_db, args):
    """
    Add new variable to every entry.
    """
    if args.function:
        for package, ebuild_data in pkg_db:
            exec(args.function)
            ebuild_data[args.name] = value
            pkg_db.add_package(package, ebuild_data)

    elif args.lambda_function:
        lmbd = "lambda package, ebuild_data: " + args.lambda_function
        f = eval(lmbd)
        for package, ebuild_data in pkg_db:
            value = f(package, ebuild_data)
            ebuild_data[args.name] = value
            pkg_db.add_package(package, ebuild_data)

    elif args.value:
        for package, ebuild_data in pkg_db:
            ebuild_data[args.name] = args.value
            pkg_db.add_package(package, ebuild_data)


@read_db
def show_all(pkg_db, args):
    """
    Display all DB entries.
    """
    for package, ebuild_data in pkg_db:
        print(package)
        print('-' * len(str(package)))
        for key, value in ebuild_data.items():
            print("    " + key + ": " + repr(value))
        print("")


def sync(pkg_db, args):
    """
    Synchronize database.
    """
    pkg_db.sync(args.uri)


@transform_db
def rename_var(pkg_db, args):
    """
    Rename variable in all entries.
    """
    for package, ebuild_data in pkg_db:
        if args.old_name in ebuild_data:
            value = ebuild_data.pop(args.old_name)
            ebuild_data[args.new_name] = value
        pkg_db.add_package(package, ebuild_data)


if __name__ == "__main__":
    sys.exit(main())
