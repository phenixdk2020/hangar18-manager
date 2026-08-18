<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

final class StateInspector
{
    /** @param array<string,mixed> $state @return list<array<string,mixed>> */
    public function sections(array $state): array
    {
        $sections = [];
        foreach ((array) ($state['Sections'] ?? []) as $section) {
            if (is_array($section)) { $sections[] = $section; }
        }
        return $sections;
    }

    /** @param array<string,mixed> $section */
    public function key(array $section): string
    {
        return trim((string) ($section['Key'] ?? ''));
    }

    /** @param array<string,mixed> $section */
    public function type(array $section): string
    {
        return strtolower(trim((string) ($section['Type'] ?? '')));
    }

    /** @param array<string,mixed> $section */
    public function headingLevel(array $section): int
    {
        foreach (['HeadingLevel','Level','HeadingTag','TitleTag'] as $key) {
            $value = strtolower(trim((string) ($section[$key] ?? '')));
            if (preg_match('/^h([1-6])$/', $value, $m)) { return (int) $m[1]; }
            if (ctype_digit($value) && (int) $value >= 1 && (int) $value <= 6) { return (int) $value; }
        }
        if ($this->type($section) === 'heading') { return 2; }
        return 0;
    }

    /** @param array<string,mixed> $state @return array<string,int> */
    public function depths(array $state): array
    {
        $sections = $this->sections($state);
        $parents = [];
        foreach ($sections as $section) {
            $key = $this->key($section);
            if ($key !== '') { $parents[$key] = trim((string) ($section['LayoutParentKey'] ?? '')); }
        }
        $depths = [];
        foreach ($parents as $key => $_) {
            $depth = 1; $cursor = $key; $seen = [];
            while (isset($parents[$cursor]) && $parents[$cursor] !== '') {
                if (isset($seen[$cursor])) { $depth = 100; break; }
                $seen[$cursor] = true; $cursor = $parents[$cursor]; $depth++;
                if ($depth > 100) { break; }
            }
            $depths[$key] = $depth;
        }
        return $depths;
    }

    public function contrastRatio(string $foreground, string $background): ?float
    {
        $fg = $this->hexRgb($foreground); $bg = $this->hexRgb($background);
        if ($fg === null || $bg === null) { return null; }
        $l1 = $this->luminance($fg); $l2 = $this->luminance($bg);
        $lighter = max($l1,$l2); $darker = min($l1,$l2);
        return ($lighter + 0.05) / ($darker + 0.05);
    }

    /** @return array{0:int,1:int,2:int}|null */
    private function hexRgb(string $value): ?array
    {
        $value = ltrim(trim($value), '#');
        if (strlen($value) === 3 && ctype_xdigit($value)) {
            $value = $value[0].$value[0].$value[1].$value[1].$value[2].$value[2];
        }
        if (strlen($value) !== 6 || !ctype_xdigit($value)) { return null; }
        return [hexdec(substr($value,0,2)),hexdec(substr($value,2,2)),hexdec(substr($value,4,2))];
    }

    /** @param array{0:int,1:int,2:int} $rgb */
    private function luminance(array $rgb): float
    {
        $channels = [];
        foreach ($rgb as $value) {
            $v = $value / 255;
            $channels[] = $v <= 0.03928 ? $v / 12.92 : (($v + 0.055) / 1.055) ** 2.4;
        }
        return 0.2126*$channels[0] + 0.7152*$channels[1] + 0.0722*$channels[2];
    }
}
