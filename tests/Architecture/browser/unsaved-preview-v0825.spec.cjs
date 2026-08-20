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
        <section class="h18-page-section-row is-selected">
          <input class="h18-layout-parent-key" value="">
          <div class="h18-canvas-preview is-direct-dragging" id="preview-1" tabindex="0" role="button" title="Editor preview">
            <div class="live-text">Ugemt tekst</div>
            <div class="h18-canvas-editable-media is-focal-dragging" tabindex="0" role="button" title="Klik for billedkontroller">
              <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==" alt="">
              <div class="h18-canvas-image-tools"><strong>Billede</strong><label>Fokus X<input type="range"></label></div>
              <button class="h18-canvas-focal-dot">Fokus</button>
            </div>
            <div class="h18-canvas-direct-controls"><strong>DIREKTE DESIGN</strong><label>Indvendig<input type="range"></label></div>
            <div class="h18-canvas-box-model-overlay"><span class="is-padding">P 0 / 0</span></div>
            <button class="h18-canvas-padding-handle">P</button>
            <button class="h18-canvas-margin-handle">M</button>
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

test('selected image editor chrome is stripped from unsaved preview', async ({ page }) => {
  await boot(page);
  await page.locator('#h18-unsaved-preview-open').click();
  const stage = page.locator('[data-h18-unsaved-preview-stage]');

  await expect(stage.locator('.h18-canvas-image-tools')).toHaveCount(0);
  await expect(stage.locator('.h18-canvas-direct-controls')).toHaveCount(0);
  await expect(stage.locator('.h18-canvas-box-model-overlay')).toHaveCount(0);
  await expect(stage.locator('.h18-canvas-padding-handle')).toHaveCount(0);
  await expect(stage.locator('.h18-canvas-margin-handle')).toHaveCount(0);
  await expect(stage.locator('.h18-canvas-focal-dot')).toHaveCount(0);
  await expect(stage).not.toContainText('DIREKTE DESIGN');
  await expect(stage).not.toContainText('Fokus X');
  await expect(stage).not.toContainText('P 0 / 0');

  const media = stage.locator('.h18-canvas-editable-media');
  await expect(media).not.toHaveAttribute('tabindex');
  await expect(media).not.toHaveAttribute('role');
  await expect(media).not.toHaveAttribute('title');
  await expect(media).not.toHaveClass(/is-focal-dragging/);
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
