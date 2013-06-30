#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    exceptions.py
    ~~~~~~~~~~~~~
    
    Exceptions hierarchy
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

class GSorceryError(Exception):
    pass

class DBError(GSorceryError):
    pass

class InvalidKeyError(DBError):
    pass

class SyncError(DBError):
    pass

class IntegrityError(DBError):
    pass

class DBStructureError(DBError):
    pass

class FileJSONError(GSorceryError):
    pass

class XMLGeneratorError(GSorceryError):
    pass
