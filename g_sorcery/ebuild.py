#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

from .exceptions import DependencyError

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

    def generate(self, package, ebuild_data=None):
        """
        Generate an ebuild for a package.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild source as a list of strings.
        """
        #a possible exception should be catched in the caller
        if not ebuild_data:
            ebuild_data = self.package_db.get_package_description(package)
        ebuild = self.get_template(package, ebuild_data)
        ebuild = self.process(ebuild, ebuild_data)
        ebuild = self.postprocess(ebuild, ebuild_data)
        return ebuild

    def process(self, ebuild, ebuild_data):
        """
        Fill ebuild tamplate with data.

        Args:
            ebuild: Ebuild template.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild source as a list of strings.
        """
        result = []
        for line in ebuild:
            error = ""
            try:
                line = line % ebuild_data
            except ValueError as e:
                error = str(e)
            if error:
                error = "substitution failed in line '" + line + "': " + error
                raise DependencyError(error)
            result.append(line)
            
        return result
        
    def get_template(self, package, ebuild_data):
        """
        Generate ebuild tamplate. Should be overriden.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild template.
        """
        ebuild = []
        return ebuild
        
    def postprocess(self, ebuild, ebuild_data):
        """
        Hook to be overriden.

        Args:
            ebuild: Ebuild source as a list of strings.
            ebuild_data: Dictionary with ebuild data.

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

    def get_template(self, package, ebuild_data):
        """
        Generate ebuild tamplate.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild template.
        """
        name = self.get_template_file(package, ebuild_data)
        with open(name, 'r') as f:
            ebuild = f.read().split('\n')
            if ebuild[-1] == '':
                ebuild = ebuild[:-1]
        return ebuild

    def get_template_file(self, package, ebuild_data):
        """
        Get template filename for a package. Should be overriden.
        
        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Template filename.
        """
        return self.filename
