# Model validation and software verification

## Scientific evidence

The loaded model card reports `training=MOCKED`, `historical_validation=false` and `performance_metrics=null`. Training has 2,400 generated examples and an artificial severity target. Three GroupKFold smoke checks use 120 artificial groups (1,600 training / 800 held out per fold). They check group separation and finite predictions, not flood skill or spatial generalization.

| Requested metric | Current evidence |
|---|---|
| ROC-AUC | Not established on observed flood events |
| PR-AUC | Not established |
| Brier score | Not established |
| F1 | Not established |
| Precision | Not established |
| Recall | Not established |
| Warning lead time | Not established |

The dashboard reads metrics from `/model-card`; it does not embed attractive numerical scores or a benchmark table. Synthetic replay behavior is not a substitute for performance evaluation.

## Required future evaluation

Define a physical prediction target and horizon, acquire genuine event/non-event labels with provenance, retain as-issued observation/forecast availability, split forward in time with entire events held out, assess basin transfer, calibrate probabilities on separate data, and report imbalance-aware metrics and uncertainty on held-out events. Evaluate failure modes and mechanisms separately, including mountain-grid representativeness and phenomena the present model does not represent.

`ml-model/evaluate_historical.py` currently validates a manifest: required columns, non-synthetic records, event separation, label-source presence, train/test groups and forward observation dates. It then exits with a planned-evaluation message. It does not fit a historical model, compute metrics, or fully certify per-record operational availability. The archive adapter uses retrospective reanalysis, not as-issued historical forecasts.

## Reproducibility and checks

From `SIH/aagaah`, run `../../.venv/Scripts/python.exe -m pytest -q` on Windows. Tests cover causal windows, missing/stale inputs, provenance rejection, SHAP reconstruction, anomaly independence, DEM conditioning/flow conservation, downstream-only propagation, low-adequacy review, exposure geometry, API semantics and replay determinism. `/dashboard?mode=live` must return 503 without replay locations.

Run `../../.venv/Scripts/python.exe scripts/replay_check.py` for representative synthetic hours 0, 12, 24, 30, 42, 60, 71, deterministic reset and the separate one-point archive adapter. It regenerates `artifacts/replay-results.json`, `docs/REPLAY_WALKTHROUGH.md` and the application OpenAPI file. These record mechanics, not historical skill.

From `frontend`, run `npm run build` and `npm run test:e2e`. Browser tests require the API, Vite proxy, Chromium and an enabled replay scheduler/worker. Install Chromium with `npx playwright install chromium` if absent. `AAGAAH_UI_URL` selects another local UI URL. Tests cover real replay, map loading/toggles/geometry, live unavailability, model/source evidence, mobile layout, missing/empty inputs, failed API reads and provenance-preserving review draft export.

Set `AAGAAH_TEST_DATABASE_URL` to a **migrated test PostGIS database** to run database integration. It seeds data and checks PostGIS/indexes and exposure agreement. Without that URL the test explicitly skips; a memory-demo run does not certify PostGIS or Compose.

The repository contains an older `requirements-lock.txt`; package versions can require a compatible Python/platform. This Windows run used Python 3.11 with `requirements.txt`. Exact installed versions are recorded in `docs/TEST_ENVIRONMENT.txt`; model seed and existing data/artifact provenance remain intact. Successful software tests do not establish scientific readiness.
