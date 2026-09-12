"""Operational usage is separate from a successful historical HTTP access probe."""
import json
from .config import ROOT


def source_catalog():
    entries=json.loads((ROOT/'data/source-registry.json').read_text(encoding='utf8'))
    usage={
        'copernicus':('DERIVED STATIC','Cached DSM; terrain and provisional catchments derived at 120m.'),
        'osm':('DERIVED STATIC','Cached rivers and asset inventory; incomplete, not historical 2013 assets.'),
        'reports':('HISTORICAL / REPLAY','Retrospective narrative context only; not model training labels.'),
        'cwc':('PLANNED','Inventory accessed; gauge time-series ingestion not connected.'),
        'openmeteo':('PLANNED','Forecast sample cached during access probe; no live dashboard adapter.'),
        'openmeteo_archive':('HISTORICAL / REPLAY','Cached reanalysis adapter for Kedarnath only; separate from default synthetic replay.'),
    }
    for source in entries:
        category,purpose=usage.get(source['id'],('PLANNED','No operational observations supplied to the dashboard.'))
        source['usage_type']=category
        source['usage_status']=purpose
        source['last_observation_at']=None
        source['retrieved_at']=(source.get('probe') or {}).get('tested_at')
        if source['id']=='openmeteo_archive':
            path=ROOT/'data/raw/openmeteo_archive.json'
            if path.exists():
                times=json.loads(path.read_text(encoding='utf8')).get('hourly',{}).get('time',[])
                source['last_observation_at']=max(times)+'Z' if times else None
    return entries
