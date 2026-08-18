<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

use RuntimeException;

/** UD-089 metadata overlay that never changes the native WordPress media ID. */
final class AssetMetadataValidator
{
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(int $mediaId, array $raw): array
    {
        if ($mediaId <= 0) {
            throw new RuntimeException('Media ID must be a positive WordPress attachment ID.');
        }

        $folder = $this->folder((string) ($raw['Folder'] ?? ''));
        $collections = $this->labels($raw['Collections'] ?? []);
        $tags = $this->labels($raw['Tags'] ?? []);
        $focal = $this->focalPoints(is_array($raw['FocalPoint'] ?? null) ? $raw['FocalPoint'] : []);

        return [
            'SchemaVersion' => '1.0',
            'MediaId' => $mediaId,
            'Folder' => $folder,
            'Collections' => $collections,
            'Tags' => $tags,
            'FocalPoint' => $focal,
            'Copyright' => mb_substr(trim((string) ($raw['Copyright'] ?? '')), 0, 240),
            'SourceUrl' => $this->httpsUrl((string) ($raw['SourceUrl'] ?? '')),
            'UpdatedUtc' => gmdate('c'),
        ];
    }

    private function folder(string $value): string
    {
        $value = trim(str_replace('\\', '/', $value));
        if ($value === '') { return ''; }
        $parts = array_values(array_filter(array_map('trim', explode('/', $value)), static fn(string $part): bool => $part !== ''));
        $clean = [];
        foreach ($parts as $part) {
            if ($part === '.' || $part === '..') { continue; }
            $part = preg_replace('/[^\pL\pN _.-]+/u', '', $part) ?? '';
            $part = trim($part);
            if ($part !== '') { $clean[] = mb_substr($part, 0, 80); }
        }
        return mb_substr(implode('/', $clean), 0, 320);
    }

    /** @param mixed $value @return list<string> */
    private function labels($value): array
    {
        if (is_string($value)) { $value = preg_split('/[,;\n]+/', $value) ?: []; }
        if (!is_array($value)) { return []; }
        $out = [];
        foreach ($value as $label) {
            $label = trim((string) $label);
            $label = preg_replace('/[^\pL\pN _.-]+/u', '', $label) ?? '';
            $label = mb_substr(trim($label), 0, 80);
            if ($label !== '') { $out[$label] = true; }
        }
        $labels = array_keys($out);
        natcasesort($labels);
        return array_values($labels);
    }

    /** @param array<string,mixed> $raw @return array<string,array{X:float,Y:float}> */
    private function focalPoints(array $raw): array
    {
        $result = [];
        foreach (['desktop','tablet','mobile'] as $device) {
            if (!is_array($raw[$device] ?? null)) { continue; }
            $x = max(0.0, min(100.0, (float) ($raw[$device]['X'] ?? 50)));
            $y = max(0.0, min(100.0, (float) ($raw[$device]['Y'] ?? 50)));
            $result[$device] = ['X'=>$x,'Y'=>$y];
        }
        return $result;
    }

    private function httpsUrl(string $url): string
    {
        $url = trim($url);
        if ($url === '') { return ''; }
        $parts = parse_url($url);
        if (!is_array($parts) || strtolower((string) ($parts['scheme'] ?? '')) !== 'https' || empty($parts['host'])) {
            return '';
        }
        return mb_substr($url, 0, 1000);
    }
}
