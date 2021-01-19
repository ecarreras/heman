import json
import pymongo

from flask import current_app, jsonify, Response

from heman.api import AuthorizedResource
from heman.auth import check_contract_allowed
from heman.config import mongo


class InfoenergiaResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )

    def options(self, *args, **kwargs):
        return jsonify({})


class InfoenergiaReport(InfoenergiaResource):

    def get_cursor_db(self, collection, query):

        return mongo.db[collection].find_one(
            query,
            sort=[('months', pymongo.ASCENDING)]
        )

    def get(self, contract):
        current_app.logger.debug('Infoenergia Report, contract {}'.format(contract))

        search_query = {
            'contractId': contract
        }
        infoenergia_report = self.get_last_report(collection='infoenergia_reports', query=search_query)

        if cursor_infoenergia:
            return Response(json.dumps(cursor_infoenergia), mimetype='application/json')

        return Response({}, mimetype='application/json')




resources = [
    (InfoenergiaReport, '/InfoenergiaReport/<contract>')
]
