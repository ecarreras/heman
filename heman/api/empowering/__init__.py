from __future__ import absolute_import

from amoniak.utils import setup_empowering_api


service = setup_empowering_api()
"""Empowering service
"""

from heman.api.empowering.ot101 import OT101
from heman.api.empowering.ot103 import OT103
from heman.api.empowering.ot201 import OT201


resources = [
    (OT101, '/OT101Results/<contract>/<period>'),
    (OT103, '/OT103Results/<contract>/<period>'),
    (OT201, '/OT201Results/<contract>/<period>')
]
