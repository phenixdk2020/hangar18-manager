# I10 — controlled conversion operator runbook

**Status:** Forberedelse komplet / cutover låst bag I9  
**Dato:** 21. august 2026

Denne runbook beskriver den **senere** kontrollerede I10-sekvens. Den giver ikke tilladelse til public cutover og ændrer ikke den implementerede lås: I10 må først begynde, når I9's obligatoriske manuelle/live evidence er samlet PASS.

Den eksisterende kode er bevidst plan/preflight-only:

- `ConversionPlanService` returnerer `Mode=plan-only` og `PublicMutationAvailable=false`.
- `ConversionCutoverPreflightService` returnerer `Mode=cutover-preflight-only`, `Executable=false` og `PublicMutationAvailable=false`.
- `ConversionReadinessGate` kan kun afgøre fremtidig eligibility; den udfører ingen writes.

---

## 1. Fast conversion-rækkefølge

I10-rækkefølgen må ikke ændres ad hoc:

1. sikker comparison-/testside;
2. `hjem`;
3. `om-foreningen`;
4. `kontakt`;
5. `bliv-medlem`;
6. protected domains kun efter særskilt compatibility proof;
7. legacy removal allersidst.

Protected domains omfatter fortsat Vehicle, Event og Gallery og er yderligere blokeret af legacy-runtime-policy, så længe denne policy er aktiv.

---

## 2. Gate 0 — I9 skal være PASS

Før nogen I10-acceptance eller senere cutover:

- [ ] Chrome PASS;
- [ ] Edge PASS;
- [ ] Firefox PASS;
- [ ] Safari PASS;
- [ ] screen reader PASS;
- [ ] test2 live E2E PASS;
- [ ] Vehicle/Event/Gallery regression PASS;
- [ ] rollback rehearsal PASS;
- [ ] I9 evidence-manifest identificerer den aktuelle build;
- [ ] ingen obligatorisk gate står PENDING/BLOCKED/FAIL.

Hvis I9 ikke er samlet PASS, stop.

---

## 3. Gate 1 — vælg comparison-side

`ConversionTargetCatalog` accepterer kun en bevidst ikke-kritisk side som comparison-kandidat. Sluggen skal være uden for core/protected domains og typisk indeholde fx:

- `editor-test`;
- `test`;
- `gammel`;
- `compare` / `comparison`;
- `sammenlign`;
- `kladde` / `draft`.

Kontrollér:

- [ ] siden eksisterer i WordPress;
- [ ] den er ikke Hjem/Om/Kontakt/Bliv medlem;
- [ ] den er ikke Vehicle/Event/Gallery;
- [ ] baseline/public output er dokumenteret;
- [ ] backup/restore-point eksisterer.

---

## 4. Gate 2 — shadow-kopi og source hash

Før acceptance skal den aktuelle shadow-kopi være knyttet til den aktuelle legacy source state.

Preflight kræver:

- gyldigt WordPress page ID;
- permalink;
- shadow copy;
- `SourceHash` fra shadow;
- current legacy hash;
- ingen source drift.

Hvis legacy source er ændret efter shadow/acceptance, er den tidligere acceptance stale og skal ikke genbruges.

---

## 5. Gate 3 — human acceptance for én side

`ConversionAcceptanceValidator` kræver alle nedenstående checks:

- [ ] `desktop-compare` — Desktop legacy/new comparison;
- [ ] `tablet-compare` — Tablet legacy/new comparison;
- [ ] `mobile-compare` — Mobil legacy/new comparison;
- [ ] `save-flow` — save flow verificeret;
- [ ] `preview-flow` — preview flow verificeret;
- [ ] `revision-flow` — revision flow verificeret;
- [ ] `rollback-flow` — rollback flow verificeret.

Desuden kræves:

- `ConfirmedManual=true`;
- ikke-tomt `Environment`;
- ikke-tomt `EvidenceRef`;
- acceptance-recordets `SourceHash` skal være identisk med den aktuelle shadow source hash.

`AcceptedForSequence` er afledt af disse beviser og må ikke behandles som et frit administrativt flag.

---

## 6. Gate 4 — preflight

Kør/vis den eksisterende preflight for målsiden.

Forventet preflight-kontrakt:

```text
Mode: cutover-preflight-only
Executable: false
PublicMutationAvailable: false
EligibleForFutureCutover: true|false
Blockers: [...]
```

Fortsæt kun i planlægningen, når `Blockers` er tom.

Hvis der findes blockers, løs den konkrete årsag; omgå ikke gaten.

---

## 7. Gate 5 — comparison acceptance først

Core-sider må ikke blive eligible, før comparison-siden er accepteret.

- [ ] comparison-side har valid acceptance;
- [ ] comparison slug er registreret som accepteret;
- [ ] source drift check er stadig grøn;
- [ ] rollback-evidence er linket.

Først derefter kan `hjem` blive næste kandidat.

---

## 8. Gate 6 — core-sekvens

### Hjem

Hjem kræver accepteret comparison-side.

### Om foreningen

Om kræver accepteret comparison-side **og** accepteret Hjem.

### Kontakt

Kontakt kræver accepteret comparison-side, Hjem og Om.

### Bliv medlem

Bliv medlem kræver accepteret comparison-side, Hjem, Om og Kontakt.

Efter hver side:

1. dokumentér legacy/new Desktop/Tablet/Mobil;
2. test save/preview/revision/rollback;
3. registrér acceptance mod den aktuelle source hash;
4. genkør preflight;
5. verificér næste stages blockers.

Hvis en tidligere accepteret sides source ændres, stop sekvensen og revurder drift/acceptance.

---

## 9. Gate 7 — protected domains

Vehicle/Event/Gallery må ikke følge core-sekvensen automatisk.

Før en protected domain overhovedet kan overvejes:

- alle core-sider skal være accepteret;
- I9 skal fortsat være gyldig for kandidatbuilden;
- særskilt compatibility proof skal eksistere;
- legacy-runtime policy skal eksplicit tillade migrationen;
- data-, specialeditor- og public-output-regression skal være PASS;
- rollback skal være særskilt verificeret.

Så længe `protected-legacy-runtime-policy:<domain>` er en blocker, må den ikke omgås.

---

## 10. Gate 8 — legacy removal sidst

Legacy-kode/data må først fjernes efter:

- hele godkendte conversion-sekvensen er stabil;
- production observation window er gennemført;
- rollbackstrategien er opdateret til den nye public state;
- protected domains har særskilt accepteret migration eller forbliver eksplicit legacy;
- backups er verificeret.

Legacy removal er en separat risikofyldt ændring og må ikke pakkes ind i første cutover.

---

## 11. Operatørens stop-regler

Stop I10 ved enhver af følgende:

- I9 er ikke samlet PASS;
- `EligibleForFutureCutover=false`;
- preflight har mindst én blocker;
- source drift;
- stale acceptance hash;
- manglende manual confirmation;
- manglende evidence reference;
- manglende backup/rollback proof;
- forkert rækkefølge;
- protected-domain policy blocker;
- uventet public forskel uden accepteret forklaring.

Ingen tidsplan eller ønsket release-dato må overstyre en blocker.

---

## 12. Evidence pr. I10-stage

For hver stage gemmes mindst:

- slug/page ID/permalink;
- Git commit/pluginversion;
- legacy source hash;
- shadow source hash;
- acceptance source hash;
- preflight-resultat;
- alle acceptance checks;
- `Environment`;
- `EvidenceRef`;
- manual confirmer/user ID/timestamp;
- før/efter screenshots Desktop/Tablet/Mobil;
- rollback-reference;
- eventuelle afvigelser.

---

## 13. Hvad denne runbook ikke gør

Denne fil:

- aktiverer ingen renderer;
- ændrer ingen WordPress-side;
- opretter ingen cutover-endpoint;
- fjerner ingen legacy-runtime;
- markerer ikke I9 eller I10 PASS.

Den dokumenterer kun det operatorflow, som den eksisterende plan/readiness/preflight-arkitektur allerede kræver.
