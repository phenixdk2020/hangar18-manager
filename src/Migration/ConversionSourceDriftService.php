<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\Portability\CanonicalJson;

/** Detects whether legacy editor-state has changed since the shadow copy was created. */
final class ConversionSourceDriftService
{
    private CanonicalJson $json;

    public function __construct(?CanonicalJson $json = null)
    {
        $this->json = $json ?? new CanonicalJson();
    }

    /** @param array<string,mixed> $shadow @param array<string,mixed> $currentLegacyState @return array<string,mixed> */
    public function evaluate(array $shadow, array $currentLegacyState): array
    {
        $shadowHash = strtolower(trim((string) ($shadow['SourceHash'] ?? '')));
        $currentHash = $this->json->hash($currentLegacyState);
        $blockers = [];
        if ($shadowHash === '') {
            $blockers[] = 'shadow-source-hash-missing';
        } elseif (!hash_equals($shadowHash, $currentHash)) {
            $blockers[] = 'legacy-source-drift';
        }
        return [
            'SchemaVersion' => '1.0',
            'ShadowSourceHash' => $shadowHash,
            'CurrentLegacyHash' => $currentHash,
            'Matches' => $blockers === [],
            'Blockers' => $blockers,
        ];
    }
}
