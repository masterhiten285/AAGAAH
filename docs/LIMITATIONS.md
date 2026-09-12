# Limitations and claim boundaries

| Area | Current limitation |
|---|---|
| Live mode | No connected live dashboard or ingestion feed. Live view is explicitly unavailable; forecast access-probe success does not change this. |
| Hazard target | Artificial synthetic severity labels, not observed floods. Demo scores are uncalibrated. |
| Validation | No measured historical ROC-AUC, PR-AUC, Brier score, F1, precision, recall or warning lead time. |
| Replay | 2013 narrative dates with generated weather; separate cached reanalysis covers one grid point only. No reconstruction of the actual event or counterfactual lives saved. |
| Data adequacy | Heuristic capped at 45%, not statistical confidence or model accuracy. Latest record age does not establish freshness of every feature. Coverage/missing fields must also be inspected. |
| Anomaly | Unusual relative to a synthetic reference; cannot certify sensor failure or flood occurrence. Calm synthetic frames may still be unusual. |
| GIS | 120m analysis of a surface model; provisional drainage/outlet snapping, not surveyed hydrology. |
| Propagation | 0.92 score and 0.95 adequacy attenuation per edge; no use of reach distance, hydraulic simulation, depth, velocity or travel time. |
| Exposure | 150m proximity screen, not inundation. OSM completeness uncertain; road/bridge feature overlap possible. No population count or 2013 asset reconstruction. |
| Priority | Illustrative weights; low adequacy can lower rank. Review flags must be considered independently. |
| Authority workflow | Local checklist and text export only. No authenticated incident log, messaging, dispatch, siren, closure or evacuation integration. |
| Storage | Memory mode is explicit and nonpersistent. PostGIS and Redis are configured adapters; real database/deployment verification is environment-dependent. |
| Browser | Map uses WebGL and locally served terrain/GIS files. The unusable external basemap was removed. Text evidence and ranking remain available on map failure. |
| Runtime | Model/data artifacts and source files must exist or be generated explicitly. Dependency/platform drift remains a reproducibility consideration. |
| Operations | Shared replay state, basic control token, no demonstrated multi-tenant authorization or production monitoring/hardening. |

AAGAAH is a decision-support and last-mile intelligence layer for **authorized authorities**. It neither replaces IMD/NDRF/SAsiaFFGS nor claims autonomous evacuation. A demo Critical label is not an official warning; Normal is not an assurance of safety. Field verification and local authority protocols govern any real action.
