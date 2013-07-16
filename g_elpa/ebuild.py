#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import collections
import os

from g_sorcery.ebuild import DefaultEbuildGenerator
from g_sorcery.fileutils import get_pkgpath

Layout = collections.namedtuple("Layout",
    ["vars_before_inherit", "inherit", "vars_after_description", "vars_after_keywords"])
  

class ElpaEbuildWithDigestGenerator(DefaultEbuildGenerator):
    def __init__(self, package_db):

        vars_before_inherit = \
          ["repo_uri", "source_type", "realname", ("digest_sources", "yes")]

        inherit = ["g-elpa"]
        
        vars_after_description = \
          ["homepage", ("src_uri", "${REPO_URI}${REALNAME}-${PV}.${SUFFIX}")]

        vars_after_keywords = \
          ["depend", "rdepend"]

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(ElpaEbuildWithDigestGenerator, self).__init__(package_db, layout)

class ElpaEbuildWithoutDigestGenerator(DefaultEbuildGenerator):
    def __init__(self, package_db):

        vars_before_inherit = \
          ["repo_uri", "source_type", "realname"]

        inherit = ["g-elpa"]
        
        vars_after_description = \
          ["homepage"]

        vars_after_keywords = \
          ["depend", "rdepend"]

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(ElpaEbuildWithoutDigestGenerator, self).__init__(package_db, layout)
