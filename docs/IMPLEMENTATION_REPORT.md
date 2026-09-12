# AAGAAH judge-focused improvement report

Completed locally on 12 September 2026. The pre-change audit was written before implementation in [ARCHITECTURE.md](ARCHITECTURE.md). The project retains its FastAPI pipeline, trained model, risk formula, storage adapters, replay engine and MapLibre renderer.

## Changes and why they help a judge

| Change / feature | Benefit |
|---|---|
| Mandakini-first dashboard, plain-language problem statement and guided demo | Establishes the pilot, problem and purpose immediately. |
| Persistent synthetic-replay banner and a separate unavailable-live screen | Prevents historical/generated results from looking like current warnings. The backend now rejects `mode=live` explicitly rather than ignoring it. |
| Four distinct hazard, data adequacy, exposure and priority cards | Separates model output, evidence quality, mapped assets and review order. |
| Actual SHAP drivers in plain language, with expandable feature/log-odds table | Explains why the model output changed without claiming measured physical causes. |
| Independent anomaly panel | Makes unusual conditions visible without treating the anomaly flag as flood confirmation. |
| Local/routed score distinction, dominant origin, connected-location links and priority formula | Explains what GIS adds beyond the local model. |
| True 150m screening polygon and selected candidate-asset filtering | Replaces a mislabeled asset layer and avoids covering the map in unrelated inventory markers. |
| Corrected map thresholds, full pilot extent, visible Unknown category and static-data labels | Matches the backend and makes scope/semantics inspectable. |
| Map container and Vite worker fixes | Fixes real rendering defects: a collapsed map container and a missing worker that prevented GeoJSON layers from appearing. Local terrain and GIS files replace third-party tiles showing an API-key watermark. |
| Data Sources & Freshness, with observation and retrieval times kept separate | Distinguishes access probes, static inputs, archive context and planned integrations. |
| Model & Validation reads the loaded model card | Removes unsupported metric/benchmark/lead-time claims; unavailable evidence remains unavailable. |
| Replay controls/history, local checklist and labeled review-draft download | Gives judges a complete data-to-authority workflow using working capabilities. Drafts are not dispatches or official incident records. |
| Empty/missing/error states and responsive layout | Keeps the interface honest when evidence or services are unavailable. |
| README plus architecture/data/AI/GIS/validation/demo/limitations documentation | Makes the full technical story reviewable without source-code reading. |

## Preserved functionality and intentional removals

Preserved the default API contracts, explicit memory/PostGIS selection, optional Redis, deterministic replay, play/pause/seek/reset/step, history, prediction endpoint, source evidence, model card, map selection, terrain/river/catchment/asset layers, XGBoost, independent Isolation Forest, SHAP and the existing priority/routing formula.

Removed frontend-only claims and dead flows: unsupported national disaster bulletins, fictitious lead time and model metrics, guessed population/asset values, road counts labeled as kilometres, autonomous emergency-action wording and incident/briefing calls to nonexistent endpoints. Replaced the briefing affordance with an actual local draft export. These were not implemented government integrations or working backend features.

The API additions are source-usage/freshness metadata, local observation timestamps, health capability fields, a screening-corridor map layer and explicit rejection of unavailable live mode. No new flood model, dataset or scientific calibration was added.

## Features intentionally not claimed

No operational live monitoring, deployed sensors, verified flood probability, measured historical accuracy, warning lead time, real 2013 event prediction, population-at-risk estimate, hydraulic/hydrodynamic simulation, inundation boundary, physical distance-decay/travel-time model, government dispatch/integration, autonomous evacuation or replacement of IMD/NDRF/SAsiaFFGS.

## Verification performed

| Check | Result |
|---|---|
| Backend pytest suite | **15 passed, 1 skipped**. Skipped test requires a migrated real PostGIS test database; no substitute database used. |
| Replay behavior script | **Passed**: seven synthetic frames, rising/falling storm scores, deterministic reset, one-point cached archive context and no historical performance metrics. |
| Frontend production build | **Passed**: TypeScript and Vite; worker emitted as a production asset. |
| Browser suite with real API | **9 passed**: replay/scheduler, sources/model evidence, mobile layout, live rejection, rendered GIS, layer toggles, missing/empty data, failed requests and authority draft export. |
| API health | HTTP 200, explicit `demo` storage, Redis disabled, `live_monitoring=false`, `scientific_readiness=false`. |
| Live mode | UI displays unavailable current conditions; API returns HTTP 503 without replay locations. |
| Map geometry | Metric 150m buffer tested against expected geometry; catchments/rivers/flowpaths/assets/hillshade endpoint checks passed. Browser assertions require actual rendered vector features and noncollapsed map height. |
| Production map smoke test | Built preview loaded the bundled worker with HTTP 200 and rendered GIS features; no page errors or failed requests. |
| Visual review | Desktop replay, full mobile page and production overview screenshots inspected. The review found and drove fixes for map height, tile watermark, missing worker and inventory clutter. |

The first browser run exposed map-load timing and a development-server restart during configuration editing. Visual review then exposed the deeper map-height and worker failures. The final browser suite passed after fixes; the production smoke test separately verifies the worker bundle.

Runtime used: Windows, Python 3.11, Node 22.14.0, npm 11.6.2, Vite 6.4.3, Playwright 1.63.0. Python dependencies are recorded in [TEST_ENVIRONMENT.txt](TEST_ENVIRONMENT.txt). The existing cross-platform requirements lock was not silently replaced. Backend output includes dependency deprecation warnings; Vite reports a large main JavaScript chunk (about 1.36 MB before compression) and a roughly 509 KB map worker.

## Remaining weaknesses

The important gaps are scientific and operational: synthetic model targets, no connected live feeds, no genuine flood-label evaluation/calibration, coarse/provisional GIS and incomplete asset mapping. Priority weights and per-edge attenuation remain illustrative. Low adequacy can lower rank, so independent review flags remain essential.

The database integration and Docker deployment were not executed here because Docker/test PostGIS were unavailable. The UI still depends on WebGL, and bundle size merits future optimization. Review notes are local drafts that reset on location/snapshot changes; they are not persisted/audited incident management. Replay state is shared and token-based; production authorization and operational hardening remain future work.

## Presentation material

[DEMO_GUIDE.md](DEMO_GUIDE.md) contains the complete **3-minute judge demo script**, **30-second explanation** and **five difficult judge questions with candid answers**. It instructs presenters to use actual loaded scores and keep the synthetic/replay banner visible.

## Files changed / added

Paths below are relative to the repository root.

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_SOURCES.md`
- `docs/ML_EXPLAINABILITY.md`
- `docs/GIS_RISK.md`
- `docs/VALIDATION.md`
- `docs/DEMO_GUIDE.md`
- `docs/LIMITATIONS.md`
- `docs/IMPLEMENTATION_REPORT.md`
- `docs/TEST_ENVIRONMENT.txt`
- `SIH/aagaah/backend-api/aagaah/main.py`
- `SIH/aagaah/backend-api/aagaah/processing.py`
- `SIH/aagaah/backend-api/aagaah/spatial.py`
- `SIH/aagaah/backend-api/aagaah/source_catalog.py`
- `SIH/aagaah/frontend/src/main.tsx`
- `SIH/aagaah/frontend/src/EvidenceViews.tsx`
- `SIH/aagaah/frontend/src/presentation.ts`
- `SIH/aagaah/frontend/src/WatershedMap.tsx`
- `SIH/aagaah/frontend/src/style.css`
- `SIH/aagaah/frontend/src/types.ts`
- `SIH/aagaah/frontend/src/vite-env.d.ts`
- `SIH/aagaah/frontend/vite.config.ts`
- `SIH/aagaah/frontend/e2e/dashboard.spec.ts`
- `SIH/aagaah/tests/test_api.py`
- `SIH/aagaah/tests/test_spatial.py`
- `SIH/aagaah/docs/openapi.json` — regenerated API contract
- `SIH/aagaah/artifacts/replay-results.json` — regenerated behavior evidence
- `SIH/aagaah/artifacts/judge-dashboard-desktop.png`
- `SIH/aagaah/artifacts/judge-dashboard-mobile.png`
- `SIH/aagaah/artifacts/judge-dashboard-viewport.png`

The existing replay walkthrough was regenerated by its script and remained unchanged. Installed `.venv`, `node_modules`, build output and Playwright reports are local ignored runtime artifacts.
