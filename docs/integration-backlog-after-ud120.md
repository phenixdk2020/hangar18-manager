# Ultimate Designer — integration backlog after UD-120

**Statusdato:** 21. august 2026  
**Aktuel pluginbaseline:** Hangar18 Manager **v0.8.39**

UD-001..120 har architecture/core-dækning, og hovedparten af wp-admin-integrationen er implementeret. LEGO-editorens spacing, responsive design, interaction states, nested composition, primary design/layout view, visuelle drop-zoner, foldbare canvas-værktøjer, automatic side-by-side layout, 12-kolonne resize og responsive Tablet/Mobil spans er samlet på den eksisterende parent/history/persistence-arkitektur gennem LEGO-033.

**Aktiv næste fase: I9-EVIDENCE — faktisk manuel/live acceptance.** DOC-1/DOC-2, I9-runbooks, evidence-manifest, read-only public smoke, manifest-validator/init, build+target-binding og dispatch-only release-gate samt I10 operator-/blocker-/acceptance-/stage-dokumentation er nu forberedt. Automatisk QA må ikke erstatte de krævede I9 live/manuelle beviser.

Eksisterende Hangar18-sider er fortsat **ikke** public-cutover til en ny renderer.

## Ikke-forhandlingsbare arkitekturregler

- Én drag/drop-motor.
- Én `LayoutParentKey` parent/child-model.
- Én Undo/Redo-stack og ét logisk history-checkpoint pr. brugerhandling.
- Eksisterende page-section felter forbliver persistence/public-renderer-kilden under migrationen.
- Ingen public sidekonvertering før I9 er manuelt accepteret.
- Vehicle/Event/Gallery forbliver beskyttede legacy-domæner, bortset fra eksplicit godkendte snævre fixes som EVENT-001.
- I10 plan/readiness/preflight forbliver decision-only og må ikke eksponere public mutation, før en særskilt kontrolleret cutover-mekanisme senere godkendes.

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
| I9 — Manual QA evidence | 🟡 Evidence pending | Prep/validator/release-gate er klar; faktiske brand-browser-, screen-reader-, test2-editor-, protected-domain- og rollback-beviser mangler. |
| I10 — Final controlled conversion | 🟡 Prep/preflight færdigt / cutover låst | Operatorflow dokumenteret; comparison → Hjem → Om → Kontakt → Bliv medlem → protected domains. |
| UX-3 — Foldbare workspace rails | ✅ v0.8.24 | Elementer/Funktioner og Inspector foldes uafhængigt. |
| UX-4 — Ugemt forhåndsvisning | ✅ v0.8.25 + v0.8.27 | Preview uden save; editor chrome renses fra klonen. |
| UX-5 — Foldbare canvas-værktøjspaneler | ✅ v0.8.39 + LEGO-031 UX | Direkte Design · LEGO og Billede starter minimeret, foldes uafhængigt og husker browser-lokal state; ingen history/save-event. |
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
| LEGO-030 — Visual four-way drop zones | ✅ v0.8.38 | Over/Under/Venstre/Højre oven på eksisterende placement-motor. |
| LEGO-031 — Automatic side-by-side layout | ✅ QA PASS | Almindelige elementer placeres side-by-side via samme Auto-kasser/layoutmotor; single history checkpoint. |
| LEGO-032 — Visual resize / column span | ✅ QA PASS | Usynlig 12-kolonne grid, visuel nabo-resize, min. span 1 og ét Undo/Redo-checkpoint. |
| LEGO-033 — Tablet/Mobile layout overrides | ✅ QA PASS | Reversible Tablet/Mobil span-overrides med Desktop-arv, snapshots og samme history-owner. |
| DOC-1 — Visuel brugermanual | ✅ Færdig | `docs/ultimate-designer-user-manual.md`. |
| DOC-2 — Hurtig reference | ✅ Færdig | `docs/ultimate-designer-quick-reference.md`. |
| DOC-3 — Migration operations index | ✅ Færdig | Samlet indgang til I9/I10 operatorfiler. |
| I9-PREP-1 — Evidence runbook | ✅ Færdig | Ensartet browser/screen-reader/protected-domain evidenceflow. |
| I9-PREP-2 — test2 live checklist | ✅ Færdig | Preflight, comparison-side, responsive, interactions og protected domains. |
| I9-PREP-3 — Rollback rehearsal | ✅ Færdig | Baseline → kandidat → restore → verifikation. |
| I9-PREP-4 — Public live read-only smoke | ✅ Implementeret | Playwright på public test2-ruter med screenshot, fatal-error og overflow guards; faktisk live evidence er stadig pending. |
| I9-PREP-5 — Evidence result template | ✅ Færdig | Standard PASS/FAIL/BLOCKED registrering. |
| I9-PREP-6 — Evidence manifest | ✅ Færdig | JSON Schema + eksempel; overall PASS kræver alle obligatoriske gates PASS, og en PASS-gate kræver evidence. |
| I9-PREP-7 — QA contracts | ✅ PASS | Isolation/read-only/evidence-kontrakter integreret i Architecture QA og særskilt I9 Prep QA. |
| I9-EVIDENCE-1 — Manifest validator | ✅ Implementeret | Struktur, gates, evidence, deterministisk overall status og release-gate-mode. |
| I9-EVIDENCE-2 — Manifest initializer | ✅ Implementeret | Ny build seedes sikkert med alle otte gates `PENDING`; kan ikke fremstille acceptance. |
| I9-EVIDENCE-3 — JSON/Markdown rapport | ✅ Implementeret | Maskinlæsbar validator-output og kompakt human-readable evidence-status. |
| I9-EVIDENCE-4 — Actions release-gate | ✅ Implementeret | `workflow_dispatch`-only, `contents: read`, validator-resultat som artifact. |
| I9-EVIDENCE-5 — Build/environment binding | ✅ Implementeret | Manifest kan bindes til forventet commit-SHA, pluginversion og normaliseret staging-target. |
| I9-EVIDENCE-6 — Source version resolution | ✅ Implementeret | Blank workflow-version læses fra `Hangar18_Manager::VERSION`; aktuel baseline 0.8.39. |
| I10-PREP-1 — Operator runbook | ✅ Færdig | Fast rækkefølge, gates, stopregler og non-executable policy. |
| I10-PREP-2 — Blocker reference | ✅ Færdig | Blocker → betydning → korrigerende handling. |
| I10-PREP-3 — Acceptance template | ✅ Færdig | Spejler de syv required human checks + source hash/evidence/manual confirmation. |
| I10-PREP-4 — Stage ledger | ✅ Færdig | Hash/evidence/acceptance/preflight pr. conversion-stage. |
| I10-PREP-5 — Documentation contract | ✅ PASS | Runbooks bindes til `ConversionTargetCatalog`, checklist og non-executable preflight i CI. |

## Stabiliseret editorhistorik

Undo/Redo er fortsat eneste history-owner:

- v0.8.20: load-order/preloader og strukturelle checkpoints;
- v0.8.21: live SELECT/INPUT/TEXTAREA-state gennem clone/restore;
- v0.8.22: første nye strukturelle handling efter fuld Undo/Redo;
- v0.8.23: tekst, farver og billeder som content-history checkpoints;
- v0.8.35: kombineret spacing/design/state på nested Kasse blev verificeret som sekventielle Undo/Redo-trin;
- v0.8.39: fold/udfold af canvas-værktøjspaneler sender ingen form-events og opretter derfor ingen history-checkpoints;
- LEGO-031: atomic transaction adapter samler ét side-drop til ét logisk checkpoint;
- LEGO-032: pointerdown→pointerup på Desktop-resize samler begge nabo-spans i ét checkpoint;
- LEGO-033: Tablet/Mobil-resize bruger samme atomic bridge, og responsive snapshots overlever Undo/Redo og arv til/fra Desktop.

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
| LEGO-030 — Visual four-way drop zones | ✅ v0.8.38 | Over/Under/Venstre/Højre visual targeting på eksisterende motor. |
| LEGO-031 — Automatic side-by-side | ✅ QA PASS | Side-drop for almindelige elementer adapteres til Auto-kasser/layout på samme placement motor. |
| LEGO-032 — Visual resize/span | ✅ QA PASS | 12-column Desktop span resize med single history checkpoint. |
| LEGO-033 — Responsive layout/span | ✅ QA PASS | Tablet/Mobil reversible span-overrides uden separat motor. |

## LEGO-031 — automatic side-by-side — ✅ QA PASS

Verificeret:

1. almindelige elementer kan slippes Venstre/Højre ved kompatible mål;
2. eksisterende Auto-kasser/layoutmodel genbruges;
3. `LayoutParentKey` forbliver autoritativ;
4. depth/cycle-regler ændres ikke;
5. ét side-drop = ét history-checkpoint;
6. Undo/Redo gendanner wrapper/layout/order/parent relationer;
7. v0.8.38 Kasse-side-drop regression er PASS;
8. Desktop/Tablet/Mobil preview ændrer ikke placement-data;
9. Vehicle/Event/Gallery protected-domain contract er PASS;
10. PHP 8.0/8.2/8.3 + system Chrome + Chromium/Firefox/WebKit er grønne.

## LEGO-032 — visual resize / column span — ✅ QA PASS

Verificeret:

1. side-by-side børn bruger canonical Desktop span på usynlig 12-kolonne grid;
2. untouched 2-element rækker løses 6/6 og 3-element rækker 4/4/4;
3. visuel grænseresize mellem naboer fungerer;
4. nabo-parrets samlede span bevares og row-budget ≤ 12;
5. min. span = 1;
6. `LayoutParentKey`/Auto-kasser forbliver placement authority;
7. ingen ny parent-store/public renderer;
8. pointerdown→pointerup = ét history-checkpoint;
9. Undo/Redo gendanner begge spans samlet;
10. LEGO-031/Kasse/panels/protected-domains regression er PASS;
11. Tablet/Mobile arver Desktop i LEGO-032;
12. PHP/browser matrix er PASS.

## LEGO-033 — responsive Tablet/Mobile layout span — ✅ QA PASS

Verificeret:

1. Desktop er canonical baseline; Tablet/Mobil arver som standard;
2. første responsive resize opretter device-specifikke snapshots;
3. device-layouts er indbyrdes isolerede;
4. `Arv Desktop` kan aktiveres uden at slette snapshot;
5. arv fra igen gendanner eksisterende snapshot;
6. samme 12-kolonne budget/min. span gælder;
7. v0.8.42 ejer responsive tile-bredde, så Desktop-runtime ikke kan overskrive den;
8. ét responsive resizeforløb = ét atomic history-checkpoint;
9. Undo/Redo gendanner begge responsive nabo-spans;
10. faktisk canvas-CSS-span er regressionsverificeret efter settling;
11. placement/public renderer er uændret;
12. Fast QA, Architecture QA, protected domains, PHP 8.0/8.2/8.3, system Chrome og Chrome/Chromium/Firefox/WebKit er PASS.

## Dokumentation og I9-forberedelse — ✅

Forberedt og kontraktbeskyttet:

- `docs/ultimate-designer-user-manual.md`;
- `docs/ultimate-designer-quick-reference.md`;
- `docs/migration-operations-index.md`;
- `docs/i9-manual-qa-evidence-runbook.md`;
- `docs/i9-test2-live-e2e-checklist.md`;
- `docs/i9-rollback-rehearsal.md`;
- `docs/i9-evidence-result-template.md`;
- `docs/i9-evidence-manifest.schema.json`;
- `docs/i9-evidence-manifest.example.json`;
- `docs/i9-evidence-tooling.md`;
- `tools/i9-evidence-init.cjs`;
- `tools/i9-evidence-validator.cjs`;
- `tests/Live/i9-public-readonly.spec.cjs`;
- `tests/Live/playwright.i9-public.config.cjs`;
- `.github/workflows/i9-test2-live-readonly.yml`;
- `.github/workflows/i9-evidence-validate.yml`;
- `.github/workflows/i9-prep-qa.yml`;
- `tests/Architecture/i9-live-readonly-contract.sh`;
- `tests/Architecture/i9-evidence-validator-contract.sh`.

Public-smoken er read-only og må ikke logge ind, submitte formularer eller mutere WordPress. Den kontrollerer centrale public-ruter, kritiske PHP/WordPress-fejl og horisontal overflow og kan gemme screenshot-evidence.

Evidence-manifestet har otte obligatoriske gates: Chrome, Edge, Firefox, Safari, screen reader, test2 live E2E, protected domains og rollback. `overallStatus=PASS` er kun gyldig, når alle otte er PASS; en PASS-gate skal have mindst én evidence-reference.

Validatoren håndhæver derudover deterministisk samlet status (`FAIL` → `BLOCKED` → alle PASS → `PENDING`), kan bindes til commit-SHA, pluginversion og staging-target og kan med `--require-pass` bruges som teknisk release-gate efter den faktiske human/live acceptance. Actions-workflowet er eksplicit dispatch-only og har kun read-permission.

## I10-forberedelse — ✅ / CUTOVER FORTSAT LÅST

Forberedt:

- `docs/i10-operator-runbook.md`;
- `docs/i10-blocker-reference.md`;
- `docs/i10-acceptance-record-template.md`;
- `docs/i10-stage-ledger-template.md`;
- `tests/Architecture/i10-operator-runbook-contract.sh`.

Dokumentationen spejler den eksisterende runtime:

- `ConversionPlanService`: `Mode=plan-only`, `PublicMutationAvailable=false`;
- `ConversionReadinessGate`: decision-only blockers/eligibility;
- `ConversionAcceptanceValidator`: syv required human checks, manual confirmation, environment/evidence reference og source hash;
- `ConversionCutoverPreflightService`: `Mode=cutover-preflight-only`, `Executable=false`, `PublicMutationAvailable=false`;
- `ConversionTargetCatalog`: Hjem → Om → Kontakt → Bliv medlem efter accepteret comparison-side;
- protected domains forbliver yderligere låst af legacy-runtime policy.

## I9 — MANUAL QA EVIDENCE — 🟡 PENDING

Krævet før nogen public cutover:

1. Chrome brand test;
2. Edge brand test;
3. Firefox brand test;
4. Safari brand test;
5. screen-reader core flow;
6. `test2` live-site E2E med rigtig editor/session;
7. Vehicle/Event/Gallery visual/function regression;
8. migration/rollback på live kopi.

Den public read-only smoke og evidence-validatoren er ekstra støttebeviser og reducerer gentagen kontrol, men kan ikke alene sætte I9 til PASS.

## I10 — FINAL CONTROLLED CONVERSION — LÅST

Fast rækkefølge efter I9 PASS:

1. comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery kun efter særskilt compatibility proof;
7. legacy removal til sidst.

Ingen LEGO-, dokumentations-, I9-prep-, I9-evidence-tooling- eller I10-prep-opgave ændrer denne public-cutover-lås.
