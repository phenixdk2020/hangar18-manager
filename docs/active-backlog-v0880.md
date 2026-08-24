# Hangar18 Manager — canonical backlog delta v0.8.80

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.80 testkandidat under build  
**Extends:** `docs/active-backlog-v0879.md`

Denne fil er den aktuelle canonical backlog. Den arver v0.8.78-masteren via v0.8.79 og overskriver kun status for denne batch.

## Batchstatus

Denne batch arbejder på **23 backlog-ID’er**. De kendte `LEGO-SELECTION-075`, `LEGO-INSIDE-075` og `LEGO-REPAINT-062` er fortsat frosset; Navigator/Move er et separat deterministisk værktøjslag og ændrer ikke canvas drag/drop-semantikken.

# E. WhatIf cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| WHATIF-CLEANUP-001 | Høj | 🟡 AUDIT FÆRDIG / SOURCE REMOVAL NÆSTE | Installeret admin-runtime har read-only cleanup-panel på Opdateringer, og repository-audit måler WhatIf runtime-referencer uden writes. Selve source-removal fortsætter i næste sikre batch. |
| WHATIF-014 | Høj | 🟡 BASELINE QA v0.8.80 | `tools/legacy-cleanup-audit.py` tæller WhatIf-referencer separat fra shim og gør reduktionen målbar i CI; DoD=0 aktive runtime-referencer er endnu ikke nået. |

# F. PowerShell / legacy bootstrap / gammel runtime cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGACY-POWERSHELL-CLEANUP-001 | Høj | 🟡 AUDIT FÆRDIG v0.8.80 | Opdateringer viser read-only installed-runtime audit af plugin/uploads for `.ps1`, bootstrap-artifacts og legacy options; ingen automatisk sletning. |
| LEGACY-002 | Høj | ✅ AUTOMATISK QA v0.8.80 | CI fejler på `.ps1` i repository/source, mens release-integrity denylist fortsat beskytter ZIP. Installeret runtime vises separat i auditpanelet. |
| LEGACY-003 | Høj | ✅ AUTOMATISK QA + MANUEL RUNTIME AUDIT v0.8.80 | CI fejler på VehicleRegister/bootstrap JSON artifacts i source; admin audit scanner også faktisk plugin/uploads. |
| LEGACY-004 | Høj | 🟡 AUDIT FÆRDIG v0.8.80 | Admin audit viser kendte bootstrap/config-import/baseline/repair WordPress-options som findes/ikke findes. |
| LEGACY-005 | Høj | 🟡 KLASSIFICERET v0.8.80 | Legacy options klassificeres som aktiv data, migration/baseline eller one-time repair-kandidat; ingen option slettes uden senere backup/QA. |

# H. LEGO Navigator, selection og produktivitets-UX

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGO-NAV-001 | Kritisk | 🟡 MANUEL TEST v0.8.80 | Nyt flydende hierarkisk Navigator-panel bygger `Side → parent → children` direkte fra canonical rows + `LayoutParentKey`; ingen parallel data-model. |
| LEGO-NAV-002 | Høj | 🟡 MANUEL TEST v0.8.80 | Klik i Navigator bruger eksisterende selection API/Inspector-handoff til den samme canonical key. |
| LEGO-NAV-003 | Høj | 🟡 MANUEL TEST v0.8.80 | Canvas/Inspector selection læses tilbage via existing `activeSelection()`/selected row og synkroniserer Navigator-highlight. |
| LEGO-NAV-004 | Høj | 🟡 MANUEL TEST v0.8.80 | Containere kan foldes/udfoldes; state gemmes browser-lokalt. |
| LEGO-NAV-007 | Høj | 🟡 MANUEL TEST v0.8.80 | Breadcrumb `Side › parent › element` vises og ancestors kan vælges. |
| LEGO-NAV-008 | Normal | 🟡 MANUEL TEST v0.8.80 | Søgning matcher label, type og key og beholder relevante parentgrene. |
| LEGO-NAV-010 | Normal | 🟡 MANUEL TEST v0.8.80 | Inaktive/skjulte rows vises dæmpet med status i Navigator i stedet for at forsvinde. |
| LEGO-MOVE-001 | Kritisk | 🟡 MANUEL TEST v0.8.80 | `Flyt til…` skriver eksisterende `LayoutParentKey`/select, flytter canonical row og kalder nesting refresh; ingen canvas drag/drop kræves. |
| LEGO-MOVE-002 | Høj | 🟡 MANUEL TEST v0.8.80 | `Flyt ud` flytter valgt element ét parentniveau op. |
| LEGO-MOVE-003 | Høj | 🟡 MANUEL TEST v0.8.80 | `Før`/`Efter` flytter valgt element relativt til sibling i samme parent. |
| LEGO-MOVE-004 | Høj | 🟡 MANUEL TEST v0.8.80 | `Til top`/`Til bund` ændrer sibling-order via eksisterende flat order fields. |
| LEGO-MOVE-005 | Høj | 🟡 MANUEL TEST v0.8.80 | Parent-picker viser kun container/flex/grid targets som er gyldige; self/descendant cycles og for dyb nesting blokeres; Auto-kasser accepterer kun Kasse. |

# N. Canvas og editor workspace

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| CANVAS-007 | Normal | 🟡 MANUEL TEST v0.8.80 | Navigator har browser-local toggle til at vise outline på alle container/grid/flex previews uden at ændre side-state. |
| WORKSPACE-003 | Normal | 🟡 DELVIST v0.8.80 | Navigator collapse/fold og container-outline gemmes pr. browser; øvrige workspace rail-bredder/layout-state er stadig åbne. |

# W. Testing og QA automation

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| QA-004 | Høj | 🟡 TESTPLAN KLAR v0.8.80 | `docs/lego-navigator-v0880-test.md` har 20-trins acceptance for Navigator/Move inkl. cycle/Auto-kasser/regression/trace evidence; faktisk browser-PASS mangler. |
| QA-020 | Normal | 🟡 DELVIST v0.8.80 | Governance CI kører `node --check` på Navigator og PHP lint på nye controllere/Autoload samt static Navigator contract; fuld lint af alle historiske editor-assets er stadig åben. |

# Næste batch efter v0.8.80

1. Manuel smoke-test af Navigator/Move på test2 med `docs/lego-navigator-v0880-test.md`.
2. Start den faktiske WhatIf source-removal i domæne-batches med Vehicle/Event/Gallery semantics beskyttet.
3. Fortsæt legacy cleanup fra audit-resultatet: backup → dokumenteret dødt state → kontrolleret fjernelse.
4. Udbyg Navigator med context menu/copy/duplicate først efter core Navigator/Move smoke-test.
5. De tre frosne canvas-runtimebugs genåbnes kun med TRACE evidence.
