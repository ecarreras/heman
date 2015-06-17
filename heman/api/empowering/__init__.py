from __future__ import absolute_import

from amoniak.utils import setup_empowering_api

from heman.api import Resource


service = setup_empowering_api()


class EmpoweringResource(Resource):
    pass
