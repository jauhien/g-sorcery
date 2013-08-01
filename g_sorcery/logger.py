#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    logger.py
    ~~~~~~~~~
    
    logging classes
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import portage


class Logger(object):
    """
    A simple logger object. Uses portage out facilities.
    """
    def __init__(self):
        self.out = portage.output.EOutput()

    def error(self, message):
        self.out.eerror(message)

    def info(self, message):
        self.out.einfo(message)

    def warn(self, message):
        self.out.ewarn(message)
