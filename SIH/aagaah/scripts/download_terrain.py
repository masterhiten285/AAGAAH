"""Resolve actual S3 object keys before downloading public Copernicus tiles."""
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET
import json
import hashlib
ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'data/raw'
records = []
for east in (78, 79):
    prefix = f'Copernicus_DSM_COG_10_N30_00_E{east:03}_00_DEM'
    base = 'https://copernicus-dem-30m.s3.amazonaws.com/'
    xml = urllib.request.urlopen(base + '?list-type=2&prefix=' + prefix, timeout=30).read()
    keys = [e.text for e in ET.fromstring(xml).iter() if e.tag.endswith('}Key')]
    key = next(k for k in keys if k.endswith('/' + prefix + '.tif'))
    target = out / f'dem_{east}.tif'
    if not target.exists():
        with urllib.request.urlopen(base + key, timeout=60) as response, target.open('wb') as dest:
            while chunk := response.read(1024 * 1024): dest.write(chunk)
    records.append({'url': base + key, 'file': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size, 'status': 'VERIFIED LIVE', 'note': 'Downloaded static DSM, not a live elevation sensor.'})
    print(records[-1], flush=True)
(out / 'terrain-downloads.json').write_text(json.dumps(records, indent=2))
