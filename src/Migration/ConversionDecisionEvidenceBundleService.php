<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

/**
 * Packages a decision packet and its evidence chain into one in-memory report.
 * It performs no persistence and carries no cutover authority.
 */
final class ConversionDecisionEvidenceBundleService
{
    private ConversionDecisionPacketReviewChainService $reviewChain;

    public function __construct(?ConversionDecisionPacketReviewChainService $reviewChain = null)
    {
        $this->reviewChain = $reviewChain ?? new ConversionDecisionPacketReviewChainService();
    }

    /**
     * @param array<string,mixed> $packet
     * @param array<string,mixed>|null $fingerprint
     * @param array<string,mixed>|null $receipt
     * @return array<string,mixed>
     */
    public function build(array $packet, ?array $fingerprint, ?array $receipt): array
    {
        $chain = $this->reviewChain->inspect($packet, $fingerprint, $receipt);
        $packetHash = is_array($fingerprint) ? strtolower(trim((string)($fingerprint['Hash'] ?? ''))) : '';

        return [
            'SchemaVersion' => '1.0',
            'Mode' => 'decision-evidence-bundle-only',
            'PacketHash' => $packetHash,
            'EvidenceChainComplete' => !empty($chain['ReviewChainValid']),
            'FreshHumanReviewRequired' => !empty($chain['FreshHumanReviewRequired']),
            'Packet' => $packet,
            'Fingerprint' => $fingerprint,
            'ReviewReceipt' => $receipt,
            'ReviewChain' => $chain,
            'AuthorizesCutover' => false,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
    }
}
