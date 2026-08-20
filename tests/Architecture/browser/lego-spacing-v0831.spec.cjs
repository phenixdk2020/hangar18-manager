const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const legoRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.js');
const legoCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.css');

async function boot(page, storedState = null) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form">
      <input name="page_slug" value="hjem">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div id="h18-page-sections-sortable">
        <section class="h18-page-section-row is-selected" data-section-type="grid" data-section-index="1">
          <header class="h18-page-section-header">Grid</header>
          <div class="h18-canvas-preview" data-canvas-device="desktop">
            <div class="h18-ud-auto-box-grid"><span>A</span><span>B</span></div>
          </div>
          <div class="h18-page-section-body">
            <input class="h18-page-section-key" value="grid-1">
            <input class="h18-page-section-type" value="grid">
            <input name="Sections[1][LayoutGapPx]" value="16">
            <input name="Sections[1][MobileLayoutGapPx]" value="12">
          </div>
        </section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate((state) => {
    window.H18LegoSpacingV0831 = {
      version: '0.8.31', schemaVersion: 2,
      pages: state ? { hjem: { SchemaVersion: state.SchemaVersion || 1, Sections: { 'grid-1': state } } } : {},
      limits: { desktop: 160, tablet: 160, mobile: 120 }
    };
    window.__legoHiddenInputEvents = 0;
    window.jQuery('#h18-page-editor-form').on('input', '.h18-lego-spacing-state-json', function () {
      window.__legoHiddenInputEvents += 1;
    });
  }, storedState);
  await page.addStyleTag({ path: legoCss });
  await page.addScriptTag({ path: legoRuntime });
  await expect(page.locator('#h18-ud-lego-spacing-panel')).toBeVisible();
}

async function setCanvasDevice(page, device) {
  await page.locator('.h18-canvas-preview').evaluate((node, value) => node.setAttribute('data-canvas-device', value), device);
}

test('v0.8.30 Mobile state stays explicit while Tablet migrates to Desktop inheritance', async ({ page }) => {
  await boot(page, {
    SchemaVersion: 1,
    Desktop: { Margin: { X: 8, Y: 10 }, Gap: { X: 24, Y: 18 } },
    Mobile: { Margin: { X: 3, Y: 5 }, Gap: { X: 9, Y: 7 } }
  });

  const state = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(state.SchemaVersion).toBe(2);
  expect(state.Tablet.InheritDesktop).toBe(true);
  expect(state.Mobile.InheritDesktop).toBe(false);
  expect(state.Mobile.Margin).toEqual({ X: 3, Y: 5 });
  expect(state.Mobile.Gap).toEqual({ X: 9, Y: 7 });

  const tabletToggle = page.locator('[data-h18-lego-inherit-device="Tablet"]');
  const mobileToggle = page.locator('[data-h18-lego-inherit-device="Mobile"]');
  await expect(tabletToggle).toBeChecked();
  await expect(mobileToggle).not.toBeChecked();
  await expect(page.locator('[data-h18-lego-path="Tablet.Gap.X"]')).toBeDisabled();
  await expect(page.locator('[data-h18-lego-path="Tablet.Gap.X"]')).toHaveValue('24');

  await setCanvasDevice(page, 'tablet');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '24px');
  await expect(page.locator('.h18-canvas-preview')).toHaveCSS('margin-left', '8px');

  await setCanvasDevice(page, 'mobile');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '9px');
  await expect(page.locator('.h18-canvas-preview')).toHaveCSS('margin-left', '3px');
});

test('Tablet override survives inherit on/off and each toggle/edit uses canonical history event', async ({ page }) => {
  await boot(page);

  const tabletToggle = page.locator('[data-h18-lego-inherit-device="Tablet"]');
  const tabletGapX = page.locator('[data-h18-lego-path="Tablet.Gap.X"]');
  const desktopGapX = page.locator('[data-h18-lego-path="Desktop.Gap.X"]');

  await tabletToggle.uncheck();
  expect(await page.evaluate(() => window.__legoHiddenInputEvents)).toBe(1);
  await expect(tabletGapX).toBeEnabled();
  await tabletGapX.fill('29');
  expect(await page.evaluate(() => window.__legoHiddenInputEvents)).toBe(2);

  await setCanvasDevice(page, 'tablet');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '29px');

  await tabletToggle.check();
  expect(await page.evaluate(() => window.__legoHiddenInputEvents)).toBe(3);
  await expect(tabletGapX).toBeDisabled();
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '16px');

  await desktopGapX.fill('35');
  expect(await page.evaluate(() => window.__legoHiddenInputEvents)).toBe(4);
  await expect(tabletGapX).toHaveValue('35');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '35px');

  await tabletToggle.uncheck();
  expect(await page.evaluate(() => window.__legoHiddenInputEvents)).toBe(5);
  await expect(tabletGapX).toHaveValue('29');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '29px');

  const state = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(state.Desktop.Gap.X).toBe(35);
  expect(state.Tablet.InheritDesktop).toBe(false);
  expect(state.Tablet.Gap.X).toBe(29);
});

test('Mobile can inherit Desktop without deleting its previous override', async ({ page }) => {
  await boot(page, {
    SchemaVersion: 1,
    Desktop: { Margin: { X: 6, Y: 8 }, Gap: { X: 20, Y: 22 } },
    Mobile: { Margin: { X: 2, Y: 4 }, Gap: { X: 10, Y: 11 } }
  });

  const toggle = page.locator('[data-h18-lego-inherit-device="Mobile"]');
  await toggle.check();
  await setCanvasDevice(page, 'mobile');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '20px');
  await expect(page.locator('.h18-canvas-preview')).toHaveCSS('margin-left', '6px');

  let state = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(state.Mobile.InheritDesktop).toBe(true);
  expect(state.Mobile.Margin).toEqual({ X: 2, Y: 4 });
  expect(state.Mobile.Gap).toEqual({ X: 10, Y: 11 });

  await toggle.uncheck();
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '10px');
  await expect(page.locator('.h18-canvas-preview')).toHaveCSS('margin-left', '2px');
  state = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(state.Mobile.InheritDesktop).toBe(false);
  expect(state.Mobile.Gap.X).toBe(10);
});

test('history-style full sections restore rehydrates inherited Tablet and explicit Mobile preview', async ({ page }) => {
  await boot(page, {
    SchemaVersion: 1,
    Desktop: { Margin: { X: 4, Y: 6 }, Gap: { X: 16, Y: 18 } },
    Mobile: { Margin: { X: 1, Y: 2 }, Gap: { X: 8, Y: 9 } }
  });

  const initialHtml = await page.locator('#h18-page-sections-sortable').evaluate((node) => node.innerHTML);
  await page.locator('[data-h18-lego-inherit-device="Tablet"]').uncheck();
  await page.locator('[data-h18-lego-path="Tablet.Gap.X"]').fill('44');
  await setCanvasDevice(page, 'tablet');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '44px');

  await page.locator('#h18-page-sections-sortable').evaluate((node, html) => { node.innerHTML = html; }, initialHtml);

  await expect.poll(async () => {
    return page.locator('.h18-page-section-row').evaluate((row) => row.style.getPropertyValue('--h18-lego-tablet-gap-x'));
  }).toBe('16px');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '16px');

  await setCanvasDevice(page, 'mobile');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '8px');
  const state = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(state.Tablet.InheritDesktop).toBe(true);
  expect(state.Mobile.InheritDesktop).toBe(false);
});
