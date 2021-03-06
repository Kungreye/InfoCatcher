#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

from datetime import datetime
from html.parser import HTMLParser

import feedparser   # parser of RSS/Atom

from app import app
from models.core import Post, Tag, PostTag, db
from models.search import Item


class MLStripper(HTMLParser):
    """Markup language stripper"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        # If true, the character references are converted automatically to the corresponding Unicode character
        # (and self.handle_data() is no longer split in chunks).
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, data):
        """overridable from HTMLParser"""
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    # feed data to the parser (call this as often as you want, with as little or as much text as you want).
    s.feed(html)
    return s.get_data()


def fetch(url):
    # parse a feed from a URL, file, stream or string, and return a FeedParserDict.
    d = feedparser.parse(url)
    entries = d.entries     # list of entry-level data

    posts = []

    for entry in entries:
        try:
            content = entry.content and entry.content[0].value
        except AttributeError:
            content = entry.summary or entry.title
        try:
            created_at = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            created_at = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')     # e.g.  Fri, 12 Oct ...
        try:
            tags = entry.tags
        except AttributeError:
            tags = []

        # Note: `author_id` should corresponds to a registered user_id.
        ok, post = Post.create_or_update(
            author_id=1, title=entry.title, orig_url=entry.link,
            content=strip_tags(content), created_at=created_at,
            tags = [tag.term for tag in tags])
        if ok:
            posts.append(post)
            # Item.add(post)
    # Item.bulk_update(posts, op_type='create')


def main():
    with app.test_request_context():
        Item._index.delete(ignore=404)  # delete Elasticsearch index, remove all data
        Item.init()     # create the index and populate the mappings in elasticsearch
        for model in (Post, Tag, PostTag):
            model.query.delete()    # by means of sqlalchemy to maneuver database. Do NOT directly operate on database.
        db.session.commit()

        for site in (
            'http://www.dongwm.com/atom.xml',
        ):
            fetch(site)


if __name__ == '__main__':
    main()
