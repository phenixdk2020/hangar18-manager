# I10 decision packet — operator review only

`ConversionDecisionPacketService` samler de eksisterende I10 decision-only services i én læsbar operatorpakke:

1. `ConversionPlanService` fastlægger canonical stage-rækkefølge og plan-blockers.
2. `ConversionReadinessGate` håndhæver manual evidence, comparison/core-sekvens og protected-domain policy.
3. `ConversionCutoverPreflightService` kontrollerer WordPress-identitet, shadow-copy, source drift og human acceptance.
4. Decision packet aggregerer disse resultater uden at udføre migration, activation eller public write.

## Output

Pakken indeholder:

- `Mode=decision-packet-only`;
- canonical `ComparisonSlug`;
- `ManualEvidenceComplete`;
- `AcceptedSlugs`;
- ordered `Stages`;
- `ReviewableTargets`;
- `BlockedTargets` med konkrete blockers;
- `Executable=false`;
- `PublicMutationAvailable=false`.

Hver stage indeholder plan-status, preflight-status og den samlede blocker-liste. En stage bliver kun `EligibleForOperatorReview=true`, når både eksisterende plan/readiness og preflight er uden blockers.

## Vigtige stopregler

Decision packet er **ikke cutover** og er ikke et signal om, at en side automatisk må aktiveres. Selv en stage med `EligibleForOperatorReview=true` er kun klar til menneskelig gennemgang.

Servicen må ikke:

- kalde WordPress content/post/option mutation APIs;
- oprette, opdatere eller publicere sider;
- ændre public renderer eller routing;
- omgå comparison → core sequence;
- omgå source-hash/acceptance-kontroller;
- omgå protected Vehicle/Event/Gallery legacy-runtime policy;
- ændre `Executable=false` eller `PublicMutationAvailable=false`.

## Typiske blockers

Decision packet viderefører eksisterende blockers og tilføjer kun packet-specifikke inputblockers:

- `decision-target-missing` — planen har ingen gyldig slug for stage;
- `decision-input-missing` — der mangler page/shadow/acceptance/preflight-input for stage;
- `non-executable-invariant-violated` — en underliggende preflight har mod forventning eksponeret execution/public mutation; dette skal behandles som arkitekturfejl.

Derudover kan eksisterende blockers bl.a. være:

- `manual-gate:*`;
- `comparison-page-not-accepted`;
- `prior-core-not-accepted:*`;
- `wordpress-page-missing`;
- `wordpress-page-id-missing`;
- `wordpress-permalink-missing`;
- `shadow-copy-missing`;
- `legacy-source-drift`;
- `acceptance-*`;
- `protected-legacy-runtime-policy:*`.

## QA

`tests/Architecture/i10-decision-packet-smoke.php` verificerer bl.a.:

- fully evidenced comparison kan blive operator-reviewable;
- Hjem/core stages er sekvenslåste;
- manglende per-target input forbliver blocking;
- manual I9 evidence blockers propagates;
- source drift propagates;
- protected domains forbliver blocked;
- servicekilden indeholder ingen kendte WordPress mutation primitives;
- packet og embedded preflight forbliver non-executable og non-mutating.

Smoken køres transitivt gennem den eksisterende `architecture-smoke.php`, så den dækkes af Architecture QA på alle understøttede PHP-versioner.
