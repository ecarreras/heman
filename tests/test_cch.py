from yamlns import ns

from testdata.curves import (
    tg_cchfact_existing_points,
    tg_cchfact_NOT_existing_points_BUT_f1,
)

from heman.app import application


class TestCchRequest(object):

    def test_tg_cchfact_existing_points(self, yaml_snapshot):
        token = tg_cchfact_existing_points['token']
        cups = tg_cchfact_existing_points['cups']
        date = tg_cchfact_existing_points['date']
        endpoint_url = '/api/CCHFact/{cups}/{date}'.format(
            cups=cups,
            date=date
        )
        client = application.test_client()
        headers = dict(
            Authorization='token {token}'.format(token=token)
        )

        response = client.get(
            endpoint_url,
            headers=headers
        )

        assert response.status_code == 200

        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))

    def test_tg_cchfact_NOT_existing_points_BUT_f1(self, yaml_snapshot):
        token = tg_cchfact_NOT_existing_points_BUT_f1['token']
        cups = tg_cchfact_NOT_existing_points_BUT_f1['cups']
        date = tg_cchfact_NOT_existing_points_BUT_f1['date']
        endpoint_url = '/api/CCHFact/{cups}/{date}'.format(
            cups=cups,
            date=date
        )
        client = application.test_client()
        headers = dict(
            Authorization='token {token}'.format(token=token)
        )

        response = client.get(
            endpoint_url,
            headers=headers
        )

        assert response.status_code == 200

        yaml_snapshot(ns(
            status=response.status,
            json=response.json,
        ))
