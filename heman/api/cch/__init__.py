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
        cursor = mongo.db['tg_cchfact'].find(
            search_query,
            fields={'_id': False, 'datetime': True, 'ai': True}).sort(
            'datetime', ASCENDING
        )
        # Forcing local timezone

        for item in cursor:
            dt = item['datetime']
            dt_tuple = datetime(dt.year, dt.month, dt.day, dt.hour).timetuple()
            res.append({
                # Unix timestamp in Javascript is python * 1000
                'date': time.mktime(dt_tuple) * 1000,
                'value': item['ai']
            })
        return Response(json.dumps(res), mimetype='application/json')


resources = [
    (CCHFact, '/CCHFact/<cups>/<period>')
]
