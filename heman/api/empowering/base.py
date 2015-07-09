from functools import wraps

from flask import current_app, jsonify
from flask.ext.login import current_user

from heman.api import AuthorizedResource


def check_contract_allowed(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        contract = kwargs.get('contract')
        if (contract and current_user.is_authenticated()
                and not current_user.allowed(contract)):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorator


class EmpoweringResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )

    def options(self, *args, **kwargs):
        return jsonify({})
