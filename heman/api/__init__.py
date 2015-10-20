from __future__ import absolute_import

from flask import jsonify
from flask.ext import restful, login, cors


class HemanAPI(restful.Api):
    pass


class BaseResource(restful.Resource):
    """Base resource
    """
    def options(self, *args, **kwargs):
        return jsonify({})


class AuthorizedResource(BaseResource):
    """Autorized resource

    Base resource to inherit if the resource must be protected with auth
    """
    method_decorators = [login.login_required, cors.cross_origin()]


class ApiCatchall(BaseResource):
    def get(self, path):
        return jsonify({'status': 404, 'message': 'Not Found'}), 404

    post = get
    put = get
    delete = get
    patch = get
