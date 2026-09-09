# Visual Designer Manager V3 — Alpha.30

Version: `3.0.0-alpha.30`

## Scope

Alpha.30 is a deliberately narrow **Footer-only visual parity pass** based on the V1/V3 mobile comparison from 2026-09-09.

Header and page sections are accepted as current reference and are not changed in this version.

## Footer mobile parity

Alpha.29 fixed the semantic stacking order of the three Desktop Footer columns, but the grouped stack added more vertical whitespace than the approved V1 mobile Footer.

Alpha.30 therefore keeps the same canonical Footer nodes and order, while tightening only the mobile visual rhythm:

1. Brand
2. Description
3. Genveje
4. Live Website-menu shortcuts
5. Foreningen
6. Bliv medlem
7. Kontakt
8. Divider
9. Copyright

### Spacing

The grouped top margins are reduced to a more compact V1-like rhythm:

- Brand: 0 px
- Description: 8 px
- Genveje heading: 20 px
- Website-menu: 6 px
- Foreningen heading: 20 px
- Bliv medlem: 10 px
- Kontakt: 8 px
- Divider: 20 px
- Copyright: 12 px

The already measured V1 outer Footer padding from Alpha.24 remains `32px 15px 20px`.

### Text and menu

- Hidden/default inner text and paragraph margins are reset inside the Footer.
- Genveje uses 6 px vertical link gap and 1.35 line-height.
- The Footer shortcut list remains dynamic and mirrors the selected Website-menu in WordPress menu order.
- Alpha.26 V1 typography remains active: brand 18 px, descriptions/headings 14 px, copyright 11 px.

### CTA buttons

Footer CTA buttons are normalized on mobile to:

- full available width
- minimum height 44 px
- padding 11 px × 16 px
- 14 px text
- 1.25 line-height

This change is scoped only to the Footer CTA nodes.

## Preserved contracts

- V1 source remains byte-identical at commit `dc3bad403c764f4ec123a526333a781d05dde491` / source version `0.1.93`.
- Alpha.29 Event Program line-break repair remains active.
- Alpha.29 linked Event-gallery action remains active.
- Alpha.29 semantic Footer grouping remains active.
- Alpha.28 Desktop-master Mobile layout remains active.
- Alpha.27 canonical paint source remains active.
- Alpha.26 Website-menu Footer shortcut binding remains active.
- Alpha.22 Header hamburger/menu controller remains active.

## Acceptance

After installation on test4, verify on the same mobile viewport used for the V1/V3 screenshots:

- Header is unchanged from Alpha.29.
- Page sections and their spacing are unchanged from Alpha.29.
- Footer is visibly more compact and closer to V1.
- Brand/description, Genveje/menu and Foreningen/buttons read as three coherent groups.
- Footer menu items do not gain extra paragraph/link padding.
- Bliv medlem and Kontakt have consistent full-width mobile geometry.
- Divider and copyright sit closer to the CTA group without excess dead space.
- Footer Genveje exactly mirror the selected Website-menu; a different number of menu items is not treated as a layout defect.
