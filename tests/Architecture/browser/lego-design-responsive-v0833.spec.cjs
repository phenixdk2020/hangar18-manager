const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const spacingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.js');
const spacingCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-spacing-v0831.css');
const designRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.js');
const designGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-event-guard-v0832.js');
const designCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.css');
const responsiveRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-v0833.js');
const responsiveGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js');
const responsiveCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-responsive-v0833.css');

const fonts = ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'];
const shadows = ['None','Soft','Medium','Strong'];
const hoverEffects = ['None','Lift','Scale','Shadow'];
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

function fields(index, key, overrides = {}) {
  const v = {
    DesignMode:'Global',CustomBackgroundColor:'#ffffff',CustomTextColor:'#30382a',CustomHeadingColor:'#30382a',BorderWidthPx:'0',CustomBorderColor:'#c3ae83',
    RadiusPx:'7',RadiusTopLeftPx:'-1',RadiusTopRightPx:'-1',RadiusBottomRightPx:'-1',RadiusBottomLeftPx:'-1',SectionBodyFontFamily:'Global',SectionHeadingFontFamily:'Global',
    BodyFontSizePx:'0',H1FontSizePx:'0',H2FontSizePx:'0',H3FontSizePx:'0',SectionOpacityPercent:'100',ShadowStyle:'None',HoverStyleMode:'Inherit',HoverBackgroundColor:'#ffffff',
    HoverTextColor:'#30382a',HoverHeadingColor:'#30382a',HoverBorderColor:'#c3ae83',HoverOpacityPercent:'100',HoverEffect:'None',HoverTransitionMs:'220',LayoutGapPx:'16',MobileLayoutGapPx:'12',...overrides
  };
  const sel = (name, opts, css='') => `<select class="legacy-design-field ${css}" name="Sections[${index}][${name}]">${opts.map(x => `<option value="${x}"${String(v[name])===x?' selected':''}>${x}</option>`).join('')}</select>`;
  const inp = (name, type='number', css='') => `<input class="legacy-design-field ${css}" type="${type}" name="Sections[${index}][${name}]" value="${v[name]}">`;
  return `<input class="h18-page-section-key" value="${key}"><input class="h18-page-section-type" value="${overrides.Type || 'text'}">
    ${sel('DesignMode',['Global','Custom'],'h18-section-design-mode')}${inp('CustomBackgroundColor','color')}${inp('CustomTextColor','color')}${inp('CustomHeadingColor','color')}
    ${inp('BorderWidthPx')}${inp('CustomBorderColor','color')}${inp('RadiusPx')}${inp('RadiusTopLeftPx')}${inp('RadiusTopRightPx')}${inp('RadiusBottomRightPx')}${inp('RadiusBottomLeftPx')}
    ${sel('SectionBodyFontFamily',fonts)}${sel('SectionHeadingFontFamily',fonts)}${inp('BodyFontSizePx')}${inp('H1FontSizePx')}${inp('H2FontSizePx')}${inp('H3FontSizePx')}
    ${inp('SectionOpacityPercent')}${sel('ShadowStyle',shadows)}${sel('HoverStyleMode',['Inherit','Custom'],'h18-hover-style-mode')}
    ${inp('HoverBackgroundColor','color')}${inp('HoverTextColor','color')}${inp('HoverHeadingColor','color')}${inp('HoverBorderColor','color')}${inp('HoverOpacityPercent')}${sel('HoverEffect',hoverEffects)}${inp('HoverTransitionMs')}
    ${inp('LayoutGapPx')}${inp('MobileLayoutGapPx')}`;
}

async function boot(page, responsiveStore = {}) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="hjem">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div class="h18-builder-canvas" data-canvas-device="desktop" data-canvas-state="normal"></div>
      <div id="h18-page-sections-sortable">
        <section id="text-row" class="h18-page-section-row is-selected" data-section-type="text"><header class="h18-page-section-header">Tekst</header><div class="h18-canvas-preview"><h2 class="h18-canvas-preview-title">Tekst</h2><p>Indhold</p></div><div class="h18-page-section-body">${fields(1,'text-1')}</div></section>
        <section id="kasse-row" class="h18-page-section-row" data-section-type="container"><header class="h18-page-section-header">Kasse</header><div class="h18-canvas-preview"><h2 class="h18-canvas-preview-title">Kasse</h2><div class="h18-ud-auto-box-grid"><span>A</span><span>B</span></div></div><div class="h18-page-section-body">${fields(2,'kasse-1',{Type:'container',DesignMode:'Custom',CustomBackgroundColor:'#112233'})}</div></section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(({ map, fonts, shadows, hoverEffects, store }) => {
    window.H18LegoSpacingV0831 = { version:'0.8.31', schemaVersion:2, pages:{}, limits:{desktop:160,tablet:160,mobile:120} };
    window.H18LegoDesignV0832 = { version:'0.8.32', schemaVersion:1, fieldMap:map, fonts, shadows, hoverEffects };
    window.H18LegoResponsiveDesignV0833 = { version:'0.8.33', schemaVersion:1, pages:store, fieldMap:map, fonts, shadows, hoverEffects };
    window.__responsiveEvents = 0; window.__spacingEvents = 0; window.__legacyEvents = 0;
    const $ = window.jQuery;
    $('#h18-page-editor-form').on('input', '.h18-lego-responsive-design-state-json', () => { window.__responsiveEvents += 1; });
    $('#h18-page-editor-form').on('input', '.h18-lego-spacing-state-json', () => { window.__spacingEvents += 1; });
    $('#h18-page-editor-form').on('input change', '.legacy-design-field', () => { window.__legacyEvents += 1; });
  }, { map:fieldMap, fonts, shadows, hoverEffects, store:responsiveStore });
  await page.addStyleTag({ path: spacingCss });
  await page.addStyleTag({ path: designCss });
  await page.addStyleTag({ path: responsiveCss });
  await page.addScriptTag({ path: spacingRuntime });
  await page.addScriptTag({ path: designRuntime });
  await page.addScriptTag({ path: designGuard });
  await page.addScriptTag({ path: responsiveGuard });
  await page.addScriptTag({ path: responsiveRuntime });
  await expect(page.locator('#h18-ud-lego-responsive-design-panel')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-responsive-design-runtime','0.8.33');
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-responsive-design-select-guard','0.8.33');
}

async function canvasDevice(page, device) {
  await page.locator('.h18-builder-canvas').evaluate((n,d) => n.setAttribute('data-canvas-device',d), device);
  const label = device === 'mobile' ? 'Mobil' : device.charAt(0).toUpperCase()+device.slice(1);
  await expect(page.locator('#h18-ud-lego-responsive-design-panel .h18-rd-tab.is-active')).toHaveText(label);
}

async function state(page, key='text-1') {
  return page.evaluate((k) => window.__h18LegoResponsiveDesignV0833.stateForKey(k), key);
}

test('Tablet and Mobile start as live Desktop inheritance with no fake override', async ({ page }) => {
  await boot(page);
  let s = await state(page);
  expect(s.Tablet.InheritDesktop).toBe(true); expect(s.Tablet.HasOverride).toBe(false);
  expect(s.Mobile.InheritDesktop).toBe(true); expect(s.Mobile.HasOverride).toBe(false);
  await canvasDevice(page,'tablet');
  await expect(page.locator('[data-h18-rd-inherit="Tablet"]')).toBeChecked();
  await expect(page.locator('[data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Colors.Background"]')).toBeDisabled();
  const effective = await page.evaluate(() => window.__h18LegoResponsiveDesignV0833.effectiveForKey('text-1','Tablet'));
  expect(effective.Inherited).toBe(true); expect(effective.Design.Colors.Background).toBe('#ffffff');
});

test('first Tablet override seeds current Desktop then survives inherit on/off', async ({ page }) => {
  await boot(page);
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-path="Colors.Background"]').evaluate((el) => { el.value='#224466'; el.dispatchEvent(new Event('input',{bubbles:true})); });
  await expect(page.locator('#text-row [name$="[CustomBackgroundColor]"]')).toHaveValue('#224466');
  await canvasDevice(page,'tablet');
  await page.locator('[data-h18-rd-inherit="Tablet"]').uncheck();
  let s = await state(page);
  expect(s.Tablet.HasOverride).toBe(true); expect(s.Tablet.Design.Colors.Background).toBe('#224466');
  await page.locator('[data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Colors.Background"]').evaluate((el) => { el.value='#446688'; el.dispatchEvent(new Event('input',{bubbles:true})); });
  s = await state(page); expect(s.Tablet.Design.Colors.Background).toBe('#446688');
  await page.locator('[data-h18-rd-inherit="Tablet"]').check();
  let effective = await page.evaluate(() => window.__h18LegoResponsiveDesignV0833.effectiveForKey('text-1','Tablet'));
  expect(effective.Design.Colors.Background).toBe('#224466');
  await page.locator('[data-h18-rd-inherit="Tablet"]').uncheck();
  effective = await page.evaluate(() => window.__h18LegoResponsiveDesignV0833.effectiveForKey('text-1','Tablet'));
  expect(effective.Design.Colors.Background).toBe('#446688');
});

test('responsive select produces one history checkpoint and hover effect works with inherited colors', async ({ page }) => {
  await boot(page);
  await canvasDevice(page,'tablet');
  await page.locator('[data-h18-rd-inherit="Tablet"]').uncheck();
  await page.evaluate(() => { window.__responsiveEvents = 0; });
  await page.locator('[data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="States.Hover.Effect"]').selectOption('Lift');
  expect(await page.evaluate(() => window.__responsiveEvents)).toBe(1);
  let s = await state(page); expect(s.Tablet.Design.States.Hover.Mode).toBe('Inherit'); expect(s.Tablet.Design.States.Hover.Effect).toBe('Lift');
  await page.locator('.h18-builder-canvas').evaluate(n => n.setAttribute('data-canvas-state','hover'));
  await expect(page.locator('#text-row')).toHaveAttribute('data-h18-responsive-design-hover','1');
  await expect.poll(async () => page.locator('#text-row .h18-canvas-preview').evaluate(n => getComputedStyle(n).transform)).not.toBe('none');
});

test('Kasse uses the same responsive design state and preview overlay', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => { document.getElementById('text-row').classList.remove('is-selected'); document.getElementById('kasse-row').classList.add('is-selected'); });
  await expect(page.locator('#h18-ud-lego-responsive-design-panel')).toHaveAttribute('data-h18-rd-role','kasse');
  await canvasDevice(page,'mobile');
  await page.locator('[data-h18-rd-inherit="Mobile"]').uncheck();
  await page.locator('[data-h18-rd-device-panel="Mobile"] [data-h18-rd-path="Colors.Background"]').evaluate((el) => { el.value='#335577'; el.dispatchEvent(new Event('input',{bubbles:true})); });
  await expect(page.locator('#kasse-row')).toHaveAttribute('data-h18-responsive-design-active','1');
  await expect(page.locator('#kasse-row .h18-canvas-preview')).toHaveCSS('background-color','rgb(51, 85, 119)');
  const s = await state(page,'kasse-1'); expect(s.Mobile.Design.Colors.Background).toBe('#335577');
});

test('spacing and responsive design remain independent single-history states', async ({ page }) => {
  await boot(page);
  await canvasDevice(page,'tablet');
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-inherit-device="Tablet"]').uncheck();
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-inherit="Tablet"]').uncheck();
  await page.evaluate(() => { window.__responsiveEvents=0; window.__spacingEvents=0; });
  await page.locator('#h18-ud-lego-spacing-panel [data-h18-lego-path="Tablet.Margin.X"]').fill('13');
  expect(await page.evaluate(() => window.__spacingEvents)).toBe(1);
  expect(await page.evaluate(() => window.__responsiveEvents)).toBe(0);
  await page.locator('#h18-ud-lego-responsive-design-panel [data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Radius.All"]').fill('19');
  expect(await page.evaluate(() => window.__responsiveEvents)).toBe(1);
  expect(await page.evaluate(() => window.__spacingEvents)).toBe(1);
});

test('history-style full DOM restore rehydrates previous responsive state', async ({ page }) => {
  await boot(page);
  const snapshot = await page.locator('#h18-page-sections-sortable').evaluate(n => n.innerHTML);
  await canvasDevice(page,'tablet');
  await page.locator('[data-h18-rd-inherit="Tablet"]').uncheck();
  await page.locator('[data-h18-rd-device-panel="Tablet"] [data-h18-rd-path="Radius.All"]').fill('27');
  expect((await state(page)).Tablet.Design.Radius.All).toBe(27);
  await page.locator('#h18-page-sections-sortable').evaluate((n,html) => { n.innerHTML=html; }, snapshot);
  await expect.poll(async () => (await state(page)).Tablet.InheritDesktop).toBe(true);
  expect((await state(page)).Tablet.HasOverride).toBe(false);
});
