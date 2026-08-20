const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0821.js');
const postRestorePath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-post-restore-v0822.js');
const jqueryRuntime = require.resolve('jquery');

function historyRuntimeScript() {
  return fs.readFileSync(runtimePath, 'utf8');
}
function postRestoreRuntimeScript() {
  return fs.readFileSync(postRestorePath, 'utf8');
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><body>
    <button class="h18-builder-palette-item" data-section-type="image" id="palette-image">Billede</button>
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
  await page.addScriptTag({ content: postRestoreRuntimeScript() });

  await page.evaluate(() => {
    const sections = document.getElementById('h18-page-sections-sortable');
    const entries = [];
    let index = -1;
    let editorHistoryTimer = null;
    let serial = 0;

    function canonicalHtml() {
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

    function addImage(key) {
      const row = document.createElement('section');
      row.className = 'h18-page-section-row is-selected';
      row.dataset.sectionType = 'image';
      row.dataset.key = key;
      row.innerHTML = '<input class="h18-page-section-key" value="' + key + '"><select class="h18-page-section-type"><option value="text" selected>Tekst</option><option value="image">Billede</option></select><div class="h18-page-section-header">Billede</div><div class="h18-page-section-body"></div>';
      row.querySelector('.h18-page-section-type').value = 'image';
      sections.querySelectorAll('.is-selected').forEach((node) => node.classList.remove('is-selected'));
      row.classList.add('is-selected');
      sections.appendChild(row);
      scheduleEditorHistoryCapture(120);
    }

    editorHistoryRecordNow();
    document.getElementById('h18-editor-undo').addEventListener('click', undo);
    document.getElementById('h18-editor-redo').addEventListener('click', redo);
    document.getElementById('palette-image').addEventListener('click', () => {
      serial += 1;
      addImage('image-' + serial);
    });

    window.__historyHarness = {
      addImage,
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
  await page.waitForFunction(() => Boolean(window.__h18HistoryPostRestoreBridgeV0822));
  await expect(page.locator('#h18-history-runtime-badge')).toHaveText('H0.8.22');
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0821.cloneBridgeInstalled())).toBe(true);
}

test('two structural image additions are two checkpoints and Undo stays on one', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  await page.evaluate(() => window.__historyHarness.addImage('image-2'));
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);
  const current = await page.evaluate(() => window.__historyHarness.state());
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
  expect(current.types).toEqual(['text', 'image']);
  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(550);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.types).toEqual(['text', 'image', 'image']);
});

test('new structural edit after full Undo and Redo cycle becomes a new checkpoint', async ({ page }) => {
  await boot(page);

  await page.locator('#palette-image').click();
  await page.locator('#palette-image').click();
  await page.locator('#palette-image').click();
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2', 'image-3']);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(180);
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(180);
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(0);
  expect(current.keys).toEqual(['text-1']);

  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2', 'image-3']);

  // Exact manual regression: immediately add a fresh palette element after
  // restoring the complete Redo chain. It must become checkpoint 4.
  await page.locator('#palette-image').click();
  await page.waitForTimeout(180);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(4);
  expect(current.entries).toBe(5);
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2', 'image-3', 'image-4']);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
  expect(current.keys).toEqual(['text-1', 'image-1', 'image-2', 'image-3']);
});

test('Undo clears historical text selection and Direct Design after structural restore', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => window.__historyHarness.addImage('image-1'));
  await page.evaluate(() => window.__historyHarness.addImage('image-2'));
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);
  const current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.selected).toEqual([]);
  await expect(page.locator('#h18-page-inspector-target')).not.toContainText('DIREKTE DESIGN');
});

test('pending text edit is flushed exactly once before Undo', async ({ page }) => {
  await boot(page);
  await page.evaluate(() => window.__historyHarness.editText('Rettet overskrift'));
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0821.hasPending())).toBe(true);
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(550);
  expect(await page.evaluate(() => window.__h18HistoryCoreBridgeV0821.hasPending())).toBe(false);
  await expect(page.locator('[data-key="text-1"] .payload')).toHaveValue('Overskrift');
});
