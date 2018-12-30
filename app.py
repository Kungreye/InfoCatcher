#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

from flask import render_template, g
from flask_security import current_user
from werkzeug.wsgi import DispatcherMiddleware
from social_flask.routes import social_auth
from social_flask_sqlalchemy.models import init_social

from corelib.flask import Flask
from corelib.email import send_mail_task as _send_mail_task
from corelib.utils import update_url_query
from ext import security, db, mail
from forms import ExtendedLoginForm, ExtendedRegisterForm

import config
import views.account as account
import views.index as index
from views.api import json_api as api


def _inject_processor():
    return dict(isinstance=isinstance, current_user=current_user,
                getattr=getattr, len=len, user=current_user)    # `user= g.user = current_user`, make current_user available on tempaltes.


def _inject_template_global(app):
    app.add_template_global(dir)    # register a custom template global function (works exactly like the `template_global` decorator.
    app.add_template_global(len)
    app.add_template_global(hasattr)
    app.add_template_global(current_user, 'current_user')
    app.add_template_global(update_url_query)



def create_app():
    from models.user import user_datastore
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    mail.init_app(app)
    init_social(app, db.session)

    app.context_processor(_inject_processor)    # register a template context processor function.
    _inject_template_global(app)

    _state = security.init_app(app, user_datastore,
                               confirm_register_form=ExtendedRegisterForm,
                               login_form=ExtendedLoginForm)
    security._state = _state
    app.security = security
    security.send_mail_task(_send_mail_task)

    app.register_blueprint(index.bp)    # no `url_prefix`
    app.register_blueprint(account.bp)
    app.register_blueprint(social_auth)

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/api': api
    })

    @app.teardown_request   # register a func to be run at the end of each request, regardless of whether there was an exception or not.
    def teardown_request(exception):
        if exception:
            db.session.rollback()
        db.session.remove()

    return app


app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.before_request
def global_user():
    g.user = current_user
