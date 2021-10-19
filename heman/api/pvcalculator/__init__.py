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

        if not scenario_report:
            return Response({}, mimetype='application/json')

        try:
            scenario = scenario_report['results']['pvAutoSize']['scenarios'][-1]
            totalLoad = scenario_report['results']['pvAutoSize']['load']['total']
        except KeyError as e:
            print("Error {}", e)
            return Response({}, mimetype='application/json')
        except IndexError as e:
            print("Error {}", e)
            return Response({}, mimetype='application/json')

        """
        [
            (
                abs(power - scenario['settings']['power']),
                abs()

            for i,scenario in itemize(scenario_report['results']['pvAutoSize']['scenarios'])
        ]
        """
        result = dict(
            loadKwhYear = totalLoad,
            productionKwhYear = scenario['generation']['total'],
            productionToLoadKwhYear = scenario['generation']['PVtoLoad'],
            productionToGridKwhYear = scenario['generation']['PVtoGrid'],
            savingsEuroYear = scenario['generation']['savings'],
            installationCostEuro = scenario['settings']['cost'],
            paybackYears = scenario['economics']['payback'],
        )

        return Response(json.dumps(result), mimetype='application/json')



resources = [
    (ScenarioReport, '/ScenarioReport/<contract>'),
]
