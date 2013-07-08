#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    dispatcher.py
    ~~~~~~~~~~~~~
    
    backend dispatcher
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import argparse

class Dispatcher(object):

    def __init__(self, server_backend, user_backend, digest_in_existent_overlay=True):
        self.server_backend = server_backend
        self.user_backend = user_backend
        if digest_in_existent_overlay:
            self.existent_overlay_backend = self.server_backend
        else:
            self.existent_overlay_backend = self.user_backend

        self.parser = argparse.ArgumentParser(description='Automatic ebuild generator.')
        self.parser.add_argument('--list')

    def __call__(self, args):
        return self.parser.parse_args(args)
