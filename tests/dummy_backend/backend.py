#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Test:
    def __init__(self):
        self.tst = 'test backend'
    
    def test(self):
        return('test')

    def __eq__(self, other):
        return self.tst == other.tst

instance = Test()
