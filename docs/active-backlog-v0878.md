# Hangar18 Manager — aktiv backlog v0.8.78

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.78**  
**Release commit:** `a91ae4fbf8cd06b7a222afd1c7df7c3a4ea72484`  
**Package SHA-256:** `1b87f85e2493db007428853347f9b2028d4f16cbb1eb85d03cd071c8d06f17f7`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. `active-backlog-v0877.md` og ældre filer er historiske snapshots.

## Aktuel status

| ID | Prioritet | Status | Næste handling |
|---|---|---|---|
| TRACE-076 | Kritisk | 🟡 MANUEL TEST | Smoke-test master TIL/FRA og testbjælke. |
| UPDATER-VERSION-002 | Kritisk | 🟡 FIX-KANDIDAT v0.8.77+ | Test page-load/auto-check viser samme latest som JA/NEJ. |
| UPDATER-STATUS-001 | Kritisk | 🟡 FIX-KANDIDAT v0.8.77+ | Test installeret==latest → NEJ efter update/refresh. |
| PAGE-VERSION-RESTORE-001 | Høj | 🟡 FIX-KANDIDAT v0.8.78 | Test versionsliste, Erstat original med safety backup og Restore som kopi/draft. Preview/sammenligning kan udbygges yderligere efter smoke-test. |
| WHATIF-CLEANUP-001 | Høj | 🟠 SOURCE AUDIT AKTIV | Kortlæg og fjern aktive WhatIf branches/UI ved kilden; fjern shim/assets/controller til sidst. |
| LEGACY-POWERSHELL-CLEANUP-001 | Høj | 🔴 ÅBEN | Read-only audit af runtime/uploads/legacy artifacts. |
| LEGO-SELECTION-075 | Kritisk | ⏸ FROSSET / TRACE | Kun med konkret trace. |
| LEGO-INSIDE-075 | Kritisk | ⏸ FROSSET / TRACE | Kun med konkret trace. |
| LEGO-REPAINT-062 | Høj | ⏸ FROSSET / TRACE | Kun med konkret trace. |
| LEGO-PRODUCT-ROADMAP | Høj | 🟡 KLAR | Fortsæt Navigator/lagtræ, alternativ Flyt til Kasse, copy/paste, layout/design-værktøjer uden at genåbne frosne bugs. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Efter kritiske regressions. |
| I10-CUTOVER | Normal | 🔒 LÅST | Først efter I9 PASS + særskilt godkendelse. |

## v0.8.78 — Page Version Restore

På Hangar18 Manager → Sider bliver den eksisterende `hangar18_manager_page_versions_v1` versionshistorik nu handlingsbar.

For hver version vælges eksplicit:

- **Erstat original** — B1 preflight + automatisk sikkerhedsbackup før write; original ID/slug/URL bevares.
- **Restore som kopi** — originalen røres ikke; ny draft med collision-safe slug oprettes.

Historisk vN kan restores komplet ved at bruge `FullBackupFile` fra den næste save, fordi denne backup er taget umiddelbart før vN+1 og derfor indeholder WordPress-post + central Page Editor-state for vN. Hvis komplet editor-state ikke kan bevises, låses destruktiv restore og kopi-mode er fallback.

## WHATIF-CLEANUP-001 — auditstatus

Den aktive legacy `hangar18-manager.php` har fortsat mange WhatIf-referencer. Første source-scan fandt mindst **48** lowercase `whatif`-matches i den store legacy-fil alene, fordelt på både UI og backend branches.

Bekræftede aktive områder inkluderer bl.a.:

- Vehicle layout/save/register/fields;
- Event layout/save/register;
- Gallery layout/save/rebuild;
- Page Editor save/version UI;
- ældre sideindhold;
- Menu create/save/add/repair;
- Header/Footer design og shell sync;
- status-/hjælpetekster og logbeskrivelser.

Nuværende shim findes fortsat som:

- `src/Admin/NoWhatIfAdminController.php`;
- `assets/hangar18-no-whatif-v0858.js`;
- `assets/hangar18-no-whatif-v0858.css`.

Cleanup-regel: fjern backend/UI-koden ved kilden først. Shim/controller/assets slettes først, når normal save/rebuild/menu/design-flow er verificeret uden WhatIf-input eller branches.

## Næste arbejdsrækkefølge

1. Fortsæt WHATIF-CLEANUP-001 source-audit og planlæg sikre source-fjernelsesbatches.
2. LEGACY-POWERSHELL-CLEANUP-001 read-only audit.
3. Fortsæt LEGO-produktroadmap: Navigator/lagtræ + alternativ `Flyt til Kasse` er næste anbefalede feature.
4. Genoptag frosne LEGO-runtimebugs kun fra TRACE-076 evidence.
5. I9/I10 senere.

## Beskyttede områder

Vehicle/Event/Gallery-funktionalitet må ikke ændres semantisk af cleanup. Backup, updater SHA, code backup, rollback og public cutover-lock bevares.
