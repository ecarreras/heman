from __future__ import unicode_literals
from yamlns import namespace as ns
import pymongo
import unittest
import mock
import pytest
import json
from ...config import create_app
from ...auth import APIUser
import os

@pytest.fixture
def api():
    os.environ['MONGO_URI']='mongodb://localhost:27017/heman_pv_test'
    if hasattr(api, 'app'):
        app = api.app
    else:
        app = create_app()
        api.app = app
    app.config['TESTING'] = True

    with app.app_context() as ctx:
        with app.test_client() as testclient:
            testclient.app = app
            testclient.ctx = ctx
            yield testclient

@pytest.fixture
def mongodb():
    mongodb = pymongo.MongoClient('mongodb://localhost:27017/heman_pv_test')
    db = mongodb['heman_pv_test']
    try:
        yield db
    finally:
        mongodb.drop_database('heman_pv_test')
        mongodb.close()

@pytest.fixture
def scenario_data(mongodb):
    contract = '666666'
    token = 'mytoken'
    user = APIUser(
        token,
        [contract]
    )
    mongodb.tokens.insert_one({
        'allowed_contracts': [
            {'cups': 'ES1111111111111111VL0F', 'name': '666666'}
        ],
        'token': token,
    })

    with open('testdata/pvautosize_example.json') as json_file:
        data = json.load(json_file)
    mongodb.photovoltaic_reports.insert_one({
        'contractName': data['_items'][0]['contractId'],
        'beedataUpdateDate': data['_items'][0]['_created'],
        'beedataCreateDate': data['_items'][0]['_created'],
        'results': data['_items'][0]['results'],
    })
    yield contract, token

def test__scenario_report__with_power(api, scenario_data, yaml_snapshot):
    contract, token = scenario_data
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        query_string=dict(
            tilt='30.0',
            azimuth=['180','0'],
            power=10.64,
        ),
        headers=dict(
            Authorization = 'token {}'.format(token)
        ),
    )
    yaml_snapshot(r.get_json())

def test__scenario_report__optimal_payback(api, scenario_data, yaml_snapshot):
    contract, token = scenario_data
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        query_string=dict(
            tilt=30.0,
            azimuth=[180,0],
        ),
        headers=dict(
            Authorization = 'token {}'.format(token)
        ),
    )
    yaml_snapshot(r.get_json())

def test__scenario_report__parameter_value_not_found(api, scenario_data):
    contract, token = scenario_data
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        query_string=dict(
            tilt=31.0, # Value for tilt not found
            azimuth=[180,0],
        ),
        headers=dict(
            Authorization = 'token {}'.format(token)
        ),
    )

    assert r.get_json() == {
        'error': 'NOT_FOUND',
        'message': "Scenario not found",
    }

def test__scenario_params(api, scenario_data):
    contract, token = scenario_data
    r = api.get('/api/ScenarioParams/{}'.format(contract),
        headers=dict(
            Authorization = 'token {}'.format(token)
        ),
    )

    assert r.get_json() == {
        'tilt': [15.0, 30.0],
        'azimuth': [[100], [100,280], [140], [140,320], [180], [180,0]],
        'power':  [
            2.280,
            3.040,
            4.560,
            5.320,
            6.080,
            7.600,
            8.360,
            9.120,
            10.640,
        ],
    }
