from __future__ import absolute_import

from flask.ext import restful, login, cors


class HemanAPI(restful.Api):
    pass


class AuthorizedResource(restful.Resource):
    method_decorators = [login.login_required, cors.cross_origin()]


class ApiCatchall(restful.Resource):
    def get(self, path):
        return {'status': 404, 'message': 'Not Found'}, 404

    post = get
    put = get
    delete = get
    patch = get
