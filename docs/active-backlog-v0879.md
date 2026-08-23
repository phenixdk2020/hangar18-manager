# Hangar18 Manager — canonical backlog delta v0.8.79

**Statusdato:** 23. august 2026  
**Baseline:** v0.8.79 release-kandidat  
**Extends:** `docs/active-backlog-v0878.md`

Denne fil er den aktuelle canonical backlog. Den arver hele master-roadmapet fra v0.8.78 og overskriver kun punkter, som er ændret i v0.8.79-batchen. `tools/backlog-governance.py` merger hele kæden til `docs/backlog-index.json` ved release.

## Batchstatus

Brugeren bad om ca. 20 backlogopgaver i én arbejdsgang. Denne batch implementerer **22 konkrete backlogpunkter** uden at ændre de frosne LEGO selection/drop/repaint-semantics.

# A. Backlog-governance, release og sporbarhed

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| BACKLOG-MAINT-002 | Høj | 🟡 DELVIST | Layered backlog + validator håndhæver unikke ID’er, prioritet, status og DoD. Eksplicit dependency-felt kan tilføjes i næste schema-revision. |
| BACKLOG-MAINT-004 | Normal | ✅ FÆRDIG v0.8.79 | Release-workflow genererer `docs/backlog-index.json` fra hele `Extends`-kæden med ID/status/område/source file. |
| BACKLOG-MAINT-005 | Normal | ✅ FÆRDIG v0.8.79 | `backlog-release-governance-qa.yml` validerer merged backlog og fejler på dubletter/manglende felter. |
| BACKLOG-MAINT-006 | Normal | ✅ FÆRDIG v0.8.79 | `release-config.json`, readme, update.json og release-manifest bindes til releaseens `backlog_ids`. |
| BACKLOG-MAINT-007 | Normal | ✅ FÆRDIG v0.8.79 | `docs/BACKLOG-CONTRIBUTING.md` dokumenterer commit-konvention med backlog-ID’er. |
| RELEASE-002 | Høj | ✅ FÆRDIG v0.8.79 | `tools/release-integrity.py` verificerer release-config/update.json/ZIP plugin header/VERSION konstant som samme version. |
| RELEASE-003 | Høj | ✅ FÆRDIG v0.8.79 | ZIP tree policy afviser dev/test/tools/docs/PowerShell/log/tmp/bak og kendte VehicleRegister bootstrap-artifacts. |
| RELEASE-004 | Normal | ✅ FÆRDIG v0.8.79 | Workflow skriver `release-manifest.json` med source commit, build UTC, package SHA, backlog-ID’er, channel og QA-summary. |
| RELEASE-005 | Normal | ✅ FÆRDIG v0.8.79 | Release metadata har eksplicit `channel=test|staging|production`; update.json og release-manifest viderefører channel. |

# B. Trace, diagnostik og fejlfindingsplatform

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| TRACE-077 | Høj | 🟡 MANUEL TEST v0.8.79 | Designer viser permanent statusbadge `TRACE OPTAGER` / `TRACE STOPPET`, når trace master er aktiv. |
| TRACE-078 | Høj | 🟡 MANUEL TEST v0.8.79 | Efter hver TEST_START logges SESSION_METADATA med pluginversion, browser, viewport, admin-page, page slug, timezone og redaction self-test. |
| TRACE-084 | Normal | 🟡 MANUEL TEST v0.8.79 | Trace support-panelet filtrerer All/Selection/Drag/Layout/Inspector/Save/Error/Network. |
| TRACE-085 | Normal | 🟡 MANUEL TEST v0.8.79 | Trace support-panelet har fritekstsøgning i key/event/detail. |
| TRACE-086 | Normal | 🟡 MANUEL TEST v0.8.79 | `Kopiér bundle` / `Download bundle` samler trace, runtime-versioner og ikke-sensitiv state summary. |
| TRACE-087 | Normal | 🟡 MANUEL TEST v0.8.79 | UI viser eventantal og tydelig advarsel ved 2000/2200 før base-tracens ringbuffer roterer gamle events ud. |
| TRACE-088 | Normal | 🟡 MANUEL TEST v0.8.79 | `error` og `unhandledrejection` registreres som `CRITICAL_JS_ERROR` / `CRITICAL_PROMISE_REJECTION`, også når tung trace er stoppet. |
| TRACE-089 | Normal | ✅ AUTOMATISK QA v0.8.79 | Support bundle har rekursiv redaction inkl. password/token/nonce/cookie/session/authorization; runtime self-test + `tools/trace-redaction-qa.py` er koblet i CI. |

# C. GitHub updater

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| UPDATER-004 | Høj | 🟡 MANUEL TEST v0.8.79 | Statuskort viser checked_at og klassificerer state FRESH når succesfuldt check er <=30 min, ellers STALE/FEJL. |
| UPDATER-005 | Høj | 🟡 MANUEL TEST v0.8.79 | GitHub/netværksfejl vises tydeligt uden at ændre den atomiske JA/NEJ-kontrakt. |
| UPDATER-011 | Normal | 🟡 MANUEL TEST v0.8.79 | Ét samlet statuskort viser installed/latest/update/freshness/check/published/WP/PHP/package SHA. |
| UPDATER-012 | Normal | 🟡 MANUEL TEST v0.8.79 | Install-submit knapper disables klient-side når `update_available` er false; legacy handler er fortsat server-side owner. |
| UPDATER-013 | Normal | 🟡 MANUEL TEST v0.8.79 | Seneste manifests changelog vises direkte i det nye statuskort. |
| UPDATER-014 | Normal | 🟡 MANUEL TEST v0.8.79 | `Kopiér updater diagnose` kopierer read-only version/state/compatibility/SHA/error snapshot uden token/credentials. |

# Næste batch efter v0.8.79

1. Smoke-test v0.8.79 Trace + Updater support UI.
2. Fortsæt `WHATIF-CLEANUP-001` med source-removal i sikre batches.
3. `LEGACY-POWERSHELL-CLEANUP-001` + ZIP/runtime audit.
4. Start `LEGO-NAV-001` + `LEGO-MOVE-001` uden at genåbne frosne drag/drop-bugs.
5. Fortsæt 20-punkts batches og opdater denne canonical backlog-kæde ved hver batch.
