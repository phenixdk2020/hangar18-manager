# I9 evidence result — template

Kopiér denne fil til den konkrete evidence-pakke og udfyld alle obligatoriske felter.

## Build-identitet

| Felt | Værdi |
|---|---|
| Dato/tid | |
| Tester | |
| Git commit SHA | |
| Pluginversion | |
| WordPress-version | |
| PHP-version | |
| Testmiljø | |
| Backup/restore-point ID | |

## Browserresultater

| Gate | Browser/OS/version | Resultat | Evidence |
|---|---|---|---|
| Chrome brand | | ⬜ PASS / FAIL / BLOCKED | |
| Edge brand | | ⬜ PASS / FAIL / BLOCKED | |
| Firefox brand | | ⬜ PASS / FAIL / BLOCKED | |
| Safari brand | | ⬜ PASS / FAIL / BLOCKED | |

## Screen reader

| Felt | Værdi |
|---|---|
| Screen reader | |
| OS | |
| Browser | |
| Resultat | ⬜ PASS / FAIL / BLOCKED |
| Evidence/noter | |

## test2 live E2E

- Resultat: ⬜ PASS / FAIL / BLOCKED
- Comparison-side ID/URL:
- Permanent version/revision:
- Public read-only Actions-run:
- Screenshot/evidence-mappe:
- Noter:

## Protected domains

| Domæne | Oversigt | Detalje | Specialeditor | Desktop/Mobil | Resultat |
|---|---|---|---|---|---|
| Vehicle | ⬜ | ⬜ | ⬜ | ⬜ | |
| Event | ⬜ | ⬜ | ⬜ | ⬜ | |
| Gallery | ⬜ | ⬜ | ⬜ | ⬜ | |

## Rollback rehearsal

- Resultat: ⬜ PASS / FAIL / BLOCKED
- Baseline version/state:
- Kandidat version/state:
- Restore handling:
- Restore timestamp:
- Baseline screenshot:
- Kandidat screenshot:
- Restored screenshot:
- Audit/revision bevis:
- Noter:

## Afvigelser

| ID | Severity | Gate | Beskrivelse | Reproduktion | Status |
|---|---|---|---|---|---|
| | | | | | |

## Samlet gate

I9 må kun sættes til PASS, når alle obligatoriske gates er PASS.

- [ ] Chrome PASS
- [ ] Edge PASS
- [ ] Firefox PASS
- [ ] Safari PASS
- [ ] Screen reader PASS
- [ ] test2 live E2E PASS
- [ ] Vehicle/Event/Gallery PASS
- [ ] Rollback PASS

**Samlet I9-resultat:** ⬜ PASS / FAIL / BLOCKED

**Godkendelsesnotat:**
