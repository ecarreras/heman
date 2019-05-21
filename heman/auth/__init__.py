from __future__ import absolute_import
from functools import wraps

from flask import current_app
from flask.ext import login
from flask.ext.login import current_user

from heman.config import mongo


login_manager = login.LoginManager()
"""Login manager object
"""


def check_contract_allowed(func):
    """Check if Contract is allowed by token
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        contract = kwargs.get('contract')
        if (contract and current_user.is_authenticated()
                and not current_user.allowed(contract)):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorator


def check_cups_allowed(func):
    """Check if CUPS is allowd by token
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        cups = kwargs.get('cups')
        if (cups and current_user.is_authenticated()
                and not current_user.allowed(cups, 'cups')):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorator


def get_perm(contract, perm):
    return current_user.perm(contract, perm)


class APIUser(login.UserMixin):
    """API User object

    :param token: token for this user
    """
    def __init__(self, token, allowed):
        self.id = token
        self.allowed_contracts = allowed

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id

    def allowed(self, value, key='name'):
        return value in [x[key] for x in self.allowed_contracts]

    def perm(self, contract, key='onlycch'):
        for x in self.allowed_contracts:
            if x['name'] == contract:
                return x.get(key, False)

        return False


@login_manager.header_loader
def load_user_from_header(header_val):
    header_val = header_val.replace('Basic ', '', 1)
    try:
        user, token = header_val.split()
        if user == 'token':
            res = mongo.db.tokens.find({'token': token})
            if res:
                res = res[0]
                return APIUser(res['token'], res.get('allowed_contracts', []))
    except Exception:
        return None


@login_manager.user_loader
def load_user(token):
    return APIUser(token)
