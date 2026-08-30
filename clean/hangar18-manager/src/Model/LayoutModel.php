<?php

declare(strict_types=1);

namespace VisualDesignerManager\Model;

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
            if (!in_array($type, ['section', 'container', 'text', 'image', 'button', 'menu'], true)) {
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
        HierarchyNormalizer::normalize($nodes);
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
        $json = wp_json_encode($normalized, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) {
            throw new \RuntimeException('Canonical layout kunne ikke serialiseres til digest.');
        }
        return hash('sha256', $json);
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
        $laptop = self::device(isset($raw['laptop']) && is_array($raw['laptop']) ? $raw['laptop'] : [], true);
        $tablet = self::device(isset($raw['tablet']) && is_array($raw['tablet']) ? $raw['tablet'] : [], true);
        $mobile = self::device(isset($raw['mobile']) && is_array($raw['mobile']) ? $raw['mobile'] : [], true);
        return ['desktop' => $desktop, 'laptop' => $laptop, 'tablet' => $tablet, 'mobile' => $mobile];
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
            $headingLevel = strtolower((string) ($raw['headingLevel'] ?? 'h2'));
            if (!in_array($headingLevel, ['h2', 'h3', 'h4', 'h5', 'h6'], true)) {
                $headingLevel = 'h2';
            }
            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) {
                $align = 'left';
            }
            $verticalAlign = strtolower((string) ($raw['verticalAlign'] ?? 'top'));
            if (!in_array($verticalAlign, ['top', 'center', 'bottom'], true)) {
                $verticalAlign = 'top';
            }
            return array_merge([
                'heading' => sanitize_text_field((string) ($raw['heading'] ?? '')),
                'headingLevel' => $headingLevel,
                'text' => wp_kses_post((string) ($raw['text'] ?? 'Ny tekst')),
                'align' => $align,
                'verticalAlign' => $verticalAlign,
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'backgroundTransparent' => true,
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#000000')) ?: '#000000',
                'headingColor' => sanitize_hex_color((string) ($raw['headingColor'] ?? '#000000')) ?: '#000000',
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.5, 0.8, 3.0, 1.5),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'headingFontFamily' => self::fontToken($raw['headingFontFamily'] ?? 'body', true),
                'headingFontSize' => self::clamp($raw['headingFontSize'] ?? 0, 0, 160, 0),
                'headingFontWeight' => self::clamp($raw['headingFontWeight'] ?? 700, 100, 900, 700),
                'headingLineHeight' => self::clampFloat($raw['headingLineHeight'] ?? 1.2, 0.8, 3.0, 1.2),
                'headingLetterSpacing' => self::clampFloat($raw['headingLetterSpacing'] ?? 0, -10.0, 30.0, 0.0),
            ], $border);
        }
        if ($type === 'button') {
            $linkType = strtolower((string) ($raw['linkType'] ?? 'url'));
            if (!in_array($linkType, ['page', 'url', 'anchor', 'email', 'phone'], true)) {
                $linkType = 'url';
            }
            return array_merge([
                'text' => sanitize_text_field((string) ($raw['text'] ?? 'Knap')),
                'linkType' => $linkType,
                'pageId' => absint($raw['pageId'] ?? 0),
                'url' => sanitize_text_field((string) ($raw['url'] ?? '')),
                'targetBlank' => !empty($raw['targetBlank']),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#30382a')) ?: '#30382a',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#ffffff')) ?: '#ffffff',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.2, 0.8, 3.0, 1.2),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'hoverBackground' => sanitize_hex_color((string) ($raw['hoverBackground'] ?? '#525a5f')) ?: '#525a5f',
                'hoverTextColor' => sanitize_hex_color((string) ($raw['hoverTextColor'] ?? '#ffffff')) ?: '#ffffff',
                'focusColor' => sanitize_hex_color((string) ($raw['focusColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'paddingX' => self::clamp($raw['paddingX'] ?? 20, 0, 120, 20),
                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),
                'autoSize' => array_key_exists('autoSize', $raw) ? (bool) $raw['autoSize'] : true,
                'placementMode' => strtolower((string) ($raw['placementMode'] ?? 'normal')) === 'overlay' ? 'overlay' : 'normal',
                'zIndex' => self::clamp($raw['zIndex'] ?? 20, 1, 200, 20),
            ], $border);
        }
        if ($type === 'menu') {
            $orientation = strtolower((string) ($raw['orientation'] ?? 'horizontal'));
            if (!in_array($orientation, ['horizontal', 'vertical'], true)) { $orientation = 'horizontal'; }
            $align = strtolower((string) ($raw['align'] ?? 'right'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'right'; }
            $mobileMode = strtolower((string) ($raw['mobileMode'] ?? 'hamburger'));
            if (!in_array($mobileMode, ['hamburger', 'vertical', 'wrap'], true)) { $mobileMode = 'hamburger'; }
            $mobilePresentation = strtolower((string) ($raw['mobilePresentation'] ?? 'dropdown'));
            if (!in_array($mobilePresentation, ['dropdown', 'panel-right', 'panel-left'], true)) { $mobilePresentation = 'dropdown'; }
            return array_merge([
                'menuId' => absint($raw['menuId'] ?? 0),
                'orientation' => $orientation,
                'align' => $align,
                'mobileMode' => $mobileMode,
                'mobilePresentation' => $mobilePresentation,
                'mobileCloseOnSelect' => array_key_exists('mobileCloseOnSelect', $raw) ? (bool) $raw['mobileCloseOnSelect'] : true,
                'mobileCloseOutside' => array_key_exists('mobileCloseOutside', $raw) ? (bool) $raw['mobileCloseOutside'] : true,
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#ffffff')) ?: '#ffffff',
                'hoverTextColor' => sanitize_hex_color((string) ($raw['hoverTextColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'activeTextColor' => sanitize_hex_color((string) ($raw['activeTextColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#30382a')) ?: '#30382a',
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $raw) ? (bool) $raw['backgroundTransparent'] : true,
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 64, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 600, 100, 900, 600),
                'menuGap' => self::clamp($raw['menuGap'] ?? 24, 0, 120, 24),
                'paddingX' => self::clamp($raw['paddingX'] ?? 8, 0, 120, 8),
                'paddingY' => self::clamp($raw['paddingY'] ?? 8, 0, 120, 8),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
            ], $border);
        }
        if ($type === 'image') {
            $fit = strtolower((string) ($raw['fit'] ?? 'contain'));
            if (!in_array($fit, ['cover', 'contain', 'original', 'stretch', 'manual'], true)) {
                $fit = 'contain';
            }
            $alignX = strtolower((string) ($raw['imageAlignX'] ?? 'center'));
            if (!in_array($alignX, ['left', 'center', 'right'], true)) {
                $alignX = 'center';
            }
            $alignY = strtolower((string) ($raw['imageAlignY'] ?? 'center'));
            if (!in_array($alignY, ['top', 'center', 'bottom'], true)) {
                $alignY = 'center';
            }
            return array_merge([
                'mediaId' => absint($raw['mediaId'] ?? 0),
                'url' => esc_url_raw((string) ($raw['url'] ?? '')),
                'alt' => sanitize_text_field((string) ($raw['alt'] ?? '')),
                'fit' => $fit,
                'imageAlignX' => $alignX,
                'imageAlignY' => $alignY,
                'boxBackground' => sanitize_hex_color((string) ($raw['boxBackground'] ?? '#ffffff')) ?: '#ffffff',
                'boxTransparent' => array_key_exists('boxTransparent', $raw) ? (bool) $raw['boxTransparent'] : true,
                'focalX' => self::clamp($raw['focalX'] ?? 50, 0, 100, 50),
                'focalY' => self::clamp($raw['focalY'] ?? 50, 0, 100, 50),
                'manualX' => self::clamp($raw['manualX'] ?? 0, -4000, 4000, 0),
                'manualY' => self::clamp($raw['manualY'] ?? 0, -4000, 4000, 0),
                'manualW' => self::clamp($raw['manualW'] ?? 320, 1, 4000, 320),
                'manualH' => self::clamp($raw['manualH'] ?? 240, 1, 4000, 240),
                'lockAspect' => array_key_exists('lockAspect', $raw) ? (bool) $raw['lockAspect'] : true,
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
            'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
            'gapX' => self::clamp($raw['gapX'] ?? 0, 0, 200, 0),
            'gapY' => self::clamp($raw['gapY'] ?? 0, 0, 200, 0),
            'offsetX' => self::clamp($raw['offsetX'] ?? 0, -2000, 2000, 0),
            'offsetY' => self::clamp($raw['offsetY'] ?? 0, -2000, 2000, 0),
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
    private static function fontToken($value, bool $heading): string
    {
        $token = sanitize_key((string) $value);
        if ($heading && $token === 'body') {
            return 'body';
        }
        return in_array($token, ['system', 'arial', 'verdana', 'tahoma', 'trebuchet', 'georgia', 'times', 'courier'], true) ? $token : 'system';
    }

    /** @param mixed $value */
    private static function clampFloat($value, float $min, float $max, float $fallback): float
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (float) $value));
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
