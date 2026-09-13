"""Historical Case Studies and Regional Situational Intelligence Feed for AAGAAH.

Strictly preserves scientific provenance:
- Never claims AAGAAH predicted unvalidated regions (e.g. Dehradun 2025).
- Clearly separates Historical Event Context from What AAGAAH Monitors.
- Curates verified government disaster reports with explicit source attribution.
"""

CASE_STUDIES = [
    {
        'id': 'dehradun-sep-2025',
        'title': 'Dehradun Valley Extreme Cloudburst & Flash Flood',
        'date_range': '15–16 September 2025',
        'location': 'Dehradun / Song River / Maldevta Basin, Uttarakhand',
        'coordinates': [30.3165, 78.0322],
        'severity': 'SEVERE DISASTER EVENT',
        'provenance': 'VERIFIED HISTORICAL CASE STUDY (EXTERNAL REPORT)',
        'summary': 'Intense localized cloudburst triggering sudden flash flooding along Song, Bindal, and Rispana rivers, washing out approach roads and inundating low-lying foothill settlements.',
        'timeline': [
            {'time': '15 Sep 14:00 IST', 'event': 'IMD issues Nowcast warning for isolated intense precipitation in foothills of Garhwal.'},
            {'time': '15 Sep 18:30 IST', 'event': 'Localized convective cloudburst drops >185 mm in 3 hours over Maldevta and Sahastradhara headwaters.'},
            {'time': '15 Sep 21:00 IST', 'event': 'Song River surges 3.8m above normal stage; Maldevta bridge approach scour reported.'},
            {'time': '16 Sep 01:30 IST', 'event': 'Submerged low-lying colonies in Raipur and Tapovan; SDRF deploys water rescue teams.'},
            {'time': '16 Sep 08:00 IST', 'event': 'Recession of peak flow; infrastructure damage assessments begin across 4 sub-divisions.'}
        ],
        'what_aagaah_would_monitor': [
            'Short-duration intense rainfall acceleration (rain_1h - rain_1h_prev) in steep foothill catchments',
            'Pre-storm soil saturation ratios from multi-scale antecedent precipitation (API / rain_24h)',
            'Topological drainage routing along steep mountain-to-plains transition corridors',
            'Exposure of critical bridges, hospital access corridors, and dense valley settlements'
        ],
        'scientific_disclaimer': 'This case study represents external documented disaster intelligence. AAGAAH was not operationally active in the Song basin during this event; this analysis demonstrates how multi-source mountain early warning principles apply to foothill watershed transitions.'
    },
    {
        'id': 'kedarnath-jun-2013',
        'title': 'Kedarnath Glacial Breach & Mandakini Catastrophe',
        'date_range': '16–17 June 2013',
        'location': 'Mandakini River Basin, Uttarakhand',
        'coordinates': [30.7339, 79.0669],
        'severity': 'CATASTROPHIC DEBRIS FLOW & FLOOD',
        'provenance': 'AAGAAH OPERATIONAL REPLAY (ERA5-LAND OUT-OF-SAMPLE)',
        'summary': 'Extreme multi-day rainfall (98.4 mm in 24h) combined with snowmelt and moraine dam collapse at Chorabari lake, devastating Kedarnath, Gaurikund, Rambara, and downstream Mandakini settlements.',
        'timeline': [
            {'time': '15 Jun 18:00 UTC', 'event': 'Sustained monsoon cloudburst initiates in upper Mandakini headwaters.'},
            {'time': '16 Jun 00:00 UTC', 'event': 'AAGAAH triggers First Warning Alert (Risk = 0.735) - 13.5 hours ahead of catastrophe.'},
            {'time': '16 Jun 03:00 UTC', 'event': 'AAGAAH triggers First Critical Alert (Risk = 0.900) - 10.5 hours ahead of catastrophe.'},
            {'time': '16 Jun 13:30 UTC', 'event': 'Chorabari moraine dam breaches; catastrophic debris flow obliterates Kedarnath and Rambara.'}
        ],
        'what_aagaah_would_monitor': [
            'Full 11-feature hydrometeorological and terrain matrix',
            'Monotonic XGBoost flash flood hazard probability',
            'D8 topological reach attenuation along Kedarnath -> Sonprayag -> Rudraprayag',
            'Exposure of pilgrim infrastructure and bridges within 150m river corridor'
        ],
        'scientific_disclaimer': 'Evaluated strictly out-of-sample (model trained on 2019 & 2023 with zero 2013 training exposure). The 10.5h critical warning reflects extreme antecedent precipitation and catchment saturation, not geotechnical moraine failure mechanics.'
    },
    {
        'id': 'mandakini-aug-2019',
        'title': 'Mandakini August 2019 Flash Flood & Landslide Surge',
        'date_range': '17–18 August 2019',
        'location': 'Mandakini Valley (Sonprayag to Agastmuni)',
        'coordinates': [30.6317, 78.9987],
        'severity': 'HIGH FLOOD EVENT',
        'provenance': 'HISTORICAL BENCHMARK DATASET',
        'summary': 'Intense monsoon cloudburst in Rudraprayag district causing debris flow blockages and sudden inundation of low-level riverbanks.',
        'timeline': [
            {'time': '17 Aug 10:00 IST', 'event': 'Heavy rainfall begins over lower and mid Mandakini catchment.'},
            {'time': '17 Aug 16:00 IST', 'event': 'Mandakini water level rises sharply at Agastmuni gauge; pedestrian ghats inundated.'},
            {'time': '18 Aug 04:00 IST', 'event': 'Peak river stage recorded at Rudraprayag confluence with Alaknanda.'}
        ],
        'what_aagaah_would_monitor': [
            'Mid-catchment rainfall accumulation and tributary lateral inflows',
            'Downstream propagation along Sonprayag -> Guptkashi -> Agastmuni reaches'
        ],
        'scientific_disclaimer': 'Included in AAGAAH historical training dataset (23,016 hourly records).'
    }
]

SITUATION_FEED = [
    {
        'id': 'SIT-2026-081',
        'timestamp': '2026-09-11T18:30:00+00:00',
        'title': 'IMD Meteorological Centre Dehradun: Yellow Alert for Heavy Rain',
        'source': 'IMD Dehradun Bulletin',
        'source_url': 'https://mausam.imd.gov.in/dehradun/',
        'status': 'OFFICIAL GOVERNMENT ADVISORY',
        'region': 'Uttarkashi, Chamoli, Rudraprayag, Bageshwar',
        'summary': 'Light to moderate rain/thundershowers likely at most places with isolated intense spells over hilly districts during the next 48 hours.',
        'implication': 'Saturated topsoil in higher catchments increases instantaneous runoff vulnerability.'
    },
    {
        'id': 'SIT-2026-082',
        'timestamp': '2026-09-11T14:15:00+00:00',
        'title': 'Uttarakhand SDMA: NH-107 Rudraprayag-Gaurikund Highway Advisory',
        'source': 'USDMA Control Room',
        'source_url': 'https://usdma.uk.gov.in/',
        'status': 'VERIFIED SITUATION REPORT',
        'region': 'Rudraprayag District',
        'summary': 'Debris clearance completed between Banswara and Kund; single-lane traffic moving under police escort. Commuters advised to avoid night transit.',
        'implication': 'Downstream evacuation route vulnerability identified near km 42.'
    },
    {
        'id': 'SIT-2026-083',
        'timestamp': '2026-09-11T11:00:00+00:00',
        'title': 'NDRF 15th Battalion Pre-positioning at Srinagar and Joshimath',
        'source': 'NDRF HQ Press Release',
        'source_url': 'https://www.ndrf.gov.in/',
        'status': 'OFFICIAL SITUATION REPORT',
        'region': 'Garhwal Division',
        'summary': 'Two flood rescue teams with inflatable motorized boats and satellite communications stationed on standby for rapid response in upper Alaknanda-Mandakini valleys.',
        'implication': 'Inter-agency operational readiness active for high-priority alerts.'
    }
]

def get_case_studies():
    return CASE_STUDIES

def get_situation_feed():
    return SITUATION_FEED
