import json
import logging
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
import redis
from .config import ROOT, Settings
from .contracts import PredictRequest, ReplayControl
from .providers import SyntheticReplay, START
from .model import Models
from .spatial import LocalSpatial
from .db import MemoryRepository, PostgresRepository, PostGISSpatial
from .pipeline import run_pipeline

logger=logging.getLogger('aagaah')

def create_app(settings: Settings | None = None):
    settings=settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        app.state.pilot=json.loads((ROOT/'data/processed/pilot.json').read_text(encoding='utf8'))
        app.state.models=Models()
        if settings.demo_memory:
            app.state.repo=MemoryRepository(); app.state.spatial=LocalSpatial()
        elif settings.database_url:
            app.state.repo=PostgresRepository(settings.database_url)
            app.state.spatial=PostGISSpatial(app.state.repo.engine)
        else:
            raise RuntimeError('Set AAGAAH_DATABASE_URL or explicitly enable AAGAAH_DEMO_MEMORY=true')
        app.state.cache=redis.Redis.from_url(settings.redis_url,decode_responses=True,socket_connect_timeout=1,socket_timeout=1) if settings.redis_url else None
        with app.state.repo.transaction() as repo:
            if repo.load() is None: compute(0,False,repo)
        scheduler=BackgroundScheduler()
        if settings.schedule:
            scheduler.add_job(tick,'interval',seconds=settings.interval_seconds,max_instances=1,coalesce=True)
            scheduler.start()
        yield
        if scheduler.running: scheduler.shutdown(wait=True)
        if app.state.cache: app.state.cache.close()
        if hasattr(app.state.repo,'engine'): app.state.repo.engine.dispose()

    app=FastAPI(title='AAGAAH',version='0.1.0',description='Explicitly labeled Himalayan replay demonstration.',lifespan=lifespan)
    app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=False,
                       allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Control-Token'])

    def compute(step,running,repo):
        date=START+timedelta(hours=step)
        readings=SyntheticReplay().read(app.state.pilot['locations'],date)
        snapshot=run_pipeline(app.state.pilot,readings,date,app.state.models,app.state.spatial)
        run_id=str(uuid.uuid4())
        snapshot.update(run_id=run_id,step=step,running=running,storage=repo.mode)
        state={'step':step,'running':running,'run_id':run_id,'snapshot':snapshot}
        repo.save(state,readings)
        return snapshot

    def tick():
        with app.state.repo.transaction() as repo:
            state=repo.load()
            if state['running']:
                return compute(min(state['step']+1,71),state['step']<70,repo)
            return state['snapshot']

    def authorize(x_control_token: str | None = Header(default=None)):
        if not x_control_token or not secrets.compare_digest(x_control_token,settings.control_token):
            raise HTTPException(401,'Invalid demo control token')

    @app.get('/health')
    def health():
        try: app.state.repo.load()
        except Exception:
            logger.exception('Database health check failed')
            return JSONResponse(status_code=503,content={'status':'unavailable','database':'unavailable'})
        cache='disabled'
        if app.state.cache:
            try: app.state.cache.ping(); cache='ready'
            except redis.RedisError: cache='unavailable; database remains authoritative'
        return {'status':'demo' if settings.demo_memory else 'ready','storage':app.state.repo.mode,
                'redis':cache,'model_status':'MOCKED','scientific_readiness':False}

    @app.get('/pilot')
    def pilot(): return app.state.pilot

    @app.get('/sources')
    def sources(): return json.loads((ROOT/'data/source-registry.json').read_text(encoding='utf8'))

    @app.get('/model-card')
    def model_card(): return app.state.models.card

    @app.get('/dashboard')
    def dashboard():
        # Read committed run ID before using Redis: a failed cache invalidation cannot serve an old run.
        state=app.state.repo.load(); snapshot=state['snapshot']
        cache=app.state.cache
        if cache:
            try:
                key='snapshot:'+state['run_id']
                cached=cache.get(key)
                if cached: return json.loads(cached)
                cache.setex(key,60,json.dumps(snapshot))
            except redis.RedisError: logger.warning('Redis unavailable; serving committed PostgreSQL snapshot')
        return snapshot

    @app.get('/map/terrain.png')
    def terrain_image(): return FileResponse(ROOT/'data/processed/hillshade.png',media_type='image/png')

    @app.get('/map/{layer}')
    def layer(layer: str):
        if layer not in ('catchments','rivers','flowpaths','infrastructure'): raise HTTPException(404,'Unknown map layer')
        return json.loads((ROOT/f'data/processed/{layer}.geojson').read_text(encoding='utf8'))

    @app.get('/locations/{location_id}/history')
    def history(location_id: str):
        if location_id not in {l['id'] for l in app.state.pilot['locations']}: raise HTTPException(404,'Unknown location')
        return app.state.repo.timeseries(location_id)

    @app.post('/predict')
    def predict(request: PredictRequest):
        known={l['id'] for l in app.state.pilot['locations']}
        if any(r.location_id not in known for r in request.readings): raise HTTPException(422,'Unknown pilot location')
        return run_pipeline(app.state.pilot,request.readings,request.as_of,app.state.models,app.state.spatial)

    @app.post('/replay/control',dependencies=[Depends(authorize)])
    def control(command: ReplayControl):
        with app.state.repo.transaction() as repo:
            state=repo.load(); step,running=state['step'],state['running']
            if command.action=='play': running=step<71
            elif command.action=='pause': running=False
            elif command.action=='reset': step,running=0,False
            elif command.action=='step': step,running=min(71,step+1),False
            elif command.action=='seek':
                if command.step is None: raise HTTPException(422,'Seek requires step')
                step,running=command.step,False
            return compute(step,running,repo)

    @app.post('/internal/tick',dependencies=[Depends(authorize)])
    def scheduled_tick(): return tick()

    return app

app=create_app()
