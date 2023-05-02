import pytest
from mock import patch
from testdata.curves import (
    tg_cchfact_existing_points,
    tg_cchfact_NOT_existing_points_BUT_f1,
)

from yamlns import ns

from heman.app import application
from heman.api.cch import CCHFact


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

        with patch.object(CCHFact, '_query_result_length', return_value=0):
            response = http_client.get(
                endpoint_url,
                headers=headers
            )

        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))
