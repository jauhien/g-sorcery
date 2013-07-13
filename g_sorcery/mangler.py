#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    mangler.py
    ~~~~~~~~~~
    
    package manager interaction
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os


class PackageManager(object):
    """
    Base class for package manager abstraction
    """

    executable = ""
    
    def __init__(self):
        pass

    def run_command(self, *args):
        return os.system(self.executable + " " + " ".join(args))

    def install(self, pkgname, *args):
        """
        It supports intallation by package name currently,
        will add support of atoms with version specified later
        """
        raise NotImplementedError


class Portage(PackageManager):
    def __init__(self):
        self.executable = "/usr/bin/emerge"

    def install(self, pkgname, *args):
        return self.run_command("-va", pkgname, *args)


package_managers = {'portage' : Portage}
