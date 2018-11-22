# _*_ coding: utf-8 _*_

import copy
import json
from datetime import datetime

from walrus import Database as _Database
from sqlalchemy.ext.serializer import loads, dumps

from config import REDIS_URL
from corelib.local_cache import lc


class Database(_Database):
    def get2(self, name):
        rs = super().get(name)
        return loads(rs)

    def set2(self, name, value, ex=None, px=None, nx=False, xx=False):
        value = dumps(value)
        return super().set(name, value, ex=ex, px=px, nx=nx, xx=xx)


rdb = Database.from_url(REDIS_URL)


class PropsMixin(object):

    @property
    def _props_name(self):
        return '__%s/props_cached' % self.get_uuid()

    @property
    def _props_db_key(self):
        return '%s/props' % self.get_uuid()

    def _get_props(self):
        props = lc.get(self._props_name)
        if props is None:
            props = rdb.get(self._props_db_key) or ''
            props = props and json.loads(props) or {}
            lc.set(self._props_name, props)
        return props

    def _set_props(self, props):
        rdb.set(self._props_db_key, json.dumps(props))
        lc.delete(self._props_name)

    def _destroy_props(self):
        rdb.delete(self._props_db_key)
        lc.delete(self._props_name)

    destroy_props = _destroy_props

    get_props = _get_props
    set_props = _set_props

    props = property(_get_props, _set_props)

    def set_props_item(self, key, value):
        props = self.props
        props[key] = value
        self.props = props

    def delete_props_item(self, key):
        props = self.props
        props.pop(key, None)
        self.props = props

    def get_props_item(self, key, default=None):
        return self.props.get(key, default)

    def incr_props_item(self, key):
        n = self.get_props_item(key, 0)
        n += 1
        self.set_props_item(key, n)
        return n

    def decr_props_item(self, key, min=0):
        n = self.get_props_item(key, 0)
        n -= 1
        n = n > 0 and n or 0
        self.set_props_item(key, n > min and n or min)
        return n

    def update_props(self, data):
        props = self.props
        props.update(data)
        self.props = props


class PropsItem(object):

    def __init__(self, name, default=None, output_filter=None, pre_set=None):
        self.name = name
        self.default = default
        self.output_filter = output_filter
        self.pre_set = pre_set

    def __get__(self, obj, objtype):
        r = obj.get_props_item(self.name, None)
        if r is None:
            return copy.deepcopy(self.default)
        elif self.output_filer:
            return self.output_filter(r)
        else:
            return r

    def __set__(self, obj, value):
        if self.pre_set:
            value = self.pre_set(value)
        obj.set_props_item(self.name, value)

    def __delete__(self, obj):
        obj.delete_props_item(self.name)


datetime_outputfilter = lambda v: datetime.strptime(
    v, '%Y-%m-%d %H:%M:%S') if v else None
date_outputfilter = lambda v: datetime.strptime(
    v, '%Y-%m-%d').date() if v else None


class DatePropsItem(PropsItem):

    def __init__(self, name, default=None):
        super(DatePropsItem, self).__init__(name, default, date_outputfilter)
