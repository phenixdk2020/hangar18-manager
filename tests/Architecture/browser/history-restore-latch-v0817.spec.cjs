const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const boxContentRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-box-content-layout.js');
const restoreLatchRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-history-v0817.js');
const editorLayoutController = path.resolve(__dirname, '../../../src/Admin/EditorLayoutToolsAdminController.php');
const jqueryRuntime = require.resolve('jquery');

function historyGuardScript() {
  const source = fs.readFileSync(editorLayoutController, 'utf8');
  const match = source.match(/private static function enqueueEditorHistoryGuardV0813\(\): void[\s\S]*?\$before = <<<'JS'\n([\s\S]*?)\nJS;\n\s*wp_add_inline_script\('hangar18-manager-admin'/);
  if (!match) {
    throw new Error('Could not extract editor history guard from EditorLayoutToolsAdminController.php');
  }
  return match[1];
}

async function boot(page) {
  await page.setContent(`<!doctype html><html><body tabindex="-1">
    <div class="h18-visual-builder">
      <form id="h18-page-editor-form">
        <button id="h18-editor-undo" type="button">Fortryd</button>
        <button id="h18-editor-redo" type="button">Gendan</button>
        <button id="h18-editor-restore-draft" type="button">Gendan lokal kladde</button>
        <input id="editor-field" value="før">
        <button class="h18-page-section-drag" type="button">Flyt</button>
        <div id="h18-page-sections-sortable">
          <section id="row-a" class="h18-page-section-row is-selected" data-section-type="text">
            <input class="h18-page-section-key" value="row-a-key">
            <button class="h18-page-section-header" type="button">A</button>
          </section>
          <section id="row-b" class="h18-page-section-row" data-section-type="text">
            <input class="h18-page-section-key" value="row-b-key">
            <button class="h18-page-section-header" type="button">B</button>
          </section>
        </div>
        <div id="h18-page-inspector-target"></div>
      </form>
    </div>
    <div id="h18-command-palette">
      <input id="h18-command-palette-search">
      <div id="h18-command-palette-results">
        <button id="cmd-undo" class="h18-command-result is-active" type="button"><span class="h18-command-result-main">Fortryd</span></button>
        <button id="cmd-redo" class="h18-command-result" type="button"><span class="h18-command-result-main">Gendan</span></button>
      </div>
    </div>
  </body></html>`);

  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ content: historyGuardScript() });
  await page.addScriptTag({ path: boxContentRuntime });
  await page.addScriptTag({ path: restoreLatchRuntime });

  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const header = event.target.closest && event.target.closest('.h18-page-section-header');
      if (!header) { return; }
      document.querySelectorAll('.h18-page-section-row').forEach((row) => row.classList.remove('is-selected'));
      header.closest('.h18-page-section-row').classList.add('is-selected');
    });
  });

  await page.waitForFunction(() => Boolean(window.__h18HistoryRestoreLatchV0817));
}

async function state(page) {
  return page.evaluate(() => {
    const guard = window.__h18HistoryTransactionV0814;
    return {
      suppressed: Boolean(guard && guard.isSuppressed()),
      trusted: Boolean(guard && guard.hasTrustedEdit && guard.hasTrustedEdit()),
      latched: Boolean(window.__h18HistoryRestoreLatchV0817 && window.__h18HistoryRestoreLatchV0817.isLatched()),
      selectionKey: window.__h18HistoryRestoreLatchV0817 ? window.__h18HistoryRestoreLatchV0817.selectionKey() : '',
      marker: document.documentElement.getAttribute('data-h18-v0817-history-latch')
    };
  });
}

test('trusted edit immediately before Undo cannot punch through restore latch', async ({ page }) => {
  await boot(page);

  await page.locator('#editor-field').fill('ændring før undo');
  expect((await state(page)).trusted).toBe(true);

  await page.locator('#h18-editor-undo').click();
  let current = await state(page);
  expect(current.marker).toBe('1');
  expect(current.latched).toBe(true);
  expect(current.suppressed).toBe(true);
  expect(current.trusted).toBe(false);

  // Old v0.8.16 suppression expired after 520 ms. The v0.8.17 latch must still
  // suppress restore fallout until a genuinely new user edit occurs.
  await page.waitForTimeout(700);
  current = await state(page);
  expect(current.latched).toBe(true);
  expect(current.suppressed).toBe(true);

  await page.evaluate(() => {
    window.jQuery('#editor-field').val('syntetisk restore').trigger('input').trigger('change');
  });
  current = await state(page);
  expect(current.latched).toBe(true);
  expect(current.suppressed).toBe(true);

  await page.locator('#editor-field').fill('ny rigtig ændring');
  current = await state(page);
  expect(current.latched).toBe(false);
  expect(current.trusted).toBe(true);
  expect(current.suppressed).toBe(false);
});

test('Ctrl+Z starts the same restore latch even inside the old trusted window', async ({ page }) => {
  await boot(page);

  await page.locator('#editor-field').fill('hurtig ændring');
  expect((await state(page)).trusted).toBe(true);

  await page.locator('#h18-editor-undo').focus();
  await page.keyboard.press('Control+z');

  const current = await state(page);
  expect(current.latched).toBe(true);
  expect(current.suppressed).toBe(true);
  expect(current.trusted).toBe(false);
});

test('Undo preserves the currently selected element instead of historical Inspector selection', async ({ page }) => {
  await boot(page);

  // Mimic base editorHistoryRestore selecting the historical snapshot element B
  // during the Undo bubble handler. v0.8.17 captured A in the capture phase and
  // must restore A afterwards without treating the programmatic click as an edit.
  await page.evaluate(() => {
    document.getElementById('h18-editor-undo').addEventListener('click', () => {
      document.querySelectorAll('.h18-page-section-row').forEach((row) => row.classList.remove('is-selected'));
      document.getElementById('row-b').classList.add('is-selected');
    });
  });

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(220);

  await expect(page.locator('#row-a')).toHaveClass(/is-selected/);
  await expect(page.locator('#row-b')).not.toHaveClass(/is-selected/);
  const current = await state(page);
  expect(current.selectionKey).toBe('row-a-key');
  expect(current.latched).toBe(true);
});
