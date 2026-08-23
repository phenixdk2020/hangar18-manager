# Hangar18 Manager — canonical master-backlog v0.8.78

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.78**  
**Release commit:** `a91ae4fbf8cd06b7a222afd1c7df7c3a4ea72484`  
**Package SHA-256:** `1b87f85e2493db007428853347f9b2028d4f16cbb1eb85d03cd071c8d06f17f7`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle **canonical master-backlog**. Tidligere `active-backlog-v08xx.md` er historiske snapshots.

## Arbejdsregel fra v0.8.78

Alle udviklingspunkter i denne backlog er **forhåndsgodkendt til implementering**. Arbejdet må fortsætte punkt for punkt uden ny godkendelse. Hver implementering skal samtidig opdatere denne backlog med status, commit/release, QA-resultat, nye afhængigheder og eventuelle nye fund.

**BACKLOG-MAINT-001 er permanent:** Ingen feature, bugfix, cleanup eller QA-opgave anses som færdig, før canonical backlog er opdateret i samme arbejdsgang.

Public I10 cutover/go-live forbliver en særskilt produktionsgate. Udvikling, test, cleanup, staging, dokumentation og QA er forhåndsgodkendt; faktisk public aktivering kræver fortsat de eksisterende I9/I10 gates.

## Statusforklaring

- ✅ FÆRDIG — implementeret og relevant QA udført.
- 🟡 FIX-KANDIDAT / MANUEL TEST — kode findes, men live/manual acceptance mangler.
- 🟠 AKTIV — under implementering/audit.
- 🔴 ÅBEN — godkendt og klar til implementering.
- ⏸ FROSSET / TRACE — må først ændres efter konkret trace-evidence.
- 🔒 LÅST — bevidst gate; ikke klar til mutation.

---

# A. Backlog-governance, release og sporbarhed

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| BACKLOG-MAINT-001 | Kritisk | 🟠 PERMANENT | Canonical backlog opdateres ved hver implementering, QA, release, regression og ny opdagelse. |
| BACKLOG-MAINT-002 | Høj | 🔴 ÅBEN | Hver backlogpost får entydigt ID, prioritet, status, afhængigheder og DoD. |
| BACKLOG-MAINT-003 | Normal | 🔴 ÅBEN | Historiske backlogfiler markeres tydeligt som snapshots og må ikke forveksles med canonical. |
| BACKLOG-MAINT-004 | Normal | 🔴 ÅBEN | Tilføj maskinlæsbar backlog-index JSON med ID/status/område/release. |
| BACKLOG-MAINT-005 | Normal | 🔴 ÅBEN | Automatisk QA der fejler hvis to aktive backlog-ID’er kolliderer. |
| BACKLOG-MAINT-006 | Normal | 🔴 ÅBEN | Release notes skal referere de backlog-ID’er releasen ændrer. |
| BACKLOG-MAINT-007 | Normal | 🔴 ÅBEN | Commit-konvention: relevante backlog-ID’er i commit message for nye større spor. |
| RELEASE-001 | Høj | ✅ FÆRDIG | `release-config.json` → workflow → ZIP → update.json → SHA-256. |
| RELEASE-002 | Høj | 🔴 ÅBEN | Automatisk validering af at release ZIP indeholder præcis samme pluginversion som update.json. |
| RELEASE-003 | Høj | 🔴 ÅBEN | Automatisk ZIP tree-diff mod source allowlist/denylist, så debug/temp/legacy artifacts ikke sniger sig med. |
| RELEASE-004 | Normal | 🔴 ÅBEN | Release-manifest med kildecommit, buildtid, SHA, ændrede backlog-ID’er og QA-summary. |
| RELEASE-005 | Normal | 🔴 ÅBEN | Staging-only releaseflag så testbuilds tydeligt kan skelnes fra production-ready builds. |
| RELEASE-006 | Normal | 🔴 ÅBEN | Rollback-verifikation skal logge fra-version, til-version og gendannet plugin-SHA. |

---

# B. Trace, diagnostik og fejlfindingsplatform

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| TRACE-076 | Kritisk | 🟡 MANUEL TEST | Master TIL/FRA på Opdateringer; Start/Stop/Fortsæt/Markér/Kopiér/TXT/JSON/Nulstil i Designer. |
| TRACE-077 | Høj | 🔴 ÅBEN | Vis tydelig optagelsesindikator i Designer-header når trace er aktiv. |
| TRACE-078 | Høj | 🔴 ÅBEN | Log session-ID, pluginversion, browser, viewport, WP admin-side og side slug ved Start test. |
| TRACE-079 | Høj | 🔴 ÅBEN | Log selected key/type/parent/path før og efter alle selection-skift. |
| TRACE-080 | Høj | 🔴 ÅBEN | Log komplet Sortable lifecycle med source/target/zone/ParentKey/order før/efter. |
| TRACE-081 | Høj | 🔴 ÅBEN | Log Undo/Redo checkpoints med action type og berørte elementkeys. |
| TRACE-082 | Høj | 🔴 ÅBEN | Log save-start/save-success/save-fail + ContentVersion + change note hash. |
| TRACE-083 | Høj | 🔴 ÅBEN | Log render/refresh-kald med caller/tag og varighed; brug til repaint performance. |
| TRACE-084 | Normal | 🔴 ÅBEN | Eventfilter i UI: Selection / Drag / Layout / Inspector / Save / Error / Network. |
| TRACE-085 | Normal | 🔴 ÅBEN | Søgefelt i trace-viewer efter key, eventtype og tekst. |
| TRACE-086 | Normal | 🔴 ÅBEN | Download samlet support bundle: JSON trace + runtime versions + non-sensitive state summary. |
| TRACE-087 | Normal | 🔴 ÅBEN | Maks logstørrelse/ringbuffer med tydelig besked når gamle events roteres ud. |
| TRACE-088 | Normal | 🔴 ÅBEN | Automatisk markering af fatal JS error/unhandled rejection som Critical event. |
| TRACE-089 | Normal | 🔴 ÅBEN | QA af maskering: password/token/nonce/credential/cookie må aldrig eksporteres råt. |
| TRACE-090 | Normal | 🔴 ÅBEN | Trace performance-budget: logging må ikke mærkbart forværre drag/resize. |

---

# C. GitHub updater

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| UPDATER-VERSION-002 | Kritisk | 🟡 FIX-KANDIDAT v0.8.77+ | Auto-check, manuel check og UI viser samme `latest`. |
| UPDATER-STATUS-001 | Kritisk | 🟡 FIX-KANDIDAT v0.8.77+ | `installed < latest` → JA; ellers NEJ. Efter update må stale JA ikke overleve. |
| UPDATER-003 | Høj | 🟡 FIX-KANDIDAT | Atomisk state snapshot før render. |
| UPDATER-004 | Høj | 🔴 ÅBEN | Vis tidspunkt for seneste succesfulde check og om state er fresh/stale. |
| UPDATER-005 | Høj | 🔴 ÅBEN | Vis tydelig fejlstatus ved GitHub/netværksfejl uden at omdanne gammel state til falsk JA. |
| UPDATER-006 | Høj | 🔴 ÅBEN | Efter installation: reload aktiv pluginfil og verificer runtimeversion mod manifest før success notice. |
| UPDATER-007 | Høj | 🔴 ÅBEN | Efter installation: invalider relevante transients/options i én operation. |
| UPDATER-008 | Høj | 🔴 ÅBEN | Verificer package SHA før udpakning og igen mod downloadet fil. |
| UPDATER-009 | Høj | 🔴 ÅBEN | Verificer plugin code backup før mutation og auditér backupsti. |
| UPDATER-010 | Høj | 🔴 ÅBEN | Automatisk rollback-test ved simuleret install failure i QA. |
| UPDATER-011 | Normal | 🔴 ÅBEN | Vis installeret version, latest, SHA, published time og compatibility i ét statuskort. |
| UPDATER-012 | Normal | 🔴 ÅBEN | Disable Install-knap når installed >= latest. |
| UPDATER-013 | Normal | 🔴 ÅBEN | Vis changelog for latest direkte på Opdateringer. |
| UPDATER-014 | Normal | 🔴 ÅBEN | Tilføj read-only “Kopiér updater diagnose” til support. |
| UPDATER-015 | Normal | 🔴 ÅBEN | QA matrix: fresh install, equal, behind, ahead, GitHub offline, corrupt manifest, bad SHA. |

---

# D. Page versions, restore, undo og backup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PAGE-VERSION-RESTORE-001 | Høj | 🟡 FIX-KANDIDAT v0.8.78 | Versionshistorik med eksplicit Erstat original / Restore som kopi. |
| PAGE-VERSION-RESTORE-002 | Høj | 🔴 ÅBEN | Preview valgt historisk version uden write. |
| PAGE-VERSION-RESTORE-003 | Høj | 🔴 ÅBEN | Side-by-side eller strukturel sammenligning mellem aktuel og valgt version. |
| PAGE-VERSION-RESTORE-004 | Høj | 🔴 ÅBEN | Vis change summary: tilføjede/fjernede/flyttede/ændrede sektioner. |
| PAGE-VERSION-RESTORE-005 | Høj | 🔴 ÅBEN | Erstat original skal vise mål-side, version, backupkilde og safety-backup før confirm. |
| PAGE-VERSION-RESTORE-006 | Høj | 🔴 ÅBEN | Restore som kopi skal vise ny titel/slug før commit og sikre collision-safe slug. |
| PAGE-VERSION-RESTORE-007 | Høj | 🔴 ÅBEN | Undo Restore: pre-restore safety-version skal kunne vælges direkte. |
| PAGE-VERSION-RESTORE-008 | Normal | 🔴 ÅBEN | Filter versionslisten efter dato/bruger/change note. |
| PAGE-VERSION-RESTORE-009 | Normal | 🔴 ÅBEN | Markér hvilken version der matcher nuværende ContentHash. |
| PAGE-VERSION-RESTORE-010 | Normal | 🔴 ÅBEN | Vis om backupkilden har komplet Page Editor state eller kun post snapshot. |
| PAGE-VERSION-RESTORE-011 | Normal | 🔴 ÅBEN | Restore audit på Sider med mode, source version, target, safety backup og bruger. |
| PAGE-VERSION-RESTORE-012 | Normal | 🔴 ÅBEN | Mulighed for at navngive en version som milestone/release-point. |
| PAGE-VERSION-RESTORE-013 | Normal | 🔴 ÅBEN | Bevar featured image, excerpt, parent og relevant side-meta ved restore/copy. |
| PAGE-VERSION-RESTORE-014 | Normal | 🔴 ÅBEN | QA: restore original → reload → public preview → undo restore. |
| PAGE-VERSION-RESTORE-015 | Normal | 🔴 ÅBEN | QA: copy restore må aldrig ændre original ID/slug/menu/public URL. |
| BACKUP-B1-001 | Høj | ✅ FÆRDIG | Sikker managed page restore/copy med safety backup og audit. |
| BACKUP-B2-001 | Høj | ✅ FÆRDIG | Versioneret site backup/restore med selective restore. |
| BACKUP-002 | Høj | 🔴 ÅBEN | Backup retention UI: alder, antal, total størrelse. |
| BACKUP-003 | Høj | 🔴 ÅBEN | Integrity check af JSON/ZIP før restore. |
| BACKUP-004 | Normal | 🔴 ÅBEN | Eksportér restore-audit som CSV/JSON. |
| BACKUP-005 | Normal | 🔴 ÅBEN | Backup cleanup må aldrig slette seneste kendte rollback-point. |
| BACKUP-006 | Normal | 🔴 ÅBEN | Periodisk read-only backup health-check på Opdateringer/Backup. |

---

# E. WhatIf cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| WHATIF-CLEANUP-001 | Høj | 🟠 SOURCE AUDIT AKTIV | Fjern WhatIf ved kilden; shim/assets slettes til sidst. |
| WHATIF-002 | Høj | 🔴 ÅBEN | Fjern Vehicle save/layout/register/fields WhatIf UI og backend branches. |
| WHATIF-003 | Høj | 🔴 ÅBEN | Fjern Event save/layout/register WhatIf UI og backend branches. |
| WHATIF-004 | Høj | 🔴 ÅBEN | Fjern Gallery save/layout/rebuild WhatIf UI og backend branches. |
| WHATIF-005 | Høj | 🔴 ÅBEN | Fjern Page Editor WhatIf UI/branches og “WhatIf opretter ingen historik”-tekster. |
| WHATIF-006 | Høj | 🔴 ÅBEN | Fjern legacy sideindhold/static-content WhatIf UI/branches. |
| WHATIF-007 | Høj | 🔴 ÅBEN | Fjern Menu create/save/add/repair WhatIf UI/branches. |
| WHATIF-008 | Høj | 🔴 ÅBEN | Fjern Header/Footer/Design/shell sync WhatIf UI/branches. |
| WHATIF-009 | Normal | 🔴 ÅBEN | Fjern WhatIf fra dashboard/help/log tekster. |
| WHATIF-010 | Normal | 🔴 ÅBEN | Fjern CSS klasser og styling kun brugt til WhatIf. |
| WHATIF-011 | Normal | 🔴 ÅBEN | Fjern JS selectors/logic kun brugt til WhatIf. |
| WHATIF-012 | Høj | 🔴 ÅBEN | Fjern `NoWhatIfAdminController` når source er ren. |
| WHATIF-013 | Høj | 🔴 ÅBEN | Slet `hangar18-no-whatif-v0858.js/.css` når controlleren er væk. |
| WHATIF-014 | Høj | 🔴 ÅBEN | Repository-wide QA: ingen aktiv `whatif` request/state/runtime reference. |
| WHATIF-015 | Normal | 🔴 ÅBEN | Opdater DESIGN-MANUAL/brugermanual så WhatIf ikke længere beskrives som feature. |

---

# F. PowerShell / legacy bootstrap / gammel runtime cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGACY-POWERSHELL-CLEANUP-001 | Høj | 🔴 ÅBEN | Read-only audit af repo, release ZIP, plugin dir, uploads og legacy data. |
| LEGACY-002 | Høj | 🔴 ÅBEN | Bekræft at ingen `.ps1` ligger i release ZIP/installationsmappe. |
| LEGACY-003 | Høj | 🔴 ÅBEN | Audit efter `Hangar18-VehicleRegister.json` og beslægtede bootstrap JSON-filer. |
| LEGACY-004 | Høj | 🔴 ÅBEN | Audit WordPress options for gamle bootstrap/config-import flags og data. |
| LEGACY-005 | Høj | 🔴 ÅBEN | Klassificér legacy options som required migration data vs dead state. |
| LEGACY-006 | Høj | 🔴 ÅBEN | Backup før oprydning af dokumenteret døde options/files. |
| LEGACY-007 | Normal | 🔴 ÅBEN | Fjern startup-repair kode der kun var nødvendig til gamle migrationstrin, når sikkert. |
| LEGACY-008 | Normal | 🔴 ÅBEN | Fjern gamle one-time repair flags efter dokumenteret migration/QA. |
| LEGACY-009 | Normal | 🔴 ÅBEN | Audit Astra legacy repair-kode og marker hvad der fortsat kræves. |
| LEGACY-010 | Normal | 🔴 ÅBEN | Audit gamle menu migration/reparation shims. |
| LEGACY-011 | Normal | 🔴 ÅBEN | Audit gamle editor migration shims/importers. |
| LEGACY-012 | Normal | 🔴 ÅBEN | Release ZIP denylist for PowerShell, old JSON baseline og dev-only leftovers. |
| LEGACY-013 | Normal | 🔴 ÅBEN | Dokumentér endelig WordPress-native architecture efter cleanup. |

---

# G. LEGO runtime stability — frosset indtil trace

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGO-SELECTION-075 | Kritisk | ⏸ FROSSET / TRACE | Præcis én rød selection; nested/top-level skift korrekt. |
| LEGO-INSIDE-075 | Kritisk | ⏸ FROSSET / TRACE | `IND I KASSEN` på relevante container/grid/flex targets. |
| LEGO-REPAINT-062 | Høj | ⏸ FROSSET / TRACE | Ingen blink/unødige fulde rerenders. |
| LEGO-STABILITY-001 | Høj | 🔴 ÅBEN | Én dokumenteret selection-owner; fjern konkurrerende historiske selection-lag efter trace-proof. |
| LEGO-STABILITY-002 | Høj | 🔴 ÅBEN | Én dokumenteret placement-owner; fjern parallelle legacy placement fallback-lag efter trace-proof. |
| LEGO-STABILITY-003 | Høj | 🔴 ÅBEN | Én parent-model (`LayoutParentKey`) med invariant-validator. |
| LEGO-STABILITY-004 | Høj | 🔴 ÅBEN | Detect orphaned child keys og tilbyd repair. |
| LEGO-STABILITY-005 | Høj | 🔴 ÅBEN | Detect cyclic parent relations og blokér save. |
| LEGO-STABILITY-006 | Høj | 🔴 ÅBEN | Detect duplicate element keys og regenerér sikkert før save. |
| LEGO-STABILITY-007 | Høj | 🔴 ÅBEN | DOM/state consistency checker til debug/QA. |
| LEGO-STABILITY-008 | Normal | 🔴 ÅBEN | Render-count budget pr. click/resize/drop. |
| LEGO-STABILITY-009 | Normal | 🔴 ÅBEN | Ingen arbitrary settle timers i kritisk selection/placement path uden dokumenteret nødvendighed. |

---

# H. LEGO Navigator, selection og produktivitets-UX

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGO-NAV-001 | Kritisk | 🔴 ÅBEN | Hierarkisk Navigator/lagtræ: Side → Kasse/Grid/Flex → børn. |
| LEGO-NAV-002 | Høj | 🔴 ÅBEN | Klik i Navigator vælger præcis samme canonical element som canvas. |
| LEGO-NAV-003 | Høj | 🔴 ÅBEN | Canvas-selection synkroniserer Navigator highlight og autoscroll. |
| LEGO-NAV-004 | Høj | 🔴 ÅBEN | Fold/udfold containere i Navigator. |
| LEGO-NAV-005 | Høj | 🔴 ÅBEN | Drag/drop i Navigator med samme parent/history-motor som canvas. |
| LEGO-NAV-006 | Høj | 🔴 ÅBEN | Kontextmenu i Navigator: Rediger, Duplikér, Kopiér, Flyt, Wrap, Fjern. |
| LEGO-NAV-007 | Høj | 🔴 ÅBEN | Breadcrumb: Side > Container > Row > Element. |
| LEGO-NAV-008 | Normal | 🔴 ÅBEN | Søg i Navigator efter navn/type/key. |
| LEGO-NAV-009 | Normal | 🔴 ÅBEN | Filtrer Navigator efter elementtype. |
| LEGO-NAV-010 | Normal | 🔴 ÅBEN | Vis skjulte/disabled elementer med særskilt statusikon. |
| LEGO-MOVE-001 | Kritisk | 🔴 ÅBEN | Alternativ deterministisk `Flyt til…` via Inspector/Navigator uden drag/drop. |
| LEGO-MOVE-002 | Høj | 🔴 ÅBEN | `Flyt ud af Kasse` handling. |
| LEGO-MOVE-003 | Høj | 🔴 ÅBEN | `Flyt før/efter…` via menu. |
| LEGO-MOVE-004 | Høj | 🔴 ÅBEN | `Flyt til top/bund` i samme parent. |
| LEGO-MOVE-005 | Høj | 🔴 ÅBEN | Parent-picker viser kun gyldige targets og forhindrer cycles. |
| LEGO-COPY-001 | Høj | 🔴 ÅBEN | Kopiér element med content/design/layout/responsive state. |
| LEGO-COPY-002 | Høj | 🔴 ÅBEN | Indsæt kopi med nye keys og korrekte child references. |
| LEGO-COPY-003 | Høj | 🔴 ÅBEN | Kopiér hel Kasse inkl. nested children. |
| LEGO-COPY-004 | Normal | 🔴 ÅBEN | Copy Styles / Paste Styles uden content. |
| LEGO-DUP-001 | Høj | 🔴 ÅBEN | Konsistent Duplikér på alle elementtyper/containere. |
| LEGO-MULTI-001 | Normal | 🔴 ÅBEN | Multi-select flere siblings. |
| LEGO-MULTI-002 | Normal | 🔴 ÅBEN | Bulk move/delete/duplicate/design for multi-select. |
| LEGO-KEYBOARD-001 | Normal | 🔴 ÅBEN | Delete/Backspace med sikkerhedsregler. |
| LEGO-KEYBOARD-002 | Normal | 🔴 ÅBEN | Ctrl/Cmd+C/V, Ctrl/Cmd+D. |
| LEGO-KEYBOARD-003 | Normal | 🔴 ÅBEN | Ctrl/Cmd+Z/Y matcher canonical Undo/Redo. |
| LEGO-KEYBOARD-004 | Normal | 🔴 ÅBEN | Piletaster til Navigator navigation og evt. finflytning. |

---

# I. LEGO drag/drop, layout, Grid og Flex

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGO-DROP-001 | Høj | 🔴 ÅBEN | Visuel dropzone-kontrakt for Over/Under/Venstre/Højre/Ind i. |
| LEGO-DROP-002 | Høj | 🔴 ÅBEN | Zone priority matrix når overlays overlapper. |
| LEGO-DROP-003 | Høj | 🔴 ÅBEN | Drop preview/ghost viser forventet slutplacering før release. |
| LEGO-DROP-004 | Høj | 🔴 ÅBEN | Invalid targets vises tydeligt disabled i stedet for silent fallback. |
| LEGO-DROP-005 | Normal | 🔴 ÅBEN | Auto-scroll canvas under drag nær top/bund. |
| LEGO-DROP-006 | Normal | 🔴 ÅBEN | Touch/pointer support til tablet. |
| LEGO-LAYOUT-001 | Høj | ✅ FOUNDATION | 12-kolonne Desktop spans. |
| LEGO-LAYOUT-002 | Høj | ✅ FOUNDATION | Tablet/Mobil overrides + Arv Desktop. |
| LEGO-LAYOUT-003 | Høj | 🔴 ÅBEN | Synlig kolonneindikator under resize: fx 7/5. |
| LEGO-LAYOUT-004 | Høj | 🔴 ÅBEN | Numerisk span-input som alternativ til drag-handle. |
| LEGO-LAYOUT-005 | Høj | 🔴 ÅBEN | Grid: antal kolonner/rows direkte i Inspector. |
| LEGO-LAYOUT-006 | Høj | 🔴 ÅBEN | Grid: row/column gap separat og responsive. |
| LEGO-LAYOUT-007 | Høj | 🔴 ÅBEN | Grid: per-child column/row span. |
| LEGO-LAYOUT-008 | Høj | 🔴 ÅBEN | Flex: direction row/column. |
| LEGO-LAYOUT-009 | Høj | 🔴 ÅBEN | Flex: wrap/no-wrap. |
| LEGO-LAYOUT-010 | Høj | 🔴 ÅBEN | Flex: justify-content grafisk kontrol. |
| LEGO-LAYOUT-011 | Høj | 🔴 ÅBEN | Flex: align-items/align-self grafisk kontrol. |
| LEGO-LAYOUT-012 | Normal | 🔴 ÅBEN | Order-kontrol pr. child. |
| LEGO-LAYOUT-013 | Normal | 🔴 ÅBEN | Gap presets fra design tokens. |
| LEGO-LAYOUT-014 | Normal | 🔴 ÅBEN | Equal-width fordelingsknap. |
| LEGO-LAYOUT-015 | Normal | 🔴 ÅBEN | Distribute space evenly. |
| LEGO-LAYOUT-016 | Normal | 🔴 ÅBEN | Align left/center/right/top/middle/bottom. |
| LEGO-LAYOUT-017 | Normal | 🔴 ÅBEN | Min/max antal columns afhængigt af breakpoint. |
| LEGO-LAYOUT-018 | Normal | 🔴 ÅBEN | Container width modes: full, content, custom. |

---

# J. Responsive design

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| RESP-001 | Høj | ✅ FOUNDATION | Desktop/Tablet/Mobil preview + reversible overrides. |
| RESP-002 | Høj | 🔴 ÅBEN | Vis/skjul pr. Desktop/Tablet/Mobil. |
| RESP-003 | Høj | 🔴 ÅBEN | Responsive order pr. breakpoint. |
| RESP-004 | Høj | 🔴 ÅBEN | Responsive Flex direction. |
| RESP-005 | Høj | 🔴 ÅBEN | Responsive Grid columns. |
| RESP-006 | Høj | 🔴 ÅBEN | Responsive width/height/min/max. |
| RESP-007 | Høj | 🔴 ÅBEN | Responsive padding/margin/gap med tydelig inheritance indicator. |
| RESP-008 | Høj | 🔴 ÅBEN | Responsive typography size/line-height/letter spacing. |
| RESP-009 | Normal | 🔴 ÅBEN | Breakpoint preview bredde kan justeres manuelt inden for breakpoint. |
| RESP-010 | Normal | 🔴 ÅBEN | Device presets: iPhone, small tablet, tablet landscape, laptop. |
| RESP-011 | Normal | 🔴 ÅBEN | Overflow warnings pr. breakpoint. |
| RESP-012 | Normal | 🔴 ÅBEN | “Reset breakpoint” og “Arv Desktop” på hele designgruppen. |
| RESP-013 | Normal | 🔴 ÅBEN | Visual badges der viser hvor overrides findes. |

---

# K. Spacing, størrelse og positionering

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| SPACE-001 | Høj | ✅ FOUNDATION | X/Y gap og margin. |
| SPACE-002 | Høj | 🔴 ÅBEN | Individuel Top/Right/Bottom/Left margin. |
| SPACE-003 | Høj | 🔴 ÅBEN | Individuel Top/Right/Bottom/Left padding. |
| SPACE-004 | Normal | 🔴 ÅBEN | Link/unlink sider grafisk. |
| SPACE-005 | Normal | 🔴 ÅBEN | Unit support px/%/rem/em/vw/vh hvor relevant. |
| SIZE-001 | Høj | 🔴 ÅBEN | Width: auto/%/px/custom. |
| SIZE-002 | Høj | 🔴 ÅBEN | Min-width/max-width. |
| SIZE-003 | Høj | 🔴 ÅBEN | Height: auto/px/%/viewport. |
| SIZE-004 | Høj | 🔴 ÅBEN | Min-height/max-height. |
| SIZE-005 | Normal | 🔴 ÅBEN | Aspect ratio lock for billed-/mediaelementer. |
| POS-001 | Normal | 🔴 ÅBEN | Position mode: static/relative/sticky. |
| POS-002 | Normal | 🔴 ÅBEN | Absolute positioning kun i eksplicit advanced mode med safeguards. |
| POS-003 | Normal | 🔴 ÅBEN | z-index kontrol. |
| POS-004 | Normal | 🔴 ÅBEN | Top/right/bottom/left offsets for positionerede elementer. |
| POS-005 | Normal | 🔴 ÅBEN | Sticky top offset og collision warning med header. |

---

# L. Design, typografi og visuel styling

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| DESIGN-001 | Høj | ✅ FOUNDATION | Fælles canonical design model for element/Kasse/Grid/Flex. |
| TYPE-001 | Høj | 🔴 ÅBEN | Font family picker + theme/design token defaults. |
| TYPE-002 | Høj | 🔴 ÅBEN | Font size responsive. |
| TYPE-003 | Høj | 🔴 ÅBEN | Weight/style. |
| TYPE-004 | Høj | 🔴 ÅBEN | Line height. |
| TYPE-005 | Normal | 🔴 ÅBEN | Letter spacing. |
| TYPE-006 | Normal | 🔴 ÅBEN | Text transform. |
| TYPE-007 | Normal | 🔴 ÅBEN | Text decoration. |
| TYPE-008 | Normal | 🔴 ÅBEN | Text alignment responsive. |
| COLOR-001 | Høj | 🔴 ÅBEN | Color picker med design tokens/recent colors. |
| BG-001 | Høj | 🔴 ÅBEN | Background solid. |
| BG-002 | Høj | 🔴 ÅBEN | Background image via Media Library. |
| BG-003 | Høj | 🔴 ÅBEN | Background position/repeat/size cover-contain. |
| BG-004 | Normal | 🔴 ÅBEN | Linear/radial gradient editor. |
| BG-005 | Normal | 🔴 ÅBEN | Overlay color/opacity. |
| BORDER-001 | Høj | 🔴 ÅBEN | Border width/style/color samlet. |
| BORDER-002 | Normal | 🔴 ÅBEN | Individuelle border-sider. |
| RADIUS-001 | Høj | 🔴 ÅBEN | Border radius samlet. |
| RADIUS-002 | Normal | 🔴 ÅBEN | Individuelle hjørner. |
| SHADOW-001 | Normal | 🔴 ÅBEN | Box shadow editor med x/y/blur/spread/opacity. |
| OPACITY-001 | Normal | 🔴 ÅBEN | Element opacity. |
| TRANSITION-001 | Høj | ✅ FOUNDATION | Interaction transition state findes. |
| ANIM-001 | Normal | 🔴 ÅBEN | Simple entrance fade/slide/scale. |
| ANIM-002 | Normal | 🔴 ÅBEN | Reduced-motion respekt. |
| ANIM-003 | Lav | 🔴 ÅBEN | Delay/duration presets; ingen tunge animationer som standard. |

---

# M. Interaction states

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| STATE-001 | Høj | ✅ FOUNDATION | Normal/Hover/Focus/Active/Disabled canonical states. |
| STATE-002 | Høj | 🔴 ÅBEN | Tydelig state-switcher i Direct Design. |
| STATE-003 | Høj | 🔴 ÅBEN | Preview state uden at kræve reel hover/focus. |
| STATE-004 | Høj | 🔴 ÅBEN | Copy Normal → Hover/Focus som startpunkt. |
| STATE-005 | Normal | 🔴 ÅBEN | Reset state override. |
| STATE-006 | Høj | 🔴 ÅBEN | Accessibility guard: Focus outline må ikke fjernes uden alternativ synlig focus style. |

---

# N. Canvas og editor workspace

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| CANVAS-001 | Høj | 🔴 ÅBEN | Zoom 50/75/100/125/150 %. |
| CANVAS-002 | Høj | 🔴 ÅBEN | Fit page / fit width. |
| CANVAS-003 | Normal | 🔴 ÅBEN | Pan canvas ved zoom. |
| CANVAS-004 | Høj | 🔴 ÅBEN | Rulers/guides valgfrit. |
| CANVAS-005 | Høj | 🔴 ÅBEN | Snap guides når kanter/centre flugter. |
| CANVAS-006 | Normal | 🔴 ÅBEN | Vis breakpoint canvas width tydeligt. |
| CANVAS-007 | Normal | 🔴 ÅBEN | Toggle outlines for all containers. |
| CANVAS-008 | Normal | 🔴 ÅBEN | Toggle spacing visualization (margin/padding/gap overlay). |
| CANVAS-009 | Normal | 🔴 ÅBEN | Empty container placeholder med tydelig drop-instruktion. |
| CANVAS-010 | Normal | 🔴 ÅBEN | Minimap/structure overview ved meget lange sider. |
| WORKSPACE-001 | Høj | ✅ FOUNDATION | Foldbare venstre/højre rails. |
| WORKSPACE-002 | Normal | 🔴 ÅBEN | Resizable rail widths. |
| WORKSPACE-003 | Normal | 🔴 ÅBEN | Gem workspace layout per bruger/browser. |
| WORKSPACE-004 | Normal | 🔴 ÅBEN | Fullscreen Designer mode. |

---

# O. Elementbibliotek og nye elementtyper

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| ELEM-001 | Høj | ✅ FOUNDATION | Søgbart elementbibliotek, kategorier og favoritter. |
| ELEM-002 | Normal | 🔴 ÅBEN | Senest brugte elementer. |
| ELEM-003 | Normal | 🔴 ÅBEN | Favorite reorder. |
| ELEM-004 | Normal | 🔴 ÅBEN | Elementbeskrivelse/tooltip med preview. |
| ELEM-005 | Høj | 🔴 ÅBEN | Heading-element H1–H6 med semantic guard. |
| ELEM-006 | Høj | 🔴 ÅBEN | Rich text element med begrænset toolbar. |
| ELEM-007 | Høj | 🔴 ÅBEN | Button/CTA element. |
| ELEM-008 | Høj | 🔴 ÅBEN | Icon element. |
| ELEM-009 | Normal | 🔴 ÅBEN | Divider element. |
| ELEM-010 | Normal | 🔴 ÅBEN | Spacer element med responsive højde. |
| ELEM-011 | Høj | 🔴 ÅBEN | Video embed element med privacy-friendly mode. |
| ELEM-012 | Normal | 🔴 ÅBEN | Map/iframe embed med allowlist/sanitization. |
| ELEM-013 | Normal | 🔴 ÅBEN | Quote/testimonial element. |
| ELEM-014 | Normal | 🔴 ÅBEN | List element. |
| ELEM-015 | Normal | 🔴 ÅBEN | Table element UX-forbedring. |
| ELEM-016 | Normal | 🔴 ÅBEN | Accordion element. |
| ELEM-017 | Normal | 🔴 ÅBEN | Tabs element. |
| ELEM-018 | Normal | 🔴 ÅBEN | Modal/lightbox trigger element. |
| ELEM-019 | Normal | 🔴 ÅBEN | Social links element. |
| ELEM-020 | Normal | 🔴 ÅBEN | Breadcrumb public element hvis site-design kræver det. |

---

# P. Media og Asset Manager integration

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| MEDIA-001 | Høj | ✅ FOUNDATION | WordPress Media integration + Asset Manager metadata. |
| MEDIA-002 | Høj | 🔴 ÅBEN | Drag billede direkte fra asset browser til canvas. |
| MEDIA-003 | Høj | 🔴 ÅBEN | Alt-tekst advarsel direkte i Inspector. |
| MEDIA-004 | Høj | 🔴 ÅBEN | Focal point preview i billed-element. |
| MEDIA-005 | Normal | 🔴 ÅBEN | Crop/aspect presets. |
| MEDIA-006 | Normal | 🔴 ÅBEN | object-fit/object-position controls. |
| MEDIA-007 | Normal | 🔴 ÅBEN | Lazy-load setting med safe defaults. |
| MEDIA-008 | Normal | 🔴 ÅBEN | Responsive image size/source summary. |
| MEDIA-009 | Normal | 🔴 ÅBEN | Find duplicate/unused assets fra Designer. |
| MEDIA-010 | Normal | 🔴 ÅBEN | Replace media globally med usage preview. |

---

# Q. Components, presets, templates og global design

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| COMP-001 | Høj | 🔴 ÅBEN | Gem valgt element som preset. |
| COMP-002 | Høj | 🔴 ÅBEN | Gem hel Kasse/sektion som reusable component. |
| COMP-003 | Høj | 🔴 ÅBEN | Indsæt reusable component med nye instance keys. |
| COMP-004 | Normal | 🔴 ÅBEN | Linked/global component mode med controlled propagation. |
| COMP-005 | Normal | 🔴 ÅBEN | Detach linked component til lokal kopi. |
| COMP-006 | Normal | 🔴 ÅBEN | Versionering af reusable components. |
| TEMPLATE-001 | Høj | 🔴 ÅBEN | Hero template. |
| TEMPLATE-002 | Høj | 🔴 ÅBEN | 2-column text/image template. |
| TEMPLATE-003 | Høj | 🔴 ÅBEN | 3/4-card row template. |
| TEMPLATE-004 | Normal | 🔴 ÅBEN | CTA banner template. |
| TEMPLATE-005 | Normal | 🔴 ÅBEN | Contact section template. |
| TEMPLATE-006 | Normal | 🔴 ÅBEN | Gallery/media section template. |
| TEMPLATE-007 | Normal | 🔴 ÅBEN | Save whole page as template. |
| TEMPLATE-008 | Normal | 🔴 ÅBEN | Create page from template med preview. |
| TOKENS-001 | Høj | 🔴 ÅBEN | Global color tokens UI. |
| TOKENS-002 | Høj | 🔴 ÅBEN | Global typography tokens UI. |
| TOKENS-003 | Høj | 🔴 ÅBEN | Global spacing tokens UI. |
| TOKENS-004 | Normal | 🔴 ÅBEN | Radius/shadow tokens. |
| TOKENS-005 | Høj | 🔴 ÅBEN | Element styles kan vælge token eller local override. |
| TOKENS-006 | Normal | 🔴 ÅBEN | Usage-list før ændring af global token. |

---

# R. Forms, polls, dynamic data og funktionselementer

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| FORM-001 | Høj | ✅ FOUNDATION | Mailformular funktion findes. |
| FORM-002 | Høj | 🔴 ÅBEN | Visuel form builder med drag/reorder fields. |
| FORM-003 | Høj | 🔴 ÅBEN | Field validation UI og inline fejlpreview. |
| FORM-004 | Høj | 🔴 ÅBEN | Success/error message design i Designer. |
| FORM-005 | Normal | 🔴 ÅBEN | Submission storage toggle + retention UI. |
| FORM-006 | Normal | 🔴 ÅBEN | CSV export fra relevant adminside. |
| FORM-007 | Høj | 🔴 ÅBEN | Anti-spam status og rate-limit diagnostics. |
| POLL-001 | Høj | ✅ FOUNDATION | Afstemningsfunktion findes. |
| POLL-002 | Normal | 🔴 ÅBEN | Visuel poll builder. |
| POLL-003 | Normal | 🔴 ÅBEN | Result chart style controls. |
| POLL-004 | Normal | 🔴 ÅBEN | Schedule/start/end UX. |
| DATA-001 | Høj | ✅ FOUNDATION | Dynamic data/query infrastructure. |
| DATA-002 | Høj | 🔴 ÅBEN | Dynamic binding picker uden rå shortcode-kendskab. |
| DATA-003 | Høj | 🔴 ÅBEN | Preview binding med eksempeldata. |
| DATA-004 | Normal | 🔴 ÅBEN | Empty-state/fallback content. |
| DATA-005 | Normal | 🔴 ÅBEN | Query builder filters/sort/limit UI. |

---

# S. Header, Footer og Menu Builder videreudvikling

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| HEADER-001 | Høj | ✅ SHADOW FOUNDATION | Visual Header/Footer builder findes i shadow mode. |
| HEADER-002 | Høj | 🔴 ÅBEN | Import nuværende legacy header til editable shadow struktur 1:1. |
| HEADER-003 | Høj | 🔴 ÅBEN | Responsive header rows/columns. |
| HEADER-004 | Høj | 🔴 ÅBEN | Sticky behavior og offset preview. |
| HEADER-005 | Normal | 🔴 ÅBEN | Logo size/crop responsive. |
| FOOTER-001 | Høj | 🔴 ÅBEN | Import nuværende footer 1:1 til editable shadow struktur. |
| FOOTER-002 | Normal | 🔴 ÅBEN | Multi-column responsive footer. |
| MENU-001 | Høj | ✅ FOUNDATION | Menu Builder v2 nested editor. |
| MENU-002 | Høj | 🔴 ÅBEN | Live header/menu preview i Designer. |
| MENU-003 | Normal | 🔴 ÅBEN | Mobile menu visual configuration. |
| MENU-004 | Normal | 🔴 ÅBEN | Menu item visibility rules pr. breakpoint. |
| MENU-005 | Normal | 🔴 ÅBEN | Active/current item styling tokens. |
| MENU-006 | Normal | 🔴 ÅBEN | Keyboard navigation accessibility preview. |

---

# T. Side management og editor workflow

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PAGE-001 | Høj | ✅ FOUNDATION | Opret blank side / template page. |
| PAGE-002 | Høj | ✅ FOUNDATION | Sikker Trash med safety backup. |
| PAGE-003 | Normal | 🔴 ÅBEN | Duplicate whole page fra Sider. |
| PAGE-004 | Normal | 🔴 ÅBEN | Rename slug med link/menu impact preview. |
| PAGE-005 | Normal | 🔴 ÅBEN | Page status draft/private/publish UX. |
| PAGE-006 | Normal | 🔴 ÅBEN | Scheduled publish. |
| PAGE-007 | Normal | 🔴 ÅBEN | Page-level SEO title/meta summary integration. |
| PAGE-008 | Normal | 🔴 ÅBEN | Page-level custom CSS advanced panel med validation. |
| PAGE-009 | Normal | 🔴 ÅBEN | Lock page against accidental edits. |
| PAGE-010 | Normal | 🔴 ÅBEN | Change note required/optional policy configurable. |
| PAGE-011 | Høj | 🔴 ÅBEN | Autosave/crash recovery for working state uden permanent version. |
| PAGE-012 | Høj | 🔴 ÅBEN | Recovery banner efter browser crash/reload. |

---

# U. Undo/Redo og history

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| HISTORY-001 | Kritisk | ✅ FOUNDATION | Én canonical Undo/Redo owner. |
| HISTORY-002 | Høj | 🔴 ÅBEN | Vis human-readable Undo/Redo label: “Flyt Billede ind i Kasse”. |
| HISTORY-003 | Høj | 🔴 ÅBEN | History panel med seneste N handlinger. |
| HISTORY-004 | Høj | 🔴 ÅBEN | Structural transaction må kun give ét checkpoint. |
| HISTORY-005 | Høj | 🔴 ÅBEN | Design slider/input coalescing til ét logisk checkpoint. |
| HISTORY-006 | Normal | 🔴 ÅBEN | Clear history efter permanent save med tydelig boundary. |
| HISTORY-007 | Normal | 🔴 ÅBEN | Trace integration for every checkpoint. |
| HISTORY-008 | Normal | 🔴 ÅBEN | QA matrix for move, nesting, duplicate, delete, resize, responsive, design. |

---

# V. Accessibility, SEO, performance og quality

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| A11Y-001 | Høj | ✅ FOUNDATION | Side Health accessibility analyser findes. |
| A11Y-002 | Høj | 🔴 ÅBEN | Inline contrast warning i Inspector. |
| A11Y-003 | Høj | 🔴 ÅBEN | Missing alt text warning. |
| A11Y-004 | Høj | 🔴 ÅBEN | Heading hierarchy warning. |
| A11Y-005 | Høj | 🔴 ÅBEN | Focus-visible warning/preview. |
| A11Y-006 | Normal | 🔴 ÅBEN | Label/field association checks for forms. |
| A11Y-007 | Normal | 🔴 ÅBEN | Keyboard-only Designer core flow test. |
| A11Y-008 | Normal | 🔴 ÅBEN | Screen reader core flow evidence. |
| SEO-001 | Høj | ✅ FOUNDATION | Side Health SEO analyse findes. |
| SEO-002 | Normal | 🔴 ÅBEN | Meta title/description editing integration. |
| SEO-003 | Normal | 🔴 ÅBEN | OpenGraph image/title preview. |
| SEO-004 | Normal | 🔴 ÅBEN | Canonical URL read-only status. |
| PERF-001 | Høj | 🔴 ÅBEN | Editor performance baseline: click/drop/resize/save timings. |
| PERF-002 | Høj | 🔴 ÅBEN | Reduce unnecessary MutationObservers/full renders. |
| PERF-003 | Høj | 🔴 ÅBEN | Public CSS/JS payload budget efter cutover. |
| PERF-004 | Normal | 🔴 ÅBEN | Image size/lazy-load warnings. |
| PERF-005 | Normal | 🔴 ÅBEN | DOM depth warning for excessive nesting. |
| QUALITY-001 | Høj | 🔴 ÅBEN | Save-time structural validator før persistence. |
| QUALITY-002 | Høj | 🔴 ÅBEN | Detect horizontal overflow pr. breakpoint. |
| QUALITY-003 | Normal | 🔴 ÅBEN | Detect empty containers/empty buttons/broken media references. |

---

# W. Testing og QA automation

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| QA-001 | Høj | 🔴 ÅBEN | Canonical unit tests for parent/child invariants. |
| QA-002 | Høj | 🔴 ÅBEN | Browser test for selection. |
| QA-003 | Høj | 🔴 ÅBEN | Browser test for Over/Under/Left/Right/Inside. |
| QA-004 | Høj | 🔴 ÅBEN | Browser test for Navigator move-to-parent. |
| QA-005 | Høj | 🔴 ÅBEN | Browser test for Undo/Redo transaction boundaries. |
| QA-006 | Høj | 🔴 ÅBEN | Browser test for Desktop/Tablet/Mobil inheritance. |
| QA-007 | Høj | 🔴 ÅBEN | Browser test for save/reload persistence. |
| QA-008 | Høj | 🔴 ÅBEN | Browser test for page version restore/copy. |
| QA-009 | Høj | 🔴 ÅBEN | Browser test updater state equal/behind/ahead. |
| QA-010 | Høj | 🔴 ÅBEN | Protected Vehicle regression. |
| QA-011 | Høj | 🔴 ÅBEN | Protected Event regression. |
| QA-012 | Høj | 🔴 ÅBEN | Protected Gallery regression. |
| QA-013 | Normal | 🔴 ÅBEN | Chrome manual acceptance. |
| QA-014 | Normal | 🔴 ÅBEN | Edge manual acceptance. |
| QA-015 | Normal | 🔴 ÅBEN | Firefox manual acceptance. |
| QA-016 | Normal | 🔴 ÅBEN | Safari manual acceptance. |
| QA-017 | Normal | 🔴 ÅBEN | Mobile Safari / touch sanity. |
| QA-018 | Normal | 🔴 ÅBEN | Regression screenshots på centrale test2 sider. |
| QA-019 | Normal | 🔴 ÅBEN | PHP 8.0/8.2/8.3 matrix for admin handlers. |
| QA-020 | Normal | 🔴 ÅBEN | JS syntax/lint/build checks for all editor assets. |

---

# X. Dokumentation og support

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| DOC-001 | Høj | ✅ FOUNDATION | Visuel Ultimate Designer brugermanual findes. |
| DOC-002 | Høj | ✅ FOUNDATION | Quick reference findes. |
| DOC-003 | Høj | 🔴 ÅBEN | Opdater manual efter WhatIf removal. |
| DOC-004 | Høj | 🔴 ÅBEN | Opdater manual med Navigator/Move-to/Copy-Paste. |
| DOC-005 | Normal | 🔴 ÅBEN | Restore/version history guide. |
| DOC-006 | Normal | 🔴 ÅBEN | Trace/debug support guide. |
| DOC-007 | Normal | 🔴 ÅBEN | Updater troubleshooting guide. |
| DOC-008 | Normal | 🔴 ÅBEN | Design tokens/presets guide. |
| DOC-009 | Normal | 🔴 ÅBEN | Accessibility authoring checklist. |
| DOC-010 | Normal | 🔴 ÅBEN | Release/rollback operator guide samlet på én side. |
| SUPPORT-001 | Normal | 🔴 ÅBEN | “Kopiér systemstatus” med plugin/WP/PHP/browser/runtime versions. |
| SUPPORT-002 | Normal | 🔴 ÅBEN | Support bundle uden personlige/sensitive data. |

---

# Y. Migration, I9 og I10

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| I9-EVIDENCE | Høj | 🟡 PENDING | Faktisk manual/live evidence for alle gates. |
| I9-001 | Høj | 🔴 ÅBEN | Authenticated test2 Designer E2E. |
| I9-002 | Høj | 🔴 ÅBEN | Comparison page visual parity. |
| I9-003 | Høj | 🔴 ÅBEN | Vehicle/Event/Gallery protected regression evidence. |
| I9-004 | Høj | 🔴 ÅBEN | Backup/restore rehearsal. |
| I9-005 | Normal | 🔴 ÅBEN | Browser matrix evidence. |
| I9-006 | Normal | 🔴 ÅBEN | Screen-reader evidence. |
| I10-CUTOVER | Kritisk | 🔒 LÅST | Public cutover først efter I9 PASS og final production preflight. |
| I10-001 | Høj | 🔴 ÅBEN | Comparison page cutover-plan. |
| I10-002 | Høj | 🔴 ÅBEN | Hjem controlled conversion plan. |
| I10-003 | Høj | 🔴 ÅBEN | Om controlled conversion plan. |
| I10-004 | Høj | 🔴 ÅBEN | Kontakt controlled conversion plan. |
| I10-005 | Høj | 🔴 ÅBEN | Bliv medlem controlled conversion plan. |
| I10-006 | Høj | 🔴 ÅBEN | Header/Footer controlled assignment plan. |
| I10-007 | Høj | 🔴 ÅBEN | Legacy renderer removal plan efter stabil cutover. |
| I10-008 | Høj | 🔴 ÅBEN | Post-cutover rollback window og monitoreringscheckliste. |

---

# Z. Beskyttede specialdomæner

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PROTECT-VEHICLE-001 | Kritisk | 🔒 BESKYT | Vehicle eksisterende data/editor/public output må ikke regressere under generelle changes. |
| PROTECT-EVENT-001 | Kritisk | 🔒 BESKYT | Event eksisterende data/editor/archive/public output må ikke regressere. |
| PROTECT-GALLERY-001 | Kritisk | 🔒 BESKYT | Gallery albums/media/public output må ikke regressere. |
| PROTECT-002 | Høj | 🔴 ÅBEN | Snapshot-regression af de tre domains i CI/manual suite. |
| PROTECT-003 | Høj | 🔴 ÅBEN | Shared shell/design changes skal have explicit protected-domain visual QA. |

---

# Prioriteret arbejdsrækkefølge

## Spor 1 — cleanup og sikker platform
1. `WHATIF-CLEANUP-001` + WHATIF-002..015.
2. `LEGACY-POWERSHELL-CLEANUP-001` + LEGACY-002..013.
3. Smoke-test/færdiggør TRACE-076 og UPDATER v0.8.77 state-fix.
4. Smoke-test PAGE-VERSION-RESTORE v0.8.78.

## Spor 2 — gør LEGO-editoren effektiv uden at afhænge af de frosne dragbugs
5. `LEGO-NAV-001` hierarkisk Navigator.
6. `LEGO-MOVE-001` deterministisk Flyt til…
7. Breadcrumb + Navigator selection sync.
8. Copy/Paste/Duplicate/Move out/Move before-after.
9. History labels/panel.

## Spor 3 — layout og responsive
10. Grid/Flex direkte controls.
11. Individuel TRBL spacing og size controls.
12. Responsive show/hide/order/direction/columns.
13. Canvas zoom/guides/spacing overlays.

## Spor 4 — design og produktivitet
14. Typography/background/border/radius/shadow UI.
15. Global tokens.
16. Reusable components og section/page templates.
17. Media integration og accessibility warnings.

## Spor 5 — genåbn kendte runtimebugs med trace
18. LEGO-SELECTION-075.
19. LEGO-INSIDE-075.
20. LEGO-REPAINT-062.
21. Fjern historiske konkurrerende runtime-lag først når trace og regressiontests beviser canonical owner.

## Spor 6 — acceptance og migration
22. A–L samlet Designer acceptance.
23. Browser/accessibility/backup/protected-domain I9 evidence.
24. I10 planning/rehearsal.
25. Public cutover forbliver sidste gate.

---

# Næste aktive kodeopgaver

1. **WHATIF-CLEANUP-001** — audit er allerede startet; fjern source i sikre batches.
2. **LEGACY-POWERSHELL-CLEANUP-001** — read-only audit efter WhatIf-batch.
3. **LEGO-NAV-001** — første nye LEGO-produktfeature efter cleanup.
4. **LEGO-MOVE-001** — alternativ til drag/drop, så editoren forbliver produktiv selv ved runtimebugs.

Canonical backlog skal opdateres igen ved hvert af ovenstående trin.