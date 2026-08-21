# I10 stage ledger — template

Brug én kopi af denne ledger for en kandidatsekvens. Den dokumenterer rækkefølge og hash/evidence pr. stage; den udfører ingen cutover.

## Kandidatbuild

| Felt | Værdi |
|---|---|
| Git commit | |
| Pluginversion | |
| I9 evidence manifest | |
| I9 samlet status | ⬜ PASS / FAIL / BLOCKED / PENDING |
| Test-/conversionmiljø | |
| Overordnet backup ID | |

## Stage-sekvens

| Stage | Kind | Slug | Page ID | Legacy hash | Shadow SourceHash | Acceptance SourceHash | Acceptance | Preflight blockers | Eligible | EvidenceRef |
|---:|---|---|---:|---|---|---|---|---|---|---|
| 1 | comparison | | | | | | ⬜ | | ⬜ | |
| 2 | core | `hjem` | | | | | ⬜ | | ⬜ | |
| 3 | core | `om-foreningen` | | | | | ⬜ | | ⬜ | |
| 4 | core | `kontakt` | | | | | ⬜ | | ⬜ | |
| 5 | core | `bliv-medlem` | | | | | ⬜ | | ⬜ | |
| 6+ | protected | kun efter særskilt proof | | | | | ⬜ | | ⬜ | |

## Stage-detail

Kopiér denne blok pr. faktisk stage.

### Stage N — `<slug>`

**Identitet**

- Kind:
- Page ID:
- Permalink:
- Environment:
- Git commit:
- Pluginversion:

**Hashes**

- Current legacy hash:
- Shadow SourceHash:
- Acceptance SourceHash:
- Source drift free: ⬜ ja / nej

**Human acceptance**

- [ ] desktop-compare
- [ ] tablet-compare
- [ ] mobile-compare
- [ ] save-flow
- [ ] preview-flow
- [ ] revision-flow
- [ ] rollback-flow
- ConfirmedManual: ⬜ true / false
- Environment recorded: ⬜
- EvidenceRef recorded: ⬜
- AcceptedForSequence (validator-derived): ⬜ true / false

**Preflight**

- Mode: `cutover-preflight-only`
- Executable: `false`
- PublicMutationAvailable: `false`
- EligibleForFutureCutover: ⬜ true / false
- Blockers:
  -

**Evidence**

- Desktop comparison:
- Tablet comparison:
- Mobil comparison:
- Save/preview/revision:
- Rollback:
- Additional notes:

**Sequence check**

- [ ] comparison accepted first, hvis dette er core;
- [ ] alle prior core stages accepteret;
- [ ] protected-domain policy respekteret;
- [ ] source hash er stadig current umiddelbart før næste stage.

## Drift-log

Registrér enhver ændring af legacy source efter shadow/acceptance.

| Tid | Slug | Tidligere hash | Ny hash | Konsekvens | Ny acceptance krævet? |
|---|---|---|---|---|---|
| | | | | | |

## Stop-log

| Tid | Stage | Blocker/årsag | Handling | Genoptaget? |
|---|---|---|---|---|
| | | | | |

## Slutstatus

- Comparison: ⬜ accepteret
- Hjem: ⬜ accepteret
- Om: ⬜ accepteret
- Kontakt: ⬜ accepteret
- Bliv medlem: ⬜ accepteret
- Protected domains: ⬜ ikke påbegyndt / særskilt proof
- Legacy removal: ⬜ ikke påbegyndt

Denne ledger er ikke i sig selv tilladelse til public mutation. Den dokumenterer readiness og acceptance omkring den eksisterende plan/preflight-only arkitektur.
