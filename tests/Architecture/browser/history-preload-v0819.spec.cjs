const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-preload-v0821.js');
const postRestorePath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-post-restore-v0822.js');
const contentHistoryPath = path.resolve(__dirname, '../../../assets/ultimate-designer-history-content-v0823.js');
const jqueryRuntime = require.resolve('jquery');

function historyRuntimeScript() { return fs.readFileSync(runtimePath, 'utf8'); }
function postRestoreRuntimeScript() { return fs.readFileSync(postRestorePath, 'utf8'); }
function contentHistoryRuntimeScript() { return fs.readFileSync(contentHistoryPath, 'utf8'); }

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
          <div class="h18-page-section-body">
            <input class="payload" value="Overskrift">
            <input class="background-field" name="Sections[0][BackgroundColor]" value="#ffffff">
            <input class="media-id" name="Sections[0][MediaId]" value="0">
            <input class="media-url" name="Sections[0][MediaUrl]" value="">
          </div>
          <div class="h18-canvas-preview">
            <div class="h18-canvas-direct-controls">
              <label class="h18-canvas-quick-color"><input id="quick-color" type="color" value="#ffffff" data-canvas-color-role="background"></label>
            </div>
            <div class="h18-canvas-image-tools"><button id="image-change" class="h18-canvas-image-change" type="button">Skift billede</button></div>
          </div>
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
  await page.addScriptTag({ content: contentHistoryRuntimeScript() });

  await page.evaluate(() => {
    const sections = document.getElementById('h18-page-sections-sortable');
    const entries = [];
    let index = -1;
    let editorHistoryTimer = null;
    let serial = 0;
    let mediaSerial = 99;

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
      editorHistoryTimer = window.setTimeout(editorHistoryRecordNow, typeof delay === 'number' ? delay : 280);
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

    document.addEventListener('input', (event) => {
      const target = event.target;
      if (!target || !target.closest) { return; }
      if (target.matches('.payload')) {
        scheduleEditorHistoryCapture(280);
        return;
      }
      if (target.matches('#quick-color')) {
        const row = target.closest('.h18-page-section-row');
        const field = row && row.querySelector('.background-field');
        if (field) { field.value = target.value; }
        scheduleEditorHistoryCapture(280);
      }
    });

    document.addEventListener('click', (event) => {
      const button = event.target && event.target.closest ? event.target.closest('.h18-canvas-image-change') : null;
      if (!button) { return; }
      const row = button.closest('.h18-page-section-row');
      if (!row) { return; }
      mediaSerial += 1;
      row.querySelector('.media-id').value = String(mediaSerial);
      row.querySelector('.media-url').value = 'https://example.test/image-' + mediaSerial + '.jpg';
      scheduleEditorHistoryCapture(280);
    });

    window.__historyHarness = {
      addImage,
      editText(value) {
        sections.querySelector('[data-key="text-1"] .payload').value = value;
        scheduleEditorHistoryCapture(280);
      },
      state() {
        const text = sections.querySelector('[data-key="text-1"]');
        return {
          index,
          entries: entries.length,
          keys: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row')).map((row) => row.dataset.key),
          types: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row')).map((row) => row.dataset.sectionType),
          timer: editorHistoryTimer,
          selected: Array.from(sections.querySelectorAll(':scope > .h18-page-section-row.is-selected')).map((row) => row.dataset.key),
          text: text ? text.querySelector('.payload').value : '',
          background: text ? text.querySelector('.background-field').value : '',
          mediaId: text ? text.querySelector('.media-id').value : '',
          mediaUrl: text ? text.querySelector('.media-url').value : ''
        };
      }
    };
  });

  await page.waitForFunction(() => Boolean(window.__h18HistoryCoreBridgeV0821));
  await page.waitForFunction(() => Boolean(window.__h18HistoryPostRestoreBridgeV0822));
  await page.waitForFunction(() => Boolean(window.__h18HistoryContentBridgeV0823));
  await expect(page.locator('#h18-history-runtime-badge')).toHaveText('H0.8.23');
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

  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(180);
  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(180);
  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(0);

  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);

  await page.locator('#palette-image').click();
  await page.waitForTimeout(180);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(4);
  expect(current.entries).toBe(5);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
});

test('text color and selected image are independent Undo Redo checkpoints', async ({ page }) => {
  await boot(page);

  await page.locator('.payload').fill('Ny overskrift');
  await page.waitForTimeout(360);
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.text).toBe('Ny overskrift');

  await page.locator('#quick-color').fill('#224466');
  await page.waitForTimeout(360);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(2);
  expect(current.background).toBe('#224466');

  await page.locator('#image-change').click();
  await page.waitForTimeout(360);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
  expect(current.mediaId).toBe('100');
  expect(current.mediaUrl).toContain('image-100.jpg');

  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(2);
  expect(current.text).toBe('Ny overskrift');
  expect(current.background).toBe('#224466');
  expect(current.mediaId).toBe('0');

  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.text).toBe('Ny overskrift');
  expect(current.background).toBe('#ffffff');

  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(0);
  expect(current.text).toBe('Overskrift');

  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
  expect(current.text).toBe('Ny overskrift');
  expect(current.background).toBe('#224466');
  expect(current.mediaId).toBe('100');
});

test('first text edit immediately after Redo is recorded as a new checkpoint', async ({ page }) => {
  await boot(page);

  await page.locator('.payload').fill('Første tekst');
  await page.waitForTimeout(360);
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click();
  await page.waitForTimeout(20);

  // Exact post-restore content regression: edit immediately, inside the old
  // 100 ms latch window. The content bridge must preserve this as checkpoint 2.
  await page.locator('.payload').fill('Tekst efter redo');
  await page.waitForTimeout(380);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(2);
  expect(current.entries).toBe(3);
  expect(current.text).toBe('Tekst efter redo');

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(220);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(1);
  expect(current.text).toBe('Første tekst');
});

test('first color and image changes after Redo are not lost', async ({ page }) => {
  await boot(page);

  await page.locator('.payload').fill('Checkpoint');
  await page.waitForTimeout(360);
  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(20);

  await page.locator('#quick-color').fill('#aa3300');
  await page.waitForTimeout(380);
  let current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(2);
  expect(current.background).toBe('#aa3300');

  await page.locator('#h18-editor-undo').click(); await page.waitForTimeout(180);
  await page.locator('#h18-editor-redo').click(); await page.waitForTimeout(20);
  await page.locator('#image-change').click();
  await page.waitForTimeout(380);
  current = await page.evaluate(() => window.__historyHarness.state());
  expect(current.index).toBe(3);
  expect(current.mediaId).toBe('100');
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
