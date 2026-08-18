<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

/** Required human checks before a shadow conversion can advance the I10 sequence. */
final class ConversionAcceptanceChecklist
{
    /** @var array<string,string> */
    private const CHECKS = [
        'desktop-compare' => 'Desktop legacy/new comparison',
        'tablet-compare' => 'Tablet legacy/new comparison',
        'mobile-compare' => 'Mobile legacy/new comparison',
        'save-flow' => 'Save flow verified',
        'preview-flow' => 'Preview flow verified',
        'revision-flow' => 'Revision flow verified',
        'rollback-flow' => 'Rollback flow verified',
    ];

    /** @return array<string,string> */
    public function required(): array
    {
        return self::CHECKS;
    }

    /** @return array<string,bool> */
    public function emptyStatus(): array
    {
        return array_fill_keys(array_keys(self::CHECKS), false);
    }
}
