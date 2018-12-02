# _*_ coding: utf-8 _*_

from flask import render_template
from flask.blueprints import Blueprint

from models.core import Post


bp = Blueprint('index', __name__)

@bp.route('/post/<id>')
def post(id):
    post = Post.get_or_404(id)  # `get_or_4o4` defined in BaseModel
    return render_template('post.html', post=post)
