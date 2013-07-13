#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    g_sorcery.py
    ~~~~~~~~~~~~
    
    the main module
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import configparser
import importlib
import os
import sys

from .fileutils import FileJSON

from .exceptions import FileJSONError

def main():
    if len(sys.argv) < 2:
        print("No backend specified")
        return 0
    name = sys.argv[1]
    cfg = name + '.json'
    cfg_path = None
    for path in '.', '~', '/etc/g-sorcery':
        current = os.path.join(path, cfg)
        if (os.path.isfile(current)):
            cfg_path = path
            break
    if not cfg_path:
        sys.stderr.write('g-sorcery error: no config file for ' + name + ' backend\n')
        return -1
    cfg_f = FileJSON(cfg_path, cfg, ['package'])
    try:
        config = cfg_f.read()
    except FileJSONError as e:
        sys.stderr.write('g-sorcery error in config file for ' + name + ': ' + str(e) + '\n')
        return -1
    backend = get_backend(config['package'])

    cfg_path = None
    for path in '.', '~', '/etc/g-sorcery':
        current = os.path.join(path, "g-sorcery.cfg")
        if (os.path.isfile(current)):
            cfg_path = path
            break
    if not cfg_path:
        sys.stderr.write('g-sorcery error: no global config file\n')
        return -1
    
    global_config = configparser.ConfigParser()
    global_config.read(cfg_path)
    
    return backend.instance(sys.argv[2:], config, global_config)


def get_backend(package):
    try:
        module = importlib.import_module(package + '.backend')
    except ImportError:
        return None
    
    return module


if __name__ == "__main__":
    sys.exit(main())
