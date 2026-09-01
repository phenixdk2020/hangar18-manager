<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class FormPageProvisioner
{
    public static function register(): void
    {
        add_action('admin_init', [self::class, 'ensurePages'], 40);
    }

    public static function ensurePages(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        self::ensurePage('kontakt', 'Kontakt', 'contactform');
        self::ensurePage('bliv-medlem', 'Bliv medlem', 'membershipform');
    }

    private static function ensurePage(string $slug, string $title, string $formType): void
    {
        $page = get_page_by_path($slug, OBJECT, 'page');
        $postId = $page instanceof \WP_Post ? (int) $page->ID : 0;

        if ($postId <= 0) {
            $created = wp_insert_post([
                'post_type' => 'page',
                'post_status' => current_user_can('publish_pages') ? 'publish' : 'draft',
                'post_title' => $title,
                'post_name' => $slug,
                'post_content' => '',
            ], true);
            if (is_wp_error($created) || (int) $created <= 0) {
                return;
            }
            $postId = (int) $created;
        }

        $model = LayoutModel::get($postId);
        foreach ($model['nodes'] ?? [] as $node) {
            if (is_array($node) && (string) ($node['type'] ?? '') === $formType) {
                return;
            }
        }

        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        $rootBottom = 0;
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['parentId'] ?? '') !== '') {
                continue;
            }
            $desktop = isset($node['geometry']['desktop']) && is_array($node['geometry']['desktop']) ? $node['geometry']['desktop'] : [];
            $y = max(0, (int) ($desktop['y'] ?? 0));
            $h = max(1, (int) ($desktop['h'] ?? 1));
            $rootBottom = max($rootBottom, $y + $h);
        }

        $membership = $formType === 'membershipform';
        $sectionY = $rootBottom > 0 ? $rootBottom + 4 : 0;
        $sectionH = $membership ? 84 : 64;
        $formH = $membership ? 74 : 54;
        $suffix = substr(hash('sha256', $slug . ':' . $postId), 0, 8);
        $sectionId = 'section-v0175-' . sanitize_key($slug) . '-' . $suffix;
        $formId = 'form-v0175-' . sanitize_key($slug) . '-' . $suffix;
        $orderBase = (count($nodes) + 1) * 10;

        $nodes[] = [
            'id' => $sectionId,
            'type' => 'section',
            'parentId' => '',
            'order' => $orderBase,
            'geometry' => [
                'desktop' => ['x' => 0, 'y' => $sectionY, 'w' => 120, 'h' => $sectionH],
            ],
            'props' => [
                'backgroundTransparent' => true,
                'background' => '#ffffff',
                'padding' => 0,
                'radius' => 0,
            ],
        ];
        $nodes[] = [
            'id' => $formId,
            'type' => $formType,
            'parentId' => $sectionId,
            'order' => $orderBase + 10,
            'geometry' => [
                'desktop' => ['x' => 6, 'y' => 4, 'w' => 108, 'h' => $formH],
            ],
            'props' => [
                'heading' => $membership ? 'Bliv medlem' : 'Kontakt os',
                'intro' => $membership
                    ? 'Udfyld formularen, så kontakter vi dig om medlemskab.'
                    : 'Har du spørgsmål, er du velkommen til at kontakte os.',
                'buttonText' => $membership ? 'Send indmeldelse' : 'Send besked',
                'background' => '#f4f1e8',
                'fieldBackground' => '#ffffff',
                'textColor' => '#30382a',
                'accentColor' => '#30382a',
                'padding' => 24,
                'radius' => 6,
                'showPhone' => true,
                'requireConsent' => true,
            ],
        ];

        try {
            LayoutModel::saveVersion(
                $postId,
                [
                    'schemaVersion' => LayoutModel::SCHEMA,
                    'units' => LayoutModel::UNITS,
                    'rowPx' => LayoutModel::ROW_PX,
                    'nodes' => $nodes,
                ],
                get_current_user_id(),
                'v0.1.75: tilføj ' . ($membership ? 'Bliv medlem-formular' : 'Kontaktformular')
            );
            clean_post_cache($postId);
        } catch (\Throwable $error) {
            // Retry on the next admin request; never break wp-admin.
        }
    }

    private function __construct()
    {
    }
}
