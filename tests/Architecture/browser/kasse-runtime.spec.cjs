const { test, expect } = require('@playwright/test');
const path = require('path');

const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const jqueryRuntime = require.resolve('jquery');

async function dropExistingBoxDirectlyOnAutoCanvas(page, boxKey) {
  await page.evaluate(async (key) => {
    const $ = window.jQuery;
    const $sections = $('#h18-page-sections-sortable');
    const $row = $sections.children('.h18-page-section-row').filter(function () {
      return String($(this).find('.h18-page-section-key').first().val() || '') === key;
    }).first();

    $sections.trigger('sortstart', [{ item: $row }]);
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

    const preview = document.querySelector('.h18-page-section-row[data-section-type="grid"] > .h18-canvas-preview');
    const zone = document.querySelector('.h18-v0814-auto-drop-zone[data-h18-v0814-auto-drop="auto-1"]');
    if (!preview || !zone) { throw new Error('Auto-kasser canvas/drop-zone is missing before sortable move'); }

    const previewRect = preview.getBoundingClientRect();
    const zoneRect = zone.getBoundingClientRect();

    // The production CSS must expand the zone across the complete Auto-kasser
    // canvas while a Kasse is dragged. This specifically avoids the old test
    // shortcut that dropped in the small footer zone.
    if (zoneRect.top > previewRect.top + 2 || zoneRect.bottom < previewRect.bottom - 2) {
      throw new Error('Auto-kasser direct-drop hit area does not cover the full canvas');
    }

    const pageX = previewRect.left + Math.min(40, previewRect.width / 4) + window.pageXOffset;
    const pageY = previewRect.top + 12 + window.pageYOffset;

    $sections.trigger($.Event('sort', { pageX, pageY }));
    if (!$sections.children('.h18-page-section-row[data-section-type="grid"]').hasClass('h18-v0814-auto-drop-target')) {
      throw new Error('Direct Auto-kasser canvas did not become the active drop target');
    }
    $sections.trigger('sortstop');

    await new Promise((resolve) => window.setTimeout(resolve, 240));
  }, boxKey);
}

test('two existing Kasser stay visible when dropped directly on Auto-kasser canvas', async ({ page }) => {
  await page.setContent(`<!doctype html><html><head><style>
    #h18-page-sections-sortable{width:760px}
    .h18-page-section-row{display:block;width:720px;margin:8px 0;padding:8px;border:1px solid #ccc}
    .h18-canvas-preview{display:block;width:680px;min-height:150px;padding:8px}
    .base-preview{height:60px}
  </style></head><body>
    <div class="h18-builder-canvas"></div>
    <div id="h18-page-inspector-target"></div>
    <div id="h18-page-sections-sortable">
      <section class="h18-page-section-row" data-section-type="grid" data-section-index="1">
        <input class="h18-page-section-key" value="auto-1">
        <input class="h18-section-navigator-label" value="Auto-kasser">
        <input class="h18-layout-parent-key" value="">
        <input class="h18-page-section-order" value="10">
        <input name="Sections[1][LayoutColumns]" value="1">
        <input name="Sections[1][LayoutGapPx]" value="16">
        <div class="h18-canvas-preview"><div class="base-preview">Auto base</div></div>
      </section>
      <section class="h18-page-section-row" data-section-type="container" data-section-index="2">
        <input class="h18-page-section-key" value="box-1">
        <input class="h18-section-navigator-label" value="Kasse">
        <input class="h18-layout-parent-key" value="">
        <input class="h18-page-section-order" value="20">
        <div class="h18-canvas-preview"><div class="base-preview">Kasse A</div></div>
      </section>
      <section class="h18-page-section-row" data-section-type="container" data-section-index="3">
        <input class="h18-page-section-key" value="box-2">
        <input class="h18-section-navigator-label" value="Kasse">
        <input class="h18-layout-parent-key" value="">
        <input class="h18-page-section-order" value="30">
        <div class="h18-canvas-preview"><div class="base-preview">Kasse B</div></div>
      </section>
    </div>
  </body></html>`);

  await page.addStyleTag({ path: nestingCss });
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ path: nestingRuntime });

  const autoRow = page.locator('.h18-page-section-row[data-section-type="grid"]');
  await expect(autoRow.locator('.h18-v0814-auto-drop-zone')).toHaveCount(1, { timeout: 2000 });
  await expect(autoRow.locator('.h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(0);

  await dropExistingBoxDirectlyOnAutoCanvas(page, 'box-1');
  await expect(page.locator('.h18-page-section-row[data-section-index="2"] .h18-layout-parent-key')).toHaveValue('auto-1');
  await expect(autoRow.locator('.h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(1, { timeout: 2000 });
  await expect(page.locator('.h18-page-section-row[data-section-index="2"]')).toBeHidden();

  await dropExistingBoxDirectlyOnAutoCanvas(page, 'box-2');
  await expect(page.locator('.h18-page-section-row[data-section-index="3"] .h18-layout-parent-key')).toHaveValue('auto-1');
  await expect(autoRow.locator('.h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 2000 });
  await expect(page.locator('.h18-page-section-row[data-section-index="3"]')).toBeHidden();
  await expect(autoRow.locator('.h18-v0811-runtime-badge').first()).toHaveText('v0.8.15');

  await autoRow.locator(':scope > .h18-canvas-preview').evaluate((preview) => {
    preview.innerHTML = '<div class="base-preview">Base editor rebuilt this preview</div>';
  });
  await expect(autoRow.locator('.h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 2000 });
});
