"""Open-Meteo client providing real-world weather, soil moisture, and forecast data.

Fetches:
1. Live/Recent hourly observations and forecasts (api.open-meteo.com).
2. Historical reanalysis archive (archive-api.open-meteo.com).
"""
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import urllib.parse
import urllib.request
from .config import ROOT
from .contracts import Reading, Status

logger = logging.getLogger('aagaah.openmeteo')
RAW_DIR = ROOT / 'data' / 'raw'

def fetch_openmeteo_archive(lat: float, lon: float, start_date: str, end_date: str, use_cache: bool = True) -> dict:
    """Fetch hourly historical reanalysis (precipitation, soil moisture) from Open-Meteo Archive API."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = RAW_DIR / f'openmeteo_archive_{lat:.4f}_{lon:.4f}_{start_date}_{end_date}.json'
    if use_cache and cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding='utf-8'))
        except Exception:
            pass

    params = {
        'latitude': f'{lat:.4f}',
        'longitude': f'{lon:.4f}',
        'start_date': start_date,
        'end_date': end_date,
        'hourly': 'precipitation,rain,soil_moisture_0_to_7cm,soil_moisture_7_to_28cm,temperature_2m',
        'timezone': 'UTC'
    }
    url = f'https://archive-api.open-meteo.com/v1/archive?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'AAGAAH-EarlyWarning/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode('utf-8'))
    cache_file.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return payload

def fetch_openmeteo_live(lat: float, lon: float, past_days: int = 2, forecast_days: int = 2) -> dict:
    """Fetch recent past and forecast hourly weather and soil moisture from Open-Meteo Forecast API."""
    params = {
        'latitude': f'{lat:.4f}',
        'longitude': f'{lon:.4f}',
        'past_days': past_days,
        'forecast_days': forecast_days,
        'hourly': 'precipitation,rain,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,temperature_2m',
        'timezone': 'UTC'
    }
    url = f'https://api.open-meteo.com/v1/forecast?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'AAGAAH-EarlyWarning/1.0'})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode('utf-8'))

def parse_openmeteo_to_readings(location_id: str, payload: dict, is_historical: bool = True) -> list[Reading]:
    """Convert an Open-Meteo hourly response to a validated list of Reading objects."""
    hourly = payload.get('hourly', {})
    times = hourly.get('time', [])
    precip = hourly.get('precipitation', [])
    soil_0_7 = hourly.get('soil_moisture_0_to_7cm') or hourly.get('soil_moisture_0_to_1cm') or []
    
    readings: list[Reading] = []
    now = datetime.now(timezone.utc)

    for i, t_str in enumerate(times):
        dt = datetime.fromisoformat(t_str).replace(tzinfo=timezone.utc)
        p_val = float(precip[i]) if i < len(precip) and precip[i] is not None else 0.0
        p_val = max(0.0, min(500.0, p_val))
        
        s_val = float(soil_0_7[i]) if i < len(soil_0_7) and soil_0_7[i] is not None else None
        if s_val is not None:
            s_val = max(0.0, min(1.0, s_val))

        # In historical reanalysis or past observations, available_at is valid after observed_at
        avail = dt if is_historical or dt <= now else now
        if avail < dt:
            avail = dt

        status = Status.REPLAY if is_historical else Status.LIVE
        # Determine 1-step ahead forecast if in the past
        next_precip = float(precip[i+1]) if i + 1 < len(precip) and precip[i+1] is not None else None
        
        readings.append(Reading(
            location_id=location_id,
            observed_at=dt,
            available_at=avail,
            source='open-meteo-archive' if is_historical else 'open-meteo-live',
            status=status,
            synthetic=False,
            rainfall_mm=p_val,
            soil_moisture=s_val,
            water_level_m=None,
            forecast_rain_mm=max(0.0, next_precip) if next_precip is not None else None,
            forecast_issued_at=dt if next_precip is not None else None,
            interval_minutes=60
        ))
    return readings
