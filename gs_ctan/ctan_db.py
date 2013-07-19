#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ctan_db.py
    ~~~~~~~~~~
    
    CTAN package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import itertools
import os
import re
import sys

import portage

from g_sorcery.g_collections import Dependency, Package, serializable_elist
from g_sorcery.logger import Logger
from g_sorcery.package_db import PackageDB
from g_sorcery.exceptions import SyncError

class CtanDB(PackageDB):
    def __init__(self, directory, config = None, common_config = None):
        super(CtanDB, self).__init__(directory, config, common_config)
        
        logger = Logger()
        gentoo_arch = portage.settings['ARCH']
        self.arch = ""
        if gentoo_arch == "x86":
            self.arch = "i386-linux"
        elif gentoo_arch == "amd64":
            self.arch = "x86_64-linux"
        else:
            logger.warning("not supported arch: " + gentoo_arch)


    def get_download_uries(self):
        tlpdb_uri = self.repo_uri + "/tlpkg/texlive.tlpdb.xz"
        return [tlpdb_uri]
        
    def parse_data(self, data_f):
        data = data_f.read()
        
        data = data.split("\n")
        
        #entries are separated by new lines
        data = \
        [list(group) for key, group in itertools.groupby(data, bool) if key]

        #we need only Package entries
        data = \
        [entry for entry in data if entry[1] == "category Package"]

        result = []

        KEY = 0
        VALUE = 1
        FILES_LENGTH = len("files")
        
        for entry in data:     
            res_entry = {}
            previous_key = ""
            current_key = ""
            for line in entry:
                line = line.split(" ")
                if line[KEY][-FILES_LENGTH:] == "files":
                    current_key = line[KEY]
                    res_entry[current_key] = {}
                    for value in line[VALUE:]:
                        key, val = value.split("=")
                        res_entry[current_key][key] = val
                    res_entry[current_key]["files"] = []
                elif not line[KEY]:
                    res_entry[current_key]["files"].append(" ".join(line[VALUE:]))
                elif line[KEY] == "depend":
                    if "depend" in res_entry:
                        res_entry["depend"].append(" ".join(line[VALUE:]))
                    else:
                        res_entry["depend"] = [" ".join(line[VALUE:])]
                else:
                    if previous_key == line[KEY]:
                        res_entry[previous_key] += " " + " ".join(line[VALUE:])
                    else:
                        res_entry[line[KEY]] = " ".join(line[VALUE:])
                        previous_key = line[KEY]
                        current_key = ""

            parts = res_entry["name"].split(".")
            if len(parts) > 1:
                if parts[1] != self.arch:
                    continue

            result.append(res_entry)
        
        return result

    def process_data(self, data):
        
        category = "dev-tex"
        
        self.add_category(category)

        ARCH_LENGTH = len("ARCH")

        data = data["texlive.tlpdb"]

        self.number_of_packages = len(data)
        self.written_number = 0

        for entry in data:
            realname = entry["name"]

            parts = realname.split(".")
            if len(parts) > 1:
                realname = "_".join(parts)
            
            #todo: work on common data vars processing: external deps, filtering etc.
            #at the moment just copy necessary code from elpa_db.py
            allowed_ords = set(range(ord('a'), ord('z'))) | set(range(ord('A'), ord('Z'))) | \
              set(range(ord('0'), ord('9'))) | set(list(map(ord,
                    ['+', '_', '-', ' ', '.', '(', ')', '[', ']', '{', '}', ','])))

            if "shortdesc" in entry:                
                description = entry["shortdesc"]
            else:
                description = entry["name"]
            description = "".join([x for x in description if ord(x) in allowed_ords])

            if "longdesc" in entry:
                longdescription = entry["longdesc"]
                longdescription = "".join([x for x in longdescription if ord(x) in allowed_ords])
            else:
                longdescription = description

            if "catalogue-version" in entry:
                version = entry["catalogue-version"]
                #todo better version checking and processing
                match_object = re.match("(^[0-9]+[a-z]?$)|(^[0-9][0-9\.]+[0-9][a-z]?$)", version)
                if not match_object:
                    version = entry["revision"]
            else:
                version = entry["revision"]

            if "catalogue-license" in entry:
                license = self.convert_license(entry["catalogue-license"])
            else:
                license = "unknown"

            if "catalogue-ctan" in entry:
                source_type = "zip"
                base_src_uri = "ftp://tug.ctan.org/pub/tex-archive"
                catalogue = entry["catalogue-ctan"]
                homepage = "http://www.ctan.org/tex-archive" + catalogue
                catalogue = catalogue[:-len(realname)]
            else:
                source_type = "tar.xz"
                base_src_uri = "http://mirror.ctan.org/systems/texlive/tlnet/archive/"
                catalogue = ""
                homepage = "http://www.ctan.org/tex-archive/systems/texlive/tlnet"

            dependencies = serializable_elist(separator="\n\t")

            if "depend" in entry:
                for dependency in entry["depend"]:
                    if dependency[-ARCH_LENGTH:] == "ARCH":
                        dependency = dependency[:-ARCH_LENGTH-1] + "_" + self.arch
                    dependencies.append(Dependency(category, dependency))

            ebuild_data = {"realname" : realname,
                           "description" : description,
                           "homepage" : homepage,
                           "license" : license,
                           "source_type" : source_type,
                           "base_src_uri" : base_src_uri,
                           "catalogue" : catalogue,
                           "dependencies" : dependencies,
                           "depend" : dependencies,
                           "rdepend" : dependencies,
            #eclass entry
                           'eclasses' : ['gs-ctan'],
            #metadata entries
                           'maintainer' : [{'email' : 'piatlicki@gmail.com',
                                            'name' : 'Jauhien Piatlicki'}],
                           'longdescription' : longdescription
                          }

            self.add_package(Package(category, realname, version), ebuild_data)

        logger = Logger()
        logger.info("writing database")

    def additional_write_version(self, category, package, version):
        chars = ['-','\\','|','/']
        show = chars[self.written_number % 4]
        percent = (self.written_number * 100)//self.number_of_packages
        length = 20
        progress = (percent * 20)//100
        blank = 20 - progress
        
        sys.stdout.write("\r %s [%s%s] %s%%" % (show, "#" * progress, " " * blank, percent))
        sys.stdout.flush()
        self.written_number += 1

    def additional_write_category(self, category):
        sys.stdout.write("\r %s [%s] %s%%" % ("-", "#" * 20, 100))
        sys.stdout.flush()
        print("")
