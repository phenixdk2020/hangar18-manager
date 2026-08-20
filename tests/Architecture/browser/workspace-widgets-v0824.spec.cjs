const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const runtimePath = path.resolve(__dirname, '../../../assets/ultimate-designer-workspace-widgets.js');
const jqueryRuntime = require.resolve('jquery');

async function boot(page, width = 1440) {
  await page.setViewportSize({ width, height: 900 });
  await page.setContent(`<!doctype html><html><body>
    <div class="h18-pages-admin">
      <div class="h18-visual-builder">
        <aside class="h18-builder-palette"><div class="palette-content">Elementer</div></aside>
        <main class="h18-builder-canvas">Canvas</main>
        <aside class="h18-builder-inspector"><div class="inspector-content">Inspector</div></aside>
      </div>
    </div>
  </body></html>`);
  await page.addScriptTag({ path: jqueryRuntime });
  await page.addScriptTag({ content: fs.readFileSync(runtimePath, 'utf8') });
  await page.waitForFunction(() => document.querySelectorAll('[data-h18-workspace-widget]').length === 2);
}

test('left and right workspace panels collapse independently and reopen', async ({ page }) => {
  await boot(page);
  const workspace = page.locator('.h18-visual-builder');
  const palette = page.locator('.h18-builder-palette');
  const inspector = page.locator('.h18-builder-inspector');

  await page.locator('[data-h18-workspace-collapse="left"]').click();
  await expect(workspace).toHaveClass(/h18-workspace-left-collapsed/);
  await expect(palette).toHaveAttribute('data-h18-workspace-collapsed', '1');
  await expect(inspector).toHaveAttribute('data-h18-workspace-collapsed', '0');

  await page.locator('[data-h18-workspace-collapse="right"]').click();
  await expect(workspace).toHaveClass(/h18-workspace-left-collapsed/);
  await expect(workspace).toHaveClass(/h18-workspace-right-collapsed/);
  await expect(inspector).toHaveAttribute('data-h18-workspace-collapsed', '1');

  await page.locator('[data-h18-workspace-expand="left"]').click();
  await expect(workspace).not.toHaveClass(/h18-workspace-left-collapsed/);
  await expect(workspace).toHaveClass(/h18-workspace-right-collapsed/);
});

test('workspace state is browser-local and restored on desktop', async ({ page }) => {
  await boot(page);
  await page.locator('[data-h18-workspace-collapse="left"]').click();
  await page.locator('[data-h18-workspace-collapse="right"]').click();
  const stored = await page.evaluate(() => localStorage.getItem('hangar18UltimateDesignerWorkspaceWidgetsV0824'));
  expect(JSON.parse(stored)).toEqual({ left: true, right: true });
});

test('tablet/mobile never forces collapsed rails', async ({ page }) => {
  await boot(page, 1000);
  await page.locator('[data-h18-workspace-collapse="left"]').click();
  await page.locator('[data-h18-workspace-collapse="right"]').click();
  await expect(page.locator('.h18-builder-palette')).toHaveAttribute('data-h18-workspace-collapsed', '0');
  await expect(page.locator('.h18-builder-inspector')).toHaveAttribute('data-h18-workspace-collapsed', '0');
});
