# I10 review chain — evidence freshness only

`ConversionDecisionPacketReviewChainService` validerer den samlede evidence-kæde:

`decision packet → SHA-256 fingerprint → human review receipt`

Formålet er at kunne afgøre, om en tidligere menneskelig gennemgang stadig gælder for **præcis det samme packet-snapshot**. Servicen autoriserer ikke cutover og udfører ingen WordPress- eller public mutation.

`ConversionDecisionPacketReviewChainFormatter` kan vise rapporten som JSON/Markdown, og `ConversionDecisionEvidenceBundleService` kan samle packet, fingerprint, receipt og review-chain i én in-memory evidence-pakke uden filskrivning.

## Output

Rapporten indeholder bl.a.:

- `Mode=decision-packet-review-chain-only`;
- `PacketModeValid`;
- `PacketSafetyInvariantValid`;
- `FingerprintValid`;
- `HumanReviewReceiptValid`;
- `FingerprintReceiptHashesMatch`;
- `ReviewChainValid`;
- `FreshHumanReviewRequired`;
- canonical `ReviewableTargets`;
- konkrete `Blockers`;
- `AuthorizesCutover=false`;
- `Executable=false`;
- `PublicMutationAvailable=false`.

Der findes bevidst **ingen** `ReadyForCutover`-værdi.

## Freshness-regel

Et review er kun frisk, når alle følgende er sande:

1. packet har `Mode=decision-packet-only`;
2. packet er fortsat non-executable og non-mutating;
3. fingerprint verifierer mod det aktuelle packet;
4. human review receipt verifierer mod det aktuelle packet;
5. receiptens `PacketHash` matcher det leverede fingerprint.

Hvis blockers, source state, acceptance, stage-data eller andre packet-felter ændres efter review, ændres packet-fingerprintet, og den gamle receipt bliver stale. Resultatet bliver `ReviewChainValid=false` og `FreshHumanReviewRequired=true`.

## Formatter

Formatteren har kun præsentationsansvar:

- JSON bevarer review-chain state;
- Markdown viser chain/freshness, packet safety, fingerprint/receipt validity og blockers;
- `Authorizes cutover: NO`, `Executable: NO` og `Public mutation available: NO` vises eksplicit;
- slutteksten siger, at en valid chain kun beviser evidence-freshness og ikke autoriserer cutover.

Formatteren skriver ikke filer eller persistence-state.

## Evidence bundle

Evidence-bundlet samler:

- det konkrete decision packet;
- packet fingerprint;
- human review receipt;
- review-chain rapport;
- `PacketHash`;
- `EvidenceChainComplete`;
- `FreshHumanReviewRequired`;
- `AuthorizesCutover=false`;
- `Executable=false`;
- `PublicMutationAvailable=false`.

Bundlet er et **in-memory report/value object**. Det arkiverer ikke sig selv, skriver ikke WordPress eller filesystem og er ikke en tilladelse. En manglende/stale receipt eller et ændret packet videreføres som incomplete evidence chain.

## Blockers

Mulige review-chain blockers:

- `review-chain:packet-mode-invalid`;
- `review-chain:packet-execution-invariant-violated`;
- `review-chain:fingerprint-missing`;
- `review-chain:fingerprint-invalid-or-stale`;
- `review-chain:human-review-receipt-missing`;
- `review-chain:human-review-receipt-invalid-or-stale`;
- `review-chain:fingerprint-receipt-hash-mismatch`.

Disse blockers beskriver kun evidence-freshness. De erstatter ikke I9 gates, conversion readiness eller preflight blockers.

## Sikkerhedsgrænse

En valid review-chain betyder kun:

> Et menneske har gennemgået dette konkrete decision-packet snapshot, og snapshotet er ikke ændret siden reviewet.

Det betyder **ikke**:

- at I9 automatisk er PASS;
- at en stage må publiceres;
- at protected Vehicle/Event/Gallery må flyttes fra legacy runtime;
- at I10 er executable;
- at nogen WordPress mutation er tilladt.

## QA

`tests/Architecture/i10-decision-packet-review-chain-smoke.php` verificerer exact-chain success, missing fingerprint/receipt, stale packet, forkert packet mode, execution-invariant brud, canonical reviewable-target output og JSON/Markdown safety-reporting.

`tests/Architecture/i10-decision-evidence-bundle-smoke.php` verificerer complete/incomplete/stale evidence bundles og de permanente non-authorizing/non-executable invariants.

Begge tests køres gennem den eksisterende Architecture QA.
