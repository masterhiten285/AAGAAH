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
