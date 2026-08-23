const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const bridgeRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js');
const fixesRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-fixes-v0851.js');
const fixesCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-fixes-v0851.css');
const stackRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-stack-selection-v0853.js');

function body(index, key, type, parent = '') {
  return `<div class="h18-page-section-body">
    <input class="h18-page-section-key" value="${key}">
    <input class="h18-page-section-type" value="${type}">
    <input class="h18-layout-parent-key" value="${parent}">
    <select class="h18-layout-parent-select"><option value="">Topniveau</option></select>
    <input class="h18-page-section-order" value="${index * 10}">
    <input class="h18-section-navigator-label" value="${type === 'grid' ? 'Række- og kolonne-kasse' : key}">
  </div>`;
}

test('LEGO-055 real-like palette Under beats side fallback and survives Inspector key handoff', async ({ page }) => {
  await page.setContent(`<!doctype html><html><head><style>
    body{margin:0;font-family:Arial,sans-serif}
    #h18-page-sections-sortable{position:relative;width:760px;min-height:300px}
    .h18-page-section-row{display:block}
    .h18-page-section-row[data-h18-nested-in-box]{display:none}
    .h18-canvas-preview{min-height:30px}
    .h18-builder-canvas{position:relative;width:760px;min-height:360px}
    #proxy-image{position:relative;width:240px;height:160px;margin:20px}
    #under-zone{position:absolute;left:60px;bottom:0;width:120px;height:40px}
    #right-zone{position:absolute;right:0;bottom:20px;width:80px;height:100px}
    #outside-prompt{min-height:48px;border:1px dashed #999;padding:12px}
  </style></head><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="test-side"></form>
    <div class="h18-builder-canvas" data-canvas-device="desktop">
      <div id="h18-page-sections-sortable">
        <section id="row-grid" class="h18-page-section-row" data-section-type="grid" data-section-index="1" data-key="grid-1">
          <div class="h18-canvas-preview">grid</div>${body(1, 'grid-1', 'grid')}
        </section>
        <section id="row-image" class="h18-page-section-row" data-section-type="image" data-section-index="2" data-key="image-1" data-h18-nested-in-box="grid-1">
          <div class="h18-canvas-preview">image</div>${body(2, 'image-1', 'image', 'grid-1')}
        </section>
        <section id="row-heading" class="h18-page-section-row" data-section-type="heading" data-section-index="3" data-h18-nested-in-box="grid-1">
          <div id="heading-preview" class="h18-canvas-preview">heading</div>
        </section>
      </div>
      <section id="proxy-image" class="h18-v0811-child-card" data-h18-v0811-child="image-1">
        <div class="h18-v0811-child-preview">Billede</div>
        <div id="under-zone" class="h18-v0838-drop-zone is-under" data-h18-v0838-position="under" data-h18-v0838-target="image-1">Under</div>
        <div id="right-zone" class="h18-v0838-drop-zone h18-v0811-side-zone is-right" data-h18-v0838-position="right" data-h18-v0838-target="image-1" data-box="image-1">Højre</div>
      </section>
    </div>
    <aside id="h18-page-inspector"><div id="h18-page-inspector-target">${body(3, 'heading-1', 'heading', 'grid-1')}</div></aside>
    <div id="outside-prompt" class="h18-ud-auto-box-empty-drop">Træk en Kasse ind i Auto-kasser.</div>
  </body></html>`);

  await page.addStyleTag({ path: fixesCss });
  await page.addScriptTag({ path: jqueryRuntime });

  await page.evaluate(() => {
    const $ = window.jQuery;
    window.H18LegoFixesV0851 = { pages: {} };
    window.__h18NestingToolsV0840 = { refresh() {} };
    window.__h18LegoResizeV0841 = { refresh() {} };
    window.__h18LegoSideBySideV0840 = {
      activeSource() { return { Key: '__new_element__', Type: 'image', Mode: 'palette-element' }; }
    };

    $(document).on('change', '.h18-layout-parent-select', function () {
      const $row = $(this).closest('.h18-page-section-row');
      if (!$row.length) return;
      $row.find('.h18-layout-parent-key').first().val(String($(this).val() || '')).trigger('change');
    });

    document.addEventListener('drop', (event) => {
      if (window.__createdNewImage) return;
      const target = event.target;
      if (!target || (target.id !== 'heading-preview' && target.id !== 'right-zone')) return;
      window.__createdNewImage = true;

      // Real editor handoff: heading controls return from Inspector during the
      // same repaint in which the new row is inserted before heading.
      const heading = document.getElementById('row-heading');
      const headingBody = document.querySelector('#h18-page-inspector-target .h18-page-section-body');
      if (headingBody) heading.appendChild(headingBody);

      const newRow = document.createElement('section');
      newRow.id = 'row-new-image';
      newRow.className = 'h18-page-section-row is-selected';
      newRow.setAttribute('data-section-type', 'image');
      newRow.setAttribute('data-section-index', '4');
      newRow.setAttribute('data-key', 'image-2');
      newRow.setAttribute('data-h18-nested-in-box', 'grid-1');
      newRow.innerHTML = `<div class="h18-canvas-preview">image-2</div>${body(4, 'image-2', 'image', 'grid-1')}`;
      heading.parentNode.insertBefore(newRow, heading);

      // Then move the new selected row body into Inspector, as the live editor does.
      const newBody = newRow.querySelector('.h18-page-section-body');
      document.getElementById('h18-page-inspector-target').replaceChildren(newBody);
    }, false);
  });

  await page.addScriptTag({ path: bridgeRuntime });
  await page.addScriptTag({ path: fixesRuntime });
  await page.addScriptTag({ path: stackRuntime });

  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-palette-nested-drop-stability', '0.8.55');

  // Coordinates deliberately hit both the visual Under zone and the right-side
  // hitbox. Under must win; old behavior falls through to side-by-side / 4-4-4.
  await page.locator('#right-zone').evaluate((node) => {
    const event = new Event('drop', { bubbles: true, cancelable: true, composed: true });
    Object.defineProperty(event, 'clientX', { value: 170 });
    Object.defineProperty(event, 'clientY', { value: 135 });
    node.dispatchEvent(event);
  });

  await page.waitForTimeout(1600);

  const state = await page.evaluate(() => {
    const row = document.getElementById('row-new-image');
    const body = document.querySelector('#h18-page-inspector-target .h18-page-section-body');
    const stackField = body?.querySelector('.h18-lego-stack-state-v0851-json') || row?.querySelector('.h18-lego-stack-state-v0851-json');
    let stack = {};
    try { stack = JSON.parse(stackField?.value || '{}'); } catch (_) {}
    const promptStyle = getComputedStyle(document.getElementById('outside-prompt'));
    return {
      created: !!row,
      parent: body?.querySelector('.h18-layout-parent-key')?.value || row?.querySelector('.h18-layout-parent-key')?.value || '',
      stackRootKey: String(stack.StackRootKey || ''),
      stackOrder: Number(stack.StackOrder || 0),
      rowOrder: Array.from(document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row')).map((node) => node.id),
      promptWidth: promptStyle.width,
      promptHeight: promptStyle.height,
      promptBorderWidth: promptStyle.borderTopWidth,
      promptFontSize: promptStyle.fontSize
    };
  });

  expect(state.created).toBe(true);
  expect(state.parent).toBe('grid-1');
  expect(state.stackRootKey).toBe('image-1');
  expect(state.stackOrder).toBeGreaterThan(0);
  expect(state.rowOrder).toEqual(['row-grid', 'row-image', 'row-new-image', 'row-heading']);
  expect(state.promptWidth).toBe('0px');
  expect(state.promptHeight).toBe('0px');
  expect(state.promptBorderWidth).toBe('0px');
  expect(state.promptFontSize).toBe('0px');
});
