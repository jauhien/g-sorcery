#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    backend.py
    ~~~~~~~~~~
    
    ELPA backend
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

from g_sorcery.backend import Backend
from g_sorcery.metadata import MetadataGenerator

from .elpa_db import ElpaDB
from .ebuild import ElpaEbuildWithDigestGenerator, ElpaEbuildWithoutDigestGenerator

instance = Backend(ElpaDB, ElpaEbuildWithDigestGenerator,
                   ElpaEbuildWithoutDigestGenerator, MetadataGenerator, sync_db=False)
