"""Render numeric elevation as a map layer; no external tile service is needed."""
from pathlib import Path
import json
import numpy as np
import rasterio
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
with rasterio.open(ROOT/'data/processed/terrain_120m.tif') as ds:
    dem=ds.read(1)
    dy,dx=np.gradient(dem,120,120)
    slope=np.arctan(np.hypot(dx,dy)); aspect=np.arctan2(-dx,dy)
    illumination=np.clip(np.cos(slope)*np.sin(np.pi/4)+np.sin(slope)*np.cos(np.pi/4)*np.cos(5*np.pi/4-aspect),0,1)
    rgb=np.stack([(12+illumination*28),(25+illumination*35),(32+illumination*42)]).astype('uint8')
    with rasterio.open(ROOT/'data/processed/hillshade.png','w',driver='PNG',width=ds.width,height=ds.height,count=3,dtype='uint8') as out: out.write(rgb)
    transform=Transformer.from_crs(ds.crs,4326,always_xy=True)
    b=ds.bounds
    corners=[transform.transform(x,y) for x,y in [(b.left,b.top),(b.right,b.top),(b.right,b.bottom),(b.left,b.bottom)]]
path=ROOT/'data/processed/pilot.json'
pilot=json.loads(path.read_text(encoding='utf8'))
pilot['terrain_image_corners']=corners
path.write_text(json.dumps(pilot,ensure_ascii=False,indent=2),encoding='utf8')
