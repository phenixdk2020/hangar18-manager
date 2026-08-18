<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use RuntimeException;

final class CanonicalJson
{
    /** @param mixed $value */
    public function encode($value): string
    {
        $json = json_encode($this->normalize($value), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        if (!is_string($json)) { throw new RuntimeException('Value could not be encoded as JSON.'); }
        return $json . "\n";
    }

    /** @param mixed $value */
    public function hash($value): string
    {
        return hash('sha256', $this->encode($value));
    }

    /** @param mixed $value @return mixed */
    private function normalize($value)
    {
        if (!is_array($value)) { return $value; }
        if ($this->isList($value)) { return array_map([$this,'normalize'], $value); }
        ksort($value, SORT_STRING);
        foreach ($value as $key => $item) { $value[$key] = $this->normalize($item); }
        return $value;
    }

    private function isList(array $value): bool
    {
        $expected = 0;
        foreach ($value as $key => $_) {
            if ($key !== $expected) { return false; }
            $expected++;
        }
        return true;
    }
}
