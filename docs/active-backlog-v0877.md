# Hangar18 Manager — aktiv backlog v0.8.77

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.77**  
**Release commit:** `b7c87d2491a6bc7545fd89ba5936908afe9239a1`  
**Package SHA-256:** `9df4c82bb2932d40c4025b22522bdc458d7568fa65161538469131495139fc1f`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. `active-backlog-v0876.md` og ældre filer er historiske snapshots.

## Status

| ID | Prioritet | Status | Næste handling |
|---|---|---|---|
| TRACE-076 | Kritisk | 🟡 MANUEL TEST | Smoke-test master TIL/FRA på Opdateringer og Start/Stop/Markér/TXT/JSON i Designeren. |
| UPDATER-VERSION-002 | Kritisk | 🟡 FIX-KANDIDAT v0.8.77 | Test at automatisk/page-load check viser samme latest-version som JA/NEJ beregnes fra. |
| UPDATER-STATUS-001 | Kritisk | 🟡 FIX-KANDIDAT v0.8.77 | Test installeret==latest → NEJ umiddelbart efter update/refresh. |
| PAGE-VERSION-RESTORE-001 | Høj | 🟠 IMPLEMENTERING | Byg versionsliste + preview/sammenligning + eksplicit Restore-mode: Erstat original eller Restore som kopi. |
| WHATIF-CLEANUP-001 | Høj | 🔴 ÅBEN | Fjern WhatIf ved kilden og derefter no-whatif shim/assets/controller. |
| LEGACY-POWERSHELL-CLEANUP-001 | Høj | 🔴 ÅBEN | Read-only audit af installeret site/uploads/legacy artifacts; backup før deletion. |
| LEGO-SELECTION-075 | Kritisk | ⏸ FROSSET / TRACE | Genoptages kun med konkret TRACE-076 reproduktion. |
| LEGO-INSIDE-075 | Kritisk | ⏸ FROSSET / TRACE | Genoptages kun med konkret TRACE-076 reproduktion. |
| LEGO-REPAINT-062 | Høj | ⏸ FROSSET / TRACE | Genoptages kun med konkret TRACE-076 reproduktion. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Efter kritiske editor/updater-fejl. |
| I10-CUTOVER | Normal | 🔒 LÅST | Først efter fuldt I9 PASS og særskilt godkendelse. |

## v0.8.77 — updater state-kontrakt

Et nyt admin-only `UpdaterStateConsistencyAdminController` normaliserer updater-state efter legacy auto-check og før `render_updates()`.

På Opdateringer hentes `update.json` frisk og følgende værdier skrives som ét snapshot:

- `checked_at_utc`
- `current_version`
- `manifest.version`
- `update_available`
- `compatible_wp`
- `compatible_php`
- `error`

`update_available` beregnes altid fra præcis de versioner, som vises. Ved GitHub-fejl beholdes senest kendte manifest, men availability genberegnes mod aktiv pluginversion. Legacy updater ejer fortsat installation, safety backup, package SHA, code backup og rollback.

## PAGE-VERSION-RESTORE-001 — autoritativt restore-flow

Versionshistorikken genbruger `hangar18_manager_page_versions_v1` og de eksisterende JSON-sidebackups/B1 restore-tjenester. Der oprettes ikke en parallel versionsdatabase.

### UI

For hver historisk version skal brugeren kunne:

1. se version, tidspunkt, bruger og ændringsnote;
2. preview/sammenligne versionen mod aktuel side uden write;
3. vælge **Restore**;
4. derefter eksplicit vælge én af to modes:
   - **Erstat original**;
   - **Restore som kopi**.

Der må ikke være en skjult/default destruktiv restore-mode.

### Erstat original

- Capability + nonce + preflight.
- Tag safety-version/backup af den aktuelle original før første write.
- Bevar original side-ID og slug/URL.
- Restore WordPress-indhold + relevant Page Editor state fra den valgte historiske version.
- Verificer canonical store og render efter restore.
- Safety-versionen skal kunne bruges som undo/restore tilbage.

### Restore som kopi

- Original side og URL røres ikke.
- Opret ny WordPress-side som **draft**.
- Collision-safe titel og slug, fx `Om foreningen - kopi`.
- Rebind Page Editor content/state til kopiens slug.
- Kopien må ikke automatisk indsættes i menuen eller gøres public.

### Sikkerhed

Vehicle/Event/Gallery påvirkes ikke. Restore skal bygge oven på eksisterende B1 `ManagedPageBackupRestoreService`, som allerede understøtter `restoreOriginal()` med safety backup og `createCopy()` som draft-kopi.

## Næste arbejdsrækkefølge

1. PAGE-VERSION-RESTORE-001 implementering.
2. WHATIF-CLEANUP-001 source audit + cleanup.
3. LEGACY-POWERSHELL-CLEANUP-001 read-only audit.
4. Fortsæt LEGO-produktroadmap uden at genåbne de tre frosne runtimebugs, medmindre TRACE-076 giver konkret reproduktion.
5. I9 evidence og senere kontrolleret I10.

## Beskyttede områder

- Vehicle/Event/Gallery må ikke ændres af disse fixes.
- Backup, package SHA-verifikation, updater code backup og automatisk rollback bevares.
- Public cutover er fortsat ikke autoriseret.
