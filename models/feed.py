# _*_ coding: utf-8 _*_

import math
from datetime import datetime, timedelta

from flask_sqlalchemy import Pagination

from config import PER_PAGE
from corelib.db import rdb
from models.consts import ONE_MINUTE
from models.contact import Contact
from models.user import User
from models.core import Post



DAYS = 300 # Should be 3; just for test
MAX = 100
FEED_KEY = 'feed:{}'    # user_id
ACTIVITY_KEY = 'feed:activity'
ACTIVITY_UPDATED_KEY = 'feed:activity_updated:{}'   # user_id
LAST_VISIT_KEY = 'last_visit_id:{}:{}'  # user_id, visit_id


class ActivityFeed:
    """hot feed, common to all users"""
    @staticmethod
    def add(time, post_id):
        # sorted set: zadd(key, score, name)
        rdb.zadd(ACTIVITY_KEY, time, post_id)
        rdb.zremrangebyrank(ACTIVITY_KEY, MAX, -1)      # only retain 200 hot post (in descending time order)

    @staticmethod
    def delete(*post_ids):
        rdb.zrem(ACTIVITY_KEY, *post_ids)

    @staticmethod
    def get_all():
        return rdb.zrange(ACTIVITY_KEY, 0, -1, withscores=True)


def get_user_latest_posts(uid, visit_id):
    user = User.get(uid)
    if not user:
        return

    query = Post.query.with_entities(Post.id, Post.created_at)
    visit_key = LAST_VISIT_KEY.format(uid, visit_id)
    last_visit_id = rdb.get(visit_key)
    if last_visit_id:
        query = query.filter(Post.id > int(last_visit_id))
    else:
        query = query.filter(Post.created_at >= (datetime.now() - timedelta(days=DAYS)))    # noqa

    posts = query.order_by(Post.id.desc()).all()

    if posts:
        last_visit_id = posts[0][0]
        rdb.set(visit_key, last_visit_id)   #  `last_visit_id` is post_id
    return posts


def gen_followers(uid):
    user = User.get(uid)
    if not user:
        return []

    pages = math.ceil((max(user.n_followers, 0) or 1) / PER_PAGE)
    for p in range(1, pages + 1):
        yield Contact.get_follower_ids(uid, p).items    # cached


def feed_to_followers(visit_id, uid):
    posts = get_user_latest_posts(uid, visit_id)
    if not posts:
        return
    items = []
    for post_id, created_at in posts:
        items.extend([post_id, int(created_at.strftime('%s'))])
    key = FEED_KEY.format(visit_id)
    rdb.zadd(key, *items)


def feed_post(post):
    user = User.get(post.author_id)
    for uids in gen_followers(post.author_id):
        for visit_id in uids:
            key = FEED_KEY.format(visit_id)
            rdb.zadd(key, int(post.created_at.strftime('%s')), post.id)
            visit_key = LAST_VISIT_KEY.format(user.id, visit_id)
            rdb.set(visit_key, post.id)


def remove_post_from_feed(post_id, author_id):
    user = User.get(author_id)
    for uids in gen_followers(author_id):
        for visit_id in uids:
            key = FEED_KEY.format(visit_id)
            rdb.zrem(key, post_id)
            ActivityFeed.delete(post_id)


def remove_user_posts_from_feed(visit_id, uid):
    post_ids = [id for id, in Post.query.with_entities(Post.id).filter(
        Post.author_id == uid)]
    key = FEED_KEY.format(visit_id)
    rdb.zrem(key, *post_ids)


def get_user_feed(user_id, page):
    """combine hot feed & subscribed feed, all zadded into user-specific feed_key"""
    feed_key = FEED_KEY.format(user_id)
    update_key = ACTIVITY_UPDATED_KEY.format(user_id)
    if not rdb.get(update_key):
        items = ActivityFeed.get_all()
        if items:
            rdb.zadd(feed_key, *sum([(int(time), id) for id, time in items], ()))    # `time` is score
        rdb.set(update_key, 1, ex=ONE_MINUTE * 5)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    post_ids = rdb.zrange(feed_key, start, end)
    items = Post.get_multi([int(id) for id in post_ids])
    total = rdb.zcard(feed_key)
    return Pagination(None, page, PER_PAGE, total, items)   # Pagination(query, page, per_page, total, items)
