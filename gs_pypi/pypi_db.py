#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    pypi_db.py
    ~~~~~~~~~~
    
    PyPI package database
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import datetime
import re
import time

import bs4

from g_sorcery.exceptions import DownloadingError
from g_sorcery.g_collections import Package, serializable_elist
from g_sorcery.package_db import DBGenerator

class PypiDBGenerator(DBGenerator):
    """
    Implementation of database generator for PYPI backend.
    """
    def get_download_uries(self, common_config, config):
        """
        Get URI of packages index.
        """
        self.repo_uri = config["repo_uri"]
        return [{"uri": self.repo_uri + "pypi?%3Aaction=index", "output": "packages"}]

    def parse_data(self, data_f):
        """
        Download and parse packages index. Then download and parse pages for all packages.
        """
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
            entry.decompose()

        packages.decompose()
        soup.decompose()

        pkg_uries = self.decode_download_uries(pkg_uries)
        for uri in pkg_uries:
            attempts = 0
            while True:
                try:
                    attempts += 1
                    self.process_uri(uri, data)
                except DownloadingError as error:
                    print(str(error))
                    time.sleep(5)
                    if attempts < 100:
                        continue
                break

        return data

    def parse_package_page(self, data_f):
        """
        Parse package page.
        """
        soup = bs4.BeautifulSoup(data_f.read())
        data = {}
        data["files"] = []
        data["info"] = {}
        try:
            for table in soup("table", class_ = "list")[-1:]:
                if not "File" in table("th")[0].string:
                    continue

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
                    entry.decompose()
                table.decompose()

            uls = soup("ul", class_ = "nodot")
            if uls:
                if "Downloads (All Versions):" in uls[0]("strong")[0].string:
                    ul = uls[1]
                else:
                    ul = uls[0]

                for entry in ul.contents:
                    if not hasattr(entry, "name") or entry.name != "li":
                        continue
                    entry_name = entry("strong")[0].string
                    if not entry_name:
                        continue

                    if entry_name == "Categories":
                        data["info"][entry_name] = {}
                        for cat_entry in entry("a"):
                            cat_data = cat_entry.string.split(" :: ")
                            if not cat_data[0] in data["info"][entry_name]:
                                data["info"][entry_name][cat_data[0]] = cat_data[1:]
                            else:
                                data["info"][entry_name][cat_data[0]].extend(cat_data[1:])
                        continue

                    if entry("span"):
                        data["info"][entry_name] = entry("span")[0].string
                        continue

                    if entry("a"):
                        data["info"][entry_name] = entry("a")[0]["href"]
                        continue
                    entry.decompose()
                ul.decompose()

        except Exception as error:
            print("There was an error during parsing: " + str(error))
            print("Ignoring this package.")
            data = {}
            data["files"] = []
            data["info"] = {}

        soup.decompose()
        return data

    def process_data(self, pkg_db, data, common_config, config):
        """
        Process parsed package data.
        """
        category = "dev-python"
        pkg_db.add_category(category)

        #todo: write filter functions
        allowed_ords_pkg = set(range(ord('a'), ord('z') + 1)) | set(range(ord('A'), ord('Z') + 1)) | \
            set(range(ord('0'), ord('9') + 1)) | set(list(map(ord,
                ['+', '_', '-'])))

        allowed_ords_desc = set(range(ord('a'), ord('z') + 1)) | set(range(ord('A'), ord('Z') + 1)) | \
              set(range(ord('0'), ord('9') + 1)) | set(list(map(ord,
                    ['+', '_', '-', ' ', '.', '(', ')', '[', ']', '{', '}', ','])))

        now = datetime.datetime.now()
        pseudoversion = "%04d%02d%02d" % (now.year, now.month, now.day)

        for (package, version), description in data["packages"]["index"].items():

            pkg = package + "-" + version
            if not pkg in data["packages"]:
                continue

            pkg_data = data["packages"][pkg]
            
            if not pkg_data["files"] and not pkg_data["info"]:
                continue

            files_src_uri = ""
            md5 = ""
            if pkg_data["files"]:
                for file_entry in pkg_data["files"]:
                    if file_entry["type"] == "\n    Source\n  ":
                        files_src_uri = file_entry["url"]
                        md5 = file_entry["md5"]
                        break

            download_url = ""
            info = pkg_data["info"]
            if info:
                if "Download URL:" in info:
                    download_url = pkg_data["info"]["Download URL:"]

            if download_url:
                source_uri = download_url #todo: find how to define src_uri
            else:
                source_uri = files_src_uri

            if not source_uri:
                continue

            homepage = ""
            pkg_license = ""
            py_versions = []
            if info:
                if "Home Page:" in info:
                    homepage = info["Home Page:"]
                categories = {}
                if "Categories" in info:
                    categories = info["Categories"]

                    if 'Programming Language' in  categories:
                        for entry in categories['Programming Language']:
                            if entry == '2':
                                py_versions.extend(['2_6', '2_7'])
                            elif entry == '3':
                                py_versions.extend(['3_2', '3_3'])
                            elif entry == '2.6':
                                py_versions.extend(['2_6'])
                            elif entry == '2.7':
                                py_versions.extend(['2_7'])
                            elif entry == '3.2':
                                py_versions.extend(['3_2'])
                            elif entry == '3.3':
                                py_versions.extend(['3_3'])

                    if "License" in categories:
                        pkg_license = categories["License"][-1]
            pkg_license = self.convert([common_config, config], "licenses", pkg_license)

            if not py_versions:
                py_versions = ['2_6', '2_7', '3_2', '3_3']
            if len(py_versions) == 1:
                python_compat = 'python' + py_versions[0]
            else:
                python_compat = '( python{' + py_versions[0]
                for ver in py_versions[1:]:
                    python_compat += ',' + ver
                python_compat += '} )'

            filtered_package = "".join([x for x in package if ord(x) in allowed_ords_pkg])
            description = "".join([x for x in description if ord(x) in allowed_ords_desc])
            filtered_version = version
            match_object = re.match("(^[0-9]+[a-z]?$)|(^[0-9][0-9\.]+[0-9][a-z]?$)",
                                    filtered_version)
            if not match_object:
                filtered_version = pseudoversion

            dependencies = serializable_elist(separator="\n\t")
            eclasses = ['g-sorcery', 'gs-pypi']
            maintainer = [{'email' : 'piatlicki@gmail.com',
                           'name' : 'Jauhien Piatlicki'}]

            ebuild_data = {}
            ebuild_data["realname"] = package
            ebuild_data["realversion"] = version

            ebuild_data["description"] = description
            ebuild_data["longdescription"] = description
            ebuild_data["dependencies"] = dependencies
            ebuild_data["eclasses"] = eclasses
            ebuild_data["maintainer"] = maintainer

            ebuild_data["homepage"] = homepage
            ebuild_data["license"] = pkg_license
            ebuild_data["source_uri"] = source_uri
            ebuild_data["md5"] = md5
            ebuild_data["python_compat"] = python_compat

            ebuild_data["info"] = info

            pkg_db.add_package(Package(category, filtered_package, filtered_version), ebuild_data)
