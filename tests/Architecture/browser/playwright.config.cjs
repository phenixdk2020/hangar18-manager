const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: /(runtime|history-guard-v0816|history-restore-latch-v0817)\.spec\.cjs/,
  timeout: 30000,
  fullyParallel: false,
  retries: 0,
  reporter: 'line',
  projects: [
    { name: 'chromium-engine', use: { browserName: 'chromium', viewport: { width: 1440, height: 900 } } },
    { name: 'firefox-engine', use: { browserName: 'firefox', viewport: { width: 1440, height: 900 } } },
    { name: 'webkit-engine', use: { browserName: 'webkit', viewport: { width: 1440, height: 900 } } },
  ],
});
