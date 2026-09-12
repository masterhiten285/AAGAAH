"""Stage 1: interchangeable providers; unavailable integrations fail explicitly."""
from typing import Protocol
from datetime import datetime, timedelta, timezone
import json
import math
from .config import ROOT
from .contracts import Reading, Status

START = datetime(2013, 6, 15, tzinfo=timezone.utc)

class Provider(Protocol):
    def read(self, locations: list[dict], as_of: datetime) -> list[Reading]: ...

class PlannedProvider:
    def __init__(self, name: str, reason: str): self.name, self.reason = name, reason
    def read(self, locations, as_of):
        raise RuntimeError(f'{self.name} is PLANNED: {self.reason}; choose an explicit replay provider')

class SyntheticReplay:
    """Deterministic heavy-rain scenario; dates provide narrative context only."""
    def read(self, locations, as_of):
        step = int((as_of - START).total_seconds() / 3600)
        rows = []
        for index, loc in enumerate(locations):
            for t in range(-24, step + 1):
                pulse = math.exp(-((t - 30 - index * 1.1) / 9) ** 2)
                rain = 0.6 + (29 - index * 1.4) * pulse
                date = START + timedelta(hours=t)
                rows.append(Reading(location_id=loc['id'], observed_at=date, available_at=date,
                    source='synthetic-heavy-rain-v1', status=Status.REPLAY, synthetic=True,
                    rainfall_mm=round(rain, 3), soil_moisture=round(0.3 + 0.64 * pulse, 3),
                    water_level_m=round(0.7 + 4.5 * pulse, 3), forecast_rain_mm=round(rain * 1.12, 3),
                    forecast_issued_at=date))
        return rows

class OpenMeteoArchiveReplay:
    """Actual cached reanalysis for one grid point; never replicated as other stations."""
    def read(self, locations, as_of):
        data = json.loads((ROOT / 'data/raw/openmeteo_archive.json').read_text(encoding='utf8'))['hourly']
        location = next(l for l in locations if l['id'] == 'kedarnath')
        rows = []
        for i, value in enumerate(data['time']):
            date = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
            if date <= as_of:
                # available_at is replay availability, not a claim of historical operational availability.
                rows.append(Reading(location_id=location['id'], observed_at=date, available_at=date,
                    source='open-meteo-reanalysis-cached', status=Status.REPLAY,
                    rainfall_mm=data['precipitation'][i], soil_moisture=data['soil_moisture_0_to_7cm'][i]))
        return rows

PROVIDERS = {name: PlannedProvider(name, reason) for name, reason in {
    'imerg': 'PPS requires free registration; anonymous probe HTTP 401',
    'imd': 'Download form verified; historical file ingestion not yet activated',
    'mosdac': 'Approved login and exact mountain-valid product required',
    'cwc': 'Station inventory is not a verified gauge time-series endpoint',
    'sentinel1': 'Catalog verified; scene download and terrain correction pending',
    'jrc': 'Static context product, not a live hydrological observation',
}.items()}
