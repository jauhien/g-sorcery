#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    g_sorcery.py
    ~~~~~~~~~~~~
    
    the main module
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os, sys

from .fileutils import FileJSON

from .exceptions import FileJSONError

def main():
    name = os.path.basename(sys.argv[0])
    if name == 'g-sorcery':
        print(name)
        return 0
    else:
        cfg = name + '.json'
        cfg_path = None
        for path in '.', '/etc/g-sorcery', '~':
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
        pass

if __name__ == "__main__":
    sys.exit(main())
