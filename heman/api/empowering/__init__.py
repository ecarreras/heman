from __future__ import absolute_import

from amoniak.utils import setup_empowering_api

from heman.api import AuthorizedResource


service = setup_empowering_api()


class EmpoweringResource(AuthorizedResource):
    pass
