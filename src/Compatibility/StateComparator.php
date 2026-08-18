<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

final class StateComparator
{
    public function compare(array $legacy, array $candidate): CompatibilityResult
    {
        if ($legacy === $candidate) {
            return new CompatibilityResult(true);
        }

        $differences = [];
        $this->diff($legacy, $candidate, '$', $differences);

        if ($differences === []) {
            $differences[] = 'State differs by PHP strict comparison.';
        }

        return new CompatibilityResult(false, array_slice($differences, 0, 25));
    }

    private function diff($legacy, $candidate, string $path, array &$differences): void
    {
        if (count($differences) >= 25 || $legacy === $candidate) {
            return;
        }

        if (is_array($legacy) && is_array($candidate)) {
            if (array_keys($legacy) !== array_keys($candidate)) {
                $differences[] = $path . ' has different key order/set.';
            }

            foreach ($legacy as $key => $legacyValue) {
                $childPath = $path . '[' . (is_int($key) ? $key : "'" . $key . "'") . ']';
                if (!array_key_exists($key, $candidate)) {
                    $differences[] = $childPath . ' is missing from candidate state.';
                    continue;
                }
                $this->diff($legacyValue, $candidate[$key], $childPath, $differences);
            }

            foreach ($candidate as $key => $_candidateValue) {
                if (!array_key_exists($key, $legacy)) {
                    $childPath = $path . '[' . (is_int($key) ? $key : "'" . $key . "'") . ']';
                    $differences[] = $childPath . ' exists only in candidate state.';
                }
            }
            return;
        }

        $differences[] = sprintf('%s differs (%s:%s !== %s:%s).', $path, gettype($legacy), $this->preview($legacy), gettype($candidate), $this->preview($candidate));
    }

    private function preview($value): string
    {
        if (is_bool($value)) {
            return $value ? 'true' : 'false';
        }
        if ($value === null) {
            return 'null';
        }
        if (is_scalar($value)) {
            $text = (string) $value;
            return strlen($text) > 80 ? substr($text, 0, 77) . '...' : $text;
        }
        return gettype($value);
    }
}
