const { test, expect } = require('@playwright/test');
const path = require('path');

const siteBuilder = path.resolve(__dirname, '../../../assets/site-builder-runtime.js');
const interaction = path.resolve(__dirname, '../../../assets/interaction-runtime.js');

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
