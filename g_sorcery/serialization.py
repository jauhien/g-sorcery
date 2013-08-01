#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    serialization.py
    ~~~~~~~~~~~~~~~~
    
    json serialization
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import json
import importlib


class JSONSerializer(json.JSONEncoder):
    """
    Custom JSON encoder.

    Each serializable class should have a method serialize
    that returns JSON serializable value. If class addfitionally
    has a classmethod deserialize that it can be deserialized
    and additional metainformation is added to the resulting JSON.
    """
    def default(self, obj):
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
        return json.JSONEncoder.default(self, obj)


def deserializeHook(json_object):
    """
    Custom JSON decoder.

    Each class that can be deserialized should have classmethod deserialize
    that takes value (previously returned by serialize method) and transforms
    it into class instance.
    """
    if "python_class" in json_object:
        module = importlib.import_module(json_object["python_module"])
        cls = getattr(module, json_object["python_class"])
        return cls.deserialize(json_object["value"])
    return json_object
