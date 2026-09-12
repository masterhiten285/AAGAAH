import { test, expect } from '@playwright/test'
import { readFile } from 'node:fs/promises'
const headers = { 'X-Control-Token': 'local-demo-only' }

test.beforeEach(async ({ request }) => {
  const result = await request.post('/api/replay/control', {
    headers,
    data: { action: 'reset' },
  })
  expect(result.ok()).toBeTruthy()
})

test('real replay updates map, priorities, explanation and history', async ({
  page,
  request,
}) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'Mandakini watershed' }),
  ).toBeVisible()
  await expect(page.locator('.mode-banner')).toContainText('Synthetic scenario')
  await expect(page.locator('.watershed-map-root')).toHaveAttribute(
    'data-map-rendered',
    'true',
  )
  expect(
    await page
      .locator('.maplibregl-map')
      .evaluate((element) => element.getBoundingClientRect().height),
  ).toBeGreaterThan(400)
  await expect(
    page.getByRole('button', { name: 'Select Kedarnath', exact: true }),
  ).toBeVisible()
  const baseline = await (await request.get('/api/dashboard')).json()
  await page.getByRole('button', { name: 'Replay', exact: true }).click()
  await page.getByRole('slider', { name: 'Replay hour' }).fill('30')
  await page.getByRole('button', { name: 'Go to hour 30' }).click()
  await expect(page.locator('.details-panel .badge')).toHaveText('Critical')
  const peak = await (await request.get('/api/dashboard')).json()
  expect(peak.step).toBe(30)
  expect(peak.summary.highest_risk).toBeGreaterThan(
    baseline.summary.highest_risk + 0.4,
  )
  await expect(page.locator('.drivers')).toContainText(
    'Raises the demo model score',
  )
  await expect(
    page.getByRole('img', {
      name: 'Rainfall bars and synthetic model score history',
    }),
  ).toBeVisible()
  await page
    .getByRole('button', { name: 'Inspect Sonprayag', exact: true })
    .click()
  await expect(page.locator('.details-panel h2')).toHaveText('Sonprayag')
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: '../artifacts/judge-dashboard-desktop.png' })
  expect(errors).toEqual([])
})

test('play advances through scheduler; pause and reset retain deterministic state', async ({
  page,
  request,
}) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Replay', exact: true }).click()
  await page.getByRole('button', { name: 'Play replay' }).click()
  await expect
    .poll(
      async () => (await (await request.get('/api/dashboard')).json()).step,
      { timeout: 20000 },
    )
    .toBeGreaterThan(0)
  await page.getByRole('button', { name: 'Pause replay' }).click()
  await expect(page.getByRole('button', { name: 'Play replay' })).toBeVisible()
  const snapshot = await (await request.get('/api/dashboard')).json()
  expect(snapshot.running).toBe(false)
  expect(
    (await (await request.post('/api/internal/tick', { headers })).json()).step,
  ).toBe(snapshot.step)
  await page.getByRole('button', { name: 'Reset replay' }).click()
  await expect
    .poll(async () => (await (await request.get('/api/dashboard')).json()).step)
    .toBe(0)
})

test('live mode cannot display a replay as current monitoring', async ({
  page,
  request,
}) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Live monitoring Planned' }).click()
  await expect(
    page.getByRole('heading', { name: 'Live monitoring is not connected' }),
  ).toBeVisible()
  await expect(page.locator('.details-panel')).toHaveCount(0)
  await expect(page.locator('.watershed-map-root')).toHaveCount(0)
  expect((await request.get('/api/dashboard?mode=live')).status()).toBe(503)
  await page.getByRole('button', { name: 'Open labeled replay' }).click()
  await expect(page.locator('.mode-banner')).toContainText('Synthetic scenario')
})

test('model evidence and source provenance work on mobile without overflow', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'Mandakini watershed' }),
  ).toBeVisible()
  await expect(page.locator('.watershed-map-root')).toHaveAttribute(
    'data-map-rendered',
    'true',
  )
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(391)
  await page.screenshot({
    path: '../artifacts/judge-dashboard-mobile.png',
    fullPage: true,
  })
  await page
    .getByRole('button', { name: 'Data Sources & Freshness', exact: true })
    .click()
  await page.locator('summary').filter({ hasText: 'NASA GPM IMERG' }).click()
  await expect(
    page.getByText(
      'Metadata public; tested PPS GIS directory returned HTTP 401.',
      { exact: true },
    ),
  ).toBeVisible()
  await expect(
    page.locator('tr').filter({ hasText: 'Open-Meteo forecast' }),
  ).toContainText('PLANNED')
  await page
    .getByRole('button', { name: 'Model & Validation', exact: true })
    .click()
  await expect(
    page.getByRole('heading', { name: 'Model & Validation' }),
  ).toBeVisible()
  await expect(
    page.locator('.metric strong').filter({ hasText: 'Not established' }),
  ).toHaveCount(6)
  await expect(page.getByText('10.5 Hours', { exact: false })).toHaveCount(0)
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(391)
})

test('all map layers load and can be toggled with honest legend', async ({
  page,
  request,
}) => {
  await page.goto('/')
  await expect(page.locator('.watershed-map-root')).toHaveAttribute(
    'data-map-rendered',
    'true',
  )
  await page.getByRole('button', { name: 'Layers', exact: true }).click()
  for (const label of [
    'Provisional catchments',
    'Mapped rivers (OSM)',
    'DEM downstream flow paths',
    '150m corridor & selected candidate assets',
    'Terrain hillshade (120m analysis)',
  ]) {
    const checkbox = page.getByRole('checkbox', { name: label, exact: true })
    await expect(checkbox).toBeChecked()
    await checkbox.uncheck()
    await expect(checkbox).not.toBeChecked()
    await checkbox.check()
  }
  const corridor = await (
    await request.get('/api/map/screening-corridor')
  ).json()
  expect(corridor.features[0].geometry.type).toMatch(/Polygon/)
  expect(corridor.features[0].properties.distance_m).toBe(150)
  await page.getByRole('button', { name: 'Layers', exact: true }).click()
  await page.getByRole('button', { name: 'Map guide', exact: true }).click()
  await expect(page.locator('.map-guide')).toContainText('Critical ≥80%')
  await expect(page.locator('.map-guide')).toContainText(
    'not official warning thresholds',
  )
})

test('missing local observations suppress hazard and explanation, preserve upstream screening', async ({
  page,
  request,
}) => {
  const snapshot = await (await request.get('/api/dashboard')).json()
  const date = snapshot.as_of
  const predicted = await (
    await request.post('/api/predict', {
      data: {
        as_of: date,
        readings: [
          {
            location_id: 'kedarnath',
            observed_at: date,
            available_at: date,
            source: 'test-synthetic',
            synthetic: true,
            status: 'REPLAY',
            rainfall_mm: 50,
          },
        ],
      },
    })
  ).json()
  await page.route('**/api/dashboard', (route) =>
    route.fulfill({ json: { ...snapshot, ...predicted } }),
  )
  await page.goto('/')
  await page
    .getByRole('button', { name: 'Inspect Sonprayag', exact: true })
    .click()
  const details = page.locator('.details-panel')
  await expect(details.locator('.metric').first()).toContainText('Unavailable')
  await expect(details).toContainText(
    'Explanation withheld because the local hazard score is unavailable',
  )
  await expect(details).toContainText('Insufficient fresh evidence')
  await expect(details).toContainText('Dominant origin: Kedarnath')
  await expect(details).toContainText('No recent sources')
})

test('empty results and API failures remain explicit', async ({
  page,
  request,
}) => {
  const snapshot = await (await request.get('/api/dashboard')).json()
  await page.route('**/api/dashboard', (route) =>
    route.fulfill({
      json: {
        ...snapshot,
        locations: [],
        summary: { ...snapshot.summary, needs_review: 0 },
      },
    }),
  )
  await page.goto('/')
  await expect(
    page.getByText('No location results are available.', { exact: false }),
  ).toBeVisible()
  await expect(page.locator('.details-panel')).toHaveCount(0)
  await page.unroute('**/api/dashboard')
  await page.route('**/api/dashboard', (route) =>
    route.fulfill({ status: 503, body: 'unavailable' }),
  )
  await page.reload()
  await expect(
    page.getByRole('alert').filter({ hasText: 'Cannot reach the backend' }),
  ).toBeVisible({ timeout: 20000 })
})

test('authority draft export includes provenance and never issues a dispatch', async ({
  page,
}) => {
  await page.goto('/')
  const checkbox = page.getByRole('checkbox', {
    name: 'Verify rainfall and upstream river conditions',
  })
  await checkbox.check()
  await page
    .getByLabel('Draft verification notes')
    .fill('Request field confirmation of crossing access.')
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export review draft' }).click()
  const download = await downloadPromise
  const path = await download.path()
  const text = await readFile(path!, 'utf8')
  expect(text).toContain('DEMONSTRATION / AUTHORITY REVIEW DRAFT')
  expect(text).toContain('synthetic=true')
  expect(text).toContain(
    'No dispatch, official warning or evacuation has been issued.',
  )
  expect(text).toContain('Request field confirmation')
  await page
    .getByRole('button', { name: 'Inspect Sonprayag', exact: true })
    .click()
  await expect(checkbox).not.toBeChecked()
  await expect(page.getByLabel('Draft verification notes')).toHaveValue('')
})

test('data and model request failures display errors rather than evidence', async ({
  page,
}) => {
  await page.route('**/api/model-card', (route) =>
    route.fulfill({ status: 503, body: 'unavailable' }),
  )
  await page.route('**/api/sources', (route) =>
    route.fulfill({ status: 503, body: 'unavailable' }),
  )
  await page.goto('/')
  await page
    .getByRole('button', { name: 'Model & Validation', exact: true })
    .click()
  await expect(
    page.getByRole('alert').filter({ hasText: 'Model evidence unavailable' }),
  ).toBeVisible()
  await page
    .getByRole('button', { name: 'Data Sources & Freshness', exact: true })
    .click()
  await expect(
    page.getByRole('alert').filter({ hasText: 'Source catalog unavailable' }),
  ).toBeVisible()
})
