# _*_ coding: utf-8 _*_

import binascii
import os
import random
import struct
import threading
import time
from sqlalchemy.ext.hybrid import hybrid_property

_missing = object()


class cached_hybrid_property(hybrid_property):
    """hybrid_property: A decorator which allows definition of a Python descriptor with both instance-level and class-level behavior."""
    def __get__(self, instance, owner):
        if instance is None:
            return self.expr(owner)
        else:
            name = self.fget.__name__
            value = instance.__dict__.get(name, _missing)
            if value is _missing:
                value = self.fget(instance)
                instance.__dict__[name] = value
            return value


class ObjectId:
    _inc = random.randint(0, 0xFFFFFF)
    _inc_lock = threading.Lock()


# MongoDB -> bson -> object_id  (PyMongo)
def generate_id():
    oid = struct.pack(">i", int(time.time()))
    oid += struct.pack(">H", os.getpid() % 0xFFFF)
    with ObjectId._inc_lock:
        oid += struct.pack(">i", ObjectId._inc)[2:4]
        ObjectId._inc = (ObjectId._inc + 1) % 0xFFFFFF
    return binascii.hexlify(oid).decode('utf-8')


def is_numeric(value):
    try:
        int(value)
    except (TypeError, ValueError):
        return False
    return True


def trunc_utf8(string, num, etc="..."):
    if num > len(string):
        return string

    if etc:
        trunc_idx = num - len(ect)
    else:
        trunc_idx = num
    ret = string[:trunc_idx]
    if etc:
        ret += etc
    return ret


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class Empty:

    def __call__(self, *a, **kw):
        return empty

    def __nonzero__(self):
        return False

    def __contains__(self, item):
        return False

    def __repr__(self):
        return '<Empty Object>'

    def __str__(self):
        return ''

    def __eq__(self, v):
        return isinstance(v, Empty)

    def __getattr__(self, name):
        if not name.startswith('__'):
            return empty
        raise AttributeError(name)

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return empty

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def next(self):
        raise StopIteration


empty = Empty()
