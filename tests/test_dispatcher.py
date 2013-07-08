#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_dispatcher.py
    ~~~~~~~~~~~~~~~~~~
    
    backend dispatcher test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import unittest

from g_sorcery import dispatcher

from tests.base import BaseTest

class TestDispatcher(BaseTest):

    def test_dispatcher(self):
        pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDispatcher('test_dispatcher'))
    return suite
