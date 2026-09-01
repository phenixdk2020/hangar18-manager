<?php

declare(strict_types=1);

namespace VisualDesignerManager\Model;

final class ModuleDesignModel
{
    public const META = '_h18_vd_module_design_v1';
    public const HISTORY_META = '_h18_vd_module_design_history_v1';
    public const MAX_HISTORY = 50;

    /** @return array<string,mixed> */
    public static function defaults(): array
    {
        return [
            'pageWidth' => 90,
            'columnsDesktop' => 3,
            'columnsTablet' => 2,
            'columnsMobile' => 1,
            'cardGap' => 22,
            'cardMaxWidth' => 0,
            'cardBackground' => '#eee8dc',
            'cardTextColor' => '#30382a',
            'cardPaddingX' => 20,
            'cardPaddingY' => 18,
            'cardRadius' => 6,
            'imageRatio' => '16/9',
            'h1Size' => 44,
            'h2Size' => 31,
            'h3Size' => 21,
            'bodySize' => 16,
            'accentColor' => '#536243',
            'sectionGap' => 44,
        ];
    }

    public static function supports(int $postId): bool
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        return in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true);
    }

    /** @return array<string,mixed> */
    public static function get(int $postId): array
    {
        $raw = get_post_meta($postId, self::META, true);
        return self::normalize(is_array($raw) ? $raw : []);
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public static function normalize(array $raw): array
    {
        $defaults = self::defaults();
        $ratio = (string) ($raw['imageRatio'] ?? $defaults['imageRatio']);
        if (!in_array($ratio, ['16/9', '3/2', '4/3', '1/1'], true)) {
            $ratio = (string) $defaults['imageRatio'];
        }

        return [
            'pageWidth' => self::clamp($raw['pageWidth'] ?? $defaults['pageWidth'], 60, 100, 90),
            'columnsDesktop' => self::clamp($raw['columnsDesktop'] ?? $defaults['columnsDesktop'], 1, 4, 3),
            'columnsTablet' => self::clamp($raw['columnsTablet'] ?? $defaults['columnsTablet'], 1, 3, 2),
            'columnsMobile' => self::clamp($raw['columnsMobile'] ?? $defaults['columnsMobile'], 1, 2, 1),
            'cardGap' => self::clamp($raw['cardGap'] ?? $defaults['cardGap'], 0, 64, 22),
            'cardMaxWidth' => self::clamp($raw['cardMaxWidth'] ?? $defaults['cardMaxWidth'], 0, 900, 0),
            'cardBackground' => self::color($raw['cardBackground'] ?? $defaults['cardBackground'], '#eee8dc'),
            'cardTextColor' => self::color($raw['cardTextColor'] ?? $defaults['cardTextColor'], '#30382a'),
            'cardPaddingX' => self::clamp($raw['cardPaddingX'] ?? $defaults['cardPaddingX'], 0, 64, 20),
            'cardPaddingY' => self::clamp($raw['cardPaddingY'] ?? $defaults['cardPaddingY'], 0, 64, 18),
            'cardRadius' => self::clamp($raw['cardRadius'] ?? $defaults['cardRadius'], 0, 40, 6),
            'imageRatio' => $ratio,
            'h1Size' => self::clamp($raw['h1Size'] ?? $defaults['h1Size'], 24, 72, 44),
            'h2Size' => self::clamp($raw['h2Size'] ?? $defaults['h2Size'], 18, 56, 31),
            'h3Size' => self::clamp($raw['h3Size'] ?? $defaults['h3Size'], 14, 40, 21),
            'bodySize' => self::clamp($raw['bodySize'] ?? $defaults['bodySize'], 12, 24, 16),
            'accentColor' => self::color($raw['accentColor'] ?? $defaults['accentColor'], '#536243'),
            'sectionGap' => self::clamp($raw['sectionGap'] ?? $defaults['sectionGap'], 12, 100, 44),
        ];
    }

    /** @return array<string,mixed> */
    public static function forRender(int $postId): array
    {
        if (
            isset($_GET['h18_vd_module_preview'], $_GET['h18_vd_module_design'])
            && current_user_can('edit_pages')
        ) {
            $json = (string) wp_unslash($_GET['h18_vd_module_design']);
            if ($json !== '' && strlen($json) <= 8192) {
                $decoded = json_decode($json, true);
                if (is_array($decoded)) {
                    return self::normalize($decoded);
                }
            }
        }
        return self::get($postId);
    }

    /** @param array<string,mixed> $design */
    public static function digest(array $design): string
    {
        $json = wp_json_encode(self::normalize($design), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) {
            throw new \RuntimeException('Moduldesign kunne ikke serialiseres.');
        }
        return hash('sha256', $json);
    }

    /** @param array<string,mixed> $design */
    public static function save(int $postId, array $design, int $version): void
    {
        $normalized = self::normalize($design);
        update_post_meta($postId, self::META, $normalized);

        $history = get_post_meta($postId, self::HISTORY_META, true);
        $history = is_array($history) ? array_values(array_filter($history, 'is_array')) : [];
        $history = array_values(array_filter($history, static fn(array $row): bool => (int) ($row['version'] ?? 0) !== $version));
        $history[] = [
            'version' => max(0, $version),
            'savedUtc' => gmdate('c'),
            'digest' => self::digest($normalized),
            'design' => $normalized,
        ];
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }
        update_post_meta($postId, self::HISTORY_META, $history);
    }

    /** @return array<string,mixed>|null */
    public static function historyDesign(int $postId, int $version): ?array
    {
        $history = get_post_meta($postId, self::HISTORY_META, true);
        if (!is_array($history)) {
            return null;
        }
        foreach ($history as $row) {
            if (!is_array($row) || (int) ($row['version'] ?? 0) !== $version || !isset($row['design']) || !is_array($row['design'])) {
                continue;
            }
            return self::normalize($row['design']);
        }
        return null;
    }

    private static function clamp(mixed $value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int) round((float) $value)));
    }

    private static function color(mixed $value, string $fallback): string
    {
        $clean = sanitize_hex_color((string) $value);
        return is_string($clean) && $clean !== '' ? strtolower($clean) : $fallback;
    }

    private function __construct() {}
}
