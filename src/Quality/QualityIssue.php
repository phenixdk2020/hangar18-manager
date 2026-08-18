<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

final class QualityIssue
{
    /** @param array<string,mixed> $meta @return array<string,mixed> */
    public static function make(string $area, string $code, string $severity, string $message, string $elementKey = '', array $meta = []): array
    {
        $severity = strtolower(trim($severity));
        if (!in_array($severity, ['info','warning','error','critical'], true)) { $severity = 'warning'; }
        return [
            'Area'=>$area,
            'Code'=>$code,
            'Severity'=>$severity,
            'Message'=>$message,
            'ElementKey'=>$elementKey,
            'Meta'=>$meta,
        ];
    }
}
