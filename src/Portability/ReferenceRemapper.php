<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use RuntimeException;

/** Remaps portable artifact:// and asset:// references without guessing target IDs. */
final class ReferenceRemapper
{
    /**
     * @param mixed $value
     * @param array<string,string> $artifactMappings
     * @param array<string,int> $assetMappings
     * @return mixed
     */
    public function remap($value, array $artifactMappings, array $assetMappings)
    {
        if (is_string($value)) {
            if (strncmp($value,'artifact://',11) === 0) {
                $exportId = substr($value,11);
                if (!isset($artifactMappings[$exportId]) || $artifactMappings[$exportId] === '') {
                    throw new RuntimeException('Broken artifact reference: '.$exportId);
                }
                return $artifactMappings[$exportId];
            }
            if (strncmp($value,'asset://',8) === 0) {
                $packageId = substr($value,8);
                if (!isset($assetMappings[$packageId]) || (int) $assetMappings[$packageId] <= 0) {
                    throw new RuntimeException('Broken asset reference: '.$packageId);
                }
                return (int) $assetMappings[$packageId];
            }
            return $value;
        }
        if (!is_array($value)) { return $value; }
        $result = [];
        foreach ($value as $key => $item) { $result[$key] = $this->remap($item,$artifactMappings,$assetMappings); }
        return $result;
    }
}
