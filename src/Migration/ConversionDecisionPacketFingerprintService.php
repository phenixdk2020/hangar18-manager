<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\Portability\CanonicalJson;

/** Creates an audit fingerprint for a decision packet. It is not an authorization token. */
final class ConversionDecisionPacketFingerprintService
{
    private CanonicalJson $canonical;

    public function __construct(?CanonicalJson $canonical = null)
    {
        $this->canonical = $canonical ?? new CanonicalJson();
    }

    /** @param array<string,mixed> $packet @return array<string,mixed> */
    public function fingerprint(array $packet): array
    {
        $snapshot = $packet;
        unset($snapshot['Fingerprint']);
        return [
            'Algorithm' => 'sha256',
            'Hash' => $this->canonical->hash($snapshot),
            'Purpose' => 'evidence-integrity-only',
            'AuthorizesCutover' => false,
            'Executable' => false,
            'PublicMutationAvailable' => false,
        ];
    }

    /** @param array<string,mixed> $packet @param array<string,mixed> $fingerprint */
    public function verify(array $packet, array $fingerprint): bool
    {
        if (($fingerprint['Algorithm'] ?? '') !== 'sha256') {
            return false;
        }
        if (!empty($fingerprint['AuthorizesCutover']) || !empty($fingerprint['Executable']) || !empty($fingerprint['PublicMutationAvailable'])) {
            return false;
        }
        $expected = (string) ($this->fingerprint($packet)['Hash'] ?? '');
        $actual = strtolower(trim((string) ($fingerprint['Hash'] ?? '')));
        return $actual !== '' && hash_equals($expected, $actual);
    }
}
