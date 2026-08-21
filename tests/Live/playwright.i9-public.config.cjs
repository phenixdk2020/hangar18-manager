const { defineConfig } = require('@playwright/test');

const baseURL = String(process.env.H18_TEST2_BASE_URL || 'https://test2.hangar18.dk').replace(/\/$/, '');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: /i9-public-readonly\.spec\.cjs/,
  timeout: 45000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  workers: 1,
  retries: 1,
  reporter: [
    ['line'],
    ['html', { outputFolder: 'artifacts/i9-public-report', open: 'never' }],
  ],
  use: {
    baseURL,
    headless: true,
    ignoreHTTPSErrors: false,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  outputDir: 'artifacts/i9-public-test-results',
  projects: [
    { name: 'system-chrome', use: { channel: 'chrome' } },
    { name: 'chromium-engine', use: { browserName: 'chromium' } },
    { name: 'firefox-engine', use: { browserName: 'firefox' } },
    { name: 'webkit-engine', use: { browserName: 'webkit' } },
  ],
});
