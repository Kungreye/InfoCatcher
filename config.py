# _*_ coding: utf-8 _*_

import os

HERE = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(HERE, 'permdir')


SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess-this')
TEMPLATES_AUTO_RELOAD = True


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
SECURITY_POST_REGISTER_VIEW = 'account.landing'  # the view to redirect to after a user successfully registers.
SECURITY_POST_CONFIRM_VIEW = 'account.landing'   # the view to redirect to after a user successfully confirms their email.
SECURITY_POST_RESET_VIEW = 'account.landing'     # the view to redirect to after a user successfully resets their password..

SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome - InfoCatcher'
SECURITY_EMAIL_SUBJECT_CONFIRM = 'Please confirm your email - InfoCatcher'
SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = 'Password reset instructions - InfoCatcher'
SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = 'Your password has been reset - InfoCatcher'
SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = 'Your password has been changed - InfoCatcher'

SECURITY_MSG_ALREADY_CONFIRMED = ('Your email has already been confirmed.', 'info')
SECURITY_MSG_CONFIRMATION_REQUIRED = ('Email requires confirmation.', 'error')
SECURITY_MSG_DISABLED_ACCOUNT = ('Account is disabled.', 'error')
SECURITY_MSG_EMAIL_ALREADY_CONFIRMED = ('%(email)s is already associated with an account.', 'error')
SECURITY_MSG_EMAIL_NOT_PROVIDED = ('Email not provided', 'error')
SECURITY_MSG_INVALID_EMAIL_ADDRESS = ('Invalid email address', 'error')
SECURITY_MSG_INVALID_PASSWORD = ('Invalid password', 'error')
SECURITY_MSG_PASSWORD_INVALID_LENGTH = ('Password length is invalid', 'error')
SECURITY_MSG_PASSWORD_IS_THE_SAME = ('Your new password must be different than your previous password.', 'error')
SECURITY_MSG_PASSWORD_MISMATCH = ('Password does not match', 'error')
SECURITY_MSG_PASSWORD_NOT_PROVIDED = ('Password not provided', 'error')
SECURITY_MSG_PASSWORD_RESET_EXPIRED = ('You did not reset your password within %(within)s. ''New instructions have been sent to %(email)s.', 'error')
SECURITY_MSG_RETYPE_PASSWORD_MISMATCH = ('Passwords do not match', 'error')
SECURITY_MSG_UNAUTHORIZED = ('You do not have permission to view this resource.', 'error')
SECURITY_MSG_USER_DOES_NOT_EXIST = ('Specified user does not exist', 'error')

SECURITY_CONFIRM_EMAIL_WITHIN = SECURITY_RESET_PASSWORD_WITHIN = '6 hours'
SECURITY_USER_IDENTITY_ATTRIBUTES = ('email', 'name')


SOCIAL_AUTH_USER_MODEL = 'models.user.User'
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.weibo.WeiboOAuth2',
    'social_core.backends.weixin.WeixinOAuth2'
)

SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''
SOCIAL_AUTH_WEIBO_KEY = ''
SOCIAL_AUTH_WEIBO_SECRET = ''
SOCIAL_AUTH_WEIBO_DOMAIN_AS_USERNAME = True
SOCIAL_AUTH_WEIXIN_KEY = ''
SOCIAL_AUTH_WEIXIN_SECRET = ''
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
CLEAN_USERNAMES = False
SOCIAL_AUTH_REMEMBER_SESSION_NAME = 'remember_me'
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['keep']


MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT') or '25'  # when used, remember to int(MAIL_PORT)
MAIL_USE_SSL = True if (os.getenv('MAIL_USE_SSL') is not None) else False
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = ('InfoCatcher', MAIL_USERNAME)


# elasticsearch config
ES_HOSTS = ['localhost']
PER_PAGE = 2


# celery config
BROKER_URL = 'amqp://kungreye:123456@localhost:5672/InfoCatcher'  # use RabbitMQ as celery broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
CELERY_ACCEPT_CONTENT = ['msgpack', 'json']


if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

try:
    from local_settings import *    # noqa
except ImportError:
    pass
