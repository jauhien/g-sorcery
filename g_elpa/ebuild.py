#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

from g_sorcery.ebuild import EbuildGeneratorFromFile
from g_sorcery.fileutils import get_pkgpath

class ElpaEbuildWithDigestGenerator(EbuildGeneratorFromFile):
    def __init__(self, package_db):
        name = os.path.join(get_pkgpath(__file__), 'data/ebuild_with_digest.tmpl')
        super(ElpaEbuildWithDigestGenerator, self).__init__(package_db, filename = name)

class ElpaEbuildWithoutDigestGenerator(EbuildGeneratorFromFile):
    def __init__(self, package_db):
        name = os.path.join(get_pkgpath(__file__), 'data/ebuild_without_digest.tmpl')
        super(ElpaEbuildWithoutDigestGenerator, self).__init__(package_db, filename = name)
