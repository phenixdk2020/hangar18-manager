const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const legoRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0830.js');
const legoCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0830.css');

async function boot(page) {
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
  await page.evaluate(() => {
    window.H18LegoSpacingV0830 = {
      version: '0.8.30', schemaVersion: 1,
      pages: {}, limits: { desktop: 160, mobile: 120 }
    };
    window.__legoHiddenInputEvents = 0;
    document.getElementById('h18-page-editor-form').addEventListener('input', (event) => {
      if (event.target.classList && event.target.classList.contains('h18-lego-spacing-state-json')) {
        window.__legoHiddenInputEvents += 1;
      }
    });
  });
  await page.addStyleTag({ path: legoCss });
  await page.addScriptTag({ path: legoRuntime });
  await expect(page.locator('#h18-ud-lego-spacing-panel')).toBeVisible();
}

test('legacy LayoutGap seeds independent X/Y and one Inspector edit emits one canonical history event', async ({ page }) => {
  await boot(page);

  const state = await page.locator('.h18-lego-spacing-state-json').inputValue();
  const parsed = JSON.parse(state);
  expect(parsed.Desktop.Gap).toEqual({ X: 16, Y: 16 });
  expect(parsed.Mobile.Gap).toEqual({ X: 12, Y: 12 });
  expect(parsed.Desktop.Margin).toEqual({ X: 0, Y: 0 });

  const gapX = page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Desktop.Gap.X"]');
  const gapY = page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Desktop.Gap.Y"]');
  await expect(gapX).toHaveValue('16');
  await expect(gapY).toHaveValue('16');
  await gapX.fill('31');

  const changed = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(changed.Desktop.Gap).toEqual({ X: 31, Y: 16 });
  expect(await page.evaluate(() => window.__legoHiddenInputEvents)).toBe(1);
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '31px');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('row-gap', '16px');
});

test('element margin X/Y stays independent and mobile preview uses mobile variables', async ({ page }) => {
  await boot(page);

  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Desktop.Margin.X"]').fill('9');
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Desktop.Margin.Y"]').fill('21');
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Mobile.Margin.X"]').fill('5');
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Mobile.Margin.Y"]').fill('13');

  const state = JSON.parse(await page.locator('.h18-lego-spacing-state-json').inputValue());
  expect(state.Desktop.Margin).toEqual({ X: 9, Y: 21 });
  expect(state.Mobile.Margin).toEqual({ X: 5, Y: 13 });

  await page.locator('.h18-canvas-preview').evaluate((node) => node.setAttribute('data-canvas-device', 'mobile'));
  await expect(page.locator('.h18-canvas-preview')).toHaveCSS('margin-left', '5px');
  await expect(page.locator('.h18-canvas-preview')).toHaveCSS('margin-top', '13px');
});

test('history-style DOM restore rehydrates visual state from the canonical hidden field', async ({ page }) => {
  await boot(page);

  const initialBodyHtml = await page.locator('.h18-page-section-body').evaluate((node) => node.outerHTML);
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Desktop.Gap.X"]').fill('44');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '44px');

  await page.locator('.h18-page-section-body').evaluate((node, html) => {
    node.outerHTML = html;
  }, initialBodyHtml);

  await expect.poll(async () => {
    return page.locator('.h18-page-section-row').evaluate((row) => row.style.getPropertyValue('--h18-lego-gap-x'));
  }).toBe('16px');
  await expect(page.locator('.h18-ud-auto-box-grid')).toHaveCSS('column-gap', '16px');
});
