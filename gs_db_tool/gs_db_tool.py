#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    gs_db_tool.py
    ~~~~~~~~~~~~~
    
    CLI to manipulate with package DB
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import argparse

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
    p_ebuild_data_rename.add_argument('-l', '--lambda_function')

    p_ebuild_data_rename = p_ebuild_data_subparsers.add_parser('rename_var')
    p_ebuild_data_rename.set_defaults(func=rename_var)
    p_ebuild_data_rename.add_argument('old_name')
    p_ebuild_data_rename.add_argument('new_name')

    p_ebuild_data_show_all = p_ebuild_data_subparsers.add_parser('show_all')
    p_ebuild_data_show_all.set_defaults(func=show_all)

    p_sync = subparsers.add_parser('sync')
    p_sync.set_defaults(func=sync)
    p_sync.add_argument('uri')

    args = parser.parse_args()
    pkg_db = PackageDB(args.db_dir)
    return args.func(pkg_db, args)


def transform_db(function):
    def transformator(pkg_db, args):
        pkg_db.read()
        function(pkg_db, args)
        pkg_db.write_and_manifest()
    return transformator


@transform_db
def add_var(pkg_db, args):
    if args.lambda_function:
        lmbd = "lambda ebuild_data: " + args.lambda_function
        f = eval(lmbd)
        for package, ebuild_data in pkg_db:
            value = f(ebuild_data)
            ebuild_data[args.name] = value
            pkg_db.add_package(package, ebuild_data)


def show_all(pkg_db, args):
    pkg_db.read()
    for package, ebuild_data in pkg_db:
        print(package)
        print('-' * len(str(package)))
        for key, value in ebuild_data.items():
            print("    " + key + ": " + repr(value))
        print("")


def sync(pkg_db, args):
    pkg_db.sync(args.uri)


@transform_db
def rename_var(pkg_db, args):
    for package, ebuild_data in pkg_db:
        if args.old_name in ebuild_data:
            value = ebuild_data.pop(args.old_name)
            ebuild_data[args.new_name] = value
        pkg_db.add_package(package, ebuild_data)


if __name__ == "__main__":
    sys.exit(main())
