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

    """Given some parameter values chooses the matching scenario with least payback
    """

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
                mimetype='application/json',
            )

        bestScenario = min(
            selectedScenarios,
            key=lambda s: s['economics']['payback'],
        )

        result = dict(
            loadKwhYear = totalLoad,
            loadByPeriodKwh = scenario_report['results']['pvAutoSize']['load']['timeslots'],
            productionKwhYear = bestScenario['generation']['total'],
            productionToLoadKwhYear = bestScenario['generation']['PVtoLoad'],
            productionToLoadEuroYear = bestScenario['generation']['PVtoLoadCost'],
            productionToLoadPercent = bestScenario['generation']['PVtoLoadPct'],
            productionToGridKwhYear = bestScenario['generation']['PVtoGrid'],
            productionToGridEuroYear = bestScenario['generation']['PVtoGridCost'],
            productionToGridPercent = bestScenario['generation']['PVtoGridPct'],
            loadFromGridKwhYear = bestScenario['generation']['loadFromGrid'],
            savingsEuroYear = bestScenario['generation']['savings'],
            paybackYears = bestScenario['economics']['payback'],
            installationCostEuro = bestScenario['settings']['cost'],
            azimuthDegrees= bestScenario['settings']['azimuth'],
            tiltDegrees= bestScenario['settings']['tilt'],
            areaM2 = bestScenario['settings']['area'],
            nModules = bestScenario['settings']['numModules'],
            totalPower = bestScenario['settings']['power'],
            dailyLoadProfileKwh = scenario_report['results']['pvAutoSize']['load']['profile'],
            dailyProductionProfileKwh = bestScenario['generation']['profile'],
        )

        return Response(json.dumps(result), mimetype='application/json')


class ScenarioParams(PVCalculatorResource):

    """Returns the parameters available values to choose scenario"""

    def get(self, contract):

        scenario_report = self.get_last_scenario(contract_name=contract)
        if not scenario_report:
            return Response({}, mimetype='application/json')
        
        try:
            scenarios = scenario_report['results']['pvAutoSize']['scenarios']
        except KeyError as e:
            print("Error {}", e)
            return Response({}, mimetype='application/json')
        except IndexError as e:
            print("Error {}", e)
            return Response({}, mimetype='application/json')

        tilts, azimuths, powers = zip(*[
            (
            scenario['settings']['tilt'],
            scenario['settings']['azimuth'],
            scenario['settings']['power'],
            )
            for i,scenario in enumerate(scenarios)
        ])
        result = dict(
            tilt = list(sorted(set(tilts))),
            azimuth = list(sorted(set(azimuths))),
            power = list(sorted(set(powers))),
        )
        return Response(json.dumps(result), mimetype='application/json')


resources = [
    (ScenarioReport, '/ScenarioReport/<contract>'),
    (ScenarioParams, '/ScenarioParams/<contract>'),

]
