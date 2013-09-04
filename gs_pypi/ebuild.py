#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import collections
import os

from g_sorcery.ebuild import DefaultEbuildGenerator

Layout = collections.namedtuple("Layout",
    ["vars_before_inherit", "inherit", "vars_after_description", "vars_after_keywords"])
  

class PypiEbuildWithoutDigestGenerator(DefaultEbuildGenerator):
    def __init__(self, package_db):

        vars_before_inherit = \
          [("repo_uri", 'http://pypi.python.org/packages/source/${PN:0:1}/${PN}/'),
           ("sourcefile", '${P}.tar.gz'), "python_compat"]

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          ["homepage"]

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithoutDigestGenerator, self).__init__(package_db, layout)

class PypiEbuildWithDigestGenerator(DefaultEbuildGenerator):
    def __init__(self, package_db):

        vars_before_inherit = \
          [("digest_sources", "yes"), "python_compat"]

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          ["homepage",
           ("src_uri", 'http://pypi.python.org/packages/source/${PN:0:1}/${PN}/${P}.tar.gz')]

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithDigestGenerator, self).__init__(package_db, layout)
