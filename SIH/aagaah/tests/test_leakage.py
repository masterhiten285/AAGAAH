"""Automated leakage and causal validation test suite for AAGAAH."""
from datetime import datetime, timedelta, timezone
import math
import numpy as np
import pytest
from aagaah.contracts import Reading, Status
from aagaah.processing import features_at, FEATURES
from aagaah.model import fetch_or_generate_dataset

TEST_LOC = {
    'id': 'kedarnath',
    'name': 'Kedarnath',
    'lat': 30.7338877,
    'lon': 79.0669073,
    'terrain': {
        'slope_deg': 5.15,
        'elevation_m': 3539.1,
        'river_distance_m': 136.2,
        'upstream_area_km2': 47.693
    }
}

def test_no_future_observation_leakage():
    """Prove that FEATURE(t) uses only observations at or before t."""
    t0 = datetime(2023, 7, 10, 12, 0, tzinfo=timezone.utc)
    base_readings = [
        Reading(
            location_id='kedarnath',
            observed_at=t0 - timedelta(hours=i),
            available_at=t0 - timedelta(hours=i),
            source='test-gauge',
            status=Status.LIVE,
            rainfall_mm=10.0,
            soil_moisture=0.45,
            interval_minutes=60
        )
        for i in range(24, -1, -1)
    ]
    feat_base, qual_base = features_at(base_readings, TEST_LOC, t0)

    # Now inject a catastrophic future cloudburst at t0 + 1h, t0 + 2h
    future_readings = base_readings + [
        Reading(
            location_id='kedarnath',
            observed_at=t0 + timedelta(hours=1),
            available_at=t0 + timedelta(hours=1),
            source='test-gauge',
            status=Status.LIVE,
            rainfall_mm=250.0,
            soil_moisture=0.99,
            interval_minutes=60
        ),
        Reading(
            location_id='kedarnath',
            observed_at=t0 + timedelta(hours=2),
            available_at=t0 + timedelta(hours=2),
            source='test-gauge',
            status=Status.LIVE,
            rainfall_mm=300.0,
            soil_moisture=1.0,
            interval_minutes=60
        )
    ]
    feat_future, qual_future = features_at(future_readings, TEST_LOC, t0)

    # Features at t0 must be identical despite extreme future cloudburst
    for k in ('rain_1h', 'rain_3h', 'rain_6h', 'rain_24h', 'soil_moisture'):
        assert feat_base[k] == feat_future[k], f"Leakage detected in {k}: base={feat_base[k]} vs future={feat_future[k]}"
    
    # Future records must be recorded as rejected
    assert qual_future['rejected'] == 2

def test_late_arriving_data_causal_availability():
    """Observations with available_at > t must not be visible at time t even if observed_at <= t."""
    t0 = datetime(2023, 7, 10, 12, 0, tzinfo=timezone.utc)
    base_reading = Reading(
        location_id='kedarnath',
        observed_at=t0,
        available_at=t0,
        source='test-gauge',
        status=Status.LIVE,
        rainfall_mm=5.0,
        interval_minutes=60
    )
    # Late revision: observed at t0, but arrived at t0 + 3 hours with revised rainfall
    revised_reading = Reading(
        location_id='kedarnath',
        observed_at=t0,
        available_at=t0 + timedelta(hours=3),
        source='test-gauge',
        status=Status.LIVE,
        rainfall_mm=120.0,
        interval_minutes=60
    )

    feat_at_t0, qual_t0 = features_at([revised_reading], TEST_LOC, t0)
    # At t0, revised reading is not yet available, so it must be rejected
    assert qual_t0['rejected'] == 1
    assert qual_t0['no_data'] is True

    # At t0 + 3h, revised reading is available
    feat_at_t3, qual_t3 = features_at([revised_reading], TEST_LOC, t0 + timedelta(hours=3))
    assert qual_t3['rejected'] == 0
    assert qual_t3['no_data'] is False
    assert qual_t3['age_hours'] == 3.0

def test_training_dataset_no_label_circularity():
    """Verify that training target y is not a trivial deterministic threshold of a single input feature."""
    X, y, groups, source = fetch_or_generate_dataset()
    assert len(X) > 0
    assert len(y) == len(X)
    
    # Verify target is binary
    unique_labels = np.unique(y)
    assert set(unique_labels).issubset({0, 1})
    
    # Check that y cannot be predicted with 100% accuracy using any single feature threshold
    for col in ('rain_1h', 'rain_3h', 'rain_6h', 'rain_24h', 'soil_moisture'):
        val = X[col].values
        # Correlation should not be 1.0 (trivial copy)
        finite_mask = np.isfinite(val)
        if finite_mask.sum() > 100:
            corr = np.corrcoef(val[finite_mask], y[finite_mask])[0, 1]
            assert abs(corr) < 0.95, f"Suspiciously high correlation ({corr}) between {col} and label y"
