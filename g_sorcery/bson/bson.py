#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    bson.py
    ~~~~~~~

    bson file format support

    :copyright: (c) 2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import bson

from g_sorcery.exceptions import FileJSONError
from g_sorcery.fileutils import FileJSONData
from g_sorcery.serialization import from_raw_serializable, to_raw_serializable

class FileBSON(FileJSONData):
    """
    Class for BSON files. Supports custom JSON serialization
    provided by g_sorcery.serialization.
    """
    def read_content(self):
        """
        Read BSON file.
        """
        content = {}
        bcnt = None
        with open(self.path, 'rb') as f:
            bcnt = f.read()
        if not bcnt:
            raise FileJSONError('failed to read: ', self.path)
        rawcnt = bson.BSON.decode(bcnt)
        content = from_raw_serializable(rawcnt)
        return content


    def write_content(self, content):
        """
        Write BSON file.
        """
        rawcnt = to_raw_serializable(content)
        bcnt = bson.BSON.encode(rawcnt)
        with open(self.path, 'wb') as f:
            f.write(bcnt)
