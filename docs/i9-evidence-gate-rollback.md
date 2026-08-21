# I9 Evidence Gate — Rollback Rehearsal

**Gate key:** `rollback`  
**Initial status:** `PENDING`

## Build / environment

- Commit SHA:
- Plugin version:
- Target URL / staging copy:
- WordPress / PHP:
- Tested at (ISO-8601):
- Tester:
- Backup/restore-point ID:

## Baseline

- [ ] Record baseline page/content identity before the rehearsal.
- [ ] Record relevant design/layout/span state.
- [ ] Record protected-domain baseline references where relevant.
- [ ] Confirm the chosen restore point exists and is readable.

## Rehearsal

- [ ] Apply a controlled, reversible change on the designated staging/test object only.
- [ ] Verify the controlled change is observable.
- [ ] Execute the documented restore path for that test object/site scope.
- [ ] Verify original content/data is restored.
- [ ] Verify layout/design/responsive state is restored.
- [ ] Verify no unrelated object was altered by restore.
- [ ] Verify Vehicle/Event/Gallery remain intact.
- [ ] Record restore logs/audit identifiers and elapsed time.

## Post-restore comparison

- Baseline hash/reference:
- Restored hash/reference:
- Content comparison:
- Layout comparison:
- Protected-domain comparison:

## Result

- Expected:
- Actual:
- Restore/audit errors:
- Deviations/issues:

## Evidence references

- Evidence 1:
- Evidence 2:
- Evidence 3:

## Decision — choose only after rehearsal

- [ ] `PASS`
- [ ] `FAIL`
- [ ] `BLOCKED`

Notes:

> This is a staging/live-copy rehearsal only. It must not be used as justification for public cutover before the complete I9 gate is accepted.