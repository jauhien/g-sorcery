#!/usr/bin/env python

from distutils.core import setup

setup(name          = 'g-sorcery',
      version       = '0.1',
      description   = 'framework for automated ebuild generators',
      author        = 'Jauhien Piatlicki',
      author_email  = 'jauhien@gentoo.org',
      packages      = ['g_sorcery', 'gs_db_tool'],
      package_data  = {'g_sorcery': ['data/*']},
      scripts       = ['bin/g-sorcery', 'bin/gs-db-tool'],
      data_files    = [('/etc/g-sorcery/', ['g-sorcery.cfg'])],
      license       = 'GPL',
      )
