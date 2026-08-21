# Hangar18 Manager — aktiv backlog v0.8.40

**Statusdato:** 21. august 2026  
**Aktuel officiel pluginbaseline:** **v0.8.40**  
**Officiel release package commit:** `b35b3809500f7de90ab7a3df0249fd84194edb51`  
**Package SHA-256:** `1497d3f0bd784aa10dcb8b14ee91a74b21fda99c78071ddedb2dcf0f2b988a66`  
**Aktiv test:** GitHub issue **#131 — LEGO v0.8.40 manual acceptance — test2 A–L**

Denne fil er den korte aktive styringsbacklog efter den historiske `integration-backlog-after-ud120.md`. Den historiske fil bevares som detaljeret arkitektur-/implementeringslog.

## Aktuel status

| Område | Status | Næste handling |
|---|---|---|
| LEGO-editor runtime | ✅ Implementeret og automatisk QA PASS | Manuel A–L test på `test2`. |
| Officiel v0.8.40 release | ✅ Bygget og checksum-verificeret | Installer samme ZIP på `test2`. |
| LEGO manual acceptance | 🟡 PRE-FLIGHT PENDING | Bekræft v0.8.40 + rollback-point og gennemfør A–L i issue #131. |
| I9 manual/live evidence | 🟡 PENDING | LEGO-test + brand browsers + screen reader + protected domains + rollback. |
| I10 controlled conversion | 🔒 LÅST | Må først fortsætte efter fuldt I9 PASS. |
| Public page conversion | 🔒 LÅST | Ingen public mutation/cutover endnu. |

## LEGO backlog

| ID | Status | Leverance |
|---|---|---|
| LEGO-031 | ✅ QA PASS | Automatic side-by-side via eksisterende Auto-kasser/LayoutParentKey-motor. |
| LEGO-032 | ✅ QA PASS | 12-kolonne Desktop resize med atomic Undo/Redo. |
| LEGO-033 | ✅ QA PASS | Reversible Tablet/Mobil span overrides med Arv Desktop. |
| LEGO-034 | ✅ Implementeret / manual PASS pending | A–L manual acceptance pack. |
| LEGO-035 | ✅ Implementeret | Dispatch-only staging test build. |
| LEGO-036 | ✅ Implementeret | Install/rollback runbook. |
| LEGO-037 | ✅ Implementeret | Staging artifact verifier. |
| LEGO-038 | ✅ Implementeret | Maskinlæsbar A–L acceptance schema + validator. |
| LEGO-039 | ✅ Implementeret | Acceptance bootstrap fra staging-manifest. |
| LEGO-040 | ✅ Implementeret / QA PASS | Read-only scenario/critical-flag recorder. |
| LEGO-041 | ✅ Implementeret / QA PASS | Official-release acceptance bootstrap fra `update.json` + ZIP. |
| LEGO-042 | ✅ Implementeret / QA PASS | Canonical v0.8.40 PENDING acceptance record. |
| LEGO-043 | ✅ QA PASS | JSON/Markdown acceptance report + sikker I9 `test2LiveE2E` evidence-handoff readiness; autoriserer aldrig I9 PASS/cutover. |
| LEGO-044 | 🟡 MANUAL PENDING | Installer/bekræft officiel v0.8.40 på `test2`, etabler rollback-point og gennemfør A–L med evidence. |

## LEGO-044 — manual v0.8.40 acceptance

Canonical record: `docs/lego-v0840-manual-acceptance.json`.
Aktiv tracking: GitHub issue #131.

### Preflight

- [ ] Bekræft at **Hangar18 Manager 0.8.40** er installeret og aktiv på `test2`.
- [ ] Bekræft at kandidaten er den officielle v0.8.40-pakke med SHA-256 ovenfor.
- [ ] Tag/identificér rollback-point før første gem/write-test.
- [ ] Registrér browser, OS samt Desktop/Tablet/Mobil viewports.
- [ ] Bekræft at testen foregår på `test2` og ikke er public cutover.

### A–L

- [ ] A — Elementbibliotek og drop
- [ ] B — Kasse og nesting
- [ ] C — Side-by-side
- [ ] D — Desktop resize
- [ ] E — Tablet/Mobil overrides + Arv Desktop
- [ ] F — Design og spacing
- [ ] G — Foldbare paneler
- [ ] H — Undo/Redo
- [ ] I — Save/reload persistence
- [ ] J — Preview Desktop/Tablet/Mobil
- [ ] K — Backup/restore
- [ ] L — Vehicle/Event/Gallery regression

Et scenarie må kun blive PASS med konkret evidence. Kritisk console/PHP-fejl, datatab/dubletter eller regression i protected domains tvinger FAIL.

Efter testen bruges `tools/lego-acceptance-report.cjs`. `readyForI9Test2EvidenceHandoff=true` betyder kun, at A–L-resultatet kan vedlægges I9 `test2LiveE2E`; det betyder ikke samlet I9 PASS.

## I9 — stadig krævet efter LEGO A–L

1. Chrome brand test.
2. Edge brand test.
3. Firefox brand test.
4. Safari brand test.
5. Screen-reader core flow.
6. Authenticated `test2` editor/live E2E.
7. Vehicle/Event/Gallery visual/function regression.
8. Migration/rollback rehearsal på live kopi.

LEGO A–L PASS kan levere evidence til I9, men kan **ikke** alene sætte I9 til PASS.

## I10 / public cutover

Fortsat fastlåst rækkefølge efter fuldt I9 PASS:

1. comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery kun efter særskilt compatibility proof;
7. legacy removal til sidst.

Ingen værktøjer i LEGO-038..043 må autorisere cutover eller public mutation.