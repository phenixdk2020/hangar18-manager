# I9 Evidence Gate — test2 Live E2E

**Gate key:** `test2LiveE2E`  
**Initial status:** `PENDING`

## Build / environment

- Commit SHA:
- Plugin version:
- Target URL:
- WordPress / PHP:
- Tested at (ISO-8601):
- Tester:
- Browser / OS:
- Backup/restore-point ID:

## Mandatory authenticated editor flow

- [ ] Build/version/target match the canonical I9 manifest.
- [ ] Confirm backup/restore point before any saved staging edit.
- [ ] Log in to the intended staging/test2 WordPress environment only.
- [ ] Open an ordinary comparison/editor test page; do not convert a production page.
- [ ] Add/edit representative Text and Image elements.
- [ ] Exercise Over / Under / Into / Left / Right placement.
- [ ] Exercise Auto-kasser and Desktop resize.
- [ ] Exercise Tablet/Mobile override and `Arv Desktop`.
- [ ] Exercise Undo/Redo around the above actions.
- [ ] Save only the designated staging/test page and verify reload persistence.
- [ ] Verify public/preview result for the designated test page.
- [ ] Verify unrelated existing pages remain unchanged.
- [ ] Record any backup/version entry created by the save path.

## Safety boundary

- [ ] No Hjem/Om/Kontakt/Bliv medlem public conversion performed.
- [ ] No Vehicle/Event/Gallery migration performed.
- [ ] No I10 cutover/mutation enabled.

## Result

- Expected:
- Actual:
- Runtime/console/server errors:
- Persistence/reload result:
- Deviations/issues:

## Evidence references

- Evidence 1:
- Evidence 2:
- Evidence 3:

## Decision — choose only after testing

- [ ] `PASS`
- [ ] `FAIL`
- [ ] `BLOCKED`

Notes:

> The existing public read-only smoke is supporting evidence only. This gate requires a real authenticated staging editor session.