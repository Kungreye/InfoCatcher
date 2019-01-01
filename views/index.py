# _*_ coding: utf-8 _*_

import os

from flask import render_template, send_from_directory, abort, request
from flask.blueprints import Blueprint
from flask_security import login_required

from models.core import Post, Tag, PostTag
from models.feed import get_user_feed
from models.search import Item
from config import UPLOAD_FOLDER


bp = Blueprint('index', __name__)


@bp.route('/')
@login_required
def index():
    page = request.args.get('page', default=1, type=int)
    posts = get_user_feed(request.user_id, page)    # `posts` is pagination object
    return render_template('index.html', posts=posts, page=page)


@bp.route('/post/<id>/')
def post(id):
    post = Post.get_or_404(id)  # `get_or_4o4` defined in BaseModel
    return render_template('post.html', post=post)


@bp.route('/static/avatars/<path>')
def avatar(path):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'avatars'), path)


@bp.route('/tag/<ident>/')
def tag(ident):
    ident = ident.lower()
    tag = Tag.get_by_name(ident)
    if not tag:
        tag = Tag.get(ident)
        if not tag:
            abort(404)
    page = request.args.get('page', default=1, type=int)
    type = request.args.get('type', default='hot')  # hot/latest
    if type == 'latest':
        posts = PostTag.get_posts_by_tag(ident, page)   # paginate
    elif type == 'hot':
        posts = Item.get_post_ids_by_tag(ident, page, type)     # via Elasticsearch
        posts.items = Post.get_multi(posts.items)
    else:
        # Unknown type
        posts = []
    return render_template('tag.html', tag=tag, ident=ident, posts=posts,
                           type=type)   #  `posts` here is pagination object.


@bp.route('/search')
def search():
    # At present, only `Post` is searchable.
    query = request.args.get('q', '')
    page = request.args.get('page', default=1, type=int)
    posts = Item.new_search(query, page)    #  `Item.new_search()` returns a pagination object.
    return render_template('search.html', query=query, posts=posts)
