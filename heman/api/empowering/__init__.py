from __future__ import absolute_import

from amoniak.utils import setup_empowering_api


service = setup_empowering_api()

from heman.api.empowering.ot101 import OT101
from heman.api.empowering.ot103 import OT103


resources = [
    (OT101, '/OT101Results/<contract>/<period>'),
    (OT103, '/OT103Results/<contract>/<period>')
]
