# _*_ coding: utf-8 _*_

import functools
import hashlib
from datetime import datetime

from flask import abort

from flask_sqlalchemy import BaseQuery, Model, DefaultMeta, SQLAlchemy, _QueryProperty

from sqlalchemy import Column, Integer, DateTime, inspect, event
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta, declarative_base
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.orm.interfaces import MapperOption

from dogpile.cache.region import make_region
from dogpile.cache.api import NO_VALUE

from flask_mail import Mail
from flask_security import Security

from config import REDIS_URL
from corelib.db import PropsMixin, PropsItem


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
    """Used to cache generated various keys/attrs/..., so avoid repeatedly generating."""
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


# `make_region` is a passthrough to `CacheRegion`; it will instantiate a new `CacheRegion`.
regions = dict(default = make_region(key_mangler=md5_key_mangler).configure(
    'dogpile.cache.redis',
    arguments={'url': REDIS_URL}
))


"""New concepts are introduced to allow the usage of Dogpile caching with SQLAlchemy, as below:

* `CachingQuery` - a Query subclass that caches and retrieves results in/from dogpile.cache.
* `FromCache` - a query option that establishes caching parameters on a Query.
* `RelationshipCache` - a variant of FromCache which specific to a query invoked during a lazy load.
* `_params_from_query` - extracts value parameters from a Query.  
"""

class CachingQuery(BaseQuery):
    """A Query subclass which optionally loads full results from a dogpile cache region.

    The CachingQuery optionally stores additional state that allows it to consult a dogpile.cache cache
    before accessing the database, in the form of a FromCache or RelationshipCache object. Each of these objects
    refer to the name of a :class:`dogpile.cache.Region` that's been configured and stored in a lookup dictionary.
    When such an object has associated itself with the CachingQuery, the corresponding :class:`dogpile.cache.Region`
    is used to locate a cached result. If none is present, then the Query is invoked normally, the result being cached.

    The FromCache and RelationshipCache mapper options below represent the "public" method of configuring this state
    upon the CachingQuery.
    """
    def __init__(self, regions, entities, *args, **kw):
        self.cache_regions = regions
        BaseQuery.__init__(self, entities=entities, *args, **kw)

    def __iter__(self):
        """override __iter__ to pull results from dogpile if particular attributes have been configured.

        Note that this approach does NOT detach the loaded objects from the current session. If the cache backend
        is an in-process cache (like "memory") and lives beyond the scope of the current session's transaction,
        those objects may be expired. The method here can be modified to first expunge() each loaded item from the
        current session before returning the list of items, so that the items in the cache are not the same ones
        in the current session.
        """
        if hasattr(self, '_cache_region'):
            return self.get_value(createfunc=lambda: list(BaseQuery.__iter__(self)))
        else:
            return BaseQuery.__iter__(self)

    def _get_cache_plus_key(self):
        """Return a cache region plus key."""
        dogpile_region = self.cache_regions[self._cache_region.region]
        if self._cache_region.cache_key:
            key = self._cache_region.cache_key
        else:
            key = _key_from_query(self)
        return dogpile_region, key

    def invalidate(self):
        dogpile_region, cache_key = self._get_cache_plus_key()
        dogpile_region.delete(cache_key)

    def get_value(self, merge=True, createfunc=None,
                  expiration_time=None, ignore_expiration=False):
        """Return the value from the cache for this query.
        Raise KeyError if no value present and no createfunc specified.
        """
        dogpile_region, cache_key = self._get_cache_plus_key()

        # ignore_expiration means, if the value is in the cache but is expired, return it anyway.
        # It doesn't make sense with createfunc, which means if the value is expired, generate a new value.
        assert not ignore_expiration or not createfunc, \
            "Can't ignore expiration and also provide createfunc"

        if ignore_expiration or not createfunc:
            cached_value = dogpile_region.get(
                cache_key,
                expiration_time=expiration_time,
                ignore_expiration=ignore_expiration)
        else:
            cached_value = dogpile_region.get_or_create(
                cache_key,
                createfunc,
                expiration_time=expiration_time)

        if cached_value is NO_VALUE:
            raise KeyError(cache_key)
        if merge:
            cached_value = self.merge_result(cached_value, load=False)

        return cached_value

    def set_value(self, value):
        dogpile_region, cache_key = self._get_cache_plus_key()
        dogpile_region.set(cache_key, value)


def query_callable(regions, query_cls=CachingQuery):
    def query(*args, **kw):
        return query_cls(regions, *args, **kw)
    return query


def _key_from_query(query, qualifier=None):
    """Given a Query, create a cache key.
    Here we create an md5 hash of the text of the SQL statement,
    combined with stringed versions of all the bound parameters within it.
    """
    stmt = query.with_labels().statement    # <tablename>_<columnname>
    compiled = stmt.compile()
    params = compiled.params

    # Here we return the key as a long string. Our "key mangler" set up with the region will boil it down to an md5.
    return " ".join(
        [str(compiled)] +
        [str(params(k)) for k in sorted(params)])


class FromCache(MapperOption):
    """Specifies that a Query should load results from a cache."""

    propagate_to_loaders = False

    def __init__(self, region="default", cache_key=None):
        """ Construct a new FromCache.
        :param region: the cache region. Should be a region configured in the dictionary of dogpile regions.
        :param cache_key: optional. A string cache key that will serve as the key to the query. Use this if your query
        has a huge amount of parameters (e.g. when using in_()) which correspond more simply to some other identifiers.
        """
        self.region = region
        self.cache_key = cache_key

    def process_query(self, query):
        """Process a Query during normal loading operation."""
        query._cache_region = self


class Query(object):
    def __init__(self, entities):
        self.entities = entities

    def __iter__(self):
        return self.entities

    def first(self):
        try:
            return self.entities.__next__()
        except StopIteration:
            return None

    def all(self):
        return list(self.entities)


class Cache(object):
    def __init__(self, model, regions, label):
        self.model = model
        self.regions = regions
        self.label = label
        self.pk = getattr(model, 'cache_pk', 'id')

    def get(self, pk):
        return self.model.query.options(self.from_cache(pk=pk)).get(pk)

    def count(self, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise TypeError(
                    'filter accept only one attribute for filtering')
            key, value = list(kwargs.items())[0]    # {'m':1} -> [('m',1)]
            if key not in self._attrs():
                raise TypeError('%s does not have an attribute %s' % self, key)

        cache_key = self._count_cache_key(**kwargs)
        r = self.regions[self.label]
        count = r.get(cache_key)

        if count is NO_VALUE:
            count = self.model.query.filter_by(**kwargs).count()
            r.set(cache_key, count)
        return count

    def filter(self, order_by='asc', offset='None', limit=None, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise TypeError(
                    'filter accept only one attribute for filtering')
            key, value = list(kwargs.items())[0]
            if key not in self._attrs():
                raise TypeError('%s does not have an attribute %s' % self, key)

        cache_key = self._cache_key(**kwargs)
        r = self.regions[self.label]
        pks = r.get(cache_key)

        if pks is NO_VALUE:
            pks = [o.id for o in self.model.query.filter_by(**kwargs)
                   .with_entities(getattr(self.model, self.pk))]
            r.set(cache_key, pks)

        if order_by == 'desc':
            pks.reverse()

        if offset is not None:
            pks = pks[offset:]

        if limit is not None:
            pks = pks[:limit]

        keys = [self._cache_key(id) for id in pks]
        return Query(self.gen_entities(pks, r.get_multi(keys)))

    def gen_entities(self, pks, objs):
        for pos, obj in enumerate(objs):
            if obj is NO_VALUE:
                yield self.get(pks[pos])
            else:
                yield obj[0]

    def flush(self, key):
        self.regions[self.label].delete(key)

    @memoize
    def _attrs(self):
        return [a.key for a in inspect(self.model).attrs if a.key != self.pk]

    @memoize
    def from_cache(self, cache_key=None, pk=None):
        if pk:
            cache_key = self._cache_key(pk)
        return FromCache(self.label, cache_key)

    @memoize
    def _count_cache_key(self, pk="all", **kwargs):
        return self._cache_key(pk, **kwargs) + '_count'

    @memoize
    def _cache_key(self, pk="all", **kwargs):
        q_filter = "".join("%s=%s" % (k, v)
                           for k, v in kwargs.items()) or self.pk
        return "%s.%s[%s]" % (self.model.__tablename__, q_filter, pk)

    def _flush_all(self, obj):
        for attr in self._attrs():
            added, unchanged, deleted = get_history(obj, attr)
            for value in list(deleted) + list(added):
                self.flush(self._cache_key(**{attr: value}))
        for key in (self._cache_key(), self._cache_key(getattr(obj, self.pk)),
                    self._count_cache_key(),
                    self._count_cache_key(getattr(obj, self.pk))):
            self.flush(key)


class BindDBPropertyMixin(object):
    def __init__(cls, name, bases, d):
        super(BindDBPropertyMixin, cls).__init__(name, bases, d)    # 元编程中 (cls, name, bases, attrs)
        db_columns = []
        for k, v in d.items():
            if isinstance(v, PropsItem):
                db_columns.append((k, v.default))
        setattr(cls, '_db_columns', db_columns)


class CombinedMeta(BindDBPropertyMixin, DefaultMeta):
    pass


"""`Model`, inherited from flask-sqlalchemy, has convenience property to query the database for instances of this model.
"""
class BaseModel(PropsMixin, Model):
    cache_label = "default"
    cache_regions = regions
    query_class = query_callable(regions)

    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=None)

    def get_uuid(self):
        return '/bran/{0.__class__.__name__}/{0.id}'.format(self)

    def __repr__(self):
        return '<{0} id: {1}>'.format(self.__class__.__name__, self.id)

    @declared_attr
    def cache(cls):
        return Cache(cls, cls.cache_regions, cls.cache_label)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_or_404(cls, ident):
        rv = cls.get(ident)
        if rv is None:
            abort(404)
        return rv

    @classmethod
    def get_multi(cls, ids):
        return [cls.cache.get(id) for id in ids]

    def url(self):
        return '/{}/{}/'.format(self.__class__.__name__.lower(), self.id)

    def to_dict(self):
        columns = self.__table__.columns.keys()
        dct = {key: getattr(self, key) for key in columns}
        return dct

    @staticmethod
    def _flush_insert_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)

    @staticmethod
    def _flush_after_update_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)

    @staticmethod
    def _flush_before_update_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)

    @staticmethod
    def _flush_delete_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)

    @staticmethod
    def _flush_event(mapper, connection, target):
        target.cache._flush_all(target)
        target.__flush_event__(target)

    @classmethod
    def __flush_event__(cls, target):
        pass

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'after_delete', cls._flush_delete_event)
        event.listen(cls, 'after_update', cls._flush_after_update_event)
        event.listen(cls, 'before_update', cls._flush_before_update_event)
        event.listen(cls, 'after_insert', cls._flush_insert_event)


class UnLockedAlchemy(SQLAlchemy):
    def make_declarative_base(self, model, metadata=None):
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=CombinedMeta
            )

        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model

    def apply_driver_hacks(self, app, info, options):
        """This method is called before engine creation and used to inject driver specific hacks into the options.
        The `options` parameter is a dictionary of keyword arguments that will then be used to call the :func:`sqlalchemy.create_engine`."""
        if 'isolation_level' not in options:
            options['isolation_level'] = 'READ COMMITTED'
        return super(UnLockedAlchemy, self).apply_driver_hacks(
            app, info, options)

mail = Mail()
security = Security()
db = UnLockedAlchemy(model_class=BaseModel)     # `model_base` for SQLAlchemy.__init__
