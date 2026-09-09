# Visual Designer Manager V3 — Alpha.31

Version: `3.0.0-alpha.31`

## Scope

Alpha.31 adds a **module-level Footer distance** so dynamic module content cannot visually run directly into the Footer.

The setting is shared by:

- Events
- Billedgalleri
- Køretøjer og materiel

and applies to both each module's overview page and its dynamic detail page.

## New Moduldesign setting

Under the module page's **Moduldesign** panel there is now:

**Afstand til Footer (px)**

Range: `0–200 px`  
Default: `64 px`

The value is versioned together with the existing Module Design settings and is restored by the existing version restore flow.

## Runtime behavior

### Module overview

The canonical `CollectionPageRenderer` uses the configured Footer distance as bottom padding. The iframe preview and public module overview therefore use the same value and the same renderer.

### Dynamic detail pages

The Visual Designer detail pages:

- `event-detalje`
- `album-detalje`
- `koeretoej-detalje`

resolve their owning collection page and read its Module Design Footer distance.

For these detail pages the space is reserved inside the page shell before the Footer. This is important for dynamic Event content such as the optional linked-gallery button after **Praktiske oplysninger**, which may extend farther than the original static detail geometry.

## Preserved behavior

- Ordinary Visual Designer pages continue to use **Sideindstillinger → Afstand til Footer** with Desktop/Laptop/Tablet/Mobil values.
- Alpha.30 Footer layout and spacing are unchanged.
- Alpha.29 Event Program line-break repair is unchanged.
- Alpha.29 linked Event-gallery button is unchanged.
- Footer Genveje continue to mirror the selected Website-menu.
- Header and page section layout are unchanged.

## Acceptance

After installation on test4:

1. Open the `Events` page in Visual Designer.
2. Choose **Moduldesign**.
3. Verify the new **Afstand til Footer (px)** field; default is 64.
4. Save a new version.
5. Open an Event detail containing a linked gallery button.
6. Verify there is visible space between the last Event content/button and the Footer.
7. Change the value, e.g. 32 / 80 / 120 px, save, and verify the detail page follows the setting.
8. Verify the Footer itself, Header, and ordinary pages have not changed.
