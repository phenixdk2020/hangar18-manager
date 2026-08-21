# Ultimate Designer — integration backlog after UD-120

**Statusdato:** 21. august 2026  
**Aktuel pluginbaseline:** Hangar18 Manager **v0.8.37**

UD-001..120 har architecture/core-dækning, og hovedparten af wp-admin-integrationen er implementeret. LEGO-editorens spacing, responsive design, interaction states, nested composition, Direkte Design og layout-kontroller er nu samlet på den eksisterende parent/history/persistence-arkitektur gennem v0.8.37.

**Aktiv næste slice: LEGO-030 — visuelle drop-zoner (Over / Under / Venstre / Højre) oven på den eksisterende placement-motor.**

Eksisterende Hangar18-sider er fortsat **ikke** public-cutover til en ny renderer. Automatisk QA erstatter ikke de krævede I9 live/manuelle acceptance-gates.

## Ikke-forhandlingsbare arkitekturregler

- Én drag/drop-motor.
- Én `LayoutParentKey` parent/child-model.
- Én Undo/Redo-stack og ét logisk history-checkpoint pr. brugerhandling.
- Eksisterende page-section felter forbliver persistence/public-renderer-kilden under migrationen.
- Ingen public sidekonvertering før I9 er manuelt accepteret.
- Vehicle/Event/Gallery forbliver beskyttede legacy-domæner, bortset fra eksplicit godkendte snævre fixes som EVENT-001.

## Statusoversigt

| Fase | Status | Leveret / næste |
|---|---|---|
| I1 — Admin integration / shadow dashboard | ✅ Færdig | Admin-only Ultimate Designer dashboard. |
| I2 — Visual Header/Footer Builder | ✅ Færdig i shadow/admin | Shared sections, visuel editing og preview; public assignment fortsat låst. |
| I3 — Menu Builder v2 | ✅ Færdig i shadow/admin | Nested drag/drop, presets og side include/exclude. |
| I4 — Side Health | ✅ Færdig | Live/read-only Design/Mobile/Accessibility/Performance/SEO-analyse. |
| I5 — Asset Manager | ✅ Færdig | Collections/tags/usage/focal point/derivatives/duplicates. |
| I6 — Portability | ✅ Færdig | Dry-run, signeret plan, conflict/remap, workspace og restore-point. |
| I7 — Permissions / Design Lock | ✅ Færdig | Additive capabilities/roles og design-lock policy. |
| I8 — AI | ✅ Færdig | Provider-neutral forslag uden direkte public page-write. |
| I9 — Manual QA evidence | 🟡 Framework færdigt / evidence pending | Live/browser/screen-reader/test2/rollback evidence mangler. |
| I10 — Final controlled conversion | 🟡 Preflight færdigt / cutover låst | Comparison page → Hjem → Om → Kontakt → Bliv medlem → protected domains. |
| UX-3 — Foldbare workspace rails | ✅ v0.8.24 | Elementer/Funktioner og Inspector foldes uafhængigt. |
| UX-4 — Ugemt forhåndsvisning | ✅ v0.8.25 + v0.8.27 | Preview uden save; editor chrome renses fra klonen. |
| EVENT-001 — Automatisk eventarkiv | ✅ v0.8.26 | Dynamisk Upcoming/Tidligere efter WP-lokal dato/sluttid. |
| B1 — Sidebackup restore | ✅ v0.8.28 | Replace original + copy draft + safety backup + audit. |
| B2 — Versioneret site-backup | ✅ v0.8.29 + senere LEGO-integration | ZIP/full/selective restore inkl. spacing/design/interaction snapshots. |
| LEGO spacing/responsive | ✅ v0.8.30–v0.8.31 | X/Y gap/margin + Tablet/Mobile inheritance. |
| LEGO common design | ✅ v0.8.32 | Fælles element/Kasse/Grid/Flex designmodel. |
| LEGO responsive design | ✅ v0.8.33 | Desktop/Tablet/Mobil reversible overrides. |
| LEGO interaction states | ✅ v0.8.34 | Transition + Hover/Focus/Active/Disabled. |
| LEGO consolidation/readiness | ✅ v0.8.35 | Nested Kasse/Auto-kasser + spacing/design/states + sekventiel Undo/Redo. |
| LEGO primary design view | ✅ v0.8.36 | Direkte Design bruger samme canonical design/state som Inspector. |
| LEGO primary layout view | ✅ v0.8.37 | Direkte Design/Inspector spejler layout i samme canonical row-state. |
| LEGO-030 — Visual side-drop zones | 🟢 Aktiv | Over/Under/Venstre/Højre på eksisterende placement-motor. |
| LEGO-031 — Automatic side-by-side layout | ⬜ Næste | Side-drop opretter/justerer layout uden ny parent/child-motor. |
| LEGO-032 — Visual resize / column span | ⬜ Senere | Resize oven på usynlig 12-kolonne layoutmotor. |
| LEGO-033 — Tablet/Mobile layout overrides | ⬜ Senere | Responsive span/layout uden separat motor. |
| DOC-1 — Visuel brugermanual | ⬜ Backlog | Udarbejdes når placement/resize-interaktionen er stabil. |

## Stabiliseret editorhistorik

Undo/Redo er manuelt accepteret og fortsat eneste history-owner:

- v0.8.20: load-order/preloader og strukturelle checkpoints;
- v0.8.21: live SELECT/INPUT/TEXTAREA-state gennem clone/restore;
- v0.8.22: første nye strukturelle handling efter fuld Undo/Redo;
- v0.8.23: tekst, farver og billeder som content-history checkpoints;
- v0.8.35: kombineret spacing/design/state på nested Kasse blev verificeret som sekventielle Undo/Redo-trin.

## Backup / restore

### B1 — ✅ v0.8.28

- Erstat original med safety backup før første write.
- Opret som separat draft-kopi med collision-safe slug.
- Capability, nonce, path-containment og audit.

### B2 — ✅ v0.8.29 + LEGO-integration

- immutable `H18-BACKUP-xxxxxx` ID og SHA-256 manifest/payloads;
- Hangar18-managed pages, page versions, Site Builder, forms/polls/data, options og referenced media;
- ZIP export/import med security preflight;
- signed/state-bound dry-run;
- full restore og selective page restore;
- safety backup før første mutation;
- stale-lock recovery og audit;
- v0.8.31 selective spacing restore;
- v0.8.33 responsive design restore;
- v0.8.34 interaction snapshots følger selected page;
- standard-B2 er applikationsbackup, ikke raw database/plugin/theme disaster recovery.

## LEGO-editor backlog

| ID | Status | Leverance |
|---|---|---|
| LEGO-001 — Shared object/state model | ✅ | Canonical spacing/design/interaction vocabulary. |
| LEGO-002 — Backward-compatible X/Y gap | ✅ v0.8.30 | Legacy gap seedes til X=Y. |
| LEGO-003 — Inspector separat X/Y spacing | ✅ v0.8.30 | X/Y controls. |
| LEGO-004 — Per-element margin | ✅ v0.8.30 | Responsive Margin X/Y. |
| LEGO-006 — Common element design | ✅ v0.8.32 | Typography/colors/background/border/radius/opacity/shadow/hover. |
| LEGO-009 — Consolidate Kasse design | ✅ v0.8.32 | Samme canonical design-paths for Kasse/Grid/Flex. |
| LEGO-010 — Kasse internal X/Y gap | ✅ v0.8.30 | Separate X/Y gaps. |
| LEGO-011 — Responsive spacing | ✅ v0.8.31 | Tablet/Mobile inheritance. |
| LEGO-012 — Responsive common design | ✅ v0.8.33 | Reversible responsive design snapshots. |
| LEGO-013 — Extended interaction states | ✅ v0.8.34 | Focus/Active/Disabled + transition. |
| LEGO-021 — Undo/Redo one step per action | ✅ | v0.8.20–23 owner + LEGO single-event bridges. |
| LEGO-025 — QA suite | ✅ v0.8.35 | Combined nested composition/state/history regressions. |
| LEGO-026 — Primary editor readiness | ✅ v0.8.35 | Readiness gate PASS. |
| LEGO-027 — Primary design view | ✅ v0.8.36 | Direkte Design canonical proxy til Inspector design/state. |
| LEGO-028 — Primary layout view | ✅ v0.8.37 | Remaining legacy layout controls mirrored canonical before history capture. |
| LEGO-030 — Visual side-drop zones | 🟢 Aktiv | Over/Under/Venstre/Højre visual targeting. |
| LEGO-031 — Automatic side-by-side | ⬜ | Side-drop til Auto-kasser/layout på samme placement motor. |
| LEGO-032 — Visual resize/span | ⬜ | 12-column span resize. |
| LEGO-033 — Responsive layout/span | ⬜ | Tablet/Mobile layout overrides. |

## v0.8.35 — consolidation/readiness — ✅

Verificeret kombinationsgate:

- Auto-kasser → Kasse A → Kasse B + element på samme `LayoutParentKey`-model;
- spacing + responsive design + interaction state i samme editor-DOM;
- Kasse/Grid/Flex/common element compatibility;
- sekventiel Undo/Redo af spacing → design → state og Redo tilbage;
- parent relationer overlever history restore;
- PHP 8.0/8.2/8.3 + system Chrome + fuld Chromium/Firefox/WebKit Architecture QA PASS.

## v0.8.36 — primary LEGO design view — ✅

- Direkte Design er en tynd proxy over samme responsive LEGO-design/state som Inspector;
- farver, radius, normal/hover opacity og Disabled opacity bruger canonical controls;
- responsive override seedes lydløst, canonical ændring ejer ét checkpoint;
- ingen ny persistence/history/placement/public renderer.

## v0.8.37 — primary LEGO layout view — ✅

- resterende layout-only controls spejles i hidden canonical row-state;
- eksisterende `PaddingPx`, `HorizontalPaddingPx`, `TopSpacingPx`, `BottomSpacingPx`, `WidthPercent`, `MinHeightPx` og Tablet/Mobile-varianter bevares som persistence/public source;
- `Columns`, `MobileColumns`, `ColumnGapPx`, `MobileColumnGapPx` bevarer eksisterende semantik;
- mirror sker native capture før delegated history, men udsender ikke et ekstra event;
- Direkte Design og Inspector bruger dermed samme history/view-state for layout;
- history-style DOM restore rehydrerer legacy + canonical layout sammen;
- QA PASS på PHP 8.0/8.2/8.3, system Chrome samt Chromium/Firefox/WebKit.

## LEGO-030 — næste aktive slice

Mål: gøre placement visuelt LEGO-agtigt uden ny placement-motor.

Acceptance:

1. Når et element/Kasse trækkes over et kompatibelt mål, vises tydelige drop-zoner **Over / Under / Venstre / Højre**.
2. Over/Under ændrer kun flat order/parent relation via eksisterende motor.
3. Venstre/Højre genbruger eksisterende Auto-kasser/side-by-side-motor; ingen ny hierarchy-store.
4. Kasse-i-Kasse og element-i-Kasse følger eksisterende nesting depth/cycle-regler.
5. Keyboard/ARIA fallback for placement bevares eller forbedres.
6. Ét drop = ét history-checkpoint.
7. Undo/Redo gendanner både order, parent og visuel composition.
8. Desktop/Tablet/Mobil preview-state må ikke ændre placement-data.
9. Vehicle/Event/Gallery protected-domain contract forbliver PASS.
10. PHP 8.0/8.2/8.3 + system Chrome + Chromium/Firefox/WebKit skal være grøn før release.

## I9 — MANUAL QA EVIDENCE — PENDING

Krævet før nogen public cutover:

1. Chrome brand test;
2. Edge brand test;
3. Firefox brand test;
4. Safari brand test;
5. screen-reader core flow;
6. `test2` live-site E2E;
7. Vehicle/Event/Gallery visual/function regression;
8. migration/rollback på live kopi.

## I10 — FINAL CONTROLLED CONVERSION — LÅST

Fast rækkefølge efter I9 PASS:

1. comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery kun efter særskilt compatibility proof;
7. legacy removal til sidst.

Ingen v0.8.35–v0.8.37 release ændrer denne public-cutover-lås.
