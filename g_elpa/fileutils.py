#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    fileutils.py
    ~~~~~~~~~~~~
    
    file utilities
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

def get_pkgpath():
    """
    Get package path.

    Returns:
        Package path.
    """
    root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))
