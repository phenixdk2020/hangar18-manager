<?php

declare(strict_types=1);

namespace Hangar18\Clean\Model;

final class LayoutModel
{
    public const META = '_h18_clean_layout_v1';
    public const HISTORY_META = '_h18_clean_layout_history_v1';
    public const VERSION_META = '_h18_clean_layout_version_v1';
    public const SCHEMA = 1;
    public const UNITS = 120;
    public const ROW_PX = 8;
    public const MAX_NODES = 300;
    public const MAX_HISTORY = 50;

    /** @return array<string,mixed> */
    public static function empty(): array
    {
        return [
            'schemaVersion' => self::SCHEMA,
            'units' => self::UNITS,
            'rowPx' => self::ROW_PX,
            'nodes' => [],
        ];
    }

    /** @return array<string,mixed> */
    public static function get(int $postId): array
    {
        $raw = get_post_meta($postId, self::META, true);
        if (!is_array($raw)) {
            return self::empty();
        }
        try {
            return self::normalize($raw);
        } catch (\Throwable $error) {
            return self::empty();
        }
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public static function normalize(array $raw): array
    {
        $nodesRaw = isset($raw['nodes']) && is_array($raw['nodes']) ? array_values($raw['nodes']) : [];
        if (count($nodesRaw) > self::MAX_NODES) {
            throw new \RuntimeException('For mange elementer i layoutmodellen.');
        }

        $nodes = [];
        foreach ($nodesRaw as $index => $nodeRaw) {
            if (!is_array($nodeRaw)) {
                throw new \RuntimeException('Ugyldigt element i layoutmodellen.');
            }
            $id = self::cleanId($nodeRaw['id'] ?? '');
            if ($id === '' || isset($nodes[$id])) {
                throw new \RuntimeException('Element-ID mangler eller er dubleret.');
            }
            $type = sanitize_key((string) ($nodeRaw['type'] ?? 'text'));
            if (!in_array($type, ['section', 'container', 'text', 'image'], true)) {
                throw new \RuntimeException('Ukendt elementtype: ' . $type);
            }
            $nodes[$id] = [
                'id' => $id,
                'type' => $type,
                'parentId' => self::cleanId($nodeRaw['parentId'] ?? ''),
                'order' => self::clamp($nodeRaw['order'] ?? (($index + 1) * 10), 1, 100000, ($index + 1) * 10),
                'geometry' => self::geometry(isset($nodeRaw['geometry']) && is_array($nodeRaw['geometry']) ? $nodeRaw['geometry'] : []),
                'props' => self::props($type, isset($nodeRaw['props']) && is_array($nodeRaw['props']) ? $nodeRaw['props'] : []),
            ];
            if (in_array($type, ['section', 'container'], true) && (!isset($nodeRaw['props']) || !is_array($nodeRaw['props']) || !array_key_exists('minHeightRows', $nodeRaw['props']))) {
                $nodes[$id]['props']['minHeightRows'] = (int) $nodes[$id]['geometry']['desktop']['h'];
            }
        }

        self::validateHierarchy($nodes);
        uasort($nodes, static function (array $a, array $b): int {
            $parent = strcmp((string) $a['parentId'], (string) $b['parentId']);
            return $parent !== 0 ? $parent : ((int) $a['order'] <=> (int) $b['order']);
        });

        return [
            'schemaVersion' => self::SCHEMA,
            'units' => self::UNITS,
            'rowPx' => self::ROW_PX,
            'nodes' => array_values($nodes),
        ];
    }

    /** @param array<string,mixed> $model */
    public static function saveVersion(int $postId, array $model, int $userId, string $note): int
    {
        $normalized = self::normalize($model);
        $version = max(0, (int) get_post_meta($postId, self::VERSION_META, true)) + 1;
        $history = get_post_meta($postId, self::HISTORY_META, true);
        $history = is_array($history) ? array_values(array_filter($history, 'is_array')) : [];
        $history[] = [
            'version' => $version,
            'savedUtc' => gmdate('c'),
            'userId' => $userId,
            'note' => sanitize_text_field($note),
            'digest' => self::structuralDigest($normalized),
            'model' => $normalized,
        ];
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }
        update_post_meta($postId, self::META, $normalized);
        update_post_meta($postId, self::HISTORY_META, $history);
        update_post_meta($postId, self::VERSION_META, $version);
        return $version;
    }

    /** @return array<int,array<string,mixed>> */
    public static function history(int $postId): array
    {
        $history = get_post_meta($postId, self::HISTORY_META, true);
        if (!is_array($history)) {
            return [];
        }
        return array_values(array_filter($history, static fn($row): bool => is_array($row) && (int) ($row['version'] ?? 0) > 0));
    }

    /** @return array<string,mixed>|null */
    public static function historyModel(int $postId, int $version): ?array
    {
        foreach (self::history($postId) as $entry) {
            if ((int) ($entry['version'] ?? 0) === $version && isset($entry['model']) && is_array($entry['model'])) {
                return self::normalize($entry['model']);
            }
        }
        return null;
    }

    /** @param array<string,mixed> $model */
    public static function structuralDigest(array $model): string
    {
        $normalized = self::normalize($model);
        $summary = [];
        foreach ($normalized['nodes'] as $node) {
            $row = [
                'id' => $node['id'],
                'type' => $node['type'],
                'parentId' => $node['parentId'],
                'order' => $node['order'],
                'geometry' => $node['geometry'],
                'border' => [
                    'width' => (int) ($node['props']['borderWidth'] ?? 0),
                    'color' => (string) ($node['props']['borderColor'] ?? '#000000'),
                ],
            ];
            if ($node['type'] === 'image') {
                $row['image'] = [
                    'mediaId' => (int) ($node['props']['mediaId'] ?? 0),
                    'fit' => (string) ($node['props']['fit'] ?? 'cover'),
                    'focalX' => (int) ($node['props']['focalX'] ?? 50),
                    'focalY' => (int) ($node['props']['focalY'] ?? 50),
                ];
            }
            $summary[] = $row;
        }
        return hash('sha256', (string) wp_json_encode($summary));
    }

    /** @param array<string,array<string,mixed>> $nodes */
    private static function validateHierarchy(array &$nodes): void
    {
        foreach ($nodes as $id => &$node) {
            $parent = (string) $node['parentId'];
            if ($parent === '') {
                continue;
            }
            if ($parent === $id || !isset($nodes[$parent]) || !in_array($nodes[$parent]['type'], ['section', 'container'], true)) {
                $node['parentId'] = '';
            }
        }
        unset($node);

        foreach (array_keys($nodes) as $start) {
            $seen = [];
            $cursor = $start;
            while ($cursor !== '' && isset($nodes[$cursor])) {
                if (isset($seen[$cursor])) {
                    $nodes[$cursor]['parentId'] = '';
                    break;
                }
                $seen[$cursor] = true;
                $cursor = (string) $nodes[$cursor]['parentId'];
            }
        }
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function geometry(array $raw): array
    {
        $desktop = self::device(isset($raw['desktop']) && is_array($raw['desktop']) ? $raw['desktop'] : [], false);
        $tablet = self::device(isset($raw['tablet']) && is_array($raw['tablet']) ? $raw['tablet'] : [], true);
        $mobile = self::device(isset($raw['mobile']) && is_array($raw['mobile']) ? $raw['mobile'] : [], true);
        return ['desktop' => $desktop, 'tablet' => $tablet, 'mobile' => $mobile];
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function device(array $raw, bool $responsive): array
    {
        $x = self::clamp($raw['x'] ?? 0, 0, self::UNITS - 1, 0);
        $w = self::clamp($raw['w'] ?? self::UNITS, 1, self::UNITS, self::UNITS);
        if ($x + $w > self::UNITS) {
            $w = self::UNITS - $x;
        }
        $result = [
            'x' => $x,
            'y' => self::clamp($raw['y'] ?? 0, -4000, 10000, 0),
            'w' => max(1, $w),
            'h' => self::clamp($raw['h'] ?? 0, 0, 4000, 0),
        ];
        if ($responsive) {
            $result['inheritDesktop'] = array_key_exists('inheritDesktop', $raw) ? (bool) $raw['inheritDesktop'] : true;
        }
        return $result;
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function props(string $type, array $raw): array
    {
        $border = self::borderProps($raw);
        if ($type === 'text') {
            return array_merge([
                'text' => wp_kses_post((string) ($raw['text'] ?? 'Ny tekst')),
                'align' => in_array((string) ($raw['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $raw['align'] : 'left',
            ], $border);
        }
        if ($type === 'image') {
            $fit = strtolower((string) ($raw['fit'] ?? 'cover'));
            if (!in_array($fit, ['cover', 'contain', 'stretch'], true)) {
                $fit = 'cover';
            }
            return array_merge([
                'mediaId' => absint($raw['mediaId'] ?? 0),
                'url' => esc_url_raw((string) ($raw['url'] ?? '')),
                'alt' => sanitize_text_field((string) ($raw['alt'] ?? '')),
                'fit' => $fit,
                'focalX' => self::clamp($raw['focalX'] ?? 50, 0, 100, 50),
                'focalY' => self::clamp($raw['focalY'] ?? 50, 0, 100, 50),
            ], $border);
        }
        if (in_array($type, ['section', 'container'], true)) {
            return array_merge([
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '')) ?: '',
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),
                'minHeightRows' => self::clamp($raw['minHeightRows'] ?? 0, 0, 4000, 0),
            ], $border);
        }
        return $border;
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function borderProps(array $raw): array
    {
        return [
            'borderWidth' => self::clamp($raw['borderWidth'] ?? 0, 0, 20, 0),
            'borderColor' => sanitize_hex_color((string) ($raw['borderColor'] ?? '#000000')) ?: '#000000',
        ];
    }

    /** @param mixed $value */
    private static function cleanId($value): string
    {
        $id = strtolower(trim((string) $value));
        $id = preg_replace('/[^a-z0-9._-]/', '', $id);
        return is_string($id) ? substr($id, 0, 100) : '';
    }

    /** @param mixed $value */
    private static function clamp($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int) $value));
    }
}
