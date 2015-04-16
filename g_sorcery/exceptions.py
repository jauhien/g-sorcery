#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    exceptions.py
    ~~~~~~~~~~~~~

    Exceptions hierarchy

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

class GSorceryError(Exception):
    pass

class DBError(GSorceryError):
    pass

class DBLayoutError(GSorceryError):
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

class DescriptionError(GSorceryError):
    pass

class DependencyError(GSorceryError):
    pass

class EclassError(GSorceryError):
    pass

class DigestError(GSorceryError):
    pass

class DownloadingError(GSorceryError):
    pass

class SerializationError(GSorceryError):
    pass
