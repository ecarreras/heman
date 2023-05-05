from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import time

from flask import current_app, jsonify, request, Response
from pymongo import ASCENDING

from heman.api import AuthorizedResource
from heman.auth import check_cups_allowed
from heman.config import mongo

from .mongo_curve_backend import MongoCurveBackend
from .timescale_curve_backend import TimescaleCurveBackend


class CurveRepository:
    extra_filter = dict()

    def __init__(self, backend):
        self.backend = backend

    def get_curve(self, start, end, cups=None):
        return self.backend.get_curve(self, start, end, cups)


class TgCchF5dRepository(CurveRepository):
    model = 'tg_cchfact'


class TgCchF1Repository(CurveRepository):
    model = 'tg_f1'


class TgCchP1Repository(CurveRepository):
    model = 'tg_p1'


class CCHResource(AuthorizedResource):
    method_decorators = (
            AuthorizedResource.method_decorators + [check_cups_allowed]
    )

    def options(self, *args, **kwargs):
        return jsonify({})


WATT = 'W'
KILOWATT = 'kW'
P1_CURVE_TYPE = 'p'


class CCHFact(CCHResource):

    def get_cursor_db(self, collection, query):
        return mongo.db[collection].find(
            query,
            fields={'_id': False, 'datetime': True, 'ai': True}).sort(
            'datetime', ASCENDING
        )

    def _curve_value(self, curve, unit):
        return {
            'date': time.mktime((curve['datetime']).timetuple()) * 1000,
            'value': curve['ai'] * 1000 if unit == KILOWATT else curve['ai']
        }

    def ordered_merge(self, cursor_f1, cursor_p1):
        curves = []
        f1_curve = next(cursor_f1, False)
        p1_curve = next(cursor_p1, False)
        while f1_curve and p1_curve:
            if f1_curve['datetime'] == p1_curve['datetime']:
                curves.append(self._curve_value(f1_curve, KILOWATT))
                f1_curve = next(cursor_f1, False)
                p1_curve = next(cursor_p1, False)
            elif f1_curve['datetime'] < p1_curve['datetime']:
                curves.append(self._curve_value(f1_curve, KILOWATT))
                f1_curve = next(cursor_f1, False)
            else:
                curves.append(self._curve_value(p1_curve, KILOWATT))
                p1_curve = next(cursor_p1, False)

        while f1_curve:
            curves.append(self._curve_value(f1_curve, KILOWATT))
            f1_curve = next(cursor_f1, False)
        while p1_curve:
            curves.append(self._curve_value(p1_curve, KILOWATT))
            p1_curve = next(cursor_p1, False)

        return curves

    def _query_result_length(self, result):
        return result.count()

    def get(self, cups, period):
        interval = request.args.get('interval')
        try:
            interval = max(min(int(interval), 12), 1)
        except:
            interval = 12
        end = datetime.strptime(period, '%Y%m') + relativedelta(months=1)
        start = end - relativedelta(months=interval)

        current_app.logger.debug('CCH from {} to {}'.format(start, end))

        result = []
        cursor_f5d = self.get_curve('tg_cchfact', start, end, cups)
        result = [self._curve_value(curve, WATT) for curve in cursor_f5d]
        if result:
            return Response(json.dumps(result), mimetype='application/json')

        cursor_f1 = self.get_curve_old('tg_f1', start, end, cups)
        cursor_p1 = self.get_curve_old('tg_p1', start, end, cups)
        result = self.ordered_merge(cursor_f1, cursor_p1)

        return Response(json.dumps(result), mimetype='application/json')

    def get_curve_old(self, curve_type, start, end, cups):
        search_query = {
            'name': {'$regex': '^{}'.format(cups[:20])},
            'datetime': {'$gte': start, '$lt': end}
        }
        if curve_type == 'tg_p1':
            search_query.update(type = P1_CURVE_TYPE)

        cursor = self.get_cursor_db(collection=curve_type, query=search_query)
        return (x for x in cursor)

    def get_curve(self, curve_type, start, end, cups):
        repository = self.create_repository(curve_type)
        return repository.get_curve(start, end, cups=cups)

    def create_repository(self, curve_type):
        CurveType = curve_types[curve_type]
        # curve_type_backends = config.CURVE_TYPE_BACKENDS
        curve_type_backends = {
            'tg_cchfact': 'mongo',
            'tg_f1': 'mongo'
        }
        # backend_name = curve_type_backends.get(
        #     curve_type, config.CURVE_TYPE_DEFAULT_BACKEND
        # )
        backend_name = curve_type_backends.get(
            curve_type, 'mongo'
        )
        Backend = curve_backends[backend_name]
        return CurveType(Backend())


curve_types = {
    'tg_cchfact': TgCchF5dRepository,
    'tg_p1': TgCchP1Repository,
    'tg_f1': TgCchF1Repository,
}

curve_backends = dict(
    mongo=MongoCurveBackend,
    timescale=TimescaleCurveBackend,
)

resources = [
    (CCHFact, '/CCHFact/<cups>/<period>')
]
