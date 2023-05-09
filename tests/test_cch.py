import os

import pytest
from mock import patch
from testdata.curves import (
    tg_cchfact_existing_points,
    tg_cchfact_NOT_existing_points_BUT_f1,
)

from yamlns import ns
from yamlns.pytestutils import assert_ns_equal

from somutils.isodates import localisodate

from heman.app import application
from heman.api.cch import CCHFact
from heman.api.cch import TgCchF1Repository
from heman.api.cch.mongo_curve_backend import MongoCurveBackend
from heman.api.cch.timescale_curve_backend import TimescaleCurveBackend


@pytest.fixture()
def http_client():
    return application.test_client()


class TestCchRequest(object):

    def test_tg_cchfact_existing_points(self, http_client, yaml_snapshot):
        token = tg_cchfact_existing_points['token']
        cups = tg_cchfact_existing_points['cups']
        date = tg_cchfact_existing_points['date']
        endpoint_url = '/api/CCHFact/{cups}/{date}'.format(
            cups=cups,
            date=date
        )
        headers = dict(
            Authorization='token {token}'.format(token=token)
        )

        response = http_client.get(
            endpoint_url,
            headers=headers
        )

        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))

    def test_tg_cchfact_NOT_existing_points_BUT_f1(self, http_client, yaml_snapshot):
        token = tg_cchfact_NOT_existing_points_BUT_f1['token']
        cups = tg_cchfact_NOT_existing_points_BUT_f1['cups']
        date = tg_cchfact_NOT_existing_points_BUT_f1['date']
        endpoint_url = '/api/CCHFact/{cups}/{date}'.format(
            cups=cups,
            date=date
        )
        headers = dict(
            Authorization='token {token}'.format(token=token)
        )

        response = http_client.get(
            endpoint_url,
            headers=headers
        )

        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))

    def test_no_curves_data(self, http_client, yaml_snapshot):
        no_results_date = 200001 # This date is so ancient there is no curves yet

        token = tg_cchfact_NOT_existing_points_BUT_f1['token']
        cups = tg_cchfact_NOT_existing_points_BUT_f1['cups']
        date = tg_cchfact_NOT_existing_points_BUT_f1['date']
        endpoint_url = '/api/CCHFact/{cups}/{date}'.format(
            cups=cups,
            date=no_results_date,
        )
        headers = dict(
            Authorization='token {token}'.format(token=token)
        )

        response = http_client.get(
            endpoint_url,
            headers=headers
        )

        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))


def get_mongo_instance():
    f = get_mongo_instance
    if not hasattr(f, 'instance'):
        from pymongo import MongoClient
        f.instance = MongoClient(os.environ.get('MONGO_URI'))
    return f.instance.somenergia

class TestCurveBackend(object):
    def test_get_curve_f1_timescale(self, yaml_snapshot):

        backend = TimescaleCurveBackend()

        result = backend.get_curve(
            curve_type=TgCchF1Repository(backend),
            start=localisodate('2019-09-21'),
            end=localisodate('2019-09-22'),
            cups=tg_cchfact_NOT_existing_points_BUT_f1['cups'],
        )


        yaml_snapshot(ns(
            result=[x for x in result]
        ))

    def test_get_curve_f1_mongo(self, yaml_snapshot):
        backend = MongoCurveBackend(get_mongo_instance())

        result = backend.get_curve(
            curve_type=TgCchF1Repository(backend),
            start=localisodate('2019-09-21'),
            end=localisodate('2019-09-22'),
            cups=tg_cchfact_NOT_existing_points_BUT_f1['cups'],
        )


        yaml_snapshot(ns(
            result=[x for x in result]
        ))

    def test_get_curve_f1_mongo_and_timescale_equal(self, yaml_snapshot):
        backend_mongo = MongoCurveBackend(get_mongo_instance())
        backend_timescale = TimescaleCurveBackend()

        result_mongo, result_timescale = [
            backend.get_curve(
                curve_type=TgCchF1Repository(backend),
                start=localisodate('2019-09-21'),
                end=localisodate('2019-09-22'),
                cups=tg_cchfact_NOT_existing_points_BUT_f1['cups'],
            )
            for backend in (backend_mongo, backend_timescale)
        ]
        assert_ns_equal(
            ns(result=list(result_mongo)),
            ns(result=list(result_timescale)),
        )

