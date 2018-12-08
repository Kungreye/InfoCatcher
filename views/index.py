# _*_ coding: utf-8 _*_

import os

from flask import render_template, send_from_directory, abort, request
from flask.blueprints import Blueprint

from models.core import Post, Tag, PostTag
from config import UPLOAD_FOLDER


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/post/<id>')
def post(id):
    post = Post.get_or_404(id)  # `get_or_4o4` defined in BaseModel
    return render_template('post.html', post=post)


@bp.route('/static/avatars/<path>')
def avatar(path):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'avatars'), path)


@bp.route('/tag/<ident>')
def tag(ident):
    ident = ident.lower()
    tag = Tag.get_by_name(ident)
    if not tag:
        tag = Tag.get(ident)
        if not tag:
            abort(404)
    page = int(request.args.get('page') or 1)
    posts = PostTag.get_posts_by_tag(ident, page)   # `PostTag.get_posts_by_tag` returns a pagination object, so use `posts.items` in tag.html
    return render_template('tag.html', tag=tag, ident=ident, posts=posts)
