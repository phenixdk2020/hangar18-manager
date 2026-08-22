const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const dropRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.js');
const dropCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.css');
const paletteBridgeRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js');
const historyAtomicRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-history-atomic-v0840.js');

function row(index, key, type, label, parent = '', extraClass = '') {
  return `<section id="row-${key}" class="h18-page-section-row ${extraClass}" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header">${label}</header>
    <div class="h18-canvas-preview"><div class="base-preview">${label}</div></div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
    </div>
  </section>`;
}

async function bootUnderDrop(page) {
  await page.setContent(`<!doctype html><html><head><style>
    .h18-builder-canvas{display:block;width:900px;min-height:700px}
    #h18-page-sections-sortable{width:820px;position:relative}
    .h18-page-section-row{display:block;width:760px;margin:12px 0;padding:8px;border:1px solid #ccc}
    .h18-page-section-row.is-nested-source{display:none}
    .h18-canvas-preview{display:block;width:720px;height:180px;padding:8px;position:relative}
    .base-preview{height:145px;background:#fff}
  </style></head><body>
    <button id="text-palette" type="button" draggable="true" class="h18-builder-palette-item" data-section-type="text">Tekst</button>
    <div class="h18-builder-canvas">
      <div id="h18-page-sections-sortable">
        ${row(1, 'auto-1', 'grid', 'Auto-kasser')}
        ${row(2, 'child-1', 'text', 'Venstre', 'auto-1', 'is-nested-source')}
        ${row(3, 'child-2', 'image', 'Højre', 'auto-1', 'is-nested-source')}
        ${row(4, 'next-1', 'text', 'Næste topniveau')}
      </div>
    </div>
    <aside id="h18-page-inspector"><div id="h18-page-inspector-target"></div></aside>
  </body></html>`);

  await page.addStyleTag({ path: dropCss });
  await page.addScriptTag({ path: jqueryRuntime });

  // Mirror the real legacy/base palette creator: every canvas drop accepts only
  // a "$before" row. This is exactly why an Under zone used to insert above its
  // target before the LEGO-046 translation bridge.
  await page.evaluate(() => {
    const $ = window.jQuery;
    let draggedPaletteType = '';
    let serial = 0;

    $(document).on('dragstart', '.h18-builder-palette-item', function () {
      draggedPaletteType = String($(this).data('section-type') || 'text');
    });
    $(document).on('dragend', '.h18-builder-palette-item', function () {
      draggedPaletteType = '';
    });

    $('.h18-builder-canvas').on('dragover', function (event) {
      if (draggedPaletteType) event.preventDefault();
    }).on('drop', function (event) {
      if (!draggedPaletteType) return;
      event.preventDefault();
      serial += 1;
      const key = `new-${serial}`;
      const $new = $(`<section id="row-${key}" class="h18-page-section-row" data-section-type="text" data-section-index="${10 + serial}">
        <header class="h18-page-section-header">Ny tekst</header>
        <div class="h18-canvas-preview"><div class="base-preview">Ny tekst</div></div>
        <div class="h18-page-section-body">
          <input class="h18-page-section-key" value="${key}">
          <input class="h18-page-section-type" value="text">
          <input class="h18-section-navigator-label" value="Tekst">
          <input class="h18-layout-parent-key" value="">
          <input class="h18-page-section-order" value="${(10 + serial) * 10}">
        </div>
      </section>`);
      const $before = $(event.target).closest('.h18-page-section-row');
      if ($before.length) $before.before($new); else $('#h18-page-sections-sortable').append($new);
    });
  });

  await page.addScriptTag({ path: dropRuntime });
  await page.addScriptTag({ path: paletteBridgeRuntime });

  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-palette-vertical-drop-bridge', '0.8.46');
}

test('LEGO-046 palette Under inserts after the complete target group, not above it', async ({ page }) => {
  await bootUnderDrop(page);

  await page.evaluate(() => {
    document.getElementById('text-palette').dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true }));
  });

  const under = page.locator('#row-auto-1 > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="under"]');
  await expect(under).toBeVisible({ timeout: 2500 });
  const rect = await under.boundingBox();
  if (!rect) throw new Error('Under zone has no geometry');

  await page.evaluate(({ x, y }) => {
    const preview = document.querySelector('#row-auto-1 > .h18-canvas-preview');
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

  const state = await page.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row'));
    return {
      keys: rows.map((node) => node.querySelector('.h18-page-section-key')?.value || ''),
      newParent: document.querySelector('#row-new-1 .h18-layout-parent-key')?.value || ''
    };
  });

  // Nested source rows stay contiguous with Auto-kasser; the new top-level row
  // belongs between the complete Auto-kasse group and the next top-level row.
  expect(state.keys).toEqual(['auto-1', 'child-1', 'child-2', 'new-1', 'next-1']);
  expect(state.newParent).toBe('');
});

async function bootRapidHistory(page) {
  await page.setContent(`<!doctype html><html><body>
    <button id="text-palette" type="button" draggable="true" class="h18-builder-palette-item" data-section-type="text">Tekst</button>
    <div class="h18-builder-canvas"><div id="h18-page-sections-sortable">
      ${row(1, 'initial-1', 'text', 'Start')}
    </div></div>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    window.__h18HistoryCoreBridgeV0821 = { flushPending() {} };
  });
  await page.addScriptTag({ path: historyAtomicRuntime });
  await page.waitForFunction(() => Boolean(window.__h18HistoryAtomicV0840));

  await page.evaluate(() => {
    const sections = document.getElementById('h18-page-sections-sortable');
    const entries = [];

    function keys() {
      return Array.from(sections.querySelectorAll(':scope > .h18-page-section-row')).map((node) => node.querySelector('.h18-page-section-key')?.value || '');
    }

    function editorHistoryRecordNow() {
      const state = JSON.stringify(keys());
      if (entries.length && entries[entries.length - 1] === state) return;
      entries.push(state);
    }

    function scheduleEditorHistoryCapture() {
      window.setTimeout(editorHistoryRecordNow, 0);
    }

    function addRow(key, index) {
      sections.insertAdjacentHTML('beforeend', `<section class="h18-page-section-row" data-section-type="text" data-section-index="${index}">
        <div class="h18-canvas-preview"></div><div class="h18-page-section-body">
          <input class="h18-page-section-key" value="${key}">
          <input class="h18-layout-parent-key" value="">
          <input class="h18-page-section-order" value="${index * 10}">
        </div></section>`);
    }

    editorHistoryRecordNow();
    window.__v0846HistoryHarness = {
      schedule: scheduleEditorHistoryCapture,
      addRow,
      entries() { return entries.map((entry) => JSON.parse(entry)); }
    };
  });

  await expect(page.locator('html')).toHaveAttribute('data-h18-v0846-history-gesture-boundary', '1');
}

async function rapidPaletteGesture(page, key, index) {
  await page.evaluate(({ key, index }) => {
    const palette = document.getElementById('text-palette');
    const sections = document.getElementById('h18-page-sections-sortable');
    palette.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true }));
    sections.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true }));
    window.__v0846HistoryHarness.addRow(key, index);
    window.__v0846HistoryHarness.schedule();
    palette.dispatchEvent(new DragEvent('dragend', { bubbles: true }));
  }, { key, index });
}

test('LEGO-046 two rapid palette gestures remain two Undo checkpoints', async ({ page }) => {
  await bootRapidHistory(page);

  await rapidPaletteGesture(page, 'first-drop', 2);
  // Intentionally start the next user gesture well inside the historical 520 ms
  // settle window. Old behavior merged both drops into one Undo transaction.
  await page.waitForTimeout(80);
  await rapidPaletteGesture(page, 'second-drop', 3);
  await page.waitForTimeout(700);

  const entries = await page.evaluate(() => window.__v0846HistoryHarness.entries());
  expect(entries).toEqual([
    ['initial-1'],
    ['initial-1', 'first-drop'],
    ['initial-1', 'first-drop', 'second-drop']
  ]);
});
