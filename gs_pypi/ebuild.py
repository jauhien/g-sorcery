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
          [{"name" : "repo_uri", "value" : 'http://pypi.python.org/packages/source/${PN:0:1}/${PN}/'},
           {"name" : "sourcefile", "value" : '${P}.tar.gz'}, {"name" : "python_compat", "raw" : True}]

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
          [{"name" : "digest_sources", "value" : "yes"}, {"name" : "python_compat", "raw" : True}]

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          ["homepage",
           {"name" : "src_uri", "value" : 'http://pypi.python.org/packages/source/${PN:0:1}/${PN}/${P}.tar.gz'}]

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithDigestGenerator, self).__init__(package_db, layout)
