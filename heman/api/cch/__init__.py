from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import time

from flask import current_app, jsonify, request, Response
from flask.ext.pymongo import ASCENDING

from heman.api import AuthorizedResource
from heman.auth import check_cups_allowed
from heman.config import mongo


class CCHResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_cups_allowed]
    )

    def options(self, *args, **kwargs):
        return jsonify({})


class CCHFact(CCHResource):

    def dict_to_array_curves(curves_dict):
        curves = []
        for _datetime, consumption in curves_dict.items():
            dt = _datetime
            dt_tuple = datetime(dt.year, dt.month, dt.day, dt.hour).timetuple()
            curves.append({
                'date': time.mktime(dt_tuple) * 1000, # ?? *1000 ?
                'value': consumption
            })
        return curves

    def merge_curves(_datetimes, f1_curves, p1_curves):
        curves = []
        for _datetime in _datetimes:
            dt = curve['datetime']
            dt_tuple = datetime(dt.year, dt.month, dt.day, dt.hour).timetuple()
            if f1_curves.get(_datetime, False):
                value = f1_curves.get(_datetime)
            else:
                value = p1_curves.get(_datetime)
            curves.append({
                'date': time.mktime(dt_tuple) * 1000, # ?? *1000 ?
                'value': value
            })
        return curves

    def get_cursor_db(self, collection, query):
        return mongo.db[collection].find(
            query,
            fields={'_id': False, 'datetime': True, 'ai': True}).sort(
            'datetime', ASCENDING
        )

    def get(self, cups, period):
        interval = request.args.get('interval')
        try:
            interval = max(min(int(interval), 12), 1)
        except:
            interval = 12
        end = datetime.strptime(period, '%Y%m') + relativedelta(months=1)
        start = end - relativedelta(months=interval)
        res = []
        current_app.logger.debug('CCH from {} to {}'.format(start, end))
        search_query = {
            'name': {'$regex': '^{}'.format(cups[:20])},
            'datetime': {'$gte': start, '$lt': end}
        }
        p1_search_query = {
            'name': {'$regex': '^{}'.format(cups[:20])},
            'datetime': {'$gte': start, '$lt': end},
            'type': 'p'
        }
        cursor_f5d = self.get_cursor_db(collection='tg_cchfact', query=search_query)
        cursor_f1 = self.get_cursor_db(collection='tg_f1', query=search_query)
        cursor_p1 = self.get_cursor_db(collection='tg_p1', query=p1_search_query)

        # Forcing local timezone
        if cursor_f5d.count() > 0:
            for item in cursor_f5d:
                dt = item['datetime']
                dt_tuple = datetime(dt.year, dt.month, dt.day, dt.hour).timetuple()
                res.append({
                    # Unix timestamp in Javascript is python * 1000
                    'date': time.mktime(dt_tuple) * 1000,
                    'value': item['ai']
                })
        elif cursor_f1.count() > 0 or cursor_p1.count() > 0:
            f1_curves = {}
            p1_curves = {}
            _datetimes = set()
            contador = 0
            for curve in cursor_f1:
                f1_curves[curve['datetime']] = curve['ai']
                _datetimes.add(curve['datetime'])
            for curve in cursor_p1:
                p1_curves[curve['datetime']] = curve['ai']
                _datetimes.add(curve['datetime'])

            if len(_datetimes) == len(f1_curves):
                res = self.dict_to_array_curves(f1_curves)
            else:
                res = self.merge_curves(_datetimes, f1_curves, p1_curves)

        return Response(json.dumps(res), mimetype='application/json')


resources = [
    (CCHFact, '/CCHFact/<cups>/<period>')
]
