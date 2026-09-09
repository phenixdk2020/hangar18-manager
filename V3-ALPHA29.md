# Visual Designer Manager V3 — Alpha.29

Version: `3.0.0-alpha.29`

## Scope

Alpha.29 is deliberately narrow. It preserves the Alpha.28 Desktop-master responsive layout and fixes the remaining Event-detail and mobile Footer issues reported from V3 screenshots.

### Event Program line breaks

The canonical `Program` Event field now has a dedicated renderer that preserves real CR/LF, escaped `\\r\\n` / `\\n` / `\\r`, and repairs the historical literal `rn` delimiter only when it occurs immediately before a clock value. It does **not** globally replace the letters `rn` in ordinary text.

### Event gallery action

Events already store an optional `galleryRecordId` through **Manager → Events → Tilknyttet album**. Alpha.29 exposes that existing relation on V3 event details. When the linked album is published, a button is rendered after the canonical **Praktiske oplysninger** block:

`Se billeder fra arrangementet – [eventtitel]`

If no published album is linked, no gallery button is rendered.

### Footer mobile grouping

Alpha.28 correctly made Desktop the placement master, but a three-column Desktop Footer cannot be stacked by one global Y sort: that interleaves nodes from the Brand, Genveje and Foreningen columns. Alpha.29 keeps the same canonical nodes and stacks the Desktop Footer columns as complete responsive groups:

1. Brand
2. Description
3. Genveje
4. Live Website-menu shortcuts
5. Foreningen
6. Bliv medlem
7. Kontakt
8. Divider
9. Copyright

The shortcut items themselves remain dynamic and continue to follow the selected Website-menu and its WordPress menu order.

## Preserved contracts

- V1 source remains byte-identical at commit `dc3bad403c764f4ec123a526333a781d05dde491` / source version `0.1.93`.
- Alpha.28 Desktop-master Mobile layout inheritance remains active.
- Alpha.27 canonical paint source remains active.
- Alpha.26 Website-menu Footer shortcut binding remains active.
- Alpha.22 Header hamburger/menu controller remains active.

## Acceptance

After installation on test4, verify:

- Program entries display on separate lines.
- Choosing a published **Tilknyttet album** on an Event produces the gallery button; clearing it removes the button.
- Mobile Footer order is Brand/description → Genveje/menu → Foreningen/buttons → copyright.
- Footer Genveje exactly mirror the currently selected Website-menu.
- Header and general page layout remain unchanged from Alpha.28.
