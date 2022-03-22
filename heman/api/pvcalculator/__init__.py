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


def parseMongoAzimuth(azimuth):
    """
    This function turns mongo representation of azimuth into a int tuple.
    Currently, Mongo objects represents azimuths either as a float like 120.0
    or as a string like "120#300" when it is a gabled roof.
    The first azimuth is always the one towards south or 90 if W-E orientation.
    TODO: change the mongo representation to be a more uniform one.
    """
    if type(azimuth) is float:
        return (int(azimuth),)
    return tuple(int(a) for a in azimuth.split('#'))

def queryAzimuth(queryAzimuth):
    """
    This turns a list of strings representing the azimuths into
    a hashable tuple of ints.
    """
    return tuple(int(a) for a in queryAzimuth)

class ScenarioReport(PVCalculatorResource):

    """Given some parameter values chooses the matching scenario with least payback
    """

    def get(self, contract):
        current_app.logger.debug('PVCalculator Report, contract {}'.format(contract))

        tiltDegrees = float(request.args.get('tilt'))
        azimuthDegrees = queryAzimuth(request.args.getlist('azimuth'))
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
            and parseMongoAzimuth(scenario['settings']['azimuth']) == azimuthDegrees
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
            azimuthDegrees= parseMongoAzimuth(bestScenario['settings']['azimuth']),
            tiltDegrees= bestScenario['settings']['tilt'],
            areaM2 = bestScenario['settings']['area'],
            nModules = bestScenario['settings']['numModules'],
            totalPower = bestScenario['settings']['power'],
            dailyLoadProfileKwh = scenario_report['results']['pvAutoSize']['load']['profile'],
            dailyProductionProfileKwh = bestScenario['generation']['profile'],
            monthlyProductionToLoadKwh = bestScenario['generation']['monthlyPVtoLoad'],
            monthlyProductionToLoadEuro = bestScenario['generation']['monthlyPVtoLoadCost'],
            monthlyGridToLoadKwh = bestScenario['generation']['monthlyLoadFromGrid'],
            monthlyGridToLoadEuro = bestScenario['generation']['monthlyLoadFromGridCost'],
            monthlyProductionToGridKwh = bestScenario['generation']['monthlyPVtoGrid'],
            monthlyProductionToGridEuro = bestScenario['generation']['monthlyPVtoGridCost'],
            monthlyProductionKwh = bestScenario['generation']['monthlyPV'],
            #monthlyProductionEuro = bestScenario['generation']['monthlyPVCost'], # TODO: Info not yet available
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
            parseMongoAzimuth(scenario['settings']['azimuth']),
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
