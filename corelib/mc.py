# _*_ coding: utf-8 _*_

"""
Derived from practice of Memcached.
"""

import re
import inspect
from functools import wraps
from pickle import UnpicklingError

from sqlalchemy.ext.serializer import loads, dumps

from corelib.db import rdb
from corelib.utils import Empty, empty


__formatters = {}
percent_pattern = re.compile(r'%\w')
brace_pattern = re.compile(r'\{[\w\d\.\[\]_]+\}')

BUILTIN_TYPES = (int, float, str, bytes, bool)


def formatter(text):
    """
    >>> format('%s %s', 3, 2, 7, a=7, id=8)
    '3 2'
    >>> format('%(a)d %(id)s', 3, 2, 7, a=7, id=8)
    '7 8'
    >>> format('{1} {id}', 3. 2, a=7, id=8)
    '2 8'
    >>> class Obj: id = 3
    >>> format('{obj.id} {o.id}', Obj(), obj=Obj())
    '3 3'
    >>> class Obj: id = 3
    >>> format('{obj.id.__class__} {obj.id.__class__.__class__} {0.id} {1}', \
    >>> Obj(), 6, obj=Obj())
    "<type 'int'> <type 'type'> 3 6"
    """
    # Return all non_overlapping matches of pattern in string, as a list of strings.
    percent = percent_pattern.findall(text)
    # Scan through string looking for the first location where pattern produces a match, and returns a MatchObject instance.
    brace = brace_pattern.search(text)
    if percent and brace:
        raise Exception('mixed format is not allowed')

    if percent:
        n = len(percent)
        return lambda *a, **kw: text % tuple(a[:n])
    elif '%(' in text:
        return lambda *a, **kw: text % kw
    else:
        return text.format


def format(text, *a, **kw):
    f = __formatters.get(text)
    if f is None:
        f = formatter(text)
        __formatters[text] = f
    return f(*a, **kw)


def gen_key(key_pattern, arg_names, defaults, *a, **kw):
    return gen_key_factory(key_pattern, arg_names, defaults)(*a, **kw)


def gen_key_factory(key_pattern, arg_names, defaults):
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
    if callable(key_pattern):
        names = inspect.getfullargspec(key_pattern)[0]

    def gen_key(*a, **kw):
        aa = args.copy()    # shallow copy
        aa.update(zip(arg_names, a))
        aa.update(kw)
        if callable(key_pattern):
            key = key_pattern(*[aa[n] for n in names])
        else:
            key = format(key_pattern, *[aa[n] for n in arg_names], **aa)
        return key and key.replace(' ', '_'), aa
    return gen_key


def cache(key_pattern, expire=None):
    def deco(f):
        arg_names, varargs, varkw, defaults = inspect.getfullargspec(f)[:4]
        if varargs or varkw:
            raise Exception("not support varargs or varkw")
        gen_key = gen_key_factory(key_pattern, arg_names, defaults)

        @wraps(f)
        def _(*a, **kw):
            key, args = gen_key(*a, **kw)
            if not key:
                return f(*a, **kw)
            force = kw.pop('force', False)
            r = rdb.get(key) if not force else None

            if r is None:
                r = f(*a, **kw)
                if r is not None:
                    if not isinstance(r, BUILTIN_TYPES):
                        r = dumps(r)
                    rdb.set(key, r, expire)
                else:
                    r = dumps(empty)
                    rdb.set(key, r, expire)

            try:
                r = loads(r)
            except (TypeError, UnpicklingError):
                pass
            if isinstance(r, Empty):
                r = None
            return r
        _.original_function = f
        return _
    return deco


def pcache(key_pattern, count=300, expire=None):
    """cache with pagination"""
    def deco(f):
        arg_names, varargs, varkw, defaults = inspect.getfullargspec(f)[:4]
        if varargs or varkw:
            raise Exception("not support varargs or varkw")
        if not ('limit' in arg_names):
            raise Exception("function must have 'limit' in args")
        gen_key = gen_key_factory(key_pattern, arg_names, defaults)

        @wraps(f)
        def _(*a, **kw):
            key, args = gen_key(*a, **kw)
            start = args.pop('start', 0)
            limit = args.pop('limit')
            start = int(start)
            limit = int(limit)
            if (not key) or (limit is None) or (start + limit > count):
                return f(*a, **kw)

            force = kw.pop('force', False)
            r = rdb.get(key) if not force else None

            if r is None:
                r = f(limit=count, **args)
                r = dumps(r)
                rdb.set(key, r, expire)

            r = loads(r)
            return r[start:start + limit]
        _.original_function = f
        return _
    return deco


def pcache2(key_pattern, count=300, expire=None):
    def deco(f):
        arg_names, varargs, varkw, defaults = inspect.getfullargspec(f)[:4]
        if varargs or varkw:
            raise Exception('not support varargs or varkw')
        if not ('limit' in arg_names):
            raise Exception("function must have 'limit' in args'")
        gen_key = gen_key_factory(key_pattern, arg_names, defaults)

        @wraps(f)
        def _(*a, **kw):
            key, args = gen_key(*a, **kw)
            start = args.pop('start', 0)
            limit = args.pop('limit')
            if (not key) or (limit is None) or (start + limit > count):
                return f(*a, **kw)

            n = 0
            force = kw.pop('force', False)
            d = rdb.get(key) if not force else None
            if d is None:
                n, r = f(limit=count, **args)
                r = dumps(n, r)
                rdb.set(key, (n, r), expire)
            else:
                n, r = loads(r)
                r = loads(r)
            return (n, r[start:start + limit])
        _.original_function = f
        return _
    return deco
