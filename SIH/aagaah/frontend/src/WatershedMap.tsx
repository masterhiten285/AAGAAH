import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { type GeoJSONSource, type Map as MapInstance } from 'maplibre-gl'
import type { FeatureCollection } from 'geojson'
import type { LocationRisk, Pilot } from './types'
import { get } from './api'
import { Layers, Search, Info } from 'lucide-react'
import 'maplibre-gl/dist/maplibre-gl.css'

// Bundle the worker explicitly so Vite preserves its shared-module imports.
maplibregl.setWorkerUrl(workerUrl)

export const colors: Record<string, string> = {
  Normal: '#2E7D5B',
  Watch: '#B58900',
  Warning: '#D97706',
  Critical: '#C62828',
  Unknown: '#667482',
}

export interface MapLayerState {
  terrain: boolean
  catchments: boolean
  rivers: boolean
  flows: boolean
  exposureBuffer: boolean
}

type GeoPreset =
  | 'india'
  | 'himalayas'
  | 'uttarakhand'
  | 'mandakini'
  | 'location'

// Search target coordinates
const SEARCH_TARGETS: Record<
  string,
  { coords: [number, number]; zoom: number; pitch: number; preset: GeoPreset }
> = {
  kedarnath: {
    coords: [79.0669, 30.7352],
    zoom: 12.5,
    pitch: 45,
    preset: 'location',
  },
  gaurikund: {
    coords: [79.0275, 30.6522],
    zoom: 12.0,
    pitch: 40,
    preset: 'location',
  },
  sonprayag: {
    coords: [78.9988, 30.631],
    zoom: 12.0,
    pitch: 40,
    preset: 'location',
  },
  guptkashi: {
    coords: [79.0786, 30.523],
    zoom: 11.5,
    pitch: 35,
    preset: 'location',
  },
  rudraprayag: {
    coords: [78.9806, 30.2844],
    zoom: 11.5,
    pitch: 35,
    preset: 'location',
  },
  dehradun: {
    coords: [78.08, 30.34],
    zoom: 10.5,
    pitch: 20,
    preset: 'uttarakhand',
  },
  mandakini: {
    coords: [79.02, 30.55],
    zoom: 10.2,
    pitch: 35,
    preset: 'mandakini',
  },
  uttarakhand: {
    coords: [79.15, 30.35],
    zoom: 8.0,
    pitch: 0,
    preset: 'uttarakhand',
  },
  himalayas: { coords: [78.2, 31.0], zoom: 6.2, pitch: 0, preset: 'himalayas' },
  india: { coords: [78.96, 22.59], zoom: 4.3, pitch: 0, preset: 'india' },
}

export default function WatershedMap({
  pilot,
  locations,
  selected,
  onSelect,
  currentPreset = 'mandakini',
  onPresetChange,
  operationalMode = 'replay',
}: {
  pilot: Pilot
  locations: LocationRisk[]
  selected: string
  onSelect: (id: string) => void
  currentPreset?:
    | 'india'
    | 'himalayas'
    | 'uttarakhand'
    | 'mandakini'
    | 'location'
  onPresetChange?: (
    preset: 'india' | 'himalayas' | 'uttarakhand' | 'mandakini' | 'location',
  ) => void
  operationalMode?: 'live' | 'replay'
}) {
  const host = useRef<HTMLDivElement>(null)
  const map = useRef<MapInstance | null>(null)
  const basinBounds = useRef<maplibregl.LngLatBounds | null>(null)
  const markers = useRef<
    { id: string; marker: maplibregl.Marker; element: HTMLButtonElement }[]
  >([])
  const callback = useRef(onSelect)
  callback.current = onSelect

  const [ready, setReady] = useState(false)
  const [rendered, setRendered] = useState(false)
  const [error, setError] = useState('')
  const [catchments, setCatchments] = useState<FeatureCollection | null>(null)
  const [showLayerMenu, setShowLayerMenu] = useState(false)
  const [showMapGuide, setShowMapGuide] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [cursorCoords, setCursorCoords] = useState<[number, number] | null>(
    null,
  )

  const [layers, setLayers] = useState<MapLayerState>({
    terrain: true,
    catchments: true,
    rivers: true,
    flows: true,
    exposureBuffer: true,
  })

  // Programmatic zoom presets
  const zoomTo = (
    preset: 'india' | 'himalayas' | 'uttarakhand' | 'mandakini' | 'location',
  ) => {
    if (onPresetChange) onPresetChange(preset)
    if (!map.current) return

    if (preset === 'india') {
      map.current.flyTo({
        center: [78.96, 22.59],
        zoom: 4.3,
        pitch: 0,
        bearing: 0,
        duration: 1200,
      })
    } else if (preset === 'himalayas') {
      map.current.flyTo({
        center: [78.2, 31.0],
        zoom: 6.2,
        pitch: 0,
        bearing: 0,
        duration: 1200,
      })
    } else if (preset === 'uttarakhand') {
      map.current.flyTo({
        center: [79.15, 30.35],
        zoom: 8.0,
        pitch: 0,
        bearing: 0,
        duration: 1200,
      })
    } else if (preset === 'mandakini') {
      if (basinBounds.current)
        map.current.fitBounds(basinBounds.current, {
          padding: { top: 100, bottom: 100, left: 35, right: 35 },
          duration: 400,
          pitch: 0,
          bearing: 0,
        })
    } else if (preset === 'location') {
      const loc = locations.find((l) => l.id === selected)
      if (loc) {
        map.current.flyTo({
          center: [loc.lon, loc.lat],
          zoom: 12.0,
          pitch: 45,
          bearing: 15,
          duration: 1200,
        })
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
    if (ready && map.current) {
      zoomTo(currentPreset)
    }
  }, [currentPreset, ready, selected])

  // Search handler
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const q = searchQuery.toLowerCase().trim()
    if (!q) return
    const matchKey = Object.keys(SEARCH_TARGETS).find(
      (k) => k.includes(q) || q.includes(k),
    )
    if (matchKey && map.current) {
      const t = SEARCH_TARGETS[matchKey]
      map.current.flyTo({
        center: t.coords,
        zoom: t.zoom,
        pitch: t.pitch,
        duration: 1400,
      })
      if (t.preset && onPresetChange) onPresetChange(t.preset)
      if (
        [
          'kedarnath',
          'gaurikund',
          'sonprayag',
          'guptkashi',
          'rudraprayag',
        ].includes(matchKey)
      ) {
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
          sources: {},
          layers: [
            {
              id: 'background-fill',
              type: 'background',
              paint: { 'background-color': '#e8eff2' },
            },
          ],
        },
        center: [79.02, 30.55],
        zoom: 10.2,
        pitch: 0,
        attributionControl: {
          compact: true,
          customAttribution:
            'Terrain: Copernicus DEM · Assets/rivers: © OpenStreetMap contributors',
        },
        maxZoom: 15,
        minZoom: 3.8,
      })
    } catch {
      setError(
        'Map rendering is unavailable. Location priorities and replay controls remain usable.',
      )
      return
    }

    map.current = instance
    instance.on('idle', () => {
      if (
        alive &&
        instance.getLayer('rivers') &&
        instance.queryRenderedFeatures({ layers: ['basin-fill', 'rivers'] })
          .length > 0
      )
        setRendered(true)
    })
    instance.addControl(
      new maplibregl.NavigationControl({ showCompass: true }),
      'bottom-right',
    )

    // Handle cursor coordinate tracking
    instance.on('mousemove', (e) => {
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
      if (alive)
        setError(
          'A map resource could not load. Check visible layers; the location table remains available.',
        )
    })

    // Load the local terrain and GIS layers as soon as the base style is available.
    instance.once('style.load', async () => {
      try {
        instance.resize()

        const [basins, rivers, flowpaths, infrastructure, corridor] =
          await Promise.all([
            get<FeatureCollection>('/map/catchments'),
            get<FeatureCollection>('/map/rivers'),
            get<FeatureCollection>('/map/flowpaths'),
            get<FeatureCollection>('/map/infrastructure'),
            get<FeatureCollection>('/map/screening-corridor'),
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
              [number, number],
            ],
          })
          instance.addLayer({
            id: 'terrain',
            type: 'raster',
            source: 'terrain',
            paint: { 'raster-opacity': 0.18, 'raster-fade-duration': 0 },
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
            'fill-opacity': ['coalesce', ['get', 'fill_opacity'], 0.28],
          },
        })
        instance.addLayer({
          id: 'basin-border',
          type: 'line',
          source: 'catchments',
          paint: {
            'line-color': ['coalesce', ['get', 'border_color'], '#174A7E'],
            'line-width': ['coalesce', ['get', 'border_width'], 2],
          },
        })

        // 3. Rivers Network
        instance.addSource('rivers', { type: 'geojson', data: rivers })
        instance.addLayer({
          id: 'rivers-halo',
          type: 'line',
          source: 'rivers',
          paint: {
            'line-color': '#bae6fd',
            'line-width': 6,
            'line-opacity': 0.9,
          },
        })
        instance.addLayer({
          id: 'rivers',
          type: 'line',
          source: 'rivers',
          paint: { 'line-color': '#0284c7', 'line-width': 2.6 },
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
            'line-opacity': 0.75,
          },
        })

        // Cached asset geometry and a separate metric candidate screening corridor
        if (infrastructure) {
          instance.addSource('infrastructure', {
            type: 'geojson',
            data: infrastructure,
          })
          instance.addSource('screening-corridor', {
            type: 'geojson',
            data: corridor,
          })
          instance.addLayer({
            id: 'infra-buffer',
            type: 'fill',
            source: 'screening-corridor',
            paint: { 'fill-color': '#fef3c7', 'fill-opacity': 0.5 },
          })
          instance.addLayer({
            id: 'infra-buffer-line',
            type: 'line',
            source: 'infrastructure',
            paint: {
              'line-color': '#f59e0b',
              'line-width': 1.2,
              'line-dasharray': [2, 2],
            },
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
              'circle-stroke-color': '#ffffff',
            },
          })
        }

        // 6. Pilot location markers (Mandakini Reaches)
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

          const marker = new maplibregl.Marker({
            element: button,
            anchor: 'left',
          })
            .setLngLat([location.lon, location.lat])
            .addTo(instance)

          markers.current.push({ id: location.id, marker, element: button })
        }

        instance.on('click', 'basin-fill', (event) => {
          const id = event.features?.[0]?.properties?.id
          if (id) {
            callback.current(String(id))
            if (onPresetChange) onPresetChange('location')
          }
        })

        const bounds = new maplibregl.LngLatBounds()
        const extend = (coordinates: unknown) => {
          if (!Array.isArray(coordinates)) return
          if (
            typeof coordinates[0] === 'number' &&
            typeof coordinates[1] === 'number'
          )
            bounds.extend([coordinates[0], coordinates[1]])
          else coordinates.forEach(extend)
        }
        basins.features.forEach((feature) => {
          if ('coordinates' in feature.geometry)
            extend(feature.geometry.coordinates)
        })
        if (!bounds.isEmpty()) basinBounds.current = bounds
        setCatchments(basins)
        setReady(true)
      } catch {
        if (alive)
          setError(
            'Watershed layers could not be loaded. Check API connection.',
          )
      }
    })

    return () => {
      alive = false
      resizeObserver.disconnect()
      markers.current.forEach((m) => m.marker.remove())
      markers.current = []
      instance.remove()
      map.current = null
    }
  }, [pilot])

  // Update marker styles and colors as live/replay data arrives
  useEffect(() => {
    if (!ready || !map.current || !catchments) return
    const risks = new Map(locations.map((l) => [l.id, l]))
    const assetIds =
      risks.get(selected)?.exposure.assets.map((asset) => asset.id) || []
    for (const layer of ['infra-buffer-line', 'infra-points']) {
      if (map.current.getLayer(layer))
        map.current.setFilter(layer, [
          'in',
          ['get', 'id'],
          ['literal', assetIds],
        ])
    }
    const source = map.current.getSource('catchments') as
      | GeoJSONSource
      | undefined
    if (source) {
      source.setData({
        ...catchments,
        features: catchments.features.map((f) => {
          const isSelected = String(f.properties?.id) === selected
          const alertLevel =
            risks.get(String(f.properties?.id))?.alert_level || 'Unknown'
          return {
            ...f,
            properties: {
              ...f.properties,
              is_selected: isSelected,
              risk_color: colors[alertLevel],
              fill_opacity: isSelected ? 0.65 : 0.22,
              border_width: isSelected ? 4 : 1.5,
              border_color: isSelected
                ? alertLevel === 'Normal'
                  ? '#0284c7'
                  : colors[alertLevel] || '#C62828'
                : '#174A7E',
            },
          }
        }),
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
        map.current.setLayoutProperty(
          id,
          'visibility',
          visible ? 'visible' : 'none',
        )
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
  }, [layers, ready])

  return (
    <div
      className="watershed-map-root w-full h-full relative"
      data-map-ready={ready}
      data-map-rendered={rendered}
    >
      <div className="absolute inset-0" ref={host} />
      <div className="map-tools">
        <form onSubmit={handleSearch} className="map-search">
          <Search size={14} />
          <input
            aria-label="Search map location"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search Kedarnath…"
          />
          <button type="submit">Find</button>
        </form>
        <div className="map-tool-buttons">
          <button onClick={() => zoomTo('mandakini')}>Basin extent</button>
          <button
            onClick={() => setShowLayerMenu(!showLayerMenu)}
            aria-expanded={showLayerMenu}
          >
            <Layers size={14} />
            Layers
          </button>
          <button
            onClick={() => setShowMapGuide(!showMapGuide)}
            aria-expanded={showMapGuide}
          >
            <Info size={14} />
            Map guide
          </button>
        </div>
        {showLayerMenu && (
          <div className="map-layer-menu">
            {(
              [
                ['catchments', 'Provisional catchments'],
                ['rivers', 'Mapped rivers (OSM)'],
                ['flows', 'DEM downstream flow paths'],
                ['exposureBuffer', '150m corridor & selected candidate assets'],
                ['terrain', 'Terrain hillshade (120m analysis)'],
              ] as [keyof MapLayerState, string][]
            ).map(([key, label]) => (
              <label key={key}>
                <input
                  type="checkbox"
                  checked={layers[key]}
                  onChange={(event) =>
                    setLayers({ ...layers, [key]: event.target.checked })
                  }
                />
                {label}
              </label>
            ))}
            <p>
              Amber = screening corridor and selected candidate assets; never an
              inundation boundary.
            </p>
          </div>
        )}
        {showMapGuide && (
          <div className="map-guide">
            <strong>Read the map</strong>
            <p>
              Catchment colours show routed demo screening levels: Critical
              ≥80%, Warning 55–&lt;80%, Watch 25–&lt;55%, Normal &lt;25%.
              Unknown means no routed score. These are not official warning
              thresholds.
            </p>
            <p>
              Blue lines: mapped rivers. Dashed blue lines: DEM-derived paths.
              Amber: 150m candidate exposure corridor and selected candidate
              assets. Marker numbers are relative priority ranks. Assets and
              terrain are cached static data.
            </p>
            <button onClick={() => setShowMapGuide(false)}>Close guide</button>
          </div>
        )}
      </div>
      <div className="map-legend">
        <strong>Routed demo screening level</strong>
        <div>
          {Object.entries(colors).map(([name, color]) => (
            <span key={name}>
              <i style={{ background: color }} />
              {name}
            </span>
          ))}
        </div>
        <small>
          Coloured areas are provisional catchments, not flood extents.
        </small>
      </div>
      <div className="map-coordinates">
        {cursorCoords
          ? `${cursorCoords[1].toFixed(3)}°N, ${cursorCoords[0].toFixed(3)}°E`
          : 'Mandakini Basin'}{' '}
        · WGS 84
      </div>
      {error && (
        <div className="map-error" role="alert">
          {error}
        </div>
      )}
    </div>
  )
}
