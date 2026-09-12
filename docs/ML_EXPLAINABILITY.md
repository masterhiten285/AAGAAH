# AI and explainability

## What is predicted?

The existing monotonic XGBoost classifier predicts an **artificial heavy-rain severity target**, fitted on 2,400 generated rows. It does not predict a documented physical flood depth, discharge threshold or observed flood event. The dashboard therefore labels its output **local demo hazard score**, with an explicit uncalibrated-score explanation.

The synthetic target combines hourly rain, 3h rain, 24h rain, soil moisture, water level and random noise. Seed: 2026. Model: 90 trees, depth 3, learning rate 0.07. Nondecreasing constraints apply to the first six weather features, not terrain slope or upstream area. The final model is fitted on all synthetic rows after three group-disjoint smoke checks.

## Inputs

| Feature | Plain-language meaning | Unit |
|---|---|---|
| `rain_1h`, `rain_3h`, `rain_6h`, `rain_24h` | Rain accumulated in complete preceding hourly windows | mm |
| `soil_moisture` | Available modeled/generated soil moisture | fraction 0–1 |
| `water_level_m` | Supplied water level; generated in default replay | m |
| `forecast_trend` | Available forecast rain minus latest hourly rain | mm |
| `slope_deg` | Local terrain slope | degrees |
| `elevation_m` | Terrain elevation | m |
| `river_distance_m` | Distance from location to cached mapped river | m |
| `upstream_area_km2` | D8 contributing area at snapped outlet | km² |

`processing.py` preserves missing windows as NaN; XGBoost handles missing branches. If there are no accepted observations or every rain window is missing, the API returns a null local score and the UI withholds its explanation. Static terrain can remain available even when local weather is missing.

## Why did the score change?

TreeSHAP returns a contribution for each input. The UI displays the largest absolute contributions, with **↑ raises the demo score** and **↓ lowers the demo score**, plain feature names and actual values. A missing-input branch is explicitly labeled when relevant; the UI never invents a rainfall or moisture value.

Mathematically, `base_log_odds + sum(SHAP contributions)` reconstructs the classifier log-odds; applying the logistic function reconstructs the score. The model test checks this. Contributions are **not percentage-point changes** or evidence of physical causality. SHAP explains the local classifier, not the final river-routed score or operational priority.

## Independent anomaly detection

Isolation Forest is fitted to the synthetic normal-condition reference, with 100 trees and contamination 0.08. Its inputs are median-imputed using the stored imputer. A negative decision-function output produces an anomaly flag. Risk and anomaly calls are independent; changing the anomaly flag does not alter the hazard output. The UI suppresses interpretation of anomaly flags when observations are absent or stale.

Anomaly means **environmental conditions are unusual relative to this reference**. It does not establish flood occurrence, sensor corruption, or safety when absent. Even a calm synthetic replay can be unusual relative to the synthetic training reference.

## Data adequacy is separate

The legacy API field `confidence` is a heuristic:

`0.45 × max(0, 1 − observation_age_hours / 6) × (1 − missing_feature_fraction) × 24h_rain_coverage`

It is capped at 45% because the model is synthetic-trained. It is not model accuracy, a calibrated confidence interval or a probability of correctness. The dashboard calls it **data adequacy** and shows the reasons, age and missing features alongside it. Routed adequacy follows the dominant upstream/local score and is separate from local adequacy.
