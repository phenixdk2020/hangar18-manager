const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const designRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.js');
const designGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-event-guard-v0832.js');
const responsiveRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-v0833.js');
const responsiveGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js');
const interactionRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-v0834.js');
const interactionGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js');
const interactionSnapshot = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-snapshot-v0834.js');
const primaryRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-primary-view-v0836.js');

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

function sel(name, values, current) {
  return `<select class="legacy-field" name="Sections[1][${name}]">${values.map(v => `<option value="${v}"${v===current?' selected':''}>${v}</option>`).join('')}</select>`;
}
function inp(name, value, type='number') {
  return `<input class="legacy-field" type="${type}" name="Sections[1][${name}]" value="${value}">`;
}
function legacyFields() {
  return `<input class="h18-page-section-key" name="Sections[1][Key]" value="box-a"><input class="h18-page-section-type" name="Sections[1][Type]" value="container">
    ${sel('DesignMode',['Global','Custom'],'Custom')}${inp('CustomBackgroundColor','#ffffff','color')}${inp('CustomTextColor','#30382a','color')}${inp('CustomHeadingColor','#30382a','color')}
    ${inp('BorderWidthPx','1')}${inp('CustomBorderColor','#c3ae83','color')}${inp('RadiusPx','7')}${inp('RadiusTopLeftPx','-1')}${inp('RadiusTopRightPx','-1')}${inp('RadiusBottomRightPx','-1')}${inp('RadiusBottomLeftPx','-1')}
    ${sel('SectionBodyFontFamily',fonts,'Global')}${sel('SectionHeadingFontFamily',fonts,'Global')}${inp('BodyFontSizePx','0')}${inp('H1FontSizePx','0')}${inp('H2FontSizePx','0')}${inp('H3FontSizePx','0')}
    ${inp('SectionOpacityPercent','80')}${sel('ShadowStyle',shadows,'Soft')}${sel('HoverStyleMode',['Inherit','Custom'],'Inherit')}
    ${inp('HoverBackgroundColor','#ffffff','color')}${inp('HoverTextColor','#30382a','color')}${inp('HoverHeadingColor','#30382a','color')}${inp('HoverBorderColor','#c3ae83','color')}${inp('HoverOpacityPercent','100')}${sel('HoverEffect',hoverEffects,'None')}${inp('HoverTransitionMs','300')}
    ${sel('TransitionPreset',transitions,'Inherit')}${sel('FocusRingStyle',focusStyles,'Global')}${inp('FocusRingColor','#8b4a2b','color')}${inp('FocusRingWidthPx','3')}${inp('FocusRingOffsetPx','2')}${sel('ActiveEffect',activeEffects,'None')}${inp('DisabledOpacityPercent','55')}
    ${inp('TabletPaddingPx','12')}${inp('TabletHorizontalPaddingPx','10')}${inp('TabletTopSpacingPx','6')}${inp('TabletBottomSpacingPx','6')}${inp('TabletWidthPercent','100')}${inp('TabletMinHeightPx','0')}`;
}
function directBar() {
  return `<div class="h18-canvas-direct-controls" data-canvas-state="normal">
    <strong class="h18-canvas-direct-title">Direkte design</strong>
    <div class="h18-canvas-quick-ranges">
      <label class="h18-canvas-quick-range"><span>Indvendig</span><input type="range" min="0" max="100" value="12" data-canvas-quick-field="TabletPaddingPx"><output>12 px</output></label>
      <label class="h18-canvas-quick-range"><span>Radius</span><input type="range" min="0" max="60" value="7" data-canvas-quick-field="RadiusPx"><output>7 px</output></label>
      <label class="h18-canvas-quick-range"><span>Opacity</span><input type="range" min="0" max="100" value="80" data-canvas-quick-field="SectionOpacityPercent"><output>80%</output></label>
    </div>
    <div class="h18-canvas-quick-colors" data-canvas-color-state="normal" data-canvas-border="#c3ae83" data-canvas-opacity="80">
      <label class="h18-canvas-quick-color"><span>Baggrund</span><input type="color" value="#ffffff" data-canvas-color-role="background"></label>
      <label class="h18-canvas-quick-color"><span>Tekst</span><input type="color" value="#30382a" data-canvas-color-role="text"></label>
      <label class="h18-canvas-quick-color"><span>Overskrift</span><input type="color" value="#30382a" data-canvas-color-role="heading"></label>
    </div>
  </div>`;
}

async function boot(page, device='desktop', state='normal') {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="hjem">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div class="h18-builder-canvas" data-canvas-device="${device}" data-canvas-state="${state}"></div>
      <div id="h18-page-sections-sortable"><section id="row-box-a" class="h18-page-section-row is-selected" data-section-type="container">
        <div class="h18-canvas-preview">${directBar()}</div><div class="h18-page-section-body">${legacyFields()}</div>
      </section></div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(({ map, fonts, shadows, hoverEffects, transitions, focusStyles, activeEffects }) => {
    window.H18LegoDesignV0832 = {version:'0.8.32',schemaVersion:2,fieldMap:map,fonts,shadows,hoverEffects};
    window.H18LegoResponsiveDesignV0833 = {version:'0.8.33',schemaVersion:1,pages:{},fieldMap:map,fonts,shadows,hoverEffects};
    window.H18LegoInteractionStatesV0834 = {version:'0.8.34',schemaVersion:1,pages:{},transitionPresets:transitions,focusStyles,activeEffects};
    window.__v0836 = { legacyDirect:0, responsive:0, interaction:0, legacyField:0 };
    const $ = window.jQuery;
    // Simulates the old admin.js direct handler. v0.8.36 capture must block it for canonical proxy controls.
    $(document).on('input', '.h18-canvas-direct-controls [data-canvas-quick-field],.h18-canvas-direct-controls [data-canvas-color-role]', () => { window.__v0836.legacyDirect += 1; });
    $('#h18-page-editor-form').on('input', '.h18-lego-responsive-design-state-json', () => { window.__v0836.responsive += 1; });
    $('#h18-page-editor-form').on('input', '.h18-lego-interaction-states-state-json', () => { window.__v0836.interaction += 1; });
    $('#h18-page-editor-form').on('input change', '.legacy-field', () => { window.__v0836.legacyField += 1; });
  }, {map:fieldMap,fonts,shadows,hoverEffects,transitions,focusStyles,activeEffects});
  await page.addScriptTag({ path: designRuntime });
  await page.addScriptTag({ path: designGuard });
  await page.addScriptTag({ path: responsiveGuard });
  await page.addScriptTag({ path: responsiveRuntime });
  await page.addScriptTag({ path: interactionGuard });
  await page.addScriptTag({ path: interactionRuntime });
  await page.addScriptTag({ path: interactionSnapshot });
  await page.addScriptTag({ path: primaryRuntime });
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-primary-view-runtime','0.8.36');
  await expect(page.locator('.h18-canvas-preview > .h18-canvas-direct-controls')).toHaveAttribute('data-h18-v0836-primary-view','1');
  await expect(page.locator('.h18-canvas-direct-title')).toHaveText('Direkte design · LEGO');
}

async function directInput(page, selector, value) {
  await page.locator(selector).evaluate((el,v) => { el.value=String(v); el.dispatchEvent(new Event('input',{bubbles:true})); }, value);
  await page.waitForTimeout(120);
}

test('Desktop direct background is a canonical LEGO proxy with no legacy duplicate event', async ({page}) => {
  await boot(page,'desktop','normal');
  await directInput(page,'[data-canvas-color-role="background"]','#224466');
  await expect(page.locator('#row-box-a [name$="[CustomBackgroundColor]"]')).toHaveValue('#224466');
  expect(await page.evaluate(() => window.__v0836.legacyDirect)).toBe(0);
  expect(await page.evaluate(() => window.__v0836.legacyField)).toBe(1);
  expect(await page.evaluate(() => window.__v0836.responsive)).toBe(0);
});

test('Tablet inherited Radius becomes one responsive override checkpoint from Direct Design', async ({page}) => {
  await boot(page,'tablet','normal');
  await page.evaluate(() => { window.__v0836 = {legacyDirect:0,responsive:0,interaction:0,legacyField:0}; });
  await directInput(page,'[data-canvas-quick-field="RadiusPx"]','18');
  const state = await page.evaluate(() => window.__h18LegoResponsiveDesignV0833.stateForKey('box-a'));
  expect(state.Tablet.InheritDesktop).toBe(false);
  expect(state.Tablet.HasOverride).toBe(true);
  expect(state.Tablet.Design.Radius.All).toBe(18);
  expect(await page.evaluate(() => window.__v0836)).toEqual({legacyDirect:0,responsive:1,interaction:0,legacyField:0});
});

test('Mobile inherited Hover background routes to responsive Hover custom as one checkpoint', async ({page}) => {
  await boot(page,'mobile','hover');
  await page.evaluate(() => { window.__v0836 = {legacyDirect:0,responsive:0,interaction:0,legacyField:0}; });
  await directInput(page,'[data-canvas-color-role="background"]','#335577');
  const state = await page.evaluate(() => window.__h18LegoResponsiveDesignV0833.stateForKey('box-a'));
  expect(state.Mobile.InheritDesktop).toBe(false);
  expect(state.Mobile.Design.States.Hover.Mode).toBe('Custom');
  expect(state.Mobile.Design.States.Hover.Background).toBe('#335577');
  expect(await page.evaluate(() => window.__v0836)).toEqual({legacyDirect:0,responsive:1,interaction:0,legacyField:0});
});

test('Tablet Disabled opacity routes to interaction state instead of normal design opacity', async ({page}) => {
  await boot(page,'tablet','disabled');
  await page.evaluate(() => { window.__v0836 = {legacyDirect:0,responsive:0,interaction:0,legacyField:0}; });
  await directInput(page,'[data-canvas-quick-field="SectionOpacityPercent"]','42');
  const interaction = await page.evaluate(() => window.__h18LegoInteractionStatesV0834.stateForKey('box-a'));
  const responsive = await page.evaluate(() => window.__h18LegoResponsiveDesignV0833.stateForKey('box-a'));
  expect(interaction.Tablet.HasOverride).toBe(true);
  expect(interaction.Tablet.Interaction.Disabled.Opacity).toBe(42);
  expect(responsive.Tablet.InheritDesktop).toBe(true);
  expect(await page.locator('#row-box-a').getAttribute('data-h18-interaction-tablet-snapshot')).toBe('1');
  expect(await page.evaluate(() => window.__v0836)).toEqual({legacyDirect:0,responsive:0,interaction:1,legacyField:0});
});

test('unique layout quick control remains legacy-owned and is not swallowed by LEGO bridge', async ({page}) => {
  await boot(page,'tablet','normal');
  await page.evaluate(() => { window.__v0836 = {legacyDirect:0,responsive:0,interaction:0,legacyField:0}; });
  await expect(page.locator('[data-canvas-quick-field="TabletPaddingPx"]')).toHaveAttribute('data-h18-v0836-layout-control','1');
  await directInput(page,'[data-canvas-quick-field="TabletPaddingPx"]','24');
  expect(await page.evaluate(() => window.__v0836.legacyDirect)).toBe(1);
  expect(await page.evaluate(() => window.__v0836.responsive)).toBe(0);
  expect(await page.evaluate(() => window.__v0836.interaction)).toBe(0);
});
