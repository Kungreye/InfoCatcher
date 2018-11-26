# _*_ coding: utf-8 _*_

import os

HERE = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(HERE, 'permdir')


SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess-this')
TEMPLATES_AUTO_RELOAD = False


DEBUG = False
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')    # noqa
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True    # for using `get_debug_queries` of Flask-SQLAlchemy
DATABASE_QUERY_TIMEOUT = 0.5    # slow database query threshold (in seconds)

CACHE_TYPE = 'redis'
REDIS_URL = "redis://localhost:6379"
CACHE_REDIS_URL = REDIS_URL

# Core of flask-security
SECURITY_PASSWORD_SALT = '234'  # HMAC salt
# Feature flags of flask-security
SECURITY_CONFIRMABLE = True     # users are required to confirm their email address when registering a new account.
SECURITY_REGISTERABLE = True    # should create a user registration endpoint.
SECURITY_RECOVERABLE = True     # should create a password reset/recover endpoint.
SECURITY_TRACKABLE = True       # should track basic user login statistics.
SECURITY_CHANGEABLE = True      # should enable the change password endpoint.
# URLs and Views of flask-security
SECURITY_POST_REGISTER_VIEW = 'online.landing'  # the view to redirect to after a user successfully registers.
SECURITY_POST_CONFIRM_VIEW = 'online.landing'   # the view to redirect to after a user successfully confirms their email.
SECURITY_POST_RESET_VIEW = 'online.landing'     # the view to redirect to after a user successfully resets their password..


if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

try:
    from local_settings import *    # noqa
except ImportError:
    pass
