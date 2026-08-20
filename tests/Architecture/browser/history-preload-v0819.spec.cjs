const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0820.js');
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
      const clone = sections.cloneNode(true);
      clone.querySelectorAll('.is-selected').forEach((node) => node.classList.remove('is-selected'));
      // Mirror editorHistoryNormalizeClone() from assets/admin.js: live form
      // properties must be materialized into serialized attributes/text before
      // the HTML signature is compared.
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

    function restore(html) {
      sections.innerHTML = html;
      // Mimic the legacy restore selecting a historical text element and opening
      // Direct Design. v0.8.20 must clear this transient UI state after Undo.
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
        row.innerHTML = '<input class="h18-page-section-key" value="' + key + '"><div class="h18-page-section-header">Billede</div><div class="h18-page-section-body"></div>';
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
          timer: editorHistoryTimer,
          selected: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row.is-selected')).map((row) => row.dataset.key)
        };
      }
    };
  });

  await page.waitForFunction(() => Boolean(window.__h18HistoryCoreBridgeV0820));
  await expect(page.locator('#h18-history-runtime-badge')).toHaveText('H0.8.20');
}

test('two structural image additions are two checkpoints and Undo stays on one', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.entries).toBe(2);
  expect(current.keys).toEqual(['text-1', 'image-1']);
  expect(current.timer).toBe(0);

  await page.evaluate(() => window.__historyHarness.addImage('image-2'));
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(2);
  expect(current.entries).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2']);
  expect(current.timer).toBe(0);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);

  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.entries).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1']);

  // Regression: legacy failure returned to step 2 after restore fallout.
  await page.waitForTimeout(900);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.keys).toEqual(['text-1', 'image-1']);
});

test('Undo clears historical text selection and Direct Design after structural restore', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  await page.evaluate(() => window.__historyHarness.addImage('image-2'));
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);

  const current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.keys).toEqual(['text-1', 'image-1']);
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
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0820.hasPending())).toBe(true);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);

  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(0);
  expect(current.entries).toBe(2);
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0820.hasPending())).toBe(false);
  await expect(page.locator('[data-key="text-1"] .payload')).toHaveValue('Overskrift');
});
