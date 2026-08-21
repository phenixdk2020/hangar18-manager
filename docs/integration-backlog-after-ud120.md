# Ultimate Designer — integration backlog after UD-120

**Statusdato:** 21. august 2026  
**Aktuel pluginbaseline:** Hangar18 Manager **v0.8.34**

UD-001..120 har architecture/core-dækning, og hovedparten af wp-admin-integrationen er implementeret. LEGO-editorens spacing-, responsive-, common-design- og interaction-state fundament er nu leveret gennem v0.8.34. **Aktiv næste gate er v0.8.35: samlet LEGO consolidation / primary-editor readiness.** Eksisterende Hangar18-sider er fortsat ikke public-cutover til en ny renderer.

## Ikke-forhandlingsbar migrationsregel

Eksisterende sidekonvertering er sidste fase. Vehicle/Event/Gallery forbliver beskyttede legacy-domæner, bortset fra eksplicit godkendte, snævre fejlrettelser som EVENT-001. Public cutover kræver fortsat side-by-side regression, kompatibilitetsbevis, backup og rollback-rehearsal.

Automatisk QA kan ikke erstatte en krævet manuel/live acceptance-gate.

## Statusoversigt

| Fase | Status | Leveret |
|---|---|---|
| I1 — Admin integration / shadow dashboard | ✅ Færdig | Admin-only Ultimate Designer dashboard; ingen renderer replacement. |
| I2 — Visual Header/Footer Builder | ✅ Færdig i shadow/admin | Shared Sections tree, visuel editing, designkontroller og preview. Public assignment er fortsat låst. |
| I3 — Menu Builder v2 | ✅ Færdig i shadow/admin | Nested drag/drop, presets, keyboard-preview og eksplicit side include/exclude. |
| I4 — Side Health | ✅ Færdig | Live/read-only Design/Mobile/Accessibility/Performance/SEO-analyse med elementlinks. |
| I5 — Asset Manager | ✅ Færdig | Collections/tags/usage/focal point/derivatives/duplicate reporting over WordPress Media IDs. |
| I6 — Portability | ✅ Færdig | Dry-run, signeret plan, conflict/remap, isoleret workspace og restore-point. |
| I7 — Permissions / Design Lock | ✅ Færdig | Additive capabilities/roles og design-lock policy. |
| I8 — AI | ✅ Færdig | Provider-neutral settings og reversible forslag uden direkte page-write. |
| I9 — Manual QA evidence | 🟡 Framework færdigt | Live/manuelle evidence-gates er endnu ikke alle registreret. |
| I10 — Final controlled conversion | 🟡 Preflight færdigt / cutover låst | Planner, shadow, acceptance ledger og source-drift preflight findes. |
| UX-3 — Foldbare workspace rails | ✅ v0.8.24 | Elementer/Funktioner og Inspector kan foldes uafhængigt. |
| UX-4 — Ugemt forhåndsvisning | ✅ v0.8.25 + v0.8.27 | Live editor-preview uden save/public mutation; editor overlays renses. |
| EVENT-001 — Automatisk eventarkiv | ✅ v0.8.26 | Events klassificeres dynamisk efter WP-lokal dato/sluttid. |
| B1 — Sidebackup restore | ✅ v0.8.28 | Replace original + copy draft, safety backup, nonce/capability og audit. |
| B2 — Versioneret site-backup | ✅ v0.8.29, udvidet v0.8.31/v0.8.33/v0.8.34 | ZIP/full/selective restore inkl. LEGO spacing, responsive design og interaction snapshots. |
| LEGO spacing/responsive foundation | ✅ v0.8.30–v0.8.31 | Canonical X/Y spacing, Tablet/Mobile inheritance og single-history integration. |
| LEGO common design model | ✅ v0.8.32 | Én canonical designmodel for elementer og Kasse/Grid/Flex. |
| LEGO responsive design | ✅ v0.8.33 | Desktop/Tablet/Mobil inheritance/overrides med reversible snapshots. |
| LEGO interaction states | ✅ v0.8.34 | Transition + Focus + Active + Disabled på samme common/responsive contract. |
| LEGO consolidation / primary editor readiness | 🟢 Aktiv v0.8.35 | Nested Kasse/Auto-kasser + spacing/design/states/history/backup samlet regression. |
| DOC-1 — Visuel brugermanual | ⬜ Backlog | Udarbejdes når editorens interaktionsmodel er stabil og primary-ready. |

## I1–I8 — IMPLEMENTERET

I1–I8 er implementeret og forbliver shadow/admin-orienteret, hvor det er relevant. Centrale regler:

- ingen skjult public cutover;
- ingen automatisk destruktiv rolle-/dataændring;
- importer starter som dry-run;
- AI-forslag skriver ikke direkte til public side;
- legacy `edit_pages`-adgang bevares under migrationen.

## I9 — MANUAL QA EVIDENCE — FRAMEWORK FÆRDIGT / EVIDENCE PENDING

Krævet manuel/live evidence:

1. seneste Chrome brand test;
2. seneste Edge brand test;
3. seneste Firefox brand test;
4. seneste Safari brand test;
5. screen-reader core flow;
6. `test2` live-site E2E;
7. Vehicle/Event/Gallery visual/function regression;
8. migration/rollback på en live kopi.

Automatisk Chromium/Firefox/WebKit, security-audit og rollback-simulation er regressionsgates, men opfylder ikke de manuelle live-gates ovenfor.

## I10 — FINAL CONTROLLED CONVERSION — PUBLIC CUTOVER FORTSAT LÅST

Fast rækkefølge:

1. comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery først efter særskilte protected-domain gates;
7. legacy removal til sidst.

### I10 slices

- **I10-A — Planner/shadow workspace:** ✅ complete.
- **I10-B — Shadow acceptance ledger:** ✅ complete.
- **I10-C — Signed cutover preflight:** ✅ complete, men public mutation forbliver låst.
- **I10-D — Public comparison-page cutover:** ⛔ blocked af I9 live/manual gates.
- **I10-E — Core page cutover:** ⛔ blocked; Hjem → Om → Kontakt → Bliv medlem én ad gangen.
- **I10-F — Protected domain cutover:** ⛔ blocked; særskilt compatibility proof kræves.
- **I10-G — Legacy removal:** ⛔ blocked indtil alle konverterede domæner er accepteret og rollback-retention kan ophøre.

## Stabiliseret editorhistorik — v0.8.20–v0.8.23

Undo/Redo er manuelt accepteret og fortsat én autoritativ history-stack:

- v0.8.20 rettede load-order og strukturelle checkpoints;
- v0.8.21 bevarer live SELECT/INPUT/TEXTAREA-state og elementtype gennem restore;
- v0.8.22 registrerer første nye strukturelle handling efter fuld Undo/Redo;
- v0.8.23 registrerer tekst, farver og billeder som logiske content-history checkpoints;
- LEGO må ikke introducere en anden drag/drop-motor, parent/child-model eller Undo/Redo-stack.

## UX / Event / Backup — LEVERET

### UX-3 — Workspace rails — ✅ v0.8.24

- Elementer/Funktioner og Inspector foldes uafhængigt;
- begge kan være smalle rails samtidig;
- state gemmes browser-lokalt;
- tablet/mobile beholder stacked layout.

### UX-4 — Ugemt preview — ✅ v0.8.25 + v0.8.27

- preview bruger aktuel levende editor-state uden save/version/public mutation;
- Desktop / Tablet / Mobil understøttes;
- v0.8.27 fjerner transient editor-chrome, Direkte Design, image-tools, box-model handles og focal-point fra preview-klonen.

### EVENT-001 — Automatisk arkiv — ✅ v0.8.26

- dato før i dag → Tidligere arrangementer;
- event i dag med sluttid → Kommende indtil sluttid, derefter Tidligere;
- event i dag uden sluttid → Kommende resten af dagen, Tidligere efter midnat;
- Kommende sorteres stigende, Tidligere nyeste først;
- runtime udfører ingen frontend save/post-write/option-write.

### B1 — Sidebackup restore — ✅ v0.8.28

- **Erstat original:** safety backup før write, samme Page ID/slug/URL og audit;
- **Opret som kopi:** separat draft med collision-safe slug;
- path-containment, capability + nonce og rollback-data.

### B2 — Versioneret site-backup — ✅ v0.8.29 + LEGO-integration

- immutable `H18-BACKUP-xxxxxx` ID;
- canonical manifest/payloads og SHA-256;
- Hangar18-managed pages, page versions, Site Builder, forms/polls/data og Hangar18-options;
- referenced media;
- ZIP export/import med security preflight;
- full restore og selective page restore med signeret/state-bound dry-run;
- safety backup før første mutation;
- stale restore-lock recovery og audit;
- v0.8.31 selective restore: valgte sides LEGO-spacing;
- v0.8.33 selective restore: valgte sides responsive LEGO-design;
- v0.8.34 selective restore: interaction snapshots følger responsive designstate, inklusive inaktive reversible snapshots;
- andre siders spacing/design/state bevares ved selective restore;
- ældre backups uden additive LEGO-state sletter ikke nyere lokal state;
- standard-B2 indeholder ikke raw database/plugin/theme disaster recovery.

## LEGO-editor backlog

Arkitekturregel: **én drag/drop-motor, én parent/child-model, én history-transaction pr. brugerhandling og ét fælles design-/spacing/state-sprog på tværs af elementtyper.**

| ID | Status | Leverance |
|---|---|---|
| LEGO-001 — Shared object/state model | ✅ Foundation v0.8.30–v0.8.34 | Canonical spacing + common/responsive design + interaction state vocabulary. |
| LEGO-002 — Backward-compatible X/Y gap | ✅ v0.8.30 | Legacy gap seedes til X=Y uden migration. |
| LEGO-003 — Inspector separat X/Y spacing | ✅ v0.8.30 | Separate X/Y controls. |
| LEGO-004 — Per-element margin | ✅ v0.8.30 | Responsive Margin X/Y. |
| LEGO-006 — Common element design model | ✅ v0.8.32 | Typography/color/background/border/radius/opacity/shadow/hover. |
| LEGO-009 — Consolidate Kasse design | ✅ Foundation v0.8.32 | Kasse/Grid/Flex bruger samme canonical design-paths. |
| LEGO-010 — Kasse internal X/Y gap | ✅ v0.8.30 | Separate X/Y gaps. |
| LEGO-011 — Responsive spacing | ✅ v0.8.31 | Tablet/Mobile inheritance og overrides. |
| LEGO-012 — Responsive common design | ✅ v0.8.33 | Desktop basis + reversible Tablet/Mobile design snapshots. |
| LEGO-013 — Extended interaction states | ✅ v0.8.34 | Transition, Focus, Active og Disabled på samme responsive state-contract. |
| LEGO-021 — Undo/Redo one step per action | ✅ Stabiliseret | v0.8.20–v0.8.23 er eneste history-owner; LEGO-lag sender ét canonical checkpoint. |
| LEGO-025 — QA suite | 🟡 Aktiv v0.8.35 | Udvides til kombineret nested Kasse/Auto-kasser + spacing/design/states/history/B2. |
| LEGO-026 — Primary editor readiness | 🟢 Aktiv v0.8.35 | Gate for at gøre LEGO til den primære editor-designmotor uden public renderer-cutover. |
| LEGO-030 — Visual side-drop zones | ⬜ Efter primary-ready | Over/Under/Venstre/Højre på eksisterende placement-motor. |
| LEGO-031 — Automatic side-by-side layout | ⬜ Efter LEGO-030 | Side-drop opretter/justerer layout uden ny parent/child-motor. |
| LEGO-032 — Visual resize / column span | ⬜ Senere | Resize oven på usynlig 12-kolonne layoutmotor. |
| LEGO-033 — Tablet/Mobile layout overrides | ⬜ Senere | Responsive layout/span uden separat layoutmotor. |

### v0.8.30 — LEGO X/Y spacing foundation — ✅

Canonical X/Y spacing, per-element margin og Kasse/Grid/Flex gaps. Legacy gap falder tilbage til X=Y. Existing history owner bruges uændret.

### v0.8.31 — Responsive LEGO spacing — ✅

Desktop basis, Tablet/Mobile inheritance, reversible overrides og selective B2 restore af spacing.

### v0.8.32 — Common element/Kasse design — ✅

Én renderer-neutral designmodel over eksisterende page-section felter. Almindelige elementer og Kasse/Grid/Flex deler farver, typografi, border, radius, opacity, shadow og Hover. Ingen ny design-option eller parallel persistence.

### v0.8.33 — Responsive common design — ✅

Desktop forbliver legacy-backed basis. Tablet/Mobil kan arve eller bruge reversible design-overrides. Inspector følger aktiv device. B2 selective restore gendanner kun valgte sides responsive design.

### v0.8.34 — Extended interaction states — ✅ LEVERET

- fælles `LegoDesignModel` løftet additivt til schema 2;
- `Motion.Transition` bruger eksisterende `TransitionPreset`;
- Focus: Global/Tilpasset/Ingen + farve/bredde/offset;
- Active: Ingen / Press / ScaleDown;
- Disabled: opacity;
- samme model og Inspector for elementer og Kasse/Grid/Flex;
- Desktop er fortsat legacy-backed;
- Tablet/Mobil bruger den eksisterende responsive design-option;
- `InteractionHasOverride` og `InteractionHasSnapshot` adskiller aktivt override fra bevaret reversibelt snapshot;
- Arv fra Desktop kan slås til/fra uden at tidligere state-værdier går tabt;
- Normal/Hover/Focus/Active/Disabled preview virker på Desktop/Tablet/Mobil;
- select-event guard sikrer ét logisk event;
- responsive state-edit sender ét canonical row input til eksisterende Undo/Redo-owner;
- B2 selective page restore verificerer aktive og inaktive interaction snapshots;
- LEGO Editor QA PASS på PHP 8.0/8.2/8.3 + system Chrome;
- Editor Runtime Fast QA PASS;
- B2 QA PASS på PHP 8.0/8.2/8.3;
- fuld Architecture QA PASS på PHP 8.0/8.2/8.3 + Chromium/Firefox/WebKit;
- Vehicle/Event/Gallery og public cutover er uændrede.

## v0.8.35 — LEGO consolidation / primary-editor readiness — 🟢 AKTIV

Dette er **gaten før LEGO kan gøres til den primære designmotor i editoren**. Den introducerer som udgangspunkt ikke nye designfeatures; den skal bevise, at de eksisterende LEGO-lag fungerer sammen under realistiske kombinationer.

### Obligatorisk kombinationsmatrix

1. almindeligt element alene;
2. element i Kasse;
3. flere elementer i samme Kasse;
4. Kasse i Kasse inden for den nuværende tilladte nesting-dybde;
5. Kasse i Auto-kasser;
6. elementer i begge/alle Auto-kasse-kolonner;
7. Grid/Flex/Kasse med X/Y-gap;
8. Desktop + Tablet + Mobil inheritance/override;
9. Normal + Hover + Focus + Active + Disabled;
10. spacing + design + states ændret i samme session;
11. Undo/Redo gennem hele kombinationen;
12. fuld Undo → Redo → ny ændring;
13. save/reload;
14. B1 page restore;
15. B2 full restore;
16. B2 selective page restore;
17. ugemt preview uden editor-chrome;
18. existing drag/drop/placement regression;
19. Vehicle/Event/Gallery protected-domain regression.

### Primary-editor PASS-kriterier

- ingen parallel history-, parent/child-, drag/drop- eller persistence-motor;
- ét bruger-greb = ét history-checkpoint;
- elementtype og nesting overlever Undo/Redo/save/reload;
- inheritance on/off er reversibel uden datatab;
- Kasse og almindelige elementer viser samme canonical design/state-semantik;
- legacy/public output ændres ikke af selve editor-switch-gaten;
- PHP 8.0/8.2/8.3 PASS;
- system Chrome PASS;
- Editor Runtime Fast PASS;
- B1/B2 regression PASS;
- Chromium/Firefox/WebKit Architecture QA PASS.

Når denne gate er PASS, kan næste release gøre **LEGO til primær editor-UI/designmotor** ved at skjule/deprioritere duplikerede legacy designkontroller. Det er stadig **ikke** det samme som public renderer cutover.

## Efter v0.8.35

1. Gør LEGO til primær editor-UI/designmotor og konsolider Direkte Design/Inspector som views over samme canonical state.
2. Kør og registrér I9 live/manual evidence på `test2`.
3. Refresh comparison-page shadow copy og registrér acceptance mod aktuel `SourceHash`.
4. Kør signed preflight igen.
5. Første public LEGO-renderer cutover må kun ske på comparison-siden, når I9 faktisk er PASS.
6. Derefter Hjem → Om → Kontakt → Bliv medlem én side ad gangen.
7. Vehicle/Event/Gallery forbliver sidste protected-domain cutover.
8. Visuelle side-dropzoner, automatisk side-by-side layout og resize/column-span fortsætter som LEGO-UX-slices uden at oprette nye motorer.

## DOC-1 — Ultimate Designer visuel brugermanual — ⬜ BACKLOG

Manualen laves efter editor-interaktionsmodellen er primary-ready, så screenshots matcher released runtime. Den skal mindst indeholde Quick start, elementkatalog, Section/Kasse/Auto-kasser/Flex/Tabel, nesting-map, Inspector-reference, responsive inheritance, interaction states, Undo/Redo, B1/B2, troubleshooting, accessibility og versionsbinding.

## Aktuelle næste handlinger

1. **Implementér v0.8.35 consolidation / primary-editor readiness QA.**
2. Ret reelle kombinationsfejl fundet af QA uden at introducere parallelle motorer.
3. Når v0.8.35 er PASS: gør LEGO til primær editor-UI/designmotor i næste slice.
4. Kør I9 live/manual evidence på `test2`.
5. Refresh comparison-page shadow copy og signed preflight.
6. Public comparison-page activation designes først, når alle I9 gates faktisk er PASS.
