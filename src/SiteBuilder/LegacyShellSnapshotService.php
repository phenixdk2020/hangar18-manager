<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

/**
 * Builds a deterministic, read-only snapshot of the currently authoritative
 * legacy Header/Footer shell. No WordPress storage is written by this service.
 */
final class LegacyShellSnapshotService
{
    public const HEADER_START = '<!-- HANGAR18-HEADER-START -->';
    public const HEADER_END = '<!-- HANGAR18-HEADER-END -->';
    public const FOOTER_START = '<!-- HANGAR18-FOOTER-START -->';
    public const FOOTER_END = '<!-- HANGAR18-FOOTER-END -->';

    /** @param array<string,mixed> $headerDesign @return array<string,mixed> */
    public function build(array $headerDesign, string $shellContent, string $runtimeVersion = ''): array
    {
        $headerHtml = $this->extractBlock($shellContent, self::HEADER_START, self::HEADER_END);
        $footerHtml = $this->extractBlock($shellContent, self::FOOTER_START, self::FOOTER_END);
        $design = $this->normalize($headerDesign);

        $source = [
            'RuntimeVersion' => $runtimeVersion,
            'HeaderDesign' => $design,
            'HeaderHtml' => $headerHtml,
            'FooterHtml' => $footerHtml,
        ];

        return [
            'SchemaVersion' => '1.0',
            'RuntimeVersion' => $runtimeVersion,
            'HeaderMarkerComplete' => $headerHtml !== '',
            'FooterMarkerComplete' => $footerHtml !== '',
            'ReadyForShadowImport' => $headerHtml !== '' && $footerHtml !== '',
            'DesignKeyCount' => count($design),
            'HeaderBytes' => strlen($headerHtml),
            'FooterBytes' => strlen($footerHtml),
            'SourceHash' => hash('sha256', $this->encode($source)),
            'HeaderDesign' => $design,
            'HeaderHtml' => $headerHtml,
            'FooterHtml' => $footerHtml,
        ];
    }

    private function extractBlock(string $content, string $start, string $end): string
    {
        $startPos = strpos($content, $start);
        if ($startPos === false) {
            return '';
        }
        $endPos = strpos($content, $end, $startPos + strlen($start));
        if ($endPos === false) {
            return '';
        }
        $length = ($endPos + strlen($end)) - $startPos;
        return trim(substr($content, $startPos, $length));
    }

    /** @param array<string,mixed> $value @return array<string,mixed> */
    private function normalize(array $value): array
    {
        ksort($value);
        foreach ($value as $key => $item) {
            if (is_array($item)) {
                $value[$key] = $this->normalizeArray($item);
            }
        }
        return $value;
    }

    /** @param array<mixed> $value @return array<mixed> */
    private function normalizeArray(array $value): array
    {
        if (!$this->isList($value)) {
            ksort($value);
        }
        foreach ($value as $key => $item) {
            if (is_array($item)) {
                $value[$key] = $this->normalizeArray($item);
            }
        }
        return $value;
    }

    /** @param array<mixed> $value */
    private function isList(array $value): bool
    {
        if ($value === []) {
            return true;
        }
        return array_keys($value) === range(0, count($value) - 1);
    }

    /** @param array<string,mixed> $value */
    private function encode(array $value): string
    {
        $json = json_encode($value, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        return is_string($json) ? $json : '';
    }
}
