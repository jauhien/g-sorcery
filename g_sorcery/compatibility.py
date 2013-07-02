#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    compatibility.py
    ~~~~~~~~~~~~~~~~
    
    utilities for py2 compatibility
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import sys

py2k = sys.version_info < (3, 0)

if py2k:
    class TemporaryDirectory():
        def __init__(self):
            pass

        def __del__(self):
            pass
else:
    from tempfile import TemporaryDirectory
