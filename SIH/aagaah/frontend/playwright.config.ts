import {defineConfig} from '@playwright/test'
export default defineConfig({
  testDir:'./e2e',fullyParallel:false,workers:1,timeout:60000,
  use:{baseURL:process.env.AAGAAH_UI_URL||'http://127.0.0.1:5173',headless:true,
    viewport:{width:1440,height:1100},launchOptions:{args:['--enable-unsafe-swiftshader']},
    screenshot:'only-on-failure',trace:'retain-on-failure'},
  reporter:[['list'],['html',{open:'never'}]],
})
