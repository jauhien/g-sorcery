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

from .logger import Logger

class PackageManager(object):
    """
    Base class for package manager abstraction
    """

    executable = ""
    logger = Logger()
    
    def __init__(self):
        pass

    def run_command(self, *args):
        command = self.executable + " " + " ".join(args)
        self.logger.info("running a package mangler: " + command)
        return os.system(self.executable + " " + " ".join(args))

    def install(self, pkgname, *args):
        """
        It supports intallation by package name currently,
        will add support of atoms with version specified later
        """
        raise NotImplementedError


class Portage(PackageManager):
    """
    Portage package manager abstraction.
    """
    def __init__(self):
        super(Portage, self).__init__()
        self.executable = "/usr/bin/emerge"

    def install(self, pkgname, *args):
        return self.run_command("-va", pkgname, *args)

#list of supported package managers.
package_managers = {'portage' : Portage}
