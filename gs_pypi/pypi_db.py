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
    import httplib
    urlparse
else:
    import xmlrpc.client as xmlrpclib
    import http.client as httplib
    import urllib.parse as urlparse

import sys

from g_sorcery.logger import Logger
from g_sorcery.package_db import DBGenerator

class PypiDBGenerator(DBGenerator):

    def process_uri(self, uri, data):
        url = uri["uri"]
        client = xmlrpclib.ServerProxy(url)
        logger = Logger()
        logger.info("downloading packages data")
        pkg_list = client.list_packages()

        number_of_packages = len(pkg_list)
        downloaded_number = 0

        connection = httplib.HTTPConnection(urlparse.urlparse(url).netloc)

        connection.request("GET", "/pypi/zmqpy/json")
        response = connection.getresponse()
        print(response.getheaders())
        
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

        connection.close()

        sys.stdout.write("\r %s [%s] %s%%" % ("-", "#" * length, 100))
        sys.stdout.flush()
        print("")

    def process_data(self, pkg_db, data, common_config, config):
        #print(data)
        pass
