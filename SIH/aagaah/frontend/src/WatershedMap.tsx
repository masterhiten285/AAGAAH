import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import { type GeoJSONSource, type Map as MapInstance } from 'maplibre-gl'
import type { FeatureCollection } from 'geojson'
import type { LocationRisk, Pilot } from './types'
import { get } from './api'
import {
  Layers,
  Search,
  RotateCcw,
  Maximize2,
  Navigation,
  Compass,
  Sparkles,
  CloudRain,
  Waves,
  Mountain,
  AlertTriangle,
  Info,
  ChevronRight
} from 'lucide-react'
import 'maplibre-gl/dist/maplibre-gl.css'

export const colors: Record<string, string> = {
  Normal: '#2E7D5B',
  Watch: '#B58900',
  Warning: '#D97706',
  Critical: '#C62828',
  Unknown: '#667482'
}

export interface MapLayerState {
  terrain: boolean
  catchments: boolean
  rivers: boolean
  flows: boolean
  exposureBuffer: boolean
  regionalContext: boolean
  nationalEvents: boolean
}

// National / Himalayan Disaster Events for India Situational Awareness
export interface NationalEvent {
  id: string
  title: string
  location: string
  state: string
  coords: [number, number]
  severity: 'CRITICAL' | 'WARNING' | 'WATCH'
  date: string
  type: 'Cloudburst / Flash Flood' | 'Landslide' | 'River Surge' | 'Glacial Surge'
  source: string
  summary: string
  icon: 'cloud' | 'wave' | 'mountain'
}

export const NATIONAL_EVENTS: NationalEvent[] = [
  {
    id: 'dehradun-2025',
    title: 'Dehradun Cloudburst & Song River Surge',
    location: 'Dehradun / Maldevta',
    state: 'Uttarakhand',
    coords: [78.08, 30.34],
    severity: 'CRITICAL',
    date: '15–16 Sept 2025',
    type: 'Cloudburst / Flash Flood',
    source: 'Official SDMA / IMD Report',
    summary: '147 mm localized cloudburst causing rapid surge in Song and Rispana catchments; bridge scouring and sediment choking.',
    icon: 'cloud'
  },
  {
    id: 'mandi-monsoon',
    title: 'Beas Tributary Flash Flood Watch',
    location: 'Mandi / Pandoh',
    state: 'Himachal Pradesh',
    coords: [76.93, 31.70],
    severity: 'WARNING',
    date: 'Monsoon Incident Archive',
    type: 'River Surge',
    source: 'HP SDMA Advisory',
    summary: 'Elevated antecedent saturation across steep catchment tributaries discharging into Beas River.',
    icon: 'wave'
  },
  {
    id: 'kishtwar-surge',
    title: 'Chenab Upper Tributary Watch',
    location: 'Kishtwar Gorge',
    state: 'Jammu & Kashmir',
    coords: [75.76, 33.31],
    severity: 'WATCH',
    date: 'Monsoon Incident Archive',
    type: 'Cloudburst / Flash Flood',
    source: 'JK DMA Operational Bulletin',
    summary: 'Steep orographic rainfall triggering local debris flow warnings along upper gorge roads.',
    icon: 'mountain'
  },
  {
    id: 'teesta-chungthang',
    title: 'Teesta River Basin Surge Monitoring',
    location: 'Chungthang / Mangan',
    state: 'Sikkim',
    coords: [88.65, 27.60],
    severity: 'WATCH',
    date: 'Himalayan Regional Context',
    type: 'Glacial Surge',
    source: 'Sikkim SDMA Context',
    summary: 'High-altitude moraine lake runoff monitoring and glacial tributary gauge surveillance.',
    icon: 'wave'
  },
  {
    id: 'alaknanda-basin',
    title: 'Upper Alaknanda Basin Drainage Watch',
    location: 'Joshimath / Badrinath Corridor',
    state: 'Uttarakhand',
    coords: [79.45, 30.55],
    severity: 'WATCH',
    date: 'Regional Basin Context',
    type: 'River Surge',
    source: 'Uttarakhand SDMA Regional Context',
    summary: '11,050 km² major drainage network feeding Badrinath tributary system; upstream glacier-fed runoff monitoring.',
    icon: 'mountain'
  },
  {
    id: 'bhagirathi-basin',
    title: 'Bhagirathi Basin Catchment Monitoring',
    location: 'Uttarkashi / Tehri Corridor',
    state: 'Uttarakhand',
    coords: [78.60, 30.70],
    severity: 'WATCH',
    date: 'Regional Basin Context',
    type: 'River Surge',
    source: 'Uttarakhand SDMA Regional Context',
    summary: '7,530 km² catchment draining Gangotri glacier & Tehri reservoir headwaters; high-altitude precipitation surveillance.',
    icon: 'wave'
  },
  {
    id: 'yamuna-basin',
    title: 'Upper Yamuna Catchment Monitoring',
    location: 'Yamunotri / Tons Valley',
    state: 'Uttarakhand',
    coords: [78.20, 30.90],
    severity: 'WATCH',
    date: 'Regional Basin Context',
    type: 'Cloudburst / Flash Flood',
    source: 'Uttarakhand SDMA Regional Context',
    summary: 'Upper Yamunotri & Tons valley drainage; antecedent slope saturation and seasonal debris watch.',
    icon: 'mountain'
  }
]

// Regional Context Basins (Uttarakhand Himalayas)
const REGIONAL_BASINS = [
  { id: 'alaknanda', name: 'Upper Alaknanda Basin', coords: [79.45, 30.55], status: 'REGIONAL CONTEXT' },
  { id: 'bhagirathi', name: 'Bhagirathi Basin', coords: [78.60, 30.70], status: 'REGIONAL CONTEXT' },
  { id: 'yamuna', name: 'Upper Yamuna Basin', coords: [78.20, 30.90], status: 'REGIONAL CONTEXT' }
]

// Search target coordinates
const SEARCH_TARGETS: Record<string, { coords: [number, number]; zoom: number; pitch: number; preset: any }> = {
  kedarnath: { coords: [79.0669, 30.7352], zoom: 12.5, pitch: 45, preset: 'location' },
  gaurikund: { coords: [79.0275, 30.6522], zoom: 12.0, pitch: 40, preset: 'location' },
  sonprayag: { coords: [78.9988, 30.6310], zoom: 12.0, pitch: 40, preset: 'location' },
  guptkashi: { coords: [79.0786, 30.5230], zoom: 11.5, pitch: 35, preset: 'location' },
  rudraprayag: { coords: [78.9806, 30.2844], zoom: 11.5, pitch: 35, preset: 'location' },
  dehradun: { coords: [78.08, 30.34], zoom: 10.5, pitch: 20, preset: 'uttarakhand' },
  mandakini: { coords: [79.02, 30.55], zoom: 10.2, pitch: 35, preset: 'mandakini' },
  uttarakhand: { coords: [79.15, 30.35], zoom: 8.0, pitch: 0, preset: 'uttarakhand' },
  himalayas: { coords: [78.2, 31.0], zoom: 6.2, pitch: 0, preset: 'himalayas' },
  india: { coords: [78.96, 22.59], zoom: 4.3, pitch: 0, preset: 'india' }
}

export default function WatershedMap({
  pilot,
  locations,
  selected,
  onSelect,
  activeWatershed = 'mandakini',
  currentPreset = 'india',
  onPresetChange,
  onSelectEvent,
  selectedEvent = null,
  operationalMode = 'live'
}: {
  pilot: Pilot
  locations: LocationRisk[]
  selected: string
  onSelect: (id: string) => void
  activeWatershed?: string
  currentPreset?: 'india' | 'himalayas' | 'uttarakhand' | 'mandakini' | 'location'
  onPresetChange?: (preset: 'india' | 'himalayas' | 'uttarakhand' | 'mandakini' | 'location') => void
  onSelectEvent?: (event: NationalEvent) => void
  selectedEvent?: NationalEvent | null
  operationalMode?: 'live' | 'replay'
}) {
  const host = useRef<HTMLDivElement>(null)
  const map = useRef<MapInstance | null>(null)
  const markers = useRef<{ id: string; marker: maplibregl.Marker; element: HTMLButtonElement }[]>([])
  const eventMarkers = useRef<maplibregl.Marker[]>([])
  const regionalMarkers = useRef<maplibregl.Marker[]>([])
  const callback = useRef(onSelect)
  callback.current = onSelect

  const [ready, setReady] = useState(false)
  const [error, setError] = useState('')
  const [catchments, setCatchments] = useState<FeatureCollection | null>(null)
  const [showLayerMenu, setShowLayerMenu] = useState(false)
  const [showMapGuide, setShowMapGuide] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [cursorCoords, setCursorCoords] = useState<[number, number] | null>(null)

  const [layers, setLayers] = useState<MapLayerState>({
    terrain: true,
    catchments: true,
    rivers: true,
    flows: true,
    exposureBuffer: true,
    regionalContext: true,
    nationalEvents: true
  })

  // Programmatic zoom presets
  const zoomTo = (preset: 'india' | 'himalayas' | 'uttarakhand' | 'mandakini' | 'location') => {
    if (onPresetChange) onPresetChange(preset)
    if (!map.current) return

    if (preset === 'india') {
      map.current.flyTo({ center: [78.96, 22.59], zoom: 4.3, pitch: 0, bearing: 0, duration: 1200 })
    } else if (preset === 'himalayas') {
      map.current.flyTo({ center: [78.2, 31.0], zoom: 6.2, pitch: 0, bearing: 0, duration: 1200 })
    } else if (preset === 'uttarakhand') {
      map.current.flyTo({ center: [79.15, 30.35], zoom: 8.0, pitch: 0, bearing: 0, duration: 1200 })
    } else if (preset === 'mandakini') {
      map.current.flyTo({ center: [79.02, 30.55], zoom: 10.2, pitch: 35, bearing: 10, duration: 1200 })
    } else if (preset === 'location') {
      const loc = locations.find(l => l.id === selected)
      if (loc) {
        map.current.flyTo({ center: [loc.lon, loc.lat], zoom: 12.0, pitch: 45, bearing: 15, duration: 1200 })
      }
    }
  }

  // Auto-resize map when operationalMode or layout shifts
  useEffect(() => {
    if (ready && map.current) {
      const timer = setTimeout(() => {
        map.current?.resize()
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [operationalMode, ready])

  // React to preset changes from parent
  useEffect(() => {
    if (ready && map.current && !selectedEvent) {
      zoomTo(currentPreset)
    }
  }, [currentPreset, ready, selectedEvent])

  // React to selected national/regional disaster event
  useEffect(() => {
    if (ready && map.current && selectedEvent) {
      map.current.flyTo({
        center: selectedEvent.coords,
        zoom: 9.0,
        pitch: 28,
        bearing: 0,
        duration: 1400
      })
    }
  }, [selectedEvent, ready])

  // Search handler
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const q = searchQuery.toLowerCase().trim()
    const matchKey = Object.keys(SEARCH_TARGETS).find(k => k.includes(q) || q.includes(k))
    if (matchKey && map.current) {
      const t = SEARCH_TARGETS[matchKey]
      map.current.flyTo({ center: t.coords, zoom: t.zoom, pitch: t.pitch, duration: 1400 })
      if (t.preset && onPresetChange) onPresetChange(t.preset)
      if (['kedarnath', 'gaurikund', 'sonprayag', 'guptkashi', 'rudraprayag'].includes(matchKey)) {
        onSelect(matchKey)
      }
    }
  }

  useEffect(() => {
    if (!host.current) return
    let alive = true
    let instance: MapInstance

    try {
      instance = new maplibregl.Map({
        container: host.current,
        style: {
          version: 8,
          sources: {
            // CartoDB Positron / OSM global neutral basemap tiles
            'raster-tiles': {
              type: 'raster',
              tiles: [
                'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
                'https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
                'https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png'
              ],
              tileSize: 256,
              attribution: 'CARTO &copy; OpenStreetMap'
            }
          },
          layers: [
            {
              id: 'background-fill',
              type: 'background',
              paint: { 'background-color': '#EEF2F5' }
            },
            {
              id: 'carto-basemap',
              type: 'raster',
              source: 'raster-tiles',
              minzoom: 0,
              maxzoom: 19
            }
          ]
        },
        center: [78.96, 22.59], // Default: Full India View
        zoom: 4.3,
        pitch: 0,
        attributionControl: false,
        maxZoom: 15,
        minZoom: 3.8
      })
    } catch {
      setError('Map rendering is unavailable. Location priorities and replay controls remain usable.')
      return
    }

    map.current = instance
    instance.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'bottom-right')

    // Handle cursor coordinate tracking
    instance.on('mousemove', e => {
      if (alive) {
        setCursorCoords([e.lngLat.lng, e.lngLat.lat])
      }
    })

    // Handle container resizing
    const resizeObserver = new ResizeObserver(() => {
      instance.resize()
    })
    resizeObserver.observe(host.current)

    instance.on('error', () => {
      if (alive) setError('Basemap tiles could not load. Geospatial network layers remain operational.')
    })

    instance.on('load', async () => {
      try {
        instance.resize()

        const [basins, rivers, flowpaths, infrastructure] = await Promise.all([
          get<FeatureCollection>('/map/catchments'),
          get<FeatureCollection>('/map/rivers'),
          get<FeatureCollection>('/map/flowpaths'),
          get<FeatureCollection>('/map/infrastructure').catch(() => null)
        ])

        if (!alive) return

        // 1. Terrain Hillshade Raster for Mandakini Gorge
        if (pilot.terrain_image_corners?.length === 4) {
          instance.addSource('terrain', {
            type: 'image',
            url: '/api/map/terrain.png',
            coordinates: pilot.terrain_image_corners as [
              [number, number],
              [number, number],
              [number, number],
              [number, number]
            ]
          })
          instance.addLayer({
            id: 'terrain',
            type: 'raster',
            source: 'terrain',
            paint: { 'raster-opacity': 0.85, 'raster-fade-duration': 0 }
          })
        }

        // 2. Catchments Fill and Border
        instance.addSource('catchments', { type: 'geojson', data: basins })
        instance.addLayer({
          id: 'basin-fill',
          type: 'fill',
          source: 'catchments',
          paint: {
            'fill-color': ['coalesce', ['get', 'risk_color'], '#174A7E'],
            'fill-opacity': ['coalesce', ['get', 'fill_opacity'], 0.28]
          }
        })
        instance.addLayer({
          id: 'basin-border',
          type: 'line',
          source: 'catchments',
          paint: {
            'line-color': ['coalesce', ['get', 'border_color'], '#174A7E'],
            'line-width': ['coalesce', ['get', 'border_width'], 2]
          }
        })

        // 3. Rivers Network
        instance.addSource('rivers', { type: 'geojson', data: rivers })
        instance.addLayer({
          id: 'rivers-halo',
          type: 'line',
          source: 'rivers',
          paint: { 'line-color': '#bae6fd', 'line-width': 6, 'line-opacity': 0.9 }
        })
        instance.addLayer({
          id: 'rivers',
          type: 'line',
          source: 'rivers',
          paint: { 'line-color': '#0284c7', 'line-width': 2.6 }
        })

        // 4. D8 Flow Direction Paths
        instance.addSource('flowpaths', { type: 'geojson', data: flowpaths })
        instance.addLayer({
          id: 'flowpaths',
          type: 'line',
          source: 'flowpaths',
          paint: {
            'line-color': '#0369a1',
            'line-width': 1.4,
            'line-dasharray': [2, 3],
            'line-opacity': 0.75
          }
        })

        // 5. 150m Infrastructure Exposure Corridor
        if (infrastructure) {
          instance.addSource('infrastructure', { type: 'geojson', data: infrastructure })
          instance.addLayer({
            id: 'infra-buffer',
            type: 'fill',
            source: 'infrastructure',
            paint: { 'fill-color': '#fef3c7', 'fill-opacity': 0.5 }
          })
          instance.addLayer({
            id: 'infra-buffer-line',
            type: 'line',
            source: 'infrastructure',
            paint: { 'line-color': '#f59e0b', 'line-width': 1.2, 'line-dasharray': [2, 2] }
          })
          instance.addLayer({
            id: 'infra-points',
            type: 'circle',
            source: 'infrastructure',
            paint: {
              'circle-radius': 4.5,
              'circle-color': '#d97706',
              'circle-opacity': 0.95,
              'circle-stroke-width': 1.2,
              'circle-stroke-color': '#ffffff'
            }
          })
        }

        // 6. Active Pilot Station Markers (Mandakini Reaches)
        for (const location of pilot.locations) {
          const button = document.createElement('button')
          button.className = 'map-marker'
          button.setAttribute('aria-label', `Select ${location.name}`)

          const dot = document.createElement('span')
          dot.className = 'marker-dot'
          dot.textContent = '·'

          const label = document.createElement('span')
          label.className = 'marker-label'
          label.textContent = location.name.replace(' (001)', '')

          button.append(dot, label)
          button.onclick = () => {
            callback.current(location.id)
            if (onPresetChange) onPresetChange('location')
          }

          const marker = new maplibregl.Marker({ element: button, anchor: 'left' })
            .setLngLat([location.lon, location.lat])
            .addTo(instance)

          markers.current.push({ id: location.id, marker, element: button })
        }

        // 7. National / Himalayan Event Markers (India Situational Awareness)
        for (const ev of NATIONAL_EVENTS) {
          const sevClass = ev.severity.toLowerCase()
          const iconType = ev.type.includes('Cloudburst')
            ? 'rain'
            : ev.type.includes('Surge')
            ? 'flood'
            : ev.type.includes('Landslide')
            ? 'landslide'
            : 'advisory'
          const iconChar = iconType === 'rain' ? '🌧' : iconType === 'flood' ? '💧' : iconType === 'landslide' ? '▲' : 'ℹ'

          const div = document.createElement('div')
          div.className = `event-marker ${sevClass}`
          div.innerHTML = `<span class="event-gis-icon ${iconType}">${iconChar}</span><span class="event-status-ring ${sevClass}"></span><span>${ev.location} <small>[${ev.severity}]</small></span>`
          div.onclick = () => {
            if (onSelectEvent) onSelectEvent(ev)
          }

          const marker = new maplibregl.Marker({ element: div, anchor: 'center' })
            .setLngLat(ev.coords)
            .addTo(instance)

          eventMarkers.current.push(marker)
        }

        // 8. Regional Context Basins (Upper Alaknanda, Bhagirathi, Yamuna)
        for (const basin of REGIONAL_BASINS) {
          const div = document.createElement('div')
          div.className = 'regional-marker'
          div.innerHTML = `<span class="reg-dot"></span><span>${basin.name} <small>[CONTEXT]</small></span>`

          const marker = new maplibregl.Marker({ element: div, anchor: 'center' })
            .setLngLat(basin.coords as [number, number])
            .addTo(instance)

          regionalMarkers.current.push(marker)
        }

        instance.on('click', 'basin-fill', event => {
          const id = event.features?.[0]?.properties?.id
          if (id) {
            callback.current(String(id))
            if (onPresetChange) onPresetChange('location')
          }
        })

        setCatchments(basins)
        setReady(true)
      } catch {
        if (alive) setError('Watershed layers could not be loaded. Check API connection.')
      }
    })

    return () => {
      alive = false
      resizeObserver.disconnect()
      markers.current.forEach(m => m.marker.remove())
      markers.current = []
      eventMarkers.current.forEach(m => m.remove())
      eventMarkers.current = []
      regionalMarkers.current.forEach(m => m.remove())
      regionalMarkers.current = []
      instance.remove()
      map.current = null
    }
  }, [pilot])

  // Update marker styles and colors as live/replay data arrives
  useEffect(() => {
    if (!ready || !map.current || !catchments) return
    const risks = new Map(locations.map(l => [l.id, l]))
    const source = map.current.getSource('catchments') as GeoJSONSource | undefined
    if (source) {
      source.setData({
        ...catchments,
        features: catchments.features.map(f => {
          const isSelected = String(f.properties?.id) === selected
          const alertLevel = risks.get(String(f.properties?.id))?.alert_level || 'Unknown'
          return {
            ...f,
            properties: {
              ...f.properties,
              is_selected: isSelected,
              risk_color: colors[alertLevel],
              fill_opacity: isSelected ? 0.65 : 0.22,
              border_width: isSelected ? 4 : 1.5,
              border_color: isSelected ? (alertLevel === 'Normal' ? '#0284c7' : colors[alertLevel] || '#C62828') : '#174A7E'
            }
          }
        })
      })
    }

    markers.current.forEach(({ id, element }) => {
      const l = risks.get(id)
      element.style.setProperty('--marker', colors[l?.alert_level || 'Unknown'])
      element.classList.toggle('is-selected', id === selected)
      element.setAttribute('aria-pressed', String(id === selected))
      const dot = element.querySelector('.marker-dot')
      if (dot) dot.textContent = String(l?.rank ?? '·')
    })
  }, [locations, selected, ready, catchments])

  // Layer visibility toggle effect
  useEffect(() => {
    if (!ready || !map.current) return
    const setVis = (id: string, visible: boolean) => {
      if (map.current?.getLayer(id)) {
        map.current.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none')
      }
    }
    setVis('terrain', layers.terrain)
    setVis('basin-fill', layers.catchments)
    setVis('basin-border', layers.catchments)
    setVis('rivers', layers.rivers)
    setVis('rivers-halo', layers.rivers)
    setVis('flowpaths', layers.flows)
    setVis('infra-buffer', layers.exposureBuffer)
    setVis('infra-buffer-line', layers.exposureBuffer)
    setVis('infra-points', layers.exposureBuffer)

    // National events visibility
    eventMarkers.current.forEach(m => {
      const el = m.getElement()
      if (el) el.style.display = layers.nationalEvents ? 'flex' : 'none'
    })

    // Regional markers visibility
    regionalMarkers.current.forEach(m => {
      const el = m.getElement()
      if (el) el.style.display = layers.regionalContext ? 'flex' : 'none'
    })
  }, [layers, ready])

  // Current selected location data for map insight card
  const selectedLocData = locations.find(l => l.id === selected)

  // Map header title based on current zoom level - Clearly distinguish Context vs Active Pilot
  const mapLevelData =
    currentPreset === 'india'
      ? { title: 'NATIONAL SITUATIONAL AWARENESS', sub: 'Regional Context Overview (Non-Predictive)' }
      : currentPreset === 'himalayas'
      ? { title: 'HIMALAYAN MOUNTAIN ARC', sub: 'Regional Context Overview (Non-Predictive)' }
      : currentPreset === 'uttarakhand'
      ? { title: 'UTTARAKHAND RIVER BASINS', sub: 'Regional Catchment Context (Non-Predictive)' }
      : { title: 'MANDAKINI RIVER BASIN (1,638 km²)', sub: 'ACTIVE PREDICTIVE MODEL PILOT · 7 MONITORED REACHES' }

  return (
    <div className="watershed-map-root w-full h-full relative" ref={host}>
      {/* Top Map Toolbar: Search + Quick Geographic Presets */}
      <div className="absolute top-3 left-3 z-20 flex flex-col gap-2">
        <div className="flex items-center gap-2">
          {/* Location Search Input */}
          <form
            onSubmit={handleSearch}
            className="flex items-center bg-white/95 backdrop-blur border border-[#D5DDE4] rounded shadow-sm px-2 py-1"
          >
            <Search size={14} className="text-slate-400 mr-1.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search e.g. Kedarnath, Dehradun..."
              className="text-xs bg-transparent border-none focus:outline-none w-44 text-slate-800 placeholder-slate-400 font-medium"
            />
          </form>

          {/* Geographic Presets Bar */}
          <div className="geo-presets">
            <button
              onClick={() => zoomTo('india')}
              className={`geo-preset-btn ${currentPreset === 'india' ? 'active' : ''}`}
              title="National overview (Regional geographic context only)"
            >
              India (Context)
            </button>
            <button
              onClick={() => zoomTo('himalayas')}
              className={`geo-preset-btn ${currentPreset === 'himalayas' ? 'active' : ''}`}
              title="Himalayan mountain arc (Regional geographic context only)"
            >
              Himalayas (Context)
            </button>
            <button
              onClick={() => zoomTo('uttarakhand')}
              className={`geo-preset-btn ${currentPreset === 'uttarakhand' ? 'active' : ''}`}
              title="Uttarakhand state basins (Regional geographic context only)"
            >
              Uttarakhand (Context)
            </button>
            <button
              onClick={() => zoomTo('mandakini')}
              className={`geo-preset-btn ${currentPreset === 'mandakini' || currentPreset === 'location' ? 'active' : ''}`}
              title="Mandakini Basin — Active Predictive Model Pilot with 7 Monitored River Reaches"
            >
              Mandakini (Active Pilot)
            </button>
          </div>
        </div>

        {/* Dynamic Map Level Title Badge */}
        <div className="bg-[#17324A]/95 backdrop-blur text-white px-3.5 py-1.5 rounded-md shadow-md flex flex-col border border-[#174A7E]/50 max-w-fit">
          <div className="text-[11.5px] font-extrabold tracking-wide uppercase text-white flex items-center gap-1.5">
            <Compass size={13} className="text-sky-300" />
            <span>{mapLevelData.title}</span>
          </div>
          <div className="text-[9.5px] text-sky-200 tracking-wider font-semibold uppercase pl-4">
            {mapLevelData.sub}
          </div>
        </div>
      </div>

      {/* Top Right Controls: Map Guide + Layers + Reset (Section 6 & 24) */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-2">
        <button
          onClick={() => setShowMapGuide(true)}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white/95 border border-[#D5DDE4] text-slate-700 hover:text-black rounded text-xs font-semibold shadow-sm"
          title="Explain symbols and risk levels shown on the map"
        >
          <Info size={13} className="text-[#174A7E]" />
          <span>Map Guide</span>
        </button>

        <div className="relative">
          <button
            onClick={() => setShowLayerMenu(!showLayerMenu)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white/95 border border-[#D5DDE4] text-slate-700 hover:text-black rounded text-xs font-semibold shadow-sm"
            title="Show or hide map information such as rainfall, rivers, risk and infrastructure"
          >
            <Layers size={13} className="text-[#174A7E]" />
            <span>Layers</span>
          </button>

          {showLayerMenu && (
            <div className="absolute top-9 right-0 w-72 bg-white border border-[#D5DDE4] p-3 rounded-md shadow-xl z-30 space-y-2 text-xs">
              <div className="flex justify-between items-center pb-1.5 border-b border-slate-200">
                <span className="font-bold text-slate-900 uppercase text-[10px] tracking-wider">
                  Topographic & GIS Layers
                </span>
                <button
                  onClick={() => setShowLayerMenu(false)}
                  className="text-slate-400 hover:text-black font-bold"
                >
                  ✕
                </button>
              </div>

              {[
                { k: 'nationalEvents', label: 'National Disaster Events', tag: 'EVENTS' },
                { k: 'catchments', label: 'Mandakini Catchment Polygon', tag: 'HYDRO' },
                { k: 'rivers', label: 'Mandakini River Network', tag: 'D8' },
                { k: 'flows', label: 'Flow Direction Vectors', tag: 'ROUTING' },
                { k: 'exposureBuffer', label: '150m Infrastructure Corridor', tag: 'HEURISTIC' },
                { k: 'regionalContext', label: 'Regional Himalayan Basins', tag: 'CONTEXT' },
                { k: 'terrain', label: 'Copernicus 30m Hillshade', tag: 'DEM' }
              ].map(({ k, label, tag }) => {
                const active = layers[k as keyof MapLayerState]
                return (
                  <label
                    key={k}
                    className="flex items-center justify-between text-slate-700 hover:text-black cursor-pointer py-1 select-none"
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={active}
                        onChange={e => setLayers({ ...layers, [k]: e.target.checked })}
                        className="rounded border-slate-300 text-[#174A7E] focus:ring-0"
                      />
                      <span>{label}</span>
                    </div>
                    <span className="text-[9px] px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded border border-slate-200">
                      {tag}
                    </span>
                  </label>
                )
              })}

            </div>
          )}
        </div>

        {/* Reset Button (Quick return to India overview) */}
        <button
          onClick={() => zoomTo('india')}
          className="flex items-center gap-1 px-2.5 py-1.5 bg-white/95 border border-[#D5DDE4] text-slate-700 hover:text-black rounded text-xs font-semibold shadow-sm"
          title="Reset to National Overview"
        >
          <RotateCcw size={12} className="text-[#174A7E]" />
          <span>Reset</span>
        </button>
      </div>

      {/* Map Guide Modal (Section 24) */}
      {showMapGuide && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-[#D5DDE4] rounded-lg max-w-md w-full shadow-2xl overflow-hidden text-xs">
            <div className="p-3.5 border-b border-[#D5DDE4] flex items-center justify-between bg-[#17324A] text-white">
              <span className="font-bold flex items-center gap-2">
                <Info size={15} className="text-sky-300" />
                AAGAAH Map Guide & Symbols
              </span>
              <button onClick={() => setShowMapGuide(false)} className="text-slate-300 hover:text-white font-bold p-1">
                ✕
              </button>
            </div>

            <div className="p-4 space-y-3.5 text-slate-700">
              <div>
                <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
                  1. Operational Risk Tiers
                </span>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="flex items-center gap-2 p-1.5 bg-red-50 border border-red-200 rounded">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#C62828]" />
                    <span><strong>Critical:</strong> &gt;70% Exceedance</span>
                  </div>
                  <div className="flex items-center gap-2 p-1.5 bg-amber-50 border border-amber-200 rounded">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#D97706]" />
                    <span><strong>Warning:</strong> 40–70% Watch</span>
                  </div>
                  <div className="flex items-center gap-2 p-1.5 bg-yellow-50 border border-yellow-200 rounded">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#B58900]" />
                    <span><strong>Watch:</strong> 20–40% Advisory</span>
                  </div>
                  <div className="flex items-center gap-2 p-1.5 bg-emerald-50 border border-emerald-200 rounded">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#2E7D5B]" />
                    <span><strong>Normal:</strong> Baseline flow</span>
                  </div>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
                  2. Regional Event Markers
                </span>
                <div className="space-y-1.5 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="p-1 bg-blue-100 rounded text-blue-700 font-bold">🌧</span>
                    <span><strong>Extreme Rainfall / Cloudburst:</strong> Localized rainfall spike</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="p-1 bg-sky-100 rounded text-sky-700 font-bold">💧</span>
                    <span><strong>River / Glacial Surge:</strong> High discharge or moraine runoff</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="p-1 bg-amber-100 rounded text-amber-700 font-bold">▲</span>
                    <span><strong>Landslide / Debris Flow:</strong> Slope failure / road blockage</span>
                  </div>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
                  3. Geospatial Coverage Boundaries
                </span>
                <div className="space-y-1 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-1 bg-[#174A7E] rounded" />
                    <span><strong>Blue Boundary:</strong> AAGAAH Active Model Pilot (Mandakini Basin)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-0.5 border-b border-dashed border-slate-500" />
                    <span><strong>Dashed Grey:</strong> Regional Himalayan context (Alaknanda, Bhagirathi, Yamuna)</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button onClick={() => setShowMapGuide(false)} className="btn-primary text-xs py-1 px-4">
                Close Guide
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Tactical Map Insight Card (Displays on Map when location selected) */}
      {selectedLocData && (currentPreset === 'mandakini' || currentPreset === 'location') && (
        <div className="absolute bottom-12 right-3 z-20 bg-white/95 backdrop-blur border border-[#174A7E]/30 p-3 rounded-lg shadow-lg text-xs w-64 space-y-1.5 border-l-4 border-l-[#C62828]">
          <div className="flex justify-between items-center">
            <span className="font-bold text-slate-900 text-[12.5px]">
              {selectedLocData.name.replace(' (001)', '')}
            </span>
            <span
              className="text-[10px] font-bold px-1.5 py-0.5 rounded text-white"
              style={{ backgroundColor: colors[selectedLocData.alert_level] }}
            >
              {selectedLocData.alert_level.toUpperCase()}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-1 text-[11px] pt-1">
            <div className="bg-slate-50 p-1 rounded text-center border border-slate-200">
              <span className="text-[9px] text-slate-500 block">HAZARD</span>
              <strong className="text-red-700">{Math.round((selectedLocData.routed_risk || 0) * 100)}%</strong>
            </div>
            <div className="bg-slate-50 p-1 rounded text-center border border-slate-200">
              <span className="text-[9px] text-slate-500 block">ADEQUACY</span>
              <strong className="text-slate-800">{Math.round(selectedLocData.confidence * 100)}/100</strong>
            </div>
            <div className="bg-slate-50 p-1 rounded text-center border border-slate-200">
              <span className="text-[9px] text-slate-500 block">PRIORITY</span>
              <strong className="text-[#174A7E]">P{selectedLocData.rank}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Left Map Legend (Positioned safely above sliding dock bar) */}
      <div className="absolute bottom-12 left-3 bg-white/95 backdrop-blur border border-slate-200/90 px-3 py-1.5 rounded-lg shadow-sm text-xs space-y-1.5 z-10 max-w-sm">
        <div className="flex items-center justify-between border-b border-slate-200 pb-1">
          <span className="text-[10px] font-bold text-slate-700 uppercase tracking-wider">
            Hydrological Legend
          </span>
          <span className="text-[9px] text-slate-400">CartoDB &middot; WGS 84</span>
        </div>

        {/* Risk Status Tiers */}
        <div className="grid grid-cols-4 gap-2 text-[10.5px]">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#C62828]" />
            <span className="text-slate-800">Critical</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#D97706]" />
            <span className="text-slate-800">Warning</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#B58900]" />
            <span className="text-slate-800">Watch</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#2E7D5B]" />
            <span className="text-slate-800">Normal</span>
          </div>
        </div>

        {/* GIS Event Symbols */}
        <div className="grid grid-cols-3 gap-1.5 text-[10px] text-slate-700 pt-1 border-t border-slate-100">
          <div className="flex items-center gap-1">
            <span className="text-sky-600 font-bold">◆</span>
            <span>Incident / Surge</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-blue-600 font-bold">◆</span>
            <span>Extreme Rain</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-amber-700 font-bold">◆</span>
            <span>Landslide</span>
          </div>
        </div>

        {/* Coverage Boundaries */}
        <div className="flex items-center gap-4 text-[10px] text-slate-600 pt-0.5 border-t border-slate-100">
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-1 bg-[#174A7E] rounded" />
            <span>Active Pilot (Mandakini Reaches)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-0.5 border-b border-dashed border-slate-500" />
            <span>Regional Context (Non-Predictive)</span>
          </div>
        </div>
      </div>

      {/* Bottom Right Coordinates / Cursor Position */}
      <div className="absolute bottom-12 right-12 bg-white/95 backdrop-blur border border-slate-200/90 px-2.5 py-1 rounded-md text-[10px] font-mono text-slate-700 shadow-sm z-10 flex items-center gap-2">
        <span className="text-slate-500 uppercase text-[9px] font-sans font-bold">CURSOR:</span>
        <span className="font-bold text-slate-900">
          {cursorCoords
            ? `${cursorCoords[1].toFixed(3)}°N, ${cursorCoords[0].toFixed(3)}°E`
            : '30.550°N, 79.020°E'}
        </span>
        <span className="text-slate-300">|</span>
        <span className="text-slate-500">WGS 84</span>
      </div>

      {error && (
        <div className="map-error" role="alert">
          {error}
        </div>
      )}
    </div>
  )
}
