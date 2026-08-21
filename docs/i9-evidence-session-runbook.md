# I9 Manual Evidence Session Runbook

Denne runbook er den operative rækkefølge for én I9-testsession. Den **udfører ikke** tests og ændrer ikke WordPress/cutover-state.

## 0. Session identity

Registrer før første gate:

- Commit SHA:
- Plugin version:
- Staging target: `https://test2.hangar18.dk/`
- WordPress version:
- PHP version:
- Tester:
- Session start (ISO-8601):
- Backup/restore-point ID:

### Preflight

- [ ] Commit SHA er den build der faktisk er deployet/testet.
- [ ] Pluginversion matcher `Hangar18_Manager::VERSION`.
- [ ] Target er staging/test2 — ikke den offentlige produktionsside.
- [ ] Restore point er tilgængeligt før authenticated save/rollback tests.
- [ ] I10 er fortsat non-executable / public mutation locked.

## 1. Seed manifest

Opret kun et nyt manifest til den konkrete build. Alle gates starter `PENDING`.

```bash
node tools/i9-evidence-init.cjs \
  --sha <40-char-sha> \
  --version <plugin-version> \
  --wordpress-version <wp-version> \
  --php-version <php-version> \
  --tester "<tester>" \
  --backup-restore-point <restore-point-id> \
  --target https://test2.hangar18.dk/ \
  --output evidence/i9/manifest.json
```

Valider straks:

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json \
  --expected-sha <40-char-sha> \
  --expected-version <plugin-version> \
  --expected-target https://test2.hangar18.dk/
```

## 2. Gate order

Brug operator-indexet: `docs/i9-evidence-gate-index.md`.

Anbefalet rækkefølge:

1. `chrome` — `docs/i9-evidence-gate-chrome.md`
2. `edge` — `docs/i9-evidence-gate-edge.md`
3. `firefox` — `docs/i9-evidence-gate-firefox.md`
4. `safari` — `docs/i9-evidence-gate-safari.md`
5. `screenReader` — `docs/i9-evidence-gate-screen-reader.md`
6. `test2LiveE2E` — `docs/i9-evidence-gate-test2-live-e2e.md`
7. `protectedDomains` — `docs/i9-evidence-gate-protected-domains.md`
8. `rollback` — `docs/i9-evidence-gate-rollback.md`

En browsergate må godt være FAIL/BLOCKED, men den må ikke springes over og efterfølgende antages PASS.

## 3. Efter hver gate

Gem først det faktiske evidence (screenshot/log/video/notes). Transformer derefter manifestet til en **ny fil**; recorderen ændrer ikke kilden.

```bash
node tools/i9-evidence-record.cjs evidence/i9/manifest.json \
  --gate <gate-key> \
  --status <PASS|FAIL|BLOCKED|PENDING> \
  --evidence <evidence-reference> \
  --browser-or-tool "<tool/version>" \
  --notes "<kort resultat>" \
  > evidence/i9/manifest.next.json
```

Valider `manifest.next.json` mod samme SHA/version/target. Er den korrekt, kan operatøren eksplicit gøre den til den nye working copy.

### Stopregel ved FAIL

- Registrer `FAIL` med evidence.
- Opret/henvis til defect.
- Ret og deploy en ny build.
- Start en **ny build-bound evidence session**; gamle PASS-resultater må ikke automatisk genbruges mod en ny SHA.

### Stopregel ved BLOCKED

- Registrer blocker og konkret årsag.
- Bevar `BLOCKED`; omdøb ikke til PASS.
- Genoptag først gaten, når blokeringen er fjernet.

## 4. Periodisk integrity/readiness

Efter flere gates eller før sessionen afsluttes:

```bash
node tools/i9-evidence-integrity.cjs evidence/i9/manifest.json \
  --root . \
  --expected-sha <40-char-sha> \
  --expected-version <plugin-version> \
  --expected-target https://test2.hangar18.dk/
```

```bash
node tools/i9-evidence-readiness.cjs evidence/i9/manifest.json \
  --expected-sha <40-char-sha> \
  --expected-version <plugin-version> \
  --expected-target https://test2.hangar18.dk/ \
  --markdown
```

Følg `nextAction` for de resterende gates. `readyForI10=false` er forventet, indtil alle otte reelle gates er PASS.

## 5. Final evidence gate

Før I9 kan foreslås accepteret:

- [ ] Alle otte gates er manuelt/live udført.
- [ ] Alle otte står `PASS` i manifestet.
- [ ] Hver PASS har mindst én reel evidence-reference.
- [ ] Build SHA/version/target matcher sessionen.
- [ ] Integrity-rapport har ingen uløste lokale refs.
- [ ] Rollback-rehearsal er faktisk gennemført.

Kør derefter:

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json \
  --expected-sha <40-char-sha> \
  --expected-version <plugin-version> \
  --expected-target https://test2.hangar18.dk/ \
  --require-pass
```

og readiness:

```bash
node tools/i9-evidence-readiness.cjs evidence/i9/manifest.json \
  --expected-sha <40-char-sha> \
  --expected-version <plugin-version> \
  --expected-target https://test2.hangar18.dk/
```

`readyForI10=true` er stadig kun et dokumenteret readiness-resultat. Det **aktiverer ikke** I10 eller public mutation.

## 6. Session close / handoff

Registrer:

- Session end (ISO-8601):
- Final derived I9 status:
- Completed gates:
- Failed/blocked/pending gates:
- Validation report reference:
- Integrity report reference:
- Readiness report reference:
- Defect/issue references:
- Næste handling:

Hvis status ikke er PASS, er næste handling at løse den konkrete gate — ikke at starte page conversion.