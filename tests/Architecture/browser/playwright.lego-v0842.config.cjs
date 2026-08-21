const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: /(lego-drop-zones-v0838|lego-side-by-side-history-v0840|lego-resize-v0841|lego-responsive-layout-v0842)\.spec\.cjs/,
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: 'line',
  use: {
    headless: true,
    viewport: { width: 1440, height: 1000 },
  },
  projects: [
    { name: 'system-chrome', use: { channel: 'chrome' } },
    { name: 'chromium-engine', use: { browserName: 'chromium' } },
    { name: 'firefox-engine', use: { browserName: 'firefox' } },
    { name: 'webkit-engine', use: { browserName: 'webkit' } },
  ],
});
