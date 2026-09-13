"""Watershed registry for Himalayan river basins.

Differentiates between:
- Operational Model Coverage (Active Pilot): Mandakini Basin
- Regional Context / Planned Expansion: Alaknanda, Bhagirathi, Yamuna
"""

WATERSHEDS = [
    {
        'id': 'mandakini',
        'name': 'Mandakini River Basin',
        'state': 'Uttarakhand',
        'coverage_status': 'OPERATIONAL MODEL COVERAGE',
        'is_active_pilot': True,
        'area_km2': 1637.9,
        'elevation_range_m': [610, 3584],
        'primary_reach': 'Kedarnath -> Gaurikund -> Sonprayag -> Rudraprayag',
        'stations_count': 7,
        'center': [30.55, 79.02],
        'zoom': 10.5,
        'description': 'High-altitude steep glacial and fluvial catchment with acute debris flow susceptibility and narrow valley settlements.'
    },
    {
        'id': 'alaknanda',
        'name': 'Upper Alaknanda Basin',
        'state': 'Uttarakhand',
        'coverage_status': 'REGIONAL CONTEXT / PLANNED',
        'is_active_pilot': False,
        'area_km2': 11050.0,
        'elevation_range_m': [610, 7816],
        'primary_reach': 'Badrinath -> Joshimath -> Chamoli -> Karnaprayag -> Rudraprayag',
        'stations_count': 0,
        'center': [30.55, 79.45],
        'zoom': 9.2,
        'description': 'Major Himalayan tributary draining Nanda Devi and Trishul massifs; planned for model deployment following local station calibration.'
    },
    {
        'id': 'bhagirathi',
        'name': 'Bhagirathi Basin',
        'state': 'Uttarakhand',
        'coverage_status': 'REGIONAL CONTEXT / PLANNED',
        'is_active_pilot': False,
        'area_km2': 7530.0,
        'elevation_range_m': [470, 7000],
        'primary_reach': 'Gangotri -> Uttarkashi -> Tehri -> Devprayag',
        'stations_count': 0,
        'center': [30.70, 78.60],
        'zoom': 9.2,
        'description': 'Source stream of Ganga river; high landslide dam hazard and glacial lake monitoring requirement.'
    },
    {
        'id': 'yamuna_upper',
        'name': 'Upper Yamuna Basin',
        'state': 'Uttarakhand / HP',
        'coverage_status': 'REGIONAL CONTEXT / PLANNED',
        'is_active_pilot': False,
        'area_km2': 4200.0,
        'elevation_range_m': [550, 6387],
        'primary_reach': 'Yamunotri -> Barkot -> Naugaon -> Dakpathar',
        'stations_count': 0,
        'center': [30.90, 78.20],
        'zoom': 9.2,
        'description': 'Western Garhwal mountain catchment; prone to intense localized monsoon cloudbursts and road washouts.'
    }
]

def get_watersheds():
    return WATERSHEDS
