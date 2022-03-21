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

def test__scenario_report__with_power(api, scenario_data):
    contract, token = scenario_data
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        query_string=dict(
            tilt=30.0,
            azimuth='180#0', # TODO: split both azimuths
            power='10.640 kWp', # TODO: Remove units from value 
        ),
        headers=dict(
            Authorization = 'token {}'.format(token)
        ),
    )

    assert r.get_json() == {
        'areaM2': 1.87,
        'azimuthDegrees': '180#0',
        'tiltDegrees': 30.0,
        'loadByPeriodKwh': {
            'p1': 803.794,
            'p2': 755.707,
            'p3': 1217.922,
        },
        "loadKwhYear": 2777.4230000000002,
        "productionKwhYear": 12863.530773648346,
        "productionToGridKwhYear": 11853.280996988628,
        'productionToGridEuroYear': 283.9833047153394,
        'productionToGridPercent': 92.10803266596614,
        "productionToLoadKwhYear": 1015.1856466597212,
        'productionToLoadEuroYear': 222.07594681978958,
        'productionToLoadPercent': 7.891967334033866,
        'installationCostEuro': 14805.56000075138,
        'savingsEuroYear': 505.2692606181667,
        "paybackYears": 20.54521623587875,
        'loadFromGridKwhYear': 1767.1732233402788,
        'nModules': 28.0,
        'totalPower': '10.640 kWp',
        'dailyLoadProfileKwh': [
            0.24,
            0.235,
            0.188,
            0.119,
            0.112,
            0.111,
            0.11,
            0.11,
            0.112,
            0.128,
            0.163,
            0.164,
            0.159,
            0.169,
            0.173,
            0.184,
            0.185,
            0.176,
            0.185,
            0.201,
            0.227,
            0.297,
            0.27,
            0.242,
        ],
        'dailyProductionProfileKwh': [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.8733649097729941,
            2.132785749209078,
            3.2393951214401646,
            4.064854211760346,
            4.643752166543438,
            4.885962038699223,
            4.944434738588591,
            4.108439767189539,
            3.0657028896604603,
            1.6406848235229639,
            0.13573439695206235,
            0.0,
            0.0,
            0.0,
            0.0,
        ],
    }


def test__scenario_report__optimal_payback(api, scenario_data):
    contract, token = scenario_data
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        query_string=dict(
            tilt=30.0,
            azimuth='180#0',
        ),
        headers=dict(
            Authorization = 'token {}'.format(token)
        ),
    )

    assert r.get_json() == {
        'areaM2': 1.87,
        'azimuthDegrees': '180#0',
        'tiltDegrees': 30.0,
        'loadByPeriodKwh': {
            'p1': 803.794,
            'p2': 755.707,
            'p3': 1217.922,
        },
        'loadKwhYear': 2777.4230000000002,
        'productionKwhYear': 2713.065471190853,
        'productionToGridKwhYear': 1938.3961489902156,
        'productionToGridEuroYear': 135.97414413724206,
        'productionToGridPercent': 71.26478514879176,
        'productionToLoadKwhYear': 779.605192200637,
        'productionToLoadEuroYear': 171.86720270326845,
        'productionToLoadPercent': 28.73521485120825,
        'installationCostEuro': 4689.960000238015,
        'savingsEuroYear': 307.05135592354816,
        'paybackYears': 12.4569525340302,
        'loadFromGridKwhYear': 2002.7536777993632,
        'nModules': 6.0,
        'totalPower': '2.280 kWp',
        'dailyLoadProfileKwh': [
            0.24,
            0.235,
            0.188,
            0.119,
            0.112,
            0.111,
            0.11,
            0.11,
            0.112,
            0.128,
            0.163,
            0.164,
            0.159,
            0.169,
            0.173,
            0.184,
            0.185,
            0.176,
            0.185,
            0.201,
            0.227,
            0.297,
            0.27,
            0.242,
        ],  
        'dailyProductionProfileKwh': [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.18447877986758623,
            0.45050322989886715,
            0.6842496794010439,
            0.8586094276676137,
            0.9808886573128532,
            1.0320500689830303,
            1.044401117451371,
            0.8678159002376173,
            0.6475610849399653,
            0.346557928998376,
            0.028670851846208854,
            0.0,
            0.0,
            0.0,
            0.0,
        ],
    }

def test__scenario_report__parameter_value_not_found(api, scenario_data):
    contract, token = scenario_data
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        query_string=dict(
            tilt=31.0, # Value for tilt not found
            azimuth='180#0',
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
        'azimuth': [100.0, 140.0, 180.0, '100#280', '140#320', '180#0'],
        'power':  [
            '10.640 kWp',
            '2.280 kWp',
            '3.040 kWp',
            '4.560 kWp',
            '5.320 kWp',
            '6.080 kWp',
            '7.600 kWp',
            '8.360 kWp',
            '9.120 kWp',
        ],
    }
