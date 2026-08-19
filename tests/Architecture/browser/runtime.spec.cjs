const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const siteBuilder = path.resolve(__dirname, '../../../assets/site-builder-runtime.js');
const interaction = path.resolve(__dirname, '../../../assets/interaction-runtime.js');
const nestingRuntime = path.resolve(__dirname, '../../../assets/ultimate-designer-nesting-tools.js');
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

test('menu supports mobile toggle, arrows, submenu and Escape', async ({ page }) => {
  await page.setContent(`<!doctype html><html><body>
    <div data-h18-menu-shell>
      <button class="h18-menu-mobile-toggle" aria-expanded="false">Menu</button>
      <nav data-h18-menu>
        <ul class="h18-menu-list--root">
          <li class="h18-menu-item"><a id="home" class="h18-menu-link" href="#home">Hjem</a></li>
          <li class="h18-menu-item"><a id="about" class="h18-menu-link" href="#about">Om</a><button id="subtoggle" class="h18-submenu-toggle" aria-expanded="false">Undermenu</button><ul class="h18-menu-list--submenu"><li><a id="child" href="#child">Barn</a></li></ul></li>
          <li class="h18-menu-item"><a id="contact" class="h18-menu-link" href="#contact">Kontakt</a></li>
        </ul>
      </nav>
    </div></body></html>`);
  await page.addScriptTag({ path: siteBuilder });

  const shell = page.locator('[data-h18-menu-shell]');
  const mobile = page.locator('.h18-menu-mobile-toggle');
  await mobile.click();
  await expect(shell).toHaveClass(/is-mobile-open/);
  await expect(mobile).toHaveAttribute('aria-expanded', 'true');

  await page.locator('#home').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#about')).toBeFocused();
  await page.keyboard.press('ArrowLeft');
  await expect(page.locator('#home')).toBeFocused();

  await page.locator('#subtoggle').focus();
  await page.keyboard.press('ArrowDown');
  await expect(page.locator('#subtoggle')).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('#child')).toBeFocused();

  await page.keyboard.press('Escape');
  await expect(shell).not.toHaveClass(/is-mobile-open/);
  await expect(mobile).toHaveAttribute('aria-expanded', 'false');
  await expect(page.locator('#subtoggle')).toHaveAttribute('aria-expanded', 'false');
});

test('modal traps focus, closes on Escape and restores opener', async ({ page }) => {
  await page.setContent(`<!doctype html><html><body>
    <button id="opener" data-h18-actions='[{"Type":"open-modal","TargetId":"demo"}]'>Åbn</button>
    <div data-h18-modal="demo" hidden>
      <div class="h18-modal-dialog" role="dialog" aria-modal="true" tabindex="-1">
        <button id="first">Første</button><button id="last">Sidste</button>
      </div>
    </div></body></html>`);
  await page.addScriptTag({ path: interaction });

  await page.locator('#opener').click();
  const modal = page.locator('[data-h18-modal="demo"]');
  await expect(modal).toBeVisible();
  await expect(page.locator('#first')).toBeFocused();
  await expect(page.locator('body')).toHaveCSS('overflow', 'hidden');

  await page.locator('#last').focus();
  await page.keyboard.press('Tab');
  await expect(page.locator('#first')).toBeFocused();

  await page.keyboard.press('Escape');
  await expect(modal).toBeHidden();
  await expect(page.locator('#opener')).toBeFocused();
});

test('invalid form marks field and moves focus without submitting', async ({ page }) => {
  await page.setContent(`<!doctype html><html><body>
    <form data-h18-form novalidate>
      <div data-h18-field><label for="email">E-mail</label><input id="email" name="email" type="email" required><span class="h18-form-error" aria-live="polite"></span></div>
      <button type="submit">Send</button>
    </form></body></html>`);
  await page.addScriptTag({ path: interaction });
  const prevented = await page.locator('form').evaluate((form) => {
    const event = new Event('submit', { bubbles: true, cancelable: true });
    return !form.dispatchEvent(event);
  });
  expect(prevented).toBeTruthy();
  await expect(page.locator('#email')).toHaveAttribute('aria-invalid', 'true');
  await expect(page.locator('#email')).toBeFocused();
  await expect(page.locator('.h18-form-error')).not.toHaveText('');
});

test('reduced motion changes scroll action to auto', async ({ page }) => {
  await page.setContent(`<!doctype html><html><body>
    <button id="jump" data-h18-actions='[{"Type":"scroll","TargetId":"target"}]'>Hop</button>
    <div id="target">Mål</div></body></html>`);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.locator('#target').evaluate((node) => {
    node.scrollIntoView = (options) => { window.__h18ScrollBehavior = options && options.behavior; };
  });
  await page.addScriptTag({ path: interaction });
  await page.locator('#jump').click();
  const behavior = await page.evaluate(() => window.__h18ScrollBehavior);
  expect(behavior).toBe('auto');
});

test('Auto-kasser keeps two Kasser visible after base preview rebuild', async ({ page }) => {
  await page.setContent(`<!doctype html><html><body>
    <div class="h18-builder-canvas"></div>
    <div id="h18-page-inspector-target"></div>
    <div id="h18-page-sections-sortable">
      <section class="h18-page-section-row" data-section-type="grid" data-section-index="1">
        <input class="h18-page-section-key" value="auto-1">
        <input class="h18-section-navigator-label" value="Auto-kasser">
        <input class="h18-layout-parent-key" value="">
        <input name="Sections[1][LayoutColumns]" value="2">
        <input name="Sections[1][LayoutGapPx]" value="16">
        <div class="h18-canvas-preview"><div class="base-preview">Auto base</div></div>
      </section>
      <section class="h18-page-section-row" data-section-type="container" data-section-index="2">
        <input class="h18-page-section-key" value="box-1">
        <input class="h18-section-navigator-label" value="Kasse">
        <input class="h18-layout-parent-key" value="auto-1">
        <div class="h18-canvas-preview"><div class="base-preview">Kasse A</div></div>
      </section>
      <section class="h18-page-section-row" data-section-type="container" data-section-index="3">
        <input class="h18-page-section-key" value="box-2">
        <input class="h18-section-navigator-label" value="Kasse">
        <input class="h18-layout-parent-key" value="auto-1">
        <div class="h18-canvas-preview"><div class="base-preview">Kasse B</div></div>
      </section>
    </div>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ path: nestingRuntime });

  const autoRow = page.locator('.h18-page-section-row[data-section-type="grid"]');
  await expect(autoRow.locator('.h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 2000 });
  await expect(page.locator('.h18-page-section-row[data-section-index="2"]')).toHaveAttribute('data-h18-v0811-child-source', '1');
  await expect(page.locator('.h18-page-section-row[data-section-index="3"]')).toHaveAttribute('data-h18-v0811-child-source', '1');
  await expect(autoRow.locator('.h18-v0811-runtime-badge').first()).toHaveText('v0.8.15');

  await autoRow.locator('.h18-canvas-preview').evaluate((preview) => {
    preview.innerHTML = '<div class="base-preview">Base editor rebuilt this preview</div>';
  });

  await expect(autoRow.locator('.h18-ud-auto-box-grid > .h18-v0811-auto-box')).toHaveCount(2, { timeout: 2000 });
});

test('Undo restore guard discards derived history capture instead of replaying it later', async ({ page }) => {
  await page.setContent(`<!doctype html><html><body>
    <button id="h18-editor-undo" type="button">Fortryd</button>
    <form id="h18-page-editor-form"><div id="history-host"></div></form>
  </body></html>`);
  await page.addScriptTag({ content: historyGuardScript() });

  const state = await page.evaluate(async () => {
    window.__h18RecordCount = 0;
    window.__h18MutationCount = 0;
    window.editorHistoryRecordNow = function editorHistoryRecordNow() {
      window.__h18RecordCount += 1;
    };

    const form = document.getElementById('h18-page-editor-form');
    const observer = new MutationObserver(function () {
      window.__h18MutationCount += 1;
    });
    observer.observe(form, { childList: true, subtree: true });

    document.getElementById('h18-editor-undo').click();
    window.setTimeout(window.editorHistoryRecordNow, 10);
    form.appendChild(document.createElement('span'));

    await new Promise((resolve) => window.setTimeout(resolve, 620));
    const duringRestore = {
      records: window.__h18RecordCount,
      mutations: window.__h18MutationCount
    };

    form.appendChild(document.createElement('b'));
    await new Promise((resolve) => window.setTimeout(resolve, 60));

    return {
      duringRestore,
      mutationsAfterRestore: window.__h18MutationCount
    };
  });

  expect(state.duringRestore.records).toBe(0);
  expect(state.duringRestore.mutations).toBe(0);
  expect(state.mutationsAfterRestore).toBeGreaterThan(0);
});
