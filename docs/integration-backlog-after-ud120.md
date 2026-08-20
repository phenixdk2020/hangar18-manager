# Ultimate Designer — integration backlog after UD-120

**Statusdato:** 20. august 2026  
**Aktuel pluginbaseline:** Hangar18 Manager **v0.8.31**

UD-001..120 har architecture/core-dækning, og hovedparten af wp-admin-integrationen er implementeret. Den aktive udvikling er nu koncentreret om LEGO-editorens fælles objekt-/designmodel, manuel I9-QA og den senere kontrollerede sidekonvertering. **Eksisterende Hangar18-sider er fortsat ikke public-cutover til en ny renderer.**

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
| I9 — Manual QA evidence | 🟡 Framework færdigt | Evidence ledger findes; alle krævede live/manuelle gates er ikke registreret endnu. |
| I10 — Final controlled conversion | 🟡 Preflight færdigt / cutover låst | Planner, shadow, acceptance ledger og source-drift preflight findes. |
| UX-3 — Foldbare workspace rails | ✅ Færdig v0.8.24 | Elementer/Funktioner og Inspector kan foldes ind uafhængigt til 44 px rails. |
| UX-4 — Ugemt forhåndsvisning | ✅ Færdig v0.8.25 + hotfix v0.8.27 | Preview af levende editor-state uden save/public mutation; editor overlays renses. |
| EVENT-001 — Automatisk eventarkiv | ✅ Færdig v0.8.26 | Events flyttes dynamisk mellem Kommende/Tidligere efter WP-lokal dato/sluttid. |
| B1 — Sidebackup restore | ✅ Færdig v0.8.28 | Replace original + copy draft, safety backup, nonce/capability og audit. |
| B2 — Versioneret site-backup | ✅ Færdig v0.8.29, udvidet v0.8.31 | H18-BACKUP-ID, SHA-256, media, ZIP, full/selective restore; selective LEGO-state og stale-lock hash-fix i v0.8.31. |
| LEGO spacing/responsive foundation | ✅ Færdig v0.8.30–v0.8.31 | Canonical X/Y spacing, Tablet/Mobile inheritance og single-history integration. |
| LEGO common design model | 🟢 Aktiv v0.8.32 | LEGO-006/009: ét fælles design-state for almindelige elementer og Kasse. |
| DOC-1 — Visuel brugermanual | ⬜ Backlog | Udarbejdes når editorens interaktionsmodel er stabil og releasebar. |

## I1–I8 — IMPLEMENTERET

I1–I8 er implementeret i v0.7.4–v0.8.1 og forbliver shadow/admin-orienteret, hvor det er relevant. De centrale regler er fortsat:

- ingen skjult public cutover;
- ingen automatisk destruktiv rolle-/dataændring;
- importer starter som dry-run;
- AI-forslag skriver ikke direkte til public side;
- legacy `edit_pages`-adgang bevares under migrationen.

## I9 — MANUAL QA EVIDENCE — FRAMEWORK FÆRDIGT / EVIDENCE PENDING

Framework leveret i v0.8.2.

Krævet manuel evidence:

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

- **I10-A — Planner/shadow workspace (v0.8.3):** ✅ complete.
- **I10-B — Shadow acceptance ledger (v0.8.4):** ✅ complete.
- **UX-1 — Auto-kasser + Tabel + Side Health collapse (v0.8.5):** ✅ complete.
- **I10-C — Signed cutover preflight (v0.8.6):** ✅ complete, men `Executable=false` og `PublicMutationAvailable=false`.
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
- begge kan være 44 px rails samtidig;
- state gemmes kun browser-lokalt;
- tablet/mobile beholder stacked layout.

### UX-4 — Ugemt preview — ✅ v0.8.25 + v0.8.27

- preview bruger aktuel levende editor-state uden save/version/public mutation;
- Desktop / Tablet / Mobil understøttes;
- v0.8.27 fjerner transient editor-chrome, Direkte Design, image-tools, box-model handles og focal-point fra preview-klonen;
- `Åbn offentlig side` er fortsat separat og viser gemt/public state.

### EVENT-001 — Automatisk arkiv — ✅ v0.8.26

- dato før i dag → Tidligere arrangementer;
- event i dag med sluttid → Kommende indtil sluttid, derefter Tidligere;
- event i dag uden sluttid → Kommende resten af dagen, Tidligere efter midnat;
- Kommende sorteres stigende, Tidligere nyeste først;
- runtime udfører ingen frontend save/post-write/option-write.

### B1 — Sidebackup restore — ✅ v0.8.28

- **Erstat original:** safety backup før write, samme Page ID/slug/URL og audit;
- **Opret som kopi:** separat draft med collision-safe `-kopi[-N]` slug;
- path-containment, capability + nonce og fejlbevarende rollback-data.

### B2 — Versioneret site-backup — ✅ v0.8.29 + integration v0.8.31

- immutable `H18-BACKUP-xxxxxx` ID;
- canonical manifest/payloads og SHA-256;
- Hangar18-managed pages, page versions, Site Builder, forms/polls/data og Hangar18-options;
- referenced original media + nødvendige derivatives;
- ZIP export/import med security preflight;
- full restore og selective page restore med signeret/state-bound dry-run;
- ny B2 safety backup før første mutation;
- stale restore-lock recovery og audit;
- v0.8.31 selective page restore gendanner kun den valgte sides LEGO-spacing;
- ældre backups uden LEGO-state sletter ikke nyere spacing;
- restore-koordinationsstate (`site_backup_restore*`) er ekskluderet fra portable snapshot/current-state hash, så stale-lock recovery ikke invaliderer sit eget dry-run;
- standard-B2 indeholder ikke raw database/plugin/theme disaster recovery.

## LEGO-editor backlog

Arkitekturregel: **én drag/drop-motor, én parent/child-model, én history-transaction pr. brugerhandling og ét fælles design-/spacing-sprog på tværs af elementtyper.**

| ID | Status | Leverance |
|---|---|---|
| LEGO-001 — Shared object/state model | 🟢 Delvist færdig v0.8.30–v0.8.31 | Canonical responsive spacing-state findes; udvides nu med fælles design-state. |
| LEGO-002 — Backward-compatible X/Y gap | ✅ v0.8.30 | `LayoutGapPx`/`MobileLayoutGapPx` seedes til X=Y uden migration. |
| LEGO-003 — Inspector separat X/Y spacing | ✅ v0.8.30 | Separate X/Y controls i Inspector. |
| LEGO-004 — Per-element margin | ✅ v0.8.30 | Responsive Margin X/Y for almindelige elementer. |
| LEGO-006 — Common element design model | 🟡 Aktiv v0.8.32 | Fælles typography/color/background/border/radius/opacity/shadow/state-kontrakt. |
| LEGO-009 — Consolidate Kasse design | 🟡 Aktiv v0.8.32 | Kasse skal bruge samme designmodel som andre elementer, ikke særregler. |
| LEGO-010 — Kasse internal X/Y gap | ✅ v0.8.30 | Separate X/Y gaps på Container/Kasse/Grid/Flex i editor-state. |
| LEGO-011 — Responsive spacing | ✅ v0.8.31 | Tablet + arv fra Desktop; Mobile kan arve eller bruge bevaret override. |
| LEGO-021 — Undo/Redo one step per action | ✅ Stabiliseret / manuelt accepteret | v0.8.20–v0.8.23 er eneste history-owner; LEGO kobles på samme DOM-state. |
| LEGO-025 — QA suite | 🟡 Aktiv | PHP 8.0/8.2/8.3, system Chrome, B2, Editor Fast og Chromium/Firefox/WebKit udbygges pr. slice. |

### v0.8.30 — LEGO X/Y spacing foundation — ✅ LEVERET

- én canonical renderer-neutral spacing-model;
- Desktop/Mobile `Margin.X/Y` for alle elementer;
- Desktop/Mobile `Gap.X/Y` for Container/Kasse/Grid/Flex;
- legacy gap fallback X=Y;
- canonical hidden row-state gør eksisterende `admin.js`/v0.8.23-history til eneste Undo/Redo-ejer;
- editor-preview bruger separate `column-gap`/`row-gap`;
- state gemmes admin-only i `hangar18_ultimate_designer_lego_spacing_v2` og indgår i B2 full backup;
- ingen public renderer/cutover eller Vehicle/Event/Gallery-ændringer.

### v0.8.31 — Responsive LEGO spacing + selective restore — ✅ LEVERET

- canonical spacing schema 2;
- Desktop er basis;
- Tablet starter som **Arv fra Desktop**;
- Tablet og Mobil kan skifte mellem inheritance og egne overrides uden at override-data slettes;
- eksisterende v0.8.30 Mobile-værdier forbliver eksplicitte overrides ved migration, så eksisterende layout ikke ændres;
- Inspector viser inheritance og effektive værdier;
- editor-preview bruger separate Desktop/Tablet/Mobile variables;
- selective B2 page restore gendanner kun valgte sides LEGO-spacing;
- B2 stale-lock/current-state hash edge case fundet af QA og rettet;
- samme admin.js/history-v0.8.23 er fortsat eneste Undo/Redo-ejer;
- B2 QA + LEGO QA PASS på PHP 8.0/8.2/8.3, system Chrome, Editor Runtime Fast og fuld Chromium/Firefox/WebKit Architecture QA.

### v0.8.32 — LEGO common element/Kasse design model — 🟡 AKTIV NÆSTE SLICE

Mål:

- introducér ét canonical design-state for både almindelige elementer og Container/Kasse/Grid/Flex;
- map eksisterende legacy Inspector/Direkte Design-felter ind i samme state uden at ændre public output;
- første kontrakt skal mindst dække typography, text/heading colors, background, border width/color, radius, opacity og shadow;
- Kasse må ikke få en separat design-store eller særskilt Undo/Redo-historik;
- eksisterende per-corner radius skal bevares og normaliseres i samme designmodel;
- eksisterende legacy-felter forbliver source-compatible, så save/public renderer fortsætter uændret i denne shadow/admin fase;
- canonical design-field skal ligge i eksisterende section-row, så history snapshot/restore tager design-state med i samme transaction;
- Inspector/Direct Design skal være views over samme state og kunne synkronisere begge veje uden dobbelt history-step;
- QA skal dække almindeligt element + Kasse, legacy→canonical hydration, ændring fra Inspector/Direkte Design, Undo/Redo-style DOM restore og kombineret design+spacing;
- PHP 8.0/8.2/8.3 + system Chrome + Chromium/Firefox/WebKit + Editor Fast skal være PASS før merge.

## Efter v0.8.32 — næste LEGO-slices

1. Responsive design overrides med samme inheritance-kontrakt som spacing.
2. Udvid fælles designmodel med hover/focus/active/disabled state-design og transitions.
3. Udbyg QA med Kasse-i-Kasse, Kasse-i-Auto-kasser, element-i-Kasse og Undo/Redo af design+spacing i kombination.
4. Først derefter større LEGO drag/drop-UX-udvidelser; parent/child- og placement-motoren genbruges.

## DOC-1 — Ultimate Designer visuel brugermanual — ⬜ BACKLOG

Manualen laves efter editor-interaktionsmodellen er stabil, så screenshots matcher en released runtime.

Skal mindst indeholde:

- Quick start;
- elementkatalog med screenshot/icon, UI-navn, formål og eksempel;
- Section / Kasse / Auto-kasser / Flex / Tabel;
- Kasse-i-Kasse og element-i-Kasse drag/drop map;
- Inspector-reference for content, typography, colors, borders, radius, spacing, responsive og states;
- Responsive guide med Desktop/Tablet/Mobile og inheritance/override;
- Undo/Redo, page versions, B1 og B2 backup/restore;
- troubleshooting og runtime-badges;
- worked recipes;
- accessibility-noter;
- versionsbinding: `Gælder for Hangar18 Manager vX.Y.Z`;
- samme canonical kilde skal senere kunne generere print/PDF.

## Aktuelle næste handlinger

1. **Implementér og QA v0.8.32:** LEGO-006/009 common element/Kasse design model.
2. Udbyg LEGO-025 QA for kombineret spacing/design/nesting/history.
3. Kør og registrér alle I9 live/manual evidence-gates på `test2` efter editorregressionen er stabil.
4. Ret eventuelle live QA / Side Health issues uden public konvertering.
5. Refresh comparison-page shadow copy og registrér page-specific acceptance mod aktuel `SourceHash`.
6. Kør signed preflight igen.
7. Public comparison-page activation designes først, når alle I9 gates faktisk er PASS.
