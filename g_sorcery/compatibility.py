#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    compatibility.py
    ~~~~~~~~~~~~~~~~
    
    utilities for py2 compatibility
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import shutil, sys

py2k = sys.version_info < (3, 0)

if py2k:

    from tempfile import mkdtemp
    
    class TemporaryDirectory(object):
        def __init__(self):
            self.name = mkdtemp()

        def __del__(self):
            shutil.rmtree(self.name)
else:
    from tempfile import TemporaryDirectory

#basestring removed in py3k
#fix for it from https://github.com/oxplot/fysom/issues/1

if py2k:
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
else:
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
