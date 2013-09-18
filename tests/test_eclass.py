#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_eclass.py
    ~~~~~~~~~~~~~~
    
    eclass test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest

from g_sorcery.eclass import EclassGenerator

from tests.base import BaseTest


class TestEclassGenerator(BaseTest):

    def test_eclass_generator(self):
        eclasses = ["test1", "test2"]
        for eclass in eclasses:
            os.system("echo 'eclass " + eclass + "' > " + os.path.join(self.tempdir.name, eclass + ".eclass"))

        eclass_g = EclassGenerator(self.tempdir.name)
        self.assertEqual(set(eclass_g.list()), set(eclasses) | set(["g-sorcery"]))

        for eclass in eclasses:
            self.assertEqual(eclass_g.generate(eclass), ["eclass " + eclass])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestEclassGenerator('test_eclass_generator'))
    return suite
