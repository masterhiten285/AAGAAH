"""Stages 6–9: downstream graph screening, exposure, priority and advisories."""
import json
import math
import networkx as nx
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform, unary_union
from .config import ROOT

RECOMMENDATIONS={
    'Normal':'Continue monitoring and check data freshness.',
    'Watch':'Review upstream rainfall and confirm conditions with local observers.',
    'Warning':'Request field verification of river crossings and prepare response teams.',
    'Critical':'Urgent authority review: verify river conditions and consider restricting exposed crossings under local protocols.',
    'Unknown':'Restore missing observations and request a manual situation assessment.'}

def screening_corridor():
    """Display the metric screening rule, clipped to the provisional pilot footprint."""
    load=lambda name:json.loads((ROOT/'data/processed'/name).read_text(encoding='utf8'))
    project=Transformer.from_crs(4326,32644,always_xy=True).transform
    unproject=Transformer.from_crs(32644,4326,always_xy=True).transform
    rivers=transform(project,unary_union([shape(f['geometry']) for f in load('rivers.geojson')['features']]))
    basin=transform(project,unary_union([shape(f['geometry']) for f in load('catchments.geojson')['features']]))
    geometry=transform(unproject,rivers.buffer(150).intersection(basin))
    return {'type':'FeatureCollection','features':[{'type':'Feature','geometry':mapping(geometry),
        'properties':{'distance_m':150,'status':'DERIVED STATIC',
            'method':'Candidate exposure screening corridor; not a flood inundation boundary'}}]}

def graph_for(pilot):
    graph=nx.DiGraph()
    graph.add_nodes_from(l['id'] for l in pilot['locations'])
    graph.add_edges_from((e['upstream'],e['downstream']) for e in pilot['edges'])
    if not nx.is_directed_acyclic_graph(graph): raise ValueError('Watershed network must be acyclic')
    return graph

class LocalSpatial:
    """Explicit memory-demo/test adapter. Compose uses PostGISSpatial instead."""
    def __init__(self):
        load=lambda name:json.loads((ROOT/'data/processed'/name).read_text(encoding='utf8'))
        self.catchments={f['properties']['id']:shape(f['geometry']) for f in load('catchments.geojson')['features']}
        self.assets=load('infrastructure.geojson')['features']
        self.project=Transformer.from_crs(4326,32644,always_xy=True).transform
        self.rivers=transform(self.project,unary_union([shape(f['geometry']) for f in load('rivers.geojson')['features']]))

    def exposure(self,location_id):
        polygon=self.catchments[location_id]
        result=[]
        for f in self.assets:
            geometry=shape(f['geometry'])
            if polygon.intersects(geometry) and transform(self.project,geometry).distance(self.rivers)<=150:
                result.append(f['properties'])
        return sorted(result,key=lambda a:a['id'])

def apply_decisions(pilot,predictions,spatial):
    graph=graph_for(pilot)
    routed={}
    for node in nx.topological_sort(graph):
        current=predictions[node]
        candidates=[]
        if current['risk_score'] is not None:
            candidates.append((current['risk_score'],node,current['confidence']))
        for parent in graph.predecessors(node):
            p=routed[parent]
            if p['routed_risk'] is not None:
                candidates.append((p['routed_risk']*.92,p['dominant_origin'],p['routed_confidence']*.95))
        risk,origin,confidence=max(candidates) if candidates else (None,None,0.)
        level='Unknown' if risk is None else 'Critical' if risk>=.8 else 'Warning' if risk>=.55 else 'Watch' if risk>=.25 else 'Normal'
        assets=spatial.exposure(node)
        counts={kind:sum(a['kind']==kind for a in assets) for kind in ('settlement','road','bridge','hospital')}
        impact_weight=1+math.log1p(counts['settlement']+counts['road']+2*counts['bridge']+5*counts['hospital'])
        priority=(risk or 0)*impact_weight*confidence
        routed[node]={**current,'routed_risk':None if risk is None else round(risk,5),
            'routed_confidence':round(confidence,4),'dominant_origin':origin,'alert_level':level,
            'recommendation':RECOMMENDATIONS[level],'advisory_only':True,
            'manual_review':level in ('Warning','Critical','Unknown') or current['quality']['stale'],
            'downstream':sorted(nx.descendants(graph,node)),
            'exposure':{'assets':assets,'counts':counts,'population':None,
                'method':'Catchment intersection and 150m mapped-river proximity; candidate exposure, not inundation'},
            'priority':round(priority,4),'priority_formula':'routed risk × mapped impact weight × routed confidence',
            'routing_method':'DEM graph with illustrative 0.92 per-edge attenuation; no physical travel-time claim'}
    ordered=sorted(routed,key=lambda k:(-routed[k]['priority'],k))
    for rank,key in enumerate(ordered,1): routed[key]['rank']=rank
    return routed
