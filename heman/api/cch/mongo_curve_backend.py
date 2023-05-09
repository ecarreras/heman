from heman.config import mongo
from pymongo import ASCENDING, DESCENDING

from .datetimeutils import as_naive


class MongoCurveBackend:
    def __init__(self, mongodb=None):
        self._mongodb = mongodb or mongo.db

    def get_cursor_db(self, collection, query):
        return self._mongodb[collection].find(
            query,
            fields={'_id': False, 'datetime': True, 'season': True, 'ai': True},
        ).sort([
            ('datetime', ASCENDING),
            # Sorting dupped times when changing from
            # summer (season=1) to winter (season=0)
            ('season', DESCENDING),
        ])

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        **extra_filter
    ):

        query = {
            'name': {'$regex': '^{}'.format(cups[:20])},
            # KLUDGE: datetime is naive but is stored in mongo as UTC,
            # if we pass dates as local, we will be comparing to the equivalent
            # UTC date which is wrong, so we remove the timezone to make them naive
            'datetime': {'$gte': as_naive(start), '$lt': as_naive(end)}
        }

        return query

    def get_curve(self, curve_type, start, end, cups=None):
        query = self.build_query(start, end, cups, **curve_type.extra_filter)

        result = self.get_cursor_db(curve_type.model, query)

        for x in result:
            yield dict(x, ai=float(x['ai']))

