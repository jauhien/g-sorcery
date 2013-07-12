#!/usr/bin/env python

from distutils.core import setup

setup(name          = 'g-sorcery',
      version       = '0.1_alpha',
      description   = 'g-sorcery framework for automated ebuild generators',
      author        = 'Jauhien Piatlicki',
      author_email  = 'piatlicki@gmail.com',
      packages      = ['g_sorcery', 'g_elpa'],
      scripts       = ['bin/g-sorcery', 'bin/g-elpa'],
      data_files    = [('/etc/g-sorcery/', ['g-elpa.json']),],
      license       = 'GPL',
      )
