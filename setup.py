#!/usr/bin/env python

from distutils.core import setup

setup(name          = 'g-sorcery',
      version       = '0.1_alpha',
      description   = 'g-sorcery framework for automated ebuild generators',
      author        = 'Jauhien Piatlicki',
      author_email  = 'jauhien@gentoo.org',
      packages      = ['g_sorcery', 'gs_db_tool', 'gs_pypi'],
      package_data  = {'g_sorcery': ['data/*'],
                       'gs_pypi': ['data/*']},
      scripts       = ['bin/g-sorcery', 'bin/gs-db-tool',
                       'bin/gs-pypi-generate-db', 'bin/gs-pypi'],
      data_files    = [('/etc/g-sorcery/', ['gs-pypi.json']),
                       ('/etc/g-sorcery/', ['g-sorcery.cfg']),
                       ('/etc/layman/overlays/', ['gs-pypi-overlays.xml'])],
      license       = 'GPL',
      )
