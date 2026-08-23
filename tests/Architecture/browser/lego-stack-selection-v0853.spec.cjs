const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const fixesRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-fixes-v0851.js');
const fixesCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-fixes-v0851.css');
const hotfixRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-stack-selection-v0853.js');
const hotfixCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-stack-selection-v0853.css');

function row(index, key, type, parent = '', includeParentOption = true) {
  const option = includeParentOption && parent ? `<option value="${parent}" selected>${parent}</option>` : '';
  return `<section id="row-${key}" class="h18-page-section-row" data-section-type="${type}" data-section-index="${index}" data-key="${key}">
    <div class="h18-canvas-preview">${key}</div>
    <div class="h18-page-section-body">
      <input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
      <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
      <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
      <select class="h18-layout-parent-select"><option value="">Topniveau</option>${option}</select>
      <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
      <input class="h18-section-navigator-label" value="${type === 'grid' ? 'Række- og kolonne-kasse' : key}">
    </div>
  </section>`;
}

async function boot(page, childType = 'image') {
  await page.setContent(`<!doctype html><html><head><style>
    body{margin:0;font-family:Arial,sans-serif}
    #h18-page-editor-form{display:block}
    #h18-page-sections-sortable{display:block}
    .h18-page-section-row{display:block}
    .h18-page-section-row[data-h18-nested-in-box]{display:none}
    .h18-canvas-preview{min-height:60px}
    .h18-builder-canvas{width:780px;min-height:320px;margin:10px}
    .h18-v0811-child-card{position:relative;width:360px;min-height:120px;margin:12px}
    .h18-v0811-child-preview{position:relative;width:100%;height:110px;box-sizing:border-box;background:#fafafa}
  </style></head><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="test-side"></form>
    <div class="h18-builder-canvas" data-canvas-device="desktop">
      <div id="h18-page-sections-sortable">
        ${row(1, 'grid-1', 'grid')}
        ${row(2, 'image-1', 'image', 'grid-1', true)}
        ${row(3, 'new-child', childType, '', false)}
      </div>
      <section id="proxy-image-1" class="h18-v0811-child-card" data-h18-v0811-child="image-1">
        <div class="h18-v0811-child-preview">Første billede</div>
      </section>
      <section id="proxy-new-child" class="h18-v0811-child-card" data-h18-v0811-child="new-child">
        <div class="h18-v0811-child-preview">Nyt element</div>
      </section>
    </div>
    <aside id="h18-page-inspector"><div id="h18-page-inspector-target"></div></aside>
  </body></html>`);

  await page.addStyleTag({ path: fixesCss });
  await page.addStyleTag({ path: hotfixCss });
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    const $ = window.jQuery;
    window.H18LegoFixesV0851 = { pages: {} };
    window.__h18NestingToolsV0840 = { refresh() {} };
    window.__h18LegoResizeV0841 = { refresh() {} };

    // Reproduce WordPress' human-facing parent select synchronization.
    // The newly-created child deliberately has no grid-1 option yet. In
    // v0.8.52 native adoptUnder writes the hidden parent first and then
    // .val('grid-1').change() on this select; jQuery resolves that to null,
    // and this listener therefore clears the canonical hidden ParentKey.
    $(document).on('change', '.h18-layout-parent-select', function () {
      const $row = $(this).closest('.h18-page-section-row');
      if (!$row.length) return;
      $row.find('.h18-layout-parent-key').first().val(String($(this).val() || '')).trigger('change');
    });
  });

  await page.addScriptTag({ path: fixesRuntime });
  await page.addScriptTag({ path: hotfixRuntime });
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-stack-selection-hotfix', '0.8.53');
  await page.waitForTimeout(100);
}

for (const childType of ['image', 'text']) {
  test(`Under creates a vertical stack after transient ParentKey clear for ${childType}`, async ({ page }) => {
    await boot(page, childType);

    const nativeResult = await page.evaluate(() => {
      return window.__h18LegoFixesV0851.adoptUnder('new-child', 'image-1', 'under');
    });
    expect(nativeResult).toBe(true);

    await page.waitForTimeout(850);

    const state = await page.evaluate(() => {
      const row = document.getElementById('row-new-child');
      const hiddenParent = row.querySelector('.h18-layout-parent-key')?.value || '';
      const stackField = row.querySelector('.h18-lego-stack-state-v0851-json');
      let stack = {};
      try { stack = JSON.parse(stackField?.value || '{}'); } catch (_) {}
      return {
        hiddenParent,
        selectParent: row.querySelector('.h18-layout-parent-select')?.value || '',
        stackRootKey: String(stack.StackRootKey || ''),
        stackOrder: Number(stack.StackOrder || 0),
        parentAttr: row.getAttribute('data-h18-nested-in-box') || ''
      };
    });

    expect(state.hiddenParent).toBe('grid-1');
    expect(state.parentAttr).toBe('grid-1');
    // The select may still lack the option; the hidden canonical value must win.
    expect(state.selectParent).toBe('');
    expect(state.stackRootKey).toBe('image-1');
    expect(state.stackOrder).toBeGreaterThan(0);
  });
}

test('clicking a nested element applies a complete direct red selection outline without legacy class injection', async ({ page }) => {
  await boot(page, 'text');

  const preview = page.locator('#proxy-image-1 > .h18-v0811-child-preview');
  await preview.click();
  await page.waitForTimeout(220);

  await expect(preview).toHaveClass(/h18-v0853-selection-target/);
  const geometry = await preview.evaluate((node) => {
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return {
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
      outlineColor: style.outlineColor,
      width: rect.width,
      height: rect.height
    };
  });

  expect(geometry.outlineStyle).toBe('solid');
  expect(geometry.outlineWidth).toBe('2px');
  expect(geometry.width).toBeGreaterThan(100);
  expect(geometry.height).toBeGreaterThan(50);

  // A late unrelated canvas mutation must not make the selected key fall back
  // to another Inspector/Grid key or remove the visible outline.
  await page.evaluate(() => {
    const marker = document.createElement('i');
    marker.className = 'late-layout-mutation';
    document.querySelector('.h18-builder-canvas').appendChild(marker);
  });
  await page.waitForTimeout(300);
  await expect(preview).toHaveClass(/h18-v0853-selection-target/);
});
