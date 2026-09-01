<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class SiteDesignHarmonizer
{
    public const CONTRACT = 'VD-SITE-DESIGN-HARMONY-001';
    public const BACKUP_META = '_h18_vd_layout_pre_theme_v0172';
    public const DONE_META = '_h18_vd_theme_harmonized_v0172';
    private const TARGET_SLUGS = ['om-foreningen', 'koeretoejer-og-materiel', 'events', 'billedgalleri', 'bliv-medlem', 'kontakt'];

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'run'], 40);
    }

    public static function run(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        if ($frontId <= 0 || !metadata_exists('post', $frontId, LayoutModel::META)) { return; }
        $home = LayoutModel::get($frontId);
        if (empty($home['nodes']) || !is_array($home['nodes'])) { return; }
        $tokens = self::tokens($home);
        $referenceDigest = LayoutModel::structuralDigest($home);
        foreach (self::TARGET_SLUGS as $slug) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post || (int) $page->ID === $frontId || !metadata_exists('post', (int) $page->ID, LayoutModel::META)) { continue; }
            $postId = (int) $page->ID;
            if (metadata_exists('post', $postId, self::DONE_META)) { continue; }
            self::harmonizePage($postId, $frontId, $referenceDigest, $tokens);
        }
    }

    /** @param array<string,mixed> $tokens */
    private static function harmonizePage(int $postId, int $frontId, string $referenceDigest, array $tokens): void
    {
        $raw = get_post_meta($postId, LayoutModel::META, true);
        if (!is_array($raw)) { return; }
        $before = LayoutModel::normalize($raw);
        $beforeFingerprint = self::layoutFingerprint($before);
        $after = self::applyTokens($before, $tokens);
        $after = LayoutModel::normalize($after);
        if ($beforeFingerprint !== self::layoutFingerprint($after)) {
            return; // Styling may never alter identity, hierarchy, order or geometry.
        }
        $beforeDigest = LayoutModel::structuralDigest($before);
        $afterDigest = LayoutModel::structuralDigest($after);
        if ($beforeDigest === $afterDigest) {
            update_post_meta($postId, self::DONE_META, ['version' => H18_CLEAN_VERSION, 'referencePostId' => $frontId, 'referenceDigest' => $referenceDigest, 'changed' => false]);
            return;
        }

        $oldHistory = get_post_meta($postId, LayoutModel::HISTORY_META, true);
        $oldVersion = get_post_meta($postId, LayoutModel::VERSION_META, true);
        if (!metadata_exists('post', $postId, self::BACKUP_META)) {
            update_post_meta($postId, self::BACKUP_META, ['savedUtc' => gmdate('c'), 'digest' => $beforeDigest, 'model' => $before]);
        }
        try {
            $version = LayoutModel::saveVersion($postId, $after, get_current_user_id(), 'Design harmoniseret med Hjem (v0.1.72)');
            $stored = LayoutModel::get($postId);
            if (self::layoutFingerprint($stored) !== $beforeFingerprint || LayoutModel::structuralDigest($stored) !== $afterDigest) {
                throw new \RuntimeException('Efterkontrol af harmoniseret layout fejlede.');
            }
            update_post_meta($postId, self::DONE_META, [
                'version' => H18_CLEAN_VERSION,
                'designerVersion' => $version,
                'referencePostId' => $frontId,
                'referenceDigest' => $referenceDigest,
                'beforeDigest' => $beforeDigest,
                'afterDigest' => $afterDigest,
                'changed' => true,
            ]);
        } catch (\Throwable $error) {
            update_post_meta($postId, LayoutModel::META, $raw);
            if (metadata_exists('post', $postId, LayoutModel::HISTORY_META)) { update_post_meta($postId, LayoutModel::HISTORY_META, $oldHistory); }
            if (metadata_exists('post', $postId, LayoutModel::VERSION_META)) { update_post_meta($postId, LayoutModel::VERSION_META, $oldVersion); }
            delete_post_meta($postId, self::DONE_META);
        }
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    private static function tokens(array $model): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $sections = [];
        $container = [];
        $text = [];
        $button = [];
        $image = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            $type = (string) ($node['type'] ?? '');
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ($type === 'section' && (string) ($node['parentId'] ?? '') === '') {
                $sections[] = self::pick($props, ['background', 'radius', 'padding', 'borderWidth', 'borderColor']);
            } elseif ($type === 'container' && !$container) {
                $container = self::pick($props, ['background', 'radius', 'padding', 'borderWidth', 'borderColor']);
            } elseif ($type === 'text' && !$text) {
                $text = self::pick($props, ['textColor', 'headingColor', 'fontFamily', 'fontWeight', 'lineHeight', 'letterSpacing', 'headingFontFamily', 'headingFontWeight', 'headingLineHeight', 'headingLetterSpacing']);
            } elseif ($type === 'button' && !$button) {
                $button = self::pick($props, ['background', 'textColor', 'hoverBackground', 'hoverTextColor', 'focusColor', 'fontFamily', 'fontWeight', 'radius', 'borderWidth', 'borderColor']);
            } elseif ($type === 'image' && !$image) {
                $image = self::pick($props, ['radius', 'borderWidth', 'borderColor']);
            }
        }
        if (!$sections) { $sections[] = ['background' => '', 'radius' => 0, 'padding' => 0, 'borderWidth' => 0, 'borderColor' => '#000000']; }
        $paletteText = (string) ($text['textColor'] ?? '#30382a');
        $paletteHeading = (string) ($text['headingColor'] ?? $paletteText);
        $paletteAccent = (string) ($button['focusColor'] ?? '#c3ae83');
        $paletteButton = (string) ($button['background'] ?? '#30382a');
        return ['sections' => $sections, 'container' => $container, 'text' => $text, 'button' => $button, 'image' => $image, 'palette' => ['text' => $paletteText, 'heading' => $paletteHeading, 'accent' => $paletteAccent, 'button' => $paletteButton]];
    }

    /** @param array<string,mixed> $model @param array<string,mixed> $tokens @return array<string,mixed> */
    private static function applyTokens(array $model, array $tokens): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $sectionIndex = 0;
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            $type = (string) ($node['type'] ?? '');
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ($type === 'section' && (string) ($node['parentId'] ?? '') === '') {
                $styles = (array) $tokens['sections'];
                $style = (array) $styles[$sectionIndex % max(1, count($styles))];
                $props = self::mergeStyle($props, $style);
                $sectionIndex++;
            } elseif ($type === 'container') {
                $props = self::mergeStyle($props, (array) ($tokens['container'] ?? []));
            } elseif ($type === 'text') {
                $props = self::mergeStyle($props, (array) ($tokens['text'] ?? []));
            } elseif ($type === 'button') {
                $props = self::mergeStyle($props, (array) ($tokens['button'] ?? []));
            } elseif ($type === 'image') {
                $props = self::mergeStyle($props, (array) ($tokens['image'] ?? []));
            } elseif (in_array($type, ['vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail'], true)) {
                $palette = (array) ($tokens['palette'] ?? []);
                if (array_key_exists('textColor', $props)) { $props['textColor'] = (string) ($palette['text'] ?? $props['textColor']); }
                if (array_key_exists('accentColor', $props)) { $props['accentColor'] = (string) ($palette['accent'] ?? $props['accentColor']); }
                if (array_key_exists('cardBackground', $props) && !empty($tokens['sections'][0]['background'])) { $props['cardBackground'] = (string) $tokens['sections'][0]['background']; }
                if (array_key_exists('background', $props) && !empty($tokens['sections'][0]['background'])) { $props['background'] = (string) $tokens['sections'][0]['background']; }
            }
            $node['props'] = $props;
        }
        unset($node);
        $model['nodes'] = $nodes;
        return $model;
    }

    /** @param array<string,mixed> $source @param array<int,string> $keys @return array<string,mixed> */
    private static function pick(array $source, array $keys): array
    {
        $out = [];
        foreach ($keys as $key) { if (array_key_exists($key, $source)) { $out[$key] = $source[$key]; } }
        return $out;
    }

    /** @param array<string,mixed> $props @param array<string,mixed> $style @return array<string,mixed> */
    private static function mergeStyle(array $props, array $style): array
    {
        foreach ($style as $key => $value) { $props[(string) $key] = $value; }
        return $props;
    }

    /** @param array<string,mixed> $model */
    private static function layoutFingerprint(array $model): string
    {
        $rows = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) { continue; }
            $rows[] = [
                'id' => (string) ($node['id'] ?? ''),
                'type' => (string) ($node['type'] ?? ''),
                'parentId' => (string) ($node['parentId'] ?? ''),
                'order' => (int) ($node['order'] ?? 0),
                'geometry' => $node['geometry'] ?? [],
            ];
        }
        return hash('sha256', (string) wp_json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    }

    private function __construct() {}
}
