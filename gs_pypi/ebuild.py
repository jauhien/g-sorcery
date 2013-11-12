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
    """
    Implementation of ebuild generator without sources digesting.
    """
    def __init__(self, package_db):

        vars_before_inherit = \
          ["realname", "realversion",
           {"name" : "repo_uri", "value" : 'http://pypi.python.org/packages/source/${REALNAME:0:1}/${REALNAME}/'},
           {"name" : "sourcefile", "value" : '${REALNAME}-${REALVERSION}.tar.gz'}, {"name" : "python_compat", "raw" : True}]

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          ["homepage", "license"]

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithoutDigestGenerator, self).__init__(package_db, layout)

class PypiEbuildWithDigestGenerator(DefaultEbuildGenerator):
    """
    Implementation of ebuild generator with sources digesting.
    """
    def __init__(self, package_db):

        vars_before_inherit = \
          ["realname", "realversion",
           {"name" : "digest_sources", "value" : "yes"}, {"name" : "python_compat", "raw" : True}]

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          ["homepage", "license",
           {"name" : "src_uri", "value" : 'http://pypi.python.org/packages/source/${REALNAME:0:1}/${REALNAME}/${REALNAME}-${REALVERSION}.tar.gz'}]

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithDigestGenerator, self).__init__(package_db, layout)
