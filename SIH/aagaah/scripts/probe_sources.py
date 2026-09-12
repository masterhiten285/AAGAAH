"""Bounded public-source probes. HTTP success alone does not verify a data product."""
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
PROBES = {
    'imerg': ('https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg/gis/early/', None),
    'imd': ('https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html', None),
    'mosdac': ('https://mosdac.gov.in/downloadapi-manual', None),
    'copernicus': ('https://copernicus-dem-30m.s3.amazonaws.com/?list-type=2&prefix=Copernicus_DSM_COG_10_N30_00_E079_00_DEM&max-keys=5', None),
    'wris': ('https://indiawris.gov.in/wris/', None),
    'cwc': ('https://www.cwc.gov.in/sites/default/files/meteorological-network-details-of-cwc.pdf', None),
    'sentinel1': ('https://catalogue.dataspace.copernicus.eu/odata/v1/Products?' + urllib.parse.urlencode({'$filter': "Collection/Name eq 'SENTINEL-1' and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((78.8 30.2,79.4 30.2,79.4 30.9,78.8 30.9,78.8 30.2))')", '$top': '1'}), None),
    'jrc': ('https://global-surface-water.appspot.com/download', None),
    'osm': ('https://overpass-api.de/api/interpreter', urllib.parse.urlencode({'data': '[out:json][timeout:25];(node[place](30.2,78.8,30.9,79.4);way[waterway=river](30.2,78.8,30.9,79.4);way[bridge](30.2,78.8,30.9,79.4);nwr[amenity=hospital](30.2,78.8,30.9,79.4););out geom;'}).encode()),
    'reports': ('https://nidm.gov.in/PDF/pubs/India%20Disaster%20Report%202013.pdf', None),
    'openmeteo': ('https://api.open-meteo.com/v1/forecast?latitude=30.7346&longitude=79.0669&hourly=precipitation,soil_moisture_0_to_1cm&forecast_days=1', None),
    'openmeteo_archive': ('https://archive-api.open-meteo.com/v1/archive?latitude=30.7346&longitude=79.0669&start_date=2013-06-14&end_date=2013-06-18&hourly=precipitation,soil_moisture_0_to_7cm', None),
}

def probe(item):
    name, (url, body) = item
    result = {'id': name, 'url': url, 'tested_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'authenticated': False}
    try:
        request = urllib.request.Request(url, data=body, headers={'User-Agent': 'AAGAAH-research-prototype/0.1'})
        with urllib.request.urlopen(request, timeout=35) as response:
            content = response.read(40_000_001)
            result.update(http_status=response.status, content_type=response.headers.get('Content-Type'), bytes=len(content), final_url=response.url, sha256=hashlib.sha256(content).hexdigest())
            ext = '.nc' if content[:3] == b'CDF' else '.json' if 'json' in response.headers.get('Content-Type','') else '.pdf' if content[:4] == b'%PDF' else '.txt'
            target = RAW / (name + ext)
            target.write_bytes(content)
            result['sample'] = str(target.relative_to(ROOT)).replace('\\','/')
            if ext == '.json':
                obj = json.loads(content)
                result['payload_keys'] = list(obj)[:12]
                if name == 'osm': result['elements'] = len(obj.get('elements', []))
                if name == 'sentinel1': result['products'] = len(obj.get('value', []))
            result['note'] = 'Transport verified; interpret product/auth/coverage separately in source registry.'
            result['truncated'] = len(content) > 40_000_000
    except Exception as exc:
        result.update(http_status=getattr(exc, 'code', None), error=str(exc), note='No usable sample; provider remains PLANNED.')
    return result

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(probe, PROBES.items()))
    (RAW / 'probe-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))
