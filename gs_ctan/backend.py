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
from g_sorcery.ebuild import EbuildGenerator
from g_sorcery.eclass import EclassGenerator
from g_sorcery.fileutils import get_pkgpath

from .ctan_db import CtanDB
from .ebuild import CtanEbuildWithoutDigestGenerator


class CtanEclassGenerator(EclassGenerator):
    def __init__(self):
        super(CtanEclassGenerator, self).__init__(os.path.join(get_pkgpath(__file__), 'data'))
        

instance = Backend(CtanDB,
                   EbuildGenerator, CtanEbuildWithoutDigestGenerator,
                   CtanEclassGenerator, MetadataGenerator, sync_db=False)
