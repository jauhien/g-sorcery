#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    g_collections.py
    ~~~~~~~~~~~~~~~~
    
    Customized classes of standard python data types
    for use withing g-sorcery for custom formatted string output
    substitution in our ebuild templates.
    
    :copyright: (c) 2013 by Brian Dolbec
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import collections

import portage

class elist(list):
    '''Custom list type which adds a customized __str__()
    and takes an optional separator argument

    elist() -> new empty elist
    elist(iterable) -> new elist initialized from iterable's items
    elist(separator='\\n\\t') -> new empty elist with
        newline & tab indented str(x) output
    elist(iterable, ' ') -> new elist initialized from iterable's items
        with space separated str(x) output
    '''

    __slots__ = ('_sep_')

    def __init__(self, iterable=None, separator=' '):
        '''
        iterable: initialize from iterable's items
        separator: string used to join list members with for __str__()
        '''
        list.__init__(self, iterable or [])
        self._sep_ = separator

    def __str__(self):
        '''Custom output function
        'x.__str__() <==> str(separator.join(x))'
        '''
        return self._sep_.join(map(str, self))

Package = collections.namedtuple("Package", "category name version")


class Dependency(object):

    __slots__ = ('atom', 'category', 'package', 'version', 'operator')

    def __init__(self, category, package, version="", operator=""):
        atom_str = operator + category + "/" + package
        if version:            
            atom_str += "-" + str(version)
        object.__setattr__(self, "atom", portage.dep.Atom(atom_str))
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "package", package)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "operator", operator)

    def __setattr__(self, name, value):
        raise AttributeError("Dependency instances are immutable",
                             self.__class__, name, value)

    def __str__(self):
        return str(self.atom)
