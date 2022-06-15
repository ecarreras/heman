import json
import pymongo
import os
from flask import current_app
from flask_restful import request

from heman.api import AuthorizedResource
from heman.auth import check_contract_allowed
from heman.config import mongo


class PVCalculatorResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )

    def options(self, *args, **kwargs):
        return {}

    def get_last_scenario(self, contract_name):
        return mongo.db['photovoltaic_reports'].find_one(
            {'contractName': contract_name},
            sort=[('id', pymongo.DESCENDING)]
        )

def timeSerie(curve):
    if type(curve) == list:
        return curve
    return curve['values']

def parseMongoAzimuth(azimuth, gabledroof):
    """
    This function turns mongo representation of azimuth into a int tuple.
    Currently, Mongo objects represents azimuths either as a float like 120.0
    or as a string like "120#300" when it is a gabled roof.
    The first azimuth is always the one towards south or 90 if W-E orientation.
    TODO: change the mongo representation to be a more uniform one.
    """
    if not gabledroof:
        return (int(azimuth),)
    return (int(azimuth), int((azimuth+180) % 360))

def parseMongoAzimuthFromSettings(settings):
    if os.environ.get("BEEDATA_UNAGREED_API"):
        return parseMongoAzimuthFromSettings_unagreedVersion(settings)

    return parseMongoAzimuth(
        settings['azimuth'],
        settings['gabledroof']
    )

def parseMongoAzimuthFromSettings_unagreedVersion(settings):
    azimuth0 = int(settings['azimuth0'])
    try:
        azimuth1 = int(settings['azimuth1'])
    except ValueError:
        return (azimuth0,)
    return (azimuth0, azimuth1)

def parseTilt(settings):
    return float(settings['tilt'])

def parsePower(settings):
    return float(settings['power'])

def queryPeakPower(peakPower):
    if not peakPower: return None
    return float(peakPower)

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
        peakPowerKw = queryPeakPower(request.args.get('power'))

        scenario_report = self.get_last_scenario(contract_name=contract)

        if not scenario_report:
            return {}

        try:
            scenarios = scenario_report['results']['pvAutoSize']['scenarios']
            totalLoad = scenario_report['results']['pvAutoSize']['load']['total']
        except KeyError as e:
            print("Error {}", e)
            return {}
        except IndexError as e:
            print("Error {}", e)
            return {}

        selectedScenarios = [
            scenario
            for i,scenario in enumerate(scenarios)
            if parseTilt(scenario['settings']) == tiltDegrees
            and parseMongoAzimuthFromSettings(scenario['settings']) == azimuthDegrees
            and (parsePower(scenario['settings']) == peakPowerKw or not peakPowerKw)
        ]
        if not selectedScenarios:
            return dict(
                error='NOT_FOUND',
                message='Scenario not found',
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
            azimuthDegrees= parseMongoAzimuthFromSettings(bestScenario['settings']),
            tiltDegrees= parseTilt(bestScenario['settings']),
            areaM2 = bestScenario['settings']['area'],
            nModules = bestScenario['settings']['numModules'],
            peakPowerKw = parsePower(bestScenario['settings']['power']),
            dailyLoadProfileKwh = timeSerie(scenario_report['results']['pvAutoSize']['load']['profile']),
            dailyProductionProfileKwh = timeSerie(bestScenario['generation']['profile']),
            monthlyProductionToLoadKwh = timeSerie(bestScenario['generation']['monthlyPVtoLoad']),
            monthlyProductionToLoadEuro = timeSerie(bestScenario['generation']['monthlyPVtoLoadCost']),
            monthlyGridToLoadKwh = timeSerie(bestScenario['generation']['monthlyLoadFromGrid']),
            monthlyGridToLoadEuro = timeSerie(bestScenario['generation']['monthlyLoadFromGridCost']),
            monthlyProductionToGridKwh = timeSerie(bestScenario['generation']['monthlyPVtoGrid']),
            monthlyProductionToGridEuro = timeSerie(bestScenario['generation']['monthlyPVtoGridCost']),
            monthlyProductionKwh = timeSerie(bestScenario['generation']['monthlyPV']),
            #monthlyProductionEuro = bestScenario['generation']['monthlyPVCost'], # TODO: Info not yet available
        )

        return result


class ScenarioParams(PVCalculatorResource):

    """Returns the parameters available values to choose scenario"""

    def get(self, contract):

        scenario_report = self.get_last_scenario(contract_name=contract)
        if not scenario_report:
            return {}
        
        try:
            scenarios = scenario_report['results']['pvAutoSize']['scenarios']
        except KeyError as e:
            print("Error {}", e)
            return {}
        except IndexError as e:
            print("Error {}", e)
            return {}

        tilts, azimuths, powers = zip(*[
            (
            parseTilt(scenario['settings']),
            parseMongoAzimuthFromSettings(scenario['settings']),
            scenario['settings']['power'],
            )
            for i,scenario in enumerate(scenarios)
        ])
        result = dict(
            tilt = list(sorted(set(tilts))),
            azimuth = list(sorted(set(azimuths))),
            power = list(sorted(set(powers))),
        )
        return result


resources = [
    (ScenarioReport, '/ScenarioReport/<contract>'),
    (ScenarioParams, '/ScenarioParams/<contract>'),

]
