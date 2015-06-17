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

    configure_logging(app)
    configure_sentry(app)
    configure_api(app)
    configure_mongodb(app)

    return app


def configure_api(app):
    """Configure API Endpoints.
    """
    from heman.api.empowering.ot103 import OT103
    from heman.api import ApiCatchall

    api.add_resource(OT103, '/OT103Results/<contract>/<period>')
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
    logging.basicConfig()
    logging.getLogger().setLevel(getattr(logging, app.config['LOG_LEVEL']))
