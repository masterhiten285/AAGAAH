export const featureLabels: Record<string, string> = {
  rain_1h: 'Rainfall in the last hour',
  rain_3h: 'Rainfall over 3 hours',
  rain_6h: 'Rainfall over 6 hours',
  rain_24h: 'Rainfall over 24 hours',
  soil_moisture: 'Soil moisture',
  water_level_m: 'Water level',
  forecast_trend: 'Forecast rainfall change',
  slope_deg: 'Local terrain slope',
  elevation_m: 'Elevation',
  river_distance_m: 'Distance from mapped river',
  upstream_area_km2: 'Upstream contributing area',
}

export function percent(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return 'Unavailable'
  if (value > 0 && value < 0.001) return '<0.1%'
  if (value < 1 && value > 0.999) return '>99.9%'
  return `${(value * 100).toFixed(1).replace(/\.0$/, '')}%`
}

export function dateLabel(value: string | null | undefined): string {
  if (!value) return 'Unavailable'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? 'Unavailable'
    : date.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
}

export function featureValue(
  key: string,
  value: number | null | undefined,
): string {
  if (value == null || !Number.isFinite(value)) return 'Unavailable'
  if (key === 'soil_moisture') return percent(value)
  const unit =
    key.startsWith('rain_') || key === 'forecast_trend'
      ? 'mm'
      : key === 'slope_deg'
        ? '°'
        : key === 'upstream_area_km2'
          ? 'km²'
          : 'm'
  return `${value.toFixed(1)} ${unit}`
}
