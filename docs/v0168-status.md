# Visual Designer Manager v0.1.68 – Canvas/Section Structure

Status: TESTKANDIDAT

## Scope
- VD-CANVAS-SECTION-001: root kun Sektioner.
- Automatisk persistent migration af eksisterende Designer-sider med rå backup, ID-verifikation og rollback.
- JavaScript runtime-normalisering af add/paste/re-parent.
- VD-SELECTION-LAYER-001: valgt/drag/resize øverst kun i editoren.
- Køretøjsmodulet er flyttet til v0.1.69 og er ikke del af denne release.

## Migration
Første admin-request efter opdatering gennemgår sider med `_h18_clean_layout_v1`. Kun sider der bryder hierarchy-kontrakten gemmes på ny. Hver berørt side får `_h18_clean_layout_pre_section_v0168` samt en ny Designer-version med note `Automatisk migrering til Section-struktur (v0.1.68)`.

## QA
- Alle eksisterende regressionstests skal være grønne.
- Hierarchy-normalisering skal være idempotent.
- Alle oprindelige node-ID'er skal overleve migreringen.
- Root må efter normalisering kun indeholde `section`.
- Nested `section` må ikke overleve som `section`; den bliver `container`.
- Selected/drag/resize layer må ikke ændre Renderer eller canonical `zIndex`.
