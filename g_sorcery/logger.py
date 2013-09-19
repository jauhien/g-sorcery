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
        """
        Args:
            length: Length of the progress bar.
            total: The overall number of items to process.
            processe: Number of processed items.
        """
        self.length = length
        self.total = total
        self.chars = ['-', '\\', '|', '/']
        self.processed = processed

    def begin(self):
        """
        Start displaying the progress bar with 0% progress.
        """
        self.processed = 0
        self.display()

    def display(self, processed = None):
        """
        Show the progress bar with current progress.

        Args:
            processed: Number of processed items.
        """
        if processed:
            self.processed = processed

        show = self.chars[self.processed % 4]
        percent = (self.processed * 100)//self.total
        progress = (percent * self.length)//100
        blank = self.length - progress
        sys.stderr.write("\r %s [%s%s] %s%%" % \
                             (show, "#" * progress, " " * blank, percent))
        sys.stderr.flush()

    def increment(self, count = 1):
        """
        Increment number of processed items.

        Args:
            count: Step of incrementation.
        """
        self.processed += count
        self.display()

    def end(self):
        """
        Show 100%.
        """
        self.processed = self.total
        self.display()
