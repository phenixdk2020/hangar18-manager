const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const primaryRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-primary-view-v0836.js');
const layoutRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-layout-primary-v0837.js');
const primaryCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-primary-view-v0836.css');
const layoutCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-layout-primary-v0837.css');

function field(name, value) {
  return `<input class="legacy-layout-field" type="number" name="Sections[1][${name}]" value="${value}">`;
}

async function boot(page, device = 'tablet') {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="hjem">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target">
        <label>Tablet width <input id="inspector-tablet-width" type="number" name="Sections[1][TabletWidthPercent]" value="100"></label>
      </div></div>
      <div class="h18-builder-canvas" data-canvas-device="${device}" data-canvas-state="normal"></div>
      <div id="h18-page-sections-sortable">
        <section id="row-box-a" class="h18-page-section-row is-selected" data-section-type="container">
          <div class="h18-canvas-preview">
            <div class="h18-canvas-direct-controls" data-canvas-state="normal">
              <strong class="h18-canvas-direct-title">Direkte design</strong>
              <div class="h18-canvas-quick-ranges">
                <label class="h18-canvas-quick-range"><span>Indvendig</span><input id="direct-tablet-padding" type="range" value="12" data-canvas-quick-field="TabletPaddingPx"><output>12 px</output></label>
                <label class="h18-canvas-quick-range"><span>Bredde</span><input id="direct-tablet-width" type="range" value="100" data-canvas-quick-field="TabletWidthPercent"><output>100%</output></label>
                <label class="h18-canvas-quick-range"><span>Kolonner</span><input id="direct-columns" type="range" value="3" data-canvas-quick-field="Columns"><output>3</output></label>
                <label class="h18-canvas-quick-range"><span>Mobil kolonneafstand</span><input id="direct-mobile-column-gap" type="range" value="9" data-canvas-quick-field="MobileColumnGapPx"><output>9 px</output></label>
                <label class="h18-canvas-quick-range"><span>Radius</span><input id="direct-radius" type="range" value="7" data-canvas-quick-field="RadiusPx"><output>7 px</output></label>
              </div>
            </div>
          </div>
          <div class="h18-page-section-body">
            <input class="h18-page-section-key" value="box-a">
            ${field('PaddingPx', '16')}${field('HorizontalPaddingPx', '16')}${field('TopSpacingPx', '8')}${field('BottomSpacingPx', '8')}${field('WidthPercent', '100')}${field('MinHeightPx', '0')}
            ${field('TabletPaddingPx', '12')}${field('TabletHorizontalPaddingPx', '10')}${field('TabletTopSpacingPx', '6')}${field('TabletBottomSpacingPx', '6')}${field('TabletWidthPercent', '100')}${field('TabletMinHeightPx', '0')}
            ${field('MobilePaddingPx', '8')}${field('MobileHorizontalPaddingPx', '8')}${field('MobileTopSpacingPx', '4')}${field('MobileBottomSpacingPx', '4')}${field('MobileWidthPercent', '100')}${field('MobileMinHeightPx', '0')}
            ${field('Columns', '3')}${field('MobileColumns', '1')}${field('ColumnGapPx', '16')}${field('MobileColumnGapPx', '9')}
          </div>
        </section>
      </div>
    </form>
  </body></html>`);

  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(() => {
    window.__v0837 = { direct: 0, inspector: 0, historyEvents: 0 };
    const $ = window.jQuery;

    // Simulate the existing admin.js direct-layout handler. It remains the
    // persistence/public-field writer while v0.8.37 mirrors canonical state.
    $(document).on('input', '.h18-canvas-direct-controls [data-canvas-quick-field]', function () {
      const fieldName = String($(this).attr('data-canvas-quick-field') || '');
      if (!fieldName) return;
      window.__v0837.direct += 1;
      $('#row-box-a [name$="[' + fieldName + ']"]').val(String($(this).val()));
    });

    // Simulate existing Inspector -> row synchronization.
    $(document).on('input change', '#h18-page-inspector-target [name]', function () {
      const name = String($(this).attr('name') || '');
      const match = name.match(/\[([^\]]+)\]$/);
      if (!match) return;
      window.__v0837.inspector += 1;
      $('#row-box-a [name$="[' + match[1] + ']"]').val(String($(this).val()));
    });

    $('#h18-page-editor-form').on('input change', ':input', function () {
      if (!$(this).hasClass('h18-lego-layout-primary-state-json')) {
        window.__v0837.historyEvents += 1;
      }
    });
  });

  await page.addStyleTag({ path: primaryCss });
  await page.addStyleTag({ path: layoutCss });
  await page.addScriptTag({ path: primaryRuntime });
  await page.addScriptTag({ path: layoutRuntime });

  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-layout-primary-runtime', '0.8.37');
  await expect(page.locator('#row-box-a')).toHaveAttribute('data-h18-v0837-layout-canonical', '1');
  await expect(page.locator('#row-box-a .h18-lego-layout-primary-state-json')).toHaveCount(1);
}

async function canonical(page) {
  return page.evaluate(() => window.__h18LegoLayoutPrimaryV0837.stateForKey('box-a'));
}

async function directInput(page, selector, value) {
  await page.locator(selector).evaluate((el, v) => {
    el.value = String(v);
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
  await page.waitForTimeout(40);
}

test('Direct Design layout mirrors into canonical row state before one existing checkpoint', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => { window.__v0837 = { direct: 0, inspector: 0, historyEvents: 0 }; });

  await directInput(page, '#direct-tablet-padding', 24);
  await expect(page.locator('#row-box-a [name$="[TabletPaddingPx]"]')).toHaveValue('24');
  const state = await canonical(page);
  expect(state.Fields.TabletPaddingPx).toBe(24);
  expect(await page.evaluate(() => window.__v0837)).toEqual({ direct: 1, inspector: 0, historyEvents: 1 });
  await expect(page.locator('#direct-tablet-padding')).toHaveAttribute('data-h18-v0837-layout-proxy', '1');
  await expect(page.locator('#direct-tablet-padding').locator('xpath=ancestor::label[1]')).toHaveAttribute('data-h18-v0837-canonical-layout', '1');
});

test('Inspector layout input updates the same canonical row state without a second state event', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => { window.__v0837 = { direct: 0, inspector: 0, historyEvents: 0 }; });

  await page.locator('#inspector-tablet-width').fill('87');
  await expect(page.locator('#row-box-a [name$="[TabletWidthPercent]"]')).toHaveValue('87');
  const state = await canonical(page);
  expect(state.Fields.TabletWidthPercent).toBe(87);
  expect(await page.evaluate(() => window.__v0837)).toEqual({ direct: 0, inspector: 1, historyEvents: 1 });
  await expect(page.locator('#inspector-tablet-width')).toHaveAttribute('data-h18-v0837-layout-proxy', '1');
});

test('specialized Columns and MobileColumnGap keep exact legacy semantics inside canonical state', async ({ page }) => {
  await boot(page, 'mobile');
  await page.evaluate(() => { window.__v0837 = { direct: 0, inspector: 0, historyEvents: 0 }; });

  await directInput(page, '#direct-columns', 4);
  await directInput(page, '#direct-mobile-column-gap', 22);
  await expect(page.locator('#row-box-a [name$="[Columns]"]')).toHaveValue('4');
  await expect(page.locator('#row-box-a [name$="[MobileColumnGapPx]"]')).toHaveValue('22');
  const state = await canonical(page);
  expect(state.Fields.Columns).toBe(4);
  expect(state.Fields.MobileColumnGapPx).toBe(22);
  expect(await page.evaluate(() => window.__v0837.historyEvents)).toBe(2);
});

test('v0.8.36 design proxy remains separate while layout controls become canonical layout', async ({ page }) => {
  await boot(page);
  await expect(page.locator('#direct-radius')).toHaveAttribute('data-h18-v0836-proxy', 'design');
  await expect(page.locator('#direct-radius')).not.toHaveAttribute('data-h18-v0837-layout-proxy', '1');
  await expect(page.locator('#direct-tablet-padding')).toHaveAttribute('data-h18-v0836-layout-control', '1');
  await expect(page.locator('#direct-tablet-padding')).toHaveAttribute('data-h18-v0837-layout-proxy', '1');
});

test('history-style DOM restore brings legacy layout and canonical state back together', async ({ page }) => {
  await boot(page);
  const baseline = await page.locator('#h18-page-sections-sortable').evaluate((node) => node.innerHTML);

  await directInput(page, '#direct-tablet-padding', 26);
  const afterPadding = await page.locator('#h18-page-sections-sortable').evaluate((node) => node.innerHTML);

  await page.locator('#inspector-tablet-width').fill('82');
  await page.waitForTimeout(40);
  const afterWidth = await page.locator('#h18-page-sections-sortable').evaluate((node) => node.innerHTML);

  await page.locator('#h18-page-sections-sortable').evaluate((node, html) => { node.innerHTML = html; }, afterPadding);
  await expect.poll(async () => (await canonical(page)).Fields.TabletPaddingPx).toBe(26);
  expect((await canonical(page)).Fields.TabletWidthPercent).toBe(100);
  await expect(page.locator('#row-box-a [name$="[TabletPaddingPx]"]')).toHaveValue('26');
  await expect(page.locator('#row-box-a [name$="[TabletWidthPercent]"]')).toHaveValue('100');

  await page.locator('#h18-page-sections-sortable').evaluate((node, html) => { node.innerHTML = html; }, baseline);
  await expect.poll(async () => (await canonical(page)).Fields.TabletPaddingPx).toBe(12);
  expect((await canonical(page)).Fields.TabletWidthPercent).toBe(100);

  await page.locator('#h18-page-sections-sortable').evaluate((node, html) => { node.innerHTML = html; }, afterWidth);
  await expect.poll(async () => (await canonical(page)).Fields.TabletPaddingPx).toBe(26);
  expect((await canonical(page)).Fields.TabletWidthPercent).toBe(82);
});
