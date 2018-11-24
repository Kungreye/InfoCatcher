# _*_ coding: utf-8 _*_

"""
Derived from practice of Memcached.
"""

import re
from functools import wraps

from sqlalchemy.ext.serializer import loads, dumps

from corelib.db import rdb
from corelib.utils import Empty


__formatters = {}
percent_pattern = re.compile(r'%\w')
brace_pattern = re.compile(r'\{[\w\d\.\[\]_]+\}')


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
    >>> Class Obj: id = 3
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

