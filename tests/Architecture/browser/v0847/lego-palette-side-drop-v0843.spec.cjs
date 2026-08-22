const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const nestingRuntime = path.resolve(__dirname, '../../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../../assets/ultimate-designer-nesting-tools.css');
const parentGuardRuntime = path.resolve(__dirname, '../../../../assets/ultimate-designer-lego-parent-key-guard-v0845.js');
const inspectorOnlyRuntime = path.resolve(__dirname, '../../../../assets/ultimate-designer-lego-inspector-only-v0847.js');
const inspectorOnlyCss = path.resolve(__dirname, '../../../../assets/ultimate-designer-lego-inspector-only-v0847.css');

function row(index, key, type, label, parent = '') {
  const preview = type === 'image'
    ? '<div class="h18-canvas-editable-media" tabindex="0"><div class="base-preview">Billede</div></div>'
    : `<div class="base-preview">${label}</div>`;
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header"><span class="h18-page-section-summary">${label}</span><button type="button" class="h18-page-section-edit">Rediger</button></header>
    <div class="h18-canvas-preview">${preview}</div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <select class="h18-layout-parent-select"><option value="">Topniveau</option><option value="auto-1"${parent === 'auto-1' ? ' selected' : ''}>Auto-kasser</option></select>
      <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
      <input name="Sections[${index}][Title]" value="">
      <input name="Sections[${index}][Content]" value="">
      <input name="Sections[${index}][LayoutColumns]" value="3">
      <input name="Sections[${index}][MobileLayoutColumns]" value="1">
      <input name="Sections[${index}][LayoutGapPx]" value="16">
      <input name="Sections[${index}][MobileLayoutGapPx]" value="12">
      <input name="Sections[${index}][LayoutDirection]" value="Column">
      <input name="Sections[${index}][LayoutAlign]" value="Stretch">
    </div>
  </section>`;
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><head><style>
    .h18-builder-canvas{display:block;width:900px;min-height:600px}
    #h18-page-sections-sortable{width:820px;position:relative}
    .h18-page-section-row{display:block;width:760px;margin:12px 0;padding:8px;border:1px solid #ccc}
    .h18-canvas-preview{display:block;width:720px;min-height:120px;padding:8px;position:relative}
    .base-preview{height:90px;background:#fff}
  </style></head><body>
    <div class="h18-builder-canvas">
      <div id="h18-page-sections-sortable">
        ${row(1, 'auto-1', 'grid', 'Auto-kasser')}
        ${row(2, 'image-1', 'image', 'Billede 1', 'auto-1')}
        ${row(3, 'image-2', 'image', 'Billede 2', 'auto-1')}
        ${row(4, 'text-1', 'text', 'Overskrift', 'auto-1')}
      </div>
    </div>
    <aside id="h18-page-inspector"><div class="h18-builder-inspector-heading"><span>Vælg</span></div><div id="h18-page-inspector-target"></div></aside>
  </body></html>`);

  await page.addStyleTag({ path: nestingCss });
  await page.addStyleTag({ path: inspectorOnlyCss });
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    const $ = window.jQuery;
    window.__legacyInlineEdits = 0;

    function restoreSelected() {
      const $selected = $('#h18-page-sections-sortable > .h18-page-section-row.is-selected').first();
      const $body = $('#h18-page-inspector-target > .h18-page-section-body').first();
      if ($selected.length && $body.length) { $selected.append($body); }
      $selected.removeClass('is-selected');
    }

    function inspectRow($row) {
      restoreSelected();
      $row.addClass('is-selected');
      $('#h18-page-inspector-target').empty().append($row.children('.h18-page-section-body'));

      // Reproduce the real symptom: selection is correct, but a later base
      // canvas/Inspector repaint wipes the visual Auto-kasse children after the
      // nesting runtime's immediate refresh has already completed.
      window.setTimeout(() => {
        const grid = document.querySelector('#row-auto-1 .h18-ud-auto-box-grid');
        if (grid) grid.replaceChildren();
      }, 220);
    }

    $(document).on('click', '.h18-page-section-header', function (event) {
      if ($(event.target).closest('.h18-page-section-edit').length) return;
      inspectRow($(this).closest('.h18-page-section-row'));
    });
    $(document).on('click', '.h18-page-section-edit', function (event) {
      event.preventDefault();
      inspectRow($(this).closest('.h18-page-section-row'));
    });

    document.addEventListener('dblclick', function (event) {
      if (event.target && event.target.closest && event.target.closest('.h18-canvas-editable-media')) {
        window.__legacyInlineEdits += 1;
      }
    }, false);
  });

  await page.addScriptTag({ path: nestingRuntime });
  await page.waitForFunction(() => Boolean(window.__h18NestingToolsV0840));
  await page.addScriptTag({ path: parentGuardRuntime });
  await page.addScriptTag({ path: inspectorOnlyRuntime });

  await page.evaluate(() => window.__h18NestingToolsV0840.refresh());
  await expect(page.locator('#row-auto-1 .h18-ud-auto-box-grid .h18-v0811-auto-box')).toHaveCount(3, { timeout: 2500 });
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-inspector-only', '0.8.47');
}

test('LEGO-047 child Rediger keeps Grid composition stable while settings move to Inspector', async ({ page }) => {
  await boot(page);

  await page.locator('#row-auto-1 .h18-v0811-auto-box').nth(1).locator('.h18-v0811-edit-child').click();

  await expect(page.locator('#row-image-2')).toHaveClass(/is-selected/);
  await expect(page.locator('#h18-page-inspector-target .h18-page-section-key')).toHaveValue('image-2');

  // The deliberate late repaint happens at 220 ms. LEGO-047 must re-arm the
  // existing reconciliation and restore all three tiles without Undo/Redo.
  await page.waitForTimeout(1000);
  await expect(page.locator('#row-auto-1 .h18-ud-auto-box-grid .h18-v0811-auto-box')).toHaveCount(3);
});

test('LEGO-047 legacy media dblclick is intercepted and routed to Inspector', async ({ page }) => {
  await boot(page);

  // Auto-kasse tiles are intentionally the pointer surface in the real canvas;
  // their cloned child preview is not a separate editable hit target. Dispatch
  // the legacy event directly to verify the capture-phase Inspector guard without
  // requiring Playwright to click through the tile/resize overlay.
  await page.locator('#row-auto-1 .h18-v0811-auto-box').first().locator('.h18-canvas-editable-media').evaluate((node) => {
    node.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
  });

  await expect(page.locator('#row-image-1')).toHaveClass(/is-selected/);
  await expect(page.locator('#h18-page-inspector-target .h18-page-section-key')).toHaveValue('image-1');
  expect(await page.evaluate(() => window.__legacyInlineEdits)).toBe(0);
});
