#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import string

class EbuildGenerator:
    def __init__(self, db):
        self.db = db

    def generate(self, package):
        #a possible exception should be catched in the caller
        description = self.db.get_package_description(package)
        ebuild = self.get_template(package, description)
        ebuild = self.process(ebuild, description)
        ebuild = self.postprocess(ebuild, description)
        return ebuild

    def process(self, ebuild, description):
        result = []
        for line in ebuild:
            tmpl = string.Template(line)
            result.append(tmpl.substitute(description))
        return result
        
    def get_template(self, package, description):
        ebuild = []
        return ebuild
        
    def postprocess(self, ebuild, description):
        return ebuild
