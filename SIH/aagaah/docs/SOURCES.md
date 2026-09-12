# Data source investigation

Checked 12 September 2026 local time (raw probes use UTC). VERIFIED LIVE means a specified endpoint/payload was actually reached during investigation; it does not mean the dashboard is receiving live sensor observations. Static samples remain static. PLANNED means the required usable product integration is not active. REPLAY identifies cached or simulated temporal playback. MOCKED identifies generated values/models.

No source has a measured uptime guarantee from this short investigation. Unknown means unverified, not unrestricted. Runtime sources and input provenance remain explicit.

## NASA GPM IMERG — PLANNED

- **role**: Rainfall
- **public access**: Metadata public; tested PPS GIS directory returned HTTP 401.
- **authentication**: Free PPS registration for tested GIS route; Earthdata login for GES DISC routes.
- **api key**: No paid API key; account credentials required by download route.
- **free**: NASA precipitation products free; account needed for tested route.
- **licence**: NASA open-data attribution; cite product/version and GPM/IMERG documentation.
- **spatial resolution**: 0.1 degree grid (~10 km); too coarse for individual mountain gullies.
- **temporal resolution**: 30 minutes; daily/monthly derivatives.
- **historical coverage**: Retrospective V07 record; exact selected collection and pilot granule completeness not verified.
- **latency**: Early about 4h; Late nominal 14h; Final about 3.5 months (NASA FAQ). Not instant warning data.
- **format**: HDF5; GIS GeoTIFF; selected NetCDF services.
- **programmatic access**: Documented HTTPS download after registration; adapter not activated.
- **rate limits**: Route-specific; numerical PPS limit not verified. Use bounded retries/cache.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Official maintained product; anonymous data access failed; no measured service uptime.
- **fallback**: Cached Open-Meteo reanalysis for context; explicit synthetic replay for demo.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://gpm.nasa.gov/data/imerg), [Official reference 2](https://registration.pps.eosdis.nasa.gov/registration/)

Probe: `{"id": "imerg", "url": "https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg/gis/early/", "tested_at": "2026-09-11T19:09:34.954596+00:00", "authenticated": false, "http_status": 401, "error": "HTTP Error 401: Unauthorized", "note": "No usable sample; provider remains PLANNED."}`

## IMD gridded rainfall — PLANNED

- **role**: Historical rainfall
- **public access**: Official form HTTP 200. Following its RF25.php POST returned binary bytes on first attempt; full retry timed out.
- **authentication**: No login requested by the tested public form.
- **api key**: No key requested.
- **free**: Public form currently free.
- **licence**: Cite Pai et al. (2014) and IMD; public download is not an unrestricted redistribution licence. Terms require confirmation for redistribution.
- **spatial resolution**: 0.25 degrees (~25 km).
- **temporal resolution**: Daily; annual files.
- **historical coverage**: 1901–2025 shown in the inspected form; 2013 download attempted.
- **latency**: Historical batch; not a subhourly operational sensor. Daily service latency not measured.
- **format**: NetCDF and binary GRD.
- **programmatic access**: Form POST confirmed; first 15 MB captured then intentionally bounded; not a validated complete dataset. No hard-coded guessed file path.
- **rate limits**: No numeric limit verified; request annual files once and cache.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Official station-gridded product; two attempts had different outcomes. Daily/coarse rainfall cannot resolve cloudburst timing.
- **fallback**: Open-Meteo archive; synthetic scenario.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html), [Official reference 2](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html)

Probe: `{"id": "imd", "url": "https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html", "tested_at": "2026-09-11T19:09:34.956601+00:00", "authenticated": false, "http_status": 200, "content_type": "text/html; charset=UTF-8", "bytes": 14141, "final_url": "https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html", "sha256": "5a68a976b9f0e47d6851fe4a8433d73bcddc718956167db7e6f28bf4eecc0e60", "sample": "data/raw/imd.txt", "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## ISRO MOSDAC soil wetness — PLANNED

- **role**: Soil moisture/context
- **public access**: Catalog/docs public in browser research; direct automated probe timed out.
- **authentication**: Approved MOSDAC account required for data downloads per official manual.
- **api key**: Account/session API authentication; independent API-key requirement not verified.
- **free**: Public catalog; exact product access depends on approved account.
- **licence**: MOSDAC product terms apply; redistribution rights not verified.
- **spatial resolution**: Product-dependent. Official agriculture example uses AMSR-2 surface moisture at 10 km; not proof of a current mountain-valid product.
- **temporal resolution**: That example is daily with weekly composites; current selected product unverified.
- **historical coverage**: Historical examples available; exact current product archive unverified.
- **latency**: Not verified for a selected product.
- **format**: Product-dependent HDF/NetCDF and maps; exact payload unverified.
- **programmatic access**: Official download API documented; cannot test authenticated download without an account.
- **rate limits**: No numeric limit verified.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Access incomplete; snow, ice, rock and relief require product quality-mask screening.
- **fallback**: Open-Meteo modeled soil moisture or explicitly synthetic rainfall-correlated moisture.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://mosdac.gov.in/downloadapi-manual), [Official reference 2](https://www.mosdac.gov.in/soil-moisture), [Official reference 3](https://mosdac.gov.in/external/agriculture?language=en)

Probe: `{"id": "mosdac", "url": "https://mosdac.gov.in/downloadapi-manual", "tested_at": "2026-09-11T19:09:34.956601+00:00", "authenticated": false, "http_status": null, "error": "The read operation timed out", "note": "No usable sample; provider remains PLANNED."}`

## Copernicus DEM GLO-30 — VERIFIED LIVE

- **role**: Static terrain downloaded; derived basin bundled
- **public access**: Anonymous S3 listing and both N30 E078/E079 terrain GeoTIFF downloads succeeded.
- **authentication**: None on tested public S3 mirror.
- **api key**: None.
- **free**: Yes, public tiles.
- **licence**: Copernicus DEM licence; preserve attribution and identify derivatives. See licence linked in mirror readme.
- **spatial resolution**: 1 arc second (~30m) DSM. Demo analysis explicitly resamples to 120m in EPSG:32644.
- **temporal resolution**: Static elevation product, not temporal observations.
- **historical coverage**: 2021 release on tested mirror; acquisition epoch differs from replay date.
- **latency**: Not applicable.
- **format**: Cloud Optimized GeoTIFF.
- **programmatic access**: Anonymous HTTPS; object keys resolved from actual bucket listing.
- **rate limits**: No product-specific numeric limit verified; cache tile downloads and use COG windows.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Two complete downloaded tiles with SHA256. DSM vegetation/buildings and coarse conditioning affect flow paths.
- **fallback**: Cached tiles; future HydroSHEDS/MERIT cross-check. OpenTopography needs a free account key if used.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://registry.opendata.aws/copernicus-dem/), [Official reference 2](https://copernicus-dem-30m.s3.amazonaws.com/readme.html)

Probe: `{"id": "copernicus", "url": "https://copernicus-dem-30m.s3.amazonaws.com/?list-type=2&prefix=Copernicus_DSM_COG_10_N30_00_E079_00_DEM&max-keys=5", "tested_at": "2026-09-11T19:09:34.956601+00:00", "authenticated": false, "http_status": 200, "content_type": "application/xml", "bytes": 1941, "final_url": "https://copernicus-dem-30m.s3.amazonaws.com/?list-type=2&prefix=Copernicus_DSM_COG_10_N30_00_E079_00_DEM&max-keys=5", "sha256": "2a54d684b17021a7c6aa797f525eec4122b07ed91e149cc4c0fa85f3f20bf9e6", "sample": "data/raw/copernicus.txt", "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## India-WRIS / CWC water observations — PLANNED

- **role**: Water level / streamflow
- **public access**: India-WRIS public portal timed out; no stable public observation endpoint verified.
- **authentication**: Unverified for station time series.
- **api key**: Unverified; no private credentials available.
- **free**: Public portal exists; station-series access and terms unverified.
- **licence**: Government source-specific terms; do not assume all hydrological observations are unrestricted.
- **spatial resolution**: Point stations; locations and completeness vary.
- **temporal resolution**: Unverified for Mandakini observations.
- **historical coverage**: No continuous Mandakini gauge history obtained.
- **latency**: Not measured.
- **format**: Portal data/exports; exact observation schema not verified.
- **programmatic access**: No observation API activated; provider interface raises an explicit PLANNED error.
- **rate limits**: Unknown.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Bounded reachability attempt failed. Station inventory does not prove telemetry access.
- **fallback**: Synthetic water level explicitly MOCKED within REPLAY; request CWC station archive later.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://indiawris.gov.in/wris/), [Official reference 2](https://www.cwc.gov.in/sites/default/files/meteorological-network-details-of-cwc.pdf)

Probe: `{"id": "wris", "url": "https://indiawris.gov.in/wris/", "tested_at": "2026-09-11T19:09:34.957600+00:00", "authenticated": false, "http_status": null, "error": "<urlopen error [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond>", "note": "No usable sample; provider remains PLANNED."}`

## CWC station inventory — VERIFIED LIVE

- **role**: Station metadata only
- **public access**: Official PDF downloaded, HTTP 200.
- **authentication**: None for inventory.
- **api key**: None.
- **free**: Yes, public PDF.
- **licence**: Cite CWC; public report access does not establish a licence for gauge data.
- **spatial resolution**: Point coordinates. Chandrapuri rainfall inventory: 30°25′51″N, 79°04′09″E.
- **temporal resolution**: Static inventory.
- **historical coverage**: Inventory lists establishment date, not retrieved observations.
- **latency**: Not applicable.
- **format**: PDF.
- **programmatic access**: HTTP download verified; station extraction/manual review.
- **rate limits**: No numeric limit verified.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Official metadata; no uptime or gauge calibration evidence collected.
- **fallback**: Keep observation provider PLANNED.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://www.cwc.gov.in/sites/default/files/meteorological-network-details-of-cwc.pdf)

Probe: `{"id": "cwc", "url": "https://www.cwc.gov.in/sites/default/files/meteorological-network-details-of-cwc.pdf", "tested_at": "2026-09-11T19:09:35.860439+00:00", "authenticated": false, "http_status": 200, "content_type": "application/pdf", "bytes": 4311320, "final_url": "https://www.cwc.gov.in/sites/default/files/meteorological-network-details-of-cwc.pdf", "sha256": "0f52ea4ab974ce11aadf81d87392a0403733f4da10d44bf6ef4259f74d8c405d", "sample": "data/raw/cwc.pdf", "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## Sentinel-1 radar — PLANNED

- **role**: Historical inundation validation candidate
- **public access**: Anonymous spatial catalog query returned one intersecting product; raster not downloaded.
- **authentication**: Catalog search anonymous; CDSE account/token for normal product download.
- **api key**: OAuth access token; no paid key required for standard free access.
- **free**: Standard data access within free quotas.
- **licence**: Copernicus Sentinel free/open data terms with attribution; processing-service quotas separate.
- **spatial resolution**: Product-dependent; common IW GRD pixel spacing ~10m does not equal independent ground resolution.
- **temporal resolution**: Satellite acquisitions, not a continuous gauge; revisit varies by acquisition plan and satellite availability.
- **historical coverage**: Since 2014 mission era; cannot reconstruct June 2013 with Sentinel-1.
- **latency**: Acquisition/delivery dependent; no pilot acquisition latency measured.
- **format**: SAFE products containing TIFF and XML.
- **programmatic access**: OData catalog tested; authenticated download, calibration, terrain correction and quality masking PLANNED.
- **rate limits**: CDSE published general quota: 4 concurrent IAD downloads, 12 TB rolling 30-day transfer before reduced speed; recheck before use.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Catalog reachable. Mountain radar shadow/layover and narrow valleys limit inundation interpretation.
- **fallback**: NRSC/government event maps; no fabricated inundation masks.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://documentation.dataspace.copernicus.eu/APIs/OData.html), [Official reference 2](https://documentation.dataspace.copernicus.eu/Quotas.html)

Probe: `{"id": "sentinel1", "url": "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?%24filter=Collection%2FName+eq+%27SENTINEL-1%27+and+OData.CSC.Intersects%28area%3Dgeography%27SRID%3D4326%3BPOLYGON%28%2878.8+30.2%2C79.4+30.2%2C79.4+30.9%2C78.8+30.9%2C78.8+30.2%29%29%27%29&%24top=1", "tested_at": "2026-09-11T19:09:36.473428+00:00", "authenticated": false, "http_status": 200, "content_type": "application/json", "bytes": 1594, "final_url": "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?%24filter=Collection%2FName+eq+%27SENTINEL-1%27+and+OData.CSC.Intersects%28area%3Dgeography%27SRID%3D4326%3BPOLYGON%28%2878.8+30.2%2C79.4+30.2%2C79.4+30.9%2C78.8+30.9%2C78.8+30.2%29%29%27%29&%24top=1", "sha256": "c7de7ede1a9bfc9bc73cdde59592c3ba8e9b381166dabf19fcc3a63c31ded94a", "sample": "data/raw/sentinel1.json", "payload_keys": ["@odata.context", "value", "@odata.nextLink"], "products": 1, "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## JRC Global Surface Water — PLANNED

- **role**: Static surface-water context
- **public access**: Download page HTTP 200; raster tile not yet downloaded.
- **authentication**: None for public download; Earth Engine route requires account.
- **api key**: None for direct TIFF.
- **free**: Yes.
- **licence**: Copernicus terms; attribution Source: EC JRC/Google; cite Pekel et al. (2016).
- **spatial resolution**: 30m Landsat-derived mapping.
- **temporal resolution**: Monthly/yearly histories and multiyear summaries.
- **historical coverage**: Official page updated 26 Aug 2026 reports 1984–2024; v1.5 mixes Landsat collections.
- **latency**: Retrospective; not real-time flood detection.
- **format**: GeoTIFF, Earth Engine assets, map services.
- **programmatic access**: Official downloadable file list and scripts exist; pixel ingestion PLANNED.
- **rate limits**: No direct-download numeric limit verified; Earth Engine quotas are separate.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Portal reachable; new release warns about co-registration offsets. Narrow rivers/clouds limit inference.
- **fallback**: OSM river geometry for demonstrator; no claim of observed inundation.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://global-surface-water.appspot.com/download), [Official reference 2](https://global-surface-water.appspot.com/faq)

Probe: `{"id": "jrc", "url": "https://global-surface-water.appspot.com/download", "tested_at": "2026-09-11T19:09:36.652244+00:00", "authenticated": false, "http_status": 200, "content_type": "text/html; charset=utf-8", "bytes": 82680, "final_url": "https://global-surface-water.appspot.com/download", "sha256": "bc07b9e5b6a7627d5c2082d9e314e90ed039359cce74c19f8fc71f8414228b7d", "sample": "data/raw/jrc.txt", "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## OpenStreetMap — VERIFIED LIVE

- **role**: Settlements, rivers, bridges, roads and mapped hospitals
- **public access**: One bounded Overpass request succeeded, 1,885 elements; local extract saved.
- **authentication**: None for tested read-only Overpass request.
- **api key**: None.
- **free**: Yes, shared public service.
- **licence**: © OpenStreetMap contributors, ODbL; attribution and derivative database obligations apply.
- **spatial resolution**: Vector features; accuracy and completeness variable, not a fixed grid.
- **temporal resolution**: Continuously edited map; cached retrieval timestamp in probe log.
- **historical coverage**: Current extract only; not asserted to reconstruct 2013 infrastructure.
- **latency**: Replication-dependent; local extract is not continually live.
- **format**: Overpass JSON, converted to GeoJSON.
- **programmatic access**: Documented Overpass interpreter query; cached for backend/PostGIS; dashboard does not query Overpass.
- **rate limits**: Shared-service policy: regular clients should stay below ~100 requests and 10 MB/day; respect 429/backoff and current policy.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Probe succeeded; incomplete infrastructure mapping. Population counts left unknown.
- **fallback**: Cached extract; authoritative government inventory after access/terms verification.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://wiki.openstreetmap.org/wiki/Overpass_API), [Official reference 2](https://www.openstreetmap.org/copyright)

Probe: `{"id": "osm", "url": "https://overpass-api.de/api/interpreter", "tested_at": "2026-09-11T19:09:37.674607+00:00", "authenticated": false, "http_status": 200, "content_type": "application/json", "bytes": 896616, "final_url": "https://overpass-api.de/api/interpreter", "sha256": "da9b08b008febbe54d2637e802c9563e4499f9e6163e42cce488cb1f07a050aa", "sample": "data/raw/osm.json", "payload_keys": ["version", "generator", "osm3s", "elements"], "elements": 1885, "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## Government disaster reports — VERIFIED LIVE

- **role**: Hand-curated event context, not training truth
- **public access**: NIDM India Disaster Report 2013 downloaded; related official event sources cited in CSV.
- **authentication**: None for tested report.
- **api key**: None.
- **free**: Public reports.
- **licence**: Cite issuing agency and report. Do not assume unrestricted report reproduction.
- **spatial resolution**: Narrative locations/maps; no uniform footprint or event-label precision.
- **temporal resolution**: Event dates; timing uncertainty retained.
- **historical coverage**: 2013 episodes and 2021 Chamoli context in curated CSV.
- **latency**: Retrospective.
- **format**: PDF; curated CSV references.
- **programmatic access**: PDF download succeeds; labels manually curated, not an invented API.
- **rate limits**: No numeric limit verified; cache downloads.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Primary agency reports; sparse events do not support skill estimation. 2021 mechanism differs from rainfall flooding.
- **fallback**: Replay scenario with its own synthetic target; no measured accuracy.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://nidm.gov.in/PDF/pubs/India%20Disaster%20Report%202013.pdf), [Official reference 2](https://nidm.gov.in/pdf/trgReports/2021/July/Report_26July2021sp.pdf)

Probe: `{"id": "reports", "url": "https://nidm.gov.in/PDF/pubs/India%20Disaster%20Report%202013.pdf", "tested_at": "2026-09-11T19:09:38.796265+00:00", "authenticated": false, "http_status": 200, "content_type": "application/pdf", "bytes": 2554532, "final_url": "https://nidm.gov.in/PDF/pubs/India%20Disaster%20Report%202013.pdf", "sha256": "17c960658a0e047338717a464f79fa6cccb00749fbf2af87f5c16214dc020922", "sample": "data/raw/reports.pdf", "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## Open-Meteo forecast — VERIFIED LIVE

- **role**: Fallback modeled rainfall/soil sample only
- **public access**: Actual precipitation and soil-moisture JSON returned HTTP 200.
- **authentication**: None on free endpoint.
- **api key**: None on free endpoint.
- **free**: Free endpoint for noncommercial evaluation; commercial access requires paid plan.
- **licence**: Weather data CC BY 4.0, credit Open-Meteo/model providers; hosted API usage terms separate.
- **spatial resolution**: Model-dependent, often kilometres; grid output not an IoT station.
- **temporal resolution**: Hourly values from forecast model cycles.
- **historical coverage**: Forecast horizon; archive is separate.
- **latency**: Model-cycle dependent; local retrieval succeeded, end-to-end observation latency not measured.
- **format**: JSON.
- **programmatic access**: Documented HTTP API verified; not automatically substituted into replay.
- **rate limits**: Free: 600/min, 5,000/hour, 10,000/day, 300,000/month per published pricing.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: No free-tier uptime guarantee. Mountain representativeness requires validation.
- **fallback**: Cached archive or explicit synthetic provider.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://open-meteo.com/en/docs), [Official reference 2](https://open-meteo.com/en/pricing)

Probe: `{"id": "openmeteo", "url": "https://api.open-meteo.com/v1/forecast?latitude=30.7346&longitude=79.0669&hourly=precipitation,soil_moisture_0_to_1cm&forecast_days=1", "tested_at": "2026-09-11T19:09:40.167993+00:00", "authenticated": false, "http_status": 200, "content_type": "application/json; charset=utf-8", "bytes": 1046, "final_url": "https://api.open-meteo.com/v1/forecast?latitude=30.7346&longitude=79.0669&hourly=precipitation,soil_moisture_0_to_1cm&forecast_days=1", "sha256": "0ff9ee558112215664d6f7cd7131e2cdf7d95c8c05d3f4f26f9e5cd1cf949bde", "sample": "data/raw/openmeteo.json", "payload_keys": ["latitude", "longitude", "generationtime_ms", "utc_offset_seconds", "timezone", "timezone_abbreviation", "elevation", "hourly_units", "hourly"], "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`

## Open-Meteo historical reanalysis — REPLAY

- **role**: Real cached 2013 weather context
- **public access**: 120 hourly values for 14–18 June 2013 downloaded at Kedarnath grid point.
- **authentication**: None on tested free endpoint.
- **api key**: None.
- **free**: Noncommercial free API terms apply.
- **licence**: CC BY 4.0 data attribution; service terms as above.
- **spatial resolution**: Reanalysis/model grid, not local ground observation.
- **temporal resolution**: Hourly.
- **historical coverage**: Service documents history from 1940; only 2013 pilot sample fetched.
- **latency**: Retrospective, unavailable as issued at the historical event time; not used to claim lead time.
- **format**: JSON.
- **programmatic access**: Actual archive request verified and cached; replay adapter only emits Kedarnath, never invented neighboring stations.
- **rate limits**: Shared Open-Meteo limits; query complexity affects accounting.
- **server side**: Use backend ingestion and cached files; no provider credentials in browser.
- **reliability**: Accessible context, not independent flood labels or operational forecast validation.
- **fallback**: SyntheticReplay with synthetic=true.
- **checked date**: 2026-09-12

Sources: [Official reference 1](https://open-meteo.com/en/docs/historical-weather-api), [Official reference 2](https://open-meteo.com/en/pricing)

Probe: `{"id": "openmeteo_archive", "url": "https://archive-api.open-meteo.com/v1/archive?latitude=30.7346&longitude=79.0669&start_date=2013-06-14&end_date=2013-06-18&hourly=precipitation,soil_moisture_0_to_7cm", "tested_at": "2026-09-11T19:09:41.201083+00:00", "authenticated": false, "http_status": 200, "content_type": "application/json; charset=utf-8", "bytes": 3926, "final_url": "https://archive-api.open-meteo.com/v1/archive?latitude=30.7346&longitude=79.0669&start_date=2013-06-14&end_date=2013-06-18&hourly=precipitation,soil_moisture_0_to_7cm", "sha256": "5d00214c136ceedb48bee44b0758cecb8f749bffca8e0979d75ad7a8f6a96ee7", "sample": "data/raw/openmeteo_archive.json", "payload_keys": ["latitude", "longitude", "generationtime_ms", "utc_offset_seconds", "timezone", "timezone_abbreviation", "elevation", "hourly_units", "hourly"], "note": "Transport verified; interpret product/auth/coverage separately in source registry."}`
