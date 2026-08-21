<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

/**
 * Validates the evidence chain packet -> fingerprint -> human review receipt.
 * This is an audit/readiness report only and can never authorize cutover.
 */
final class ConversionDecisionPacketReviewChainService
{
    private ConversionDecisionPacketFingerprintService $fingerprints;
    private ConversionDecisionPacketReviewReceiptService $receipts;

    public function __construct(
        ?ConversionDecisionPacketFingerprintService $fingerprints = null,
        ?ConversionDecisionPacketReviewReceiptService $receipts = null
    ) {
        $this->fingerprints = $fingerprints ?? new ConversionDecisionPacketFingerprintService();
        $this->receipts = $receipts ?? new ConversionDecisionPacketReviewReceiptService($this->fingerprints);
    }

    /**
     * @param array<string,mixed> $packet
     * @param array<string,mixed>|null $fingerprint
     * @param array<string,mixed>|null $receipt
     * @return array<string,mixed>
     */
    public function inspect(array $packet, ?array $fingerprint, ?array $receipt): array
    {
        $blockers = [];
        $packetModeValid = ($packet['Mode'] ?? '') === 'decision-packet-only';
        $packetSafe = empty($packet['Executable']) && empty($packet['PublicMutationAvailable']);

        if (!$packetModeValid) {
            $blockers[] = 'review-chain:packet-mode-invalid';
        }
        if (!$packetSafe) {
            $blockers[] = 'review-chain:packet-execution-invariant-violated';
        }

        $fingerprintValid = is_array($fingerprint) && $this->fingerprints->verify($packet, $fingerprint);
        if (!is_array($fingerprint)) {
            $blockers[] = 'review-chain:fingerprint-missing';
        } elseif (!$fingerprintValid) {
            $blockers[] = 'review-chain:fingerprint-invalid-or-stale';
        }

        $receiptValid = is_array($receipt) && $this->receipts->verify($packet, $receipt);
        if (!is_array($receipt)) {
            $blockers[] = 'review-chain:human-review-receipt-missing';
        } elseif (!$receiptValid) {
            $blockers[] = 'review-chain:human-review-receipt-invalid-or-stale';
        }

        $fingerprintHash = is_array($fingerprint) ? strtolower(trim((string) ($fingerprint['Hash'] ?? ''))) : '';
        $receiptHash = is_array($receipt) ? strtolower(trim((string) ($receipt['PacketHash'] ?? ''))) : '';
        $hashesMatch = $fingerprintHash !== '' && $receiptHash !== '' && hash_equals($fingerprintHash, $receiptHash);
        if (is_array($fingerprint) && is_array($receipt) && !$hashesMatch) {
            $blockers[] = 'review-chain:fingerprint-receipt-hash-mismatch';
        }

        $blockers = array_values(array_unique($blockers));
        sort($blockers, SORT_STRING);
        $reviewChainValid = $blockers === [] && $packetModeValid && $packetSafe && $fingerprintValid && $receiptValid && $hashesMatch;

        $reviewableTargets = array_values(array_filter(
            array_map(static fn($v): string => strtolower(trim((string) $v)), (array) ($packet['ReviewableTargets'] ?? [])),
            static fn(string $v): bool => $v !== ''
        ));
        $reviewableTargets = array_values(array_unique($reviewableTargets));
        sort($reviewableTargets, SORT_STRING);

        return [
            'SchemaVersion' => '1.0',
            'Mode' => 'decision-packet-review-chain-only',
            'PacketModeValid' => $packetModeValid,
            'PacketSafetyInvariantValid' => $packetSafe,
            'FingerprintValid' => $fingerprintValid,
            'HumanReviewReceiptValid' => $receiptValid,
            'FingerprintReceiptHashesMatch' => $hashesMatch,
            'ReviewChainValid' => $reviewChainValid,
            'FreshHumanReviewRequired' => !$reviewChainValid,
            'ReviewableTargets' => $reviewableTargets,
            'Blockers' => $blockers,
            'AuthorizesCutover' => false,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
    }
}
