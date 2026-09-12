import {test,expect} from '@playwright/test'
const headers={'X-Control-Token':'local-demo-only'}
test.beforeEach(async({request})=>{
  const result=await request.post('/api/replay/control',{headers,data:{action:'reset'}})
  expect(result.ok()).toBeTruthy()
})

test('real backend replay updates the map, priorities, explanation and history',async({page,request})=>{
  const errors:string[]=[]
  page.on('pageerror',error=>errors.push(error.message))
  await page.goto('/')
  await expect(page.getByRole('heading',{name:'Mandakini watershed'})).toBeVisible()
  await expect(page.getByRole('button',{name:'Select Kedarnath',exact:true})).toBeVisible()
  await expect(page.getByText('Synthetic scenario.',{exact:true})).toBeVisible()
  const baseline=await (await request.get('/api/dashboard')).json()
  await page.getByRole('slider',{name:'Replay hour'}).fill('30')
  await page.getByRole('button',{name:'Go to hour 30'}).click()
  await expect(page.locator('.details-panel .badge')).toHaveText('Critical')
  const peak=await (await request.get('/api/dashboard')).json()
  expect(peak.step).toBe(30)
  expect(peak.summary.highest_risk).toBeGreaterThan(baseline.summary.highest_risk+.4)
  await expect(page.getByRole('img',{name:'Rainfall bars and synthetic model score history'})).toBeVisible()
  await page.getByRole('button',{name:'Select Sonprayag',exact:true}).click()
  await expect(page.locator('.details-panel h2')).toHaveText('Sonprayag')
  await page.screenshot({path:'../artifacts/dashboard-desktop.png',fullPage:true})
  expect(errors).toEqual([])
})

test('play advances through scheduler and pause stops playback',async({page,request})=>{
  await page.goto('/')
  await page.getByRole('button',{name:'Play replay'}).click()
  await expect.poll(async()=> (await (await request.get('/api/dashboard')).json()).step,{timeout:20000}).toBeGreaterThan(0)
  await page.getByRole('button',{name:'Pause replay'}).click()
  await expect(page.getByRole('button',{name:'Play replay'})).toBeVisible()
  const snapshot=await (await request.get('/api/dashboard')).json()
  expect(snapshot.running).toBe(false)
  const tick=await (await request.post('/api/internal/tick',{headers})).json()
  expect(tick.step).toBe(snapshot.step)
})

test('source details and mobile layout remain usable',async({page})=>{
  await page.setViewportSize({width:390,height:844})
  await page.goto('/')
  await expect(page.getByRole('button',{name:'Select Kedarnath',exact:true})).toBeVisible()
  await page.getByRole('button',{name:'Data sources',exact:true}).click()
  await expect(page.getByRole('heading',{name:'Data sources & provenance'})).toBeVisible()
  await page.locator('summary').filter({hasText:'NASA GPM IMERG'}).click()
  await expect(page.getByText('Metadata public; tested PPS GIS directory returned HTTP 401.',{exact:true})).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).toHaveCount(0)
  const dimensions=await page.evaluate(()=>({width:innerWidth,content:document.documentElement.scrollWidth}))
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.width+1)
  await page.screenshot({path:'../artifacts/dashboard-mobile.png',fullPage:true})
})

test('backend failure is visible rather than silently presenting cached data as current',async({page})=>{
  await page.route('**/api/dashboard',route=>route.fulfill({status:503,body:'unavailable'}))
  await page.goto('/')
  await expect(page.getByRole('alert').filter({hasText:'Cannot reach the backend'})).toBeVisible({timeout:20000})
})
