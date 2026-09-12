from datetime import datetime
import json
import threading
import uuid
from contextlib import contextmanager
from sqlalchemy import create_engine, text, select, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from geoalchemy2 import Geometry
from .config import ROOT

class Base(DeclarativeBase): pass
class ReplayState(Base):
    __tablename__='replay_state'
    id: Mapped[int]=mapped_column(primary_key=True)
    step: Mapped[int]=mapped_column(default=0)
    running: Mapped[bool]=mapped_column(default=False)
    run_id: Mapped[str]=mapped_column(String(36))
    snapshot: Mapped[dict]=mapped_column(JSONB)

class Observation(Base):
    __tablename__='sensor_readings'
    id: Mapped[int]=mapped_column(primary_key=True)
    location_id: Mapped[str]=mapped_column(String(80),index=True)
    observed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True)
    source: Mapped[str]=mapped_column(String(100))
    payload: Mapped[dict]=mapped_column(JSONB)
    __table_args__=(UniqueConstraint('location_id','observed_at','source',name='uq_observation'),)

class RiskHistory(Base):
    __tablename__='risk_history'
    id: Mapped[int]=mapped_column(primary_key=True)
    run_id: Mapped[str]=mapped_column(String(36),index=True)
    location_id: Mapped[str]=mapped_column(String(80),index=True)
    as_of: Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True)
    payload: Mapped[dict]=mapped_column(JSONB)

class Catchment(Base):
    __tablename__='catchments'
    id: Mapped[str]=mapped_column(String(80),primary_key=True)
    properties: Mapped[dict]=mapped_column(JSONB)
    geom: Mapped[object]=mapped_column(Geometry('GEOMETRY',srid=4326,spatial_index=True))

class Infrastructure(Base):
    __tablename__='infrastructure'
    id: Mapped[str]=mapped_column(String(100),primary_key=True)
    properties: Mapped[dict]=mapped_column(JSONB)
    geom: Mapped[object]=mapped_column(Geometry('GEOMETRY',srid=4326,spatial_index=True))

class River(Base):
    __tablename__='rivers'
    id: Mapped[int]=mapped_column(primary_key=True)
    geom: Mapped[object]=mapped_column(Geometry('GEOMETRY',srid=4326,spatial_index=True))

class NetworkEdge(Base):
    __tablename__='network_edges'
    upstream: Mapped[str]=mapped_column(ForeignKey('catchments.id'),primary_key=True)
    downstream: Mapped[str]=mapped_column(ForeignKey('catchments.id'),primary_key=True)
    properties: Mapped[dict]=mapped_column(JSONB)

class MemoryRepository:
    """Explicit nonpersistent local demo. Never selected by database failure."""
    mode='MEMORY DEMO — PostGIS unavailable'
    def __init__(self): self.state=None; self.history=[]; self.lock=threading.RLock()
    @contextmanager
    def transaction(self):
        with self.lock: yield self
    def load(self): return self.state
    def save(self,state,readings):
        self.state=state
        # Keep one record per replay instant, including after deterministic reset.
        self.history=[h for h in self.history if h['as_of']!=state['snapshot']['as_of']]
        self.history.append(state['snapshot'])
        self.history=self.history[-96:]
    def timeseries(self,location_id):
        return sorted([{'as_of':s['as_of'],'risk_score':l['risk_score'],'rain_1h':l['features']['rain_1h']}
            for s in self.history for l in s['locations'] if l['id']==location_id and s['as_of']<=self.state['snapshot']['as_of']],key=lambda x:x['as_of'])

class PostGISSpatial:
    def __init__(self,engine): self.engine=engine
    def exposure(self,location_id):
        with self.engine.connect() as conn:
            return list(conn.execute(text('''SELECT DISTINCT i.properties FROM infrastructure i
                JOIN catchments c ON c.id=:id AND ST_Intersects(c.geom,i.geom)
                WHERE EXISTS (SELECT 1 FROM rivers r WHERE ST_DWithin(i.geom::geography,r.geom::geography,150))
                ORDER BY i.properties'''),{'id':location_id}).scalars())

class PostgresRepository:
    mode='PostgreSQL + PostGIS'
    def __init__(self,url):
        self.engine=create_engine(url,pool_pre_ping=True)
        self.session=None
        self.lock=threading.RLock()
        with self.engine.connect() as conn: conn.execute(text('SELECT PostGIS_Version()'))
    @contextmanager
    def transaction(self):
        with self.lock,Session(self.engine) as session,session.begin():
            session.execute(text('SELECT pg_advisory_xact_lock(1042026)'))
            self.session=session
            try: yield self
            finally: self.session=None
    def load(self):
        # The lock must be acquired before inspecting the active transaction/session.
        # Concurrent GET handlers must never share a different thread's SQLAlchemy Session.
        with self.lock:
            if self.session is not None:
                state=self.session.get(ReplayState,1)
                return None if state is None else {k:getattr(state,k) for k in ('step','running','run_id','snapshot')}
            with Session(self.engine) as session:
                state=session.get(ReplayState,1)
                return None if state is None else {k:getattr(state,k) for k in ('step','running','run_id','snapshot')}
    def save(self,state,readings):
        from sqlalchemy.dialects.postgresql import insert
        if self.session is None: raise RuntimeError('Write requires a transaction')
        self.session.merge(ReplayState(id=1,**state))
        for row in readings:
            self.session.execute(insert(Observation).values(location_id=row.location_id,observed_at=row.observed_at,
                source=row.source,payload=row.model_dump(mode='json')).on_conflict_do_nothing(constraint='uq_observation'))
        for row in state['snapshot']['locations']:
            self.session.add(RiskHistory(run_id=state['run_id'],location_id=row['id'],
                as_of=datetime.fromisoformat(state['snapshot']['as_of']),payload=row))
    def timeseries(self,location_id):
        with self.engine.connect() as conn:
            rows=conn.execute(text('''SELECT DISTINCT ON (as_of) as_of,payload FROM risk_history
                WHERE location_id=:id AND as_of <= (SELECT (snapshot->>'as_of')::timestamptz FROM replay_state WHERE id=1)
                ORDER BY as_of DESC,id DESC LIMIT 96'''),{'id':location_id}).all()
        return sorted([{'as_of':r.as_of.isoformat(),'risk_score':r.payload['risk_score'],
                        'rain_1h':r.payload['features']['rain_1h']} for r in rows],key=lambda x:x['as_of'])

def seed(engine):
    with engine.begin() as conn:
        for filename,table in [('catchments.geojson','catchments'),('infrastructure.geojson','infrastructure'),('rivers.geojson','rivers')]:
            features=json.loads((ROOT/'data/processed'/filename).read_text(encoding='utf8'))['features']
            for idx,f in enumerate(features):
                if table=='rivers':
                    conn.execute(text('INSERT INTO rivers(id,geom) VALUES (:id,ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326)) ON CONFLICT (id) DO NOTHING'),{'id':idx,'geom':json.dumps(f['geometry'])})
                else:
                    # Table identifiers are fixed internal constants, never request parameters.
                    conn.execute(text(f'INSERT INTO {table}(id,properties,geom) VALUES (:id,CAST(:props AS jsonb),ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326)) ON CONFLICT (id) DO NOTHING'),
                        {'id':f['properties']['id'],'props':json.dumps(f['properties']),'geom':json.dumps(f['geometry'])})
        pilot=json.loads((ROOT/'data/processed/pilot.json').read_text(encoding='utf8'))
        for edge in pilot['edges']:
            conn.execute(text('INSERT INTO network_edges(upstream,downstream,properties) VALUES (:u,:d,CAST(:p AS jsonb)) ON CONFLICT DO NOTHING'),{'u':edge['upstream'],'d':edge['downstream'],'p':json.dumps(edge)})
