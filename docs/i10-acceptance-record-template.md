# I10 acceptance record — template

Denne skabelon spejler felterne i `ConversionAcceptanceValidator`. Den er kun dokumentation/evidence; den må ikke bruges til at omgå den rigtige validator.

## Identitet

| Felt | Værdi |
|---|---|
| Slug | |
| Page ID | |
| Permalink | |
| SourceHash | |
| Git commit | |
| Pluginversion | |
| Environment | |
| EvidenceRef | |
| Tester/UserId | |
| Captured UTC | |

## Required checks

- [ ] `desktop-compare`
- [ ] `tablet-compare`
- [ ] `mobile-compare`
- [ ] `save-flow`
- [ ] `preview-flow`
- [ ] `revision-flow`
- [ ] `rollback-flow`

## Manual confirmation

- `ConfirmedManual`: ⬜ true / false
- `AcceptedForSequence`: **må kun være afledt af validatoren**

## Notes


## Source-hash regel

Acceptance er kun gyldig, når den gemte `SourceHash` matcher den aktuelle shadow source hash. Ved source drift skal acceptance gentages mod den nye source.

## Før næste stage

- [ ] alle required checks er PASS;
- [ ] manual confirmation er udført;
- [ ] Environment er udfyldt;
- [ ] EvidenceRef er udfyldt;
- [ ] source hash matcher;
- [ ] preflight har ingen blockers;
- [ ] preflight er fortsat `Executable=false` / `PublicMutationAvailable=false` i den nuværende planfase;
- [ ] stage-rækkefølgen er korrekt.
