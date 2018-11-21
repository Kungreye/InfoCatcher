# _*_ coding: utf-8 _*_

import functools
import hashlib

from dogpile.cache.region import make_region

from config import REDIS_URL


def md5_key_mangler(key):
    """
    key_mangler functions are used on all incoming keys before passing to the backend.
    Default to None, in which case the key mangling function recommended by the cache backend will be used.
    A typical mangler is SHA1 mangler, which coerces keys into a SHA1 hash, so the string length is fixed.

    :param key: incoming key
    :return: mangled key
    """
    if key.startswith('SELECT '):
        key = hashlib.md5(key.encode('ascii')).hexdigest()
    return key


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


regions = dict(
    default = make_region(key_mangler=md5_key_mangler).configure(
        'dogpile.cache.redis',
        arguments={
            'url': REDIS_URL,
        }
    )
)