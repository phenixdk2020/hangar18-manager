const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../assets/ultimate-designer-lego-selection-inspector-v0849.js');

async function boot(page) {
  await page.setContent(`<!doctype html><html><body>
    <div class="h18-builder-canvas">
      <div id="h18-page-sections-sortable">
        <section id="row-auto" class="h18-page-section-row" data-section-type="grid">
          <header class="h18-page-section-header">Grid</header>
          <div class="h18-canvas-preview">
            <div id="grid-live">
              <section class="h18-v0811-auto-box" data-h18-v0811-row="image-1"><strong>Billede</strong></section>
              <section class="h18-v0811-auto-box" data-h18-v0811-row="text-1"><strong>Overskrift</strong></section>
            </div>
          </div>
          <div class="h18-page-section-body"><input class="h18-page-section-key" value="auto-1"></div>
        </section>
        <section id="row-image" class="h18-page-section-row" data-section-type="image">
          <header class="h18-page-section-header">Billede</header>
          <div class="h18-canvas-preview">Billede</div>
          <div class="h18-page-section-body"><input class="h18-page-section-key" value="image-1"></div>
        </section>
        <section id="row-text" class="h18-page-section-row" data-section-type="text">
          <header class="h18-page-section-header">Tekst</header>
          <div class="h18-canvas-preview">Tekst</div>
          <div class="h18-page-section-body"><input class="h18-page-section-key" value="text-1"></div>
        </section>
      </div>
    </div>
    <aside id="h18-page-inspector">
      <div id="h18-page-inspector-target">
        <div class="h18-page-section-body">
          <div id="normal-a"><strong>Indhold</strong><input value="a"></div>
          <div id="dynamic"><strong>Dynamic data binding</strong><input id="dynamic-value" value="vehicle.title"></div>
          <div id="normal-b"><strong>Design</strong><input value="b"></div>
          <div id="conditions"><strong>Conditions / synlighed</strong><input id="condition-value" value="logged_in"></div>
        </div>
      </div>
    </aside>
  </body></html>`);

  // Reproduce the base Inspector handoff and a later Grid repaint that replaces
  // the selected visual tile and drops transient CSS classes.
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const tile = event.target.closest('.h18-v0811-auto-box[data-h18-v0811-row]');
      if (!tile) return;
      const key = tile.getAttribute('data-h18-v0811-row');
      document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row').forEach(row => row.classList.remove('is-selected'));
      const row = document.querySelector('#row-' + (key === 'image-1' ? 'image' : 'text'));
      row.classList.add('is-selected');
      row.setAttribute('data-key', key);
      const body = row.querySelector('.h18-page-section-body');
      const target = document.querySelector('#h18-page-inspector-target');
      target.innerHTML = '';
      target.appendChild(body);

      window.setTimeout(() => {
        row.classList.remove('is-selected');
        document.querySelector('#grid-live').innerHTML = `
          <section class="h18-v0811-auto-box" data-h18-v0811-row="image-1"><strong>Billede repaint</strong></section>
          <section class="h18-v0811-auto-box" data-h18-v0811-row="text-1"><strong>Overskrift repaint</strong></section>`;
      }, 120);
    }, false);
  });

  await page.addScriptTag({ content: fs.readFileSync(runtimePath, 'utf8') });
  await page.waitForFunction(() => Boolean(window.__h18LegoSelectionInspectorV0849));
}

test('LEGO-049 selected nested element stays marked after late Grid repaint', async ({ page }) => {
  await boot(page);
  await page.locator('.h18-v0811-auto-box[data-h18-v0811-row="image-1"]').click();

  await page.waitForTimeout(700);
  const repainted = page.locator('.h18-v0811-auto-box[data-h18-v0811-row="image-1"]');
  await expect(repainted).toHaveClass(/is-h18-v0848-selected-element/);
  await expect(page.locator('.h18-v0811-auto-box[data-h18-v0811-row="text-1"]')).not.toHaveClass(/is-h18-v0848-selected-element/);
});

test('LEGO-049 dynamic binding and conditions move below normal Inspector controls', async ({ page }) => {
  await boot(page);
  await page.waitForTimeout(100);

  const order = await page.locator('#h18-page-inspector-target > .h18-page-section-body').evaluate((root) =>
    Array.from(root.children).map((node) => node.id || node.className)
  );

  expect(order).toEqual([
    'normal-a',
    'normal-b',
    'h18-v0849-advanced-heading',
    'dynamic',
    'conditions'
  ]);
  await expect(page.locator('#dynamic-value')).toHaveValue('vehicle.title');
  await expect(page.locator('#condition-value')).toHaveValue('logged_in');
  await expect(page.locator('.h18-v0849-advanced-heading')).toContainText('Avanceret');
});
