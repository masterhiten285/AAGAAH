# End-to-end demonstration walkthrough

This run uses the explicitly selected memory-demo spatial adapter. It does not certify Docker/PostGIS; run the integration workflow for that.

The dates refer to the June 2013 Mandakini disaster as narrative context. The environmental series below is deterministic and synthetic. No historical event detection, predictive accuracy, precision, recall, or warning lead time is inferred.

| Replay hour | Simulated timestamp | Highest demo score | Locations requiring review |
|---|---|---|---|
| 0 | 2013-06-15T00:00:00+00:00 | 0.001 | 0 |
| 12 | 2013-06-15T12:00:00+00:00 | 0.001 | 0 |
| 24 | 2013-06-16T00:00:00+00:00 | 0.774 | 5 |
| 30 | 2013-06-16T06:00:00+00:00 | 0.998 | 7 |
| 42 | 2013-06-16T18:00:00+00:00 | 0.846 | 2 |
| 60 | 2013-06-17T12:00:00+00:00 | 0.002 | 0 |
| 71 | 2013-06-17T23:00:00+00:00 | 0.001 | 0 |

## Observed behavior

1. At baseline, generated rainfall is low. The provider emits provenance-tagged hourly readings, including 24 hours of warm-up history.
2. As the synthetic rainfall pulse rises, validation accepts only available, nonfuture hourly readings. Rainfall accumulation windows and other features are recomputed.
3. XGBoost and Isolation Forest independently process the same feature vector. SHAP contributions explain the local score in log-odds. Confidence is a capped data-adequacy heuristic.
4. The terrain-derived graph propagates screening scores downstream. PostGIS in Compose, or the explicit local spatial adapter in this walkthrough, intersects mapped infrastructure with incremental catchments and river proximity.
5. Locations are ranked by risk × mapped impact weight × confidence. Warning/Critical conditions remain flagged for review even at low confidence.
6. Scores fall as the synthetic pulse recedes. Reset reproduces baseline; chart history hides future frames after a rewind.
7. The browser polls committed snapshots. Play advances one simulated hour every eight seconds; pause stops the scheduler from advancing the replay.

## Real archive context check

The cached Open-Meteo 2013 reanalysis adapter also passed through the pipeline. It supplies only the Kedarnath grid point. Other locations retain missing local predictions. The model remains synthetic-trained. Reanalysis was not an as-issued forecast and is not evidence of historical lead time.

## What the run cannot answer

**Did it detect the real 2013 flood? Not established. How early? Not established.** A synthetic pulse changing a synthetic-trained score proves software behavior only. Real evaluation needs gauge records, independent event/non-event labels, as-issued input availability, event/time-blocked training and held-out evaluation, uncertainty assessment and mechanism-specific validation.