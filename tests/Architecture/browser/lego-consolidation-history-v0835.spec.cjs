const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const spacingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.js');
const designRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.js');
const designGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-event-guard-v0832.js');
const responsiveRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-v0833.js');
const responsiveGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js');
const interactionRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-v0834.js');
const interactionGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js');
const interactionSnapshot = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-snapshot-v0834.js');

const fonts = ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'];
const shadows = ['None','Soft','Medium','Strong'];
const hoverEffects = ['None','Lift','Scale','Shadow'];
const transitions = ['Inherit','Fast','Normal','Slow','Custom'];
const focusStyles = ['Global','Custom','None'];
const activeEffects = ['None','Press','ScaleDown'];
const fieldMap = {
  Mode:'DesignMode','Colors.Background':'CustomBackgroundColor','Colors.Text':'CustomTextColor','Colors.Heading':'CustomHeadingColor',
  'Border.Width':'BorderWidthPx','Border.Color':'CustomBorderColor','Radius.All':'RadiusPx','Radius.TopLeft':'RadiusTopLeftPx',
  'Radius.TopRight':'RadiusTopRightPx','Radius.BottomRight':'RadiusBottomRightPx','Radius.BottomLeft':'RadiusBottomLeftPx',
  'Typography.BodyFont':'SectionBodyFontFamily','Typography.HeadingFont':'SectionHeadingFontFamily','Typography.BodySize':'BodyFontSizePx',
  'Typography.H1Size':'H1FontSizePx','Typography.H2Size':'H2FontSizePx','Typography.H3Size':'H3FontSizePx','Effects.Opacity':'SectionOpacityPercent',
  'Effects.Shadow':'ShadowStyle','States.Hover.Mode':'HoverStyleMode','States.Hover.Background':'HoverBackgroundColor',
  'States.Hover.Text':'HoverTextColor','States.Hover.Heading':'HoverHeadingColor','States.Hover.Border':'HoverBorderColor',
  'States.Hover.Opacity':'HoverOpacityPercent','States.Hover.Effect':'HoverEffect','States.Hover.TransitionMs':'HoverTransitionMs'
};

function select(name, values, current) {
  return `<select class="legacy-field" name="Sections[2][${name}]">${values.map(v => `<option value="${v}"${v===current?' selected':''}>${v}</option>`).join('')}</select>`;
}
function input(name, value, type='number') {
  return `<input class="legacy-field" type="${type}" name="Sections[2][${name}]" value="${value}">`;
}
function boxFields() {
  return `<input class="h18-page-section-key" name="Sections[2][Key]" value="box-a">
    <input class="h18-page-section-type" name="Sections[2][Type]" value="container">
    <input class="h18-section-navigator-label" name="Sections[2][NavigatorLabel]" value="Kasse">
    <input class="h18-layout-parent-key" name="Sections[2][LayoutParentKey]" value="auto-1">
    ${select('DesignMode',['Global','Custom'],'Custom')}${input('CustomBackgroundColor','#f6f2e8','color')}${input('CustomTextColor','#30382a','color')}${input('CustomHeadingColor','#30382a','color')}
    ${input('BorderWidthPx','1')}${input('CustomBorderColor','#c3ae83','color')}${input('RadiusPx','7')}${input('RadiusTopLeftPx','-1')}${input('RadiusTopRightPx','-1')}${input('RadiusBottomRightPx','-1')}${input('RadiusBottomLeftPx','-1')}
    ${select('SectionBodyFontFamily',fonts,'Global')}${select('SectionHeadingFontFamily',fonts,'Global')}${input('BodyFontSizePx','0')}${input('H1FontSizePx','0')}${input('H2FontSizePx','0')}${input('H3FontSizePx','0')}
    ${input('SectionOpacityPercent','80')}${select('ShadowStyle',shadows,'Soft')}${select('HoverStyleMode',['Inherit','Custom'],'Inherit')}
    ${input('HoverBackgroundColor','#ffffff','color')}${input('HoverTextColor','#30382a','color')}${input('HoverHeadingColor','#30382a','color')}${input('HoverBorderColor','#c3ae83','color')}${input('HoverOpacityPercent','100')}${select('HoverEffect',hoverEffects,'None')}${input('HoverTransitionMs','300')}
    ${select('TransitionPreset',transitions,'Inherit')}${select('FocusRingStyle',focusStyles,'Global')}${input('FocusRingColor','#8b4a2b','color')}${input('FocusRingWidthPx','3')}${input('FocusRingOffsetPx','2')}${select('ActiveEffect',activeEffects,'None')}${input('DisabledOpacityPercent','55')}
    ${input('LayoutGapPx','12')}${input('MobileLayoutGapPx','10')}`;
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="hjem">
      <button id="h18-editor-undo" type="button">Fortryd</button><button id="h18-editor-redo" type="button">Gendan</button>
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div class="h18-builder-canvas" data-canvas-device="desktop" data-canvas-state="normal"></div>
      <div id="h18-page-sections-sortable">
        <section id="row-auto-1" class="h18-page-section-row" data-section-type="grid"><input class="h18-page-section-key" value="auto-1"><input class="h18-page-section-type" value="grid"><input class="h18-layout-parent-key" value=""><div class="h18-canvas-preview">Auto</div></section>
        <section id="row-box-a" class="h18-page-section-row is-selected" data-section-type="container"><header class="h18-page-section-header">Kasse</header><div class="h18-canvas-preview">Kasse</div><div class="h18-page-section-body">${boxFields()}</div></section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(({ map, fonts, shadows, hoverEffects, transitions, focusStyles, activeEffects }) => {
    window.H18LegoSpacingV0831 = { version:'0.8.31', schemaVersion:2, pages:{}, limits:{desktop:160,tablet:160,mobile:120} };
    window.H18LegoDesignV0832 = { version:'0.8.32', schemaVersion:2, fieldMap:map, fonts, shadows, hoverEffects };
    window.H18LegoResponsiveDesignV0833 = { version:'0.8.33', schemaVersion:1, pages:{}, fieldMap:map, fonts, shadows, hoverEffects };
    window.H18LegoInteractionStatesV0834 = { version:'0.8.34', schemaVersion:1, pages:{}, transitionPresets:transitions, focusStyles, activeEffects };
  }, { map:fieldMap, fonts, shadows, hoverEffects, transitions, focusStyles, activeEffects });

  await page.addScriptTag({ path: spacingRuntime });
  await page.addScriptTag({ path: designRuntime });
  await page.addScriptTag({ path: designGuard });
  await page.addScriptTag({ path: responsiveGuard });
  await page.addScriptTag({ path: responsiveRuntime });
  await page.addScriptTag({ path: interactionGuard });
  await page.addScriptTag({ path: interactionRuntime });
  await page.addScriptTag({ path: interactionSnapshot });

  await expect(page.locator('#h18-ud-lego-spacing-panel')).toBeVisible();
  await expect(page.locator('#h18-ud-lego-responsive-design-panel')).toBeVisible();
  await expect(page.locator('#h18-ud-lego-interaction-states-panel')).toBeVisible();
}

async function tablet(page) {
  await page.locator('.h18-builder-canvas').evaluate(n => n.setAttribute('data-canvas-device','tablet'));
  await expect(page.locator('#h18-ud-lego-responsive-design-panel .h18-rd-tab.is-active')).toHaveText('Tablet');
  await expect(page.locator('#h18-ud-lego-interaction-states-panel .h18-i-tab.is-active')).toHaveText('Tablet');
}

async function installHistory(page) {
  await page.evaluate(() => {
    const $ = window.jQuery;
    const sections = document.getElementById('h18-page-sections-sortable');
    let entries = [];
    let index = -1;
    let timer = null;

    function canonicalHtml() {
      const clone = $(sections).clone(false, false).get(0);
      clone.querySelectorAll('.is-selected').forEach(n => n.classList.remove('is-selected'));
      clone.querySelectorAll('input').forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
          if (input.checked) input.setAttribute('checked','checked'); else input.removeAttribute('checked');
        } else input.setAttribute('value', String(input.value == null ? '' : input.value));
      });
      clone.querySelectorAll('select').forEach(select => {
        const values = Array.from(select.selectedOptions).map(o => String(o.value));
        Array.from(select.options).forEach(o => values.includes(String(o.value)) ? o.setAttribute('selected','selected') : o.removeAttribute('selected'));
      });
      return clone.innerHTML;
    }
    function record() {
      timer = null;
      const html = canonicalHtml();
      if (index >= 0 && entries[index] === html) return;
      if (index < entries.length - 1) entries.splice(index + 1);
      entries.push(html); index = entries.length - 1;
    }
    function schedule() { clearTimeout(timer); timer = setTimeout(record, 60); }
    function flush() { if (!timer) return; clearTimeout(timer); timer = null; record(); }
    function restore(html) {
      sections.innerHTML = html;
      const box = document.getElementById('row-box-a');
      if (box) box.classList.add('is-selected');
    }
    function undo() { flush(); if (index <= 0) return; index -= 1; restore(entries[index]); }
    function redo() { flush(); if (index >= entries.length - 1) return; index += 1; restore(entries[index]); }

    $('#h18-page-editor-form').on('input', '.h18-lego-spacing-state-json,.h18-lego-responsive-design-state-json,.h18-lego-interaction-states-state-json', schedule);
    document.getElementById('h18-editor-undo').addEventListener('click', undo);
    document.getElementById('h18-editor-redo').addEventListener('click', redo);
    window.__v0835History = {
      reset() { clearTimeout(timer); timer = null; entries = []; index = -1; record(); },
      state() { return { index, entries:entries.length }; }
    };
  });
}

async function combined(page) {
  return page.evaluate(() => {
    const $ = window.jQuery;
    const spacing = JSON.parse(String($('#row-box-a .h18-lego-spacing-state-json').val() || '{}'));
    const responsive = window.__h18LegoResponsiveDesignV0833.stateForKey('box-a');
    const interaction = window.__h18LegoInteractionStatesV0834.stateForKey('box-a');
    return {
      parent: String($('#row-box-a .h18-layout-parent-key').val() || ''),
      gap: spacing.Tablet.Gap.X,
      radius: responsive.Tablet.Design.Radius.All,
      active: interaction.Tablet.Interaction.Active.Effect
    };
  });
}

test('spacing design and state Undo Redo one logical action at a time on nested Kasse', async ({ page }) => {
  await boot(page);
  await tablet(page);
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-inherit-device="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-inherit="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-inherit="Tablet"]').uncheck();
  await installHistory(page);
  await page.evaluate(() => window.__v0835History.reset());

  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Tablet.Gap.X"]').fill('27');
  await page.waitForTimeout(100);
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Radius.All"]').fill('18');
  await page.waitForTimeout(100);
  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-device-panel="Tablet"] [data-h18-i-path="Active.Effect"]').selectOption('ScaleDown');
  await page.waitForTimeout(100);
  expect(await combined(page)).toEqual({ parent:'auto-1', gap:27, radius:18, active:'ScaleDown' });
  expect(await page.evaluate(() => window.__v0835History.state())).toEqual({ index:3, entries:4 });

  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  expect(await combined(page)).toEqual({ parent:'auto-1', gap:27, radius:18, active:'None' });
  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  expect(await combined(page)).toEqual({ parent:'auto-1', gap:27, radius:7, active:'None' });
  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  expect(await combined(page)).toEqual({ parent:'auto-1', gap:12, radius:7, active:'None' });

  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  expect(await combined(page)).toEqual({ parent:'auto-1', gap:27, radius:18, active:'ScaleDown' });
});
