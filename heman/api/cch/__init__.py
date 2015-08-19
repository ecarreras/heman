from datetime import datetime
from dateutil.relativedelta import relativedelta
from functools import wraps
import json

from flask import current_app, jsonify, request, Response
from flask.ext.login import current_user

from heman.api import AuthorizedResource
from heman.config import mongo


def check_cups_allowed(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        cups = kwargs.get('cups')
        if (cups and current_user.is_authenticated()
                and not current_user.allowed(cups, 'cups')):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorator


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
        end = datetime.strptime(period, '%Y%m') + relativedelta(month=1)
        start = end - relativedelta(months=interval)
        res = mongo.db['tg_cchcons'].find({
            'name': cups,
            'datetime': {'$gte': start, '$lt': end}
        }, fields={'_id': False, 'datetime': True, 'ai': True})
        return Response(json.dumps(list(res)), mimetype='application/json')

resources = [
    (CCHFact, '/CCHFact/<cups>/<period>')
]
