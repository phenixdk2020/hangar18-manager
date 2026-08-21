const { test, expect } = require('@playwright/test');
const path = require('path');

const jqueryRuntime = require.resolve('jquery');
const runtime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-v0834.js');
const guard = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js');
const snapshotRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-snapshot-v0834.js');
const css = path.resolve(__dirname, '../../../assets/ultimate-designer-lego-interaction-states-v0834.css');

const transitions = ['Inherit','Fast','Normal','Slow','Custom'];
const focusStyles = ['Global','Custom','None'];
const activeEffects = ['None','Press','ScaleDown'];

function fields(index, key, overrides = {}) {
  const v = {
    TransitionPreset:'Inherit',FocusRingStyle:'Global',FocusRingColor:'#8b4a2b',FocusRingWidthPx:'3',FocusRingOffsetPx:'2',ActiveEffect:'None',DisabledOpacityPercent:'55',
    SectionOpacityPercent:'80',ShadowStyle:'Soft',HoverStyleMode:'Inherit',HoverOpacityPercent:'100',HoverTransitionMs:'300',
    DesktopTranslateXPx:'0',DesktopTranslateYPx:'0',DesktopScalePercent:'100',DesktopRotateDeg:'0',
    TabletTranslateXPx:'0',TabletTranslateYPx:'0',TabletScalePercent:'100',TabletRotateDeg:'0',
    MobileTranslateXPx:'0',MobileTranslateYPx:'0',MobileScalePercent:'100',MobileRotateDeg:'0',...overrides
  };
  const sel = (name, opts) => `<select class="legacy-interaction-field" name="Sections[${index}][${name}]">${opts.map(x => `<option value="${x}"${String(v[name])===x?' selected':''}>${x}</option>`).join('')}</select>`;
  const inp = (name, type='number') => `<input class="legacy-interaction-field" type="${type}" name="Sections[${index}][${name}]" value="${v[name]}">`;
  return `<input class="h18-page-section-key" value="${key}"><input name="Sections[${index}][Key]" value="${key}"><input name="Sections[${index}][Type]" value="${overrides.Type || 'text'}">
    ${sel('TransitionPreset',transitions)}${sel('FocusRingStyle',focusStyles)}${inp('FocusRingColor','color')}${inp('FocusRingWidthPx')}${inp('FocusRingOffsetPx')}${sel('ActiveEffect',activeEffects)}${inp('DisabledOpacityPercent')}
    ${inp('SectionOpacityPercent')}${sel('ShadowStyle',['None','Soft','Medium','Strong'])}${sel('HoverStyleMode',['Inherit','Custom'])}${inp('HoverOpacityPercent')}${inp('HoverTransitionMs')}
    ${inp('DesktopTranslateXPx')}${inp('DesktopTranslateYPx')}${inp('DesktopScalePercent')}${inp('DesktopRotateDeg')}
    ${inp('TabletTranslateXPx')}${inp('TabletTranslateYPx')}${inp('TabletScalePercent')}${inp('TabletRotateDeg')}
    ${inp('MobileTranslateXPx')}${inp('MobileTranslateYPx')}${inp('MobileScalePercent')}${inp('MobileRotateDeg')}`;
}

async function boot(page, store = {}) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form"><input name="page_slug" value="hjem">
      <div id="h18-page-inspector"><div id="h18-page-inspector-target"></div></div>
      <div class="h18-builder-canvas" data-canvas-device="desktop" data-canvas-state="normal"></div>
      <div id="h18-page-sections-sortable">
        <section id="text-row" class="h18-page-section-row is-selected" data-section-type="text"><header class="h18-page-section-header">Tekst</header><div class="h18-canvas-preview"><h2>Tekst</h2></div><div class="h18-page-section-body">${fields(1,'text-1')}</div></section>
        <section id="kasse-row" class="h18-page-section-row" data-section-type="container"><header class="h18-page-section-header">Kasse</header><div class="h18-canvas-preview"><h2>Kasse</h2></div><div class="h18-page-section-body">${fields(2,'kasse-1',{Type:'container'})}</div></section>
      </div>
    </form>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.evaluate(({ store, transitions, focusStyles, activeEffects }) => {
    window.H18LegoInteractionStatesV0834 = { version:'0.8.34', schemaVersion:1, pages:store, transitionPresets:transitions, focusStyles, activeEffects };
    window.__h18LegoResponsiveDesignV0833 = {
      effectiveForKey: () => ({ Design:{ Effects:{Opacity:80,Shadow:'Soft'}, States:{Hover:{Mode:'Inherit',Opacity:100,TransitionMs:300}} } })
    };
    window.__interactionEvents = 0; window.__legacyEvents = 0;
    const $ = window.jQuery;
    $('#h18-page-editor-form').on('input', '.h18-lego-interaction-states-state-json', () => { window.__interactionEvents += 1; });
    $('#h18-page-editor-form').on('input change', '.legacy-interaction-field', () => { window.__legacyEvents += 1; });
  }, { store, transitions, focusStyles, activeEffects });
  await page.addStyleTag({ path: css });
  await page.addScriptTag({ path: guard });
  await page.addScriptTag({ path: runtime });
  await page.addScriptTag({ path: snapshotRuntime });
  await expect(page.locator('#h18-ud-lego-interaction-states-panel')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-interaction-states-runtime','0.8.34');
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-interaction-states-select-guard','0.8.34');
  await expect(page.locator('html')).toHaveAttribute('data-h18-lego-interaction-snapshot-runtime','0.8.34');
}

async function device(page, value) {
  await page.locator('.h18-builder-canvas').evaluate((n,v) => n.setAttribute('data-canvas-device',v), value);
  const label = value === 'mobile' ? 'Mobil' : value.charAt(0).toUpperCase()+value.slice(1);
  await expect(page.locator('#h18-ud-lego-interaction-states-panel .h18-i-tab.is-active')).toHaveText(label);
}
async function previewState(page, value) {
  await page.locator('.h18-builder-canvas').evaluate((n,v) => n.setAttribute('data-canvas-state',v), value);
  await expect(page.locator('#text-row')).toHaveAttribute('data-h18-interaction-preview-state',value);
}
async function state(page, key='text-1') {
  return page.evaluate((k) => window.__h18LegoInteractionStatesV0834.stateForKey(k), key);
}

test('Desktop interaction controls write existing legacy fields as one logical event', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => { window.__legacyEvents = 0; window.__interactionEvents = 0; });
  await page.locator('[data-h18-i-device-panel="Desktop"] [data-h18-i-path="Focus.Style"]').selectOption('Custom');
  await expect(page.locator('#text-row [name$="[FocusRingStyle]"]')).toHaveValue('Custom');
  expect(await page.evaluate(() => window.__legacyEvents)).toBe(1);
  expect(await page.evaluate(() => window.__interactionEvents)).toBe(0);
  await page.locator('[data-h18-i-device-panel="Desktop"] [data-h18-i-path="Focus.Color"]').fill('#123456');
  await expect(page.locator('#text-row [name$="[FocusRingColor]"]')).toHaveValue('#123456');
});

test('Tablet first override seeds Desktop and one responsive edit is one history checkpoint', async ({ page }) => {
  await boot(page);
  await page.locator('[data-h18-i-device-panel="Desktop"] [data-h18-i-path="Active.Effect"]').selectOption('Press');
  await device(page,'tablet');
  await expect(page.locator('[data-h18-i-inherit="Tablet"]')).toBeChecked();
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  let s = await state(page);
  expect(s.Tablet.HasOverride).toBe(true);
  expect(s.Tablet.Interaction.Active.Effect).toBe('Press');
  await page.evaluate(() => { window.__interactionEvents = 0; window.__legacyEvents = 0; });
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Active.Effect"]').selectOption('ScaleDown');
  s = await state(page);
  expect(s.Tablet.Interaction.Active.Effect).toBe('ScaleDown');
  expect(await page.evaluate(() => window.__interactionEvents)).toBe(1);
  expect(await page.evaluate(() => window.__legacyEvents)).toBe(0);
});

test('Tablet interaction snapshot survives inherit on then off in the same editing session', async ({ page }) => {
  await boot(page);
  await device(page,'tablet');
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Style"]').selectOption('Custom');
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Color"]').fill('#654321');
  await page.locator('[data-h18-i-inherit="Tablet"]').check();
  let effective = await page.evaluate(() => window.__h18LegoInteractionStatesV0834.effectiveForKey('text-1','Tablet'));
  expect(effective.Inherited).toBe(true);
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  const s = await state(page);
  expect(s.Tablet.Interaction.Focus.Color).toBe('#654321');
  effective = await page.evaluate(() => window.__h18LegoInteractionStatesV0834.effectiveForKey('text-1','Tablet'));
  expect(effective.Interaction.Focus.Color).toBe('#654321');
});

test('stored inactive interaction snapshot returns after reload', async ({ page }) => {
  const store = { hjem:{ Sections:{ 'text-1':{ Tablet:{ InteractionHasOverride:false, InteractionHasSnapshot:true, Design:{ Motion:{Transition:'Fast'}, States:{ Focus:{Style:'Custom',Color:'#246810',Width:6,Offset:3}, Active:{Effect:'ScaleDown'}, Disabled:{Opacity:39} } } } } } } };
  await boot(page, store);
  await device(page,'tablet');
  await expect(page.locator('[data-h18-i-inherit="Tablet"]')).toBeChecked();
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  const s = await state(page);
  expect(s.Tablet.Interaction.Focus.Color).toBe('#246810');
  expect(s.Tablet.Interaction.Active.Effect).toBe('ScaleDown');
});

test('responsive Focus Active and Disabled previews use the interaction override', async ({ page }) => {
  await boot(page);
  await device(page,'tablet');
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Style"]').selectOption('Custom');
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Color"]').fill('#ff0000');
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Focus.Width"]').fill('6');
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Active.Effect"]').selectOption('ScaleDown');
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Disabled.Opacity"]').fill('40');

  await previewState(page,'focus');
  await expect.poll(async () => page.locator('#text-row .h18-canvas-preview').evaluate(n => getComputedStyle(n).boxShadow)).toContain('255, 0, 0');
  await previewState(page,'active');
  await expect.poll(async () => page.locator('#text-row .h18-canvas-preview').evaluate(n => n.style.transform)).toContain('0.97');
  await previewState(page,'disabled');
  await expect.poll(async () => page.locator('#text-row .h18-canvas-preview').evaluate(n => Number(getComputedStyle(n).opacity))).toBeCloseTo(0.32,2);
});

test('Kasse uses the exact same interaction-state panel and model', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => { document.getElementById('text-row').classList.remove('is-selected'); document.getElementById('kasse-row').classList.add('is-selected'); });
  await page.locator('#kasse-row .h18-page-section-header').click();
  await expect(page.locator('#h18-ud-lego-interaction-states-panel')).toHaveAttribute('data-h18-i-role','kasse');
  await device(page,'mobile');
  await page.locator('[data-h18-i-inherit="Mobile"]').uncheck();
  await page.locator('[data-h18-i-device-panel="Mobile"] [data-h18-i-path="Disabled.Opacity"]').fill('33');
  const s = await state(page,'kasse-1');
  expect(s.Mobile.Interaction.Disabled.Opacity).toBe(33);
});

test('history-style full DOM restore rehydrates prior interaction state', async ({ page }) => {
  await boot(page);
  const snapshot = await page.locator('#h18-page-sections-sortable').evaluate(n => n.innerHTML);
  await device(page,'tablet');
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Disabled.Opacity"]').fill('28');
  expect((await state(page)).Tablet.Interaction.Disabled.Opacity).toBe(28);
  await page.locator('#h18-page-sections-sortable').evaluate((n,html) => { n.innerHTML=html; }, snapshot);
  await expect.poll(async () => (await state(page)).Tablet.HasOverride).toBe(false);
});

test('submit payload carries reversible snapshot metadata without a new persistence store', async ({ page }) => {
  await boot(page);
  await device(page,'tablet');
  await page.locator('[data-h18-i-inherit="Tablet"]').uncheck();
  await page.locator('[data-h18-i-device-panel="Tablet"] [data-h18-i-path="Active.Effect"]').selectOption('Press');
  await page.locator('[data-h18-i-inherit="Tablet"]').check();
  await page.locator('#h18-page-editor-form').evaluate(form => form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
  const payload = await page.locator('input[name^="h18_lego_interaction_states"][name$="[StateJson]"]').first().inputValue();
  const parsed = JSON.parse(payload);
  expect(parsed.Tablet.HasOverride).toBe(false);
  expect(parsed.Tablet.HasSnapshot).toBe(true);
  expect(parsed.Tablet.Interaction.Active.Effect).toBe('Press');
});
