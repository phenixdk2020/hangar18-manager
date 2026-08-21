# I10 review chain — evidence freshness only

`ConversionDecisionPacketReviewChainService` validerer den samlede evidence-kæde:

`decision packet → SHA-256 fingerprint → human review receipt`

Formålet er at kunne afgøre, om en tidligere menneskelig gennemgang stadig gælder for **præcis det samme packet-snapshot**. Servicen autoriserer ikke cutover og udfører ingen WordPress- eller public mutation.

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

`tests/Architecture/i10-decision-packet-review-chain-smoke.php` verificerer exact-chain success, missing fingerprint/receipt, stale packet, forkert packet mode, execution-invariant brud og canonical reviewable-target output. Testen køres gennem den eksisterende Architecture QA.
