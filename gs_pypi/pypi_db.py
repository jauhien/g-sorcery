#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    pypi_db.py
    ~~~~~~~~~~
    
    PyPI package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

from g_sorcery.compatibility import py2k

if py2k:
    import xmlrpclib
else:
    import xmlrpc.client as xmlrpclib

import datetime
import re
import sys

from g_sorcery.g_collections import Package, serializable_elist
from g_sorcery.logger import Logger 
from g_sorcery.package_db import DBGenerator

class PypiDBGenerator(DBGenerator):

    def get_download_uries(self, common_config, config):
        return [config["repo_uri"] + "/pypi"]

    def process_uri(self, uri, data):
        url = uri["uri"]
        client = xmlrpclib.ServerProxy(url)
        logger = Logger()
        logger.info("downloading packages data")
        pkg_list = client.list_packages()

        number_of_packages = len(pkg_list)
        downloaded_number = 0

        for pkg in pkg_list:
            data[pkg] = {}

            chars = ['-','\\','|','/']
            show = chars[downloaded_number % 4]
            percent = (downloaded_number * 100)//number_of_packages
            length = 70
            progress = (percent * length)//100
            blank = length - progress

            sys.stdout.write("\r %s [%s%s] %s%%" % (show, "#" * progress, " " * blank, percent))
            sys.stdout.flush()
            downloaded_number += 1

            versions = client.package_releases(pkg)
            for version in versions:
                data[pkg][version] = client.release_data(pkg, version)

        sys.stdout.write("\r %s [%s] %s%%" % ("-", "#" * length, 100))
        sys.stdout.flush()
        print("")

    def process_data(self, pkg_db, data, common_config, config):
        category = "dev-python"
        pkg_db.add_category(category)

        #todo: write filter functions
        allowed_ords_pkg = set(range(ord('a'), ord('z'))) | set(range(ord('A'), ord('Z'))) | \
            set(range(ord('0'), ord('9'))) | set(list(map(ord,
                ['+', '_', '-'])))

        allowed_ords_desc = set(range(ord('a'), ord('z'))) | set(range(ord('A'), ord('Z'))) | \
              set(range(ord('0'), ord('9'))) | set(list(map(ord,
                    ['+', '_', '-', ' ', '.', '(', ')', '[', ']', '{', '}', ','])))

        now = datetime.datetime.now()
        pseudoversion = "%04d%02d%02d" % (now.year, now.month, now.day)
        
        for package, versions in data.items():
            package = "".join([x for x in package if ord(x) in allowed_ords_pkg])
            for version, ebuild_data in versions.items():
                description = ebuild_data["summary"]
                description = "".join([x for x in description if ord(x) in allowed_ords_desc])
                longdescription = ebuild_data["description"]
                longdescription = "".join([x for x in longdescription if ord(x) in allowed_ords_desc])

                pkgver = version            
                match_object = re.match("(^[0-9]+[a-z]?$)|(^[0-9][0-9\.]+[0-9][a-z]?$)", pkgver)
                if not match_object:
                    pkgver = pseudoversion

                dependencies = serializable_elist(separator="\n\t")
                eclasses = ['gs-pypi']
                maintainer = [{'email' : 'piatlicki@gmail.com',
                               'name' : 'Jauhien Piatlicki'}]

                ebuild_data["description"] = description
                ebuild_data["longdescription"] = longdescription
                ebuild_data["dependencies"] = dependencies
                ebuild_data["eclasses"] = eclasses
                ebuild_data["maintainer"] = maintainer

                pkg_db.add_package(Package(category, package, pkgver), ebuild_data)
