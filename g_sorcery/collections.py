#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    collections.py
    ~~~~~~~~~~~~~~
    
    Customized classes of standard python data types
    for use withing g-sorcery for custom formatted string output
    substitution in our ebuild templates.
    
    :copyright: (c) 2013 by Brian Dolbec
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import collections

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
        return self._sep_.join(self)

Package = collections.namedtuple("Package", "category name version")
