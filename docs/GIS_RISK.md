# GIS, downstream risk and priority

**AI:** What is the estimated local demo hazard score?
**GIS:** Which reaches are connected downstream?
**Exposure:** Which mapped assets match the river-proximity screening rule?
**Priority:** Which locations should authorities review first?

## Terrain and river network

`scripts/prepare_pilot.py` uses cached Copernicus 30m DSM tiles, projects to EPSG:32644, and resamples to a 120m analysis grid. `hydrology.py` conditions depressions with priority-flood, resolves flats with a small deterministic gradient, routes D8 flow, accumulates upstream area and delineates incremental catchments at selected outlets. Outlets are snapped to drainage cells; settlement coordinates and outlet coordinates can differ.

The provisional basin is about 1,637.9 km². Geometry is not a surveyed hydrological boundary. Cached OSM mapped rivers are distinct from DEM-derived flow paths; the UI labels them separately. Hillshade is rendered from the 120m analysis raster, not a live 30m elevation service or a hydraulic surface.

## Relative downstream propagation

Process nodes in topological order. For each location, choose the maximum of its available local score and each parent's routed score multiplied by **0.92**. The selected score retains its dominant origin; its adequacy is multiplied by **0.95** at each downstream edge. Missing local evidence does not prevent upstream screening, but it remains visibly missing and flagged for review.

The graph stores reach length in metres, but the current formula does **not** use it. This is relative downstream screening with illustrative **per-edge attenuation**, not exponential physical distance decay, flow volume, water level, travel time, hydraulic or hydrodynamic simulation.

| Routed score | Internal screening label |
|---|---|
| Null | Unknown |
| Below 0.25 | Normal |
| 0.25 to below 0.55 | Watch |
| 0.55 to below 0.80 | Warning |
| At least 0.80 | Critical |

These are demo thresholds, not IMD or other official alert classifications. Normal is not an all-clear. Map marker numbers are relative priority ranks, not P1/P2 emergency codes.

## Candidate exposure

Assets must intersect the location's incremental catchment and be within **150m of a mapped river**. The explicit memory demo uses Shapely in metric UTM; PostGIS uses `ST_Intersects` and geography `ST_DWithin`. Small projection differences at the threshold are possible; the optional integration test compares matched IDs.

The map now has a real, metric-buffered screening polygon exposed at `/map/screening-corridor`, clipped to the provisional pilot footprint. It is drawn separately from the cached asset geometry. This polygon is **candidate exposure screening, never a flood inundation boundary**. It does not establish that an asset will flood, its damage severity or whether a crossing is safe.

Counted kinds: settlements, roads, bridges, hospitals. Road values count mapped features, **not kilometres**. A bridge can also have a separately identified road feature, so counts are inventory features rather than unique physical structures. Zero means no matched feature in this extract, not proof no asset exists. Population remains null. Current cached assets do not reconstruct 2013 infrastructure.

## Priority and human review

`impact_weight = 1 + ln(1 + settlements + roads + 2×bridges + 5×hospitals)`

`priority = routed_score × impact_weight × routed_adequacy`

Locations are sorted descending by priority, with ID tie-breaking. Weight choices are illustrative and not operationally calibrated. Low adequacy can depress priority; the UI also retains an independent manual-review flag for Warning, Critical, Unknown or stale local observations. A low priority cannot be used to dismiss missing evidence.

Recommendations prompt field checks and authority review. The browser checklist and exported draft are local notes, not an authenticated incident log, dispatch, official verification or evacuation order.
