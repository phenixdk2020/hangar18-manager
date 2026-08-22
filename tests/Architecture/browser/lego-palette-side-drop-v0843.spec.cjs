const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const dropRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.js');
const dropCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.css');
const parentGuardRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-parent-key-guard-v0845.js');
const bridgeRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js');

function row(index, key, type, label, parent = '') {
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header">${label}</header>
    <div class="h18-canvas-preview"><div class="base-preview">${label}</div></div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <select class="h18-layout-parent-select"><option value="">Topniveau på siden</option></select>
      <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
      <input name="Sections[${index}][Title]" value="">
      <input name="Sections[${index}][Content]" value="">
      <input name="Sections[${index}][LayoutColumns]" value="1">
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
    .h18-canvas-preview{display:block;width:720px;height:180px;padding:8px;position:relative}
    .base-preview{height:145px;background:#fff}
  </style></head><body>
    <button id="text-palette" type="button" draggable="true" class="h18-builder-palette-item" data-section-type="text">Tekst</button>
    <button id="grid-palette" type="button" class="h18-builder-palette-item" data-section-type="grid">Grid container</button>
    <div class="h18-builder-canvas">
      <div id="h18-page-sections-sortable">
        ${row(1, 'target-1', 'text_image', 'Tekst og billede')}
      </div>
    </div>
    <aside id="h18-page-inspector"><div id="h18-page-inspector-target"></div></aside>
  </body></html>`);

  await page.addStyleTag({ path: nestingCss });
  await page.addStyleTag({ path: dropCss });
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    const $ = window.jQuery;
    let gridSerial = 0;
    let elementSerial = 0;

    function appendRow(index, key, type, label) {
      $('#h18-page-sections-sortable').append(`<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
        <header class="h18-page-section-header">${label}</header>
        <div class="h18-canvas-preview"><div class="base-preview">${label}</div></div>
        <div class="h18-page-section-body">
          <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
          <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
          <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
          <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="">
          <select class="h18-layout-parent-select"><option value="">Topniveau på siden</option></select>
          <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
          <input name="Sections[${index}][Title]" value=""><input name="Sections[${index}][Content]" value="">
          <input name="Sections[${index}][LayoutColumns]" value="1"><input name="Sections[${index}][MobileLayoutColumns]" value="1">
          <input name="Sections[${index}][LayoutGapPx]" value="16"><input name="Sections[${index}][MobileLayoutGapPx]" value="12">
          <input name="Sections[${index}][LayoutDirection]" value="Column"><input name="Sections[${index}][LayoutAlign]" value="Stretch">
        </div></section>`);
    }

    $('#grid-palette').on('click', function () {
      gridSerial += 1;
      appendRow(20 + gridSerial, `auto-${gridSerial}`, 'grid', 'Grid container');
    });

    // Mirror the real WordPress editor contract that exposed the manual bug:
    // the human-facing select writes its current value back to LayoutParentKey.
    // A select without the just-created parent option therefore used to erase
    // the canonical hidden key when nesting-tools called .val(newKey).change().
    $(document).on('change', '.h18-layout-parent-select', function () {
      const $row = $(this).closest('.h18-page-section-row');
      if (!$row.length) return;
      $row.find('.h18-layout-parent-key').first()
        .val(String($(this).val() || ''))
        .trigger('change');
    });

    // This represents the existing palette creator: the new section is created
    // by the normal palette path after the accepted drop. nesting-tools then
    // discovers it from its pre-drag key snapshot and owns placement.
    document.addEventListener('drop', function (event) {
      const zone = event.target && event.target.closest ? event.target.closest('.h18-v0811-side-zone') : null;
      if (!zone || document.getElementById('row-text-new')) return;
      elementSerial += 1;
      appendRow(10 + elementSerial, 'text-new', 'text', 'Tekst');
    }, false);
  });

  await page.addScriptTag({ path: nestingRuntime });
  await page.addScriptTag({ path: parentGuardRuntime });
  await page.addScriptTag({ path: dropRuntime });
  await page.addScriptTag({ path: bridgeRuntime });

  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-parent-key-guard', '0.8.45');
}

test('palette Tekst dropped at visual left zone survives WordPress select-to-hidden parent synchronization', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => {
    const palette = document.getElementById('text-palette');
    palette.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true }));
  });

  const zone = page.locator('#row-target-1 > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="left"]');
  await expect(zone).toBeVisible({ timeout: 2500 });
  const rect = await zone.boundingBox();
  if (!rect) throw new Error('Left side zone has no geometry');

  // Reproduce both real-world layers: coordinates hit the visible left zone,
  // while native HTML5 target remains the preview; after bridge retargeting the
  // real WordPress parent select writes back to the hidden LayoutParentKey.
  await page.evaluate(({ x, y }) => {
    const preview = document.querySelector('#row-target-1 > .h18-canvas-preview');
    preview.dispatchEvent(new DragEvent('dragover', {
      bubbles: true,
      cancelable: true,
      clientX: x,
      clientY: y
    }));
    preview.dispatchEvent(new DragEvent('drop', {
      bubbles: true,
      cancelable: true,
      clientX: x,
      clientY: y
    }));
    document.getElementById('text-palette').dispatchEvent(new DragEvent('dragend', { bubbles: true }));
  }, { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });

  await page.waitForTimeout(650);

  const state = await page.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row'));
    const byKey = Object.fromEntries(rows.map((row) => [
      row.querySelector('.h18-page-section-key')?.value || '',
      {
        parent: row.querySelector('.h18-layout-parent-key')?.value || '',
        selectedParent: row.querySelector('.h18-layout-parent-select')?.value || '',
        label: row.querySelector('.h18-section-navigator-label')?.value || '',
        type: row.getAttribute('data-section-type') || ''
      }
    ]));
    return {
      keys: rows.map((row) => row.querySelector('.h18-page-section-key')?.value || ''),
      byKey,
      tiles: document.querySelectorAll('.h18-ud-auto-box-grid .h18-v0811-auto-box').length,
      orphanGridContainers: rows.filter((row) => {
        const type = row.getAttribute('data-section-type') || '';
        if (type !== 'grid') return false;
        const key = row.querySelector('.h18-page-section-key')?.value || '';
        const children = rows.filter((candidate) => (candidate.querySelector('.h18-layout-parent-key')?.value || '') === key);
        return children.length === 0;
      }).length
    };
  });

  expect(state.keys).toEqual(['auto-1', 'text-new', 'target-1']);
  expect(state.byKey['auto-1'].label).toBe('Auto-kasser');
  expect(state.byKey['text-new'].parent).toBe('auto-1');
  expect(state.byKey['target-1'].parent).toBe('auto-1');
  expect(state.byKey['text-new'].selectedParent).toBe('auto-1');
  expect(state.byKey['target-1'].selectedParent).toBe('auto-1');
  expect(state.tiles).toBe(2);
  expect(state.orphanGridContainers).toBe(0);
});
