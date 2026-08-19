const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const boxContentRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-box-content-layout.js');
const editorLayoutController = path.resolve(__dirname, '../../../src/Admin/EditorLayoutToolsAdminController.php');
const jqueryRuntime = require.resolve('jquery/dist/jquery.min.js');

function historyGuardScript() {
  const source = fs.readFileSync(editorLayoutController, 'utf8');
  const match = source.match(/private static function enqueueEditorHistoryGuardV0813\(\): void[\s\S]*?\$before = <<<'JS'\n([\s\S]*?)\nJS;\n\s*wp_add_inline_script\('hangar18-manager-admin'/);
  if (!match) {
    throw new Error('Could not extract editor history guard from EditorLayoutToolsAdminController.php');
  }
  return match[1];
}

async function bootHistoryGuard(page) {
  await page.setContent(`<!doctype html><html><body>
    <div class="h18-visual-builder">
      <form id="h18-page-editor-form">
        <button id="h18-editor-undo" type="button">Fortryd</button>
        <button id="h18-editor-redo" type="button">Gendan</button>
        <button id="h18-editor-restore-draft" type="button">Gendan lokal kladde</button>
        <input id="editor-field" value="før">
        <button class="h18-page-section-drag" type="button">Flyt</button>
        <div id="h18-page-sections-sortable"></div>
        <div id="h18-page-inspector-target"></div>
      </form>
    </div>
    <div id="h18-command-palette">
      <input id="h18-command-palette-search">
      <div id="h18-command-palette-results">
        <button id="cmd-undo" class="h18-command-result is-active" type="button"><span class="h18-command-result-main">Fortryd</span></button>
        <button id="cmd-redo" class="h18-command-result" type="button"><span class="h18-command-result-main">Gendan</span></button>
        <button id="cmd-other" class="h18-command-result" type="button"><span class="h18-command-result-main">Tilføj tekst</span></button>
      </div>
    </div>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ content: historyGuardScript() });
  await page.addScriptTag({ path: boxContentRuntime });
  await page.waitForFunction(() => Boolean(window.__h18HistoryInteractionGuardV0816));
}

async function suppressionState(page) {
  return page.evaluate(() => {
    const guard = window.__h18HistoryTransactionV0814;
    return {
      suppressed: Boolean(guard && guard.isSuppressed()),
      trusted: Boolean(guard && guard.hasTrustedEdit && guard.hasTrustedEdit()),
      marker: document.documentElement.getAttribute('data-h18-v0816-history-guard')
    };
  });
}

test('command palette Undo starts the same restore transaction as toolbar Undo', async ({ page }) => {
  await bootHistoryGuard(page);
  await page.locator('#cmd-undo').click();
  const state = await suppressionState(page);
  expect(state.marker).toBe('1');
  expect(state.suppressed).toBe(true);
  expect(state.trusted).toBe(false);
});

test('command palette keyboard Redo and local draft restore are guarded', async ({ page }) => {
  await bootHistoryGuard(page);

  await page.waitForTimeout(560);
  await page.evaluate(() => {
    document.querySelectorAll('.h18-command-result').forEach((node) => node.classList.remove('is-active'));
    document.getElementById('cmd-redo').classList.add('is-active');
    document.getElementById('h18-command-palette-search').focus();
  });
  await page.keyboard.press('Enter');
  expect((await suppressionState(page)).suppressed).toBe(true);

  await page.waitForTimeout(560);
  await page.locator('#h18-editor-restore-draft').click();
  expect((await suppressionState(page)).suppressed).toBe(true);
});

test('synthetic restore events stay suppressed but real post-Undo input is history-eligible', async ({ page }) => {
  await bootHistoryGuard(page);
  await page.locator('#h18-editor-undo').click();
  expect((await suppressionState(page)).suppressed).toBe(true);

  await page.evaluate(() => {
    window.jQuery('#editor-field').val('syntetisk').trigger('input').trigger('change');
  });
  const synthetic = await suppressionState(page);
  expect(synthetic.suppressed).toBe(true);
  expect(synthetic.trusted).toBe(false);

  await page.locator('#editor-field').fill('rigtig brugerændring');
  const trusted = await suppressionState(page);
  expect(trusted.trusted).toBe(true);
  expect(trusted.suppressed).toBe(false);
});

test('a real drag-handle interaction immediately after Undo is not lost', async ({ page }) => {
  await bootHistoryGuard(page);
  await page.locator('#h18-editor-undo').click();
  expect((await suppressionState(page)).suppressed).toBe(true);

  await page.locator('.h18-page-section-drag').click();
  const state = await suppressionState(page);
  expect(state.trusted).toBe(true);
  expect(state.suppressed).toBe(false);
});
