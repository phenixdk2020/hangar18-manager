const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const boxContentRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-box-content-layout.js');
const historyRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-history-v0818.js');
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
        <div id="h18-page-sections-sortable"></div>
        <aside id="h18-page-inspector">
          <div class="h18-builder-inspector-heading"><span>Vælg en sektion i sideopbygningen</span></div>
          <span id="h18-inspector-type">–</span><span id="h18-inspector-key">–</span>
          <button id="h18-inspector-copy-key" type="button"></button>
          <button id="h18-inspector-duplicate" type="button"></button>
          <button id="h18-inspector-copy-design" type="button"></button>
          <button id="h18-inspector-paste-design" type="button"></button>
          <button id="h18-save-section-preset" type="button"></button>
          <div id="h18-page-inspector-target"></div>
        </aside>
      </form>
    </div>
  </body></html>`);

  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ content: historyGuardScript() });
  await page.addScriptTag({ path: boxContentRuntime });
  await page.addScriptTag({ path: historyRuntime });

  await page.evaluate(() => {
    const sections = document.getElementById('h18-page-sections-sortable');
    const inspector = document.getElementById('h18-page-inspector-target');
    const heading = document.querySelector('#h18-page-inspector .h18-builder-inspector-heading span');

    function row(key, type, selected) {
      const section = document.createElement('section');
      section.className = 'h18-page-section-row' + (selected ? ' is-selected' : '');
      section.dataset.sectionType = type;
      section.innerHTML = `
        <input class="h18-page-section-key" value="${key}">
        <button class="h18-page-section-header" type="button">${key}</button>
        <div class="h18-canvas-preview">${selected ? '<div class="h18-canvas-direct-controls"><strong>Direkte design</strong></div>' : ''}</div>
        <div class="h18-page-section-body"><input value="${key}"></div>`;
      return section;
    }

    function select(key) {
      const current = sections.querySelector('.h18-page-section-row.is-selected');
      if (current) {
        const body = inspector.querySelector(':scope > .h18-page-section-body');
        if (body) current.appendChild(body);
        current.classList.remove('is-selected');
      }
      const wanted = Array.from(sections.children).find((node) => node.querySelector('.h18-page-section-key')?.value === key);
      if (!wanted) return;
      wanted.classList.add('is-selected');
      const body = wanted.querySelector(':scope > .h18-page-section-body');
      if (body) inspector.appendChild(body);
      wanted.querySelector('.h18-canvas-preview').insertAdjacentHTML('beforeend', '<div class="h18-canvas-direct-controls"><strong>Direkte design</strong></div>');
      heading.textContent = key;
    }

    document.addEventListener('click', (event) => {
      const header = event.target.closest && event.target.closest('.h18-page-section-header');
      if (header) select(header.closest('.h18-page-section-row').querySelector('.h18-page-section-key').value);
    });

    const snapshots = [
      { keys: ['text-a'], historicalSelection: 'text-a' },
      { keys: ['text-a', 'image-1'], historicalSelection: 'text-a' },
      { keys: ['text-a', 'image-1', 'image-2'], historicalSelection: 'image-2' }
    ];
    let historyIndex = 0;
    let editorHistoryTimer = null;
    let recordCount = 0;

    function renderSnapshot(snapshot) {
      const wanted = snapshot.keys;
      const existing = {};
      Array.from(sections.children).forEach((node) => {
        const key = node.querySelector('.h18-page-section-key')?.value;
        if (key) existing[key] = node;
      });
      sections.innerHTML = '';
      wanted.forEach((key) => sections.appendChild(existing[key] || row(key, key.startsWith('image') ? 'image' : 'text', false)));
      // Mimic the base editor restoring entry.selectedKey even though selection
      // is not page content.
      select(snapshot.historicalSelection);
      // Mimic a helper runtime attempting a synthetic capture after restore.
      scheduleHistory(20);
    }

    function editorHistoryRecordNow() {
      recordCount += 1;
      const keys = Array.from(sections.children).map((node) => node.querySelector('.h18-page-section-key')?.value).filter(Boolean);
      const current = snapshots[historyIndex];
      if (current && JSON.stringify(current.keys) === JSON.stringify(keys)) return;
      snapshots.splice(historyIndex + 1);
      snapshots.push({ keys, historicalSelection: current?.historicalSelection || 'text-a' });
      historyIndex = snapshots.length - 1;
    }

    function scheduleHistory(delay) {
      window.clearTimeout(editorHistoryTimer);
      editorHistoryTimer = window.setTimeout(editorHistoryRecordNow, delay == null ? 25 : delay);
    }

    function flushCorePending() {
      // This is the exact problematic admin.js contract: a stale truthy timer id
      // causes editorHistoryRecordNow() to be replayed during Undo.
      if (!editorHistoryTimer) return;
      window.clearTimeout(editorHistoryTimer);
      editorHistoryTimer = null;
      editorHistoryRecordNow();
    }

    function undo() {
      flushCorePending();
      if (historyIndex <= 0) return;
      historyIndex -= 1;
      renderSnapshot(snapshots[historyIndex]);
    }

    document.getElementById('h18-editor-undo').addEventListener('click', undo);

    sections.appendChild(row('text-a', 'text', false));
    window.__v0818Harness = {
      addImage(key) {
        sections.appendChild(row(key, 'image', false));
        select(key);
        scheduleHistory(20);
      },
      state() {
        return {
          historyIndex,
          recordCount,
          keys: Array.from(sections.children).map((node) => node.querySelector('.h18-page-section-key')?.value).filter(Boolean),
          selected: sections.querySelector('.h18-page-section-row.is-selected .h18-page-section-key')?.value || '',
          directDesign: sections.querySelectorAll('.h18-canvas-direct-controls').length,
          coreTimer: editorHistoryTimer,
          runtimePending: window.__h18HistoryRuntimeV0818.hasPending(),
          latched: window.__h18HistoryRuntimeV0818.isLatched()
        };
      }
    };
  });

  await page.waitForFunction(() => Boolean(window.__h18HistoryRuntimeV0818));
}

test('two image edits Undo once without 2 to 1 to 2 replay', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__v0818Harness.addImage('image-1'));
  await page.waitForTimeout(60);
  await page.evaluate(() => window.__v0818Harness.addImage('image-2'));
  await page.waitForTimeout(60);

  let current = await page.evaluate(() => window.__v0818Harness.state());
  expect(current.historyIndex).toBe(2);
  expect(current.keys).toEqual(['text-a', 'image-1', 'image-2']);
  // Critical contract: admin.js receives 0, so its own flush cannot replay a
  // timer that has already fired.
  expect(current.coreTimer).toBe(0);
  expect(current.runtimePending).toBe(false);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(500);

  current = await page.evaluate(() => window.__v0818Harness.state());
  expect(current.historyIndex).toBe(1);
  expect(current.keys).toEqual(['text-a', 'image-1']);
  expect(current.latched).toBe(true);
  expect(current.runtimePending).toBe(false);
});

test('Undo removing selected image clears historical Text selection and Direct design', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__v0818Harness.addImage('image-1'));
  await page.waitForTimeout(60);
  await page.evaluate(() => window.__v0818Harness.addImage('image-2'));
  await page.waitForTimeout(60);

  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(500);

  const current = await page.evaluate(() => window.__v0818Harness.state());
  expect(current.keys).toEqual(['text-a', 'image-1']);
  // image-2 was selected before Undo and no longer exists. The base restore
  // selected text-a historically; v0.8.18 must explicitly clear that UI state.
  expect(current.selected).toBe('');
  expect(current.directDesign).toBe(0);
  await expect(page.locator('#h18-page-inspector-target')).toContainText('Klik på Rediger');
});

test('a genuinely pending edit is flushed once before Undo', async ({ page }) => {
  await boot(page);

  await page.evaluate(() => window.__v0818Harness.addImage('image-1'));
  // Click Undo before the owned 20 ms timer fires. v0.8.18 capture phase must
  // flush this pending edit exactly once, then core Undo moves back to base.
  await page.locator('#h18-editor-undo').click();
  await page.waitForTimeout(250);

  const current = await page.evaluate(() => window.__v0818Harness.state());
  expect(current.historyIndex).toBe(0);
  expect(current.keys).toEqual(['text-a']);
  expect(current.runtimePending).toBe(false);
});
