from flask import current_app
from amoniak.caching import OT103Caching

from heman.config import mongo
from heman.api.empowering import service, EmpoweringResource


class OT103(EmpoweringResource):
    def get(self, contract, period):
        ot103 = OT103Caching(service, mongo.db)
        result = ot103.get_cached(contract, period)
        if not result.get('_items'):
            current_app.logger.debug(
                'No cached result for contract %s and period %s',
                contract, period
            )
