const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const runtime = path.resolve(__dirname, '../../../assets/ultimate-designer-canvas-panel-collapse-v0839.js');
const css = path.resolve(__dirname, '../../../assets/ultimate-designer-canvas-panel-collapse-v0839.css');

async function boot(page) {
  await page.goto('about:blank');
  await page.evaluate(() => localStorage.clear());
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form">
      <div id="h18-page-sections-sortable">
        <section class="h18-page-section-row is-selected" data-section-type="text_image">
          <div class="h18-canvas-preview">
            <div class="h18-canvas-direct-controls">
              <strong class="h18-canvas-direct-title">Direkte design · LEGO</strong>
              <div class="h18-canvas-quick-ranges"><label>Indvendig <input type="range" value="0"></label></div>
              <div class="h18-canvas-quick-colors">Farver</div>
            </div>
            <div class="h18-canvas-editable-media">
              <div class="h18-canvas-image-tools">
                <strong>Billede</strong>
                <div class="h18-canvas-image-actions"><button type="button">Skift billede</button></div>
                <label>Fokus X <input type="range" value="50"></label>
              </div>
            </div>
          </div>
        </section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(() => {
    window.__panelFormEvents = 0;
    window.jQuery('#h18-page-editor-form').on('input change', () => { window.__panelFormEvents += 1; });
  });
  await page.addStyleTag({ path: css });
  await page.addScriptTag({ path: runtime });
  await expect(page.locator('html')).toHaveAttribute('data-h18-canvas-panel-collapse-runtime', '0.8.39');
}

test('image and Direkte Design panels minimize independently without editor/history events', async ({ page }) => {
  await boot(page);

  const direct = page.locator('.h18-canvas-direct-controls');
  const image = page.locator('.h18-canvas-image-tools');
  await expect(direct.locator(':scope > .h18-canvas-panel-collapse-toggle')).toHaveCount(1);
  await expect(image.locator(':scope > .h18-canvas-panel-collapse-toggle')).toHaveCount(1);

  await image.locator(':scope > .h18-canvas-panel-collapse-toggle').click();
  await expect(image).toHaveAttribute('data-h18-canvas-panel-collapsed', '1');
  await expect(image.locator(':scope > .h18-canvas-panel-collapse-toggle')).toHaveAttribute('aria-expanded', 'false');
  await expect(image.locator('.h18-canvas-image-actions')).toBeHidden();
  await expect(direct).toHaveAttribute('data-h18-canvas-panel-collapsed', '0');

  await direct.locator(':scope > .h18-canvas-panel-collapse-toggle').click();
  await expect(direct).toHaveAttribute('data-h18-canvas-panel-collapsed', '1');
  await expect(direct.locator('.h18-canvas-quick-ranges')).toBeHidden();
  await expect(direct.locator('.h18-canvas-direct-title')).toBeVisible();
  expect(await page.evaluate(() => window.__panelFormEvents)).toBe(0);

  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('hangar18CanvasPanelCollapseV0839')));
  expect(stored).toEqual({ image: true, direct: true });
});

test('collapsed state survives dynamic canvas panel rerender', async ({ page }) => {
  await boot(page);
  const image = page.locator('.h18-canvas-image-tools');
  await image.locator(':scope > .h18-canvas-panel-collapse-toggle').click();
  await expect(image).toHaveAttribute('data-h18-canvas-panel-collapsed', '1');

  await page.locator('.h18-canvas-editable-media').evaluate((media) => {
    media.innerHTML = '<div class="h18-canvas-image-tools"><strong>Billede</strong><div class="h18-canvas-image-actions"><button type="button">Skift billede</button></div><label>Fokus Y <input type="range" value="50"></label></div>';
  });

  const rerendered = page.locator('.h18-canvas-image-tools');
  await expect(rerendered.locator(':scope > .h18-canvas-panel-collapse-toggle')).toHaveCount(1);
  await expect(rerendered).toHaveAttribute('data-h18-canvas-panel-collapsed', '1');
  await expect(rerendered.locator('.h18-canvas-image-actions')).toBeHidden();

  await rerendered.locator(':scope > .h18-canvas-panel-collapse-toggle').click();
  await expect(rerendered).toHaveAttribute('data-h18-canvas-panel-collapsed', '0');
  await expect(rerendered.locator('.h18-canvas-image-actions')).toBeVisible();
  expect(await page.evaluate(() => window.__panelFormEvents)).toBe(0);
});
