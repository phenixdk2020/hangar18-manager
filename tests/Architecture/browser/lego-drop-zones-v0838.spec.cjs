const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const dropRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.js');
const dropCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-drop-zones-v0838.css');

function row(index, key, type, label, parent = '') {
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header">${label}</header>
    <div class="h18-canvas-preview"><div class="base-preview">${key}</div></div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" value="${key}">
      <input class="h18-page-section-type" value="${type}">
      <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <select class="h18-layout-parent-select"><option value=""></option></select>
      <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
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
    #h18-page-sections-sortable{width:800px;position:relative}.h18-page-section-row{display:block;width:720px;margin:12px 0;padding:8px;border:1px solid #ccc}.h18-canvas-preview{display:block;width:680px;height:150px;padding:8px;position:relative}.base-preview{height:110px}
  </style></head><body>
    <button id="grid-palette" class="h18-builder-palette-item" data-section-type="grid">Grid</button>
    <div class="h18-builder-canvas"></div>
    <div id="h18-page-inspector-target"></div>
    <div id="h18-page-sections-sortable">
      ${row(1, 'box-a', 'container', 'Kasse')}
      ${row(2, 'box-b', 'container', 'Kasse')}
      ${row(3, 'text-1', 'text', 'Tekst')}
      ${row(4, 'text-2', 'text', 'Tekst 2')}
    </div>
  </body></html>`);
  await page.addStyleTag({ path: nestingCss });
  await page.addStyleTag({ path: dropCss });
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    let gridSerial = 0;
    window.jQuery('#grid-palette').on('click', function () {
      gridSerial += 1;
      const index = 10 + gridSerial;
      window.jQuery('#h18-page-sections-sortable').append(`<section id="row-auto-${gridSerial}" class="h18-page-section-row" data-section-type="grid" data-section-index="${index}">
        <header class="h18-page-section-header">Grid</header><div class="h18-canvas-preview"><div class="base-preview">grid</div></div><div class="h18-page-section-body">
        <input class="h18-page-section-key" value="auto-${gridSerial}"><input class="h18-page-section-type" value="grid"><input class="h18-section-navigator-label" value="Grid">
        <input class="h18-layout-parent-key" value=""><select class="h18-layout-parent-select"><option value=""></option></select><input class="h18-page-section-order" value="${index * 10}">
        <input name="Sections[${index}][LayoutColumns]" value="1"><input name="Sections[${index}][MobileLayoutColumns]" value="1"><input name="Sections[${index}][LayoutGapPx]" value="16"><input name="Sections[${index}][MobileLayoutGapPx]" value="12"><input name="Sections[${index}][LayoutDirection]" value="Column"><input name="Sections[${index}][LayoutAlign]" value="Stretch">
        </div></section>`);
    });
  });

  await page.addScriptTag({ path: nestingRuntime });
  await page.addScriptTag({ path: dropRuntime });
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-drop-zones-runtime', '0.8.38');
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-side-by-side-runtime', '0.8.40');
  await expect(page.locator('#h18-page-sections-sortable')).toHaveAttribute('data-h18-v0811-kasse-runtime', '1', { timeout: 2000 });
  await expect(page.locator('#h18-page-sections-sortable')).toHaveAttribute('data-h18-v0840-side-by-side-runtime', '1', { timeout: 2000 });
}

async function startSort(page, key) {
  await page.evaluate((sourceKey) => {
    const $ = window.jQuery;
    const $row = $('#row-' + sourceKey);
    $('#h18-page-sections-sortable').trigger('sortstart', [{ item: $row }]);
  }, key);
  await expect(page.locator('#h18-page-sections-sortable')).toHaveClass(/h18-v0838-drop-zones-active/, { timeout: 2000 });
}

async function stopSort(page) {
  await page.evaluate(() => window.jQuery('#h18-page-sections-sortable').trigger('sortstop'));
  await expect(page.locator('.h18-v0838-drop-overlay')).toHaveCount(0, { timeout: 2000 });
}

test('existing Kasse drag shows Over Under Venstre Højre and reuses existing side-zone contract', async ({ page }) => {
  await boot(page);
  await startSort(page, 'box-b');

  const overlay = page.locator('#row-box-a > .h18-canvas-preview > .h18-v0838-drop-overlay');
  await expect(overlay).toHaveCount(1);
  await expect(overlay.locator('[data-h18-v0838-position="over"]')).toHaveText('Over');
  await expect(overlay.locator('[data-h18-v0838-position="under"]')).toHaveText('Under');
  await expect(overlay.locator('[data-h18-v0838-position="left"]')).toHaveText('Venstre');
  await expect(overlay.locator('[data-h18-v0838-position="right"]')).toHaveText('Højre');

  const left = overlay.locator('[data-h18-v0838-position="left"]');
  await expect(left).toHaveClass(/h18-v0811-side-zone/);
  await expect(left).toHaveAttribute('data-side', 'left');
  await expect(left).toHaveAttribute('data-box', 'box-a');
  await expect(left).toHaveAttribute('data-h18-v0838-existing-placement-contract', '1');

  await expect(overlay.locator('[data-h18-v0838-position="over"]')).toHaveCSS('pointer-events', 'none');
  await expect(overlay.locator('[data-h18-v0838-position="under"]')).toHaveCSS('pointer-events', 'none');
  await stopSort(page);
});

test('LEGO-031 generic element drag activates Left Right through the same side-zone contract', async ({ page }) => {
  await boot(page);
  await startSort(page, 'text-2');

  const overlay = page.locator('#row-text-1 > .h18-canvas-preview > .h18-v0838-drop-overlay');
  await expect(overlay.locator('[data-h18-v0838-position="over"]')).not.toHaveClass(/is-disabled/);
  await expect(overlay.locator('[data-h18-v0838-position="under"]')).not.toHaveClass(/is-disabled/);
  await expect(overlay.locator('[data-h18-v0838-position="left"]')).not.toHaveClass(/is-disabled/);
  await expect(overlay.locator('[data-h18-v0838-position="right"]')).not.toHaveClass(/is-disabled/);
  await expect(overlay.locator('[data-h18-v0838-position="left"]')).toHaveClass(/h18-v0811-side-zone/);
  await expect(overlay.locator('[data-h18-v0838-position="left"]')).toHaveAttribute('data-h18-v0840-generic-side-contract', '1');
  await stopSort(page);
});

test('LEGO-031 dropping ordinary element beside ordinary element creates authoritative Auto-kasser', async ({ page }) => {
  await boot(page);
  await startSort(page, 'text-2');

  const zone = page.locator('#row-text-1 > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="right"]');
  const rect = await zone.boundingBox();
  if (!rect) throw new Error('Right zone has no geometry');

  await page.evaluate(({ x, y }) => {
    const $ = window.jQuery;
    $('#h18-page-sections-sortable').trigger($.Event('sort', { pageX: x, pageY: y }));
    $('#h18-page-sections-sortable').trigger('sortstop');
  }, { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });

  await expect(page.locator('#row-text-1 .h18-layout-parent-key')).toHaveValue('auto-1', { timeout: 3000 });
  await expect(page.locator('#row-text-2 .h18-layout-parent-key')).toHaveValue('auto-1');
  await expect(page.locator('#row-auto-1 .h18-section-navigator-label')).toHaveValue('Auto-kasser');
  await expect(page.locator('#row-auto-1 .h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 3000 });
  await expect(page.locator('#row-auto-1 .h18-v0811-auto-box[data-h18-v0840-auto-child="text-1"]')).toHaveCount(1);
  await expect(page.locator('#row-auto-1 .h18-v0811-auto-box[data-h18-v0840-auto-child="text-2"]')).toHaveCount(1);
});

test('dropping existing Kasse on v0.8.38 Left zone is executed by existing nesting motor', async ({ page }) => {
  await boot(page);
  await startSort(page, 'box-b');

  const zone = page.locator('#row-box-a > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="left"]');
  const rect = await zone.boundingBox();
  if (!rect) throw new Error('Left zone has no geometry');

  await page.evaluate(({ x, y }) => {
    const $ = window.jQuery;
    $('#h18-page-sections-sortable').trigger($.Event('sort', { pageX: x, pageY: y }));
    $('#h18-page-sections-sortable').trigger('sortstop');
  }, { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });

  await expect(page.locator('#row-box-a .h18-layout-parent-key')).toHaveValue('auto-1', { timeout: 3000 });
  await expect(page.locator('#row-box-b .h18-layout-parent-key')).toHaveValue('auto-1');
  await expect(page.locator('#row-auto-1 .h18-section-navigator-label')).toHaveValue('Auto-kasser');
  await expect(page.locator('#row-auto-1 .h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 3000 });
});

test('Kasse already inside Auto-kasser gets visual left/right proxy targets without new placement data', async ({ page }) => {
  await boot(page);

  await startSort(page, 'box-b');
  const firstZone = page.locator('#row-box-a > .h18-canvas-preview > .h18-v0838-drop-overlay [data-h18-v0838-position="right"]');
  const rect = await firstZone.boundingBox();
  if (!rect) throw new Error('Right zone has no geometry');
  await page.evaluate(({ x, y }) => {
    const $ = window.jQuery;
    $('#h18-page-sections-sortable').trigger($.Event('sort', { pageX: x, pageY: y }));
    $('#h18-page-sections-sortable').trigger('sortstop');
  }, { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });
  await expect(page.locator('#row-auto-1 .h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 3000 });

  await page.evaluate(() => {
    const $ = window.jQuery;
    $('#h18-page-sections-sortable').append(`<section id="row-box-c" class="h18-page-section-row" data-section-type="container"><header class="h18-page-section-header">Kasse</header><div class="h18-canvas-preview"><div class="base-preview">box-c</div></div><div class="h18-page-section-body"><input class="h18-page-section-key" value="box-c"><input class="h18-page-section-type" value="container"><input class="h18-section-navigator-label" value="Kasse"><input class="h18-layout-parent-key" value=""><select class="h18-layout-parent-select"><option value=""></option></select><input class="h18-page-section-order" value="90"><input name="Sections[90][LayoutGapPx]" value="12"></div></section>`);
    $('#h18-page-sections-sortable').trigger('sortstart', [{ item: $('#row-box-c') }]);
  });

  await expect(page.locator('#row-auto-1 .h18-v0838-auto-proxy-overlay')).toHaveCount(2, { timeout: 2000 });
  await expect(page.locator('#row-auto-1 .h18-v0838-auto-proxy-overlay .h18-v0811-side-zone')).toHaveCount(4);
  await stopSort(page);
});
