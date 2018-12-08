# _*_ coding: utf-8 _*_

from flask.blueprints import Blueprint
from flask import request, abort,  render_template
from flask_security import login_required

from models.user import User
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


@bp.route('/user/<identifier>/')
def user(identifier):
    user = User.cache.get(identifier)
    if not user:
        user = User.cache.filter(name=identifier).first()
    if not user:
        abort(404)
    return render_template('user.html', **locals())


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
        user.update(**form)     #  `update` defined in BaseMixin, which is inherited to User
        if image:
            user.upload_avatar(image)
        notice = True
    return render_template('settings.html', notice=notice)
