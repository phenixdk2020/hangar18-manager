<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use RuntimeException;

/** Creates and verifies a human-review receipt for a fingerprinted decision packet. */
final class ConversionDecisionPacketReviewReceiptService
{
    private ConversionDecisionPacketFingerprintService $fingerprints;

    public function __construct(?ConversionDecisionPacketFingerprintService $fingerprints = null)
    {
        $this->fingerprints = $fingerprints ?? new ConversionDecisionPacketFingerprintService();
    }

    /**
     * @param array<string,mixed> $packet
     * @param array<string,mixed> $fingerprint
     * @return array<string,mixed>
     */
    public function capture(array $packet, array $fingerprint, string $reviewer, string $environment, string $evidenceRef, string $notes = ''): array
    {
        if (!$this->fingerprints->verify($packet, $fingerprint)) {
            throw new RuntimeException('Decision packet fingerprint is invalid or stale.');
        }
        $reviewer = trim($reviewer);
        $environment = trim($environment);
        $evidenceRef = trim($evidenceRef);
        $notes = trim($notes);
        if ($reviewer === '') { throw new RuntimeException('Operator review requires reviewer identity.'); }
        if ($environment === '') { throw new RuntimeException('Operator review requires environment reference.'); }
        if ($evidenceRef === '') { throw new RuntimeException('Operator review requires evidence reference.'); }

        return [
            'SchemaVersion' => '1.0',
            'Mode' => 'decision-packet-review-receipt-only',
            'PacketHash' => (string) ($fingerprint['Hash'] ?? ''),
            'Reviewer' => mb_substr($reviewer, 0, 240),
            'Environment' => mb_substr($environment, 0, 240),
            'EvidenceRef' => mb_substr($evidenceRef, 0, 700),
            'Notes' => mb_substr($notes, 0, 4000),
            'ReviewedUtc' => gmdate('c'),
            'HumanReviewRecorded' => true,
            'AuthorizesCutover' => false,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
    }

    /** @param array<string,mixed> $packet @param array<string,mixed> $receipt */
    public function verify(array $packet, array $receipt): bool
    {
        if (($receipt['Mode'] ?? '') !== 'decision-packet-review-receipt-only') { return false; }
        if (empty($receipt['HumanReviewRecorded'])) { return false; }
        if (!empty($receipt['AuthorizesCutover']) || !empty($receipt['Executable']) || !empty($receipt['PublicMutationAvailable'])) { return false; }
        foreach (['Reviewer','Environment','EvidenceRef','ReviewedUtc','PacketHash'] as $key) {
            if (trim((string) ($receipt[$key] ?? '')) === '') { return false; }
        }
        $fingerprint = [
            'Algorithm' => 'sha256',
            'Hash' => (string) $receipt['PacketHash'],
            'Purpose' => 'evidence-integrity-only',
            'AuthorizesCutover' => false,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
        return $this->fingerprints->verify($packet, $fingerprint);
    }
}
