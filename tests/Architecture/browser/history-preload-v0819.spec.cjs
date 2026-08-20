const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0821.js');
const jqueryRuntime = require.resolve('jquery');

function historyRuntimeScript() {
  return fs.readFileSync(runtimePath, 'utf8');
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><body>
    <form id="h18-page-editor-form">
      <button id="h18-editor-undo" type="button">Fortryd</button>
      <button id="h18-editor-redo" type="button">Gendan</button>
      <span id="h18-editor-history-status">Ingen ugemte ændringer</span>
      <div id="h18-page-sections-sortable">
        <section class="h18-page-section-row is-selected" data-section-type="text" data-key="text-1">
          <input class="h18-page-section-key" value="text-1">
          <select class="h18-page-section-type"><option value="text" selected>Tekst</option><option value="image">Billede</option></select>
          <div class="h18-page-section-header">Tekst</div>
          <div class="h18-page-section-body"><input class="payload" value="Overskrift"></div>
        </section>
      </div>
      <aside id="h18-page-inspector">
        <div class="h18-builder-inspector-heading"><span>Tekst</span></div>
        <span id="h18-inspector-type">text</span>
        <span id="h18-inspector-key">text-1</span>
        <div id="h18-page-inspector-target"><div class="h18-canvas-direct-controls">DIREKTE DESIGN</div></div>
      </aside>
    </form>
    <div id="h18-command-palette"><div id="h18-command-palette-results"></div></div>
  </body></html>`);

  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ content: historyRuntimeScript() });

  await page.evaluate(() => {
    const sections = document.getElementById('h18-page-sections-sortable');
    const entries = [];
    let index = -1;
    let editorHistoryTimer = null;

    function canonicalHtml() {
      // Mirror editorHistorySnapshot(): the production editor uses jQuery.clone().
      // v0.8.21 must preserve live SELECT/INPUT/TEXTAREA properties in that clone.
      const clone = window.jQuery(sections).clone(false, false).get(0);
      clone.querySelectorAll('.is-selected').forEach((node) => node.classList.remove('is-selected'));
      clone.querySelectorAll('input').forEach((input) => {
        if (input.type === 'checkbox' || input.type === 'radio') {
          if (input.checked) { input.setAttribute('checked', 'checked'); }
          else { input.removeAttribute('checked'); }
        } else {
          input.setAttribute('value', String(input.value == null ? '' : input.value));
        }
      });
      clone.querySelectorAll('textarea').forEach((textarea) => {
        textarea.textContent = String(textarea.value == null ? '' : textarea.value);
      });
      clone.querySelectorAll('select').forEach((select) => {
        const values = Array.from(select.selectedOptions).map((option) => String(option.value));
        Array.from(select.options).forEach((option) => {
          if (values.includes(String(option.value))) { option.setAttribute('selected', 'selected'); }
          else { option.removeAttribute('selected'); }
        });
      });
      return clone.innerHTML;
    }

    function editorHistoryRecordNow() {
      const html = canonicalHtml();
      const current = index >= 0 ? entries[index] : null;
      if (current && current === html) { return; }
      if (index < entries.length - 1) { entries.splice(index + 1); }
      entries.push(html);
      index = entries.length - 1;
    }

    function scheduleEditorHistoryCapture(delay) {
      window.clearTimeout(editorHistoryTimer);
      editorHistoryTimer = window.setTimeout(editorHistoryRecordNow, delay);
    }

    function flushPending() {
      if (!editorHistoryTimer) { return; }
      window.clearTimeout(editorHistoryTimer);
      editorHistoryTimer = null;
      editorHistoryRecordNow();
    }

    function refreshTypesAfterRestore() {
      Array.from(sections.querySelectorAll(':scope > .h18-page-section-row')).forEach((row) => {
        const select = row.querySelector('.h18-page-section-type');
        const type = String(select && select.value ? select.value : 'text');
        row.dataset.sectionType = type;
        const header = row.querySelector('.h18-page-section-header');
        if (header) { header.textContent = type === 'image' ? 'Billede' : 'Tekst'; }
      });
    }

    function restore(html) {
      sections.innerHTML = html;
      // Mirror production editorHistoryRestore(): refreshPageSectionType() trusts
      // the restored type SELECT and writes data-section-type from its live value.
      refreshTypesAfterRestore();
      const text = sections.querySelector('[data-key="text-1"]');
      if (text) { text.classList.add('is-selected'); }
      const inspector = document.getElementById('h18-page-inspector-target');
      inspector.innerHTML = '<div class="h18-canvas-direct-controls">DIREKTE DESIGN</div>';
    }

    function undo() {
      flushPending();
      if (index <= 0) { return; }
      index -= 1;
      restore(entries[index]);
    }

    function redo() {
      flushPending();
      if (index < 0 || index >= entries.length - 1) { return; }
      index += 1;
      restore(entries[index]);
    }

    editorHistoryRecordNow();

    document.getElementById('h18-editor-undo').addEventListener('click', undo);
    document.getElementById('h18-editor-redo').addEventListener('click', redo);

    window.__historyHarness = {
      addImage(key) {
        const row = document.createElement('section');
        row.className = 'h18-page-section-row is-selected';
        row.dataset.sectionType = 'image';
        row.dataset.key = key;
        // Deliberately keep TEXT as the markup default, exactly like the shared
        // production template. The live select property is then changed to image.
        row.innerHTML = '<input class="h18-page-section-key" value="' + key + '"><select class="h18-page-section-type"><option value="text" selected>Tekst</option><option value="image">Billede</option></select><div class="h18-page-section-header">Billede</div><div class="h18-page-section-body"></div>';
        row.querySelector('.h18-page-section-type').value = 'image';
        sections.querySelectorAll('.is-selected').forEach((node) => node.classList.remove('is-selected'));
        row.classList.add('is-selected');
        sections.appendChild(row);
        scheduleEditorHistoryCapture(120);
      },
      editText(value) {
        sections.querySelector('[data-key="text-1"] .payload').value = value;
        scheduleEditorHistoryCapture(280);
      },
      state() {
        return {
          index,
          entries: entries.length,
          keys: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row')).map((row) => row.dataset.key),
          types: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row')).map((row) => row.dataset.sectionType),
          timer: editorHistoryTimer,
          selected: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row.is-selected')).map((row) => row.dataset.key)
        };
      }
    };
  });

  await page.waitForFunction(() => Boolean(window.__h18HistoryCoreBridgeV0821));
  await expect(page.locator('#h18-history-runtime-badge')).toHaveText('H0.8.21');
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0821.cloneBridgeInstalled())).toBe(true);
}

test('two structural image additions are two checkpoints and Undo stays on one', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.entries).toBe(2);
  expect(current.keys).toEqual(['text-1', 'image-1']);
  expect(current.types).toEqual(['text', 'image']);
  expect(current.timer).toBe(0);

  await page.evaluate(() => window.__historyHarness.addImage('image-2'));
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(2);
  expect(current.entries).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2']);
  expect(current.types).toEqual(['text', 'image', 'image']);
  expect(current.timer).toBe(0);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);

  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.entries).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1']);
  expect(current.types).toEqual(['text', 'image']);

  await page.waitForTimeout(900);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.keys).toEqual(['text-1', 'image-1']);
  expect(current.types).toEqual(['text', 'image']);
});

test('image element type survives Undo and Redo instead of reverting to text', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  await page.evaluate(() => window.__historyHarness.addImage('image-2'));

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.keys).toEqual(['text-1', 'image-1']);
  expect(current.types).toEqual(['text', 'image']);
  await expect(page.locator('[data-key="image-1"] .h18-page-section-header')).toHaveText('Billede');

  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(550);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2']);
  expect(current.types).toEqual(['text', 'image', 'image']);
  await expect(page.locator('[data-key="image-1"] .h18-page-section-header')).toHaveText('Billede');
  await expect(page.locator('[data-key="image-2"] .h18-page-section-header')).toHaveText('Billede');
});

test('Undo clears historical text selection and Direct Design after structural restore', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  await page.evaluate(() => window.__historyHarness.addImage('image-2'));
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);

  const current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.keys).toEqual(['text-1', 'image-1']);
  expect(current.types).toEqual(['text', 'image']);
  expect(current.selected).toEqual([]);
  await expect(page.locator('#h18-page-inspector-target')).not.toContainText('DIREKTE DESIGN');
  await expect(page.locator('#h18-page-inspector-target')).toContainText('Klik på');
});

test('pending text edit is flushed exactly once before Undo', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__historyHarness.editText('Rettet overskrift'));
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(0);
  expect(current.entries).toBe(1);
  expect(current.timer).toBe(0);
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0821.hasPending())).toBe(true);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);

  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(0);
  expect(current.entries).toBe(2);
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0821.hasPending())).toBe(false);
  await expect(page.locator('[data-key="text-1"] .payload')).toHaveValue('Overskrift');
});
