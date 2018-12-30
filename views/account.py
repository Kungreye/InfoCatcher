# _*_ coding: utf-8 _*_

from flask.blueprints import Blueprint
from flask import request, abort,  render_template
from flask_security import login_required

from models.user import User
from models.like import LikeItem
from models.collect import CollectItem
from models.contact import Contact
from models.core import Post
from corelib.utils import AttrDict


bp = Blueprint('account', __name__)


@bp.route('/landing')
def landing():
    email = request.args.get('email')
    if not email:
        abort(404)
    type = request.args.get('type')     # reset / confirm / register
    type_map = {
        'reset': 'RESET',
        'confirm': 'CONFIRM',
        'register': 'REGISTER',
        'confirmed': 'CONFIRMED'
    }
    if type not in type_map:
        type = 'register'
    action = type_map.get(type)
    return render_template('security/landing.html', **locals())


@bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def settings():
    notice = False
    if request.method == 'POST':
        user = request.user
        image = request.files.get('user_image')
        d = request.form.to_dict()
        d.pop('submit', None)
        form = AttrDict(d)
        github_id = form.github_id
        if github_id:
            form.github_url = f'http://github.com/{github_id}'
        del form.github_id
        user.update(**form)     #  `update` defined in BaseMixin, which is inherited to User
        if image:
            user.upload_avatar(image)
        notice = True
    return render_template('settings.html', notice=notice)


@bp.route('/user/<identifier>/')
def user(identifier):
    return render_user_page(identifier, 'user.html', User,
                           endpoint='account.user')


@bp.route('/user/<identifier>/likes/')
def user_likes(identifier):
    return render_user_page(identifier, 'card.html', Post, type='like',
                           endpoint='account.user_likes')


@bp.route('/user/<identifier>/collects/')
def user_collects(identifier):
    return render_user_page(identifier, 'card.html', Post, type='collect',
                           endpoint='account.user_collects')


@bp.route('/user/<identifier>/following/')
def user_following(identifier):
    return render_user_page(identifier, 'user.html', User, type='following',
                           endpoint='account.user_following')


@bp.route('/user/<identifier>/followers/')
def user_followers(identifier):
    return render_user_page(identifier, 'user.html', User, type='followers',
                           endpoint='account.user_followers')


def render_user_page(identifier, renderer, target_cls, type='following',
                     endpoint=None):
    user = User.cache.get(identifier)
    if not user:
        user = User.cache.filter(name=identifier).first()
    if not user:
        abort(404)
    page = request.args.get('page', default=1, type=int)
    if type == 'like':
        p = LikeItem.get_target_ids_by_user(user.id, page=page)     # post ids paginate
    elif type == 'collect':
        p = CollectItem.get_target_ids_by_user(user.id, page=page)  # post ids paginate
    elif type == 'following':
        p = Contact.get_following_ids(user.id, page=page)   # user ids paginate
    elif type == 'followers':
        p = Contact.get_follower_ids(user.id, page=page)    # user ids paginate
    p.items = target_cls.get_multi(p.items)     # posts or users
    return render_template(renderer, **locals())
