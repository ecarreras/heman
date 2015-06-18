from __future__ import absolute_import

from amoniak.utils import setup_empowering_api


service = setup_empowering_api()


from heman.api.empowering.ot103 import OT103


resources = [
    (OT103, '/OT103Results/<contract>/<period>')
]
