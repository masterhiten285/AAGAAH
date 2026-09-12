from datetime import timedelta
import math
import pytest
from pydantic import ValidationError
from aagaah.providers import SyntheticReplay, START
from aagaah.processing import features_at
from aagaah.contracts import Reading

LOCATION = {'id': 'test', 'terrain': {'slope_deg': 25., 'elevation_m': 2000., 'river_distance_m': 70., 'upstream_area_km2': 10.}}

def test_causal_windows_missing_and_stale():
    rows = SyntheticReplay().read([LOCATION], START)
    f, q = features_at(rows, LOCATION, START)
    assert f['rain_24h'] > f['rain_3h'] > f['rain_1h']
    assert q['coverage']['24'] == 1
    f, q = features_at(rows[:-1], LOCATION, START)
    assert math.isnan(f['rain_1h']) and q['coverage']['24'] == 23/24
    assert features_at(rows, LOCATION, START + timedelta(hours=4))[1]['stale']

def test_future_and_late_data_do_not_leak():
    rows = SyntheticReplay().read([LOCATION], START + timedelta(hours=5))
    now = features_at(rows, LOCATION, START)
    baseline = features_at(SyntheticReplay().read([LOCATION], START), LOCATION, START)
    assert now[0] == baseline[0] and now[1]['rejected'] == 5
    late = rows[24].model_copy(update={'available_at': START + timedelta(hours=1), 'rainfall_mm': 300})
    assert features_at(rows + [late], LOCATION, START)[0]['rain_1h'] == baseline[0]['rain_1h']

def test_provenance_validation():
    row = SyntheticReplay().read([LOCATION], START)[-1].model_dump()
    with pytest.raises(ValidationError): Reading(**{**row, 'status': 'VERIFIED LIVE'})
    with pytest.raises(ValidationError): Reading(**{**row, 'rainfall_mm': -1})
    with pytest.raises(ValidationError): Reading(**{**row, 'rainfall_mm': float('nan')})
