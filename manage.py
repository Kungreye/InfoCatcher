#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import sys

import IPython
from IPython.terminal.ipapp import load_default_config
from traitlets.config.loader import Config
from flask.cli import with_appcontext, click
from flask_migrate import Migrate

from app import app
from ext import db
from corelib.db import rdb


def include_object(object, name, type_, reflected, compare_to):
    if type_ == 'table' and name.startswith('social_auth'):
        return False
    return True


migrate = Migrate(app, db, include_object=include_object)


from models.core import Post, Tag, PostTag
from models.comment import CommentItem
from models.collect import CollectItem
from models.like import LikeItem
from models.user import User, Role, user_datastore
from models.search import Item
from models.contact import Contact, userFollowStats


@app.cli.command()
def initdb():
    """Initialize database."""
    from social_flask_sqlalchemy import models as models_
    engine = db.get_engine()
    models_.PSABase.metadata.drop_all(engine)   # PSABase = declarative_base()
    db.session.commit()
    db.drop_all()
    db.create_all()
    models_.PSABase.metadata.create_all(engine)
    click.echo('Init finished!')


@app.cli.command('ishell', short_help='Runs a IPython shell in the app context.')
@click.argument('ipython_args', nargs=-1, type=click.UNPROCESSED)
@with_appcontext    # wraps a callback so that it's guaranteed to be executed with the script's application context.
def ishell(ipython_args):
    if 'IPYTHON_CONFIG' in app.config:
        config = Config(app.config['IPYTHON_CONFIG'])
    else:
        config = load_default_config()

    user_ns = app.make_shell_context()
    user_ns.update(dict(db=db, User=User, Role=Role, rdb=rdb, Post=Post,
                        Tag=Tag, PostTag=PostTag, Item=Item, Contact=Contact,
                        userFollowStats=userFollowStats))
    config.TerminalInteractiveShell.banner1 = """Python %s on %s
IPython: %s
App: %s%s
Instance: %s""" % (sys.version,
                   sys.platform,
                   IPython.__version__,
                   app.import_name,
                   app.debug and ' [debug]' or '',
                   app.instance_path)

    IPython.start_ipython(argv=ipython_args, user_ns=user_ns, config=config)


@app.cli.command()
@with_appcontext
def create_social_db():
    from social_flask_sqlalchemy import models as models_
    engine = db.get_engine()
    models_.PSABase.metadata.drop_all(engine)
    models_.PSABase.metadata.create_all(engine)
    click.echo('Create social DB finished!')
