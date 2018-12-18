#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

from flask import render_template
from flask_security import current_user

from corelib.flask import Flask
from corelib.email import send_mail_task as _send_mail_task
from ext import security, db, mail
from forms import ExtendedLoginForm, ExtendedRegisterForm

import views.index as index
import views.account as account
import config


def _inject_processor():
    return dict(isinstance=isinstance, current_user=current_user,
                getattr=getattr, len=len)


def _inject_template_global(app):
    app.add_template_global(dir)    # register a custom template global function (works exactly like the `template_global` decorator.
    app.add_template_global(len)
    app.add_template_global(hasattr)
    app.add_template_global(current_user, 'current_user')



def create_app():
    from models.user import user_datastore
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    mail.init_app(app)

    app.context_processor(_inject_processor)    # register a template context processor function.
    _inject_template_global(app)

    _state = security.init_app(app, user_datastore,
                               confirm_register_form=ExtendedRegisterForm,
                               login_form=ExtendedLoginForm)
    security._state = _state
    app.security = security
    security.send_mail_task(_send_mail_task)

    app.register_blueprint(index.bp, url_prefix='/')
    app.register_blueprint(account.bp, url_prefix='/')

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
