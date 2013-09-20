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

from g_sorcery.ebuild import DefaultEbuildGenerator

Layout = collections.namedtuple("Layout",
    ["vars_before_inherit", "inherit", "vars_after_description", "vars_after_keywords"])
  

class CtanEbuildWithoutDigestGenerator(DefaultEbuildGenerator):
    """
    Implementation of ebuild generator without sources digesting.
    """
    def __init__(self, package_db):

        vars_before_inherit = \
          ["base_src_uri", "catalogue", "source_type", "realname"]

        inherit = ["gs-ctan"]
        
        vars_after_description = \
          ["homepage", {"name" : "src_uri", "value" : ""}, "license"]

        vars_after_keywords = \
          ["depend", "rdepend"]

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(CtanEbuildWithoutDigestGenerator, self).__init__(package_db, layout)

class CtanEbuildWithDigestGenerator(DefaultEbuildGenerator):
    """
    Implementation of ebuild generator with sources digesting.
    """
    def __init__(self, package_db):

        vars_before_inherit = \
          ["base_src_uri", "catalogue", "source_type", "realname", {"name" : "digest_sources", "value" : "yes"}]

        inherit = ["gs-ctan"]
        
        vars_after_description = \
          ["homepage", {"name" : "src_uri", "value" : "${BASE_SRC_URI}${CATALOGUE}${REALNAME}.${SOURCE_TYPE} -> ${P}.${SOURCE_TYPE}"}, "license"]

        vars_after_keywords = \
          ["depend", "rdepend"]

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(CtanEbuildWithDigestGenerator, self).__init__(package_db, layout)
