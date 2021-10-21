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
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context() as ctx:
        with app.test_client() as api:
            api.app = app
            api.ctx = ctx
            yield api

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
    with open('testdata/pvautosize_example.json') as json_file:
        data = json.load(json_file)

    mongodb.tokens.insert_one({
        'allowed_contracts': [
            {'cups': 'ES1111111111111111VL0F', 'name': '666666'}
        ],
        'token': 'mytoken'
    })

    mongodb.photovoltaic_reports.insert_one({
        'contractName':data['_items'][0]['contractId'],
        'beedataUpdateDate':data['_items'][0]['_created'],
        'beedataCreateDate':data['_items'][0]['_created'],
        'results': data['_items'][0]['results'],
    })

def test_scenario_report(api, scenario_data):
    contract='666666'
    user = APIUser(
        'mytoken',
        ['666666']
    )
    r = api.get('/api/ScenarioReport/{}'.format(contract),
        json={},
        headers=dict(
            Authorization = 'token mytoken'
        ),
    )

    assert r.get_json() == {
        "productionToGridKwhYear": 11853.280996988628,
        "loadKwhYear": 2777.4230000000002,
        "productionKwhYear": 12863.530773648346,
        "installationCostEuro": 14805.56000075138,
        "savingsEuroYear": 505.2692606181667,
        "paybackYears": 20.54521623587875,
        "productionToLoadKwhYear": 1015.1856466597212
    }

