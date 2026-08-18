<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

final class MarkupComparator
{
    public function compare(string $legacy, string $candidate, array $requiredHooks = []): CompatibilityResult
    {
        $legacyNormalized = $this->normalize($legacy);
        $candidateNormalized = $this->normalize($candidate);
        $differences = [];

        foreach ($requiredHooks as $hook) {
            if ($hook === '') {
                continue;
            }
            if (strpos($legacyNormalized, $hook) === false) {
                $differences[] = "Baseline fixture is missing required hook '{$hook}'.";
            }
            if (strpos($candidateNormalized, $hook) === false) {
                $differences[] = "Candidate markup is missing required hook '{$hook}'.";
            }
        }

        if ($legacyNormalized !== $candidateNormalized) {
            $offset = $this->firstDifferenceOffset($legacyNormalized, $candidateNormalized);
            $differences[] = sprintf(
                'Markup differs at byte %d (legacy sha256=%s, candidate sha256=%s).',
                $offset,
                hash('sha256', $legacyNormalized),
                hash('sha256', $candidateNormalized)
            );
        }

        return new CompatibilityResult($differences === [], array_values(array_unique($differences)));
    }

    private function normalize(string $markup): string
    {
        return str_replace(["\r\n", "\r"], "\n", $markup);
    }

    private function firstDifferenceOffset(string $legacy, string $candidate): int
    {
        $max = min(strlen($legacy), strlen($candidate));
        for ($i = 0; $i < $max; $i++) {
            if ($legacy[$i] !== $candidate[$i]) {
                return $i;
            }
        }
        return $max;
    }
}
