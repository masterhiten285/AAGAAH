import pytest
from fastapi.testclient import TestClient
from aagaah.main import create_app
from aagaah.config import Settings
from aagaah.providers import START, SyntheticReplay

@pytest.fixture(scope='module')
def client():
    with TestClient(create_app(Settings(demo_memory=True,schedule=False))) as client:
        yield client

def test_api_and_replay(client):
    assert client.get('/health').json()['status']=='demo'
    assert client.get('/map/catchments').json()['features']
    assert client.get('/map/secret').status_code==404
    assert client.post('/replay/control',json={'action':'step'}).status_code==401
    before=client.get('/dashboard').json()
    after=client.post('/replay/control',json={'action':'seek','step':30},headers={'X-Control-Token':'local-demo-only'}).json()
    assert after['summary']['highest_risk']>before['summary']['highest_risk']+.4
    assert after['run_id']!=before['run_id']
    assert all(l['advisory_only'] for l in after['locations'])
    assert any(l['alert_level']=='Critical' for l in after['locations'])
    reset=client.post('/replay/control',json={'action':'reset'},headers={'X-Control-Token':'local-demo-only'}).json()
    assert [l['risk_score'] for l in reset['locations']]==[l['risk_score'] for l in before['locations']]
    assert len(client.get('/locations/kedarnath/history').json())==1

def test_prediction_validation_and_missing_data(client):
    pilot=client.get('/pilot').json()
    rows=SyntheticReplay().read(pilot['locations'][:1],START)
    payload={'as_of':START.isoformat(),'readings':[r.model_dump(mode='json') for r in rows]}
    response=client.post('/predict',json=payload)
    assert response.status_code==200
    rows_out=response.json()['locations']
    assert sum(l['risk_score'] is None for l in rows_out)==len(pilot['locations'])-1
    assert all(l['confidence']==0 for l in rows_out if l['risk_score'] is None)
    payload['readings'][0]['rainfall_mm']=-5
    assert client.post('/predict',json=payload).status_code==422
    assert client.get('/locations/invalid/history').status_code==404

def test_provenance_and_scope(client):
    assert client.get('/model-card').json()['performance_metrics'] is None
    assert len(client.get('/sources').json())>=10
    pilot=client.get('/pilot').json()
    assert not pilot['boundary_touches_dem_edge']
    assert 1500<pilot['area_km2']<1800
    assert not pilot['scientific_readiness']

def test_live_mode_cannot_return_replay(client):
    live=client.get('/dashboard?mode=live')
    assert live.status_code==503
    assert 'not connected' in live.json()['detail']
    assert 'locations' not in live.json()
    assert client.get('/dashboard?mode=replay').json()['mode']=='REPLAY'
    assert client.get('/dashboard?mode=invalid').status_code==422
    assert client.get('/health').json()['live_monitoring'] is False

def test_sources_distinguish_access_probe_from_operational_usage(client):
    sources={source['id']:source for source in client.get('/sources').json()}
    assert sources['openmeteo']['status']=='VERIFIED LIVE'  # Preserve original probe evidence.
    assert sources['openmeteo']['usage_type']=='PLANNED'
    assert sources['openmeteo']['last_observation_at'] is None
    assert sources['osm']['usage_type']=='DERIVED STATIC'
    assert sources['cwc']['usage_type']=='PLANNED'
    assert sources['openmeteo_archive']['usage_type']=='HISTORICAL / REPLAY'
    assert sources['openmeteo_archive']['last_observation_at'].startswith('2013-06-18')
    assert all(source['usage_type']!='LIVE' for source in sources.values())

def test_all_map_layers_and_observation_provenance(client):
    for layer in ('catchments','rivers','flowpaths','infrastructure','screening-corridor'):
        response=client.get('/map/'+layer)
        assert response.status_code==200
        assert response.json()['features']
    assert client.get('/map/terrain.png').headers['content-type']=='image/png'
    snapshot=client.get('/dashboard').json()
    for location in snapshot['locations']:
        assert location['quality']['latest_observed_at']==snapshot['as_of']
        assert location['quality']['latest_available_at']==snapshot['as_of']
