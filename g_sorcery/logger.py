#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    logger.py
    ~~~~~~~~~
    
    logging classes
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import sys

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


class ProgressBar(object):
    """
    A progress bar for CLI
    """

    __slots__ = ('length', 'total', 'processed', 'chars')
    
    def __init__(self, length, total, processed = 0):
        self.length = length
        self.total = total
        self.chars = ['-', '\\', '|', '/']
        self.processed = processed

    def begin(self):
        self.processed = 0
        self.display()

    def display(self, processed = None):
        if processed:
            self.processed = processed

        show = self.chars[self.processed % 4]
        percent = (self.processed * 100)//self.total
        progress = (percent * self.length)//100
        blank = self.length - progress
        sys.stdout.write("\r %s [%s%s] %s%%" % \
                             (show, "#" * progress, " " * blank, percent))
        sys.stdout.flush()

    def increment(self, count = 1):
        self.processed += count
        self.display()

    def end(self):
        self.processed = self.total
        self.display()
