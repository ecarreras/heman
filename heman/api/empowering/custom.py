from flask import jsonify
from amoniak.caching import AVALIABLE_ONLINE_TOOLS

from heman.config import mongo
from heman.api.empowering.base import EmpoweringResource


class PeriodRange(EmpoweringResource):
    def get(self, contract):
        existing_collections = mongo.db.collection_names(False)
        result = {'max': None, 'min': None}
        for collection in AVALIABLE_ONLINE_TOOLS:
            if collection in existing_collections:
                collection = mongo.db[collection]
                cursor = collection.aggregate([
                    {"$match": {"contractId": contract}},
                    {"$group": {
                        "_id": "$item",
                        "minPeriod": {"$min": "$month"},
                        "maxPeriod": {"$max": "$month"}
                    }}
                ])
                if cursor.get('result'):
                    if result['max'] is None:
                        result['max'] = cursor['result'][0]['maxPeriod']
                    else:
                        result['max'] = max(
                            result['max'], cursor['result'][0]['maxPeriod']
                        )
                    if result['min'] is None:
                        result['min'] = cursor['result'][0]['minPeriod']
                    else:
                        result['min'] = min(
                            result['min'], cursor['result'][0]['minPeriod']
                        )
        return jsonify(result)
