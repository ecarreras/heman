import json
import pymongo

from flask import current_app, jsonify, Response

from heman.api import AuthorizedResource
from heman.auth import check_contract_allowed
from heman.config import mongo


class PVCalculatorResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )

    def options(self, *args, **kwargs):
        return jsonify({})

    def get_last_scenario(self, contract_name):
        return mongo.db['photovoltaic_reports'].find_one(
            {'contractName': contract_name},
            sort=[('id', pymongo.DESCENDING)]
        )


class ScenarioReport(PVCalculatorResource):

    def get(self, contract):
        current_app.logger.debug('PVCalculator Report, contract {}'.format(contract))

        scenario_report = self.get_last_scenario(contract_name=contract)

        if scenario_report:
            return Response(json.dumps(scenario_report), mimetype='application/json')

        return Response({}, mimetype='application/json')


resources = [
    (ScenarioReport, '/ScenarioReport/<contract>'),
]
