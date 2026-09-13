"""Tests for Government Operations Center endpoints:
- Watersheds registry
- Incident management workflow (create, list, transition status, audit log)
- Case studies (Dehradun 2025 context)
- Regional situation feed
- Authority situation briefing generation
"""
import pytest
from fastapi.testclient import TestClient
from aagaah.main import create_app
from aagaah.config import Settings

@pytest.fixture(scope='module')
def client():
    with TestClient(create_app(Settings(demo_memory=True, schedule=False))) as client:
        yield client

def test_watersheds_registry(client):
    res = client.get('/api/v1/watersheds')
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    mandakini = next(w for w in data if w['id'] == 'mandakini')
    assert mandakini['is_active_pilot'] is True
    assert mandakini['coverage_status'] == 'OPERATIONAL MODEL COVERAGE'
    alaknanda = next(w for w in data if w['id'] == 'alaknanda')
    assert alaknanda['is_active_pilot'] is False
    assert 'PLANNED' in alaknanda['coverage_status']

def test_incidents_workflow(client):
    # 1. List existing seeded incidents
    res = client.get('/api/v1/incidents')
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) >= 2

    # 2. Create new incident
    payload = {
        'location_id': 'gaurikund',
        'location_name': 'Gaurikund',
        'title': 'Test Culvert Obstruction Check',
        'severity': 'P2_HIGH',
        'summary': 'High local rainfall rate; field patrol dispatched to check tributary confluence.',
        'operator_notes': 'SDRF unit standby confirmed.',
        'reported_by': 'DEOC Duty Officer Test'
    }
    create_res = client.post('/api/v1/incidents', json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created['id'].startswith('INC-2026-')
    assert created['status'] == 'NEW'

    # 3. Update status to VERIFIED
    patch_res = client.patch(f"/api/v1/incidents/{created['id']}", json={
        'status': 'VERIFIED',
        'verification_details': 'Field patrol confirms culvert clear; flow normal.',
        'updated_by': 'Field Commander Rawat'
    })
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated['status'] == 'VERIFIED'
    assert any(log['action'] == 'STATUS_CHANGE' for log in updated['audit_log'])

def test_case_studies_and_situation_feed(client):
    # Case studies
    cs_res = client.get('/api/v1/case-studies')
    assert cs_res.status_code == 200
    cases = cs_res.json()
    assert len(cases) >= 3
    dehradun = next(c for c in cases if c['id'] == 'dehradun-sep-2025')
    assert 'Dehradun' in dehradun['title']
    assert 'EXTERNAL REPORT' in dehradun['provenance']

    # Situation feed
    feed_res = client.get('/api/v1/situation-feed')
    assert feed_res.status_code == 200
    feed = feed_res.json()
    assert len(feed) >= 3
    assert any('IMD' in item['source'] for item in feed)

def test_situation_summary_briefing(client):
    res = client.get('/api/v1/situation-summary/kedarnath')
    assert res.status_code == 200
    data = res.json()
    assert data['location_id'] == 'kedarnath'
    assert 'FLASH-FLOOD SITUATIONAL INTELLIGENCE BRIEFING' in data['briefing_markdown']
    assert 'Physical Hazard' in data['briefing_markdown']
    assert 'MANDATED AUTHORITY VERIFICATION ACTIONS' in data['briefing_markdown']
