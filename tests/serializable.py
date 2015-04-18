#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    serializable.py
    ~~~~~~~~~~~~~~~

    test classes for serialization

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

class NonSerializableClass(object):
    pass


class SerializableClass(object):

    __slots__ = ("field1", "field2")

    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2

    def __eq__(self, other):
        return self.field1 == other.field1 \
          and self.field2 == other.field2

    def serialize(self):
        return {"field1": self.field1, "field2": self.field2}


class DeserializableClass(SerializableClass):

    @classmethod
    def deserialize(cls, value):
        return DeserializableClass(value["field1"], value["field2"])
