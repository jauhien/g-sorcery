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

from g_sorcery.package_db import DBGenerator

class PypiDBGenerator(DBGenerator):

    def get_download_uries(self, common_config, config):
        return [config["repo_uri"] + "?%3Aaction=index"]

    def parse_data(self, data_f):
        soup = bs4.BeautifulSoup(data_f.read())
        return soup.table
            
                
    def process_data(self, pkg_db, data, common_config, config):
        data = data["pypi?:action=index"]
        for entry in data.find_all("tr")[1:-1]:
            package, description = entry.find_all("td")
            
            if description.contents:
                description = description.contents[0]
            else:
                description = ""
            package, version = package.a["href"].split("/")[2:]

            print(package, version, description)
