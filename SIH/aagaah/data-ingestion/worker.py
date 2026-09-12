"""The small scheduler process delegates an atomic replay tick to the API."""
import os
import logging
import httpx
from apscheduler.schedulers.blocking import BlockingScheduler
logging.basicConfig(level=logging.INFO)
def tick():
    try:
        response=httpx.post(os.getenv('AAGAAH_API_URL','http://backend-api:8000')+'/internal/tick',
            headers={'X-Control-Token':os.getenv('AAGAAH_CONTROL_TOKEN','local-demo-only')},timeout=45)
        response.raise_for_status()
        logging.info('Replay step %s',response.json()['step'])
    except httpx.HTTPError:
        logging.exception('Tick failed; persisted replay position will be retried next interval')
if __name__=='__main__':
    scheduler=BlockingScheduler()
    scheduler.add_job(tick,'interval',seconds=int(os.getenv('AAGAAH_INTERVAL_SECONDS','8')),max_instances=1,coalesce=True)
    scheduler.start()
