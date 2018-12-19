# _*_ coding: utf-8 _*_

from flask import request, get_template_attribute
from flask.views import MethodView

from ext import db, security
from models.core import Post
from models.user import user_datastore

from . import errors
from .exceptions import ApiException
from .schemas import PostSchema
from .utils import ApiFlask, ApiResult, marshal_with


def create_app():
    app = ApiFlask(__name__, template_folder='../../templates')
    app.config.from_object('config')
    db.init_app(app)
    security.init_app(app, user_datastore)

    return app


json_api = create_app()


#Register a function to handle errors by `code_or_exception` class
@json_api.errorhandler(ApiException)
def api_error_handler(error):
    return error.to_result()


@json_api.errorhandler(401)     # Unauthorized
@json_api.errorhandler(403)     # Forbidden
@json_api.errorhandler(404)     # Not found
@json_api.errorhandler(500)     # Internal server error
def error_handler(error):
    if hasattr(error, 'name'):
        status = error.code
        if status == '403':
            msg = 'Forbidden'
        else:
            msg = error.name
    else:
        msg = error.message
        status = 500
    return ApiResult({'errmsg': msg, 'r': 1, 'status': status})


class ActionAPI(MethodView):
    do_action = None
    undo_action = None

    def _prepare(self, post_id):
        post = Post.get(post_id)
        if not post:
            raise ApiException(errors.post_not_found)
        return post

    def _merge(self, post):
        user_id = request.user_id
        post.is_liked = post.is_liked_by(user_id)
        post.is_collected = post.is_collected_by(user_id)
        return post

    @marshal_with(PostSchema)
    def post(self, post_id):    #  `post` corresponds to method 'POST'
        post = self._prepare(post_id)
        if self.do_action != 'add_comment':
            # only `add_comment` involves `content`
            ok = getattr(post, self.do_action)(request.user_id)
        else:
            content = request.form.get('content')   # 'content' in comment form of post.html ?
            ok, comment = getattr(post, self.do_action)(
                request.user_id, content)
            if ok:
                macro = get_template_attribute(
                    '_macros.html', 'render_comment')
                return {'html': str(macro(comment).replace('\n\r', ''))}
        if not ok:
            raise ApiException(errors.illegal_state)
        return self._merge(post)

    @marshal_with(PostSchema)
    def delete(self, post_id):  # `delete` corresponds to method `DELETE`
        post = self._prepare(post_id)
        if self.undo_action != 'del_comment':
            # only `del_comment` needs `comment_id` plus `post_id`
            ok = getattr(post, self.undo_action)(request.user_id)
        else:
            comment_id = request.form.get('comment_id')
            ok = getattr(post, self.undo_action)(request.user_id, comment_id)
        if not ok:
            raise ApiException(errors.illegal_state)
        return self._merge(post)


class LikeAPI(ActionAPI):
    do_action = 'like'
    undo_action = 'unlike'


class CommentAPI(ActionAPI):
    do_action = 'add_comment'
    undo_action = 'del_comment'


class CollectAPI(ActionAPI):
    do_action = 'collect'
    undo_action = 'uncollect'


for name, view_cls in (('like', LikeAPI), ('comment', CommentAPI),
                       ('collect', CollectAPI)):
    view = view_cls.as_view(name)
    json_api.add_url_rule(f'/post/<int:post_id>/{name}',
                          view_func=view, methods=['POST', 'DELETE'])

"""
### Only for test

class PostAPI(MethodView):
    def get(self, post_id):
        post = Post.get_or_404(post_id)
        return {}
    
    @marshal_with(PostSchema)
    def post(self, post_id):
        data = self.get_data()  # ?
        return Post.create(**data)
    
    @marshal_with(PostSchema)
    def delete(self, post_id):
        raise ApiException(errors.not_supported)
        

post_view = PostAPI.as_view('roles')
json_api.add_url_rule('/post/<int:post_id>',
                      view_func=post_view, methods=['GET', 'POST', 'DELETE'])
"""
