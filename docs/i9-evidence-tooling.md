# I9 evidence tooling

Dette værktøjssæt understøtter den manuelle/live I9-gate uden at ændre WordPress, public renderer eller cutover-state.

## Formål

I9 består fortsat af faktiske browser-, screen-reader-, `test2`-, protected-domain- og rollback-beviser. Værktøjerne hjælper kun med at oprette, registrere, validere, integritetskontrollere og opsummere evidence-manifestet.

- `tools/i9-evidence-init.cjs` opretter et nyt manifest med alle gates som `PENDING`.
- `tools/i9-evidence-validator.cjs` validerer struktur, build- og miljøidentitet, gate-status, evidence-referencer og den afledte samlede I9-status.
- `tools/i9-evidence-record.cjs` transformerer én gate ad gangen og skriver kun det beregnede manifest til stdout; kildefilen ændres aldrig.
- `tools/i9-evidence-integrity.cjs` beregner SHA-256 og størrelse for lokale evidence-filer og markerer eksterne refs som eksterne/ikke lokalt verificerede.
- `tools/i9-evidence-readiness.cjs` laver en blocker-/next-action-rapport for alle otte gates og kan kun sætte `readyForI10=true` ved fuld valideret PASS.
- `.github/workflows/i9-evidence-validate.yml` samler validation, integrity og readiness i et eksplicit `workflow_dispatch`-job.
- Ingen af værktøjerne logger ind i WordPress, skriver sideindhold eller aktiverer cutover.

## 1. Opret et nyt manifest

Eksempel med den aktuelle pluginbaseline 0.8.39:

```bash
node tools/i9-evidence-init.cjs \
  --sha 0123456789abcdef0123456789abcdef01234567 \
  --version 0.8.39 \
  --wordpress-version 6.8.2 \
  --php-version 8.2 \
  --tester "Allan" \
  --backup-restore-point H18-BACKUP-123456 \
  --output evidence/i9/manifest.json
```

Standard-target er `https://test2.hangar18.dk/`. Et andet staging-target kan sættes med `--target`.

Initializeren:

- kræver en reel 40-tegns commit-SHA;
- afviser all-zero template-SHA;
- kræver plugin-, WordPress- og PHP-version;
- kræver tester-reference;
- starter alle obligatoriske gates som `PENDING` med tom evidence-liste;
- sætter altid `overallStatus=PENDING`;
- overskriver ikke en eksisterende fil uden `--force`.

## 2. Valider under evidence-arbejdet

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json
```

Validatoren kontrollerer bl.a.:

- schemaVersion;
- ukendte felter;
- commit-SHA og pluginversion;
- testtidspunkt og target-URL;
- WordPress/PHP-version;
- alle otte obligatoriske gates;
- tilladte statusværdier `PASS`, `FAIL`, `BLOCKED`, `PENDING`;
- at `PASS` altid har mindst én evidence-reference;
- at evidence-referencer er unikke og ikke tomme;
- at `overallStatus` svarer til gate-statusserne.

Samlet status afledes deterministisk:

1. mindst én `FAIL` → `FAIL`;
2. ellers mindst én `BLOCKED` → `BLOCKED`;
3. alle gates `PASS` → `PASS`;
4. ellers → `PENDING`.

Et manifest kan derfor ikke manuelt erklære en anden samlet status end den, evidence-gates faktisk giver.

## 3. Lås validation til konkret build og stagingmiljø

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/
```

URL'en normaliseres, så fx `https://test2.hangar18.dk` og `https://test2.hangar18.dk/` er samme target. Et andet host/path accepteres ikke, når `--expected-target` bruges.

Build- og target-binding bør bruges, når evidence vurderes som release-bevis, så et gammelt manifest eller evidence fra et andet stagingmiljø ikke ved en fejl kan genbruges.

## 4. Kræv fuld I9 PASS

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/ \
  --require-pass
```

`--require-pass` returnerer fejlstatus, medmindre alle otte gates er evidenced `PASS` og den samlede status derfor er `PASS`.

Det er denne mode, der kan bruges som teknisk release-gate efter den faktiske manuelle/live test. Den skaber ikke acceptance; den kontrollerer kun, at den registrerede acceptance er konsistent og hører til den forventede build og staging-target.

## 5. Maskin- og human-readable validation

JSON:

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json --json
```

Markdown:

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.json --markdown
```

Markdown-outputtet viser build, target, afledt I9-status, gate-tællere, fejl og advarsler og kan gemmes sammen med øvrig evidence.

## 6. Registrer én gate sikkert

Recorderen ændrer **aldrig** den fil, den læser. Den validerer først manifestet, transformerer én gate i hukommelsen, genberegner `overallStatus`, validerer resultatet og skriver derefter det nye JSON til stdout.

Eksempel:

```bash
node tools/i9-evidence-record.cjs evidence/i9/manifest.json \
  --gate chrome \
  --status PASS \
  --evidence evidence/chrome-desktop.md \
  --evidence evidence/chrome-mobile.md \
  --browser-or-tool "Google Chrome" \
  --notes "Brand test gennemført" \
  > evidence/i9/manifest.next.json
```

Derefter valideres den nye fil eksplicit:

```bash
node tools/i9-evidence-validator.cjs evidence/i9/manifest.next.json \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/
```

Recorder-regler:

- kun de otte kendte gates accepteres;
- kun `PASS`, `FAIL`, `BLOCKED` og `PENDING` accepteres;
- `PASS` kan ikke registreres uden mindst én evidence-reference;
- evidence deduplikeres;
- `--clear-evidence` rydder kun i outputmodellen, ikke i kildefilen;
- `overallStatus` kan ikke vælges manuelt, men afledes på ny efter hver transformation;
- kildefilen forbliver byte-identisk.

## 7. Kontroller evidence-integritet

Lokale evidence-filer kan hashes og størrelseskontrolleres uden at ændre dem:

```bash
node tools/i9-evidence-integrity.cjs evidence/i9/manifest.json \
  --root . \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/
```

Integritetsrapporten:

- genbruger den canonical manifest-validator;
- afviser manglende lokale evidence-filer;
- afviser absolute/traversal-stier;
- beregner SHA-256 og byte-størrelse for lokale filer;
- markerer URL-/eksterne refs som `external` og **ikke lokalt verificerede**;
- kan med `--require-all-local` kræve, at alle refs kan verificeres lokalt;
- kan med `--require-pass` samtidig kræve fuld I9 PASS.

Den ændrer hverken manifest eller evidence-filer.

## 8. Se readiness og konkrete blockers

```bash
node tools/i9-evidence-readiness.cjs evidence/i9/manifest.json \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/
```

Markdown-version:

```bash
node tools/i9-evidence-readiness.cjs evidence/i9/manifest.json --markdown
```

Rapporten viser for hver gate:

- status;
- antal evidence-referencer;
- om gaten er komplet;
- blocker (`gate-pending`, `gate-blocked`, `gate-failed` eller manglende PASS-evidence);
- næste konkrete manuelle handling.

`readyForI10` er kun `true`, når manifestet er validt, den afledte status er `PASS`, alle otte gates er komplette, og build/miljøbindingen accepteres. Feltet er kun en **readiness-indikator**; det ændrer ikke I10-preflight, aktiverer ikke en mutation og er ikke i sig selv en cutover-godkendelse.

## 9. GitHub Actions release-gate

Workflowet **I9 Evidence Validate** er kun `workflow_dispatch`; det kører ikke automatisk på push eller pull request.

Inputs:

- `manifest_path` — repository-relativ sti til manifestet;
- `evidence_root` — repository-relativ rod for lokale evidence-referencer;
- `expected_sha` — build-SHA; blank bruger workflow-commit SHA;
- `expected_version` — forventet pluginversion; blank læser `Hangar18_Manager::VERSION` direkte fra `hangar18-manager.php`;
- `expected_target` — forventet staging-URL, standard `https://test2.hangar18.dk/`;
- `require_pass` — når `true`, skal hele I9 være evidenced PASS;
- `require_all_local` — når `true`, må der ikke være eksterne/ikke-lokalt-verificerede evidence-referencer.

Workflowet:

- har kun `contents: read`;
- afviser absolutte/path-traversal manifest-/evidence-root-stier;
- binder manifestet til build-SHA, source-version og staging-target;
- kører canonical validation, integrity og readiness;
- gemmer `i9-evidence-validation.json`, `i9-evidence-integrity.json` og `i9-evidence-readiness.json` samlet som Actions-artifact;
- laver ingen WordPress-, login- eller public-write-kald.

## 10. Hvad værktøjet ikke må gøre

Det må ikke:

- markere en manuel browsertest som udført;
- opfinde screenshots eller evidence-links;
- logge ind i WordPress;
- submitte formularer;
- ændre Vehicle/Event/Gallery;
- aktivere ny public renderer;
- gøre I10 executable;
- erstatte rollback-rehearsal.

I9 er først faktisk PASS, når de krævede human/live gates er udført, registreret med reel evidence og validatoren derefter accepterer manifestet i `--require-pass` mode. Readiness-rapporten må først vise `readyForI10=true` i samme situation, og selv dér forbliver selve I10-cutover-koden separat låst/non-executable indtil den senere kontrollerede cutover-fase.
