const path = require('path');

module.exports = {
  testDir: __dirname,
  testMatch: /(?:runtime|kasse-runtime|history-restore-latch-v0817|history-pending-v0818|history-preload-v0819|lego-spacing-v0830)\.spec\.cjs/,
  timeout: 15000,
  fullyParallel: false,
  workers: 1,
  reporter: [['line']],
  use: {
    headless: true,
    channel: 'chrome',
    viewport: { width: 1440, height: 1000 },
  },
  projects: [
    {
      name: 'system-chrome-editor-runtime',
      use: { channel: 'chrome' },
    },
  ],
};
