# Judge demo guide

## Before presenting

Start the API in explicit memory-demo mode and the frontend, or use the existing Compose stack. Confirm `/health` and the visible storage label. Enable one replay scheduler/worker if demonstrating Play. Start paused at hour 0; keep the **REPLAY · Synthetic scenario** banner visible. The pilot is Mandakini; other regions are not operational deployments.

## Three-minute script

| Time | Screen/action | What to say |
|---|---|---|
| 0:00–0:25 | Basin situation, Mandakini map | “AAGAAH helps authorities decide where to verify conditions first. Mountain rainfall is uneven, observations can be sparse, and upstream conditions can matter far downstream. We connect environmental evidence with river geography and mapped assets.” |
| 0:25–0:45 | Point to replay banner; briefly open Live monitoring | “This build is a research prototype. Live monitoring is not connected. Our demonstration is a synthetic heavy-rain scenario with 2013 dates for context; it is not a reconstruction of the actual flood.” |
| 0:45–1:10 | Replay → Go to hour 30; select a high-score row | “The local demo hazard score responds to the generated rainfall pulse. It is separate from data adequacy, asset exposure and priority. Even complete synthetic inputs are capped at 45% adequacy; that is not model accuracy.” |
| 1:10–1:35 | Why panel, then connected locations | “These SHAP contributions show which inputs raise or lower this model output. The anomaly detector runs independently. GIS adds downstream connectivity: we pass relative screening scores along the river graph using illustrative per-edge attenuation, not hydraulics or travel time.” |
| 1:35–1:55 | Layers → screening corridor; asset inventory and ranking | “The 150m corridor screens candidate assets; it is not an inundation boundary. These are cached mapped features, roads are counts rather than kilometres, and population is unknown. Priority combines the routed score, mapped impact weight and adequacy; missing evidence still needs review.” |
| 1:55–2:20 | Data Sources & Freshness | “Here are the input sources, coverage and times. A successful source probe does not make a live integration. DEM and OSM are cached static inputs. Reanalysis exists for one location, and government time-series integrations remain planned.” |
| 2:20–2:40 | Model & Validation | “XGBoost is trained on synthetic targets. We have tested causal processing, SHAP reconstruction, independent anomaly detection and replay behavior. Historical ROC-AUC, precision, recall and lead time are not established; the interface says so.” |
| 2:40–3:00 | Return to location → authority checklist/export | “The output is a verification prompt: confirm upstream conditions, freshness, assets and official advisories. An authority can export a clearly labeled review draft. AAGAAH supports human decisions; it does not dispatch responders or order evacuation.” |

Do not promise an exact score or highest-ranked location before inspecting the loaded snapshot. Scores, contributors and rankings must come from the actual run.

## Thirty-second project explanation

“AAGAAH helps authorities see which places deserve attention when upstream environmental conditions change. It combines an explainable AI hazard score with river-network connectivity, mapped asset exposure and data adequacy to prioritize field verification. Our Mandakini prototype demonstrates the full workflow using clearly labeled synthetic replay. Live feeds, real flood validation and warning lead time are not established. It supports authorized authorities; it does not replace official warnings or make evacuation decisions.”

## Five difficult judge questions

**1. What exactly does your AI predict, and what is its accuracy?**
The current classifier predicts an artificial heavy-rain severity target on 2,400 synthetic examples. The output is a demo score, not a calibrated flood probability. Historical accuracy metrics are not available. The next scientific step is defining the physical target/horizon and evaluating genuine event/non-event labels with forward, event-disjoint splits.

**2. Did AAGAAH predict the 2013 disaster or provide 10.5 hours of warning?**
No such result is established. The default weather sequence is generated, and the separate cached archive is retrospective reanalysis at one grid point. Neither is evidence of as-issued forecasting skill or warning lead time.

**3. Why is the score high when adequacy is only 45%, and can you trust SHAP?**
The score describes the classifier output; adequacy describes input freshness/completeness and the synthetic-model limitation. SHAP faithfully decomposes that classifier, as checked by reconstruction tests, but cannot prove the model is scientifically correct. Authorities need verified observations and independent validation before operational reliance.

**4. Does the shaded map show flooding, and is downstream propagation a simulation?**
No. Catchments are provisional DEM-derived areas and the 150m shading is a candidate exposure corridor. Routing uses graph connectivity and illustrative per-edge attenuation. It does not compute flood extent, depth, discharge, velocity or arrival time. A hydraulic model would require additional observations, boundary conditions and validation.

**5. What can an authority actually do with this, and why not just use existing systems?**
The intended role is a last-mile review layer linking evidence to named locations, connected reaches, candidate assets and verification prompts. The current implementation supports inspection and a local review draft, not government integration or dispatch. It complements official advisories from existing systems and does not replace IMD, NDRF or SAsiaFFGS. Its operational usefulness still needs assessment with authorities.
