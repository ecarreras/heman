from flask import current_app, jsonify
from amoniak.caching import OT201Caching

from heman.config import mongo
from heman.api.empowering import service
from heman.api.empowering.base import EmpoweringResource


class OT201(EmpoweringResource):
    def get(self, contract, period):
        ot201 = OT201Caching(service, mongo.db)
        result = ot201.get_cached(contract, period)
        if not result.get('_items'):
            current_app.logger.debug(
                'No cached result for contract %s and period %s',
                contract, period
            )
        return jsonify(result)
