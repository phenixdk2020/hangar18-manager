<?php

declare(strict_types=1);

namespace VisualDesignerManager\Model;

use VisualDesignerManager\Icons\IconRegistry;
use VisualDesignerManager\Modules\ModuleBinding;

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
            if (!in_array($type, ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'eventvalue', 'eventimage', 'eventfacts', 'gallerylist', 'gallerydetail', 'eventfield', 'contactform', 'membershipform'], true)) {
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
            if (!in_array($headingLevel, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], true)) {
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
        if ($type === 'spacer') {
            return $border;
        }
        if ($type === 'divider') {
            $orientation = strtolower((string) ($raw['orientation'] ?? 'horizontal'));
            if (!in_array($orientation, ['horizontal', 'vertical'], true)) { $orientation = 'horizontal'; }
            $lineStyle = strtolower((string) ($raw['lineStyle'] ?? 'solid'));
            if (!in_array($lineStyle, ['solid', 'dashed', 'dotted'], true)) { $lineStyle = 'solid'; }
            return array_merge([
                'orientation' => $orientation,
                'lineColor' => sanitize_hex_color((string) ($raw['lineColor'] ?? '#c3c4c7')) ?: '#c3c4c7',
                'lineWidth' => self::clamp($raw['lineWidth'] ?? 1, 1, 20, 1),
                'lineStyle' => $lineStyle,
            ], $border);
        }
        if ($type === 'icon') {
            $align = strtolower((string) ($raw['align'] ?? 'center'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'center'; }
            $selection = IconRegistry::normalizeSelection((string) ($raw['iconSet'] ?? 'core'), (string) ($raw['icon'] ?? 'star'));
            return array_merge([
                'iconSet' => $selection['set'],
                'icon' => $selection['icon'],
                'iconSize' => self::clamp($raw['iconSize'] ?? 32, 8, 240, 32),
                'iconColor' => sanitize_hex_color((string) ($raw['iconColor'] ?? '#30382a')) ?: '#30382a',
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $raw) ? (bool) $raw['backgroundTransparent'] : true,
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
                'align' => $align,
            ], $border);
        }
        if ($type === 'badge') {
            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'left'; }
            return array_merge([
                'text' => sanitize_text_field((string) ($raw['text'] ?? 'Badge')),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#c3ae83')) ?: '#c3ae83',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 13, 8, 80, 13),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 700, 100, 900, 700),
                'paddingX' => self::clamp($raw['paddingX'] ?? 12, 0, 120, 12),
                'paddingY' => self::clamp($raw['paddingY'] ?? 5, 0, 120, 5),
                'radius' => self::clamp($raw['radius'] ?? 20, 0, 100, 20),
                'align' => $align,
            ], $border);
        }
        if ($type === 'link') {
            $linkType = strtolower((string) ($raw['linkType'] ?? 'url'));
            if (!in_array($linkType, ['page', 'url', 'anchor', 'email', 'phone'], true)) { $linkType = 'url'; }
            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'left'; }
            return array_merge([
                'text' => sanitize_text_field((string) ($raw['text'] ?? 'Læs mere →')),
                'linkType' => $linkType,
                'pageId' => absint($raw['pageId'] ?? 0),
                'url' => sanitize_text_field((string) ($raw['url'] ?? '')),
                'targetBlank' => !empty($raw['targetBlank']),
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#2271b1')) ?: '#2271b1',
                'hoverTextColor' => sanitize_hex_color((string) ($raw['hoverTextColor'] ?? '#135e96')) ?: '#135e96',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 600, 100, 900, 600),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.3, 0.8, 3.0, 1.3),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'underline' => array_key_exists('underline', $raw) ? (bool) $raw['underline'] : false,
                'align' => $align,
            ], $border);
        }
        if ($type === 'datalist') {
            $layout = strtolower((string) ($raw['layout'] ?? 'rows'));
            if (!in_array($layout, ['rows', 'stacked'], true)) { $layout = 'rows'; }
            return array_merge([
                'rows' => self::pairRows($raw['rows'] ?? []),
                'layout' => $layout,
                'labelWidth' => self::clamp($raw['labelWidth'] ?? 40, 15, 80, 40),
                'cellPadding' => self::clamp($raw['cellPadding'] ?? 8, 0, 60, 8),
                'showDividers' => array_key_exists('showDividers', $raw) ? (bool) $raw['showDividers'] : true,
                'zebra' => !empty($raw['zebra']),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'zebraBackground' => sanitize_hex_color((string) ($raw['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7',
                'lineColor' => sanitize_hex_color((string) ($raw['lineColor'] ?? '#dcdcde')) ?: '#dcdcde',
                'labelColor' => sanitize_hex_color((string) ($raw['labelColor'] ?? '#30382a')) ?: '#30382a',
                'valueColor' => sanitize_hex_color((string) ($raw['valueColor'] ?? '#30382a')) ?: '#30382a',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 15, 8, 80, 15),
                'labelWeight' => self::clamp($raw['labelWeight'] ?? 600, 100, 900, 600),
                'valueWeight' => self::clamp($raw['valueWeight'] ?? 400, 100, 900, 400),
            ], $border);
        }
        if ($type === 'table') {
            $headers = self::stringList($raw['headers'] ?? [], 12, ['Kolonne 1', 'Kolonne 2', 'Kolonne 3']);
            $mobileMode = strtolower((string) ($raw['mobileMode'] ?? 'scroll'));
            if (!in_array($mobileMode, ['scroll', 'cards'], true)) { $mobileMode = 'scroll'; }
            return array_merge([
                'headers' => $headers,
                'rows' => self::matrixRows($raw['rows'] ?? [], count($headers), 50),
                'headerBackground' => sanitize_hex_color((string) ($raw['headerBackground'] ?? '#30382a')) ?: '#30382a',
                'headerTextColor' => sanitize_hex_color((string) ($raw['headerTextColor'] ?? '#ffffff')) ?: '#ffffff',
                'cellBackground' => sanitize_hex_color((string) ($raw['cellBackground'] ?? '#ffffff')) ?: '#ffffff',
                'cellTextColor' => sanitize_hex_color((string) ($raw['cellTextColor'] ?? '#30382a')) ?: '#30382a',
                'zebra' => array_key_exists('zebra', $raw) ? (bool) $raw['zebra'] : true,
                'zebraBackground' => sanitize_hex_color((string) ($raw['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7',
                'cellBorderColor' => sanitize_hex_color((string) ($raw['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde',
                'cellBorderWidth' => self::clamp($raw['cellBorderWidth'] ?? 1, 0, 10, 1),
                'cellBorderStyle' => self::lineStyle($raw['cellBorderStyle'] ?? 'solid'),
                'borderMode' => self::tableBorderMode($raw['borderMode'] ?? 'all'),
                'cellBorders' => self::tableCellBorders($raw['cellBorders'] ?? []),
                'cellPadding' => self::clamp($raw['cellPadding'] ?? 8, 0, 60, 8),
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 14, 8, 80, 14),
                'headerWeight' => self::clamp($raw['headerWeight'] ?? 700, 100, 900, 700),
                'mobileMode' => $mobileMode,
            ], $border);
        }
        if ($type === 'vehiclelist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'sortOrder'), ['sortOrder', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'sortOrder') : 'sortOrder';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $binding = ModuleBinding::normalize([
                'mode' => 'module', 'module' => 'vehicles', 'view' => 'list',
                'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit],
            ]);
            return array_merge([
                'binding' => $binding,
                'limit' => $limit,
                'orderBy' => $orderBy,
                'order' => $order,
                'detailPageId' => absint($raw['detailPageId'] ?? 0),
                'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3),
                'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18),
                'cardPadding' => self::clamp($raw['cardPadding'] ?? 12, 0, 60, 12),
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 180, 60, 600, 180),
                'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true,
                'showCategory' => array_key_exists('showCategory', $raw) ? (bool) $raw['showCategory'] : true,
                'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true,
                'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true,
                'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'cardRadius' => self::clamp($raw['cardRadius'] ?? 4, 0, 60, 4),
            ], $border);
        }
        if ($type === 'vehicledetail') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'vehicles', 'view' => 'detail', 'recordId' => $recordId]);
            return array_merge([
                'binding' => $binding,
                'recordId' => $recordId,
                'showGallery' => array_key_exists('showGallery', $raw) ? (bool) $raw['showGallery'] : true,
                'showCategory' => array_key_exists('showCategory', $raw) ? (bool) $raw['showCategory'] : true,
                'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true,
                'showDescription' => array_key_exists('showDescription', $raw) ? (bool) $raw['showDescription'] : true,
                'showAttributes' => array_key_exists('showAttributes', $raw) ? (bool) $raw['showAttributes'] : true,
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 900, 360),
                'labelWidth' => self::clamp($raw['labelWidth'] ?? 34, 20, 60, 34),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'padding' => self::clamp($raw['padding'] ?? 16, 0, 80, 16),
                'radius' => self::clamp($raw['radius'] ?? 4, 0, 60, 4),
            ], $border);
        }
        if ($type === 'eventlist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'start'), ['start', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'start') : 'start';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $dateFilter = in_array((string) ($raw['dateFilter'] ?? 'upcoming'), ['all', 'upcoming', 'past'], true) ? (string) ($raw['dateFilter'] ?? 'upcoming') : 'upcoming';
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'events', 'view' => 'list', 'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit]]);
            return array_merge(['binding' => $binding, 'limit' => $limit, 'orderBy' => $orderBy, 'order' => $order, 'dateFilter' => $dateFilter, 'detailPageId' => absint($raw['detailPageId'] ?? 0), 'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3), 'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18), 'cardPadding' => self::clamp($raw['cardPadding'] ?? 12, 0, 60, 12), 'imageHeight' => self::clamp($raw['imageHeight'] ?? 180, 60, 600, 180), 'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true, 'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true, 'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true, 'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true, 'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true, 'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'cardRadius' => self::clamp($raw['cardRadius'] ?? 4, 0, 60, 4)], $border);
        }
        if ($type === 'eventdetail') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? ''))); if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'events', 'view' => 'detail', 'recordId' => $recordId]);
            return array_merge(['binding' => $binding, 'recordId' => $recordId, 'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true, 'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true, 'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true, 'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true, 'showDescription' => array_key_exists('showDescription', $raw) ? (bool) $raw['showDescription'] : true, 'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 900, 360), 'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'padding' => self::clamp($raw['padding'] ?? 16, 0, 80, 16), 'radius' => self::clamp($raw['radius'] ?? 4, 0, 60, 4)], $border);
        }

        if ($type === 'eventvalue') {
            $valueKey = strtolower((string) ($raw['valueKey'] ?? 'title'));
            if (!in_array($valueKey, ['title','date','location','summary','description'], true)) { $valueKey = 'title'; }
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $tag = strtolower((string) ($raw['tag'] ?? ($valueKey === 'title' ? 'h1' : ($valueKey === 'description' ? 'div' : 'p'))));
            if (!in_array($tag, ['div','p','h1','h2','h3','h4','h5','h6'], true)) { $tag = 'div'; }
            return array_merge([
                'valueKey' => $valueKey,
                'recordId' => $recordId,
                'tag' => $tag,
                'align' => in_array((string) ($raw['align'] ?? 'left'), ['left','center','right'], true) ? (string) $raw['align'] : 'left',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? ($valueKey === 'title' ? 44 : 16), 8, 160, $valueKey === 'title' ? 44 : 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? ($valueKey === 'title' || $valueKey === 'summary' ? 700 : 400), 100, 900, $valueKey === 'title' || $valueKey === 'summary' ? 700 : 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? ($valueKey === 'title' ? 1.1 : 1.5), 0.8, 3.0, $valueKey === 'title' ? 1.1 : 1.5),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $raw) ? (bool) $raw['backgroundTransparent'] : true,
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
            ], $border);
        }
        if ($type === 'eventimage') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $fit = strtolower((string) ($raw['fit'] ?? 'cover'));
            if (!in_array($fit, ['cover','contain'], true)) { $fit = 'cover'; }
            return array_merge([
                'recordId' => $recordId,
                'fit' => $fit,
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 1000, 360),
                'focalX' => self::clamp($raw['focalX'] ?? 50, 0, 100, 50),
                'focalY' => self::clamp($raw['focalY'] ?? 50, 0, 100, 50),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'radius' => self::clamp($raw['radius'] ?? 4, 0, 100, 4),
            ], $border);
        }

        if ($type === 'eventfacts') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            return array_merge([
                'recordId' => $recordId,
                'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true,
                'showTime' => array_key_exists('showTime', $raw) ? (bool) $raw['showTime'] : true,
                'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true,
                'showAddress' => array_key_exists('showAddress', $raw) ? (bool) $raw['showAddress'] : true,
                'showContact' => array_key_exists('showContact', $raw) ? (bool) $raw['showContact'] : true,
                'gap' => self::clamp($raw['gap'] ?? 12, 0, 80, 12),
                'minCardWidth' => self::clamp($raw['minCardWidth'] ?? 150, 100, 360, 150),
                'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#f4f1e8')) ?: '#f4f1e8',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'labelColor' => sanitize_hex_color((string) ($raw['labelColor'] ?? '#30382a')) ?: '#30382a',
                'valueColor' => sanitize_hex_color((string) ($raw['valueColor'] ?? '#30382a')) ?: '#30382a',
                'paddingX' => self::clamp($raw['paddingX'] ?? 16, 0, 80, 16),
                'paddingY' => self::clamp($raw['paddingY'] ?? 16, 0, 80, 16),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 60, 0),
                'labelFontFamily' => self::fontToken($raw['labelFontFamily'] ?? 'system', false),
                'labelFontSize' => self::clamp($raw['labelFontSize'] ?? 16, 8, 80, 16),
                'labelFontWeight' => self::clamp($raw['labelFontWeight'] ?? 700, 100, 900, 700),
                'valueFontFamily' => self::fontToken($raw['valueFontFamily'] ?? 'system', false),
                'valueFontSize' => self::clamp($raw['valueFontSize'] ?? 16, 8, 80, 16),
                'valueFontWeight' => self::clamp($raw['valueFontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.35, 0.8, 3.0, 1.35),
            ], $border);
        }

        if ($type === 'eventfield') {
            $fieldKey = sanitize_key((string) ($raw['fieldKey'] ?? 'about'));
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            return array_merge([
                'fieldKey' => $fieldKey !== '' ? $fieldKey : 'about',
                'recordId' => $recordId,
                'showHeading' => array_key_exists('showHeading', $raw) ? (bool) $raw['showHeading'] : true,
                'showWhenEmpty' => array_key_exists('showWhenEmpty', $raw) ? (bool) $raw['showWhenEmpty'] : false,
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '')) ?: '',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.5, 0.8, 3.0, 1.5),
                'headingColor' => sanitize_hex_color((string) ($raw['headingColor'] ?? '#30382a')) ?: '#30382a',
                'headingFontFamily' => self::fontToken($raw['headingFontFamily'] ?? 'body', true),
                'headingFontSize' => self::clamp($raw['headingFontSize'] ?? 40, 8, 160, 40),
                'headingFontWeight' => self::clamp($raw['headingFontWeight'] ?? 400, 100, 900, 400),
                'headingLineHeight' => self::clampFloat($raw['headingLineHeight'] ?? 1.15, 0.8, 3.0, 1.15),
                'headingGap' => self::clamp($raw['headingGap'] ?? 12, 0, 80, 12),
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 80, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 60, 0),
            ], $border);
        }
        if ($type === 'gallerylist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'sortOrder'), ['sortOrder', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'sortOrder') : 'sortOrder';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'galleries', 'view' => 'list', 'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit]]);
            return array_merge(['binding' => $binding, 'limit' => $limit, 'orderBy' => $orderBy, 'order' => $order, 'detailPageId' => absint($raw['detailPageId'] ?? 0), 'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3), 'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18), 'cardPadding' => self::clamp($raw['cardPadding'] ?? 12, 0, 60, 12), 'imageHeight' => self::clamp($raw['imageHeight'] ?? 220, 80, 600, 220), 'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true, 'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true, 'showCount' => array_key_exists('showCount', $raw) ? (bool) $raw['showCount'] : true, 'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true, 'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'cardRadius' => self::clamp($raw['cardRadius'] ?? 4, 0, 60, 4)], $border);
        }
        if ($type === 'gallerydetail') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? ''))); if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'galleries', 'view' => 'detail', 'recordId' => $recordId]);
            return array_merge(['binding' => $binding, 'recordId' => $recordId, 'showDescription' => array_key_exists('showDescription', $raw) ? (bool) $raw['showDescription'] : true, 'columns' => self::clamp($raw['columns'] ?? 4, 1, 6, 4), 'gap' => self::clamp($raw['gap'] ?? 12, 0, 80, 12), 'imageHeight' => self::clamp($raw['imageHeight'] ?? 220, 80, 700, 220), 'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'padding' => self::clamp($raw['padding'] ?? 16, 0, 80, 16), 'radius' => self::clamp($raw['radius'] ?? 4, 0, 60, 4)], $border);
        }

        if (in_array($type, ['contactform', 'membershipform'], true)) {
            $membership = $type === 'membershipform';
            return array_merge([
                'heading' => sanitize_text_field((string) ($raw['heading'] ?? ($membership ? 'Bliv medlem' : 'Kontakt os'))),
                'intro' => sanitize_textarea_field((string) ($raw['intro'] ?? ($membership ? 'Udfyld formularen, så kontakter vi dig om medlemskab.' : 'Har du spørgsmål, er du velkommen til at kontakte os.'))),
                'buttonText' => sanitize_text_field((string) ($raw['buttonText'] ?? ($membership ? 'Send indmeldelse' : 'Send besked'))),
                'recipient' => sanitize_email((string) ($raw['recipient'] ?? '')),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#f4f1e8')) ?: '#f4f1e8',
                'fieldBackground' => sanitize_hex_color((string) ($raw['fieldBackground'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#30382a')) ?: '#30382a',
                'padding' => self::clamp($raw['padding'] ?? 24, 0, 80, 24),
                'radius' => self::clamp($raw['radius'] ?? 6, 0, 60, 6),
                'showPhone' => array_key_exists('showPhone', $raw) ? (bool) $raw['showPhone'] : true,
                'requireConsent' => array_key_exists('requireConsent', $raw) ? (bool) $raw['requireConsent'] : true,
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
                'moduleSlot' => in_array((string) ($raw['moduleSlot'] ?? 'before'), ['before','between','after'], true) ? (string) ($raw['moduleSlot'] ?? 'before') : 'before',
            ], $border);
        }
        return $border;
    }

    /** @param mixed $value @return array<int,array{label:string,value:string}> */
    private static function pairRows($value): array
    {
        $source = is_array($value) ? array_values($value) : [];
        $rows = [];
        foreach (array_slice($source, 0, 50) as $row) {
            if (!is_array($row)) { continue; }
            $label = sanitize_text_field((string) ($row['label'] ?? ''));
            $cellValue = sanitize_text_field((string) ($row['value'] ?? ''));
            if ($label === '' && $cellValue === '') { continue; }
            $rows[] = ['label' => $label, 'value' => $cellValue];
        }
        return $rows ?: [
            ['label' => 'Felt', 'value' => 'Værdi'],
            ['label' => 'Eksempel', 'value' => 'Indhold'],
        ];
    }

    /** @param mixed $value @param array<int,string> $fallback @return array<int,string> */
    private static function stringList($value, int $max, array $fallback): array
    {
        $source = is_array($value) ? array_values($value) : [];
        $out = [];
        foreach (array_slice($source, 0, max(1, $max)) as $item) {
            $cell = sanitize_text_field((string) $item);
            if ($cell !== '') { $out[] = $cell; }
        }
        return $out ?: $fallback;
    }

    /** @param mixed $value @return array<int,array<int,string>> */
    private static function matrixRows($value, int $columns, int $maxRows): array
    {
        $columns = max(1, min(12, $columns));
        $source = is_array($value) ? array_values($value) : [];
        $out = [];
        foreach (array_slice($source, 0, max(1, $maxRows)) as $row) {
            if (!is_array($row)) { continue; }
            $cells = [];
            for ($i = 0; $i < $columns; $i++) {
                $cells[] = sanitize_text_field((string) ($row[$i] ?? ''));
            }
            if (implode('', $cells) !== '') { $out[] = $cells; }
        }
        if (!$out) {
            $sample1 = array_fill(0, $columns, '');
            $sample2 = array_fill(0, $columns, '');
            $sample1[0] = 'Række 1';
            $sample2[0] = 'Række 2';
            if ($columns > 1) { $sample1[1] = 'Værdi'; $sample2[1] = 'Værdi'; }
            $out = [$sample1, $sample2];
        }
        return $out;
    }

    /** @param mixed $value */
    private static function lineStyle($value): string
    {
        $style = strtolower((string) $value);
        return in_array($style, ['solid', 'dashed', 'dotted'], true) ? $style : 'solid';
    }

    /** @param mixed $value */
    private static function tableBorderMode($value): string
    {
        $mode = strtolower((string) $value);
        return in_array($mode, ['all', 'outer', 'inner', 'none'], true) ? $mode : 'all';
    }

    /** @param mixed $value @return array<string,array<string,array<string,mixed>>> */
    private static function tableCellBorders($value): array
    {
        if (!is_array($value)) { return []; }
        $out = [];
        $count = 0;
        foreach ($value as $key => $cell) {
            if ($count >= 700 || !is_array($cell)) { break; }
            $key = (string) $key;
            if (!preg_match('/^(?:h\d+|r\d+c\d+)$/', $key)) { continue; }
            foreach (['top', 'right', 'bottom', 'left'] as $side) {
                if (!array_key_exists($side, $cell) || !is_array($cell[$side])) { continue; }
                $raw = $cell[$side];
                $out[$key][$side] = [
                    'enabled' => array_key_exists('enabled', $raw) ? (bool) $raw['enabled'] : true,
                    'width' => self::clamp($raw['width'] ?? 1, 0, 10, 1),
                    'color' => sanitize_hex_color((string) ($raw['color'] ?? '#dcdcde')) ?: '#dcdcde',
                    'style' => self::lineStyle($raw['style'] ?? 'solid'),
                ];
            }
            if (isset($out[$key])) { $count++; }
        }
        return $out;
    }

    /** @param mixed $value */
    private static function iconToken($value): string
    {
        return IconRegistry::normalizeSelection('core', (string) $value)['icon'];
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
