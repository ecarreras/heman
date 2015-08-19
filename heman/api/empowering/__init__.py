from __future__ import absolute_import

from amoniak.utils import setup_empowering_api


service = setup_empowering_api()
"""Empowering service
"""

from heman.api.empowering.ot101 import OT101
from heman.api.empowering.ot103 import OT103
from heman.api.empowering.ot201 import OT201
from heman.api.empowering.ot401 import OT401
from heman.api.empowering.custom import PeriodRange

resources = [
    (OT101, '/OT101Results/<contract>/<period>'),
    (OT103, '/OT103Results/<contract>/<period>'),
    (OT201, '/OT201Results/<contract>/<period>'),
    (OT401, '/OT401Results/<contract>/<period>'),
    (PeriodRange, '/PeriodRange/<contract>')
]
