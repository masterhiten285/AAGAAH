import { useQuery } from '@tanstack/react-query'
import { get } from './api'
import type { Health, ModelCard, Snapshot, Source } from './types'
import { dateLabel, featureLabels } from './presentation'

export function SourcesView({ snapshot }: { snapshot?: Snapshot }) {
  const query = useQuery({
    queryKey: ['sources'],
    queryFn: () => get<Source[]>('/sources'),
  })
  return (
    <section className="evidence-page">
      <h2>Data Sources & Freshness</h2>
      <p>
        Access to a source does not mean it feeds this dashboard. No live
        environmental feed is connected.
      </p>
      <div className="notice">
        <strong>Current dashboard input: synthetic-heavy-rain-v1</strong>
        <p>
          HISTORICAL / REPLAY · Generated hourly rainfall, soil moisture, water
          level and forecast values. Scenario time: {dateLabel(snapshot?.as_of)}
          . Freshness is measured against this replay clock, never against
          today.
        </p>
      </div>
      {query.isPending && <p role="status">Loading source provenance…</p>}
      {query.isError && (
        <p role="alert">Source catalog unavailable. {query.error.message}</p>
      )}
      {query.data?.length === 0 && <p>No sources registered.</p>}
      <div className="table-scroll">
        <table>
          <caption>
            Stored source evidence; retrieval time is not observation freshness
          </caption>
          <thead>
            <tr>
              <th>Source</th>
              <th>Type</th>
              <th>Purpose / implementation status</th>
              <th>Last available time</th>
            </tr>
          </thead>
          <tbody>
            {query.data?.map((source) => (
              <tr key={source.id}>
                <td>
                  <strong>{source.name}</strong>
                </td>
                <td>
                  <span className="tag">{source.usage_type}</span>
                </td>
                <td>
                  {source.role}
                  <p>{source.usage_status}</p>
                </td>
                <td>
                  {source.last_observation_at ? (
                    <>
                      Last cached observation:{' '}
                      {dateLabel(source.last_observation_at)}
                    </>
                  ) : (
                    'Observation freshness unavailable'
                  )}
                  <p>Access probe: {dateLabel(source.retrieved_at)}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {query.data?.map((source) => (
        <details key={source.id}>
          <summary>{source.name} — access evidence & limitations</summary>
          <div className="detail-body">
            <p>{source.public_access}</p>
            <p>{source.programmatic_access}</p>
            <p>{source.reliability}</p>
            <dl className="facts">
              <dt>Stored probe label</dt>
              <dd>{source.status} (access evidence only)</dd>
              <dt>Resolution</dt>
              <dd>
                {source.spatial_resolution} / {source.temporal_resolution}
              </dd>
              <dt>Latency note</dt>
              <dd>{source.latency}</dd>
              <dt>Terms recorded in repository</dt>
              <dd>{source.licence}</dd>
              <dt>Authentication</dt>
              <dd>{source.authentication}</dd>
              <dt>Fallback</dt>
              <dd>{source.fallback}</dd>
            </dl>
            <p className="source-links">
              {source.references
                .filter((url) => /^https?:\/\//.test(url))
                .map((url, index) => (
                  <a key={url} href={url} target="_blank" rel="noreferrer">
                    Source reference {index + 1}
                  </a>
                ))}
            </p>
          </div>
        </details>
      ))}
    </section>
  )
}

export function ModelView() {
  const query = useQuery({
    queryKey: ['model-card'],
    queryFn: () => get<ModelCard>('/model-card'),
  })
  if (query.isPending) return <p role="status">Loading model card…</p>
  if (query.isError)
    return <p role="alert">Model evidence unavailable. {query.error.message}</p>
  const card = query.data
  const metrics = [
    ['roc_auc', 'ROC-AUC'],
    ['pr_auc', 'PR-AUC'],
    ['brier_score', 'Brier score'],
    ['f1', 'F1'],
    ['precision', 'Precision'],
    ['recall', 'Recall'],
  ]
  return (
    <section className="evidence-page">
      <h2>Model & Validation</h2>
      <p>
        What the software demonstrates, and what still needs scientific
        evidence.
      </p>
      <div className="notice">
        <strong>
          Historical flood performance:{' '}
          {card.historical_validation ? 'See model card' : 'Not established'}
        </strong>
        <p>
          {card.risk_semantics}. Warning lead time has not been established.
        </p>
      </div>
      <dl className="facts">
        <dt>Model</dt>
        <dd>Monotonic XGBoost · {card.id}</dd>
        <dt>Training data</dt>
        <dd>
          {card.training} · 2,400 generated examples, 120 artificial groups,
          seed {card.seed}. No observed flood labels.
        </dd>
        <dt>Prediction target</dt>
        <dd>{card.target}</dd>
        <dt>Validation performed</dt>
        <dd>{card.validation}</dd>
      </dl>
      <div className="metric-grid">
        {metrics.map(([key, label]) => (
          <article className="metric" key={key}>
            <span>{label}</span>
            <strong>
              {card.performance_metrics?.[key] == null
                ? 'Not established'
                : card.performance_metrics[key]?.toFixed(4)}
            </strong>
            <small>
              {card.performance_metrics?.[key] == null
                ? 'No historical evaluation metric supplied'
                : 'Reported by the loaded model card'}
            </small>
          </article>
        ))}
      </div>
      <details open>
        <summary>Features & model methodology</summary>
        <div className="detail-body">
          <ul>
            {card.features.map((key) => (
              <li key={key}>
                {featureLabels[key] || key} <code>{key}</code>
              </li>
            ))}
          </ul>
          <p>
            90 trees, depth 3, learning rate 0.07. Nondecreasing constraints
            apply to rainfall windows, soil moisture and water level; terrain
            features are unconstrained. XGBoost handles missing inputs; missing
            rainfall evidence suppresses the displayed local score.
          </p>
          <p>
            Isolation Forest runs independently against a synthetic
            normal-condition reference, using median-imputed inputs and
            contamination 0.08. Its flag means unusual conditions, not a flood
            or a faulty sensor.
          </p>
        </div>
      </details>
      <details>
        <summary>Validation checks & reproducibility</summary>
        <div className="detail-body">
          <p>
            Three GroupKFold checks establish disjoint artificial groups and
            finite predictions. These are not spatially independent flood
            events.
          </p>
          <ul>
            {card.folds.map((fold, index) => (
              <li key={index}>
                Fold {index + 1}: {fold.training_rows} training /{' '}
                {fold.held_out_rows} held out; disjoint groups:{' '}
                {String(fold.groups_disjoint)}.
              </li>
            ))}
          </ul>
          <p>
            Training data SHA-256 (recorded fingerprint; no runtime integrity
            certification):
          </p>
          <code className="hash">{card.data_sha256}</code>
          <p>
            Historical evaluation requires genuine event/non-event labels,
            observed and available times, forward event/time splits, calibration
            checks and independent held-out basins. The existing evaluation
            script checks a manifest; fitting and metric computation are
            planned.
          </p>
        </div>
      </details>
      <details>
        <summary>SHAP: what the explanation means</summary>
        <div className="detail-body">
          <p>
            TreeSHAP contributions plus the base value reconstruct the local
            classifier log-odds. An upward contribution raises this model score
            relative to its baseline; a downward contribution lowers it.
            Contributions are not percentage points, measured causes, or
            explanations of the final priority.
          </p>
        </div>
      </details>
      <details open>
        <summary>Known limitations</summary>
        <div className="detail-body">
          <p>
            Synthetic targets cannot establish flood accuracy. Coarse weather
            grids and a 120m terrain analysis may miss local mountain processes.
            No calibrated probability, inundation depth, hydraulic simulation,
            travel time, warning lead time, surveyed asset completeness or
            population exposure is available.
          </p>
        </div>
      </details>
    </section>
  )
}

export function MethodologyView() {
  const stages = [
    [
      'Data sources & ingestion',
      'The default replay generates hourly environmental inputs. A separate cached reanalysis adapter covers only Kedarnath. Government integrations remain planned.',
    ],
    [
      'Validation & preprocessing',
      'Check ranges and provenance; use only available, nonfuture hourly readings. Deduplicate by observation time. Preserve missing rainfall as missing.',
    ],
    [
      'Features & AI hazard',
      'Build 11 weather and terrain features. The synthetic-trained XGBoost estimates an artificial severity target; the output is a demo score.',
    ],
    [
      'Explanation & data adequacy',
      'TreeSHAP explains local model drivers. Freshness and feature/window completeness produce a separate adequacy heuristic capped at 45%.',
    ],
    [
      'GIS & downstream connectivity',
      'DEM-derived D8 paths connect reaches. Take the maximum local or upstream routed score, reducing upstream score by 0.92 and adequacy by 0.95 at each edge. Edge lengths do not determine attenuation.',
    ],
    [
      'Candidate exposure',
      'Screen cached OSM assets that intersect a catchment and lie within 150m of mapped rivers. The shaded corridor is a screening area, not a flood boundary.',
    ],
    [
      'Priority & authority review',
      'Rank by routed score × mapped impact weight × routed adequacy. Keep missing/stale and high-score sites visible for manual review. Authorities verify evidence and act under their own protocols.',
    ],
  ]
  return (
    <section className="evidence-page">
      <h2>How AAGAAH works</h2>
      <p>
        Mountain rainfall varies sharply, observations can be sparse or late,
        and upstream conditions matter downstream. AAGAAH connects these pieces
        for local authority review.
      </p>
      <ol className="pipeline-story">
        {stages.map(([title, description]) => (
          <li key={title}>
            <h3>{title}</h3>
            <p>{description}</p>
          </li>
        ))}
      </ol>
      <div className="notice">
        <strong>Implemented vs planned</strong>
        <p>
          Implemented: causal feature processing, synthetic model, independent
          anomaly detector, SHAP, GIS screening, priority, replay and evidence
          views. Planned: connected live ingestion, observed flood-label
          training, historical performance evaluation, calibration and
          authority-system integrations.
        </p>
      </div>
      <p>
        AAGAAH is a decision-support and last-mile intelligence layer for
        authorized authorities. It does not replace IMD, NDRF or SAsiaFFGS and
        does not order evacuations.
      </p>
    </section>
  )
}

export function HealthView() {
  const query = useQuery({
    queryKey: ['health'],
    queryFn: () => get<Health>('/health'),
    refetchInterval: 15000,
  })
  return (
    <details>
      <summary>Connection settings & system health</summary>
      <div className="detail-body">
        {query.isError ? (
          <p role="alert">Health check failed. {query.error.message}</p>
        ) : query.data ? (
          <dl className="facts">
            <dt>API status</dt>
            <dd>{query.data.status}</dd>
            <dt>Storage</dt>
            <dd>{query.data.storage}</dd>
            <dt>Redis</dt>
            <dd>{query.data.redis}</dd>
            <dt>Live monitoring</dt>
            <dd>
              {query.data.live_monitoring ? 'Available' : 'Not connected'}
            </dd>
            <dt>Replay scheduler in API</dt>
            <dd>
              {query.data.replay_scheduler
                ? `Enabled: ${query.data.replay_interval_seconds}s per replay hour`
                : 'Disabled; Play needs the separate worker. Step and seek work without it.'}
            </dd>
            <dt>Scientific readiness</dt>
            <dd>{String(query.data.scientific_readiness)}</dd>
          </dl>
        ) : (
          <p>Checking services…</p>
        )}
      </div>
    </details>
  )
}
