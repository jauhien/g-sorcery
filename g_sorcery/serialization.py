#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    serialization.py
    ~~~~~~~~~~~~~~~~

    json serialization

    :copyright: (c) 2013-2015 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json
import importlib

from .compatibility import basestring

def step_to_raw_serializable(obj):
    """
    Make one step of convertion of object
    to the type that is serializable
    by the json library.

    None return value signifies an error.
    """
    if hasattr(obj, "serialize"):
        if hasattr(obj, "deserialize"):
            module = obj.__class__.__module__
            name = obj.__class__.__name__
            value = obj.serialize()
            return {"python_module" : module,
                    "python_class" : name,
                    "value" : value}
        else:
            return obj.serialize()
    return None


def to_raw_serializable(obj):
    """
    Convert object to the raw serializable type.
    Logic is the same as in the standard json encoder.
    """
    if isinstance(obj, basestring) \
       or obj is None \
       or obj is True \
       or obj is False \
       or isinstance(obj, int) \
       or isinstance(obj, float):
        return obj
    elif isinstance(obj, dict):
        return {k: to_raw_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_raw_serializable(item) for item in obj]

    else:
        sobj = step_to_raw_serializable(obj)
        if not sobj:
            raise TypeError('Non serializable object: ', obj)
        return to_raw_serializable(sobj)


def step_from_raw_serializable(sobj):
    """
    Make one step of building of object from the
    raw json serializable type.
    """
    if "python_class" in sobj:
        module = importlib.import_module(sobj["python_module"])
        cls = getattr(module, sobj["python_class"])
        return cls.deserialize(sobj["value"])
    return sobj


def from_raw_serializable(sobj):
    """
    Build object from the raw serializable object.
    """
    if isinstance(sobj, dict):
        res = {k: from_raw_serializable(v) for k, v in sobj.items()}
        return step_from_raw_serializable(res)
    elif isinstance(sobj, list):
        return [from_raw_serializable(item) for item in sobj]
    else:
        return sobj


class JSONSerializer(json.JSONEncoder):
    """
    Custom JSON encoder.

    Each serializable class should have a method serialize
    that returns JSON serializable value. If class additionally
    has a classmethod deserialize that it can be deserialized
    and additional metainformation is added to the resulting JSON.
    """
    def default(self, obj):
        res = step_to_raw_serializable(obj)
        if res:
            return res
        else:
            return json.JSONEncoder.default(self, obj)


def deserializeHook(json_object):
    """
    Custom JSON decoder.

    Each class that can be deserialized should have classmethod deserialize
    that takes value (previously returned by serialize method) and transforms
    it into class instance.
    """
    return step_from_raw_serializable(json_object)
