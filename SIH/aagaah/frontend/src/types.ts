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
  explanation: { feature: string; value: number | null; contribution_log_odds: number }[]
  exposure: { counts: Record<string, number>; population: number | null; method: string; assets: { id: string; name: string; kind: string }[] }
  quality: { stale: boolean; age_hours: number; coverage: Record<string, number>; missing_features: string[]; sources: string[]; statuses: string[]; synthetic: boolean }
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
  summary: { locations: number; needs_review: number; highest_risk: number; data_adequacy: number; population: null }
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
}

export interface HistoryPoint {
  as_of: string
  risk_score: number | null
  rain_1h: number | null
}

export interface Incident {
  id: string
  location_id: string
  location_name: string
  title: string
  severity: 'P1_CRITICAL' | 'P2_HIGH' | 'P3_MEDIUM' | 'P4_LOW'
  status: 'NEW' | 'UNDER_REVIEW' | 'VERIFIED' | 'MONITORING' | 'RESOLVED'
  summary: string
  operator_notes: string
  reported_by: string
  created_at: string
  updated_at: string
  audit_log: { timestamp: string; action: string; actor: string; details: string }[]
}

export interface Watershed {
  id: string
  name: string
  state: string
  coverage_status: string
  is_active_pilot: boolean
  area_km2: number
  elevation_range_m: [number, number]
  primary_reach: string
  center: [number, number]
  zoom: number
  description: string
}

export interface CaseStudy {
  id: string
  title: string
  date_range: string
  location: string
  coordinates: [number, number]
  severity: string
  provenance: string
  summary: string
  timeline: { time: string; event: string }[]
  what_aagaah_would_monitor: string[]
  scientific_disclaimer: string
}

export interface SituationFeedItem {
  id: string
  timestamp: string
  title: string
  source: string
  source_url: string
  status: string
  region: string
  summary: string
  implication: string
}

export interface SituationSummaryResponse {
  location_id: string
  briefing_markdown: string
  as_of: string
}
