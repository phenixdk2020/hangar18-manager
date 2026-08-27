# Visual Designer Manager 0.1.32 – Status

Dato: 27. august 2026

## Scope

- VD-TEXT-SEL-001: robust selection efter Fed/Kursiv/Understregning.
- VD-BUTTON-TYPE-001: canonical Button-type + tydelig feedback ved hierarchy-afvist root-drop.
- VD-INSPECTOR-SCROLL-001: 360 px editor-only bund-buffer.
- VD-FLOAT-001: regression-gate for parent-relativ floating.

## Bevidst ikke med i denne patch

Tabel, Divider, Spacer, Icon, Hero/Topbanner, Menu og øvrige større nye elementtyper forbliver planlagte featurepakker. 0.1.32 er en kontrakt-/fejlrettelsesrelease.

## QA-gates

- PHP syntax på hele pluginet.
- JavaScript syntax på alle aktive editor-assets.
- HierarchyNormalizer + LayoutModel regression-QA.
- v0.1.32 asset/enqueue/version checks.
- Selection-hærdning og Button-type/drop-feedback findes i aktiv late patch.
- Inspector 360 px buffer findes kun som editor CSS.
- Floating-kontrakten findes fortsat i core/responsive/frontend.
