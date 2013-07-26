#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    pypi_db.py
    ~~~~~~~~~~
    
    PyPI database generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import sys

from g_sorcery.fileutils import FileJSON
from g_sorcery.logger import Logger

from .pypi_db import PypiDBGenerator

def main():

    if len(sys.argv) < 2:
        print("Usage: ")
        print("gs-pypi-generate-db db_name")
        return -1
    
    logger = Logger()
    cfg_path = None
    for path in '.', '~', '/etc/g-sorcery':
        current = os.path.join(path, "gs-pypi.json")
        if (os.path.isfile(current)):
            cfg_path = path
            break
    if not cfg_path:
        logger.error('no config file for gs-pypi backend\n')
        return -1
    cfg_f = FileJSON(cfg_path, "gs-pypi.json", ['package'])
    try:
        config = cfg_f.read()
    except FileJSONError as e:
        logger.error('error loading config file for gs-pypi: ' + str(e) + '\n')
        return -1

    generator = PypiDBGenerator()
    db_name = sys.argv[1]
    pkg_db = generator(db_name, "pypi", config=config["repositories"]["pypi"])
    os.system('tar cvzf ' +  db_name + '.tar.gz ' + db_name)

if __name__ == "__main__":
    sys.exit(main())
