from __future__ import absolute_import

from flask.ext import login

from heman.config import mongo


login_manager = login.LoginManager()
"""Login manager object
"""


class APIUser(login.UserMixin):
    """API User object

    :param token: token for this user
    """
    def __init__(self, token):
        self.token = token

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.token


@login_manager.header_loader
def load_user_from_header(header_val):
    header_val = header_val.replace('Basic ', '', 1)
    try:
        user, token = header_val.split()
        if user == 'token':
            if mongo.db.tokens.find({'token': token}).count():
                return APIUser(token)
    except ValueError:
        return None


@login_manager.user_loader
def load_user(token):
    return APIUser(token)
