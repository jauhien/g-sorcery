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
        if self.eclass_dir:
            for f_name in glob.iglob(os.path.join(self.eclass_dir, '*.eclass')):
                result.append(os.path.basename(f_name)[:-7])
        return result

    def generate(self, eclass):
        """
        Generate a given eclass.

        Args:
            eclass: String containing eclass name.

        Returns:
            Eclass source as a list of strings.
        """
        if not self.eclass_dir:
            EclassError('No eclass dir')
        f_name = os.path.join(self.eclass_dir, eclass + '.eclass')
        if not os.path.isfile(f_name):
            EclassError('No eclass ' + eclass)
        with open(f_name, 'r') as f:
            eclass = f.read().split('\n')
            if eclass[-1] == '':
                eclass = eclass[:-1]
        return eclass
