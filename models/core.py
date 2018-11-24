# _*_ coding: utf-8 _*_

import os

from ext import db

from models.comment import CommentMixin
from models.consts import K_POST
from models.mixin import BaseMixin

from corelib.db import PropsItem
from corelib.mc import rdb
from corelib.utils import is_numeric, cached_hybrid_property


MC_KEY_ALL_TAGS = 'core:all_tags'
HERE = os.path.abspath(os.path.dirname(__file__))


class Post(BaseMixin, CommentMixin, db.Model):
    __tablename__ = 'posts'
    author_id = db.Column(db.Integer)
    title = db.Column(db.String(128), default='')
    orig_url = db.Column(db.String(255), default='')
    can_comment = db.Column(db.Boolean, default=True)
    content = PropsItem('content', '')
    kind = K_POST

    __table_args__ = (
        db.Index('idx_title', title),
    )

    def url(self):
        return '/{}/{}/'.format(self.__class__.__name__.lower(),
                                self.slug or self.id)

    @classmethod
    def __flush_event__(cls, target):
        rdb.delete(MC_KEY_ALL_TAGS)

    @classmethod
    def get(cls, identifier):
        post = cls.cache.filter(slug=identifier).first()
        if post:
            return post
        if is_numeric:
            return cls.cache.get(identifier)
        return cls.cache.filter(title=identifier).first()

    @property
    # TODO cache
    def tags(self):
        at_ids = PostTag.query.with_entities(
            PostTag.tag_id).filter(
                PostTag.article_id == self.id
            ).all()

        tags = Tag.query.filter(Tag.id.in_(id for id, in at_ids))
        tags = [t.name for t in tags]
        return tags

    @cached_hybrid_property
    def abstract_content(self):
        return self.content

    @classmethod
    def create_or_update(cls, **kwargs):
        tags = kwargs.pop('tags', [])
        created, obj = super(Post, cls).create_or_update(**kwargs)
        if tags:
            PostTag.update_multi(obj.id, tags)
        return created, obj


class Tag(BaseMixin, db.Model):
    __tablename__ = 'tags'
    name = db.Column(db.String(128), default='')

    __table_args__ = (
        db.Index('idx_name', name),
    )

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


class PostTag(BaseMixin, db.Model):
    __tablename__ = 'post_tags'
    post_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)

    __table_args__ = (
        db.Index('idx_post_id', post_id, 'updated_at'),
        db.Index('idx_tag_id', tag_id, 'updated_at'),
    )

    @classmethod
    def get_posts_by_tag(cls, identifier):
        if not identifier:
            return []
        if not is_numeric(identifier):
            tag = Tag.get_by_name(identifier)
            if not tag:
                return
            identifier = tag.id
        at_ids = cls.query.with_entities(cls.post_id).filter(
            cls.tag_id == identifier
        ).all()

        posts = Post.query.filter(
            Post.id.in_(id for id, in at_ids)).order_by(Post.id.desc())
        return posts

    @classmethod
    def update_multi(cls, post_id, tags):
        origin_tags = Post.get(post_id).tags
        need_add = set()
        need_del = set()
        for tag in tags:
            if tag not in origin_tags:
                need_add.add(tag)
        for tag in origin_tags:
            if tag not in tags:
                need_del.add(tag)
        need_add_tag_ids = set()
        need_del_tag_ids = set()
        for tag_name in need_add:
            _, tag = Tag.create(name=tag_name)
            need_add_tag_ids.add(tag.id)
        for tag_name in need_del:
            _, tag = Tag.create(name=tag_name)
            need_del_tag_ids.add(tag.id)

        if need_del_tag_ids:
            obj = cls.query.filter(cls.post_id == post_id,
                                   cls.tag_id.in_(need_del_tag_ids))
            obj.delete(synchronize_session='fetch')     #  `fetch`: perform a select query, and matched objects are removed from session.
        for tag_id in need_add_tag_ids:
            cls.create(post_id=post_id, tag_id=tag_id)
        db.session.commit()
