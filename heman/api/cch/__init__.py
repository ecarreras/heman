from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import time

from flask import current_app, jsonify, request, Response
from pymongo import ASCENDING

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

    def get_cursor_db(self, collection, query):
        return mongo.db[collection].find(
            query,
            fields={'_id': False, 'datetime': True, 'ai': True}).sort(
            'datetime', ASCENDING
        )

    def ordered_merge(self, cursor_f1, cursor_p1):
        res = []
        item_f1 = next(cursor_f1, False)
        item_p1 = next(cursor_p1, False)
        while item_f1 and item_p1:
            if item_f1['datetime'] == item_p1['datetime']:
                res.append({
                    'date': time.mktime((item_f1['datetime']).timetuple()) * 1000,
                    'value': (item_f1['ai'])
                })
                item_f1 = next(cursor_f1, False)
                item_p1 = next(cursor_p1, False)
            elif item_f1['datetime'] < item_p1['datetime']:
                res.append({
                    'date': time.mktime((item_f1['datetime']).timetuple()) * 1000,
                    'value': item_f1['ai']
                })
                item_f1 = next(cursor_f1, False)
            else:
                res.append({
                    'date': time.mktime((item_p1['datetime']).timetuple()) * 1000,
                    'value': item_p1['ai']
                })
                item_p1 = next(cursor_p1, False)

        while item_f1:
            res.append({
                'date': time.mktime((item_f1['datetime']).timetuple()) * 1000,
                'value': item_f1['ai']
            })
            item_f1 = next(cursor_f1, False)
        while item_p1:
            res.append({
                'date': time.mktime((item_p1['datetime']).timetuple()) * 1000,
                'value': item_p1['ai']
            })
            item_p1 = next(cursor_p1, False)
        return res

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
            res = self.ordered_merge(cursor_f1, cursor_p1)

        return Response(json.dumps(res), mimetype='application/json')


resources = [
    (CCHFact, '/CCHFact/<cups>/<period>')
]
