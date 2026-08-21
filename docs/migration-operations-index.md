# Ultimate Designer — migration operations index

Denne side er indgangen til den operative dokumentation efter LEGO-033. Den ændrer ingen public state.

## Daglig editorbrug

- `ultimate-designer-user-manual.md` — fuld visuel brugermanual.
- `ultimate-designer-quick-reference.md` — kort daglig reference.
- `DESIGN-MANUAL.md` i repo-roden — autoritativ visuel designkontrakt.

## I9 — manual/live acceptance

I9 er den aktuelle aktive gate før public cutover.

Læs/kør i denne rækkefølge:

1. `i9-manual-qa-evidence-runbook.md`
   - samlet evidence-struktur og PASS/FAIL/BLOCKED-regler.
2. `i9-test2-live-e2e-checklist.md`
   - rigtig staging-/WordPress-E2E.
3. `i9-rollback-rehearsal.md`
   - baseline → kandidat → restore → verifikation.
4. `i9-evidence-result-template.md`
   - menneskeligt resultatark.
5. `i9-evidence-manifest.schema.json`
   - maskinlæsbar evidence-kontrakt.
6. `i9-evidence-manifest.example.json`
   - PENDING-startskabelon.
7. `.github/workflows/i9-test2-live-readonly.yml`
   - read-only public smoke; støttebevis, ikke erstatning for manuelle gates.

I9 må først sættes PASS, når Chrome, Edge, Firefox, Safari, screen reader, test2 live E2E, protected domains og rollback alle er PASS.

## I10 — controlled conversion preparation

I10 er **låst**, indtil I9 er samlet PASS.

Dokumenter:

- `i10-operator-runbook.md` — fast operatorsekvens og stopregler.
- `i10-blocker-reference.md` — blocker → betydning → handling.
- `i10-acceptance-record-template.md` — human acceptance-felter/checks.
- `i10-stage-ledger-template.md` — sequence/hash/evidence-ledger pr. stage.

Kodekontrakt:

- `ConversionPlanService` — plan-only.
- `ConversionReadinessGate` — blocker/eligibility decision-only.
- `ConversionAcceptanceValidator` — human evidence + source hash.
- `ConversionCutoverPreflightService` — preflight-only, ikke eksekverbar.

## Fast stage-rækkefølge

```text
I9 PASS
  ↓
comparison/testside
  ↓
Hjem
  ↓
Om foreningen
  ↓
Kontakt
  ↓
Bliv medlem
  ↓
Vehicle/Event/Gallery kun efter særskilt compatibility proof
  ↓
legacy removal sidst
```

## QA-kontrakter

- `tests/Architecture/i9-live-readonly-contract.sh`
  - read-only public test, routes, evidence-manifest og manual/live-distinktion.
- `tests/Architecture/i10-operator-runbook-contract.sh`
  - runbooks skal følge runtime-rækkefølge/checklist/non-executable policy.
- `tests/Architecture/assert-foundation-isolation.sh`
  - dokumentations/prep-scope må ikke lække til legacy/public runtime.

## Stopregel

Hvis næste handling kræver at en eksisterende public side faktisk skifter renderer eller at WordPress-data muteres som del af cutover, er man nået forbi prep-fasen. På det punkt kræves I9 PASS og den senere eksplicit kontrollerede I10-mekanisme; plan/preflight-dokumentationen må ikke bruges som genvej.
