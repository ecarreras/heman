from functools import wraps

from flask import current_app
from flask.ext.login import current_user

from heman.api import AuthorizedResource


def check_contract_allowed(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        contract = kwargs.get('contract')
        if contract and not current_user.allowed(contract):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorator


class EmpoweringResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )
