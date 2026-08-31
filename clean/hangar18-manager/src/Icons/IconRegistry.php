<?php

declare(strict_types=1);

namespace VisualDesignerManager\Icons;

final class IconRegistry
{
    public const MODULE_FILTER = 'visual_designer_manager_module_icon_sets';
    public const CUSTOM_FILTER = 'visual_designer_manager_custom_icon_sets';

    /** @return array<int,array<string,mixed>> */
    public static function sets(): array
    {
        $sets = [self::coreSet()];
        $sets = array_merge($sets, self::normalizeExternalSets(apply_filters(self::MODULE_FILTER, []), 'module'));
        $sets = array_merge($sets, self::normalizeExternalSets(apply_filters(self::CUSTOM_FILTER, []), 'custom'));
        return $sets;
    }

    /** @return array{set:string,icon:string} */
    public static function normalizeSelection(string $set, string $icon): array
    {
        $set = sanitize_key($set) ?: 'core';
        $icon = sanitize_key($icon) ?: 'star';
        foreach (self::sets() as $candidate) {
            if ((string) ($candidate['key'] ?? '') !== $set) {
                continue;
            }
            foreach ((array) ($candidate['categories'] ?? []) as $category) {
                foreach ((array) ($category['icons'] ?? []) as $entry) {
                    if ((string) ($entry['key'] ?? '') === $icon) {
                        return ['set' => $set, 'icon' => $icon];
                    }
                }
            }
        }

        // Legacy compatibility: v0.1.65 stored only the icon token.
        foreach ((array) (self::coreSet()['categories'] ?? []) as $category) {
            foreach ((array) ($category['icons'] ?? []) as $entry) {
                if ((string) ($entry['key'] ?? '') === $icon) {
                    return ['set' => 'core', 'icon' => $icon];
                }
            }
        }
        return ['set' => 'core', 'icon' => 'star'];
    }

    public static function svg(string $set, string $icon): string
    {
        $selection = self::normalizeSelection($set, $icon);
        foreach (self::sets() as $candidate) {
            if ((string) ($candidate['key'] ?? '') !== $selection['set']) {
                continue;
            }
            foreach ((array) ($candidate['categories'] ?? []) as $category) {
                foreach ((array) ($category['icons'] ?? []) as $entry) {
                    if ((string) ($entry['key'] ?? '') === $selection['icon']) {
                        return self::wrapSvg((string) ($entry['shape'] ?? ''));
                    }
                }
            }
        }
        return self::wrapSvg('<polygon points="12 2.7 14.8 8.4 21 9.3 16.5 13.7 17.6 20 12 17 6.4 20 7.5 13.7 3 9.3 9.2 8.4 12 2.7"/>');
    }

    /** @return array<string,mixed> */
    public static function editorCatalog(): array
    {
        $sets = self::sets();
        foreach ($sets as &$set) {
            foreach ($set['categories'] as &$category) {
                foreach ($category['icons'] as &$icon) {
                    $icon['svg'] = self::wrapSvg((string) ($icon['shape'] ?? ''));
                    unset($icon['shape']);
                }
                unset($icon);
            }
            unset($category);
        }
        unset($set);
        return [
            'sources' => ['core', 'module', 'custom'],
            'customUploadEnabled' => false,
            'sets' => $sets,
        ];
    }

    /** @return array<string,mixed> */
    private static function coreSet(): array
    {
        return [
            'key' => 'core',
            'label' => 'Core icons',
            'source' => 'core',
            'categories' => [
                self::category('general', 'Generelt', [
                    self::icon('star', 'Stjerne', '<polygon points="12 2.7 14.8 8.4 21 9.3 16.5 13.7 17.6 20 12 17 6.4 20 7.5 13.7 3 9.3 9.2 8.4 12 2.7"/>'),
                    self::icon('check', 'Check', '<polyline points="4 12.5 9.5 18 20 6"/>'),
                    self::icon('info', 'Info', '<circle cx="12" cy="12" r="9"/><line x1="12" y1="10.5" x2="12" y2="17"/><line x1="12" y1="7" x2="12.01" y2="7"/>'),
                    self::icon('warning', 'Advarsel', '<path d="M12 3l9 17H3z"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
                    self::icon('plus', 'Plus', '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>'),
                    self::icon('minus', 'Minus', '<line x1="5" y1="12" x2="19" y2="12"/>'),
                    self::icon('close', 'Luk', '<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>'),
                    self::icon('link', 'Link', '<path d="M10 13a5 5 0 007 0l2-2a5 5 0 00-7-7l-1 1"/><path d="M14 11a5 5 0 00-7 0l-2 2a5 5 0 007 7l1-1"/>'),
                    self::icon('external-link', 'Eksternt link', '<path d="M14 4h6v6"/><path d="M20 4l-9 9"/><path d="M18 13v6a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h6"/>'),
                ]),
                self::category('navigation', 'Navigation', [
                    self::icon('arrow-left', 'Pil venstre', '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="11 6 5 12 11 18"/>'),
                    self::icon('arrow-right', 'Pil højre', '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="13 6 19 12 13 18"/>'),
                    self::icon('arrow-up', 'Pil op', '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="6 11 12 5 18 11"/>'),
                    self::icon('arrow-down', 'Pil ned', '<line x1="12" y1="5" x2="12" y2="19"/><polyline points="6 13 12 19 18 13"/>'),
                    self::icon('menu', 'Menu', '<line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/>'),
                ]),
                self::category('contact', 'Kontakt', [
                    self::icon('phone', 'Telefon', '<path d="M6.5 3h3l1.2 5-2.2 1.7a15 15 0 005.8 5.8L16 13.3l5 1.2v3c0 1.4-1.1 2.5-2.5 2.5C10.5 20 4 13.5 4 5.5 4 4.1 5.1 3 6.5 3z"/>'),
                    self::icon('mail', 'E-mail', '<rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="4 7 12 13 20 7"/>'),
                    self::icon('location', 'Placering', '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1116 0z"/><circle cx="12" cy="10" r="2.5"/>'),
                    self::icon('website', 'Website', '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 010 18M12 3a15 15 0 000 18"/>'),
                ]),
                self::category('events', 'Dato og events', [
                    self::icon('calendar', 'Kalender', '<rect x="3" y="5" width="18" height="16" rx="2"/><line x1="7" y1="3" x2="7" y2="7"/><line x1="17" y1="3" x2="17" y2="7"/><line x1="3" y1="10" x2="21" y2="10"/>'),
                    self::icon('clock', 'Ur', '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 16 14"/>'),
                    self::icon('ticket', 'Billet', '<path d="M4 7h16v4a2 2 0 000 4v4H4v-4a2 2 0 000-4z"/><line x1="12" y1="7" x2="12" y2="19"/>'),
                    self::icon('people', 'Personer', '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-4 3-6 6-6s5.2 2 6 6"/><path d="M14 15c3.5-.5 6 1.1 7 4"/>'),
                ]),
                self::category('media', 'Medier', [
                    self::icon('image', 'Billede', '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><polyline points="4 18 10 12 14 16 17 13 20 16"/>'),
                    self::icon('camera', 'Kamera', '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.5-3h5L16 7"/><circle cx="12" cy="13.5" r="3.5"/>'),
                    self::icon('gallery', 'Galleri', '<rect x="5" y="5" width="16" height="14" rx="2"/><path d="M3 16V4a1 1 0 011-1h14"/><circle cx="10" cy="10" r="1.5"/><polyline points="6 17 11 12 14 15 17 12 20 15"/>'),
                    self::icon('play', 'Afspil', '<circle cx="12" cy="12" r="9"/><polygon points="10 8 17 12 10 16"/>'),
                ]),
                self::category('technical', 'Tekniske data', [
                    self::icon('gear', 'Tandhjul', '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>'),
                    self::icon('tools', 'Værktøj', '<path d="M14 6a4 4 0 005 5l-8 8-3-3 8-8a4 4 0 01-2-2z"/><path d="M5 4l4 4-2 2-4-4z"/>'),
                    self::icon('ruler', 'Lineal', '<path d="M4 17L17 4l3 3L7 20z"/><line x1="13" y1="8" x2="16" y2="11"/><line x1="10" y1="11" x2="12" y2="13"/><line x1="7" y1="14" x2="10" y2="17"/>'),
                    self::icon('weight', 'Vægt', '<path d="M6 8h12l2 12H4z"/><path d="M9 8a3 3 0 016 0"/><line x1="12" y1="11" x2="14" y2="14"/>'),
                    self::icon('speed', 'Hastighed', '<path d="M4 18a8 8 0 1116 0"/><line x1="12" y1="14" x2="17" y2="9"/><line x1="7" y1="18" x2="17" y2="18"/>'),
                    self::icon('fuel', 'Brændstof', '<rect x="5" y="3" width="9" height="18" rx="1"/><line x1="7" y1="7" x2="12" y2="7"/><path d="M14 8h2l3 3v7a2 2 0 01-4 0v-4"/>'),
                    self::icon('engine', 'Motor', '<rect x="5" y="7" width="14" height="10" rx="2"/><path d="M8 7V4h7v3M3 10h2M19 10h2M9 17v3M15 17v3"/>'),
                    self::icon('wheel', 'Hjul', '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="3" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="21"/><line x1="3" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="21" y2="12"/>'),
                    self::icon('track', 'Bælte', '<rect x="2.5" y="6" width="19" height="12" rx="6"/><circle cx="7" cy="12" r="2.5"/><circle cx="12" cy="12" r="2.5"/><circle cx="17" cy="12" r="2.5"/>'),
                ]),
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function category(string $key, string $label, array $icons): array
    {
        return ['key' => $key, 'label' => $label, 'icons' => $icons];
    }

    /** @return array<string,string> */
    private static function icon(string $key, string $label, string $shape): array
    {
        return ['key' => $key, 'label' => $label, 'shape' => $shape];
    }

    /** @param mixed $value @return array<int,array<string,mixed>> */
    private static function normalizeExternalSets($value, string $source): array
    {
        if (!is_array($value)) {
            return [];
        }
        $out = [];
        foreach (array_slice(array_values($value), 0, 30) as $set) {
            if (!is_array($set)) { continue; }
            $key = sanitize_key((string) ($set['key'] ?? ''));
            if ($key === '' || $key === 'core') { continue; }
            $categories = [];
            foreach (array_slice((array) ($set['categories'] ?? []), 0, 40) as $category) {
                if (!is_array($category)) { continue; }
                $categoryKey = sanitize_key((string) ($category['key'] ?? ''));
                if ($categoryKey === '') { continue; }
                $icons = [];
                foreach (array_slice((array) ($category['icons'] ?? []), 0, 200) as $icon) {
                    if (!is_array($icon)) { continue; }
                    $iconKey = sanitize_key((string) ($icon['key'] ?? ''));
                    $shape = self::sanitizeShape((string) ($icon['shape'] ?? ''));
                    if ($iconKey === '' || $shape === '') { continue; }
                    $icons[] = [
                        'key' => $iconKey,
                        'label' => sanitize_text_field((string) ($icon['label'] ?? $iconKey)),
                        'shape' => $shape,
                    ];
                }
                if ($icons) {
                    $categories[] = [
                        'key' => $categoryKey,
                        'label' => sanitize_text_field((string) ($category['label'] ?? $categoryKey)),
                        'icons' => $icons,
                    ];
                }
            }
            if ($categories) {
                $out[] = [
                    'key' => $key,
                    'label' => sanitize_text_field((string) ($set['label'] ?? $key)),
                    'source' => $source,
                    'categories' => $categories,
                ];
            }
        }
        return $out;
    }

    private static function wrapSvg(string $shape): string
    {
        $shape = self::sanitizeShape($shape);
        return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' . $shape . '</svg>';
    }

    private static function sanitizeShape(string $shape): string
    {
        return wp_kses($shape, [
            'path' => ['d' => true],
            'circle' => ['cx' => true, 'cy' => true, 'r' => true],
            'rect' => ['x' => true, 'y' => true, 'width' => true, 'height' => true, 'rx' => true, 'ry' => true],
            'line' => ['x1' => true, 'y1' => true, 'x2' => true, 'y2' => true],
            'polyline' => ['points' => true],
            'polygon' => ['points' => true],
        ]);
    }
}
