#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    pypi_db.py
    ~~~~~~~~~~
    
    PyPI package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import bs4

from g_sorcery.g_collections import Package
from g_sorcery.package_db import DBGenerator

class PypiDBGenerator(DBGenerator):

    def get_download_uries(self, common_config, config):
        self.repo_uri = config["repo_uri"]
        return [{"uri": self.repo_uri + "?%3Aaction=index", "output": "packages"}]

    def parse_data(self, data_f):
        soup = bs4.BeautifulSoup(data_f.read())
        packages = soup.table
        data = {}
        data["index"] = {}

        pkg_uries = []
        
        for entry in packages.find_all("tr")[1:-1]:
            package, description = entry.find_all("td")
            
            if description.contents:
                description = description.contents[0]
            else:
                description = ""
            package, version = package.a["href"].split("/")[2:]            
            data["index"][(package, version)] = description
            pkg_uries.append({"uri": self.repo_uri + "pypi/" + package + "/" + version,
                              "parser": self.parse_package_page,
                              "output": package + "-" + version})
        pkg_uries = self.decode_download_uries(pkg_uries)
        for uri in pkg_uries:
            self.process_uri(uri, data)

        return data

    def parse_package_page(self, data_f):
        soup = bs4.BeautifulSoup(data_f.read())
        data = {}
        data["files"] = []
        data["info"] = {}
        for table in soup("table")[-1:]:
            for entry in table("tr")[1:-1]:
                fields = entry("td")
                
                FILE = 0
                URL = 0
                MD5 = 1
                
                TYPE = 1
                PYVERSION = 2
                UPLOADED = 3
                SIZE = 4
                
                file_inf = fields[FILE]("a")[0]["href"].split("#")
                file_url = file_inf[URL]
                file_md5 = file_inf[MD5][4:]

                file_type = fields[TYPE].string
                file_pyversion = fields[PYVERSION].string
                file_uploaded = fields[UPLOADED].string
                file_size = fields[SIZE].string

                data["files"].append({"url": file_url,
                                      "md5": file_md5,
                                      "type": file_type,
                                      "pyversion": file_pyversion,
                                      "uploaded": file_uploaded,
                                      "size": file_size})
                
        for ul in soup("ul", class_ = "nodot")[:1]:
            for entry in ul.contents:
                if not hasattr(entry, "name") or entry.name != "li":
                    continue
                entry_name = entry("strong")[0].string
                if not entry_name:
                    continue

                if entry_name == "Categories":
                    data["info"][entry_name] = []
                    for cat_entry in entry("a"):
                        data["info"][entry_name].append(cat_entry.string.split(" :: "))
                    continue

                if entry("span"):
                    data["info"][entry_name] = entry("span")[0].string
                    continue

                if entry("a"):
                    data["info"][entry_name] = entry("a")[0]["href"]
                    continue

        return data

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
