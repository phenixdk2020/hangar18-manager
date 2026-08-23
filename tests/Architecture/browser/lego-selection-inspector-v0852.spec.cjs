const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const fixesRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-fixes-v0851.js');
const fixesCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-fixes-v0851.css');

function editorRow() {
  return `<section id="row-text-1" class="h18-page-section-row" data-section-type="text" data-section-index="1">
    <div class="h18-canvas-preview" style="background:#fff;border:1px solid #777;border-radius:5px">Tekst-preview</div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[1][Key]" value="text-1">
      <input class="h18-page-section-type" name="Sections[1][Type]" value="text">
      <input class="h18-layout-parent-key" name="Sections[1][LayoutParentKey]" value="grid-1">
      <select class="h18-layout-parent-select"><option value="grid-1" selected>grid-1</option></select>
      <input class="h18-page-section-order" name="Sections[1][Order]" value="20">
      <input name="Sections[1][DesignMode]" value="Global">
      <input name="Sections[1][CustomBackgroundColor]" value="#ffffff">
      <details class="h18-section-module-box" open>
        <summary>Luft, baggrund og placering</summary>
        <div class="legacy-device-grid">
          <fieldset class="legacy-device-panel">
            <legend>Desktop</legend>
            <label><strong>Placeringsluft før (px)</strong><input type="number" value="0"></label>
            <label><strong>Luft efter (px)</strong><input type="number" value="0"></label>
            <label><strong>Indvendig luft – lodret (px)</strong><input type="number" value="0"></label>
            <label><strong>Indvendig luft – vandret (px)</strong><input type="number" value="0"></label>
          </fieldset>
          <fieldset class="legacy-device-panel">
            <legend>Mobil</legend>
            <label><strong>Placeringsluft før (px)</strong><input type="number" value="0"></label>
            <label><strong>Luft efter (px)</strong><input type="number" value="0"></label>
            <label><strong>Indvendig luft – lodret (px)</strong><input type="number" value="0"></label>
            <label><strong>Indvendig luft – vandret (px)</strong><input type="number" value="0"></label>
          </fieldset>
        </div>
      </details>
    </div>
  </section>`;
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><head><style>
    body{margin:0;font-family:Arial,sans-serif}
    #h18-page-editor-form{display:block}
    .h18-builder-canvas{position:relative;width:760px;min-height:300px;margin:20px}
    #h18-page-sections-sortable{display:block}
    .h18-page-section-row{display:block}
    .h18-canvas-preview{width:360px;min-height:100px;padding:10px;box-sizing:border-box}
    #h18-page-inspector{width:360px;margin:20px;border:1px solid #ddd}
    #h18-page-inspector-target{width:340px;padding:10px;box-sizing:border-box}
    .legacy-device-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;width:320px;box-sizing:border-box}
    .legacy-device-panel{min-width:0;padding:4px;margin:0}
    .legacy-device-panel label{display:block;min-width:0}
    .h18-v0811-child-card{position:relative;width:360px;min-height:120px;margin-top:12px}
    .h18-v0811-child-preview{position:relative;width:100%;min-height:110px;box-sizing:border-box;background:#fafafa}
  </style></head><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="test-side"></form>
    <div class="h18-builder-canvas" data-canvas-device="desktop">
      <div id="h18-page-sections-sortable">${editorRow()}</div>
      <section id="proxy-text-1" class="h18-v0811-child-card" data-h18-v0811-child="text-1">
        <div class="h18-v0811-child-preview">Klikbart nested element</div>
      </section>
    </div>
    <aside id="h18-page-inspector"><div id="h18-page-inspector-target"></div></aside>
  </body></html>`);

  await page.addStyleTag({ path: fixesCss });
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(() => {
    window.H18LegoFixesV0851 = { pages: {} };
    window.__h18ResizeRefreshCalls = 0;
    window.__h18NestingToolsV0840 = { refresh() {} };
    window.__h18LegoResizeV0841 = {
      refresh() {
        window.__h18ResizeRefreshCalls += 1;
        window.setTimeout(() => {
          const canvas = document.querySelector('.h18-builder-canvas');
          const marker = document.createElement('i');
          marker.className = 'async-layout-marker';
          canvas.appendChild(marker);
        }, 120);
      }
    };
  });
  await page.addScriptTag({ path: fixesRuntime });
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-fixes-hotfix', '0.8.52');
  await page.waitForTimeout(900);
}

async function selectNestedElement(page) {
  await page.evaluate(() => {
    window.__h18ResizeRefreshCalls = 0;
    document.querySelectorAll('.async-layout-marker').forEach((node) => node.remove());
    const row = document.getElementById('row-text-1');
    const proxy = document.getElementById('proxy-text-1');
    const target = document.getElementById('h18-page-inspector-target');
    row.classList.add('is-selected');
    proxy.classList.add('is-h18-v0848-selected-element');
    target.replaceChildren(row.querySelector('.h18-page-section-body'));
    proxy.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  });
}

test('nested selection settles without a derived-layout observer loop and receives the red overlay', async ({ page }) => {
  await boot(page);
  await selectNestedElement(page);
  await page.waitForTimeout(450);

  const state = await page.evaluate(() => ({
    resizeRefreshCalls: window.__h18ResizeRefreshCalls,
    selectedRows: document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row.is-selected').length,
    inspectorOwnsBody: Boolean(document.querySelector('#h18-page-inspector-target > .h18-page-section-body')),
    overlayCount: document.querySelectorAll('#proxy-text-1 .h18-v0851-selection-overlay').length,
    selectionTarget: document.querySelector('#proxy-text-1 .h18-v0811-child-preview')?.classList.contains('h18-v0851-selection-target') || false
  }));

  expect(state.resizeRefreshCalls).toBe(0);
  expect(state.selectedRows).toBe(1);
  expect(state.inspectorOwnsBody).toBe(true);
  expect(state.overlayCount).toBe(1);
  expect(state.selectionTarget).toBe(true);
});

test('Luft, baggrund og placering uses one full-width device shell instead of legacy narrow grid columns', async ({ page }) => {
  await boot(page);
  await selectNestedElement(page);
  await page.waitForTimeout(120);

  const desktop = page.locator('[data-h18-v0851-device-panel].is-active');
  const shell = page.locator('.h18-v0852-device-shell');
  const legacyGrid = page.locator('.legacy-device-grid');
  await expect(shell).toHaveCount(1);
  await expect(page.locator('.h18-v0851-device-tab')).toHaveCount(2);
  await expect(desktop).toBeVisible();

  const geometry = await page.evaluate(() => {
    const shell = document.querySelector('.h18-v0852-device-shell');
    const grid = document.querySelector('.legacy-device-grid');
    const active = document.querySelector('[data-h18-v0851-device-panel].is-active');
    const tabs = Array.from(document.querySelectorAll('.h18-v0851-device-tab'));
    const input = active?.querySelector('input[type="number"]');
    const legend = active?.querySelector(':scope > legend');
    const rect = (node) => node ? node.getBoundingClientRect() : { width: 0, height: 0 };
    return {
      shellWidth: rect(shell).width,
      gridWidth: rect(grid).width,
      activeWidth: rect(active).width,
      firstTabWidth: rect(tabs[0]).width,
      secondTabWidth: rect(tabs[1]).width,
      inputWidth: rect(input).width,
      legendDisplay: legend ? getComputedStyle(legend).display : ''
    };
  });

  expect(geometry.shellWidth).toBeGreaterThanOrEqual(315);
  expect(Math.abs(geometry.shellWidth - geometry.gridWidth)).toBeLessThanOrEqual(5);
  expect(geometry.activeWidth).toBeGreaterThanOrEqual(315);
  expect(geometry.firstTabWidth).toBeGreaterThan(140);
  expect(geometry.secondTabWidth).toBeGreaterThan(140);
  expect(geometry.inputWidth).toBeGreaterThan(250);
  expect(geometry.legendDisplay).toBe('none');

  await page.locator('.h18-v0851-device-tab').nth(1).click();
  await expect(page.locator('[data-h18-v0851-device-panel]').nth(0)).toBeHidden();
  await expect(page.locator('[data-h18-v0851-device-panel]').nth(1)).toBeVisible();
});
