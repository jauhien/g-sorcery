#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    g_sorcery.py
    ~~~~~~~~~~~~

    the main module

    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""


import importlib
import os
import sys

from .compatibility import configparser
from .fileutils import FileJSON
from .exceptions import FileJSONError
from .logger import Logger

def main():
    logger = Logger()
    if len(sys.argv) < 2:
        logger.error("no backend specified")
        return -1
    name = sys.argv[1]
    cfg = name + '.json'
    cfg_path = None
    check_configs = ['.', '~', os.path.join('etc', 'g-sorcery')]
    for path in os.environ['PATH'].split(os.pathsep):
        check_configs.append(os.path.join(os.path.dirname(path), 'etc', 'g-sorcery'))
    for path in check_configs:
        current = os.path.join(path, cfg)
        if (os.path.isfile(current)):
            cfg_path = path
            break
    if not cfg_path:
        logger.error('no config file for ' + name + ' backend\n')
        return -1
    cfg_f = FileJSON(cfg_path, cfg, ['package'])
    try:
        config = cfg_f.read()
    except FileJSONError as e:
        logger.error('error loading config file for ' \
                     + name + ': ' + str(e) + '\n')
        return -1
    backend = get_backend(config['package'])

    if not backend:
        logger.error("backend initialization failed, exiting")
        return -1

    config_file = None
    for path in check_configs:
        config_file = os.path.join(path, "g-sorcery.cfg")
        if (os.path.isfile(config_file)):
            break
        else:
            config_file = None

    if not config_file:
        logger.error('no global config file\n')
        return -1

    global_config = configparser.ConfigParser()
    global_config.read(config_file)

    return backend.instance(sys.argv[2:], config, global_config)


def get_backend(package):
    """
    Load backend by package name.
    """
    logger = Logger()
    try:
        module = importlib.import_module(package + '.backend')
    except ImportError as error:
        logger.error("error importing backend: " + str(error))
        return None

    return module


if __name__ == "__main__":
    sys.exit(main())
