const { test, expect } = require('@playwright/test');

const routes = [
  { key: 'home', path: '/' },
  { key: 'about', path: '/om-foreningen/' },
  { key: 'contact', path: '/kontakt/' },
  { key: 'join', path: '/bliv-medlem/' },
  { key: 'vehicles', path: '/koeretoejer-og-materiel/' },
  { key: 'events', path: '/events/' },
  { key: 'gallery', path: '/billedgalleri/' },
];

const viewports = [
  { key: 'desktop', width: 1440, height: 1000 },
  { key: 'mobile', width: 390, height: 844 },
];

const fatalPatterns = [
  /Fatal error\s*:/i,
  /Parse error\s*:/i,
  /Uncaught Error\s*:/i,
  /There has been a critical error on this website/i,
  /Warning:\s*(?:require|include|Undefined|Trying to access|Cannot modify header)/i,
];

async function assertHealthyPublicPage(page, route, viewport, testInfo) {
  await page.setViewportSize({ width: viewport.width, height: viewport.height });

  const response = await page.goto(route.path, { waitUntil: 'domcontentloaded' });
  expect(response, `${route.path} did not return a navigation response`).not.toBeNull();
  expect(response.status(), `${route.path} returned HTTP ${response.status()}`).toBeLessThan(400);

  await page.waitForLoadState('networkidle').catch(() => {});

  const currentUrl = page.url();
  expect(currentUrl, `${route.path} unexpectedly redirected to login`).not.toMatch(/\/wp-login\.php/i);

  const title = (await page.title()).trim();
  expect(title, `${route.path} has an empty document title`).not.toBe('');

  const bodyText = await page.locator('body').innerText();
  expect(bodyText.trim().length, `${route.path} has suspiciously little body content`).toBeGreaterThan(40);
  for (const pattern of fatalPatterns) {
    expect(bodyText, `${route.path} exposes a PHP/WordPress error matching ${pattern}`).not.toMatch(pattern);
  }

  const geometry = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    bodyWidth: document.body ? document.body.scrollWidth : 0,
  }));
  const overflow = Math.max(geometry.documentWidth, geometry.bodyWidth) - geometry.clientWidth;
  expect(overflow, `${route.path} has ${overflow}px horizontal page overflow at ${viewport.key}`).toBeLessThanOrEqual(3);

  const mainCount = await page.locator('main, [role="main"], #main, .site-main').count();
  expect(mainCount, `${route.path} has no detectable main-content region`).toBeGreaterThan(0);

  const screenshotPath = testInfo.outputPath(`${route.key}-${viewport.key}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  await testInfo.attach(`${route.key}-${viewport.key}`, {
    path: screenshotPath,
    contentType: 'image/png',
  });
}

for (const route of routes) {
  for (const viewport of viewports) {
    test(`${route.key} ${viewport.key} is publicly healthy and overflow-free`, async ({ page }, testInfo) => {
      await assertHealthyPublicPage(page, route, viewport, testInfo);
    });
  }
}

test('protected-domain public routes remain separate public destinations', async ({ page }) => {
  const protectedRoutes = routes.filter((route) => ['vehicles', 'events', 'gallery'].includes(route.key));
  const resolved = [];

  for (const route of protectedRoutes) {
    const response = await page.goto(route.path, { waitUntil: 'domcontentloaded' });
    expect(response).not.toBeNull();
    expect(response.status()).toBeLessThan(400);
    resolved.push(new URL(page.url()).pathname.replace(/\/+$/, '') || '/');
  }

  expect(new Set(resolved).size, 'Vehicle/Event/Gallery unexpectedly resolve to the same public route').toBe(3);
});
