#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    backend.py
    ~~~~~~~~~~
    
    CTAN backend
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

from g_sorcery.backend import Backend
from g_sorcery.metadata import MetadataGenerator
from g_sorcery.eclass import EclassGenerator
from g_sorcery.fileutils import get_pkgpath

from .ctan_db import CtanDBGenerator
from .ebuild import CtanEbuildWithoutDigestGenerator, CtanEbuildWithDigestGenerator


class CtanEclassGenerator(EclassGenerator):
    def __init__(self):
        super(CtanEclassGenerator, self).__init__(os.path.join(get_pkgpath(__file__), 'data'))
        

instance = Backend(CtanDBGenerator,
                   CtanEbuildWithDigestGenerator, CtanEbuildWithoutDigestGenerator,
                   CtanEclassGenerator, MetadataGenerator)
