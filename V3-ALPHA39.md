# Visual Designer Manager V3 — Alpha.39

Version: `3.0.0-alpha.39`

## Scope

Alpha.39 fixes defects found in a full test of Alpha.38 in a real WordPress installation (WordPress 6.8, PHP 8.x). It is built from Alpha.38 by `.github/scripts/build_v3_alpha39.py`.

## 1. Text elements lost everything after the first letter

Typing in a text element kept only the first character. The Inspector scroll/focus preservation (`editor-v0114.js`) moved focus back to the hidden text field after every Inspector rebuild, even while the rich text editor still had focus. The blur committed the field and rebuilt the Inspector.

Focus is now restored only when the field the user worked in was replaced and nothing else in the Inspector is focused. Separately, the rich text editor's deferred selection prime (`editor-v0125.js`) is now skipped when the user has already typed, so it can no longer select and overwrite new text.

## 2. Arrow keys did not move the element after editing a field

After changing a value in the Inspector (e.g. Skriftstørrelse) and clicking an element on the canvas, focus jumped back into the Inspector field and the arrow keys changed the value instead of moving the element. A click on the canvas now commits and releases the Inspector field, and the focus restore leaves focus alone when the selection changed.

## 3. A new Menu was invisible on a light background

The Menu element defaulted to white text (made for the dark V1 header). On the white default header, the desktop menu items and the mobile hamburger were invisible. A new Menu now picks a readable text colour from the background it is placed on: dark (`#30382a`) on light backgrounds, white on dark ones.

## 4. Import turned an existing image into a page

`get_page_by_path()` also returns attachments. Importing a site package with page `aktiviteter` into a site with an image `aktiviteter.jpg` overwrote the image with the page. All page lookups now use `vdm_page_by_path()`, which only returns real pages. The imported page is created next to the image (WordPress gives it a unique slug).

## 5. Import / restore was unreachable

The import page (`vdm-transfer`) is hidden from the menu, and nothing linked to it. Backup and Eksport now link to **Gendan / importér**.

## 6. PHP 8.1 deprecations on every admin page

Hidden admin routes were registered with a `null` parent and had no title, producing deprecation notices in the log on every admin page. They now use an empty parent and get a proper title.

## Acceptance

1. Type a heading and several paragraphs in a text element at normal speed: the full text is shown, is kept after **Gem**, and is shown on the website.
2. Change Skriftstørrelse in the Inspector, click the element on the canvas and press an arrow key: the element moves.
3. In Header / Footer, drag a new Menu into a white section: the menu items are dark, and the hamburger is visible on mobile.
4. Import a site package into a site with an image whose slug equals a page slug: the image still exists afterwards.
5. Backup and Eksport show a link to **Gendan / importér**.
6. `debug.log` shows no `Deprecated` lines from the admin pages.
