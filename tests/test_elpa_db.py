#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_elpa_db.py
    ~~~~~~~~~~~~~~~
    
    ELPA package database test suite
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os

import unittest

from g_elpa import elpa_db

from g_sorcery import exceptions, package_db

from tests.server import Server

from tests.base import BaseTest

def generate_archive_contents(packages):
    archive_contents = "(1"
    for pkg in packages:
        archive_contents += "\n(" + pkg[0] + ' . [('
        for v in pkg[1]:
            archive_contents += ' ' + str(v)
        archive_contents += ')\n'
        if pkg[4]:
            archive_contents += '('
            for p in pkg[4]:
                archive_contents += '(' + p[0] + ' ('
                for v in p[1]:
                    archive_contents += ' ' + str(v)
                archive_contents += '))\n'
            archive_contents += ')'
        else:
            archive_contents += 'nil'
        archive_contents += '\n "' + pkg[2] + '" ' + pkg[3] + '])' 
    archive_contents += ')'
    return archive_contents

packages = [['ack', [1, 2],
             "Interface to ack-like source code search tools",
             "tar",
             []
             ],
            ['dict-tree', [0, 12, 8],
             "Dictionary data structure",
             "tar",
             [['trie', [0, 2, 5]],
              ['tNFA', [0, 1, 1]],
              ['heap', [0, 3]]]
             ],
            ['tNFA', [0, 1, 1],
             "Tagged non-deterministic finite-state automata",
             "single",
             [['queue', [0, 1]]]
             ],
            ['trie', [0, 2, 6],
             "Trie data structure",
             "single",
             [['tNFA', [0, 1, 1]],
              ['queue', [0, 1]]]
             ],
            ['heap', [0, 3],
             "Heap (a.k.a. priority queue) data structure",
             "single",
             []
             ],
            ['queue', [0, 1],
             "Queue data structure",
             "single",
             []
             ]
            ]

def fill_database(database, packages, tempdir):
    prev = os.getcwd()
    os.chdir(tempdir)

    archive_contents = generate_archive_contents(packages)

    with open(os.path.join(tempdir, 'archive-contents'), 'w') as f:
        f.write(archive_contents)

    server = Server()
    server.start()

    database.generate()

    server.shutdown()
    server.join()

    os.chdir(prev)
    

class TestElpaDB(BaseTest):

    def test_generate(self):
        edb = elpa_db.ElpaDB(os.path.join(self.tempdir.name, 'db'),
                             repo_uri = 'http://127.0.0.1:8080')
        self.assertRaises(exceptions.SyncError, edb.generate)

        fill_database(edb, packages, self.tempdir.name)

        for pkg in packages:
            package = package_db.Package('app-emacs',
                                         pkg[0],
                                         '.'.join(map(str, pkg[1])))
            description = edb.get_package_description(package)
            self.assertEqual(description['source_type'], pkg[3])
            self.assertEqual(description['description'], pkg[2])
            deps = []
            depend=[]
            for d in pkg[4]:
                deps.append(package_db.Package('app-emacs',
                                               d[0],
                                               '.'.join(map(str, d[1]))))
                depend.append('app-emacs' + '/' + d[0])

            dependencies = description['dependencies']
            for d in dependencies:
                self.assertTrue(d in deps)
            for d in deps:
                self.assertTrue(d in dependencies)
            
            for ds in (description['depend'], description['rdepend']):
                for d in ds:
                    self.assertTrue(d in depend)
                for d in depend:
                    self.assertTrue(d in ds)
        

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestElpaDB('test_generate'))
    return suite
