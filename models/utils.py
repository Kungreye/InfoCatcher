# _*_ coding: utf-8 _*_

import redis

from corelib.mc import rdb


def incr_key(MC_key, amount):
    try:
        total = rdb.incr(MC_key, amount)
    except redis.exceptions.ResponseError:
        rdb.delete(MC_key)
        total = rdb.incr(MC_key, amount)
    return total
