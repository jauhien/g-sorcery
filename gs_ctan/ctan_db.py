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

from g_sorcery.package_db import PackageDB
from g_sorcery.exceptions import SyncError

class CtanDB(PackageDB):
    def __init__(self, directory, repo_uri="", db_uri=""):
        super(CtanDB, self).__init__(directory, repo_uri, db_uri)

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
            result.append(res_entry)
        
        return result

    def process_data(self, data):

        self.add_category('dev-tex')

        for entry in data["texlive.tlpdb"]:

            realname = entry["name"]
            
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
            else:
                version = entry["revision"]

            #todo: convert to gentoo licenses
            if "catalogue-license" in entry:
                license = entry["catalogue-license"]
            else:
                license = "unknown"

            if "catalogue-ctan" in entry:
                source_type = "zip"
                base_src_uri = "http://www.ctan.org/tex-archive"
                catalogue = entry["catalogue-ctan"]
            else:
                source_type = "tar.xz"
                base_src_uri = "http://mirror.ctan.org/systems/texlive/tlnet/archive"
                catalogue = ""

            print("dev-tex/" + realname + "-" + version)
            print("    license: " + license)
            print("    " + description)
            print
            print("    " + longdescription)
            print
