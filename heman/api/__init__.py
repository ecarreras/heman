from __future__ import absolute_import

from flask import jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from flask_login import login_required

class HemanAPI(Api):
    pass


class BaseResource(Resource):
    """Base resource
    """
    def options(self, *args, **kwargs):
        return jsonify({})


class AuthorizedResource(BaseResource):
    """Autorized resource

    Base resource to inherit if the resource must be protected with auth
    """
    method_decorators = [login_required, cross_origin()]


class ApiCatchall(BaseResource):
    def get(self, path):
        return jsonify({'status': 404, 'message': 'Not Found'}), 404

    post = get
    put = get
    delete = get
    patch = get
