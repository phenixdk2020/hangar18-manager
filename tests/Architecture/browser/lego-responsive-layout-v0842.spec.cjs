const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const historyBridge = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0821.js');
const historyAtomic = path.resolve(__dirname, '../../../assets/ultimate-designer-history-atomic-v0840.js');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const resizeRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-resize-v0841.js');
const resizeCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-resize-v0841.css');
const responsiveRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-responsive-layout-v0842.js');
const responsiveCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-responsive-layout-v0842.css');

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
  await page.addStyleTag({ path: responsiveCss });
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ path: historyBridge });
  await page.addScriptTag({ path: historyAtomic });
  await page.evaluate(() => {
    window.H18LegoResizeV0841 = { version: '0.8.42', schemaVersion: 2, columns: 12, pages: {} };
  });
  await page.addScriptTag({ path: nestingRuntime });
  await page.addScriptTag({ path: resizeRuntime });
  await page.addScriptTag({ path: responsiveRuntime });

  await page.waitForFunction(() => Boolean(window.__h18LegoResizeV0841 && window.__h18LegoResponsiveLayoutV0842 && window.__h18HistoryAtomicV0840));
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
        if (window.__h18LegoResponsiveLayoutV0842) window.__h18LegoResponsiveLayoutV0842.refresh();
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

    window.__v0842Harness = {
      history() { return { index, entries: entries.length }; },
      state(key) { return window.__h18LegoResponsiveLayoutV0842.stateForKey(key); },
      spans(device) { return window.__h18LegoResponsiveLayoutV0842.effectiveForAuto('auto-1', device); }
    };
  });
}

async function setDevice(page, device) {
  await page.locator('.h18-builder-canvas').evaluate((node, value) => node.setAttribute('data-canvas-device', value), device.toLowerCase());
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-responsive-layout-device', device.toLowerCase(), { timeout: 2500 });
  await page.waitForTimeout(80);
}

async function resizeFirstBoundaryByColumns(page, deltaColumns) {
  const handle = page.locator('.h18-v0841-resize-handle').first();
  const grid = page.locator('.h18-v0841-resize-grid');
  const handleBox = await handle.boundingBox();
  const gridBox = await grid.boundingBox();
  if (!handleBox || !gridBox) throw new Error('Responsive resize geometry unavailable');
  const gap = await grid.evaluate((node) => parseFloat(getComputedStyle(node).columnGap || getComputedStyle(node).gap || '0') || 0);
  const step = (gridBox.width + gap) / 12;
  const x = handleBox.x + handleBox.width / 2;
  const y = handleBox.y + handleBox.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x + step * deltaColumns, y, { steps: 8 });
  await page.mouse.up();
}

async function expectRenderedSpans(page, expected) {
  const tiles = page.locator('.h18-v0841-resize-tile');
  for (let index = 0; index < expected.length; index += 1) {
    await expect(tiles.nth(index)).toHaveAttribute('data-h18-v0842-effective-span', String(expected[index]));
    await expect.poll(async () => tiles.nth(index).evaluate((node) => node.style.getPropertyValue('--h18-v0841-span'))).toBe(String(expected[index]));
  }
}

test('LEGO-033 Tablet and Mobile initially inherit the Desktop 6/6 Auto layout', async ({ page }) => {
  await boot(page);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Desktop'))).toEqual([6, 6]);

  await setDevice(page, 'Tablet');
  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([6, 6]);
  await expectRenderedSpans(page, [6, 6]);
  await expect(page.locator('.h18-v0841-resize-handle').first()).toBeVisible();
  await expect(page.locator('.h18-v0842-inherit-toggle')).toHaveCount(2);
  expect(await page.evaluate(() => window.__v0842Harness.state('text-1').Tablet.InheritDesktop)).toBe(true);

  await setDevice(page, 'Mobile');
  expect(await page.evaluate(() => window.__v0842Harness.spans('Mobile'))).toEqual([6, 6]);
  await expectRenderedSpans(page, [6, 6]);
  expect(await page.evaluate(() => window.__v0842Harness.state('text-1').Mobile.InheritDesktop)).toBe(true);
});

test('LEGO-033 Tablet resize creates only Tablet overrides as one Undo Redo checkpoint', async ({ page }) => {
  await boot(page);
  await setDevice(page, 'Tablet');
  await resizeFirstBoundaryByColumns(page, 2);
  await page.waitForTimeout(420);

  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([8, 4]);
  await expectRenderedSpans(page, [8, 4]);
  await page.waitForTimeout(500);
  await expectRenderedSpans(page, [8, 4]);
  const states = await page.evaluate(() => ['text-1','image-1'].map((key) => window.__v0842Harness.state(key)));
  expect(states.map((state) => state.Desktop.Span)).toEqual([0, 0]);
  expect(states.map((state) => state.Tablet.Span)).toEqual([8, 4]);
  expect(states.map((state) => state.Tablet.InheritDesktop)).toEqual([false, false]);
  expect(states.map((state) => state.Tablet.HasOverride)).toEqual([true, true]);
  expect(states.map((state) => state.Mobile.InheritDesktop)).toEqual([true, true]);
  expect(await page.evaluate(() => window.__v0842Harness.history())).toEqual({ index: 1, entries: 2 });
  expect(await page.evaluate(() => window.__h18HistoryAtomicV0840.isActive())).toBe(false);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(360);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([6, 6]);
  await expectRenderedSpans(page, [6, 6]);
  expect(await page.evaluate(() => window.__v0842Harness.history())).toEqual({ index: 0, entries: 2 });

  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(360);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([8, 4]);
  await expectRenderedSpans(page, [8, 4]);
  expect(await page.evaluate(() => window.__v0842Harness.history())).toEqual({ index: 1, entries: 2 });
});

test('LEGO-033 Desktop Tablet and Mobile layouts remain independent', async ({ page }) => {
  await boot(page);
  await setDevice(page, 'Tablet');
  await resizeFirstBoundaryByColumns(page, 2);
  await page.waitForTimeout(360);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([8, 4]);
  await expectRenderedSpans(page, [8, 4]);

  await setDevice(page, 'Desktop');
  expect(await page.evaluate(() => window.__v0842Harness.spans('Desktop'))).toEqual([6, 6]);

  await setDevice(page, 'Mobile');
  expect(await page.evaluate(() => window.__v0842Harness.spans('Mobile'))).toEqual([6, 6]);
  await expectRenderedSpans(page, [6, 6]);
  await resizeFirstBoundaryByColumns(page, -1);
  await page.waitForTimeout(360);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Mobile'))).toEqual([5, 7]);
  await expectRenderedSpans(page, [5, 7]);

  expect(await page.evaluate(() => window.__v0842Harness.spans('Desktop'))).toEqual([6, 6]);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([8, 4]);
  const text = await page.evaluate(() => window.__v0842Harness.state('text-1'));
  expect(text.Tablet.Span).toBe(8);
  expect(text.Mobile.Span).toBe(5);
});

test('LEGO-033 Arv Desktop preserves and restores the responsive override snapshot', async ({ page }) => {
  await boot(page);
  await setDevice(page, 'Tablet');
  await resizeFirstBoundaryByColumns(page, 2);
  await page.waitForTimeout(360);
  await expectRenderedSpans(page, [8, 4]);

  const firstToggle = page.locator('.h18-v0842-inherit-toggle').first();
  await expect(firstToggle).toHaveAttribute('aria-pressed', 'false');
  await firstToggle.click();
  await page.waitForTimeout(340);
  let state = await page.evaluate(() => window.__v0842Harness.state('text-1'));
  expect(state.Tablet.InheritDesktop).toBe(true);
  expect(state.Tablet.HasOverride).toBe(true);
  expect(state.Tablet.Span).toBe(8);

  await page.locator('.h18-v0842-inherit-toggle').first().click();
  await page.waitForTimeout(340);
  state = await page.evaluate(() => window.__v0842Harness.state('text-1'));
  expect(state.Tablet.InheritDesktop).toBe(false);
  expect(state.Tablet.Span).toBe(8);
  expect(await page.evaluate(() => window.__v0842Harness.spans('Tablet'))).toEqual([8, 4]);
  await expectRenderedSpans(page, [8, 4]);
});
