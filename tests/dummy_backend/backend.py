#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Test(object):
    def __init__(self):
        self.tst = 'test backend'
    
    def __call__(self, args):
        print(args[0])
        return 0

    def __eq__(self, other):
        return self.tst == other.tst

dispatcher = Test()
