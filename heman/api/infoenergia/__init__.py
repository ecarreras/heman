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

    def get_last_infoenergia_report(self, contract_name):
        return mongo.db['infoenergia_reports'].find_one(
            {'contractId': contract_name},
            sort=[('months', pymongo.ASCENDING)]
        )


class InfoenergiaReport(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug('Infoenergia Report, contract {}'.format(contract))

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        if infoenergia_report:
            return Response(json.dumps(infoenergia_report), mimetype='application/json')

        return Response({}, mimetype='application/json')


class SeasonalProfile(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug(
            'SeasonalProfile from Infoenergia Report, contract {}'.format(contract)
        )

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        have_results = infoenergia_report and \
            infoenergia_report.get('results', {}).get('seasonalProfile')
        if have_results:
            return Response(
                json.dumps(infoenergia_report['results']['seasonalProfile']),
                mimetype='application/json'
            )

        return Response({}, mimetype='application/json')


class DistributionByPeriod(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug(
            'DistributionByPeriod from Infoenergia Report, contract {}'.format(contract)
        )

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        have_results = infoenergia_report and \
            infoenergia_report.get('results', {}).get('distributionByPeriods')
        if have_results:
            return Response(
                json.dumps(infoenergia_report['results']['distributionByPeriods']),
                mimetype='application/json'
            )

        return Response({}, mimetype='application/json')


class DistributionByTypeOfUse(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug(
            'DistributionByTypeOfUse from Infoenergia Report, contract {}'.format(contract)
        )

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        have_results = infoenergia_report and \
            infoenergia_report.get('results', {}).get('distributionByTypeOfUse')
        if have_results:
            return Response(
                json.dumps(infoenergia_report['results']['distributionByTypeOfUse']),
                mimetype='application/json'
            )

        return Response({}, mimetype='application/json')


class DailyProfile(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug(
            'DailyProfile from Infoenergia Report, contract {}'.format(contract)
        )

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        have_results = infoenergia_report and \
            infoenergia_report.get('results', {}).get('dailyTypicalProfileLast12Months')
        if have_results:
            return Response(
                json.dumps(infoenergia_report['results']['dailyTypicalProfileLast12Months']),
                mimetype='application/json'
            )

        return Response({}, mimetype='application/json')


class WeeklyProfile(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug(
            'WeeklyProfile from Infoenergia Report, contract {}'.format(contract)
        )

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        have_results = infoenergia_report and \
            infoenergia_report.get('results', {}).get('weeklyAvgConsumeLast3Months')
        if have_results:
            return Response(
                json.dumps(infoenergia_report['results']['weeklyAvgConsumeLast3Months']),
                mimetype='application/json'
            )

        return Response({}, mimetype='application/json')


class MonthsProfile(InfoenergiaResource):

    def get(self, contract):
        current_app.logger.debug(
            'MonthsProfile from Infoenergia Report, contract {}'.format(contract)
        )

        infoenergia_report = self.get_last_infoenergia_report(contract_name=contract)

        have_results = infoenergia_report and \
            infoenergia_report.get('results', {}).get('last3MonthsProfile')
        if have_results:
            return Response(
                json.dumps(infoenergia_report['results']['last3MonthsProfile']),
                mimetype='application/json'
            )

        return Response({}, mimetype='application/json')


resources = [
    (InfoenergiaReport, '/InfoenergiaReport/<contract>'),
    (SeasonalProfile, '/InfoenergiaReport/data/seasonalprofile/<contract>'),
    (DistributionByPeriod, '/InfoenergiaReport/data/distributionbyperiod/<contract>'),
    (DistributionByTypeOfUse, '/InfoenergiaReport/data/distributionbytypeofuse/<contract>'),
    (DailyProfile, '/InfoenergiaReport/data/dailyprofile/<contract>'),
    (WeeklyProfile, '/InfoenergiaReport/data/weeklyprofile/<contract>'),
    (MonthsProfile, '/InfoenergiaReport/data/monthsprofile/<contract>'),
]
