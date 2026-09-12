"""Derive pilot geometry from actual Copernicus DSM and cached OSM, not circles."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend-api'))
import json
import hashlib
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin, rowcol, xy
from rasterio.features import shapes
from pyproj import Transformer
from shapely.geometry import shape, mapping, Point, LineString
from shapely.ops import transform, unary_union
from aagaah.hydrology import condition_dem, route_d8, delineate

OUT = ROOT / 'data/processed'
OUT.mkdir(parents=True, exist_ok=True)
to_utm = Transformer.from_crs(4326, 32644, always_xy=True)
to_geo = Transformer.from_crs(32644, 4326, always_xy=True)
CELL = 120
datasets = [rasterio.open(ROOT / f'data/raw/dem_{east}.tif') for east in (78,79)]
mosaic, source_transform = merge(datasets, bounds=(78.65,30.15,79.5,30.98))
west, south, east, north = transform_bounds(4326,32644,78.65,30.15,79.5,30.98)
affine = from_origin(west,north,CELL,CELL)
dem = np.full((int(np.ceil((north-south)/CELL)),int(np.ceil((east-west)/CELL))),np.nan,dtype='float32')
reproject(mosaic[0],dem,src_transform=source_transform,src_crs=4326,
          dst_transform=affine,dst_crs=32644,resampling=Resampling.bilinear)
for ds in datasets: ds.close()
if not np.isfinite(dem).all(): raise RuntimeError('Incomplete DEM coverage; enlarge source mosaic')
print('Conditioning', dem.shape, flush=True)
filled = condition_dem(dem)
receiver, acc, order = route_d8(filled,CELL)
dy,dx = np.gradient(dem,CELL,CELL)
slope = np.degrees(np.arctan(np.hypot(dx,dy)))
osm = json.loads((ROOT/'data/raw/osm.json').read_text(encoding='utf8'))['elements']
nodes = {e['id']:e for e in osm if e['type']=='node'}
selected = [('kedarnath',1188262619),('gaurikund',342108397),('sonprayag',1809868954),
            ('guptkashi',342108333),('chandrapuri',342108043)]
agast = next(e for e in osm if e.get('tags',{}).get('name')=='Agastmuni')
selected += [('agastmuni',agast['id']),('rudraprayag',342107378)]
river_geoms = [LineString([(p['lon'],p['lat']) for p in e['geometry']]) for e in osm
               if e.get('geometry') and e.get('tags',{}).get('waterway')=='river']
rivers = unary_union([transform(to_utm.transform,g) for g in river_geoms])

def snap(lon,lat,radius=800,allowed=None):
    x,y = to_utm.transform(lon,lat)
    r,c = rowcol(affine,x,y)
    n = int(radius/CELL)
    candidates=[]
    for rr in range(max(0,r-n),min(dem.shape[0],r+n+1)):
        for cc in range(max(0,c-n),min(dem.shape[1],c+n+1)):
            if np.hypot(rr-r,cc-c)*CELL > radius: continue
            i = rr*dem.shape[1]+cc
            if allowed is None or allowed[i]: candidates.append((int(acc[rr,cc]),-np.hypot(rr-r,cc-c),i))
    if not candidates: raise ValueError(f'No in-basin stream near {lon},{lat}')
    return max(candidates)[2]

# Upstream of Mandakini–Alaknanda confluence; do not snap onto Alaknanda.
outlet = snap(78.977,30.303,240)
basin_mask = delineate(receiver,order,[outlet])==0
outlets=[]
locations=[]
for ident,node_id in selected:
    node = nodes[node_id]
    # Guptkashi is upslope; use a broader stream search but retain actual settlement point.
    cell = outlet if ident=='rudraprayag' else snap(node['lon'],node['lat'],1800 if ident=='guptkashi' else 800,basin_mask)
    if cell in outlets: raise ValueError('Outlets collapsed onto the same cell')
    outlets.append(cell)
    r,c = divmod(cell,dem.shape[1]); x,y = xy(affine,r,c)
    sr,sc = rowcol(affine,*to_utm.transform(node['lon'],node['lat']))
    locations.append({'id':ident,'name':'Rudraprayag approach' if ident=='rudraprayag' else node['tags']['name'],
        'lon':to_geo.transform(x,y)[0] if ident=='rudraprayag' else node['lon'],
        'lat':to_geo.transform(x,y)[1] if ident=='rudraprayag' else node['lat'],
        'settlement_lon':node['lon'],'settlement_lat':node['lat'],
        'osm_id':node_id, 'geometry_status':'VERIFIED LIVE', 'population':None,
        'outlet':list(to_geo.transform(x,y)), 'terrain':{
            'slope_deg':round(float(slope[r,c] if ident=='rudraprayag' else slope[sr,sc]),2), 'elevation_m':round(float(dem[r,c] if ident=='rudraprayag' else dem[sr,sc]),1),
            'river_distance_m':round(rivers.distance(Point(*to_utm.transform(node['lon'],node['lat']))),1),
            'upstream_area_km2':round(float(acc[r,c]*CELL*CELL/1e6),3)}})
labels = delineate(receiver,order,outlets)
features=[]
for i, loc in enumerate(locations):
    mask=(labels.reshape(dem.shape)==i)&basin_mask.reshape(dem.shape)
    polygons=[shape(g) for g,v in shapes(mask.astype('uint8'),mask=mask,transform=affine) if v==1]
    polygon=unary_union(polygons).simplify(70,preserve_topology=True)
    features.append({'type':'Feature','geometry':mapping(transform(to_geo.transform,polygon)),
        'properties':{'id':loc['id'],'name':loc['name']+' incremental catchment','area_km2':round(mask.sum()*CELL*CELL/1e6,3),
        'status':'REPLAY','geometry_origin':'Copernicus GLO-30; resampled 120m; priority-flood/D8; provisional'}})
edges=[]
flow_features=[]
for i,source in enumerate(outlets):
    path=[source]; target=receiver[source]
    while target>=0 and basin_mask[target] and target not in outlets:
        path.append(int(target)); target=receiver[target]
    if target in outlets:
        path.append(int(target)); j=outlets.index(target)
        coords=[xy(affine,*divmod(k,dem.shape[1])) for k in path]
        line=LineString(coords)
        edges.append({'upstream':locations[i]['id'],'downstream':locations[j]['id'],
                      'length_m':round(line.length,1),'method':'DEM D8 flow path'})
        flow_features.append({'type':'Feature','geometry':mapping(transform(to_geo.transform,line.simplify(50))),
                              'properties':edges[-1]})
basin=unary_union([shape(f['geometry']) for f in features])
infrastructure=[]
for e in osm:
    tags=e.get('tags',{})
    kind='hospital' if tags.get('amenity')=='hospital' else 'bridge' if tags.get('bridge') else 'settlement' if tags.get('place') else None
    if not kind: continue
    if 'lat' in e: geometry=Point(e['lon'],e['lat'])
    elif e.get('geometry') and len(e['geometry'])>=2: geometry=LineString([(p['lon'],p['lat']) for p in e['geometry']])
    else: continue
    if not basin.intersects(geometry): continue
    infrastructure.append({'type':'Feature','geometry':mapping(geometry),
       'properties':{'id':f"osm-{e['type']}-{e['id']}", 'name':tags.get('name',f'Unnamed {kind}'),
                     'kind':kind,'population':None,'status':'VERIFIED LIVE','source':'OpenStreetMap'}})
# Preserve actual road/bridge geometry; do not invent population or hospitals.
for e in osm:
    if e.get('tags',{}).get('highway') and e.get('geometry') and len(e['geometry'])>=2:
        g=LineString([(p['lon'],p['lat']) for p in e['geometry']])
        if basin.intersects(g): infrastructure.append({'type':'Feature','geometry':mapping(g),'properties':{
            'id':f"osm-road-{e['id']}",'name':e['tags'].get('name','Mapped road segment'),'kind':'road',
            'population':None,'status':'VERIFIED LIVE','source':'OpenStreetMap'}})

def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
save('catchments.geojson',{'type':'FeatureCollection','features':features})
save('flowpaths.geojson',{'type':'FeatureCollection','features':flow_features})
save('infrastructure.geojson',{'type':'FeatureCollection','features':infrastructure})
save('rivers.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'source':'OSM'},'geometry':mapping(g.intersection(basin))} for g in river_geoms if g.intersects(basin)]})
save('pilot.json',{'id':'mandakini-v1','name':'Mandakini watershed','status':'PROVISIONAL DEM DELINEATION',
 'crs':'EPSG:32644','source_resolution_m':30,'analysis_resolution_m':CELL,
 'outlet':locations[-1]['outlet'],'area_km2':round(basin_mask.sum()*CELL*CELL/1e6,3),
 'locations':locations,'edges':edges,'station_coverage':[{'name':'Chandrapuri','type':'CWC rainfall inventory','observations_access':'PLANNED','lat':30.430833,'lon':79.069167}],
 'scientific_readiness':False,'boundary_touches_dem_edge':bool(basin_mask.reshape(dem.shape)[[0,-1],:].any() or basin_mask.reshape(dem.shape)[:,[0,-1]].any()),
 'limitations':['120m analysis of a surface model; not a surveyed hydrological boundary','No accessible gauge history verified','OSM infrastructure coverage incomplete; population unknown','Current terrain/infrastructure do not reconstruct 2013 conditions']})
with rasterio.open(OUT/'terrain_120m.tif','w',driver='GTiff',height=dem.shape[0],width=dem.shape[1],count=3,dtype='float32',crs=32644,transform=affine,compress='deflate') as dst:
    dst.write(dem,1); dst.write(slope.astype('float32'),2); dst.write((acc*CELL*CELL/1e6).astype('float32'),3)
print(json.dumps({'area_km2':round(basin_mask.sum()*CELL*CELL/1e6,2),'edges':edges,'infrastructure':len(infrastructure)},indent=2))
