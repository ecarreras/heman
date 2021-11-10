import json
import pymongo

from flask import current_app, jsonify, Response
from flask_restful import request

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

        tiltDegrees = float(request.args.get('tilt'))
        azimuthDegrees = request.args.get('azimuth')
        powerKwh = request.args.get('power')

        scenario_report = self.get_last_scenario(contract_name=contract)

        if not scenario_report:
            return Response({}, mimetype='application/json')

        try:
            scenarios = scenario_report['results']['pvAutoSize']['scenarios']
            totalLoad = scenario_report['results']['pvAutoSize']['load']['total']
        except KeyError as e:
            print("Error {}", e)
            return Response({}, mimetype='application/json')
        except IndexError as e:
            print("Error {}", e)
            return Response({}, mimetype='application/json')

        selectedScenarios = [
            scenario
            for i,scenario in enumerate(scenarios)
            if scenario['settings']['tilt'] == tiltDegrees
            and scenario['settings']['azimuth'] == azimuthDegrees
            and (scenario['settings']['power'] == powerKwh or not powerKwh)
        ]
        if not selectedScenarios:
            return Response(
                json.dumps(dict(
                    error='NOT_FOUND',
                    message='Scenario not found',
                )),
                mimetype='application/json'
            )

        bestScenario = min(
            selectedScenarios,
            key=lambda s: s['economics']['payback'],
        )

        result = dict(
            loadKwhYear = totalLoad,
            productionKwhYear = bestScenario['generation']['total'],
            productionToLoadKwhYear = bestScenario['generation']['PVtoLoad'],
            productionToGridKwhYear = bestScenario['generation']['PVtoGrid'],
            savingsEuroYear = bestScenario['generation']['savings'],
            installationCostEuro = bestScenario['settings']['cost'],
            paybackYears = bestScenario['economics']['payback'],
        )

        return Response(json.dumps(result), mimetype='application/json')



resources = [
    (ScenarioReport, '/ScenarioReport/<contract>'),
]
