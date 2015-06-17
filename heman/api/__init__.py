from __future__ import absolute_import

from flask.ext.restful import Api, Resource


class HemanAPI(Api):
    pass


class ApiCatchall(Resource):
    def get(self, path):
        return {'status': 404, 'message': 'Not Found'}, 404

    post = get
    put = get
    delete = get
    patch = get
