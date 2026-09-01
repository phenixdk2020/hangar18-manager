<?php

declare(strict_types=1);

namespace VisualDesignerManager\Model;

/**
 * Compatibility-safe hierarchy normalization for the Visual Designer model.
 *
 * Canonical target:
 * PAGE -> SECTION -> (CONTAINER|LEAF), with nested CONTAINER allowed.
 *
 * Legacy 0.1.21 could place container/text/image directly at root and could
 * technically nest a section. We preserve visible geometry by wrapping each
 * legacy root non-section in a neutral section and by converting nested
 * sections to containers instead of detaching or deleting content.
 */
final class HierarchyNormalizer
{
    /** @param array<string,array<string,mixed>> $nodes */
    public static function normalize(array &$nodes): void
    {
        if (!$nodes) {
            return;
        }

        // A Section is a page-level wrapper. A historical nested Section has
        // the same wrapper capabilities as a Kasse, so conversion is lossless.
        foreach ($nodes as &$node) {
            if ((string) ($node['type'] ?? '') === 'section' && (string) ($node['parentId'] ?? '') !== '') {
                $node['type'] = 'container';
            }
        }
        unset($node);

        // Snapshot the IDs because the array is extended while we migrate.
        $rootIds = [];
        foreach ($nodes as $id => $node) {
            if ((string) ($node['parentId'] ?? '') === '' && (string) ($node['type'] ?? '') !== 'section') {
                $rootIds[] = (string) $id;
            }
        }

        foreach ($rootIds as $id) {
            if (!isset($nodes[$id])) {
                continue;
            }

            $node = &$nodes[$id];
            $oldGeometry = isset($node['geometry']) && is_array($node['geometry']) ? $node['geometry'] : [];
            $oldOrder = max(1, (int) ($node['order'] ?? 10));
            $gapX = self::intProp($node, 'gapX', 0, 200);
            $gapY = self::intProp($node, 'gapY', 0, 200);

            $wrapperId = self::uniqueWrapperId($id, $nodes);
            $nodes[$wrapperId] = [
                'id' => $wrapperId,
                'type' => 'section',
                'parentId' => '',
                'order' => $oldOrder,
                'geometry' => self::copyGeometry($oldGeometry),
                'props' => self::neutralSectionProps($gapX, $gapY),
            ];

            // External spacing belonged to the root node. Move that spacing to
            // the new wrapper so neighbouring root layout remains equivalent.
            if (isset($node['props']) && is_array($node['props'])) {
                $node['props']['gapX'] = 0;
                $node['props']['gapY'] = 0;
            }

            $node['parentId'] = $wrapperId;
            $node['order'] = 10;
            $node['geometry'] = self::localGeometry($oldGeometry);
            unset($node);
        }
    }


    /**
     * Returns true only when the node graph obeys the canonical page contract:
     * PAGE -> SECTION -> (CONTAINER|LEAF), with nested CONTAINER allowed.
     *
     * @param array<int|string,array<string,mixed>> $nodes
     */
    public static function isCanonical(array $nodes): bool
    {
        $map = [];
        foreach ($nodes as $key => $node) {
            if (!is_array($node)) {
                return false;
            }
            $id = (string) ($node['id'] ?? (is_string($key) ? $key : ''));
            if ($id === '' || isset($map[$id])) {
                return false;
            }
            $map[$id] = $node;
        }

        foreach ($map as $id => $node) {
            $type = (string) ($node['type'] ?? '');
            $parent = (string) ($node['parentId'] ?? '');

            if ($type === 'section') {
                if ($parent !== '') {
                    return false;
                }
                continue;
            }
            if ($parent === '') {
                return false;
            }

            $seen = [];
            $cursor = $id;
            while (isset($map[$cursor])) {
                if (isset($seen[$cursor])) {
                    return false;
                }
                $seen[$cursor] = true;
                $current = $map[$cursor];
                $currentType = (string) ($current['type'] ?? '');
                $currentParent = (string) ($current['parentId'] ?? '');
                if ($currentParent === '') {
                    if ($currentType !== 'section') {
                        return false;
                    }
                    break;
                }
                if (!isset($map[$currentParent])) {
                    return false;
                }
                $parentType = (string) ($map[$currentParent]['type'] ?? '');
                if (!in_array($parentType, ['section', 'container'], true)) {
                    return false;
                }
                $cursor = $currentParent;
            }
        }

        return true;
    }

    /** @param array<string,array<string,mixed>> $nodes */
    private static function uniqueWrapperId(string $sourceId, array $nodes): string
    {
        $base = 'section-migrated-' . substr(hash('sha256', $sourceId), 0, 12);
        $candidate = $base;
        $suffix = 2;
        while (isset($nodes[$candidate])) {
            $candidate = $base . '-' . $suffix;
            $suffix++;
        }
        return $candidate;
    }

    /** @param array<string,mixed> $geometry @return array<string,mixed> */
    private static function copyGeometry(array $geometry): array
    {
        $desktop = self::device($geometry['desktop'] ?? [], false, false);
        $laptop = self::device($geometry['laptop'] ?? [], true, false);
        $tablet = self::device($geometry['tablet'] ?? [], true, false);
        $mobile = self::device($geometry['mobile'] ?? [], true, false);
        return [
            'desktop' => $desktop,
            'laptop' => $laptop,
            'tablet' => $tablet,
            'mobile' => $mobile,
        ];
    }

    /** @param array<string,mixed> $geometry @return array<string,mixed> */
    private static function localGeometry(array $geometry): array
    {
        $desktopSource = isset($geometry['desktop']) && is_array($geometry['desktop']) ? $geometry['desktop'] : [];
        $desktop = self::device($desktopSource, false, true);

        $result = ['desktop' => $desktop];
        foreach (['laptop', 'tablet', 'mobile'] as $key) {
            $source = isset($geometry[$key]) && is_array($geometry[$key]) ? $geometry[$key] : [];
            $inherit = array_key_exists('inheritDesktop', $source) ? (bool) $source['inheritDesktop'] : true;
            if ($inherit) {
                $source['h'] = (int) ($desktopSource['h'] ?? 0);
            }
            $result[$key] = self::device($source, true, true);
        }
        return $result;
    }

    /** @param mixed $raw @return array<string,mixed> */
    private static function device($raw, bool $responsive, bool $local): array
    {
        $raw = is_array($raw) ? $raw : [];
        $x = $local ? 0 : max(0, min(119, (int) ($raw['x'] ?? 0)));
        $w = $local ? 120 : max(1, min(120, (int) ($raw['w'] ?? 120)));
        if (!$local && $x + $w > 120) {
            $w = 120 - $x;
        }

        $out = [
            'x' => $x,
            'y' => $local ? 0 : max(-4000, min(10000, (int) ($raw['y'] ?? 0))),
            'w' => max(1, $w),
            'h' => max(0, min(4000, (int) ($raw['h'] ?? 0))),
        ];
        if ($responsive) {
            $out['inheritDesktop'] = array_key_exists('inheritDesktop', $raw) ? (bool) $raw['inheritDesktop'] : true;
        }
        return $out;
    }

    /** @return array<string,mixed> */
    private static function neutralSectionProps(int $gapX, int $gapY): array
    {
        return [
            'background' => '',
            'radius' => 0,
            'padding' => 0,
            'minHeightRows' => 0,
            'moduleSlot' => 'before',
            'borderWidth' => 0,
            'borderColor' => '#000000',
            'gapX' => $gapX,
            'gapY' => $gapY,
            'offsetX' => 0,
            'offsetY' => 0,
        ];
    }

    /** @param array<string,mixed> $node */
    private static function intProp(array $node, string $key, int $min, int $max): int
    {
        $value = isset($node['props']) && is_array($node['props']) ? ($node['props'][$key] ?? 0) : 0;
        if (!is_numeric($value)) {
            return 0;
        }
        return max($min, min($max, (int) $value));
    }
}
