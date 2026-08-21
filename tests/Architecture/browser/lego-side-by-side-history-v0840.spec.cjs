const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const historyBridge = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0821.js');
const historyAtomic = path.resolve(__dirname, '../../../assets/ultimate-designer-history-atomic-v0840.js');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const dropRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.js');
const dropCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.css');

function row(index, key, type, label, parent = '') {
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header">${label}</header>
    <div class="h18-canvas-preview"><div class="base-preview">${key}</div></div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <select class="h18-layout-parent-select"><option value=""></option></select>
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
    #h18-page-editor-form{display:block}.h18-builder-canvas{display:block;width:820px;min-height:500px}
    #h18-page-sections-sortable{width:800px;position:relative}.h18-page-section-row{display:block;width:720px;margin:12px 0;padding:8px;border:1px solid #ccc}
    .h18-canvas-preview{display:block;width:680px;height:150px;padding:8px;position:relative}.base-preview{height:110px}
  </style></head><body>
    <form id="h18-page-editor-form">
      <button id="h18-editor-undo" type="button">Fortryd</button>
      <button id="h18-editor-redo" type="button">Gendan</button>
      <span id="h18-editor-history-status">Ingen ugemte ændringer</span>
      <button id="grid-palette" type="button" class="h18-builder-palette-item" data-section-type="grid">Grid</button>
      <div class="h18-builder-canvas">
        <div id="h18-page-sections-sortable">
          ${row(1, 'text-1', 'text', 'Tekst')}
          ${row(2, 'text-2', 'text', 'Tekst 2')}
        </div>
      </div>
      <aside id="h18-page-inspector"><div class="h18-builder-inspector-heading"><span>Vælg</span></div><span id="h18-inspector-type">–</span><span id="h18-inspector-key">–</span><div id="h18-page-inspector-target"></div></aside>
    </form>
  </body></html>`);

  await page.addStyleTag({ path: nestingCss });
  await page.addStyleTag({ path: dropCss });
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ path: historyBridge });

  await page.evaluate(() => {
    let gridSerial = 0;
    window.jQuery('#grid-palette').on('click', function () {
      gridSerial += 1;
      const index = 10 + gridSerial;
      window.jQuery('#h18-page-sections-sortable').append(`<section id="row-auto-${gridSerial}" class="h18-page-section-row" data-section-type="grid" data-section-index="${index}">
        <header class="h18-page-section-header">Grid</header><div class="h18-canvas-preview"><div class="base-preview">grid</div></div><div class="h18-page-section-body">
        <input class="h18-page-section-key" name="Sections[${index}][Key]" value="auto-${gridSerial}"><input class="h18-page-section-type" name="Sections[${index}][Type]" value="grid"><input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="Grid">
        <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value=""><select class="h18-layout-parent-select"><option value=""></option></select><input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
        <input name="Sections[${index}][Title]" value=""><input name="Sections[${index}][Content]" value=""><input name="Sections[${index}][LayoutColumns]" value="1"><input name="Sections[${index}][MobileLayoutColumns]" value="1"><input name="Sections[${index}][LayoutGapPx]" value="16"><input name="Sections[${index}][MobileLayoutGapPx]" value="12"><input name="Sections[${index}][LayoutDirection]" value="Column"><input name="Sections[${index}][LayoutAlign]" value="Stretch">
        </div></section>`);
    });
  });

  await page.addScriptTag({ path: nestingRuntime });
  await page.addScriptTag({ path: historyAtomic });
  await page.addScriptTag({ path: dropRuntime });

  await expect(page.locator('#h18-page-sections-sortable')).toHaveAttribute('data-h18-v0840-side-by-side-runtime', '1', { timeout: 2500 });
  await page.waitForFunction(() => Boolean(window.__h18HistoryCoreBridgeV0821 && window.__h18HistoryAtomicV0840));

  await page.evaluate(() => {
    const $ = window.jQuery;
    const sections = document.getElementById('h18-page-sections-sortable');
    const entries = [];
    let index = -1;
    let editorHistoryTimer = null;
    let applying = false;

    function canonicalHtml() {
      const clone = $(sections).clone(false, false).get(0);
      clone.querySelectorAll('.h18-v0838-drop-overlay,.h18-ud-auto-box-grid,.h18-v0814-auto-drop-zone,.h18-ud-box-contents-preview,.h18-v0811-side-zones').forEach((node) => node.remove());
      clone.querySelectorAll('.is-selected,.h18-ud-nesting-drop-target,.h18-v0814-auto-drop-target').forEach((node) => node.classList.remove('is-selected','h18-ud-nesting-drop-target','h18-v0814-auto-drop-target'));
      clone.querySelectorAll('input').forEach((input) => {
        if (input.type === 'checkbox' || input.type === 'radio') {
          if (input.checked) input.setAttribute('checked', 'checked'); else input.removeAttribute('checked');
        } else {
          input.setAttribute('value', String(input.value == null ? '' : input.value));
        }
      });
      clone.querySelectorAll('select').forEach((select) => {
        const values = Array.from(select.selectedOptions).map((option) => String(option.value));
        Array.from(select.options).forEach((option) => values.includes(String(option.value)) ? option.setAttribute('selected','selected') : option.removeAttribute('selected'));
      });
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
      window.setTimeout(() => { applying = false; }, 0);
    }

    function undo() {
      flushPending();
      if (index <= 0) return;
      index -= 1;
      restore(entries[index]);
    }

    function redo() {
      flushPending();
      if (index < 0 || index >= entries.length - 1) return;
      index += 1;
      restore(entries[index]);
    }

    $('#h18-page-editor-form').on('input change', '.h18-page-section-body :input', function () {
      if (!applying) scheduleEditorHistoryCapture(280);
    });

    const observer = new MutationObserver((mutations) => {
      if (applying) return;
      const meaningful = mutations.some((mutation) => mutation.type === 'childList' && mutation.target.closest && mutation.target.closest('#h18-page-sections-sortable'));
      if (meaningful) scheduleEditorHistoryCapture(120);
    });
    observer.observe(sections, { childList: true, subtree: true });

    document.getElementById('h18-editor-undo').addEventListener('click', undo);
    document.getElementById('h18-editor-redo').addEventListener('click', redo);
    editorHistoryRecordNow();

    window.__v0840HistoryHarness = {
      state() {
        const rows = Array.from(sections.querySelectorAll(':scope > .h18-page-section-row'));
        return {
          index,
          entries: entries.length,
          keys: rows.map((row) => String(row.querySelector('.h18-page-section-key')?.value || '')),
          parents: Object.fromEntries(rows.map((row) => [String(row.querySelector('.h18-page-section-key')?.value || ''), String(row.querySelector('.h18-layout-parent-key')?.value || '')])),
          orders: Object.fromEntries(rows.map((row) => [String(row.querySelector('.h18-page-section-key')?.value || ''), String(row.querySelector('.h18-page-section-order')?.value || '')])),
          atomic: Boolean(window.__h18HistoryAtomicV0840 && window.__h18HistoryAtomicV0840.isActive())
        };
      }
    };
  });
}

async function sideDropText2RightOfText1(page) {
  await page.evaluate(() => {
    const $ = window.jQuery;
    $('#h18-page-sections-sortable').trigger('sortstart', [{ item: $('#row-text-2') }]);
  });
  await expect(page.locator('#h18-page-sections-sortable')).toHaveClass(/h18-v0838-drop-zones-active/, { timeout: 2000 });
  const zone = page.locator('#row-text-1 > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="right"]');
  const rect = await zone.boundingBox();
  if (!rect) throw new Error('Right side zone has no geometry');
  await page.evaluate(({ x, y }) => {
    const $ = window.jQuery;
    $('#h18-page-sections-sortable').trigger($.Event('sort', { pageX: x, pageY: y }));
    $('#h18-page-sections-sortable').trigger('sortstop');
  }, { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });
}

test('LEGO-031 side-drop is one history checkpoint and Undo Redo restores wrapper order and parents', async ({ page }) => {
  await boot(page);
  expect(await page.evaluate(() => window.__v0840HistoryHarness.state())).toMatchObject({ index: 0, entries: 1, keys: ['text-1','text-2'], atomic: false });

  await sideDropText2RightOfText1(page);
  await page.waitForTimeout(850);

  let current = await page.evaluate(() => window.__v0840HistoryHarness.state());
  expect(current.index).toBe(1);
  expect(current.entries).toBe(2);
  expect(current.keys).toEqual(['auto-1','text-1','text-2']);
  expect(current.parents['text-1']).toBe('auto-1');
  expect(current.parents['text-2']).toBe('auto-1');
  expect(current.orders).toEqual({ 'auto-1':'10', 'text-1':'20', 'text-2':'30' });
  expect(current.atomic).toBe(false);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(260);
  current = await page.evaluate(() => window.__v0840HistoryHarness.state());
  expect(current.index).toBe(0);
  expect(current.entries).toBe(2);
  expect(current.keys).toEqual(['text-1','text-2']);
  expect(current.parents['text-1']).toBe('');
  expect(current.parents['text-2']).toBe('');
  expect(current.orders).toEqual({ 'text-1':'10', 'text-2':'20' });

  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(300);
  current = await page.evaluate(() => window.__v0840HistoryHarness.state());
  expect(current.index).toBe(1);
  expect(current.entries).toBe(2);
  expect(current.keys).toEqual(['auto-1','text-1','text-2']);
  expect(current.parents['text-1']).toBe('auto-1');
  expect(current.parents['text-2']).toBe('auto-1');
  expect(current.orders).toEqual({ 'auto-1':'10', 'text-1':'20', 'text-2':'30' });
});
