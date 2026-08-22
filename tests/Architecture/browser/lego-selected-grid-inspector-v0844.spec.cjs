const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const dropRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.js');
const dropCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.css');
const parentGuardRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-parent-key-guard-v0845.js');
const bridgeRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js');

function row(index, key, type, label) {
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header"><span class="h18-page-section-title-summary">${label}</span></header>
    <div class="h18-canvas-preview"><div class="base-preview">${label}</div></div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="">
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

    <!-- Real editor order: Inspector is before the canvas. -->
    <aside id="h18-page-inspector"><div id="h18-page-inspector-target"></div></aside>

    <div class="h18-builder-canvas">
      <div id="h18-page-sections-sortable">
        ${row(1, 'target-1', 'text_image', 'Tekst og billede')}
      </div>
    </div>
  </body></html>`);

  await page.addStyleTag({ path: nestingCss });
  await page.addStyleTag({ path: dropCss });
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    const $ = window.jQuery;
    let inspected = $();
    let gridSerial = 0;
    let elementSerial = 0;

    function controls($row, selector) {
      let $result = $row.find(selector);
      if (inspected.length && inspected.get(0) === $row.get(0)) {
        $result = $result.add($('#h18-page-inspector-target').find(selector));
      }
      return $result;
    }

    function rowForElement(element) {
      const $closest = $(element).closest('.h18-page-section-row');
      return $closest.length ? $closest : inspected;
    }

    function restoreInspected() {
      if (!inspected.length) return;
      const $body = $('#h18-page-inspector-target').children('.h18-page-section-body');
      if ($body.length) inspected.append($body);
      inspected.removeClass('is-selected');
      inspected = $();
      $('#h18-page-inspector-target').empty();
    }

    function inspect($row) {
      restoreInspected();
      inspected = $row;
      $row.addClass('is-selected');
      $('#h18-page-inspector-target').empty().append($row.children('.h18-page-section-body'));
    }

    function appendRow(index, key, type, label) {
      $('#h18-page-sections-sortable').append(window.__rowMarkup(index, key, type, label));
      const $row = $('#row-' + key);
      // Real addPageSection() selects every newly created section and physically
      // moves its .h18-page-section-body into the Inspector.
      inspect($row);
      return $row;
    }

    window.__h18InspectorHarness = {
      controls,
      inspectedKey: () => inspected.length ? String(controls(inspected, '.h18-page-section-key').first().val() || '') : ''
    };

    $('#grid-palette').on('click', function () {
      gridSerial += 1;
      appendRow(20 + gridSerial, `auto-${gridSerial}`, 'grid', 'Grid container');
    });

    // Model the real pageSectionForElement()/pageSectionControls() path. When a
    // selected row's select lives in Inspector, closest(row) is intentionally empty.
    $(document).on('change', '.h18-layout-parent-select', function () {
      const $row = rowForElement(this);
      controls($row, '.h18-layout-parent-key').first()
        .val(String($(this).val() || ''))
        .trigger('change');
    });

    // The canvas drop creates the requested palette element before the document
    // level nesting drop handler completes, matching the real bubble order.
    document.addEventListener('drop', function (event) {
      const zone = event.target && event.target.closest ? event.target.closest('.h18-v0811-side-zone') : null;
      if (!zone || document.getElementById('row-text-new')) return;
      elementSerial += 1;
      appendRow(10 + elementSerial, 'text-new', 'text', 'Tekst');
    }, false);
  });

  // Supply row markup inside the page context without duplicating test logic in JS.
  await page.evaluate((markup) => {
    window.__rowMarkup = function (index, key, type, label) {
      return markup
        .replaceAll('__INDEX__', String(index))
        .replaceAll('__KEY__', String(key))
        .replaceAll('__TYPE__', String(type))
        .replaceAll('__LABEL__', String(label));
    };
  }, row('__INDEX__', '__KEY__', '__TYPE__', '__LABEL__'));

  await page.addScriptTag({ path: nestingRuntime });
  await page.addScriptTag({ path: parentGuardRuntime });
  await page.addScriptTag({ path: dropRuntime });
  await page.addScriptTag({ path: bridgeRuntime });
}

test('selected Grid created during palette side-drop stays discoverable while its body lives in Inspector', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => {
    document.getElementById('text-palette').dispatchEvent(new DragEvent('dragstart', {
      bubbles: true,
      cancelable: true
    }));
  });

  const zone = page.locator('#row-target-1 > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="left"]');
  await expect(zone).toBeVisible({ timeout: 2500 });
  const rect = await zone.boundingBox();
  if (!rect) throw new Error('Left side zone has no geometry');

  await page.evaluate(({ x, y }) => {
    const preview = document.querySelector('#row-target-1 > .h18-canvas-preview');
    preview.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, clientX: x, clientY: y }));
    preview.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, clientX: x, clientY: y }));
    document.getElementById('text-palette').dispatchEvent(new DragEvent('dragend', { bubbles: true }));
  }, { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });

  await page.waitForTimeout(700);

  const state = await page.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row'));
    const inspector = document.getElementById('h18-page-inspector-target');

    function control(row, selector) {
      return row.querySelector(selector) || (row.classList.contains('is-selected') ? inspector.querySelector(selector) : null);
    }
    function value(row, selector) {
      return control(row, selector)?.value || '';
    }

    const byKey = {};
    rows.forEach((row) => {
      const key = value(row, '.h18-page-section-key');
      byKey[key] = {
        type: row.getAttribute('data-section-type') || '',
        parent: value(row, '.h18-layout-parent-key'),
        selectedParent: value(row, '.h18-layout-parent-select'),
        label: value(row, '.h18-section-navigator-label'),
        selected: row.classList.contains('is-selected')
      };
    });

    const orphanGridContainers = rows.filter((row) => {
      if ((row.getAttribute('data-section-type') || '') !== 'grid') return false;
      const key = value(row, '.h18-page-section-key');
      return rows.filter((candidate) => value(candidate, '.h18-layout-parent-key') === key).length === 0;
    }).length;

    return {
      keys: rows.map((row) => value(row, '.h18-page-section-key')),
      byKey,
      inspectedKey: window.__h18InspectorHarness.inspectedKey(),
      tiles: document.querySelectorAll('.h18-ud-auto-box-grid .h18-v0811-auto-box').length,
      orphanGridContainers
    };
  });

  expect(state.inspectedKey).toBe('auto-1');
  expect(state.keys).toEqual(['auto-1', 'text-new', 'target-1']);
  expect(state.byKey['auto-1'].label).toBe('Auto-kasser');
  expect(state.byKey['text-new'].parent).toBe('auto-1');
  expect(state.byKey['target-1'].parent).toBe('auto-1');
  expect(state.tiles).toBe(2);
  expect(state.orphanGridContainers).toBe(0);
});
