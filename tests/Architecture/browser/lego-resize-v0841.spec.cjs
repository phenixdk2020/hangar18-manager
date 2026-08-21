const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const historyBridge = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0821.js');
const historyAtomic = path.resolve(__dirname, '../../../assets/ultimate-designer-history-atomic-v0840.js');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const resizeRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-resize-v0841.js');
const resizeCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-resize-v0841.css');

function row(index, key, type, label, parent = '') {
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header">${label}</header>
    <div class="h18-canvas-preview"><div class="base-preview">${key}</div></div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <select class="h18-layout-parent-select"><option value=""></option><option value="auto-1"${parent === 'auto-1' ? ' selected' : ''}>auto-1</option></select>
      <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
      <input name="Sections[${index}][Title]" value="">
      <input name="Sections[${index}][Content]" value="">
      <input name="Sections[${index}][LayoutColumns]" value="2">
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
    body{margin:20px}#h18-page-editor-form{display:block}.h18-builder-canvas{display:block;width:900px;min-height:450px}
    #h18-page-sections-sortable{width:860px;position:relative}.h18-page-section-row{display:block;width:820px;margin:12px 0;padding:8px;border:1px solid #ccc}
    .h18-canvas-preview{display:block;width:780px;min-height:160px;padding:8px;position:relative}.base-preview{height:80px}
  </style></head><body>
    <form id="h18-page-editor-form">
      <input name="page_slug" value="hjem">
      <button id="h18-editor-undo" type="button">Fortryd</button>
      <button id="h18-editor-redo" type="button">Gendan</button>
      <span id="h18-editor-history-status">Ingen ugemte ændringer</span>
      <div class="h18-builder-canvas" data-canvas-device="desktop">
        <div id="h18-page-sections-sortable">
          ${row(1, 'auto-1', 'grid', 'Auto-kasser')}
          ${row(2, 'text-1', 'text', 'Tekst', 'auto-1')}
          ${row(3, 'image-1', 'image', 'Billede', 'auto-1')}
        </div>
      </div>
      <aside id="h18-page-inspector"><div id="h18-page-inspector-target"></div></aside>
    </form>
  </body></html>`);

  await page.addStyleTag({ path: nestingCss });
  await page.addStyleTag({ path: resizeCss });
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ path: historyBridge });
  await page.addScriptTag({ path: historyAtomic });
  await page.evaluate(() => {
    window.H18LegoResizeV0841 = { version: '0.8.41', schemaVersion: 1, columns: 12, pages: {} };
  });
  await page.addScriptTag({ path: nestingRuntime });
  await page.addScriptTag({ path: resizeRuntime });

  await page.waitForFunction(() => Boolean(window.__h18LegoResizeV0841 && window.__h18HistoryAtomicV0840));
  await expect(page.locator('.h18-v0841-resize-grid')).toHaveCount(1, { timeout: 2500 });

  await page.evaluate(() => {
    const $ = window.jQuery;
    const sections = document.getElementById('h18-page-sections-sortable');
    const entries = [];
    let index = -1;
    let editorHistoryTimer = null;
    let applying = false;

    function canonicalHtml() {
      const clone = $(sections).clone(false, false).get(0);
      clone.querySelectorAll('.h18-ud-auto-box-grid,.h18-v0814-auto-drop-zone,.h18-v0811-side-zones,.h18-ud-box-contents-preview').forEach((node) => node.remove());
      clone.querySelectorAll('.is-selected').forEach((node) => node.classList.remove('is-selected'));
      clone.querySelectorAll('input').forEach((input) => input.setAttribute('value', String(input.value == null ? '' : input.value)));
      return clone.innerHTML;
    }

    function editorHistoryRecordNow() {
      if (applying) return;
      const html = canonicalHtml();
      if (index >= 0 && entries[index] === html) return;
      if (index < entries.length - 1) entries.splice(index + 1);
      entries.push(html);
      index = entries.length - 1;
    }

    function scheduleEditorHistoryCapture(delay) {
      window.clearTimeout(editorHistoryTimer);
      editorHistoryTimer = window.setTimeout(editorHistoryRecordNow, typeof delay === 'number' ? delay : 280);
    }
    function flushPending() {
      if (!editorHistoryTimer) return;
      window.clearTimeout(editorHistoryTimer);
      editorHistoryTimer = null;
      editorHistoryRecordNow();
    }
    function restore(html) {
      applying = true;
      sections.innerHTML = html;
      window.setTimeout(() => {
        applying = false;
        if (window.__h18LegoResizeV0841) window.__h18LegoResizeV0841.refresh();
      }, 0);
    }
    function undo() { flushPending(); if (index <= 0) return; index -= 1; restore(entries[index]); }
    function redo() { flushPending(); if (index < 0 || index >= entries.length - 1) return; index += 1; restore(entries[index]); }

    $('#h18-page-editor-form').on('input change', '.h18-page-section-body :input', function () {
      if (!applying) scheduleEditorHistoryCapture(280);
    });
    document.getElementById('h18-editor-undo').addEventListener('click', undo);
    document.getElementById('h18-editor-redo').addEventListener('click', redo);
    editorHistoryRecordNow();

    window.__v0841HistoryHarness = {
      state() { return { index, entries: entries.length }; },
      spans() { return window.__h18LegoResizeV0841.effectiveForAuto('auto-1'); },
      stored() {
        return ['text-1','image-1'].map((key) => window.__h18LegoResizeV0841.stateForKey(key).Desktop.Span);
      }
    };
  });
}

async function resizeFirstBoundaryByColumns(page, deltaColumns) {
  const handle = page.locator('.h18-v0841-resize-handle').first();
  const grid = page.locator('.h18-v0841-resize-grid');
  const handleBox = await handle.boundingBox();
  const gridBox = await grid.boundingBox();
  if (!handleBox || !gridBox) throw new Error('Resize geometry unavailable');
  const gap = await grid.evaluate((node) => parseFloat(getComputedStyle(node).columnGap || getComputedStyle(node).gap || '0') || 0);
  const step = (gridBox.width + gap) / 12;
  const x = handleBox.x + handleBox.width / 2;
  const y = handleBox.y + handleBox.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x + step * deltaColumns, y, { steps: 8 });
  await page.mouse.up();
}

test('LEGO-032 two Auto-kasser children default to 6/6 without persisted mutation', async ({ page }) => {
  await boot(page);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.spans())).toEqual([6, 6]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.stored())).toEqual([0, 0]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.state())).toEqual({ index: 0, entries: 1 });
  await expect(page.locator('.h18-v0841-resize-tile').nth(0)).toHaveAttribute('data-h18-v0841-effective-span', '6');
  await expect(page.locator('.h18-v0841-resize-tile').nth(1)).toHaveAttribute('data-h18-v0841-effective-span', '6');
});

test('LEGO-032 decoration settles and does not recreate handles on its own observer', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => {
    const grid = document.querySelector('.h18-v0841-resize-grid');
    window.__v0841DecorationMutations = 0;
    const observer = new MutationObserver((mutations) => {
      window.__v0841DecorationMutations += mutations.filter((m) => m.type === 'childList').length;
    });
    observer.observe(grid, { childList: true, subtree: true });
    window.__h18LegoResizeV0841.refresh();
  });
  await page.waitForTimeout(250);
  expect(await page.evaluate(() => window.__v0841DecorationMutations)).toBe(0);
  await expect(page.locator('.h18-v0841-resize-handle')).toHaveCount(1);
});

test('LEGO-032 visual resize changes 6/6 to 8/4 as one Undo Redo checkpoint', async ({ page }) => {
  await boot(page);
  await resizeFirstBoundaryByColumns(page, 2);
  await page.waitForTimeout(420);

  expect(await page.evaluate(() => window.__v0841HistoryHarness.spans())).toEqual([8, 4]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.stored())).toEqual([8, 4]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.state())).toEqual({ index: 1, entries: 2 });
  expect(await page.evaluate(() => window.__h18HistoryAtomicV0840.isActive())).toBe(false);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(320);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.spans())).toEqual([6, 6]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.stored())).toEqual([0, 0]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.state())).toEqual({ index: 0, entries: 2 });

  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(320);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.spans())).toEqual([8, 4]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.stored())).toEqual([8, 4]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.state())).toEqual({ index: 1, entries: 2 });
});

test('LEGO-032 resize clamps each neighbor to at least one of twelve columns', async ({ page }) => {
  await boot(page);
  // From 6/6, +6 requests 12/0. The runtime must clamp that one-column
  // overshoot to 11/1 without sending the pointer outside the viewport.
  await resizeFirstBoundaryByColumns(page, 6);
  await page.waitForTimeout(350);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.spans())).toEqual([11, 1]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.stored())).toEqual([11, 1]);
});

test('LEGO-032 Tablet and Mobile inherit Desktop and cannot initiate resize', async ({ page }) => {
  await boot(page);
  const canvas = page.locator('.h18-builder-canvas');
  const handle = page.locator('.h18-v0841-resize-handle').first();

  await canvas.evaluate((node) => node.setAttribute('data-canvas-device', 'tablet'));
  await page.waitForTimeout(80);
  await expect(handle).toBeHidden();
  await handle.dispatchEvent('pointerdown', { button: 0, pointerId: 71, clientX: 400, clientY: 180 });
  await page.evaluate(() => document.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, pointerId: 71, clientX: 700, clientY: 180 })));
  await page.evaluate(() => document.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 71, clientX: 700, clientY: 180 })));
  await page.waitForTimeout(80);

  expect(await page.evaluate(() => window.__v0841HistoryHarness.stored())).toEqual([0, 0]);
  expect(await page.evaluate(() => window.__v0841HistoryHarness.state())).toEqual({ index: 0, entries: 1 });
  const state = await page.evaluate(() => window.__h18LegoResizeV0841.stateForKey('text-1'));
  expect(state.Tablet.InheritDesktop).toBe(true);
  expect(state.Mobile.InheritDesktop).toBe(true);

  await canvas.evaluate((node) => node.setAttribute('data-canvas-device', 'mobile'));
  await page.waitForTimeout(50);
  await expect(handle).toBeHidden();
});
