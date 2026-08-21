<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Editor\LegoDesignModel;
use Hangar18\UltimateDesigner\Editor\LegoInteractionStateModel;

/**
 * Admin-only companion for v0.8.34 interaction states.
 *
 * Desktop values stay in the legacy section fields. Tablet/Mobile interaction
 * overrides are merged into the existing v0.8.33 responsive Design snapshots;
 * there is deliberately no additional WordPress option or history owner.
 */
final class EditorLegoInteractionStatesAdminController
{
    private static bool $registered = false;
    /** @var array<string,mixed> */
    private static array $previousPage = [];

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_h18_save_page_editor', [self::class, 'preserveBeforeSave'], 4);
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 6);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-interaction-states-v0834.js';
        $guardPath = $pluginDir . '/assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-interaction-states-v0834.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-interaction-states-event-guard-v0834',
            $pluginUrl . 'assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js',
            ['jquery', 'hangar18-ultimate-designer-lego-design-responsive-event-guard-v0833'],
            is_file($guardPath) ? (string) filemtime($guardPath) : '0.8.34',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-interaction-states-v0834',
            $pluginUrl . 'assets/ultimate-designer-lego-interaction-states-v0834.js',
            [
                'jquery',
                'hangar18-ultimate-designer-history-content-v0823',
                'hangar18-ultimate-designer-lego-design-responsive-v0833',
                'hangar18-ultimate-designer-lego-interaction-states-event-guard-v0834',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.34',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-interaction-states-v0834',
            $pluginUrl . 'assets/ultimate-designer-lego-interaction-states-v0834.css',
            ['hangar18-ultimate-designer-lego-design-responsive-v0833'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.34'
        );

        $store = get_option(EditorLegoResponsiveDesignAdminController::OPTION, []);
        wp_localize_script(
            'hangar18-ultimate-designer-lego-interaction-states-v0834',
            'H18LegoInteractionStatesV0834',
            [
                'version' => '0.8.34',
                'schemaVersion' => LegoInteractionStateModel::SCHEMA_VERSION,
                'pages' => is_array($store) ? $store : [],
                'transitionPresets' => LegoDesignModel::transitionPresets(),
                'focusStyles' => LegoDesignModel::focusStyles(),
                'activeEffects' => LegoDesignModel::activeEffects(),
            ]
        );
    }

    public static function preserveBeforeSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        check_admin_referer('h18_save_page_editor');
        $slug = self::postedSlug();
        if ($slug === '') {
            return;
        }
        $store = get_option(EditorLegoResponsiveDesignAdminController::OPTION, []);
        self::$previousPage = is_array($store) && isset($store[$slug]) && is_array($store[$slug])
            ? $store[$slug]
            : [];
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        check_admin_referer('h18_save_page_editor');
        $slug = self::postedSlug();
        if ($slug === '') {
            return;
        }

        $postedByKey = [];
        if (isset($_POST['h18_lego_interaction_states']) && is_array($_POST['h18_lego_interaction_states'])) {
            foreach (wp_unslash($_POST['h18_lego_interaction_states']) as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                $key = isset($entry['SectionKey']) ? sanitize_text_field((string)$entry['SectionKey']) : '';
                $json = isset($entry['StateJson']) ? (string)$entry['StateJson'] : '';
                $decoded = $json !== '' ? json_decode($json, true) : null;
                if ($key !== '' && is_array($decoded)) {
                    $postedByKey[$key] = $decoded;
                }
            }
        }

        $store = get_option(EditorLegoResponsiveDesignAdminController::OPTION, []);
        $store = is_array($store) ? $store : [];
        $page = isset($store[$slug]) && is_array($store[$slug]) ? $store[$slug] : [];
        $sections = isset($page['Sections']) && is_array($page['Sections']) ? $page['Sections'] : [];
        $previousSections = isset(self::$previousPage['Sections']) && is_array(self::$previousPage['Sections'])
            ? self::$previousPage['Sections']
            : [];

        $keys = array_values(array_unique(array_merge(array_keys($sections), array_keys($previousSections), array_keys($postedByKey))));
        foreach ($keys as $key) {
            $section = isset($sections[$key]) && is_array($sections[$key]) ? $sections[$key] : [];
            $previous = isset($previousSections[$key]) && is_array($previousSections[$key]) ? $previousSections[$key] : [];
            $posted = isset($postedByKey[$key]) && is_array($postedByKey[$key]) ? $postedByKey[$key] : [];

            foreach (['Tablet', 'Mobile'] as $device) {
                $deviceEntry = isset($section[$device]) && is_array($section[$device]) ? $section[$device] : [];
                $previousDevice = isset($previous[$device]) && is_array($previous[$device]) ? $previous[$device] : [];
                $postedDevice = isset($posted[$device]) && is_array($posted[$device]) ? $posted[$device] : [];

                $hasPostedState = array_key_exists('HasOverride', $postedDevice);
                $hasOverride = $hasPostedState
                    ? !empty($postedDevice['HasOverride'])
                    : !empty($previousDevice['InteractionHasOverride']);

                $fallbackDesign = isset($deviceEntry['Design']) && is_array($deviceEntry['Design'])
                    ? $deviceEntry['Design']
                    : (isset($previousDevice['Design']) && is_array($previousDevice['Design'])
                        ? $previousDevice['Design']
                        : LegoDesignModel::defaults());

                // Preserve the snapshot even while inheritance is active. The
                // flag decides whether it is effective; the values remain ready
                // if inheritance is disabled again later.
                $interaction = $hasPostedState && isset($postedDevice['Interaction']) && is_array($postedDevice['Interaction'])
                    ? $postedDevice['Interaction']
                    : LegoInteractionStateModel::fromDesign(
                        isset($previousDevice['Design']) && is_array($previousDevice['Design'])
                            ? $previousDevice['Design']
                            : $fallbackDesign
                    );
                $deviceEntry['Design'] = LegoInteractionStateModel::mergeIntoDesign($fallbackDesign, $interaction);
                $deviceEntry['InteractionHasOverride'] = $hasOverride;
                $section[$device] = $deviceEntry;
            }
            $sections[$key] = $section;
        }

        $page['SchemaVersion'] = $page['SchemaVersion'] ?? 1;
        $page['SavedUtc'] = gmdate('c');
        $page['Sections'] = $sections;
        $store[$slug] = $page;
        update_option(EditorLegoResponsiveDesignAdminController::OPTION, $store, false);
    }

    private static function postedSlug(): string
    {
        return isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
    }
}
