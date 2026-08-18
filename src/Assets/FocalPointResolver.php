<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

/** UD-091 resolves responsive focal points to CSS object-position. */
final class FocalPointResolver
{
    /**
     * @param array<string,array{X?:mixed,Y?:mixed}> $points
     * @return array<string,array{X:float,Y:float,Css:string}>
     */
    public function resolve(array $points): array
    {
        $resolved = [];
        $last = ['X'=>50.0,'Y'=>50.0];
        foreach (['desktop','tablet','mobile'] as $device) {
            if (is_array($points[$device] ?? null)) {
                $last = [
                    'X'=>max(0.0,min(100.0,(float) ($points[$device]['X'] ?? $last['X']))),
                    'Y'=>max(0.0,min(100.0,(float) ($points[$device]['Y'] ?? $last['Y']))),
                ];
            }
            $resolved[$device] = [
                'X'=>$last['X'],
                'Y'=>$last['Y'],
                'Css'=>$this->number($last['X']) . '% ' . $this->number($last['Y']) . '%',
            ];
        }
        return $resolved;
    }

    /** @param array<string,array{X?:mixed,Y?:mixed}> $points */
    public function cssVariables(array $points): string
    {
        $resolved = $this->resolve($points);
        return '--h18-focal-desktop:' . $resolved['desktop']['Css'] . ';'
            . '--h18-focal-tablet:' . $resolved['tablet']['Css'] . ';'
            . '--h18-focal-mobile:' . $resolved['mobile']['Css'] . ';';
    }

    private function number(float $value): string
    {
        $formatted = number_format($value, 2, '.', '');
        return rtrim(rtrim($formatted, '0'), '.');
    }
}
