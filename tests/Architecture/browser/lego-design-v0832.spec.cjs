const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const designRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.js');
const designGuard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-event-guard-v0832.js');
const designCss = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-design-v0832.css');

const fieldMap = {
  Mode: 'DesignMode',
  'Colors.Background': 'CustomBackgroundColor',
  'Colors.Text': 'CustomTextColor',
  'Colors.Heading': 'CustomHeadingColor',
  'Border.Width': 'BorderWidthPx',
  'Border.Color': 'CustomBorderColor',
  'Radius.All': 'RadiusPx',
  'Radius.TopLeft': 'RadiusTopLeftPx',
  'Radius.TopRight': 'RadiusTopRightPx',
  'Radius.BottomRight': 'RadiusBottomRightPx',
  'Radius.BottomLeft': 'RadiusBottomLeftPx',
  'Typography.BodyFont': 'SectionBodyFontFamily',
  'Typography.HeadingFont': 'SectionHeadingFontFamily',
  'Typography.BodySize': 'BodyFontSizePx',
  'Typography.H1Size': 'H1FontSizePx',
  'Typography.H2Size': 'H2FontSizePx',
  'Typography.H3Size': 'H3FontSizePx',
  'Effects.Opacity': 'SectionOpacityPercent',
  'Effects.Shadow': 'ShadowStyle',
  'States.Hover.Mode': 'HoverStyleMode',
  'States.Hover.Background': 'HoverBackgroundColor',
  'States.Hover.Text': 'HoverTextColor',
  'States.Hover.Heading': 'HoverHeadingColor',
  'States.Hover.Border': 'HoverBorderColor',
  'States.Hover.Opacity': 'HoverOpacityPercent',
  'States.Hover.Effect': 'HoverEffect',
  'States.Hover.TransitionMs': 'HoverTransitionMs'
};

function designFields(index, overrides = {}) {
  const values = {
    DesignMode: 'Global', CustomBackgroundColor: '#ffffff', CustomTextColor: '#30382a', CustomHeadingColor: '#30382a',
    BorderWidthPx: '0', CustomBorderColor: '#c3ae83', RadiusPx: '7', RadiusTopLeftPx: '-1', RadiusTopRightPx: '-1', RadiusBottomRightPx: '-1', RadiusBottomLeftPx: '-1',
    SectionBodyFontFamily: 'Global', SectionHeadingFontFamily: 'Global', BodyFontSizePx: '0', H1FontSizePx: '0', H2FontSizePx: '0', H3FontSizePx: '0',
    SectionOpacityPercent: '100', ShadowStyle: 'None', HoverStyleMode: 'Inherit', HoverBackgroundColor: '#ffffff', HoverTextColor: '#30382a', HoverHeadingColor: '#30382a', HoverBorderColor: '#c3ae83', HoverOpacityPercent: '100', HoverEffect: 'None', HoverTransitionMs: '220',
    ...overrides
  };
  const select = (name, options, css = '') => `<select class="legacy-design-field ${css}" name="Sections[${index}][${name}]">${options.map(v => `<option value="${v}"${String(values[name]) === v ? ' selected' : ''}>${v}</option>`).join('')}</select>`;
  const input = (name, type = 'number', css = '') => `<input class="legacy-design-field ${css}" type="${type}" name="Sections[${index}][${name}]" value="${values[name]}">`;
  return `
    ${select('DesignMode', ['Global','Custom'], 'h18-section-design-mode')}
    <div class="h18-custom-design-fields">
      ${input('CustomBackgroundColor','color')}${input('CustomTextColor','color')}${input('CustomHeadingColor','color')}
    </div>
    ${input('BorderWidthPx')}${input('CustomBorderColor','color')}
    ${input('RadiusPx')}${input('RadiusTopLeftPx')}${input('RadiusTopRightPx')}${input('RadiusBottomRightPx')}${input('RadiusBottomLeftPx')}
    ${select('SectionBodyFontFamily', ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'])}
    ${select('SectionHeadingFontFamily', ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'])}
    ${input('BodyFontSizePx')}${input('H1FontSizePx')}${input('H2FontSizePx')}${input('H3FontSizePx')}
    ${input('SectionOpacityPercent')}${select('ShadowStyle', ['None','Soft','Medium','Strong'])}
    ${select('HoverStyleMode', ['Inherit','Custom'], 'h18-hover-style-mode')}
    <div class="h18-hover-style-fields">
      ${input('HoverBackgroundColor','color')}${input('HoverTextColor','color')}${input('HoverHeadingColor','color')}${input('HoverBorderColor','color')}${input('HoverOpacityPercent')}
    </div>
    ${select('HoverEffect', ['None','Lift','Scale','Shadow'])}${input('HoverTransitionMs')}
  `;
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div id="h18-page-sections-sortable">
        <section id="text-row" class="h18-page-section-row is-selected" data-section-type="text">
          <header class="h18-page-section-header">Tekst</header>
          <div class="h18-page-section-body">
            <input name="Sections[1][Type]" value="text">
            ${designFields(1)}
          </div>
        </section>
        <section id="kasse-row" class="h18-page-section-row" data-section-type="container">
          <header class="h18-page-section-header">Kasse</header>
          <div class="h18-page-section-body">
            <input name="Sections[2][Type]" value="container">
            ${designFields(2, { DesignMode: 'Custom', CustomBackgroundColor: '#112233', RadiusPx: '12' })}
          </div>
        </section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate((map) => {
    window.H18LegoDesignV0832 = {
      version: '0.8.32', schemaVersion: 1, fieldMap: map,
      fonts: ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'],
      shadows: ['None','Soft','Medium','Strong'], hoverEffects: ['None','Lift','Scale','Shadow']
    };
    window.__designLegacyEvents = 0;
    window.jQuery('#h18-page-editor-form').on('input change', '.legacy-design-field', function () {
      window.__designLegacyEvents += 1;
    });
  }, fieldMap);
  await page.addStyleTag({ path: designCss });
  await page.addScriptTag({ path: designRuntime });
  await page.addScriptTag({ path: designGuard });
  await expect(page.locator('#h18-ud-lego-design-panel')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-design-select-guard', '0.8.32');
}

async function eventCount(page) {
  return page.evaluate(() => window.__designLegacyEvents);
}

async function resetEvents(page) {
  await page.evaluate(() => { window.__designLegacyEvents = 0; });
}

test('ordinary element derives canonical state from existing fields with no parallel persistence', async ({ page }) => {
  await boot(page);
  await expect(page.locator('#h18-ud-lego-design-panel')).toHaveAttribute('data-h18-lego-design-role', 'element');
  await expect(page.locator('#h18-ud-lego-design-panel .h18-ud-lego-design-badge')).toHaveText('0.8.32');
  expect(await page.locator('#text-row').getAttribute('data-h18-lego-design-role')).toBe('element');
  expect(await page.locator('#text-row').getAttribute('data-h18-lego-design-mode')).toBe('global');
  expect(await page.locator('input[name^="h18_lego_design"],input.h18-lego-design-state-json').count()).toBe(0);

  const state = await page.evaluate(() => window.__h18LegoDesignV0832.stateForSelectedRow());
  expect(state.Mode).toBe('Global');
  expect(state.Colors.Background).toBe('#ffffff');
  expect(state.Radius.TopLeft).toBe(-1);
  expect(state.Typography.BodyFont).toBe('Global');
  expect(state.States.Hover.Mode).toBe('Inherit');
});

test('one color action switches Custom in the same transaction and emits one legacy history event', async ({ page }) => {
  await boot(page);
  await resetEvents(page);

  await page.locator('[data-h18-lego-design-path="Colors.Background"]').evaluate((el) => {
    el.value = '#224466';
    el.dispatchEvent(new Event('input', { bubbles: true }));
  });

  await expect(page.locator('#text-row [name$="[DesignMode]"]')).toHaveValue('Custom');
  await expect(page.locator('#text-row [name$="[CustomBackgroundColor]"]')).toHaveValue('#224466');
  expect(await eventCount(page)).toBe(1);
  const state = await page.evaluate(() => window.__h18LegoDesignV0832.stateForSelectedRow());
  expect(state.Mode).toBe('Custom');
  expect(state.Colors.Background).toBe('#224466');
});

test('select controls emit one history event instead of input plus change duplicates', async ({ page }) => {
  await boot(page);
  await resetEvents(page);
  await page.locator('[data-h18-lego-design-path="Effects.Shadow"]').selectOption('Strong');
  await expect(page.locator('#text-row [name$="[ShadowStyle]"]')).toHaveValue('Strong');
  expect(await eventCount(page)).toBe(1);
});

test('Kasse uses the exact same canonical controls and writes its own existing fields', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => {
    document.getElementById('text-row').classList.remove('is-selected');
    document.getElementById('kasse-row').classList.add('is-selected');
  });
  await expect(page.locator('#h18-ud-lego-design-panel')).toHaveAttribute('data-h18-lego-design-role', 'kasse');
  await expect(page.locator('#h18-ud-lego-design-panel')).toContainText('Kasse/Grid/Flex');
  expect(await page.locator('#kasse-row').getAttribute('data-h18-lego-design-role')).toBe('kasse');
  await expect(page.locator('[data-h18-lego-design-path="Colors.Background"]')).toHaveValue('#112233');

  await resetEvents(page);
  await page.locator('[data-h18-lego-design-path="Radius.TopLeft"]').fill('0');
  await expect(page.locator('#kasse-row [name$="[RadiusTopLeftPx]"]')).toHaveValue('0');
  expect(await eventCount(page)).toBe(1);

  await resetEvents(page);
  await page.locator('[data-h18-lego-design-path="Typography.BodyFont"]').selectOption('Georgia');
  await expect(page.locator('#kasse-row [name$="[SectionBodyFontFamily]"]')).toHaveValue('Georgia');
  expect(await eventCount(page)).toBe(1);
});

test('hover color becomes Custom without changing normal colors and remains one action', async ({ page }) => {
  await boot(page);
  const normalBefore = await page.locator('#text-row [name$="[CustomBackgroundColor]"]').inputValue();
  await resetEvents(page);

  await page.locator('[data-h18-lego-design-path="States.Hover.Background"]').evaluate((el) => {
    el.value = '#335577';
    el.dispatchEvent(new Event('input', { bubbles: true }));
  });

  await expect(page.locator('#text-row [name$="[HoverStyleMode]"]')).toHaveValue('Custom');
  await expect(page.locator('#text-row [name$="[HoverBackgroundColor]"]')).toHaveValue('#335577');
  expect(await page.locator('#text-row [name$="[CustomBackgroundColor]"]').inputValue()).toBe(normalBefore);
  expect(await eventCount(page)).toBe(1);
});

test('restoring legacy fields is authoritative and canonical state re-derives without a second store', async ({ page }) => {
  await boot(page);
  const snapshot = await page.locator('#text-row .h18-page-section-body').evaluate((body) =>
    Array.from(body.querySelectorAll('input,select')).map((el) => [el.name, el.value])
  );

  await page.locator('[data-h18-lego-design-path="Effects.Opacity"]').fill('41');
  await expect(page.locator('#text-row [name$="[SectionOpacityPercent]"]')).toHaveValue('41');

  await page.evaluate((pairs) => {
    const row = document.getElementById('text-row');
    pairs.forEach(([name, value]) => {
      const el = row.querySelector(`[name="${name}"]`);
      if (el) el.value = value;
    });
    row.classList.remove('is-selected');
    row.classList.add('is-selected');
  }, snapshot);

  await expect.poll(async () => {
    const state = await page.evaluate(() => window.__h18LegoDesignV0832.stateForSelectedRow());
    return state && state.Effects.Opacity;
  }).toBe(100);
  await expect(page.locator('[data-h18-lego-design-path="Effects.Opacity"]')).toHaveValue('100');
});
