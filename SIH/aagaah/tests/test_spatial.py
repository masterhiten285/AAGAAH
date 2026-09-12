import json
import networkx as nx
from aagaah.config import ROOT
from aagaah.spatial import graph_for,apply_decisions,LocalSpatial

def test_graph_and_downstream_only():
    pilot=json.loads((ROOT/'data/processed/pilot.json').read_text(encoding='utf8'))
    graph=graph_for(pilot)
    assert nx.has_path(graph,'kedarnath','rudraprayag')
    assert not nx.has_path(graph,'rudraprayag','kedarnath')
    predictions={l['id']:{'risk_score':.05,'confidence':.3,'quality':{'stale':False}} for l in pilot['locations']}
    predictions['rudraprayag']['risk_score']=.95
    result=apply_decisions(pilot,predictions,LocalSpatial())
    assert result['kedarnath']['routed_risk']==.05
    assert result['rudraprayag']['alert_level']=='Critical'
    assert result['rudraprayag']['manual_review']
    ids=[a['id'] for a in result['sonprayag']['exposure']['assets']]
    assert len(ids)==len(set(ids))

def test_corridor_is_metric_screening_geometry():
    from shapely.geometry import shape
    from shapely.ops import transform, unary_union
    from aagaah.spatial import screening_corridor
    spatial=LocalSpatial()
    feature=screening_corridor()['features'][0]
    corridor=transform(spatial.project,shape(feature['geometry']))
    basin=transform(spatial.project,unary_union(list(spatial.catchments.values())))
    expected=spatial.rivers.buffer(150).intersection(basin)
    assert corridor.is_valid and corridor.area>0
    assert corridor.symmetric_difference(expected).area/expected.area<1e-7
    assert feature['properties']['distance_m']==150
    assert 'not a flood inundation' in feature['properties']['method']

def test_high_risk_low_adequacy_and_missing_evidence_remain_reviewable():
    pilot=json.loads((ROOT/'data/processed/pilot.json').read_text(encoding='utf8'))
    predictions={l['id']:{'risk_score':None,'confidence':0.,'quality':{'stale':True}} for l in pilot['locations']}
    predictions['kedarnath'].update(risk_score=.95,confidence=.01)
    result=apply_decisions(pilot,predictions,LocalSpatial())
    assert result['kedarnath']['alert_level']=='Critical'
    assert result['kedarnath']['manual_review']
    assert all(row['manual_review'] for row in result.values())
    assert result['rudraprayag']['risk_score'] is None
    assert result['rudraprayag']['routed_risk'] is not None
    assert result['rudraprayag']['dominant_origin']=='kedarnath'
