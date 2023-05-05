from heman.config import mongo
from pymongo import ASCENDING


class MongoCurveBackend:
    def __init__(self, mongodb=None):
        self._mongodb = mongodb or mongo.db

    def get_cursor_db(self, collection, query):
        return self._mongodb[collection].find(
            query,
            fields={'_id': False, 'datetime': True, 'ai': True}).sort(
            'datetime', ASCENDING
        )

    def build_query(
        self,
        start=None,
        end=None,
        cups=None,
        **extra_filter
    ):

        query = {
            'name': {'$regex': '^{}'.format(cups[:20])},
            'datetime': {'$gte': start, '$lt': end}
        }

        return query

    def get_curve(self, curve_type, start, end, cups=None):
        query = self.build_query(start, end, cups, **curve_type.extra_filter)

        result = self.get_cursor_db(curve_type.model, query)

        return result
