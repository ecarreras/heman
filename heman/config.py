from __future__ import absolute_import
import logging
import os

from flask import Flask
from flask.ext.pymongo import PyMongo
from raven.contrib.flask import Sentry

from heman.api import HemanAPI


api = HemanAPI(prefix='/api')
sentry = Sentry(logging=True, level=logging.ERROR)
mongo = PyMongo()


def create_app(**config):
    """Create base application for HeMan.
    """
    app = Flask(
        __name__, static_folder=None
    )

    if 'MONGO_URI' in os.environ:
        app.config['MONGO_URI'] = os.environ['MONGO_URI']

    app.config['LOG_LEVEL'] = 'DEBUG'
    app.config['SECRET_KEY'] = '2205552d13b5431bb537732bbb051f1214414f5ab34d47'

    configure_logging(app)
    configure_sentry(app)
    configure_api(app)
    configure_mongodb(app)
    configure_login(app)

    return app


def configure_api(app):
    """Configure API Endpoints.
    """
    from heman.api.empowering import resources as empowering_resources
    from heman.api import ApiCatchall

    # Add Empowering resources
    for resource in empowering_resources:
        api.add_resource(*resource)
    api.add_resource(ApiCatchall, '/<path:path>')

    api.init_app(app)


def configure_sentry(app):
    """Configure Sentry logger.
    """
    sentry.init_app(app)


def configure_mongodb(app):
    """Configure MongoDB access.
    """
    mongo.init_app(app)


def configure_logging(app):
    logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))


def configure_login(app):
    from heman.auth import login_manager, login
    login_manager.init_app(app)

    @app.teardown_request
    def force_logout(*args, **kwargs):
        login.logout_user()
