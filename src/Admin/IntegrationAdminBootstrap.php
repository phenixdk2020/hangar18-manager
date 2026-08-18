<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAssetMetadataRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionMenuRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionSiteTemplateRepository;
use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;

/**
 * Safe admin-only bridge from the legacy plugin shell to the extracted Ultimate Designer services.
 *
 * This class deliberately does NOT register frontend hooks, renderers or migration handlers.
 * It only exposes shadow-mode status/readiness in wp-admin while the legacy frontend remains authoritative.
 */
final class IntegrationAdminBootstrap
{
    public const PAGE_SLUG = 'hangar18-ultimate-designer';

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_menu', [self::class, 'registerMenu'], 30);
    }

    public static function registerMenu(): void
    {
        if (!class_exists('Hangar18_Manager')) {
            return;
        }
        add_submenu_page(
            \Hangar18_Manager::MENU_SLUG,
            'Ultimate Designer',
            'Ultimate Designer',
            'edit_pages',
            self::PAGE_SLUG,
            [self::class, 'render']
        );
    }

    public static function render(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne side.', 'hangar18-manager'));
        }

        $templates = new WordPressOptionSiteTemplateRepository();
        $menus = new WordPressOptionMenuRepository();
        $assets = new WordPressOptionAssetMetadataRepository();
        $readiness = new ReleaseReadiness();

        $allTemplates = $templates->all();
        $headerCount = 0;
        $footerCount = 0;
        foreach ($allTemplates as $template) {
            if (($template['Kind'] ?? '') === 'header') {
                $headerCount++;
            } elseif (($template['Kind'] ?? '') === 'footer') {
                $footerCount++;
            }
        }

        $manual = $readiness->requiredManualEvidence();
        $manualPending = array_keys(array_filter($manual, static fn(bool $passed): bool => !$passed));

        $capabilities = (new CapabilityCatalog())->all();
        $currentCapabilities = [];
        foreach ($capabilities as $capability) {
            if (current_user_can($capability)) {
                $currentCapabilities[] = $capability;
            }
        }

        $assetCount = count($assets->all());
        $menuCount = count($menus->all());
        $globalHeader = $templates->globalAssignment('header');
        $globalFooter = $templates->globalAssignment('footer');

        echo '<div class="wrap h18-admin h18-ud-integration-admin">';
        echo '<h1>Ultimate Designer</h1>';
        echo '<p class="description">Integrationsoverblik i shadow mode. Den nuværende Hangar18-frontend og Vehicle/Event/Gallery er stadig autoritative.</p>';

        echo '<div class="notice notice-info inline"><p><strong>Ingen sidekonvertering:</strong> Denne skærm aktiverer ikke nye renderere, ændrer ikke URLs og overskriver ikke eksisterende sider.</p></div>';

        echo '<div class="h18-ud-status-grid">';
        self::card('Site Builder', sprintf('%d Header · %d Footer · %d Menu', $headerCount, $footerCount, $menuCount), 'Kerne implementeret; frontend-cutover er deaktiveret.');
        self::card('Global assignment (shadow)', 'Header: ' . ($globalHeader ?: 'ingen') . ' · Footer: ' . ($globalFooter ?: 'ingen'), 'Assignments ligger i separat v1-option og påvirker ikke legacy header/footer endnu.');
        self::card('Asset metadata', (string) $assetCount . ' registreret', 'Metadata-lag oven på native WordPress Media IDs.');
        self::card('Permissions', sprintf('%d/%d capabilities på aktuel bruger', count($currentCapabilities), count($capabilities)), 'Legacy edit_pages-gate er fortsat aktiv under migrationen.');
        self::card('Automated QA', 'PHP 8.0 / 8.2 / 8.3 + E14', 'Automatiske gates er implementeret. Manual/live evidence holdes separat.');
        self::card('Manual release gates', (string) count($manualPending) . ' pending', 'Konvertering forbliver blokeret indtil de manuelle/live gates er gennemført.');
        echo '</div>';

        echo '<h2>Integration backlog</h2>';
        echo '<table class="widefat striped h18-ud-backlog"><thead><tr><th>Fase</th><th>Status</th><th>Næste leverance</th></tr></thead><tbody>';
        self::backlogRow('I1', 'Aktiv', 'Admin integration: Site Builder, Side Health, Assets, Permissions, Portability og QA-overblik.');
        self::backlogRow('I2', 'Næste', 'Visuel Header/Footer editor på samme Sections-tree uden frontend-aktivering.');
        self::backlogRow('I3', 'Næste', 'Menu UI v2: presets, off-canvas/fullscreen/mega-panel editor og keyboard-preview.');
        self::backlogRow('I4', 'Næste', 'Side Health-panelet kobles til den eksisterende sideeditor med element-links.');
        self::backlogRow('I5', 'Næste', 'Asset Manager UI: collections/tags/usage/focal point/duplicates/derivatives.');
        self::backlogRow('I6', 'Næste', 'Import/Export UI med dry-run, conflicts, remap og restore-point.');
        self::backlogRow('I7', 'Næste', 'Permissions/Design Lock UI og rolle-installation med migration preview.');
        self::backlogRow('I8', 'Næste', 'AI provider settings + forslagspaneler; stadig accept/undo-gated.');
        self::backlogRow('I9', 'Næste', 'Manual QA dashboard/evidence capture og live-copy rollback rehearsal.');
        self::backlogRow('I10', 'Sidst', 'Kontrolleret konvertering af eksisterende sider og til sidst Vehicle/Event/Gallery.');
        echo '</tbody></table>';

        echo '<h2>Manuelle gates før I10</h2><ul class="ul-disc">';
        foreach ($manualPending as $item) {
            echo '<li><code>' . esc_html($item) . '</code></li>';
        }
        echo '</ul>';

        echo '</div>';
    }

    private static function card(string $title, string $value, string $description): void
    {
        echo '<section class="h18-ud-status-card">';
        echo '<h3>' . esc_html($title) . '</h3>';
        echo '<strong>' . esc_html($value) . '</strong>';
        echo '<p>' . esc_html($description) . '</p>';
        echo '</section>';
    }

    private static function backlogRow(string $phase, string $status, string $description): void
    {
        echo '<tr><td><strong>' . esc_html($phase) . '</strong></td><td>' . esc_html($status) . '</td><td>' . esc_html($description) . '</td></tr>';
    }
}
