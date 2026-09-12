"""Stages 2 and 3: causal validation and hourly feature windows."""
from datetime import datetime, timedelta
import math
import numpy as np
import pandas as pd
from .contracts import Reading

FEATURES = ['rain_1h', 'rain_3h', 'rain_6h', 'rain_24h', 'soil_moisture',
            'water_level_m', 'forecast_trend', 'slope_deg', 'elevation_m',
            'river_distance_m', 'upstream_area_km2']

def features_at(readings: list[Reading], location: dict, as_of: datetime):
    accepted, rejected = {}, 0
    for r in readings:
        if r.location_id != location['id']: continue
        # No future observations, late-arriving revisions, or future-issued forecasts.
        if r.observed_at > as_of or r.available_at > as_of or r.interval_minutes != 60:
            rejected += 1
            continue
        key = r.observed_at
        if key not in accepted or accepted[key].available_at <= r.available_at:
            accepted[key] = r
    rows = sorted(accepted.values(), key=lambda r: r.observed_at)
    latest = rows[-1] if rows else None
    age = (as_of - latest.observed_at).total_seconds() / 3600 if latest else 999.0
    windows = {}
    coverage = {}
    for hours in (1, 3, 6, 24):
        expected = pd.date_range(end=as_of, periods=hours, freq='h')
        values = pd.Series({r.observed_at: r.rainfall_mm for r in rows}, dtype='float64').reindex(expected)
        coverage[str(hours)] = float(values.notna().sum() / hours)
        # Never silently interpret missing rain as zero, or scale partial sums to a full window.
        windows[f'rain_{hours}h'] = float(values.sum()) if values.notna().all() else np.nan
    def recent(field):
        for row in reversed(rows):
            if (as_of - row.observed_at).total_seconds() > 7200: break
            value = getattr(row, field)
            if value is not None: return value
        return np.nan
    forecast = np.nan
    if latest and latest.forecast_rain_mm is not None and latest.forecast_issued_at <= as_of and age <= 2:
        base = windows['rain_1h']
        if math.isfinite(base): forecast = latest.forecast_rain_mm - base
    terrain = location['terrain']
    features = {**windows, 'soil_moisture': recent('soil_moisture'), 'water_level_m': recent('water_level_m'),
                'forecast_trend': forecast, **{k: terrain[k] for k in FEATURES[7:]}}
    missing = [k for k, v in features.items() if not math.isfinite(v)]
    recent_rows = [r for r in rows if r.observed_at > as_of - timedelta(hours=24)]
    return features, {'age_hours': round(age, 2), 'coverage': coverage, 'missing_features': missing,
                      'latest_observed_at': latest.observed_at.isoformat() if latest else None,
                      'latest_available_at': latest.available_at.isoformat() if latest else None,
                      'rejected': rejected, 'stale': age > 2, 'no_data': latest is None,
                      'statuses': sorted({r.status.value for r in recent_rows}),
                      'synthetic': any(r.synthetic for r in recent_rows),
                      'sources': sorted({r.source for r in recent_rows})}
