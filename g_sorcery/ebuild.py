#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import copy
import re
import string

from .exceptions import DescriptionError

def substitute_list(text, values):
    """
    Performs the template substitution. Variables are
    substituted by lists.

    Variable format.
    ~~~~~~~~~~~~~~~~

    #[n ]#name#
    'n': Separate list entries with '\n'.
    ' ': Separate list entries with ' '.
    name: Key in values dict.

    Args:
        text: List with template strings.
        values: Dictionary with values.
    """
    result = copy.deepcopy(text)
    regex = re.compile('#[n ]#\w+#')
    for idx, line in enumerate(result):
        match = regex.search(line)
        if not match:
                continue
        group = match.group()
        new_line = (group[1] == 'n')
        key = group[3:-1]
        if not key in values:
            error = "missing key: " + key
            raise DescriptionError(error)
        lst = values[key]
        if new_line:
            sep = '\n'
        else:
            sep = ' '
        repl = sep.join(lst)
        result[idx] = regex.sub(repl, line)
    return result


class EbuildGenerator(object):
    """
    Ebuild generator.
    """
    def __init__(self, package_db):
        """
        Args:
            package_db: Package database.
        """
        self.package_db = package_db

    def generate(self, package):
        """
        Generate an ebuild for a package.

        Args:
            package: package_db.Package instance.

        Returns:
            Ebuild source as a list of strings.
        """
        #a possible exception should be catched in the caller
        description = self.package_db.get_package_description(package)
        ebuild = self.get_template(package, description)
        ebuild = self.process(ebuild, description)
        ebuild = self.postprocess(ebuild, description)
        return ebuild

    def process(self, ebuild, description):
        """
        Fill ebuild tamplate with data.

        Args:
            ebuild: Ebuild template.
            description: Dictionary with ebuild description.

        Returns:
            Ebuild source as a list of strings.
        """
        result = []
        for line in ebuild:
            tmpl = string.Template(line)
            result.append(tmpl.substitute(description))
        return result
        
    def get_template(self, package, description):
        """
        Generate ebuild tamplate. Should be overriden.

        Args:
            package: package_db.Package instance.
            description: Dictionary with ebuild description.

        Returns:
            Ebuild template.
        """
        ebuild = []
        return ebuild
        
    def postprocess(self, ebuild, description):
        """
        Hook to be overriden.

        Args:
            ebuild: Ebuild source as a list of strings.
            description: Dictionary with ebuild description.

        Returns:
            Ebuild source as a list of strings.
        """
        return ebuild

class EbuildGeneratorFromFile(EbuildGenerator):
    """
    Ebuild generators that takes templates from files.
    """
    def __init__(self, package_db, filename=""):
        super(EbuildGeneratorFromFile, self).__init__(package_db)
        self.filename = filename

    def get_template(self, package, description):
        """
        Generate ebuild tamplate.

        Args:
            package: package_db.Package instance.
            description: Dictionary with ebuild description.

        Returns:
            Ebuild template.
        """
        name = self.get_template_file(package, description)
        with open(name, 'r') as f:
            ebuild = f.read().split('\n')
            if ebuild[-1] == '':
                ebuild = ebuild[:-1]
        return ebuild

    def get_template_file(self, package, description):
        """
        Get template filename for a package. Should be overriden.
        
        Args:
            package: package_db.Package instance.
            description: Dictionary with ebuild description.

        Returns:
            Template filename.
        """
        return self.filename
