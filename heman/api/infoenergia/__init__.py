from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import time

from flask import current_app, jsonify, request, Response
from pymongo import ASCENDING

from heman.api import AuthorizedResource
from heman.auth import check_contract_allowed
from heman.config import mongo

# https://infoenergia-api.somenergia.coop/api/InfoenergiaReport/ES0031406238503003AP0F

class InfoenergiaResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )

    def options(self, *args, **kwargs):
        return jsonify({})


class InfoenergiaReport(InfoenergiaResource):

    def get_cursor_db(self, collection, query, limit):

        return mongo.db[collection].find(
            query,
            {'_items': 1}
        ).limit(limit)

    def get(self, contract):
        current_app.logger.debug('Infoenergia Report, contract {}'.format(contract))

        search_query = {
            '_items.0.contractId': contract
        }

        cursor_infoenergia = self.get_cursor_db(collection='infoenergia_reports', query=search_query, limit=1)

        res = []
        if cursor_infoenergia.count() > 0:
            for report in cursor_infoenergia:
                res.append(report['_items'])

        return Response(json.dumps(res), mimetype='application/json')


resources = [
    (InfoenergiaReport, '/InfoenergiaReport/<contract>')
]
