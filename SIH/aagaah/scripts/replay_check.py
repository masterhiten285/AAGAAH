"""Execute representative replay frames through every stage and save behavior evidence."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend-api'))
import json
from datetime import timedelta
from aagaah.config import Settings
from aagaah.main import create_app
from aagaah.providers import START,SyntheticReplay,OpenMeteoArchiveReplay
from aagaah.pipeline import run_pipeline
from fastapi.testclient import TestClient

app=create_app(Settings(demo_memory=True,schedule=False))
frames=[]
with TestClient(app) as client:
    for step in (0,12,24,30,42,60,71):
        response=client.post('/replay/control',json={'action':'seek','step':step},headers={'X-Control-Token':'local-demo-only'})
        response.raise_for_status()
        frame=response.json(); frames.append(frame)
    assert frames[3]['summary']['highest_risk']>frames[0]['summary']['highest_risk']+.4
    assert frames[-1]['summary']['highest_risk']<frames[3]['summary']['highest_risk']
    for frame in frames:
        assert len(frame['pipeline_stages'])==10
        assert frame['synthetic'] and frame['model_status']=='MOCKED'
        assert all(l['advisory_only'] and l['confidence']<=.45 for l in frame['locations'])
    reset=client.post('/replay/control',json={'action':'reset'},headers={'X-Control-Token':'local-demo-only'}).json()
    assert [x['risk_score'] for x in reset['locations']]==[x['risk_score'] for x in frames[0]['locations']]
    assert len(client.get('/locations/kedarnath/history').json())==1
    # Exercise the real cached archive adapter separately. Never fill neighboring sites with its values.
    rows=OpenMeteoArchiveReplay().read(app.state.pilot['locations'],START+timedelta(hours=30))
    archive=run_pipeline(app.state.pilot,rows,START+timedelta(hours=30),app.state.models,app.state.spatial)
    assert not archive['synthetic'] and archive['model_status']=='MOCKED'
    assert sum(l['risk_score'] is not None for l in archive['locations'])==1
    (ROOT/'docs/openapi.json').write_text(json.dumps(client.get('/openapi.json').json(),indent=2),encoding='utf8')

(ROOT/'artifacts').mkdir(exist_ok=True)
(ROOT/'artifacts/replay-results.json').write_text(json.dumps({'synthetic_frames':frames,'real_archive_context':archive},indent=2),encoding='utf8')
report=['# End-to-end demonstration walkthrough','','This run uses the explicitly selected memory-demo spatial adapter. It does not certify Docker/PostGIS; run the integration workflow for that.','','The dates refer to the June 2013 Mandakini disaster as narrative context. The environmental series below is deterministic and synthetic. No historical event detection, predictive accuracy, precision, recall, or warning lead time is inferred.','','| Replay hour | Simulated timestamp | Highest demo score | Locations requiring review |','|---|---|---|---|']
for frame in frames:
    report.append(f"| {frame['step']} | {frame['as_of']} | {frame['summary']['highest_risk']:.3f} | {frame['summary']['needs_review']} |")
report += ['','## Observed behavior','',
 '1. At baseline, generated rainfall is low. The provider emits provenance-tagged hourly readings, including 24 hours of warm-up history.',
 '2. As the synthetic rainfall pulse rises, validation accepts only available, nonfuture hourly readings. Rainfall accumulation windows and other features are recomputed.',
 '3. XGBoost and Isolation Forest independently process the same feature vector. SHAP contributions explain the local score in log-odds. Confidence is a capped data-adequacy heuristic.',
 '4. The terrain-derived graph propagates screening scores downstream. PostGIS in Compose, or the explicit local spatial adapter in this walkthrough, intersects mapped infrastructure with incremental catchments and river proximity.',
 '5. Locations are ranked by risk × mapped impact weight × confidence. Warning/Critical conditions remain flagged for review even at low confidence.',
 '6. Scores fall as the synthetic pulse recedes. Reset reproduces baseline; chart history hides future frames after a rewind.',
 '7. The browser polls committed snapshots. Play advances one simulated hour every eight seconds; pause stops the scheduler from advancing the replay.',
 '','## Real archive context check','',
 'The cached Open-Meteo 2013 reanalysis adapter also passed through the pipeline. It supplies only the Kedarnath grid point. Other locations retain missing local predictions. The model remains synthetic-trained. Reanalysis was not an as-issued forecast and is not evidence of historical lead time.',
 '','## What the run cannot answer','',
 '**Did it detect the real 2013 flood? Not established. How early? Not established.** A synthetic pulse changing a synthetic-trained score proves software behavior only. Real evaluation needs gauge records, independent event/non-event labels, as-issued input availability, event/time-blocked training and held-out evaluation, uncertainty assessment and mechanism-specific validation.']
(ROOT/'docs/REPLAY_WALKTHROUGH.md').write_text('\n'.join(report),encoding='utf8')
print(json.dumps({'frames':len(frames),'checks':'passed','historical_performance_metrics':None},indent=2))
