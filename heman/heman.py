# -*- coding: utf-8 -*-
from amoniak.utils import setup_empowering_api


class HeMan(object):
    def __init__(self, app=None):
        """Initializized a HeMan object.
        """
        self.app = None
        self.empowering = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.set_defaults()
        self.empowering = setup_empowering_api(**self.app.config)

    def set_defaults(self):
        self.app.config.setdefault('HEMAN_PREFIX', '/heman')
