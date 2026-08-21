const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
const nestingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.css');
const spacingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.js');
const spacingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.css');
const designRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.js');
const designGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-event-guard-v0832.js');
const designCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.css');
const responsiveRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-v0833.js');
const responsiveGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js');
const responsiveCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-v0833.css');
const interactionRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-v0834.js');
const interactionGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js');
const interactionSnapshot = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-snapshot-v0834.js');
const interactionCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-v0834.css');

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

function fields(index, key, type, parent, label, overrides = {}) {
  const v = {
    DesignMode:'Custom',CustomBackgroundColor:'#ffffff',CustomTextColor:'#30382a',CustomHeadingColor:'#30382a',BorderWidthPx:'1',CustomBorderColor:'#c3ae83',
    RadiusPx:'7',RadiusTopLeftPx:'-1',RadiusTopRightPx:'-1',RadiusBottomRightPx:'-1',RadiusBottomLeftPx:'-1',SectionBodyFontFamily:'Global',SectionHeadingFontFamily:'Global',
    BodyFontSizePx:'0',H1FontSizePx:'0',H2FontSizePx:'0',H3FontSizePx:'0',SectionOpacityPercent:'80',ShadowStyle:'Soft',HoverStyleMode:'Inherit',HoverBackgroundColor:'#ffffff',
    HoverTextColor:'#30382a',HoverHeadingColor:'#30382a',HoverBorderColor:'#c3ae83',HoverOpacityPercent:'100',HoverEffect:'None',HoverTransitionMs:'300',
    TransitionPreset:'Inherit',FocusRingStyle:'Global',FocusRingColor:'#8b4a2b',FocusRingWidthPx:'3',FocusRingOffsetPx:'2',ActiveEffect:'None',DisabledOpacityPercent:'55',
    LayoutGapPx:'16',MobileLayoutGapPx:'12',LayoutColumns:'1',MobileLayoutColumns:'1',LayoutDirection:'Column',LayoutAlign:'Stretch',
    ...overrides
  };
  const sel = (name, opts, css='') => `<select class="legacy-field ${css}" name="Sections[${index}][${name}]">${opts.map(x => `<option value="${x}"${String(v[name])===x?' selected':''}>${x}</option>`).join('')}</select>`;
  const inp = (name, typeName='number', css='') => `<input class="legacy-field ${css}" type="${typeName}" name="Sections[${index}][${name}]" value="${v[name]}">`;
  return `<input class="h18-page-section-key" name="Sections[${index}][Key]" value="${key}">
    <input class="h18-page-section-type" name="Sections[${index}][Type]" value="${type}">
    <input class="h18-section-navigator-label" name="Sections[${index}][NavigatorLabel]" value="${label}">
    <input class="h18-layout-parent-key" name="Sections[${index}][LayoutParentKey]" value="${parent}">
    <input class="h18-page-section-order" name="Sections[${index}][Order]" value="${index * 10}">
    ${sel('DesignMode',['Global','Custom'],'h18-section-design-mode')}${inp('CustomBackgroundColor','color')}${inp('CustomTextColor','color')}${inp('CustomHeadingColor','color')}
    ${inp('BorderWidthPx')}${inp('CustomBorderColor','color')}${inp('RadiusPx')}${inp('RadiusTopLeftPx')}${inp('RadiusTopRightPx')}${inp('RadiusBottomRightPx')}${inp('RadiusBottomLeftPx')}
    ${sel('SectionBodyFontFamily',fonts)}${sel('SectionHeadingFontFamily',fonts)}${inp('BodyFontSizePx')}${inp('H1FontSizePx')}${inp('H2FontSizePx')}${inp('H3FontSizePx')}
    ${inp('SectionOpacityPercent')}${sel('ShadowStyle',shadows)}${sel('HoverStyleMode',['Inherit','Custom'],'h18-hover-style-mode')}
    ${inp('HoverBackgroundColor','color')}${inp('HoverTextColor','color')}${inp('HoverHeadingColor','color')}${inp('HoverBorderColor','color')}${inp('HoverOpacityPercent')}${sel('HoverEffect',hoverEffects)}${inp('HoverTransitionMs')}
    ${sel('TransitionPreset',transitions)}${sel('FocusRingStyle',focusStyles)}${inp('FocusRingColor','color')}${inp('FocusRingWidthPx')}${inp('FocusRingOffsetPx')}${sel('ActiveEffect',activeEffects)}${inp('DisabledOpacityPercent')}
    ${inp('LayoutGapPx')}${inp('MobileLayoutGapPx')}${inp('LayoutColumns')}${inp('MobileLayoutColumns')}${sel('LayoutDirection',['Row','Column'])}${sel('LayoutAlign',['Start','Center','End','Stretch'])}`;
}

function row(index, key, type, parent, label, selected = false, overrides = {}) {
  return `<section id="row-${key}" class="h18-page-section-row${selected ? ' is-selected' : ''}" data-section-type="${type}" data-section-index="${index}">
    <header class="h18-page-section-header">${label}</header>
    <div class="h18-canvas-preview"><h3 class="h18-canvas-preview-title">${label}</h3><div class="base-preview">${key}</div></div>
    <div class="h18-page-section-body">${fields(index,key,type,parent,label,overrides)}</div>
  </section>`;
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><head><style>
    #h18-page-sections-sortable{width:820px}.h18-page-section-row{display:block;width:760px;margin:6px;padding:8px}.h18-canvas-preview{min-height:80px;padding:8px}
  </style></head><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="hjem">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div class="h18-builder-canvas" data-canvas-device="desktop" data-canvas-state="normal"></div>
      <div id="h18-page-sections-sortable">
        ${row(1,'auto-1','grid','','Auto-kasser',false,{LayoutGapPx:'16'})}
        ${row(2,'box-a','container','auto-1','Kasse',true,{LayoutGapPx:'12',CustomBackgroundColor:'#f6f2e8'})}
        ${row(3,'box-b','container','box-a','Kasse',false,{LayoutGapPx:'10',CustomBackgroundColor:'#eeeeee'})}
        ${row(4,'text-1','text','box-a','Tekst',false,{CustomBackgroundColor:'#ffffff'})}
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(({ map, fonts, shadows, hoverEffects, transitions, focusStyles, activeEffects }) => {
    window.H18LegoSpacingV0831 = { version:'0.8.31', schemaVersion:2, pages:{}, limits:{desktop:160,tablet:160,mobile:120} };
    window.H18LegoDesignV0832 = { version:'0.8.32', schemaVersion:2, fieldMap:map, fonts, shadows, hoverEffects };
    window.H18LegoResponsiveDesignV0833 = { version:'0.8.33', schemaVersion:1, pages:{}, fieldMap:map, fonts, shadows, hoverEffects };
    window.H18LegoInteractionStatesV0834 = { version:'0.8.34', schemaVersion:1, pages:{}, transitionPresets:transitions, focusStyles, activeEffects };
    window.__v0835 = { spacing:0, responsive:0, interaction:0, legacy:0 };
    const $ = window.jQuery;
    $('#h18-page-editor-form').on('input', '.h18-lego-spacing-state-json', () => { window.__v0835.spacing += 1; });
    $('#h18-page-editor-form').on('input', '.h18-lego-responsive-design-state-json', () => { window.__v0835.responsive += 1; });
    $('#h18-page-editor-form').on('input', '.h18-lego-interaction-states-state-json', () => { window.__v0835.interaction += 1; });
    $('#h18-page-editor-form').on('input change', '.legacy-field', () => { window.__v0835.legacy += 1; });
  }, { map:fieldMap, fonts, shadows, hoverEffects, transitions, focusStyles, activeEffects });

  for (const css of [nestingCss, spacingCss, designCss, responsiveCss, interactionCss]) await page.addStyleTag({ path: css });
  await page.addScriptTag({ path: spacingRuntime });
  await page.addScriptTag({ path: designRuntime });
  await page.addScriptTag({ path: designGuard });
  await page.addScriptTag({ path: responsiveGuard });
  await page.addScriptTag({ path: responsiveRuntime });
  await page.addScriptTag({ path: interactionGuard });
  await page.addScriptTag({ path: interactionRuntime });
  await page.addScriptTag({ path: interactionSnapshot });
  await page.addScriptTag({ path: nestingRuntime });

  await expect(page.locator('#h18-ud-lego-spacing-panel')).toBeVisible();
  await expect(page.locator('#h18-ud-lego-responsive-design-panel')).toBeVisible();
  await expect(page.locator('#h18-ud-lego-interaction-states-panel')).toBeVisible();
  await expect(page.locator('#h18-page-sections-sortable')).toHaveAttribute('data-h18-v0815-kasse-runtime','1');
}

async function setDevice(page, device) {
  await page.locator('.h18-builder-canvas').evaluate((n,d) => n.setAttribute('data-canvas-device', d), device);
  const label = device === 'mobile' ? 'Mobil' : device.charAt(0).toUpperCase()+device.slice(1);
  await expect(page.locator('#h18-ud-lego-responsive-design-panel .h18-rd-tab.is-active')).toHaveText(label);
  await expect(page.locator('#h18-ud-lego-interaction-states-panel .h18-i-tab.is-active')).toHaveText(label);
}

async function setPreviewState(page, state) {
  await page.locator('.h18-builder-canvas').evaluate((n,s) => n.setAttribute('data-canvas-state',s), state);
  await expect(page.locator('#row-box-a')).toHaveAttribute('data-h18-interaction-preview-state',state);
}

test('nested Auto-kasser -> Kasse -> Kasse + element stays one parent/child model', async ({ page }) => {
  await boot(page);
  await expect(page.locator('#row-box-a .h18-layout-parent-key')).toHaveValue('auto-1');
  await expect(page.locator('#row-box-b .h18-layout-parent-key')).toHaveValue('box-a');
  await expect(page.locator('#row-text-1 .h18-layout-parent-key')).toHaveValue('box-a');
  await expect(page.locator('#row-auto-1 .h18-v0811-auto-box[data-h18-v0811-box="box-a"]')).toHaveCount(1);
  await expect(page.locator('#row-box-a .h18-v0811-child-card[data-h18-v0811-child="box-b"]')).toHaveCount(1);
  await expect(page.locator('#row-box-a .h18-v0811-child-card[data-h18-v0811-child="text-1"]')).toHaveCount(1);
  await expect(page.locator('#row-box-a')).toHaveAttribute('data-h18-v0811-child-source','1');
  await expect(page.locator('#row-box-b')).toHaveAttribute('data-h18-v0811-child-source','1');
  await expect(page.locator('#row-text-1')).toHaveAttribute('data-h18-v0811-child-source','1');
});

test('spacing responsive design and interaction state stay independent on the same nested Kasse', async ({ page }) => {
  await boot(page);
  await setDevice(page,'tablet');
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-inherit-device="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-inherit="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-inherit="Tablet"]').uncheck();
  await page.evaluate(() => { window.__v0835 = { spacing:0, responsive:0, interaction:0, legacy:0 }; });

  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Tablet.Gap.X"]').fill('27');
  expect(await page.evaluate(() => window.__v0835)).toEqual({ spacing:1, responsive:0, interaction:0, legacy:0 });

  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Radius.All"]').fill('18');
  expect(await page.evaluate(() => window.__v0835)).toEqual({ spacing:1, responsive:1, interaction:0, legacy:0 });

  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-device-panel="Tablet"] [data-h18-i-path="Active.Effect"]').selectOption('ScaleDown');
  expect(await page.evaluate(() => window.__v0835)).toEqual({ spacing:1, responsive:1, interaction:1, legacy:0 });

  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-device-panel="Tablet"] [data-h18-i-path="Disabled.Opacity"]').fill('42');
  expect(await page.evaluate(() => window.__v0835)).toEqual({ spacing:1, responsive:1, interaction:2, legacy:0 });

  await expect.poll(async () => page.locator('#row-box-a').evaluate(n => n.style.getPropertyValue('--h18-lego-tablet-gap-x'))).toBe('27px');
  await expect(page.locator('#row-box-a .h18-canvas-preview').first()).toHaveCSS('border-radius','18px');
  await setPreviewState(page,'active');
  await expect.poll(async () => page.locator('#row-box-a .h18-canvas-preview').first().evaluate(n => n.style.transform)).toContain('0.97');
  await setPreviewState(page,'disabled');
  await expect.poll(async () => page.locator('#row-box-a .h18-canvas-preview').first().evaluate(n => Number(getComputedStyle(n).opacity))).toBeCloseTo(0.336,2);
});

test('one combined history-style DOM restore rehydrates spacing design states and nested composition', async ({ page }) => {
  await boot(page);
  const snapshot = await page.locator('#h18-page-sections-sortable').evaluate(n => n.innerHTML);
  await setDevice(page,'tablet');
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-inherit-device="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Tablet.Margin.X"]').fill('15');
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-inherit="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Colors.Background"]').evaluate(el => { el.value='#335577'; el.dispatchEvent(new Event('input',{bubbles:true})); });
  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-inherit="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Style"]').selectOption('Custom');
  await page.locator('#h18-ud-lego-interaction-states-panel [data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Color"]').fill('#ff0000');

  await expect.poll(async () => page.locator('#row-box-a').evaluate(n => n.style.getPropertyValue('--h18-lego-tablet-margin-x'))).toBe('15px');
  await expect(page.locator('#row-box-a .h18-canvas-preview').first()).toHaveCSS('background-color','rgb(51, 85, 119)');
  await setPreviewState(page,'focus');
  await expect.poll(async () => page.locator('#row-box-a .h18-canvas-preview').first().evaluate(n => getComputedStyle(n).boxShadow)).toContain('255, 0, 0');

  await page.locator('#h18-page-sections-sortable').evaluate((n,html) => { n.innerHTML = html; }, snapshot);

  await expect.poll(async () => page.evaluate(() => window.__h18LegoResponsiveDesignV0833.stateForKey('box-a').Tablet.InheritDesktop)).toBe(true);
  await expect.poll(async () => page.evaluate(() => window.__h18LegoInteractionStatesV0834.stateForKey('box-a').Tablet.HasOverride)).toBe(false);
  await expect.poll(async () => page.locator('#row-box-a').evaluate(n => n.style.getPropertyValue('--h18-lego-tablet-margin-x'))).toBe('0px');
  await expect(page.locator('#row-box-a .h18-v0811-child-card[data-h18-v0811-child="box-b"]')).toHaveCount(1);
  await expect(page.locator('#row-auto-1 .h18-v0811-auto-box[data-h18-v0811-box="box-a"]')).toHaveCount(1);
});
