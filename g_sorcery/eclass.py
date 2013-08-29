#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    eclass.py
    ~~~~~~~~~
    
    eclass generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import glob
import os

from .exceptions import EclassError
from .fileutils import get_pkgpath

class EclassGenerator(object):
    """
    Generates eclasses from files in a given dir.
    """

    def __init__(self, eclass_dir):
        """
        __init__ in a subclass should take no parameters.
        """
        self.eclass_dir = eclass_dir

    def list(self):
        """
        List all eclasses.
        
        Returns:
            List of all eclasses with string entries.
        """
        result = []

        for directory in [self.eclass_dir, os.path.join(get_pkgpath(), 'data')]:
            if directory:
                for f_name in glob.iglob(os.path.join(directory, '*.eclass')):
                    result.append(os.path.basename(f_name)[:-7])

        return list(set(result))

    def generate(self, eclass):
        """
        Generate a given eclass.

        Args:
            eclass: String containing eclass name.

        Returns:
            Eclass source as a list of strings.
        """
        for directory in [self.eclass_dir, os.path.join(get_pkgpath(), 'data')]:
            f_name = os.path.join(directory, eclass + '.eclass')
            if os.path.isfile(f_name):
                with open(f_name, 'r') as f:
                    eclass = f.read().split('\n')
                    if eclass[-1] == '':
                        eclass = eclass[:-1]
                return eclass

        raise EclassError('No eclass ' + eclass)
