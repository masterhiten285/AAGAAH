"""One causal pipeline, shared by replay, ingestion, and /predict."""
from datetime import datetime, timezone
from .processing import features_at
from .spatial import apply_decisions

def run_pipeline(pilot,readings,as_of,models,spatial):
    predictions={}
    for location in pilot['locations']:
        features,quality=features_at(readings,location,as_of)
        prediction=models.predict(features,quality)
        predictions[location['id']]={**prediction,'id':location['id'],'name':location['name'],
            'lat':location['lat'],'lon':location['lon'],'terrain':location['terrain'],
            'features':{k:None if v!=v else round(v,4) for k,v in features.items()}}
    decisions=apply_decisions(pilot,predictions,spatial)
    locations=sorted(decisions.values(),key=lambda r:r['rank'])
    return {'as_of':as_of.isoformat(),'computed_at':datetime.now(timezone.utc).isoformat(),
        'mode':'REPLAY' if all(r.status.value=='REPLAY' for r in readings) else 'MIXED INPUTS',
        'synthetic':any(r.synthetic for r in readings),'model_status':'MOCKED',
        'disclaimer':'Demonstration only. Scores are not validated flood probabilities; no warning lead time established.',
        'locations':locations,'pipeline_stages':['ingestion','validation/freshness','features','risk model (independent)',
        'anomaly model (independent)','confidence/SHAP','terrain/graph','exposure','priority','advisory'],
        'summary':{'locations':len(locations),'needs_review':sum(l['manual_review'] for l in locations),
                   'highest_risk':max((l['routed_risk'] or 0 for l in locations),default=0),
                   'population':None,'data_adequacy':round(sum(l['confidence'] for l in locations)/max(1,len(locations)),4)}}
