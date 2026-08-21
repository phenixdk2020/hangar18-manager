# I10 — blocker reference

**Status:** Operator reference  
**Dato:** 21. august 2026

Denne reference oversætter de eksisterende migration/readiness/preflight blocker-koder til konkret operatørhandling. En blocker skal løses ved kilden; den må ikke undertrykkes for at få en stage til at se grøn ud.

## Readiness blockers

| Blocker | Betydning | Handling |
|---|---|---|
| `manual-gate:<gate>` | En obligatorisk I9 manual evidence-gate mangler | Gennemfør den navngivne I9-test og registrér evidence. |
| `target-empty` | Target slug mangler | Stop; vælg en konkret side. |
| `comparison-page-not-accepted` | Core-side forsøges før comparison er accepteret | Accepter comparison-stage først. |
| `prior-core-not-accepted:<slug>` | En tidligere core-stage mangler acceptance | Følg fast core-rækkefølge. |
| `core-not-accepted:<slug>` | Protected target mangler accepteret core-side | Afslut hele core-sekvensen først. |
| `protected-legacy-runtime-policy:<domain>` | Domain er fortsat tvunget til legacy-runtime | Ingen cutover; kræver særskilt compatibility/policy-ændring. |
| `not-approved-comparison-target` | Slug er ikke en sikker comparison-kandidat | Vælg en ikke-kritisk test/compare/draft-side. |
| `wordpress-page-missing` | Planlagt target findes ikke i WordPress-kataloget | Stop og afklar target; opfind ikke side automatisk. |

## Preflight blockers

| Blocker | Betydning | Handling |
|---|---|---|
| `wordpress-page-id-missing` | Page ID ≤ 0 | Genindlæs target fra WordPress og verificér ID. |
| `wordpress-permalink-missing` | Permalink mangler | Verificér den faktiske WordPress-side og routing. |
| `shadow-copy-missing` | Ingen shadow-version til sammenligning | Opret/indlæs shadow-flowet før acceptance. |
| source-drift blocker | Current legacy source matcher ikke shadow source | Genbyg shadow og gentag acceptance mod ny source hash. |
| `acceptance-evidence-missing` | Intet acceptance record | Udfør alle human acceptance checks og gem evidence. |
| `acceptance-source-hash-stale` | Acceptance hører til en ældre shadow/source | Invalidér gammel acceptance og gentest aktuel source. |
| `acceptance-check:<key>` | Ét required human check er ikke PASS | Gennemfør det navngivne check. |
| `acceptance-manual-confirmation-missing` | Menneskelig confirmation mangler | En reel tester skal bekræfte acceptance. |
| `acceptance-environment-missing` | Testmiljø er ikke registreret | Registrér miljø/build/testtarget. |
| `acceptance-evidence-ref-missing` | Acceptance peger ikke på evidence | Tilføj stabil evidence-reference. |

## Required acceptance-check keys

Disse keys kommer fra den eksisterende `ConversionAcceptanceChecklist` og skal alle være true:

| Key | Krav |
|---|---|
| `desktop-compare` | Desktop legacy/new comparison |
| `tablet-compare` | Tablet legacy/new comparison |
| `mobile-compare` | Mobil legacy/new comparison |
| `save-flow` | Save flow verified |
| `preview-flow` | Preview flow verified |
| `revision-flow` | Revision flow verified |
| `rollback-flow` | Rollback flow verified |

## Prioritet ved flere blockers

Hvis en stage har flere blockers, håndteres de normalt i denne rækkefølge:

1. I9/manual gates;
2. target/page identitet;
3. sequence blockers;
4. shadow/source drift;
5. acceptance hash/evidence;
6. protected-domain policy.

Efter rettelse skal preflight bygges på ny. Genbrug ikke et gammelt `EligibleForFutureCutover`-resultat.

## Sikkerhedskontrakt

Et tomt blocker-array betyder kun **eligible for future cutover** i den nuværende arkitektur. Det betyder ikke, at der eksisterer en public mutation-knap eller endpoint. Preflight skal fortsat rapportere:

- `Executable=false`;
- `PublicMutationAvailable=false`.
