export type AlertLevel = 'Normal' | 'Watch' | 'Warning' | 'Critical' | 'Unknown'

export interface LocationRisk {
  id: string
  name: string
  lat: number
  lon: number
  risk_score: number | null
  routed_risk: number | null
  confidence: number
  routed_confidence: number
  anomaly: boolean
  anomaly_score: number
  alert_level: AlertLevel
  rank: number
  priority: number
  manual_review: boolean
  recommendation: string
  dominant_origin: string | null
  downstream: string[]
  confidence_reasons: string[]
  features: Record<string, number | null>
  terrain: Record<string, number>
  explanation: {
    feature: string
    value: number | null
    contribution_log_odds: number
  }[]
  exposure: {
    counts: Record<string, number>
    population: number | null
    method: string
    assets: { id: string; name: string; kind: string }[]
  }
  quality: {
    stale: boolean
    no_data: boolean
    age_hours: number
    latest_observed_at?: string | null
    latest_available_at?: string | null
    coverage: Record<string, number>
    missing_features: string[]
    sources: string[]
    statuses: string[]
    synthetic: boolean
  }
}

export interface Snapshot {
  run_id: string
  as_of: string
  computed_at: string
  step: number
  running: boolean
  mode: string
  synthetic: boolean
  storage: string
  locations: LocationRisk[]
  disclaimer: string
  pipeline_stages: string[]
  summary: {
    locations: number
    needs_review: number
    highest_risk: number
    data_adequacy: number
    population: null
  }
}

export interface Pilot {
  id: string
  name: string
  area_km2: number
  analysis_resolution_m: number
  limitations: string[]
  terrain_image_corners: [number, number][]
  locations: { id: string; name: string; lon: number; lat: number }[]
  edges: { upstream: string; downstream: string; length_m: number }[]
}

export interface Source {
  id: string
  name: string
  status: string
  role: string
  public_access: string
  authentication: string
  api_key: string
  free: string
  licence: string
  spatial_resolution: string
  temporal_resolution: string
  historical_coverage: string
  latency: string
  format: string
  programmatic_access: string
  rate_limits: string
  reliability: string
  fallback: string
  references: string[]
  usage_type: string
  usage_status: string
  retrieved_at: string | null
  last_observation_at: string | null
}

export interface ModelCard {
  id: string
  training: string
  seed: number
  features: string[]
  target: string
  validation: string
  folds: {
    training_rows: number
    held_out_rows: number
    groups_disjoint: boolean
  }[]
  performance_metrics: Record<string, number | null> | null
  historical_validation: boolean
  risk_semantics: string
  data_sha256: string
}

export interface Health {
  status: string
  storage: string
  redis: string
  model_status: string
  scientific_readiness: boolean
  live_monitoring: boolean
  replay_scheduler: boolean
  replay_interval_seconds: number
}

export interface HistoryPoint {
  as_of: string
  risk_score: number | null
  rain_1h: number | null
}
