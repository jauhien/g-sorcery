#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    setup.py
    ~~~~~~~~

    installation script

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :copyright: (c) 2014 by Brian Dolbec
                    (code for conditional module installation
                    is taken from the layman project)
    :license: GPL-2, see LICENSE for more details.
"""

import os

from distutils.core import setup

SELECTABLE = {'bson': 'file_bson'}

use_defaults = ' '.join(list(SELECTABLE))
USE = os.environ.get("USE", use_defaults).split()

optional_modules = []
for mod in SELECTABLE:
    if mod in USE:
        optional_modules.append('g_sorcery.%s' % SELECTABLE[mod])

setup(name          = 'g-sorcery',
      version       = '0.2',
      description   = 'framework for automated ebuild generators',
      author        = 'Jauhien Piatlicki',
      author_email  = 'jauhien@gentoo.org',
      packages      = ['g_sorcery', 'gs_db_tool'] + optional_modules,
      package_data  = {'g_sorcery': ['data/*']},
      scripts       = ['bin/g-sorcery', 'bin/gs-db-tool'],
      data_files    = [('/etc/g-sorcery/', ['g-sorcery.cfg'])],
      license       = 'GPL-2',
      )
