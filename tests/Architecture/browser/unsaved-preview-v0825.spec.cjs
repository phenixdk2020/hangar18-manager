const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../../assets/ultimate-designer-unsaved-preview.js');
const jqueryRuntime = require.resolve('jquery');

async function boot(page) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form">
      <div class="h18-form-header"><span class="h18-safe-switch">Safe</span></div>
      <div id="h18-page-sections-sortable">
        <section class="h18-page-section-row">
          <input class="h18-layout-parent-key" value="">
          <div class="h18-canvas-preview" id="preview-1">
            <div class="live-text">Ugemt tekst</div>
            <button class="h18-page-section-actions">Rediger</button>
            <input value="editor-control">
          </div>
        </section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ content: fs.readFileSync(runtimePath, 'utf8') });
  await page.waitForSelector('#h18-unsaved-preview-open');
}

test('unsaved preview clones the current live canvas without saving', async ({ page }) => {
  await boot(page);
  await page.locator('.live-text').evaluate(node => { node.textContent = 'Ny ugemt tekst'; });
  await page.locator('#h18-unsaved-preview-open').click();
  await expect(page.locator('#h18-unsaved-preview-modal')).toHaveClass(/is-open/);
  await expect(page.locator('[data-h18-unsaved-preview-stage]')).toContainText('Ny ugemt tekst');
  await expect(page.locator('[data-h18-unsaved-preview-stage] button')).toHaveCount(0);
  await expect(page.locator('[data-h18-unsaved-preview-stage] input')).toHaveCount(0);
});

test('preview switches desktop tablet mobile and closes with Escape', async ({ page }) => {
  await boot(page);
  await page.locator('#h18-unsaved-preview-open').click();
  const viewport = page.locator('[data-h18-unsaved-preview-viewport]');

  await page.locator('[data-h18-preview-device="tablet"]').click();
  await expect(viewport).toHaveClass(/is-tablet/);
  await page.locator('[data-h18-preview-device="mobile"]').click();
  await expect(viewport).toHaveClass(/is-mobile/);
  await page.keyboard.press('Escape');
  await expect(page.locator('#h18-unsaved-preview-modal')).not.toHaveClass(/is-open/);
});
