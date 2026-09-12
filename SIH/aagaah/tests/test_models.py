import numpy as np
import pytest
from aagaah.model import Models
from aagaah.providers import SyntheticReplay, START
from aagaah.processing import features_at
from datetime import timedelta
from test_processing import LOCATION

@pytest.fixture(scope='module')
def models(): return Models()

def test_storm_changes_risk_and_shap_reconstructs(models):
    outputs=[]
    for step in (0,30):
        date=START+timedelta(hours=step)
        f,q=features_at(SyntheticReplay().read([LOCATION],date),LOCATION,date)
        outputs.append(models.predict(f,q))
    calm,storm=outputs
    assert storm['risk_score']>calm['risk_score']+.4
    logit=storm['shap_base_value']+sum(e['contribution_log_odds'] for e in storm['explanation'])
    assert abs(1/(1+np.exp(-logit))-storm['risk_score'])<1e-4
    assert storm['confidence']<=.45 and storm['model_status']=='MOCKED'

def test_anomaly_does_not_gate_risk(models,monkeypatch):
    f,q=features_at(SyntheticReplay().read([LOCATION],START),LOCATION,START)
    monkeypatch.setattr(models.anomaly,'decision_function',lambda X:np.array([-1.]))
    a=models.predict(f,q)
    monkeypatch.setattr(models.anomaly,'decision_function',lambda X:np.array([1.]))
    b=models.predict(f,q)
    assert a['risk_score']==b['risk_score'] and a['anomaly']!=b['anomaly']
