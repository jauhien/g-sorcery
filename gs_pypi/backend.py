#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    backend.py
    ~~~~~~~~~~
    
    PyPI backend
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

from g_sorcery.backend import Backend
from g_sorcery.metadata import MetadataGenerator
from g_sorcery.eclass import EclassGenerator
from g_sorcery.fileutils import get_pkgpath

from .pypi_db import PypiDBGenerator
from .ebuild import PypiEbuildWithoutDigestGenerator, PypiEbuildWithDigestGenerator


class PypiEclassGenerator(EclassGenerator):
    def __init__(self):
        super(PypiEclassGenerator, self).__init__(os.path.join(get_pkgpath(__file__), 'data'))
        

instance = Backend(PypiDBGenerator,
                   PypiEbuildWithDigestGenerator, PypiEbuildWithoutDigestGenerator,
                   PypiEclassGenerator, MetadataGenerator, sync_db=True)
