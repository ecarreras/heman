from __future__ import absolute_import
import logging
import os

from flask import Flask
from flask.ext.pymongo import PyMongo
from raven.contrib.flask import Sentry

from heman.api import HemanAPI


api = HemanAPI(prefix='/api')
"""API object
"""
sentry = Sentry(logging=True, level=logging.ERROR)
"""Sentry object
"""
mongo = PyMongo()
"""Access to database

In other parts of the application you can do::

    from heman.config import mongo

    mongo.db.collection.find({"foo": "bar"})
"""


def create_app(**config):
    """Application Factory

    You can create a new He-Man application with::

        from heman.config import create_app

        app = create_app() # app can be uses as WSGI application
        app.run() # Or you can run as a simple web server
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
    from heman.api.cch import resources as cch_resources
    from heman.api import ApiCatchall

    # Add Empowering resources
    for resource in empowering_resources:
        api.add_resource(*resource)

    # Add CCHFact resources
    for resource in cch_resources:
        api.add_resource(*resource)

    api.add_resource(ApiCatchall, '/<path:path>')
    api.init_app(app)


def configure_sentry(app):
    """Configure Sentry logger.

    Uses `Raven
    <http://raven.readthedocs.org/en/latest/integrations/flask.html>`_
    """
    sentry.init_app(app)


def configure_mongodb(app):
    """Configure MongoDB access.

    Uses `Flask-PyMongo <https://flask-pymongo.readthedocs.org/>`_
    """
    mongo.init_app(app)


def configure_logging(app):
    """Configure logging

    Call ``logging.basicConfig()`` with the level ``LOG_LEVEL`` of application.
    """
    logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))


def configure_login(app):
    """Configure login authentification

    Uses `Flask-Login <https://flask-login.readthedocs.org>`_
    """
    from heman.auth import login_manager, login
    login_manager.init_app(app)

    @app.teardown_request
    def force_logout(*args, **kwargs):
        login.logout_user()
