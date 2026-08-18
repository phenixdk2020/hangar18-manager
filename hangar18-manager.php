<?php
/**
 * Plugin Name: Hangar18 Manager
 * Plugin URI: https://hangar18.dk/
 * Description: Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.
 * Version: 0.7.0
 * Author: Hangar18
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Text Domain: hangar18-manager
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Hangar18_Manager {
    const VERSION = '0.7.0';

    const MENU_SLUG = 'hangar18-manager';

    const VEHICLE_PARENT_SLUG = 'koeretoejer-og-materiel';
    const EVENT_PARENT_SLUG   = 'events';
    const GALLERY_PARENT_SLUG = 'billedgalleri';
    const HOME_SLUG           = 'hjem';

    const VEHICLE_MARKER = 'HANGAR18-VEHICLE-DATA';
    const EVENT_MARKER   = 'HANGAR18-EVENT-DATA';
    const GALLERY_MARKER = 'HANGAR18-GALLERY-ALBUM-DATA';
    const STATIC_CONTENT_MARKER = 'HANGAR18-STATIC-CONTENT-DATA';
    const PAGE_EDITOR_MARKER = 'HANGAR18-PAGE-EDITOR-DATA';

    const LOG_OPTION               = 'hangar18_manager_log';
    const DESIGN_OPTION            = 'hangar18_manager_design'; // v0.3.0 legacy
    const HEADER_DESIGN_OPTION     = 'hangar18_manager_header_design_v25';
    const VEHICLE_REGISTER_OPTION  = 'hangar18_manager_vehicle_register_v12';
    const VEHICLE_FIELDS_OPTION    = 'hangar18_manager_vehicle_fields_v1';
    const CONTENT_LAYOUT_OPTION     = 'hangar18_manager_content_layout_v1';
    const STATIC_CONTENT_OPTION     = 'hangar18_manager_static_content_v1';
    const PAGE_EDITOR_OPTION        = 'hangar18_manager_pages_v1';
    const PAGE_VERSION_HISTORY_OPTION = 'hangar18_manager_page_versions_v1';
    const PAGE_PRESETS_OPTION         = 'hangar18_manager_page_presets_v1';
    const PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1';
    const PAGE_TEMPLATES_OPTION       = 'hangar18_manager_page_templates_v1';
    const CUSTOM_DATA_TYPES_OPTION    = 'hangar18_manager_custom_data_types_v1';
    const DATA_ENTRY_POST_TYPE        = 'h18_data_entry';
    const DATA_TAG_TAXONOMY            = 'h18_data_tag';
    const FORM_SUBMISSIONS_OPTION   = 'hangar18_manager_form_submissions_v1';
    const POLL_VOTES_OPTION         = 'hangar18_manager_poll_votes_v1';
    const MENU_ORDER_OPTION        = 'hangar18_manager_menu_order_v20';
    const CONFIG_IMPORT_META_OPTION= 'hangar18_manager_config_import_meta';
    const CONFIG_BOOTSTRAP_OPTION   = 'hangar18_manager_config_bootstrap_v032';
    const UPDATE_SETTINGS_OPTION    = 'hangar18_manager_update_settings_v1';
    const UPDATE_STATE_OPTION       = 'hangar18_manager_update_state_v1';
    const UPDATE_LOCK_OPTION        = 'hangar18_manager_update_lock_v1';
    const AUTHORITATIVE_BASELINE_OPTION = 'hangar18_manager_authoritative_baseline_20260813';
    const ACTIVE_MENU_OPTION       = 'hangar18_manager_active_menu';
    const FRONTEND_REPAIR_046_OPTION = 'hangar18_manager_frontend_repair_046';
    const ASTRA_BANNER_REPAIR_047_OPTION = 'hangar18_manager_astra_banner_repair_047';
    const VEHICLE_LAYOUT_REPAIR_049_OPTION = 'hangar18_manager_vehicle_layout_repair_049';
    const LEGACY_PAGE_TEMPLATE_REPAIR_0411_OPTION = 'hangar18_manager_legacy_page_template_repair_0411';
    const MOBILE_CONTENT_LAYOUT_REPAIR_0414_OPTION = 'hangar18_manager_mobile_content_layout_repair_0414';
    const LEGACY_STARTUP_CLEANUP_0415_OPTION = 'hangar18_manager_legacy_startup_cleanup_0415';
    const HOME_EDITOR_DESIGN_REPAIR_0423_OPTION = 'hangar18_manager_home_editor_design_repair_0423';
    const NOTICE_PREFIX            = 'hangar18_manager_notice_';

    const CONFIG_STORE_SLUG  = 'hangar18-configuration-store';
    const CONFIG_STORE_TITLE = 'Hangar18 Configuration Store';

    const HEADER_START = '<!-- HANGAR18-HEADER-START -->';
    const HEADER_END   = '<!-- HANGAR18-HEADER-END -->';
    const CSS_START    = '<!-- HANGAR18-SHELL-CSS-START -->';
    const CSS_END      = '<!-- HANGAR18-SHELL-CSS-END -->';
    const FOOTER_START = '<!-- HANGAR18-FOOTER-START -->';
    const FOOTER_END   = '<!-- HANGAR18-FOOTER-END -->';

    const OVERRIDE_START = '<!-- HANGAR18-WEB-OVERRIDE-START -->';
    const OVERRIDE_END   = '<!-- HANGAR18-WEB-OVERRIDE-END -->';

    private static $instance = null;
    private $active_dynamic_data_context = null;
    private $active_query_list_stack = [];

    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('init', [$this, 'register_dynamic_data_post_type'], 5);
        add_action('admin_init', [$this, 'maybe_run_frontend_repair_046'], 15);
        add_action('admin_init', [$this, 'maybe_repair_astra_banner_047'], 16);
        add_action('admin_init', [$this, 'maybe_repair_vehicle_layout_049'], 17);
        add_action('admin_init', [$this, 'maybe_repair_legacy_page_templates_0411'], 18);
        add_action('admin_init', [$this, 'maybe_repair_mobile_content_layout_0414'], 19);
        add_action('admin_init', [$this, 'maybe_cleanup_legacy_startup_and_vehicle_mobile_0415'], 19);
        add_action('admin_init', [$this, 'maybe_restore_home_editor_design_0423'], 20);
        add_action('admin_init', [$this, 'maybe_check_for_updates'], 20);
        add_action('wp', [$this, 'disable_astra_banner_for_managed_pages'], 1);
        add_action('wp_head', [$this, 'render_design_tokens_v050'], 998);
        add_action('wp_head', [$this, 'render_frontend_runtime_fixes'], 999);
        add_action('wp_footer', [$this, 'render_header_origin_guard'], PHP_INT_MAX);
        add_action('admin_menu', [$this, 'register_admin_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_assets']);
        add_shortcode('hangar18_page_editor', [$this, 'shortcode_page_editor']);
        add_shortcode('hangar18_data_query', [$this, 'shortcode_data_query']);
        add_shortcode('hangar18_data_query_advanced', [$this, 'shortcode_data_query_advanced']);
        add_filter('wp_robots', [$this, 'filter_conversion_test_robots']);

        add_action('admin_post_h18_save_vehicle', [$this, 'handle_save_vehicle']);
        add_action('admin_post_h18_save_vehicle_register_settings', [$this, 'handle_save_vehicle_register_settings']);
        add_action('admin_post_h18_save_vehicle_fields', [$this, 'handle_save_vehicle_fields']);
        add_action('admin_post_h18_rebuild_vehicle_register', [$this, 'handle_rebuild_vehicle_register']);

        add_action('admin_post_h18_save_event', [$this, 'handle_save_event']);
        add_action('admin_post_h18_save_event_layout', [$this, 'handle_save_event_layout']);
        add_action('admin_post_h18_rebuild_event_register', [$this, 'handle_rebuild_event_register']);

        add_action('admin_post_h18_save_gallery_album', [$this, 'handle_save_gallery_album']);
        add_action('admin_post_h18_save_gallery_layout', [$this, 'handle_save_gallery_layout']);
        add_action('admin_post_h18_rebuild_gallery_index', [$this, 'handle_rebuild_gallery_index']);

        add_action('admin_post_h18_save_static_content', [$this, 'handle_save_static_content']);
        add_action('admin_post_h18_save_data_type', [$this, 'handle_save_data_type']);
        add_action('admin_post_h18_delete_data_type', [$this, 'handle_delete_data_type']);
        add_action('admin_post_h18_save_data_entry', [$this, 'handle_save_data_entry']);
        add_action('admin_post_h18_delete_data_entry', [$this, 'handle_delete_data_entry']);
        add_action('admin_post_h18_save_page_editor', [$this, 'handle_save_page_editor']);
        add_action('wp_ajax_h18_save_page_preset', [$this, 'ajax_save_page_preset']);
        add_action('wp_ajax_h18_delete_page_preset', [$this, 'ajax_delete_page_preset']);
        add_action('wp_ajax_h18_save_page_component', [$this, 'ajax_save_page_component']);
        add_action('wp_ajax_h18_delete_page_component', [$this, 'ajax_delete_page_component']);
        add_action('wp_ajax_h18_save_page_component_variant', [$this, 'ajax_save_page_component_variant']);
        add_action('wp_ajax_h18_delete_page_component_variant', [$this, 'ajax_delete_page_component_variant']);
        add_action('wp_ajax_h18_save_page_template', [$this, 'ajax_save_page_template']);
        add_action('wp_ajax_h18_delete_page_template', [$this, 'ajax_delete_page_template']);
        add_action('wp_ajax_h18_create_page_from_template', [$this, 'ajax_create_page_from_template']);
        add_action('wp_ajax_h18_create_blank_page', [$this, 'ajax_create_blank_page']);
        add_action('admin_post_h18_create_page_conversion_test', [$this, 'handle_create_page_conversion_test']);
        add_action('admin_post_h18_restore_page_before_editor', [$this, 'handle_restore_page_before_editor']);
        add_action('admin_post_h18_send_page_form', [$this, 'handle_send_page_form']);
        add_action('admin_post_nopriv_h18_send_page_form', [$this, 'handle_send_page_form']);
        add_action('admin_post_h18_submit_poll', [$this, 'handle_submit_poll']);
        add_action('admin_post_nopriv_h18_submit_poll', [$this, 'handle_submit_poll']);
        add_action('admin_post_h18_export_poll', [$this, 'handle_export_poll']);
        add_action('admin_post_h18_export_form_submissions', [$this, 'handle_export_form_submissions']);
        add_action('admin_post_h18_test_page_form', [$this, 'handle_test_page_form']);

        add_action('admin_post_h18_create_menu', [$this, 'handle_create_menu']);
        add_action('admin_post_h18_save_menu', [$this, 'handle_save_menu']);
        add_action('admin_post_h18_save_menu_pin', [$this, 'handle_save_menu_pin']);
        add_action('admin_post_h18_add_menu_page', [$this, 'handle_add_menu_page']);
        add_action('admin_post_h18_repair_menu', [$this, 'handle_repair_menu']);

        add_action('admin_post_h18_save_design', [$this, 'handle_save_design']);
        add_action('admin_post_h18_sync_shell', [$this, 'handle_sync_shell']);

        add_action('admin_post_h18_create_full_backup', [$this, 'handle_create_full_backup']);
        add_action('admin_post_h18_create_home_comparison', [$this, 'handle_create_home_comparison']);

        add_action('admin_post_h18_save_update_settings', [$this, 'handle_save_update_settings']);
        add_action('admin_post_h18_check_updates', [$this, 'handle_check_updates']);
        add_action('admin_post_h18_install_update', [$this, 'handle_install_update']);

        add_action('admin_post_h18_clear_log', [$this, 'handle_clear_log']);
    }

    private function is_hangar18_managed_frontend_page() {
        if (!is_page()) {
            return false;
        }

        $page_id = (int) get_queried_object_id();
        if ($page_id <= 0) {
            return false;
        }

        $post = get_post($page_id);
        if (!$post instanceof WP_Post) {
            return false;
        }

        $content = (string) $post->post_content;

        if (
            strpos($content, self::HEADER_START) !== false ||
            strpos($content, self::VEHICLE_MARKER) !== false ||
            strpos($content, self::EVENT_MARKER) !== false ||
            strpos($content, self::GALLERY_MARKER) !== false ||
            strpos($content, self::PAGE_EDITOR_MARKER) !== false
        ) {
            return true;
        }

        $slug = (string) $post->post_name;
        return in_array(
            $slug,
            [
                self::HOME_SLUG,
                self::VEHICLE_PARENT_SLUG,
                self::EVENT_PARENT_SLUG,
                self::GALLERY_PARENT_SLUG,
                'om-foreningen',
                'bliv-medlem',
                'kontakt',
            ],
            true
        );
    }

    public function filter_conversion_test_robots($robots) {
        if (!is_singular('page')) {
            return $robots;
        }

        $page_id = (int) get_queried_object_id();
        if ($page_id <= 0 || !get_post_meta($page_id, '_h18_conversion_test_source_id', true)) {
            return $robots;
        }

        if (!is_array($robots)) {
            $robots = [];
        }
        $robots['noindex'] = true;
        $robots['nofollow'] = true;
        $robots['noarchive'] = true;
        return $robots;
    }

    public function disable_astra_banner_for_managed_pages() {
        if (is_admin() || !$this->is_hangar18_managed_frontend_page()) {
            return;
        }

        /*
         * Astra 4.x kan generere en separat Banner Area før entry-content.
         * Det er denne wrapper der har givet den lilla/blå bjælke.
         * Brug Astra's egne filtre i stedet for at forsøge at skjule
         * stadig flere CSS-selectors.
         */
        add_filter('astra_the_title_enabled', '__return_false', 999);
        add_filter('astra_advanced_header_title', '__return_false', 999);
        add_filter('astra_apply_hero_header_banner', '__return_false', 999);
        add_filter('astra_remove_entry_header_content', '__return_true', 999);
        add_filter('astra_single_layout_one_banner_visibility', '__return_false', 999);
        add_filter('astra_banner_title_area_visibility', [$this, 'disable_astra_banner_visibility_047'], 999);
    }

    public function disable_astra_banner_visibility_047($visibility) {
        return 'disabled';
    }

    private function get_hangar18_managed_page_ids_047() {
        $ids = [];

        foreach ($this->get_managed_pages() as $page) {
            if ($page instanceof WP_Post) {
                $ids[] = (int) $page->ID;
            }
        }

        return array_values(array_unique(array_filter($ids)));
    }

    public function maybe_repair_astra_banner_047() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::ASTRA_BANNER_REPAIR_047_OPTION, false)) {
            return;
        }

        try {
            $this->create_full_managed_backup(
                'Før v0.4.7 Astra Banner Area-reparation'
            );

            $updated = 0;

            foreach ($this->get_hangar18_managed_page_ids_047() as $page_id) {
                /*
                 * Astra's egne sidemeta-felter:
                 * site-post-title          = Disable Title
                 * ast-title-bar-display    = ældre title-bar toggle
                 * ast-banner-title-visibility = nyere Banner Area toggle
                 *
                 * Vi ændrer ikke Hangar18-indhold, Events, køretøjer,
                 * galleri eller HeaderDesign her.
                 */
                update_post_meta($page_id, 'site-post-title', 'disabled');
                update_post_meta($page_id, 'ast-title-bar-display', 'disabled');
                update_post_meta($page_id, 'ast-banner-title-visibility', 'disabled');

                $updated++;
            }

            update_option(
                self::ASTRA_BANNER_REPAIR_047_OPTION,
                [
                    'CompletedUtc' => gmdate('c'),
                    'Pages'        => $updated,
                ],
                false
            );

            $this->rebuild_vehicle_register();
            $this->rebuild_event_register();
            $this->rebuild_gallery_index();

            $this->log(
                'INFO',
                'ASTRA_BANNER_REPAIR_047_COMPLETE',
                "Astra Banner Area er deaktiveret på {$updated} Hangar18-styrede sider, og oversigtssiderne er genbygget."
            );

            $this->set_notice(
                'success',
                "v0.4.7: Astra Banner Area er slået fra på {$updated} Hangar18-styrede sider."
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'ASTRA_BANNER_REPAIR_047_FAILED',
                $e->getMessage()
            );
        }
    }

    public function maybe_repair_vehicle_layout_049() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::VEHICLE_LAYOUT_REPAIR_049_OPTION, false)) {
            return;
        }

        try {
            $this->create_full_managed_backup(
                'Automatisk v0.4.9 reparation af køretøjslayout'
            );

            $vehicles = $this->rebuild_vehicle_detail_pages_046();
            $this->rebuild_vehicle_register();

            update_option(
                self::VEHICLE_LAYOUT_REPAIR_049_OPTION,
                [
                    'CompletedUtc' => gmdate('c'),
                    'Vehicles'     => $vehicles,
                ],
                false
            );

            $this->log(
                'INFO',
                'VEHICLE_LAYOUT_REPAIR_049_COMPLETE',
                "v0.4.9: {$vehicles} køretøjssider er genbygget med billede til venstre og tekniske data til højre."
            );

            $this->set_notice(
                'success',
                "v0.4.9: {$vehicles} køretøjssider er genbygget med det korrekte to-kolonne-layout."
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'VEHICLE_LAYOUT_REPAIR_049_FAILED',
                $e->getMessage()
            );
        }
    }

    public function maybe_repair_legacy_page_templates_0411() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::LEGACY_PAGE_TEMPLATE_REPAIR_0411_OPTION, false)) {
            return;
        }

        $previous_templates = [];

        try {
            $pages = $this->get_managed_pages();
            $configuration_store = $this->get_configuration_store_page();

            if ($configuration_store) {
                $pages[] = $configuration_store;
            }

            foreach ($pages as $page) {
                $template = get_page_template_slug($page->ID);

                if (!$template || $template === 'default') {
                    continue;
                }

                $previous_templates[(int) $page->ID] = (string) $template;
                update_post_meta($page->ID, '_wp_page_template', 'default');
            }

            update_option(
                self::LEGACY_PAGE_TEMPLATE_REPAIR_0411_OPTION,
                [
                    'CompletedUtc'      => gmdate('c'),
                    'PreviousTemplates'=> $previous_templates,
                ],
                false
            );

            $count = count($previous_templates);
            $this->log(
                'INFO',
                'LEGACY_PAGE_TEMPLATE_REPAIR_0411_COMPLETE',
                "v0.4.11: {$count} styrede sider inklusive Configuration Store er flyttet fra gamle Astra-sideskabeloner til temaets standardskabelon."
            );

            if ($count > 0) {
                $this->set_notice(
                    'success',
                    "v0.4.11: {$count} gamle Astra-sideskabeloner er ryddet. HeaderDesign, Configuration Store, Billedgalleri og øvrige styrede sider kan nu gemmes igen."
                );
            }
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'LEGACY_PAGE_TEMPLATE_REPAIR_0411_FAILED',
                $e->getMessage()
            );
        }
    }

    public function maybe_repair_mobile_content_layout_0414() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::MOBILE_CONTENT_LAYOUT_REPAIR_0414_OPTION, false)) {
            return;
        }

        try {
            $this->create_full_managed_backup(
                'Før automatisk v0.4.14 mobilcentrering af Events og Billedgalleri'
            );

            $settings = $this->get_content_layout_settings();
            update_option(self::CONTENT_LAYOUT_OPTION, $settings, false);

            $published = $settings;
            $published['Saved'] = gmdate('c');
            $this->publish_configuration_file('Hangar18-ContentLayout.json', $published);

            $events = 0;
            foreach ($this->get_event_pages(false) as $page) {
                $data = $this->decode_marker(self::EVENT_MARKER, $page->post_content);
                if (!$data) {
                    continue;
                }

                $result = wp_update_post(
                    [
                        'ID'           => $page->ID,
                        'page_template'=> 'default',
                        'post_content' => $this->wrap_with_shell(
                            $this->build_event_core($page->ID, $data),
                            $page->ID
                        ),
                    ],
                    true
                );

                if (is_wp_error($result)) {
                    throw new RuntimeException(
                        "Event ID {$page->ID}: " . $result->get_error_message()
                    );
                }
                $events++;
            }

            $albums = 0;
            foreach ($this->get_gallery_pages(false) as $page) {
                $data = $this->decode_marker(self::GALLERY_MARKER, $page->post_content);
                if (!$data) {
                    continue;
                }

                $result = wp_update_post(
                    [
                        'ID'           => $page->ID,
                        'page_template'=> 'default',
                        'post_content' => $this->wrap_with_shell(
                            $this->build_gallery_album_core($page->ID, $data),
                            $page->ID
                        ),
                    ],
                    true
                );

                if (is_wp_error($result)) {
                    throw new RuntimeException(
                        "Gallerialbum ID {$page->ID}: " . $result->get_error_message()
                    );
                }
                $albums++;
            }

            $this->rebuild_event_register();
            $this->rebuild_gallery_index();

            update_option(
                self::MOBILE_CONTENT_LAYOUT_REPAIR_0414_OPTION,
                [
                    'CompletedUtc' => gmdate('c'),
                    'Events'       => $events,
                    'Albums'       => $albums,
                ],
                false
            );

            $this->log(
                'INFO',
                'MOBILE_CONTENT_LAYOUT_REPAIR_0414_COMPLETE',
                "v0.4.14: Mobilvisning er midtstillet for Events og Billedgalleri. Events={$events}; Albums={$albums}."
            );

            $this->set_notice(
                'success',
                "v0.4.14: Events og Billedgalleri er midtstillet på mobil. {$events} events og {$albums} albumsider er opdateret."
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'MOBILE_CONTENT_LAYOUT_REPAIR_0414_FAILED',
                $e->getMessage()
            );
        }
    }

    public function maybe_cleanup_legacy_startup_and_vehicle_mobile_0415() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::LEGACY_STARTUP_CLEANUP_0415_OPTION, false)) {
            return;
        }

        try {
            $this->create_full_managed_backup(
                'Før v0.4.15 oprydning og mobilplacering for køretøjer'
            );

            /*
             * De tre options tilhørte den oprindelige PowerShell/bootstrap-
             * arbejdsgang. Den nuværende web-manager bruger sine egne
             * WordPress-options og den private Configuration Store.
             */
            delete_option(self::CONFIG_IMPORT_META_OPTION);
            delete_option(self::CONFIG_BOOTSTRAP_OPTION);
            delete_option(self::AUTHORITATIVE_BASELINE_OPTION);

            $settings = $this->get_vehicle_register_settings();
            update_option(self::VEHICLE_REGISTER_OPTION, $settings, false);

            $central = $settings;
            $central['Saved'] = gmdate('c');
            $this->publish_configuration_file(
                'Hangar18-VehicleRegister.json',
                $central
            );

            $vehicles = $this->apply_vehicle_detail_alignment_to_existing_pages(
                $settings
            );
            $this->rebuild_vehicle_register();

            update_option(
                self::LEGACY_STARTUP_CLEANUP_0415_OPTION,
                [
                    'CompletedUtc' => gmdate('c'),
                    'Vehicles'     => $vehicles,
                ],
                false
            );

            $this->log(
                'INFO',
                'LEGACY_STARTUP_CLEANUP_0415_COMPLETE',
                "v0.4.15: Gammel PowerShell/bootstrap-status er ryddet, og {$vehicles} køretøjssider er genbygget med mobilplacering."
            );

            $this->set_notice(
                'success',
                "v0.4.15: Den gamle opstartsimport er ryddet, og {$vehicles} køretøjssider er opdateret med mobilplacering."
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'LEGACY_STARTUP_CLEANUP_0415_FAILED',
                $e->getMessage()
            );
        }
    }

    public function maybe_restore_home_editor_design_0423() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::HOME_EDITOR_DESIGN_REPAIR_0423_OPTION, false)) {
            return;
        }

        try {
            $page = $this->post_by_slug(self::HOME_SLUG);
            if (!$page instanceof WP_Post) {
                return;
            }

            $data = $this->get_page_editor_data(self::HOME_SLUG, $page);
            $has_imported_sections = false;
            foreach ((array) $data['Sections'] as $section) {
                if (strpos((string) ($section['Key'] ?? ''), 'importeret-') === 0) {
                    $has_imported_sections = true;
                    break;
                }
            }
            if (!$has_imported_sections) {
                return;
            }

            $this->create_full_managed_backup(
                'Før v0.4.23 gendannede Hjem-sidens sektionsdesign'
            );

            $changed = 0;
            $previous_type = '';
            foreach ($data['Sections'] as &$section) {
                $type = (string) ($section['Type'] ?? '');
                $title = trim((string) ($section['Title'] ?? ''));
                $plain_content = trim(wp_strip_all_tags((string) ($section['Content'] ?? '')));
                $values = [];

                if ($type === 'hero') {
                    $values = [
                        'TopSpacingPx' => 0,
                        'BottomSpacingPx' => 0,
                        'MobileTopSpacingPx' => 0,
                        'MobileBottomSpacingPx' => 0,
                        'HorizontalPaddingPx' => 0,
                        'MobileHorizontalPaddingPx' => 0,
                        'MobileHeroHeightPx' => 180,
                    ];
                } elseif (
                    $previous_type === 'hero' &&
                    $type === 'text' &&
                    $title === ''
                ) {
                    $values = [
                        'Background' => 'Sand',
                        'TopSpacingPx' => 32,
                        'BottomSpacingPx' => 0,
                        'MobileTopSpacingPx' => 24,
                        'MobileBottomSpacingPx' => 0,
                        'PaddingPx' => 16,
                        'HorizontalPaddingPx' => 24,
                        'MobilePaddingPx' => 13,
                        'MobileHorizontalPaddingPx' => 18,
                        'RadiusPx' => 0,
                        'DesktopAlignment' => 'Center',
                        'MobileAlignment' => 'Center',
                    ];
                } else {
                    $background = '';
                    if ($title === 'Om foreningen' || $title === 'Kontakt os') {
                        $background = 'OffWhite';
                    } elseif ($title === 'Køretøjer og materiel') {
                        $background = 'Olive';
                    } elseif ($title === 'Bliv en del af foreningen') {
                        $background = 'Sand';
                    } elseif (
                        $type === 'html' &&
                        (
                            strpos($plain_content, 'Bevaring') !== false ||
                            strpos($plain_content, 'Events') !== false ||
                            strpos($plain_content, 'Billedgalleri') !== false
                        )
                    ) {
                        $background = 'White';
                    }

                    if ($background !== '') {
                        $values = [
                            'Background' => $background,
                            'TopSpacingPx' => 32,
                            'BottomSpacingPx' => 0,
                            'MobileTopSpacingPx' => 24,
                            'MobileBottomSpacingPx' => 0,
                            'PaddingPx' => 64,
                            'HorizontalPaddingPx' => 24,
                            'MobilePaddingPx' => 38,
                            'MobileHorizontalPaddingPx' => 18,
                            'RadiusPx' => 0,
                            'DesktopAlignment' => 'Left',
                            'MobileAlignment' => 'Center',
                        ];
                    }
                }

                foreach ($values as $key => $value) {
                    if (!array_key_exists($key, $section) || $section[$key] !== $value) {
                        $section[$key] = $value;
                        $changed++;
                    }
                }
                $previous_type = $type;
            }
            unset($section);

            $data = $this->normalize_page_editor_data($data, $page);
            $this->save_page_editor_data(self::HOME_SLUG, $data);

            $store = $this->get_page_editor_store();
            $this->publish_configuration_file('Hangar18-Pages.json', [
                'Version' => '1.22',
                'Saved'   => gmdate('c'),
                'Pages'   => $store,
            ]);

            $result = wp_update_post([
                'ID'            => $page->ID,
                'page_template' => 'default',
                'post_content'  => $this->wrap_with_shell(
                    $this->build_page_editor_core(self::HOME_SLUG, $data),
                    $page->ID
                ),
            ], true);
            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            update_option(self::HOME_EDITOR_DESIGN_REPAIR_0423_OPTION, [
                'CompletedUtc' => gmdate('c'),
                'ChangedValues' => $changed,
            ], false);

            $this->log(
                'INFO',
                'HOME_EDITOR_DESIGN_REPAIR_0423_COMPLETE',
                "v0.4.23: Hjem-sidens farver, sektionsafstand, indvendige luft, knapper og mobilbanner er gendannet. Ændrede værdier={$changed}."
            );
            $this->set_notice(
                'success',
                'v0.4.23: Hjem-sidens oprindelige sektionsdesign er gendannet. Der blev taget backup før ændringen.'
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'HOME_EDITOR_DESIGN_REPAIR_0423_FAILED',
                $e->getMessage()
            );
            $this->set_notice(
                'error',
                'v0.4.23 kunne ikke gendanne Hjem-sidens design: ' . $e->getMessage()
            );
        }
    }

    public function render_design_tokens_v050() {
    if (is_admin() || !$this->is_hangar18_managed_frontend_page()) {
        return;
    }

    $d = $this->get_header_design_settings();
    $body_font = $this->header_font_family_css($d['BodyFontFamily']);
    $heading_font = $this->header_font_family_css($d['HeadingFontFamily']);
    $transition = (int) $d['MenuTransitionMs'];
    ?>
    <style id="hangar18-design-tokens-v050">
    :root {
        --h18-color-primary:<?php echo esc_html($d['PrimaryColor']); ?>;
        --h18-color-secondary:<?php echo esc_html($d['SecondaryColor']); ?>;
        --h18-color-accent:<?php echo esc_html($d['AccentColor']); ?>;
        --h18-color-surface:<?php echo esc_html($d['SurfaceColor']); ?>;
        --h18-color-background:<?php echo esc_html($d['BackgroundColor']); ?>;
        --h18-color-text:<?php echo esc_html($d['TextColor']); ?>;
        --h18-color-light:<?php echo esc_html($d['LightTextColor']); ?>;
        --h18-color-action:<?php echo esc_html($d['ActionColor']); ?>;
        --h18-font-body:<?php echo esc_html($body_font); ?>;
        --h18-font-heading:<?php echo esc_html($heading_font); ?>;
        --h18-font-body-size:<?php echo esc_html((int) $d['BodyFontSize']); ?>px;
        --h18-font-h1-size:<?php echo esc_html((int) $d['H1FontSize']); ?>px;
        --h18-font-h2-size:<?php echo esc_html((int) $d['H2FontSize']); ?>px;
        --h18-font-h3-size:<?php echo esc_html((int) $d['H3FontSize']); ?>px;
        --h18-radius-small:<?php echo esc_html((int) $d['RadiusSmallPx']); ?>px;
        --h18-radius-medium:<?php echo esc_html((int) $d['RadiusMediumPx']); ?>px;
        --h18-radius-large:<?php echo esc_html((int) $d['RadiusLargePx']); ?>px;
        --h18-space-xs:<?php echo esc_html((int) $d['SpacingXsPx']); ?>px;
        --h18-space-s:<?php echo esc_html((int) $d['SpacingSmallPx']); ?>px;
        --h18-space-m:<?php echo esc_html((int) $d['SpacingMediumPx']); ?>px;
        --h18-space-l:<?php echo esc_html((int) $d['SpacingLargePx']); ?>px;
        --h18-space-xl:<?php echo esc_html((int) $d['SpacingXlPx']); ?>px;
        --h18-motion-fast:<?php echo esc_html((int) $d['MotionFastMs']); ?>ms;
        --h18-motion-normal:<?php echo esc_html((int) $d['MotionNormalMs']); ?>ms;
        --h18-motion-slow:<?php echo esc_html((int) $d['MotionSlowMs']); ?>ms;
        --h18-focus-ring:<?php echo esc_html($d['FocusRingColor']); ?>;
        --h18-focus-ring-width:<?php echo esc_html((int) $d['FocusRingWidthPx']); ?>px;
        --h18-menu-transition:<?php echo esc_html($transition); ?>ms;
    }

    body.page .h18-editor-page {
        color:var(--h18-color-text);
        font-family:var(--h18-font-body);
        font-size:var(--h18-font-body-size);
    }
    body.page .h18-editor-page h1 {font-family:var(--h18-font-heading);font-size:clamp(2rem,5vw,var(--h18-font-h1-size));}
    body.page .h18-editor-page h2 {font-family:var(--h18-font-heading);font-size:clamp(1.55rem,3.5vw,var(--h18-font-h2-size));}
    body.page .h18-editor-page h3 {font-family:var(--h18-font-heading);font-size:clamp(1.2rem,2.5vw,var(--h18-font-h3-size));}
    body.page .h18-editor-section--offwhite {background:var(--h18-color-surface) !important;}
    body.page .h18-editor-section--sand {background:var(--h18-color-accent) !important;color:var(--h18-color-text) !important;}
    body.page .h18-editor-section--olive {background:var(--h18-color-primary) !important;color:var(--h18-color-light) !important;}
    body.page .h18-editor-section--steel {background:var(--h18-color-secondary) !important;color:var(--h18-color-light) !important;}
    body.page .h18-editor-section a {color:var(--h18-color-action);}
    .h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a {position:relative;transition:color var(--h18-menu-transition) ease,background var(--h18-menu-transition) ease,transform var(--h18-menu-transition) ease;}

    <?php if ($d['MenuPresentation'] === 'FloatingPill') : ?>
    .h18-site-header .h18-desktop-nav {background:var(--h18-color-surface) !important;border:1px solid rgba(48,56,42,.14) !important;border-radius:999px !important;padding:6px 12px !important;box-shadow:0 8px 24px rgba(0,0,0,.09) !important;}
              .h18-site-header .h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a {color:var(--h18-color-text) !important;}
    <?php elseif ($d['MenuPresentation'] === 'Framed') : ?>
    .h18-site-header .h18-desktop-nav {border:1px solid var(--h18-color-accent) !important;border-radius:var(--h18-radius-medium) !important;padding:6px 12px !important;}
    <?php endif; ?>

    <?php if ($d['MenuHoverEffect'] === 'Underline') : ?>
    .h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a::after {content:"";position:absolute;left:12%;right:12%;bottom:-4px;height:2px;background:var(--h18-color-accent);transform:scaleX(0);transition:transform var(--h18-menu-transition) ease;}
    .h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a:hover::after,.h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a:focus-visible::after {transform:scaleX(1);}
    <?php elseif ($d['MenuHoverEffect'] === 'Lift') : ?>
    .h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a:hover,.h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a:focus-visible {transform:translateY(-2px);}
    <?php elseif ($d['MenuHoverEffect'] === 'Pill') : ?>
    .h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a:hover,.h18-desktop-nav .h18-web-menu-root > .h18-menu-item > a:focus-visible {background:color-mix(in srgb,var(--h18-color-accent) 24%,transparent);border-radius:999px;}
    <?php endif; ?>

    <?php if ($d['MenuActiveStyle'] === 'Underline') : ?>
    .h18-desktop-nav .current-menu-item > a::after,.h18-desktop-nav .current_page_item > a::after,.h18-desktop-nav .current-menu-ancestor > a::after {content:"";position:absolute;left:12%;right:12%;bottom:-4px;height:2px;background:var(--h18-color-accent);transform:scaleX(1);}
    <?php elseif ($d['MenuActiveStyle'] === 'Pill') : ?>
    .h18-desktop-nav .current-menu-item > a,.h18-desktop-nav .current_page_item > a,.h18-desktop-nav .current-menu-ancestor > a {background:color-mix(in srgb,var(--h18-color-accent) 24%,transparent);border-radius:999px;}
    <?php elseif ($d['MenuActiveStyle'] === 'Dot') : ?>
    .h18-desktop-nav .current-menu-item > a::after,.h18-desktop-nav .current_page_item > a::after {content:"";position:absolute;width:5px;height:5px;border-radius:50%;background:var(--h18-color-accent);left:50%;bottom:-7px;transform:translateX(-50%);}
    <?php endif; ?>

    <?php if ($d['SubmenuAnimation'] !== 'None') : ?>
    .h18-site-header .h18-desktop-nav .h18-submenu {display:flex !important;opacity:0;visibility:hidden;pointer-events:none;transition:opacity var(--h18-menu-transition) ease,transform var(--h18-menu-transition) ease;}
    <?php if ($d['SubmenuAnimation'] === 'FadeSlide') : ?>.h18-site-header .h18-desktop-nav .h18-submenu {transform:translateY(-8px);}
    <?php elseif ($d['SubmenuAnimation'] === 'Scale') : ?>.h18-site-header .h18-desktop-nav .h18-submenu {transform:scale(.96);transform-origin:top left;}
    <?php endif; ?>
    .h18-site-header .h18-desktop-nav .h18-menu-item-has-children:hover > .h18-submenu,.h18-site-header .h18-desktop-nav .h18-menu-item-has-children:focus-within > .h18-submenu {opacity:1;visibility:visible;pointer-events:auto;transform:none;}
    <?php endif; ?>
    </style>
    <?php
}

    public function render_frontend_runtime_fixes() {
        if (is_admin() || !$this->is_hangar18_managed_frontend_page()) {
            return;
        }

        $design = $this->get_header_design_settings();
        $desktop_width = (int) $design['DesktopContentWidthPercent'];
        $maximum_width = max(
            $desktop_width,
            (int) $design['MaximumDesktopContentWidthPercent']
        );
        $laptop_width = min(
            (int) $design['LaptopContentWidthPercent'],
            $maximum_width
        );
        $desktop_width = min($desktop_width, $maximum_width);
        $laptop_breakpoint = (int) $design['ResponsiveLaptopWidthPx'];
        $content_max_width = $design['ContentMaxWidth'] === 'None'
            ? ''
            : ((int) $design['ContentMaxWidth']) . 'px';

        $desktop_max_width = $content_max_width === ''
            ? $desktop_width . 'vw'
            : 'min(' . $desktop_width . 'vw, ' . $content_max_width . ')';
        $laptop_max_width = $content_max_width === ''
            ? $laptop_width . 'vw'
            : 'min(' . $laptop_width . 'vw, ' . $content_max_width . ')';
        $section_spacing = (int) $design['SectionSpacingPx'];
        $mobile_section_spacing = (int) $design['MobileSectionSpacingPx'];
        $content_top_spacing = (int) $design['ContentTopSpacingPx'];
        $content_bottom_spacing = (int) $design['ContentBottomSpacingPx'];
        $mobile_content_top_spacing = (int) $design['MobileContentTopSpacingPx'];
        $mobile_content_bottom_spacing = (int) $design['MobileContentBottomSpacingPx'];

        ?>
        <style id="hangar18-manager-runtime-fixes">
        /*
         * Hangar18 tegner sin egen header inde i sideindholdet.
         * Astra/WordPress' native sidetitel skal derfor ikke vises ovenover.
         */
        body.page .entry-header,
        body.page header.entry-header,
        body.page .page-header,
        body.page .ast-page-title,
        body.page .ast-page-title-wrap,
        body.page .ast-single-entry-banner,
        body.page .ast-single-entry-banner[data-post-type="page"],
        body.page .ast-banner-title,
        body.page .ast-banner-title-area,
        body.page .ast-page-title-bar,
        body.page .ast-title-bar-wrap,
        body.page .ast-archive-description,
        body.page .ast-advanced-headers-wrap,
        body.page .ast-advanced-headers-layout,
        body.page .ast-single-post-order > .entry-title,
        body.page .entry-title,
        body.page h1.entry-title,
        body.page .wp-block-post-title {
            display:none !important;
            visibility:hidden !important;
            height:0 !important;
            min-height:0 !important;
            max-height:0 !important;
            margin:0 !important;
            padding:0 !important;
            border:0 !important;
            overflow:hidden !important;
        }

        body.page .site-content,
        body.page .site-content > .ast-container,
        body.page .content-area,
        body.page .site-main,
        body.page article.page,
        body.page .ast-article-single,
        body.page .entry-content {
            margin-top:0 !important;
            padding-top:0 !important;
        }

        /*
         * Brug de gemte HeaderDesign-bredder direkte. Den gamle importerede
         * shell indeholder stadig en fast v2.0.39-formel; disse mere specifikke
         * regler gør indstillingerne autoritative uden at ændre sideindholdet.
         */
        body.page .h18-site-header,
        body.page .h18-page-frame,
        body.page .h18-site-footer {
            width:<?php echo esc_html($desktop_width); ?>vw !important;
            max-width:<?php echo esc_html($desktop_max_width); ?> !important;
            margin-left:auto !important;
            margin-right:auto !important;
        }

        /*
         * Ensartet, brugerdefineret afstand mellem de synlige hovedsektioner.
         * STYLE/SCRIPT-elementer tæller ikke som en sektion, og den første
         * synlige sektion får derfor aldrig ekstra luft over sig.
         */
        body.page .h18-page-frame {
            --h18-section-spacing:<?php echo esc_html($section_spacing); ?>px;
            --h18-content-top-spacing:<?php echo esc_html($content_top_spacing); ?>px;
            --h18-content-bottom-spacing:<?php echo esc_html($content_bottom_spacing); ?>px;
            margin-top:0 !important;
            margin-block-start:0 !important;
            padding-top:var(--h18-content-top-spacing) !important;
            padding-bottom:var(--h18-content-bottom-spacing) !important;
            padding-block-start:var(--h18-content-top-spacing) !important;
            padding-block-end:var(--h18-content-bottom-spacing) !important;
            box-sizing:border-box !important;
        }

        body.page .h18-page-frame > :not(style):not(script) {
            margin-block-start:0 !important;
            margin-block-end:0 !important;
        }

        body.page .h18-page-frame > :not(style):not(script) ~ :not(style):not(script) {
            margin-block-start:var(--h18-section-spacing) !important;
        }

        /* Headeren skal være det første synlige element helt oppe ved kanten. */
        html,
        body.page,
        body.page #page,
        body.page .h18-theme-main,
        body.page article.h18-theme-page,
        body.page .h18-theme-entry-content,
        body.page .entry-content,
        body.page .entry-content > .h18-site-header:first-child {
            margin-top:0 !important;
            margin-block-start:0 !important;
            padding-top:0 !important;
            padding-block-start:0 !important;
        }

        @media (max-width:<?php echo esc_html($laptop_breakpoint); ?>px) and (min-width:783px) {
            body.page .h18-site-header,
            body.page .h18-page-frame,
            body.page .h18-site-footer {
                width:<?php echo esc_html($laptop_width); ?>vw !important;
                max-width:<?php echo esc_html($laptop_max_width); ?> !important;
            }
        }

        @media (max-width:782px) {
            body.page .h18-site-header,
            body.page .h18-page-frame,
            body.page .h18-site-footer {
                width:100% !important;
                max-width:100% !important;
                margin-left:0 !important;
                margin-right:0 !important;
            }

            body.page .h18-page-frame {
                --h18-section-spacing:<?php echo esc_html($mobile_section_spacing); ?>px;
                --h18-content-top-spacing:<?php echo esc_html($mobile_content_top_spacing); ?>px;
                --h18-content-bottom-spacing:<?php echo esc_html($mobile_content_bottom_spacing); ?>px;
            }
        }

        /* H18-align klasser vinder over Astra/Gutenberg auto-margin. */
        body.page .h18-align-left {
            margin-left:0 !important;
            margin-right:auto !important;
            text-align:left !important;
        }

        body.page .h18-align-left.h18-vehicle-inner,
        body.page .h18-align-left.h18-gallery-grid {
            margin-left:0 !important;
            margin-right:auto !important;
        }

        body.page .h18-align-left.h18-gallery-grid {
            justify-content:start !important;
            justify-items:start !important;
        }

        body.page .h18-align-center {
            margin-left:auto !important;
            margin-right:auto !important;
            text-align:center !important;
        }

        body.page .h18-align-center.h18-gallery-grid {
            justify-content:center !important;
        }
        </style>
        <?php
    }

    public function render_header_origin_guard() {
        if (is_admin() || !$this->is_hangar18_managed_frontend_page()) {
            return;
        }

        ?>
        <style id="hangar18-header-origin-guard">
        /*
         * WordPress reserverer 32 px til admin-baren på desktop og 46 px på
         * mobil. Hangar18 skjuler admin-baren på frontend, så reservationen
         * skal fjernes som sidens sidste CSS-regel.
         */
        html,
        html:has(body.admin-bar),
        html body.admin-bar,
        body.admin-bar #page,
        body.admin-bar .h18-theme-main,
        body.admin-bar article.h18-theme-page,
        body.admin-bar .h18-theme-entry-content {
            margin-top:0 !important;
            margin-block-start:0 !important;
            padding-top:0 !important;
            padding-block-start:0 !important;
        }

        body.admin-bar .h18-site-header,
        body.admin-bar .h18-site-header.h18-scroll-sticky {
            top:0 !important;
            inset-block-start:0 !important;
            margin-top:0 !important;
            margin-block-start:0 !important;
        }
        </style>
        <?php
    }

    private function rebuild_vehicle_detail_pages_046() {
        $updated = 0;

        foreach ($this->get_vehicle_pages(false) as $page) {
            $data = $this->decode_marker(
                self::VEHICLE_MARKER,
                $page->post_content
            );

            if (!$data) {
                continue;
            }

            $result = wp_update_post(
                [
                    'ID'           => $page->ID,
                    'post_content' => $this->wrap_with_shell(
                        $this->build_vehicle_core($page->ID, $data),
                        $page->ID
                    ),
                ],
                true
            );

            if (is_wp_error($result)) {
                throw new RuntimeException(
                    "Køretøj ID {$page->ID}: " .
                    $result->get_error_message()
                );
            }

            $updated++;
        }

        return $updated;
    }

    private function rebuild_gallery_detail_pages_046() {
        $updated = 0;

        foreach ($this->get_gallery_pages(false) as $page) {
            $data = $this->decode_marker(
                self::GALLERY_MARKER,
                $page->post_content
            );

            if (!$data) {
                continue;
            }

            $result = wp_update_post(
                [
                    'ID'           => $page->ID,
                    'post_content' => $this->wrap_with_shell(
                        $this->build_gallery_album_core($page->ID, $data),
                        $page->ID
                    ),
                ],
                true
            );

            if (is_wp_error($result)) {
                throw new RuntimeException(
                    "Gallerialbum ID {$page->ID}: " .
                    $result->get_error_message()
                );
            }

            $updated++;
        }

        return $updated;
    }

    public function maybe_run_frontend_repair_046() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::FRONTEND_REPAIR_046_OPTION, false)) {
            return;
        }

        try {
            $this->create_full_managed_backup(
                'Automatisk v0.4.6 frontend-reparation'
            );

            $vehicles = $this->rebuild_vehicle_detail_pages_046();
            $albums = $this->rebuild_gallery_detail_pages_046();

            $this->rebuild_vehicle_register();
            $this->rebuild_gallery_index();

            update_option(
                self::FRONTEND_REPAIR_046_OPTION,
                [
                    'CompletedUtc' => gmdate('c'),
                    'Vehicles'     => $vehicles,
                    'Albums'       => $albums,
                ],
                false
            );

            $this->log(
                'INFO',
                'FRONTEND_REPAIR_046_COMPLETE',
                "v0.4.6 frontend-reparation fuldført. Vehicles={$vehicles}; Albums={$albums}; Events=unchanged."
            );

            $this->set_notice(
                'success',
                "v0.4.6 frontend-reparation er kørt: {$vehicles} køretøjer og {$albums} albums er genbygget. Events er ikke ændret."
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'FRONTEND_REPAIR_046_FAILED',
                $e->getMessage()
            );
        }
    }

    public function register_admin_menu() {
        $capability = 'edit_pages';

        add_menu_page(
            'Hangar18 Manager',
            'Hangar18 Manager',
            $capability,
            self::MENU_SLUG,
            [$this, 'render_dashboard'],
            'dashicons-admin-tools',
            3
        );

        add_submenu_page(self::MENU_SLUG, 'Dashboard', 'Dashboard', $capability, self::MENU_SLUG, [$this, 'render_dashboard']);
        add_submenu_page(self::MENU_SLUG, 'Køretøjer', 'Køretøjer', $capability, 'hangar18-vehicles', [$this, 'render_vehicles']);
        add_submenu_page(self::MENU_SLUG, 'Køretøjsfelter', 'Køretøjsfelter', $capability, 'hangar18-vehicle-fields', [$this, 'render_vehicle_fields']);
        add_submenu_page(self::MENU_SLUG, 'Events', 'Events', $capability, 'hangar18-events', [$this, 'render_events']);
        add_submenu_page(self::MENU_SLUG, 'Billedgalleri', 'Billedgalleri', $capability, 'hangar18-gallery', [$this, 'render_gallery']);
        add_submenu_page(self::MENU_SLUG, 'Data', 'Data', $capability, 'hangar18-data', [$this, 'render_data']);
        add_submenu_page(self::MENU_SLUG, 'Sider', 'Sider', $capability, 'hangar18-pages', [$this, 'render_pages']);
        add_submenu_page(self::MENU_SLUG, 'Menu', 'Menu', $capability, 'hangar18-menu', [$this, 'render_menu']);
        add_submenu_page(self::MENU_SLUG, 'Header / Footer og design', 'Header / Footer', $capability, 'hangar18-header-footer', [$this, 'render_header_footer']);
        add_submenu_page(self::MENU_SLUG, 'Backup', 'Backup', $capability, 'hangar18-backup', [$this, 'render_backup']);
        add_submenu_page(self::MENU_SLUG, 'Opdateringer', 'Opdateringer', $capability, 'hangar18-updates', [$this, 'render_updates']);
        add_submenu_page(self::MENU_SLUG, 'Log', 'Log', $capability, 'hangar18-log', [$this, 'render_log']);
    }

    public function enqueue_admin_assets($hook) {
        if (strpos((string) $hook, 'hangar18') === false) {
            return;
        }

        wp_enqueue_media();
        wp_enqueue_script('jquery-ui-sortable');

        wp_enqueue_style(
            'hangar18-manager-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.css',
            [],
            self::VERSION
        );

        wp_enqueue_script(
            'hangar18-manager-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.js',
            ['jquery', 'jquery-ui-sortable'],
            self::VERSION,
            true
        );

        wp_localize_script('hangar18-manager-admin', 'Hangar18Manager', [
            'chooseImage'       => 'Vælg hovedbillede',
            'useImage'          => 'Brug dette billede',
            'chooseGallery'     => 'Vælg billeder til albummet',
            'useGallery'        => 'Tilføj valgte billeder',
            'removeImage'       => 'Fjern',
            'galleryEmpty'      => 'Albummet har ingen billeder endnu.',
            'ajaxUrl'              => admin_url('admin-ajax.php'),
            'pagePresetNonce'      => wp_create_nonce('h18_page_presets_v051'),
            'pageComponentNonce'   => wp_create_nonce('h18_page_components_v0521'),
            'pageTemplateNonce'    => wp_create_nonce('h18_page_templates_v0522'),
            'conditionUser'        => (function () {
                $user = wp_get_current_user();
                $caps = [];
                foreach ((array) $user->allcaps as $capability => $granted) {
                    if ($granted) { $caps[] = sanitize_key((string) $capability); }
                }
                sort($caps, SORT_STRING);
                return [
                    'LoggedIn' => is_user_logged_in(),
                    'Roles' => array_values(array_map('sanitize_key', (array) $user->roles)),
                    'Capabilities' => array_values(array_unique($caps)),
                ];
            })(),
            'conditionNow'         => wp_date('Y-m-d\TH:i:sP', time(), wp_timezone()),
        ]);
    }

    private function require_capability() {
        if (!current_user_can('edit_pages')) {
            wp_die('Du har ikke rettigheder til Hangar18 Manager.');
        }
    }

    private function bool_value($value, $default = false) {
        if ($value === null) {
            return (bool) $default;
        }

        if (is_bool($value)) {
            return $value;
        }

        if (is_int($value) || is_float($value)) {
            return ((int) $value) !== 0;
        }

        $text = strtolower(trim((string) $value));

        if (in_array($text, ['true', '1', 'yes', 'on'], true)) {
            return true;
        }

        if (in_array($text, ['false', '0', 'no', 'off', ''], true)) {
            return false;
        }

        return (bool) $default;
    }

    private function clamp_int($value, $minimum, $maximum, $default) {
        if (!is_numeric($value)) {
            $value = $default;
        }

        $value = (int) $value;
        return max((int) $minimum, min((int) $maximum, $value));
    }

    private function default_header_design() {
        return [
            'Version' => '2.3',
            'DesignerSchemaVersion' => '1.1',
            'PrimaryColor' => '#30382a',
            'SecondaryColor' => '#525a5f',
            'AccentColor' => '#c3ae83',
            'SurfaceColor' => '#f2f0e8',
            'BackgroundColor' => '#ffffff',
            'TextColor' => '#30382a',
            'LightTextColor' => '#ffffff',
            'ActionColor' => '#8b4a2b',
            'BodyFontFamily' => 'Segoe UI',
            'HeadingFontFamily' => 'Segoe UI',
            'BodyFontSize' => 16,
            'H1FontSize' => 48,
            'H2FontSize' => 32,
            'H3FontSize' => 22,
            'RadiusSmallPx' => 4,
            'RadiusMediumPx' => 7,
            'RadiusLargePx' => 12,
            'SpacingXsPx' => 4,
            'SpacingSmallPx' => 8,
            'SpacingMediumPx' => 16,
            'SpacingLargePx' => 24,
            'SpacingXlPx' => 40,
            'BreakpointMobileMaxPx' => 782,
            'BreakpointTabletMaxPx' => 1199,
            'MotionFastMs' => 120,
            'MotionNormalMs' => 220,
            'MotionSlowMs' => 420,
            'FocusRingColor' => '#8b4a2b',
            'FocusRingWidthPx' => 3,
            'MenuPresentation' => 'Classic',
            'MenuHoverEffect' => 'None',
            'MenuActiveStyle' => 'None',
            'MenuTransitionMs' => 180,
            'SubmenuAnimation' => 'None',
            'VisualBaseScalePercent' => 90,
            'MenuAlignment' => 'Right',
            'PositionMode' => 'Normal',
            'StickyOnScroll' => false,
            'BackgroundMode' => 'None',
            'WidthMode' => 'Contained',
            'ShowBrand' => true,
            'BrandText' => 'Aalborg Kaserners Veteran Panser- og Køretøjsforening',
            'IdentityAlignment' => 'Center',
            'BrandFontSize' => 22,
            'BrandSizePercent' => 100,
            'ShowLogo' => false,
            'LogoMediaId' => 0,
            'LogoUrl' => '',
            'LogoWidthPx' => 52,
            'LogoSizePercent' => 100,
            'MobileStyle' => 'Dark',
            'MenuFontSize' => 15,
            'MenuSizePercent' => 100,
            'MenuFontFamily' => 'Segoe UI',
            'MenuFontWeight' => 'Semibold',
            'MenuFontItalic' => false,
            'MenuUppercase' => false,
            'ResponsiveScaleEnabled' => true,
            'ResponsiveLargeWidthPx' => 2560,
            'ResponsiveLaptopWidthPx' => 1920,
            'ResponsiveLaptopScalePercent' => 90,
            'ResponsiveMinimumScalePercent' => 90,
            'DesktopContentWidthPercent' => 80,
            'LaptopContentWidthPercent' => 90,
            'MaximumDesktopContentWidthPercent' => 90,
            'ContentMaxWidth' => 'None',
            'FooterWidthPercent' => 100,
            'SectionSpacingPx' => 32,
            'MobileSectionSpacingPx' => 24,
            'ContentTopSpacingPx' => 32,
            'ContentBottomSpacingPx' => 32,
            'MobileContentTopSpacingPx' => 24,
            'MobileContentBottomSpacingPx' => 24
        ];
    }

    private function normalize_header_design(array $saved) {
        $default = $this->default_header_design();

        $allowed_alignments = ['Left', 'Center', 'Right'];
        $allowed_positions = ['Normal', 'Sticky', 'Floating', 'Overlay'];
        $allowed_backgrounds = ['None', 'Bar', 'Box', 'Glass'];
        $allowed_widths = ['Full', 'Contained', 'Narrow'];
        $allowed_mobile = ['Dark', 'Transparent'];
        $allowed_fonts = [
            'System',
            'Segoe UI',
            'Arial',
            'Verdana',
            'Tahoma',
            'Trebuchet MS',
            'Georgia',
            'Times New Roman',
            'Courier New',
        ];
        $allowed_weights = ['Normal', 'Medium', 'Semibold', 'Bold'];
        $allowed_max_widths = ['None', '1400', '1600', '1800', '2000'];
        $allowed_menu_presentations = ['Classic', 'FloatingPill', 'Framed'];
        $allowed_menu_hover = ['None', 'Underline', 'Lift', 'Pill'];
        $allowed_menu_active = ['None', 'Underline', 'Pill', 'Dot'];
        $allowed_submenu_animations = ['None', 'Fade', 'FadeSlide', 'Scale'];
        $normalize_color = static function($value, $fallback) {
            $color = sanitize_hex_color((string) $value);
            return $color ?: $fallback;
        };

        $position = in_array(
            (string) ($saved['PositionMode'] ?? ''),
            $allowed_positions,
            true
        )
            ? (string) $saved['PositionMode']
            : $default['PositionMode'];

        $brand_text = trim((string) ($saved['BrandText'] ?? ''));
        if ($brand_text === '') {
            $brand_text = $default['BrandText'];
        }

        $content_max_width = (string) ($saved['ContentMaxWidth'] ?? '');
        if (!in_array($content_max_width, $allowed_max_widths, true)) {
            $content_max_width = $default['ContentMaxWidth'];
        }

        return [
            'Version'                           => '2.3',
            'DesignerSchemaVersion'             => '1.1',
            'PrimaryColor'                      => $normalize_color($saved['PrimaryColor'] ?? $default['PrimaryColor'], $default['PrimaryColor']),
            'SecondaryColor'                    => $normalize_color($saved['SecondaryColor'] ?? $default['SecondaryColor'], $default['SecondaryColor']),
            'AccentColor'                       => $normalize_color($saved['AccentColor'] ?? $default['AccentColor'], $default['AccentColor']),
            'SurfaceColor'                      => $normalize_color($saved['SurfaceColor'] ?? $default['SurfaceColor'], $default['SurfaceColor']),
            'BackgroundColor'                   => $normalize_color($saved['BackgroundColor'] ?? $default['BackgroundColor'], $default['BackgroundColor']),
            'TextColor'                         => $normalize_color($saved['TextColor'] ?? $default['TextColor'], $default['TextColor']),
            'LightTextColor'                    => $normalize_color($saved['LightTextColor'] ?? $default['LightTextColor'], $default['LightTextColor']),
            'ActionColor'                       => $normalize_color($saved['ActionColor'] ?? $default['ActionColor'], $default['ActionColor']),
            'BodyFontFamily'                    => in_array((string) ($saved['BodyFontFamily'] ?? ''), $allowed_fonts, true) ? (string) $saved['BodyFontFamily'] : $default['BodyFontFamily'],
            'HeadingFontFamily'                 => in_array((string) ($saved['HeadingFontFamily'] ?? ''), $allowed_fonts, true) ? (string) $saved['HeadingFontFamily'] : $default['HeadingFontFamily'],
            'BodyFontSize'                      => $this->clamp_int($saved['BodyFontSize'] ?? $default['BodyFontSize'], 12, 24, $default['BodyFontSize']),
            'H1FontSize'                        => $this->clamp_int($saved['H1FontSize'] ?? $default['H1FontSize'], 24, 88, $default['H1FontSize']),
            'H2FontSize'                        => $this->clamp_int($saved['H2FontSize'] ?? $default['H2FontSize'], 20, 64, $default['H2FontSize']),
            'H3FontSize'                        => $this->clamp_int($saved['H3FontSize'] ?? $default['H3FontSize'], 16, 48, $default['H3FontSize']),
            'RadiusSmallPx'                     => $this->clamp_int($saved['RadiusSmallPx'] ?? $default['RadiusSmallPx'], 0, 30, $default['RadiusSmallPx']),
            'RadiusMediumPx'                    => $this->clamp_int($saved['RadiusMediumPx'] ?? $default['RadiusMediumPx'], 0, 40, $default['RadiusMediumPx']),
            'RadiusLargePx'                     => $this->clamp_int($saved['RadiusLargePx'] ?? $default['RadiusLargePx'], 0, 60, $default['RadiusLargePx']),
            'SpacingXsPx'                       => $this->clamp_int($saved['SpacingXsPx'] ?? $default['SpacingXsPx'], 0, 24, $default['SpacingXsPx']),
            'SpacingSmallPx'                    => $this->clamp_int($saved['SpacingSmallPx'] ?? $default['SpacingSmallPx'], 0, 40, $default['SpacingSmallPx']),
            'SpacingMediumPx'                   => $this->clamp_int($saved['SpacingMediumPx'] ?? $default['SpacingMediumPx'], 0, 64, $default['SpacingMediumPx']),
            'SpacingLargePx'                    => $this->clamp_int($saved['SpacingLargePx'] ?? $default['SpacingLargePx'], 0, 96, $default['SpacingLargePx']),
            'SpacingXlPx'                       => $this->clamp_int($saved['SpacingXlPx'] ?? $default['SpacingXlPx'], 0, 140, $default['SpacingXlPx']),
            'BreakpointMobileMaxPx'             => $this->clamp_int($saved['BreakpointMobileMaxPx'] ?? $default['BreakpointMobileMaxPx'], 480, 900, $default['BreakpointMobileMaxPx']),
            'BreakpointTabletMaxPx'             => $this->clamp_int($saved['BreakpointTabletMaxPx'] ?? $default['BreakpointTabletMaxPx'], 901, 1600, $default['BreakpointTabletMaxPx']),
            'MotionFastMs'                      => $this->clamp_int($saved['MotionFastMs'] ?? $default['MotionFastMs'], 0, 1000, $default['MotionFastMs']),
            'MotionNormalMs'                    => $this->clamp_int($saved['MotionNormalMs'] ?? $default['MotionNormalMs'], 0, 1500, $default['MotionNormalMs']),
            'MotionSlowMs'                      => $this->clamp_int($saved['MotionSlowMs'] ?? $default['MotionSlowMs'], 0, 2500, $default['MotionSlowMs']),
            'FocusRingColor'                    => $normalize_color($saved['FocusRingColor'] ?? $default['FocusRingColor'], $default['FocusRingColor']),
            'FocusRingWidthPx'                  => $this->clamp_int($saved['FocusRingWidthPx'] ?? $default['FocusRingWidthPx'], 1, 8, $default['FocusRingWidthPx']),
            'MenuPresentation'                  => in_array((string) ($saved['MenuPresentation'] ?? ''), $allowed_menu_presentations, true) ? (string) $saved['MenuPresentation'] : $default['MenuPresentation'],
            'MenuHoverEffect'                   => in_array((string) ($saved['MenuHoverEffect'] ?? ''), $allowed_menu_hover, true) ? (string) $saved['MenuHoverEffect'] : $default['MenuHoverEffect'],
            'MenuActiveStyle'                   => in_array((string) ($saved['MenuActiveStyle'] ?? ''), $allowed_menu_active, true) ? (string) $saved['MenuActiveStyle'] : $default['MenuActiveStyle'],
            'MenuTransitionMs'                  => $this->clamp_int($saved['MenuTransitionMs'] ?? $default['MenuTransitionMs'], 0, 1200, $default['MenuTransitionMs']),
            'SubmenuAnimation'                  => in_array((string) ($saved['SubmenuAnimation'] ?? ''), $allowed_submenu_animations, true) ? (string) $saved['SubmenuAnimation'] : $default['SubmenuAnimation'],
            'VisualBaseScalePercent'            => $this->clamp_int($saved['VisualBaseScalePercent'] ?? $default['VisualBaseScalePercent'], 50, 100, $default['VisualBaseScalePercent']),
            'MenuAlignment'                     => in_array((string) ($saved['MenuAlignment'] ?? ''), $allowed_alignments, true) ? (string) $saved['MenuAlignment'] : $default['MenuAlignment'],
            'PositionMode'                      => $position,
            'StickyOnScroll'                    => array_key_exists('StickyOnScroll', $saved) ? $this->bool_value($saved['StickyOnScroll'], $default['StickyOnScroll']) : $default['StickyOnScroll'],
            'BackgroundMode'                    => in_array((string) ($saved['BackgroundMode'] ?? ''), $allowed_backgrounds, true) ? (string) $saved['BackgroundMode'] : $default['BackgroundMode'],
            'WidthMode'                         => in_array((string) ($saved['WidthMode'] ?? ''), $allowed_widths, true) ? (string) $saved['WidthMode'] : $default['WidthMode'],
            'ShowBrand'                         => array_key_exists('ShowBrand', $saved) ? $this->bool_value($saved['ShowBrand'], $default['ShowBrand']) : $default['ShowBrand'],
            'BrandText'                         => $brand_text,
            'IdentityAlignment'                 => in_array((string) ($saved['IdentityAlignment'] ?? ''), $allowed_alignments, true) ? (string) $saved['IdentityAlignment'] : $default['IdentityAlignment'],
            'BrandFontSize'                     => $this->clamp_int($saved['BrandFontSize'] ?? $default['BrandFontSize'], 12, 36, $default['BrandFontSize']),
            'BrandSizePercent'                  => $this->clamp_int($saved['BrandSizePercent'] ?? $default['BrandSizePercent'], 50, 150, $default['BrandSizePercent']),
            'ShowLogo'                          => array_key_exists('ShowLogo', $saved) ? $this->bool_value($saved['ShowLogo'], $default['ShowLogo']) : $default['ShowLogo'],
            'LogoMediaId'                       => max(0, (int) ($saved['LogoMediaId'] ?? $default['LogoMediaId'])),
            'LogoUrl'                           => (string) ($saved['LogoUrl'] ?? $default['LogoUrl']),
            'LogoWidthPx'                       => $this->clamp_int($saved['LogoWidthPx'] ?? $default['LogoWidthPx'], 24, 200, $default['LogoWidthPx']),
            'LogoSizePercent'                   => $this->clamp_int($saved['LogoSizePercent'] ?? $default['LogoSizePercent'], 50, 150, $default['LogoSizePercent']),
            'MobileStyle'                       => in_array((string) ($saved['MobileStyle'] ?? ''), $allowed_mobile, true) ? (string) $saved['MobileStyle'] : $default['MobileStyle'],
            'MenuFontSize'                      => $this->clamp_int($saved['MenuFontSize'] ?? $default['MenuFontSize'], 11, 28, $default['MenuFontSize']),
            'MenuSizePercent'                   => $this->clamp_int($saved['MenuSizePercent'] ?? $default['MenuSizePercent'], 50, 150, $default['MenuSizePercent']),
            'MenuFontFamily'                    => in_array((string) ($saved['MenuFontFamily'] ?? ''), $allowed_fonts, true) ? (string) $saved['MenuFontFamily'] : $default['MenuFontFamily'],
            'MenuFontWeight'                    => in_array((string) ($saved['MenuFontWeight'] ?? ''), $allowed_weights, true) ? (string) $saved['MenuFontWeight'] : $default['MenuFontWeight'],
            'MenuFontItalic'                    => array_key_exists('MenuFontItalic', $saved) ? $this->bool_value($saved['MenuFontItalic'], $default['MenuFontItalic']) : $default['MenuFontItalic'],
            'MenuUppercase'                     => array_key_exists('MenuUppercase', $saved) ? $this->bool_value($saved['MenuUppercase'], $default['MenuUppercase']) : $default['MenuUppercase'],
            'ResponsiveScaleEnabled'            => array_key_exists('ResponsiveScaleEnabled', $saved) ? $this->bool_value($saved['ResponsiveScaleEnabled'], $default['ResponsiveScaleEnabled']) : $default['ResponsiveScaleEnabled'],
            'ResponsiveLargeWidthPx'            => $this->clamp_int($saved['ResponsiveLargeWidthPx'] ?? $default['ResponsiveLargeWidthPx'], 1600, 5120, $default['ResponsiveLargeWidthPx']),
            'ResponsiveLaptopWidthPx'           => $this->clamp_int($saved['ResponsiveLaptopWidthPx'] ?? $default['ResponsiveLaptopWidthPx'], 1200, 3000, $default['ResponsiveLaptopWidthPx']),
            'ResponsiveLaptopScalePercent'      => $this->clamp_int($saved['ResponsiveLaptopScalePercent'] ?? $default['ResponsiveLaptopScalePercent'], 60, 100, $default['ResponsiveLaptopScalePercent']),
            'ResponsiveMinimumScalePercent'     => $this->clamp_int($saved['ResponsiveMinimumScalePercent'] ?? $default['ResponsiveMinimumScalePercent'], 50, 100, $default['ResponsiveMinimumScalePercent']),
            'DesktopContentWidthPercent'        => $this->clamp_int($saved['DesktopContentWidthPercent'] ?? $default['DesktopContentWidthPercent'], 50, 100, $default['DesktopContentWidthPercent']),
            'LaptopContentWidthPercent'         => $this->clamp_int($saved['LaptopContentWidthPercent'] ?? $default['LaptopContentWidthPercent'], 70, 98, $default['LaptopContentWidthPercent']),
            'MaximumDesktopContentWidthPercent' => max(
                $this->clamp_int($saved['DesktopContentWidthPercent'] ?? $default['DesktopContentWidthPercent'], 50, 100, $default['DesktopContentWidthPercent']),
                $this->clamp_int($saved['MaximumDesktopContentWidthPercent'] ?? $default['MaximumDesktopContentWidthPercent'], 70, 100, $default['MaximumDesktopContentWidthPercent'])
            ),
            'ContentMaxWidth'                   => $content_max_width,
            'FooterWidthPercent'                => $this->clamp_int($saved['FooterWidthPercent'] ?? $default['FooterWidthPercent'], 50, 100, $default['FooterWidthPercent']),
            'SectionSpacingPx'                  => $this->clamp_int($saved['SectionSpacingPx'] ?? $default['SectionSpacingPx'], 0, 120, $default['SectionSpacingPx']),
            'MobileSectionSpacingPx'            => $this->clamp_int($saved['MobileSectionSpacingPx'] ?? $default['MobileSectionSpacingPx'], 0, 80, $default['MobileSectionSpacingPx']),
            'ContentTopSpacingPx'               => $this->clamp_int($saved['ContentTopSpacingPx'] ?? $default['ContentTopSpacingPx'], 0, 120, $default['ContentTopSpacingPx']),
            'ContentBottomSpacingPx'            => $this->clamp_int($saved['ContentBottomSpacingPx'] ?? $default['ContentBottomSpacingPx'], 0, 120, $default['ContentBottomSpacingPx']),
            'MobileContentTopSpacingPx'         => $this->clamp_int($saved['MobileContentTopSpacingPx'] ?? $default['MobileContentTopSpacingPx'], 0, 80, $default['MobileContentTopSpacingPx']),
            'MobileContentBottomSpacingPx'      => $this->clamp_int($saved['MobileContentBottomSpacingPx'] ?? $default['MobileContentBottomSpacingPx'], 0, 80, $default['MobileContentBottomSpacingPx']),
        ];
    }

    private function default_vehicle_register_settings() {
        return [
            'Version'                   => '1.4',
            'Saved'                     => '2026-08-13T08:19:43.3711647+02:00',
            'RegisterAlignment'         => 'Center',
            'CardAlignment'             => 'Center',
            'DetailAlignment'           => 'Center',
            'MobileRegisterAlignment'   => 'Center',
            'MobileDetailAlignment'     => 'Center',
        ];
    }

    private function normalize_vehicle_register_settings(array $saved) {
        $default = $this->default_vehicle_register_settings();

        $legacy_card = (string) ($saved['CardAlignment'] ?? '');
        $register_source = (string) ($saved['RegisterAlignment'] ?? $legacy_card);

        $register = in_array($register_source, ['Left', 'Center'], true)
            ? $register_source
            : $default['RegisterAlignment'];

        $detail_source = (string) ($saved['DetailAlignment'] ?? '');
        if ($detail_source === 'Auto') {
            // v1.2 Auto var centreret på desktop; bevar derfor det visuelle udgangspunkt.
            $detail_source = 'Center';
        }

        $detail = in_array($detail_source, ['Left', 'Center'], true)
            ? $detail_source
            : $default['DetailAlignment'];

        $mobile_register_source = (string) ($saved['MobileRegisterAlignment'] ?? '');
        $mobile_register = in_array($mobile_register_source, ['Left', 'Center'], true)
            ? $mobile_register_source
            : $default['MobileRegisterAlignment'];

        $mobile_detail_source = (string) ($saved['MobileDetailAlignment'] ?? '');
        $mobile_detail = in_array($mobile_detail_source, ['Left', 'Center'], true)
            ? $mobile_detail_source
            : $default['MobileDetailAlignment'];

        return [
            'Version'                   => '1.4',
            'RegisterAlignment'         => $register,
            // CardAlignment bevares som data-alias for eksisterende installationer.
            'CardAlignment'             => $register,
            'DetailAlignment'           => $detail,
            'MobileRegisterAlignment'   => $mobile_register,
            'MobileDetailAlignment'     => $mobile_detail,
        ];
    }

    private function vehicle_legacy_field_map() {
        return [
            'type'               => 'Type',
            'manufacturer'       => 'Manufacturer',
            'production_year'    => 'ProductionYear',
            'engine'             => 'Engine',
            'weight'             => 'Weight',
            'crew'               => 'Crew',
            'service_period'     => 'ServicePeriod',
            'restoration_status' => 'RestorationStatus',
        ];
    }

    private function vehicle_field_type_labels() {
        return [
            'text'     => 'Kort tekst',
            'textarea' => 'Lang tekst',
            'number'   => 'Tal',
            'boolean'  => 'Ja / Nej',
            'select'   => 'Dropdown',
            'date'     => 'Dato',
            'url'      => 'URL / link',
            'color'    => 'Farvevælger',
        ];
    }

    private function default_vehicle_field_settings() {
        return [
            'Version' => '1.0',
            'Fields'  => [
                ['Key'=>'type',               'Label'=>'Type',                  'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>true,  'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>10],
                ['Key'=>'manufacturer',       'Label'=>'Producent',             'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>true,  'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>20],
                ['Key'=>'production_year',    'Label'=>'Produktionsår',         'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>true,  'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>30],
                ['Key'=>'engine',             'Label'=>'Motor',                 'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>false, 'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>40],
                ['Key'=>'weight',             'Label'=>'Vægt',                  'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>true,  'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>50],
                ['Key'=>'crew',               'Label'=>'Besætning',             'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>false, 'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>60],
                ['Key'=>'service_period',     'Label'=>'Tjenesteperiode',       'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>false, 'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>70],
                ['Key'=>'restoration_status', 'Label'=>'Restaureringsstatus',   'Type'=>'text', 'Active'=>true,  'ShowOnRegister'=>true,  'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>80],
                ['Key'=>'color',              'Label'=>'Farve',                 'Type'=>'text', 'Active'=>false, 'ShowOnRegister'=>false, 'ShowOnDetail'=>true,  'Options'=>[], 'Order'=>90],
            ],
        ];
    }

    private function normalize_vehicle_field_settings(array $saved) {
        $types = array_keys($this->vehicle_field_type_labels());
        $source_fields = isset($saved['Fields']) && is_array($saved['Fields'])
            ? $saved['Fields']
            : [];

        $fields = [];
        $seen = [];
        $order_fallback = 10;

        foreach ($source_fields as $source) {
            if (!is_array($source)) {
                continue;
            }

            $key = sanitize_key((string) ($source['Key'] ?? ''));
            $label = trim((string) ($source['Label'] ?? ''));

            if ($key === '' || $label === '' || isset($seen[$key])) {
                continue;
            }

            $type = sanitize_key((string) ($source['Type'] ?? 'text'));
            if (!in_array($type, $types, true)) {
                $type = 'text';
            }

            $options = $source['Options'] ?? [];
            if (is_string($options)) {
                $options = preg_split('/[\r\n,;]+/', $options);
            }
            if (!is_array($options)) {
                $options = [];
            }
            $options = array_values(array_filter(array_map(static function($value) {
                return sanitize_text_field((string) $value);
            }, $options), static function($value) {
                return $value !== '';
            }));

            $order = is_numeric($source['Order'] ?? null)
                ? max(1, (int) $source['Order'])
                : $order_fallback;

            $fields[] = [
                'Key'            => $key,
                'Label'          => sanitize_text_field($label),
                'Type'           => $type,
                'Active'         => $this->bool_value($source['Active'] ?? false),
                'ShowOnRegister' => $this->bool_value($source['ShowOnRegister'] ?? false),
                'ShowOnDetail'   => $this->bool_value($source['ShowOnDetail'] ?? true, true),
                'Options'        => $options,
                'Order'          => $order,
            ];

            $seen[$key] = true;
            $order_fallback += 10;
        }

        usort($fields, static function($a, $b) {
            $cmp = ((int) $a['Order']) <=> ((int) $b['Order']);
            return $cmp !== 0 ? $cmp : strcmp((string) $a['Label'], (string) $b['Label']);
        });

        foreach ($fields as $index => &$field) {
            $field['Order'] = ($index + 1) * 10;
        }
        unset($field);

        return [
            'Version' => '1.0',
            'Fields'  => $fields,
        ];
    }

    private function get_vehicle_field_settings() {
        $stored = get_option(self::VEHICLE_FIELDS_OPTION, null);

        if (!is_array($stored)) {
            return $this->default_vehicle_field_settings();
        }

        return $this->normalize_vehicle_field_settings($stored);
    }

    private function get_vehicle_fields($active_only = false) {
        $settings = $this->get_vehicle_field_settings();
        $fields = is_array($settings['Fields'] ?? null) ? $settings['Fields'] : [];

        if (!$active_only) {
            return $fields;
        }

        return array_values(array_filter($fields, static function($field) {
            return !empty($field['Active']);
        }));
    }

    private function vehicle_field_value(array $data, $key, $default = '') {
        $key = sanitize_key((string) $key);
        $custom = isset($data['CustomFields']) && is_array($data['CustomFields'])
            ? $data['CustomFields']
            : [];

        if (array_key_exists($key, $custom)) {
            return (string) $custom[$key];
        }

        $legacy_map = $this->vehicle_legacy_field_map();
        if (isset($legacy_map[$key]) && array_key_exists($legacy_map[$key], $data)) {
            return (string) $data[$legacy_map[$key]];
        }

        return (string) $default;
    }

    private function sanitize_vehicle_field_value(array $field, $raw) {
        $type = (string) ($field['Type'] ?? 'text');
        $raw = is_scalar($raw) ? (string) wp_unslash($raw) : '';

        switch ($type) {
            case 'textarea':
                return sanitize_textarea_field($raw);
            case 'number':
                $value = trim($raw);
                return preg_match('/^-?[0-9]+(?:[\.,][0-9]+)?$/', $value)
                    ? str_replace(',', '.', $value)
                    : sanitize_text_field($value);
            case 'boolean':
                return in_array(strtolower(trim($raw)), ['1','true','yes','ja','on'], true) ? '1' : '0';
            case 'date':
                $value = sanitize_text_field($raw);
                return preg_match('/^\d{4}-\d{2}-\d{2}$/', $value) ? $value : '';
            case 'url':
                return esc_url_raw($raw);
            case 'color':
                $value = sanitize_hex_color($raw);
                return $value ?: '';
            case 'select':
                $value = sanitize_text_field($raw);
                $options = is_array($field['Options'] ?? null) ? $field['Options'] : [];
                return in_array($value, $options, true) ? $value : '';
            case 'text':
            default:
                return sanitize_text_field($raw);
        }
    }

    private function format_vehicle_field_value(array $field, $value) {
        $value = (string) $value;
        if ($value === '') {
            return '<span class="h18-field-empty">—</span>';
        }

        switch ((string) ($field['Type'] ?? 'text')) {
            case 'textarea':
                return nl2br(esc_html($value), false);
            case 'boolean':
                return $value === '1' ? 'Ja' : 'Nej';
            case 'url':
                return '<a href="' . esc_url($value) . '" target="_blank" rel="noopener">' . esc_html($value) . '</a>';
            case 'color':
                $safe = sanitize_hex_color($value);
                if (!$safe) {
                    return esc_html($value);
                }
                return '<span class="h18-color-value"><span class="h18-color-swatch" style="background:' . esc_attr($safe) . '"></span>' . esc_html($safe) . '</span>';
            default:
                return esc_html($value);
        }
    }

    private function build_vehicle_field_rows(array $data, $context) {
        $rows = '';
        foreach ($this->get_vehicle_fields(true) as $field) {
            $show = $context === 'register'
                ? !empty($field['ShowOnRegister'])
                : !empty($field['ShowOnDetail']);

            if (!$show) {
                continue;
            }

            $value = $this->vehicle_field_value($data, $field['Key']);
            $rows .= '<tr><th>' . esc_html($field['Label']) . '</th><td>' .
                $this->format_vehicle_field_value($field, $value) . '</td></tr>';
        }

        if ($rows === '') {
            $rows = '<tr><td colspan="2"><span class="h18-field-empty">Ingen aktive felter er valgt til denne visning.</span></td></tr>';
        }

        return $rows;
    }

    private function render_vehicle_dynamic_field(array $field, $value) {
        $key = (string) $field['Key'];
        $label = (string) $field['Label'];
        $type = (string) $field['Type'];
        $name = 'vehicle_fields[' . $key . ']';
        $id = 'h18-vehicle-field-' . $key;
        ?>
        <div class="h18-field">
            <label for="<?php echo esc_attr($id); ?>"><strong><?php echo esc_html($label); ?></strong></label>
            <?php if ($type === 'textarea') : ?>
                <textarea id="<?php echo esc_attr($id); ?>" name="<?php echo esc_attr($name); ?>" rows="4"><?php echo esc_textarea($value); ?></textarea>
            <?php elseif ($type === 'boolean') : ?>
                <input type="hidden" name="<?php echo esc_attr($name); ?>" value="0" />
                <label class="h18-inline-check"><input id="<?php echo esc_attr($id); ?>" type="checkbox" name="<?php echo esc_attr($name); ?>" value="1" <?php checked((string) $value, '1'); ?> /> Ja</label>
            <?php elseif ($type === 'select') : ?>
                <select id="<?php echo esc_attr($id); ?>" name="<?php echo esc_attr($name); ?>">
                    <option value="">— Vælg —</option>
                    <?php foreach (($field['Options'] ?? []) as $option) : ?>
                        <option value="<?php echo esc_attr($option); ?>" <?php selected((string) $value, (string) $option); ?>><?php echo esc_html($option); ?></option>
                    <?php endforeach; ?>
                </select>
            <?php else : ?>
                <?php
                $html_type = 'text';
                if ($type === 'number') { $html_type = 'text'; }
                elseif ($type === 'date') { $html_type = 'date'; }
                elseif ($type === 'url') { $html_type = 'url'; }
                elseif ($type === 'color') { $html_type = 'color'; }
                ?>
                <input id="<?php echo esc_attr($id); ?>" type="<?php echo esc_attr($html_type); ?>" name="<?php echo esc_attr($name); ?>" value="<?php echo esc_attr($value); ?>" />
            <?php endif; ?>
            <p class="description">Nøgle: <code><?php echo esc_html($key); ?></code></p>
        </div>
        <?php
    }

    private function default_content_layout_settings() {
        return [
            'Version'                      => '1.2',
            'EventIndexAlignment'          => 'Left',
            'EventDetailAlignment'         => 'Left',
            'GalleryIndexAlignment'        => 'Left',
            'GalleryDetailAlignment'       => 'Left',
            'MobileEventIndexAlignment'    => 'Center',
            'MobileEventDetailAlignment'   => 'Center',
            'MobileGalleryIndexAlignment'  => 'Center',
            'MobileGalleryDetailAlignment' => 'Center',
        ];
    }

    private function normalize_content_layout_settings(array $saved) {
        $default = $this->default_content_layout_settings();

        $legacy_event = (string) ($saved['EventAlignment'] ?? '');
        $legacy_gallery = (string) ($saved['GalleryAlignment'] ?? '');

        $event_index_source = (string) ($saved['EventIndexAlignment'] ?? $legacy_event);
        $event_detail_source = (string) ($saved['EventDetailAlignment'] ?? $legacy_event);
        $gallery_index_source = (string) ($saved['GalleryIndexAlignment'] ?? $legacy_gallery);
        $gallery_detail_source = (string) ($saved['GalleryDetailAlignment'] ?? $legacy_gallery);
        $mobile_event_index_source = (string) ($saved['MobileEventIndexAlignment'] ?? '');
        $mobile_event_detail_source = (string) ($saved['MobileEventDetailAlignment'] ?? '');
        $mobile_gallery_index_source = (string) ($saved['MobileGalleryIndexAlignment'] ?? '');
        $mobile_gallery_detail_source = (string) ($saved['MobileGalleryDetailAlignment'] ?? '');

        $normalize_alignment = static function($value, $fallback) {
            return in_array((string) $value, ['Left', 'Center'], true)
                ? (string) $value
                : $fallback;
        };

        return [
            'Version'                      => '1.2',
            'EventIndexAlignment'          => $normalize_alignment($event_index_source, $default['EventIndexAlignment']),
            'EventDetailAlignment'         => $normalize_alignment($event_detail_source, $default['EventDetailAlignment']),
            'GalleryIndexAlignment'        => $normalize_alignment($gallery_index_source, $default['GalleryIndexAlignment']),
            'GalleryDetailAlignment'       => $normalize_alignment($gallery_detail_source, $default['GalleryDetailAlignment']),
            'MobileEventIndexAlignment'    => $normalize_alignment($mobile_event_index_source, $default['MobileEventIndexAlignment']),
            'MobileEventDetailAlignment'   => $normalize_alignment($mobile_event_detail_source, $default['MobileEventDetailAlignment']),
            'MobileGalleryIndexAlignment'  => $normalize_alignment($mobile_gallery_index_source, $default['MobileGalleryIndexAlignment']),
            'MobileGalleryDetailAlignment' => $normalize_alignment($mobile_gallery_detail_source, $default['MobileGalleryDetailAlignment']),
        ];
    }

    private function default_static_content_settings() {
        return [
            'Version'                 => '1.0',
            'PageSlug'                => 'om-foreningen',
            'Heading'                 => 'Foreningens formål',
            'Intro'                   => "Foreningens formål er at indsamle, restaurere, vedligeholde og bevare militærhistorisk materiel samt formidle materiellets historie.\n\nDer lægges særlig vægt på bælte-, hjul- og hestekøretøjer samt andre effekter, der gennem tiden har været i brug ved Aalborg Kaserner.",
            'CardsTopSpacingPx'       => 24,
            'CardGapPx'               => 20,
            'MobileCardsTopSpacingPx' => 18,
            'MobileCardGapPx'         => 14,
            'CardPaddingPx'           => 26,
            'MobileCardPaddingPx'     => 20,
            'CardRadiusPx'            => 7,
            'Sections'                => [
                [
                    'Key'    => 'bevaring',
                    'Title'  => 'Bevaring',
                    'Body'   => 'Materiellet bevares som en del af den lokale og militære historie omkring Aalborg Kaserner.',
                    'Active' => true,
                    'Order'  => 10,
                ],
                [
                    'Key'    => 'restaurering',
                    'Title'  => 'Restaurering',
                    'Body'   => 'Historiske køretøjer og effekter vedligeholdes og restaureres med fokus på at bevare deres historiske udtryk og funktion.',
                    'Active' => true,
                    'Order'  => 20,
                ],
                [
                    'Key'    => 'formidling',
                    'Title'  => 'Formidling',
                    'Body'   => 'Foreningen arbejder for at gøre historien om materiellet tilgængelig gennem aktiviteter, billeder, fortællinger og arrangementer.',
                    'Active' => true,
                    'Order'  => 30,
                ],
            ],
        ];
    }

    private function normalize_static_content_settings(array $saved) {
        $default = $this->default_static_content_settings();
        $heading = sanitize_text_field((string) ($saved['Heading'] ?? ''));
        if ($heading === '') {
            $heading = $default['Heading'];
        }

        $raw_sections = array_key_exists('Sections', $saved) && is_array($saved['Sections'])
            ? $saved['Sections']
            : $default['Sections'];
        $sections = [];
        $used_keys = [];
        $fallback_order = 10;

        foreach (array_slice($raw_sections, 0, 30) as $index => $raw) {
            if (!is_array($raw)) {
                continue;
            }

            $title = sanitize_text_field((string) ($raw['Title'] ?? ''));
            $body = sanitize_textarea_field((string) ($raw['Body'] ?? ''));
            if ($title === '' && $body === '') {
                continue;
            }

            $key = sanitize_key((string) ($raw['Key'] ?? ''));
            if ($key === '') {
                $key = sanitize_key(sanitize_title($title));
            }
            if ($key === '') {
                $key = 'sektion_' . ((int) $index + 1);
            }

            $base_key = $key;
            $suffix = 2;
            while (isset($used_keys[$key])) {
                $key = $base_key . '_' . $suffix++;
            }
            $used_keys[$key] = true;

            $sections[] = [
                'Key'    => $key,
                'Title'  => $title,
                'Body'   => $body,
                'Active' => array_key_exists('Active', $raw)
                    ? $this->bool_value($raw['Active'], false)
                    : true,
                'Order'  => $this->clamp_int($raw['Order'] ?? $fallback_order, 1, 10000, $fallback_order),
            ];
            $fallback_order += 10;
        }

        usort($sections, static function($a, $b) {
            return ((int) $a['Order']) <=> ((int) $b['Order']);
        });

        return [
            'Version'                 => '1.0',
            'PageSlug'                => 'om-foreningen',
            'Heading'                 => $heading,
            'Intro'                   => sanitize_textarea_field((string) ($saved['Intro'] ?? $default['Intro'])),
            'CardsTopSpacingPx'       => $this->clamp_int($saved['CardsTopSpacingPx'] ?? $default['CardsTopSpacingPx'], 0, 120, $default['CardsTopSpacingPx']),
            'CardGapPx'               => $this->clamp_int($saved['CardGapPx'] ?? $default['CardGapPx'], 0, 80, $default['CardGapPx']),
            'MobileCardsTopSpacingPx' => $this->clamp_int($saved['MobileCardsTopSpacingPx'] ?? $default['MobileCardsTopSpacingPx'], 0, 80, $default['MobileCardsTopSpacingPx']),
            'MobileCardGapPx'         => $this->clamp_int($saved['MobileCardGapPx'] ?? $default['MobileCardGapPx'], 0, 60, $default['MobileCardGapPx']),
            'CardPaddingPx'           => $this->clamp_int($saved['CardPaddingPx'] ?? $default['CardPaddingPx'], 0, 80, $default['CardPaddingPx']),
            'MobileCardPaddingPx'     => $this->clamp_int($saved['MobileCardPaddingPx'] ?? $default['MobileCardPaddingPx'], 0, 60, $default['MobileCardPaddingPx']),
            'CardRadiusPx'            => $this->clamp_int($saved['CardRadiusPx'] ?? $default['CardRadiusPx'], 0, 30, $default['CardRadiusPx']),
            'Sections'                => $sections,
        ];
    }

    private function get_static_content_settings() {
        $stored = get_option(self::STATIC_CONTENT_OPTION, []);
        if (!is_array($stored) || !$stored) {
            return $this->default_static_content_settings();
        }
        return $this->normalize_static_content_settings($stored);
    }

    private function default_menu_order_settings() {
        return [
            'Version' => '1.0',
            'Saved' => '2026-08-12T06:53:38.5469021+02:00',
            'Order' => [
                'hjem',
                'koeretoejer-og-materiel',
                'events',
                'billedgalleri',
                'bliv-medlem',
                'kontakt',
                'om-foreningen'
            ]
        ];
    }

    private function normalize_menu_order_settings(array $saved) {
        $default = $this->default_menu_order_settings();
        $order = [];

        if (!empty($saved['Order']) && is_array($saved['Order'])) {
            foreach ($saved['Order'] as $slug_value) {
                $slug = sanitize_title((string) $slug_value);

                if ($slug !== '' && !in_array($slug, $order, true)) {
                    $order[] = $slug;
                }
            }
        } elseif (!empty($saved['Items']) && is_array($saved['Items'])) {
            // Backward compatibility with the incorrect v0.3.x/v0.4.0
            // web schema. Convert it back to the authoritative schema 1.0.
            $items = $saved['Items'];

            usort($items, static function($a, $b) {
                return ((int) ($a['Order'] ?? 0)) <=> ((int) ($b['Order'] ?? 0));
            });

            foreach ($items as $item) {
                if (!is_array($item)) {
                    continue;
                }

                if (array_key_exists('Included', $item) && !$this->bool_value($item['Included'], true)) {
                    continue;
                }

                $slug = sanitize_title((string) ($item['Slug'] ?? ''));

                if ($slug !== '' && !in_array($slug, $order, true)) {
                    $order[] = $slug;
                }
            }
        }

        if (!$order) {
            $order = array_values((array) ($default['Order'] ?? []));
        }

        return [
            'Version' => '1.0',
            'Order'   => $order,
        ];
    }

    private function strip_utf8_bom($text) {
        $text = (string) $text;

        if (substr($text, 0, 3) === "\xEF\xBB\xBF") {
            return substr($text, 3);
        }

        return $text;
    }

    private function extract_css_custom_property($text, $property_name) {
        $text = (string) $text;
        $property_name = preg_quote((string) $property_name, '/');

        if (preg_match('/' . $property_name . '\s*:\s*([^;]+);?/i', $text, $m)) {
            return trim((string) $m[1]);
        }

        return '';
    }

    private function extract_int_from_css_value($value, $default = 0) {
        if (preg_match('/-?\d+(?:\.\d+)?/', (string) $value, $m)) {
            return (int) round((float) $m[0]);
        }

        return (int) $default;
    }

    private function extract_header_design_from_live_shell() {
        $defaults = $this->default_header_design();
        $shell = $this->get_shell_source();

        if (!$shell || empty($shell['header'])) {
            return $defaults;
        }

        $header = (string) $shell['header'];
        $saved = $defaults;

        if (preg_match('/<header\s+class="([^"]*\bh18-site-header\b[^"]*)"[^>]*>/i', $header, $m)) {
            $classes = preg_split('/\s+/', trim((string) $m[1]));

            foreach ($classes as $class) {
                if (strpos($class, 'h18-align-') === 0) {
                    $value = ucfirst(substr($class, strlen('h18-align-')));
                    if (in_array($value, ['Left', 'Center', 'Right'], true)) {
                        $saved['MenuAlignment'] = $value;
                    }
                }

                if (strpos($class, 'h18-identity-align-') === 0) {
                    $value = ucfirst(substr($class, strlen('h18-identity-align-')));
                    if (in_array($value, ['Left', 'Center', 'Right'], true)) {
                        $saved['IdentityAlignment'] = $value;
                    }
                }

                if (strpos($class, 'h18-pos-') === 0) {
                    $value = ucfirst(substr($class, strlen('h18-pos-')));
                    if (in_array($value, ['Normal', 'Floating', 'Overlay'], true)) {
                        $saved['PositionMode'] = $value;
                    }
                }

                if ($class === 'h18-scroll-sticky') {
                    $saved['StickyOnScroll'] = true;
                }

                if ($class === 'h18-scroll-normal') {
                    $saved['StickyOnScroll'] = false;
                }

                if (strpos($class, 'h18-bg-') === 0) {
                    $value = ucfirst(substr($class, strlen('h18-bg-')));
                    if (in_array($value, ['None', 'Bar', 'Box', 'Glass'], true)) {
                        $saved['BackgroundMode'] = $value;
                    }
                }

                if (strpos($class, 'h18-width-') === 0) {
                    $value = ucfirst(substr($class, strlen('h18-width-')));
                    if (in_array($value, ['Full', 'Contained', 'Narrow'], true)) {
                        $saved['WidthMode'] = $value;
                    }
                }

                if ($class === 'h18-mobile-transparent') {
                    $saved['MobileStyle'] = 'Transparent';
                }

                if ($class === 'h18-mobile-dark') {
                    $saved['MobileStyle'] = 'Dark';
                }

                if ($class === 'h18-brandtext-visible') {
                    $saved['ShowBrand'] = true;
                }

                if ($class === 'h18-brandtext-hidden') {
                    $saved['ShowBrand'] = false;
                }

                if ($class === 'h18-logo-visible') {
                    $saved['ShowLogo'] = true;
                }

                if ($class === 'h18-logo-hidden') {
                    $saved['ShowLogo'] = false;
                }
            }
        }

        if (preg_match('/<header[^>]*\sstyle="([^"]*)"/i', $header, $m)) {
            $style = html_entity_decode((string) $m[1], ENT_QUOTES);

            $menu_family = $this->extract_css_custom_property($style, '--h18-menu-font-family');
            if ($menu_family !== '') {
                if (stripos($menu_family, 'Segoe UI') !== false) {
                    $saved['MenuFontFamily'] = 'Segoe UI';
                } elseif (stripos($menu_family, 'Arial') !== false) {
                    $saved['MenuFontFamily'] = 'Arial';
                } elseif (stripos($menu_family, 'Verdana') !== false) {
                    $saved['MenuFontFamily'] = 'Verdana';
                } elseif (stripos($menu_family, 'Tahoma') !== false) {
                    $saved['MenuFontFamily'] = 'Tahoma';
                } elseif (stripos($menu_family, 'Trebuchet') !== false) {
                    $saved['MenuFontFamily'] = 'Trebuchet MS';
                } elseif (stripos($menu_family, 'Georgia') !== false) {
                    $saved['MenuFontFamily'] = 'Georgia';
                } elseif (stripos($menu_family, 'Times New Roman') !== false) {
                    $saved['MenuFontFamily'] = 'Times New Roman';
                } elseif (stripos($menu_family, 'Courier New') !== false) {
                    $saved['MenuFontFamily'] = 'Courier New';
                } else {
                    $saved['MenuFontFamily'] = 'System';
                }
            }

            $weight = $this->extract_css_custom_property($style, '--h18-menu-font-weight');
            if ($weight !== '') {
                switch ((string) $weight) {
                    case '500':
                        $saved['MenuFontWeight'] = 'Medium';
                        break;
                    case '600':
                        $saved['MenuFontWeight'] = 'Semibold';
                        break;
                    case '700':
                        $saved['MenuFontWeight'] = 'Bold';
                        break;
                    default:
                        $saved['MenuFontWeight'] = 'Normal';
                        break;
                }
            }

            $font_style = strtolower($this->extract_css_custom_property($style, '--h18-menu-font-style'));
            if ($font_style !== '') {
                $saved['MenuFontItalic'] = ($font_style === 'italic');
            }

            $transform = strtolower($this->extract_css_custom_property($style, '--h18-menu-text-transform'));
            if ($transform !== '') {
                $saved['MenuUppercase'] = ($transform === 'uppercase');
            }
        }

        if (preg_match('/<span\s+class="h18-site-brand-text"[^>]*>(.*?)<\/span>/s', $header, $m)) {
            $brand = trim(wp_strip_all_tags((string) $m[1]));
            if ($brand !== '') {
                $saved['BrandText'] = $brand;
            }
        }

        if (preg_match('/<img\s+class="h18-site-logo"[^>]*\ssrc="([^"]+)"/i', $header, $m)) {
            $saved['LogoUrl'] = esc_url_raw(html_entity_decode((string) $m[1], ENT_QUOTES));
            $saved['ShowLogo'] = ($saved['LogoUrl'] !== '');

            if ($saved['LogoUrl'] !== '') {
                $attachment_id = attachment_url_to_postid($saved['LogoUrl']);
                if ($attachment_id) {
                    $saved['LogoMediaId'] = (int) $attachment_id;
                }
            }
        }

        if (preg_match('/<style\s+id="hangar18-layout-runtime">(.*?)<\/style>/s', $header, $m)) {
            $runtime = (string) $m[1];

            $footer_width = $this->extract_css_custom_property($runtime, '--h18-footer-content-width');
            if ($footer_width !== '') {
                $saved['FooterWidthPercent'] = $this->clamp_int(
                    $this->extract_int_from_css_value($footer_width, $defaults['FooterWidthPercent']),
                    50,
                    100,
                    $defaults['FooterWidthPercent']
                );
            }

            $section_spacing = $this->extract_css_custom_property($runtime, '--h18-section-spacing');
            if ($section_spacing !== '') {
                $saved['SectionSpacingPx'] = $this->clamp_int(
                    $this->extract_int_from_css_value($section_spacing, $defaults['SectionSpacingPx']),
                    0,
                    120,
                    $defaults['SectionSpacingPx']
                );
            }

            $mobile_section_spacing = $this->extract_css_custom_property($runtime, '--h18-mobile-section-spacing');
            if ($mobile_section_spacing !== '') {
                $saved['MobileSectionSpacingPx'] = $this->clamp_int(
                    $this->extract_int_from_css_value($mobile_section_spacing, $defaults['MobileSectionSpacingPx']),
                    0,
                    80,
                    $defaults['MobileSectionSpacingPx']
                );
            }

            $content_top_spacing = $this->extract_css_custom_property($runtime, '--h18-content-top-spacing');
            if ($content_top_spacing !== '') {
                $saved['ContentTopSpacingPx'] = $this->clamp_int(
                    $this->extract_int_from_css_value($content_top_spacing, $defaults['ContentTopSpacingPx']),
                    0,
                    120,
                    $defaults['ContentTopSpacingPx']
                );
            }

            $content_bottom_spacing = $this->extract_css_custom_property($runtime, '--h18-content-bottom-spacing');
            if ($content_bottom_spacing !== '') {
                $saved['ContentBottomSpacingPx'] = $this->clamp_int(
                    $this->extract_int_from_css_value($content_bottom_spacing, $defaults['ContentBottomSpacingPx']),
                    0,
                    120,
                    $defaults['ContentBottomSpacingPx']
                );
            }

            $mobile_content_top_spacing = $this->extract_css_custom_property($runtime, '--h18-mobile-content-top-spacing');
            if ($mobile_content_top_spacing !== '') {
                $saved['MobileContentTopSpacingPx'] = $this->clamp_int(
                    $this->extract_int_from_css_value($mobile_content_top_spacing, $defaults['MobileContentTopSpacingPx']),
                    0,
                    80,
                    $defaults['MobileContentTopSpacingPx']
                );
            }

            $mobile_content_bottom_spacing = $this->extract_css_custom_property($runtime, '--h18-mobile-content-bottom-spacing');
            if ($mobile_content_bottom_spacing !== '') {
                $saved['MobileContentBottomSpacingPx'] = $this->clamp_int(
                    $this->extract_int_from_css_value($mobile_content_bottom_spacing, $defaults['MobileContentBottomSpacingPx']),
                    0,
                    80,
                    $defaults['MobileContentBottomSpacingPx']
                );
            }

            $max_width = $this->extract_css_custom_property($runtime, '--h18-site-max-width');
            if ($max_width !== '') {
                if (strtolower(trim($max_width)) === 'none') {
                    $saved['ContentMaxWidth'] = 'None';
                } else {
                    $candidate = (string) $this->extract_int_from_css_value($max_width, 0);
                    if (in_array($candidate, ['1400', '1600', '1800', '2000'], true)) {
                        $saved['ContentMaxWidth'] = $candidate;
                    }
                }
            }
        }

        // Known current v2.0.39 baseline that is not reversibly encoded in
        // generated CSS. These are the established project settings.
        $saved['Version']                           = '2.5';
        $saved['VisualBaseScalePercent']            = 90;
        $saved['ResponsiveScaleEnabled']            = true;
        $saved['ResponsiveLargeWidthPx']            = 2560;
        $saved['ResponsiveLaptopWidthPx']           = 1920;
        $saved['ResponsiveLaptopScalePercent']      = 90;
        $saved['ResponsiveMinimumScalePercent']     = 90;
        $saved['DesktopContentWidthPercent']        = 80;
        $saved['LaptopContentWidthPercent']         = 90;
        $saved['MaximumDesktopContentWidthPercent'] = 90;

        return $this->normalize_header_design($saved);
    }

    private function bootstrap_menu_order_from_current_site() {
        $menu_id = $this->get_active_menu_id();

        if ($menu_id) {
            $config = $this->menu_order_config_from_nav_menu($menu_id);

            if (!empty($config['Items'])) {
                return $this->normalize_menu_order_settings($config);
            }
        }

        return $this->default_menu_order_settings();
    }

    private function bootstrap_vehicle_register_from_current_site() {
        // The PowerShell model is global. When the remote JSON is absent,
        // start from the known current project defaults rather than the
        // obsolete per-vehicle v0.3.0 values.
        return $this->default_vehicle_register_settings();
    }

    private function create_configuration_store_from_live_site() {
        $header = $this->extract_header_design_from_live_shell();
        $menu = $this->bootstrap_menu_order_from_current_site();
        $vehicle = $this->bootstrap_vehicle_register_from_current_site();
        $vehicle_fields = $this->default_vehicle_field_settings();

        update_option(self::HEADER_DESIGN_OPTION, $header, false);
        update_option(self::MENU_ORDER_OPTION, $menu, false);
        update_option(self::VEHICLE_REGISTER_OPTION, $vehicle, false);
        update_option(self::VEHICLE_FIELDS_OPTION, $vehicle_fields, false);

        $header_file = $header;
        $header_file['Saved'] = gmdate('c');

        $menu_file = $menu;
        $menu_file['Saved'] = gmdate('c');

        $vehicle_file = $vehicle;
        $vehicle_file['Saved'] = gmdate('c');

        $vehicle_fields_file = $vehicle_fields;
        $vehicle_fields_file['Saved'] = gmdate('c');

        // publish_configuration_file() auto-creates the private page when absent.
        $this->publish_configuration_file(
            'Hangar18-HeaderDesign.json',
            $header_file
        );
        $this->publish_configuration_file(
            'Hangar18-MenuOrder.json',
            $menu_file
        );
        $this->publish_configuration_file(
            'Hangar18-VehicleRegister.json',
            $vehicle_file
        );
        $this->publish_configuration_file(
            'Hangar18-VehicleFields.json',
            $vehicle_fields_file
        );

        $page = $this->get_configuration_store_page();

        $meta = [
            'plugin_version'           => self::VERSION,
            'source'                   => 'Bootstrap fra eksisterende live Hangar18-site',
            'source_page_id'           => $page ? (int) $page->ID : 0,
            'source_page_modified_gmt' => $page ? (string) $page->post_modified_gmt : '',
            'manifest_saved_utc'       => gmdate('c'),
            'manifest_program'         => 'Hangar18 Manager',
            'manifest_program_version' => self::VERSION,
            'imported_at_utc'          => gmdate('c'),
            'imported_files'           => [
                'Hangar18-HeaderDesign.json',
                'Hangar18-MenuOrder.json',
                'Hangar18-VehicleRegister.json',
                'Hangar18-VehicleFields.json',
            ],
            'success'                  => true,
            'bootstrapped'             => true,
        ];

        update_option(self::CONFIG_IMPORT_META_OPTION, $meta, false);
        update_option(self::CONFIG_BOOTSTRAP_OPTION, [
            'created_at_utc' => gmdate('c'),
            'page_id'        => $page ? (int) $page->ID : 0,
        ], false);

        $this->log(
            'INFO',
            'CONFIG_STORE_BOOTSTRAP_SUCCESS',
            'Configuration Store manglede og blev oprettet automatisk fra live Hangar18-site.'
        );

        return $meta;
    }

    private function authoritative_uploaded_header_design() {
        return [
            'Version' => '2.3',
            'VisualBaseScalePercent' => 90,
            'MenuAlignment' => 'Right',
            'PositionMode' => 'Normal',
            'StickyOnScroll' => false,
            'BackgroundMode' => 'None',
            'WidthMode' => 'Contained',
            'ShowBrand' => true,
            'BrandText' => 'Aalborg Kaserners Veteran Panser- og Køretøjsforening',
            'IdentityAlignment' => 'Center',
            'BrandFontSize' => 22,
            'BrandSizePercent' => 100,
            'ShowLogo' => false,
            'LogoMediaId' => 0,
            'LogoUrl' => '',
            'LogoWidthPx' => 52,
            'LogoSizePercent' => 100,
            'MobileStyle' => 'Dark',
            'MenuFontSize' => 15,
            'MenuSizePercent' => 100,
            'MenuFontFamily' => 'Segoe UI',
            'MenuFontWeight' => 'Semibold',
            'MenuFontItalic' => false,
            'MenuUppercase' => false,
            'ResponsiveScaleEnabled' => true,
            'ResponsiveLargeWidthPx' => 2560,
            'ResponsiveLaptopWidthPx' => 1920,
            'ResponsiveLaptopScalePercent' => 90,
            'ResponsiveMinimumScalePercent' => 90,
            'DesktopContentWidthPercent' => 80,
            'LaptopContentWidthPercent' => 90,
            'MaximumDesktopContentWidthPercent' => 90,
            'ContentMaxWidth' => 'None',
            'FooterWidthPercent' => 100,
            'SectionSpacingPx' => 32,
            'MobileSectionSpacingPx' => 24,
            'ContentTopSpacingPx' => 32,
            'ContentBottomSpacingPx' => 32,
            'MobileContentTopSpacingPx' => 24,
            'MobileContentBottomSpacingPx' => 24
        ];
    }

    private function authoritative_uploaded_menu_order() {
        return [
            'Version' => '1.0',
            'Saved' => '2026-08-12T06:53:38.5469021+02:00',
            'Order' => [
                'hjem',
                'koeretoejer-og-materiel',
                'events',
                'billedgalleri',
                'bliv-medlem',
                'kontakt',
                'om-foreningen'
            ]
        ];
    }

    private function authoritative_uploaded_vehicle_register() {
        return [
            'Version' => '1.2',
            'Saved' => '2026-08-13T08:19:43.3711647+02:00',
            'CardAlignment' => 'Center',
            'DetailAlignment' => 'Auto'
        ];
    }

    public function maybe_apply_authoritative_config_baseline() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        if (get_option(self::AUTHORITATIVE_BASELINE_OPTION, false)) {
            return;
        }

        try {
            $header = $this->authoritative_uploaded_header_design();
            $menu = $this->authoritative_uploaded_menu_order();
            $vehicle = $this->authoritative_uploaded_vehicle_register();

            update_option(
                self::HEADER_DESIGN_OPTION,
                $this->normalize_header_design($header),
                false
            );

            update_option(
                self::MENU_ORDER_OPTION,
                $this->normalize_menu_order_settings($menu),
                false
            );

            update_option(
                self::VEHICLE_REGISTER_OPTION,
                $this->normalize_vehicle_register_settings($vehicle),
                false
            );

            // Publish the exact uploaded baseline files to the shared
            // Configuration Store. This changes configuration only; no
            // frontend page/header/menu is rewritten here.
            $this->publish_configuration_file(
                'Hangar18-HeaderDesign.json',
                $header
            );

            $this->publish_configuration_file(
                'Hangar18-MenuOrder.json',
                $menu
            );

            $this->publish_configuration_file(
                'Hangar18-VehicleRegister.json',
                $vehicle
            );

            update_option(
                self::AUTHORITATIVE_BASELINE_OPTION,
                [
                    'applied_at_utc' => gmdate('c'),
                    'plugin_version' => self::VERSION,
                    'source' => 'User-uploaded authoritative JSON baseline 2026-08-13',
                ],
                false
            );

            update_option(
                self::CONFIG_IMPORT_META_OPTION,
                [
                    'plugin_version' => self::VERSION,
                    'source' => 'User-uploaded authoritative JSON baseline 2026-08-13',
                    'manifest_program' => 'Hangar18 Manager',
                    'manifest_program_version' => self::VERSION,
                    'manifest_saved_utc' => gmdate('c'),
                    'imported_at_utc' => gmdate('c'),
                    'imported_files' => [
                        'Hangar18-HeaderDesign.json',
                        'Hangar18-MenuOrder.json',
                        'Hangar18-VehicleRegister.json',
                    ],
                    'success' => true,
                    'authoritative_baseline' => true,
                ],
                false
            );

            $this->log(
                'INFO',
                'AUTHORITATIVE_BASELINE_APPLIED',
                'Uploadet baseline anvendt: HeaderDesign 2.3; MenuOrder 1.0; VehicleRegister 1.2. Frontend blev ikke ændret.'
            );

        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'AUTHORITATIVE_BASELINE_FAILED',
                $e->getMessage()
            );
        }
    }

    private function get_configuration_store_page() {
        $pages = get_posts([
            'post_type'        => 'page',
            'post_status'      => ['private', 'draft', 'publish'],
            'name'             => self::CONFIG_STORE_SLUG,
            'posts_per_page'   => 10,
            'orderby'          => 'modified',
            'order'            => 'DESC',
            'suppress_filters' => false,
        ]);

        return $pages ? $pages[0] : null;
    }

    private function get_remote_configuration_manifest() {
        $page = $this->get_configuration_store_page();

        if (!$page) {
            throw new RuntimeException(
                "Den private WordPress-konfigurationsside '" .
                self::CONFIG_STORE_SLUG .
                "' blev ikke fundet."
            );
        }

        $payload = trim((string) $page->post_content);

        if ($payload === '') {
            throw new RuntimeException(
                'Den centrale WordPress-konfiguration indeholder ingen data.'
            );
        }

        $manifest_json = base64_decode($payload, true);

        if ($manifest_json === false) {
            throw new RuntimeException(
                'Den centrale WordPress-konfiguration har ugyldigt Base64-format.'
            );
        }

        $manifest = json_decode(
            $this->strip_utf8_bom($manifest_json),
            true
        );

        if (!is_array($manifest)) {
            throw new RuntimeException(
                'Den centrale WordPress-konfiguration kunne ikke afkodes som JSON.'
            );
        }

        if ((string) ($manifest['SchemaVersion'] ?? '') !== '1.0') {
            throw new RuntimeException(
                'Ukendt centralt konfigurationsformat: ' .
                (string) ($manifest['SchemaVersion'] ?? '')
            );
        }

        if (!isset($manifest['Files']) || !is_array($manifest['Files'])) {
            throw new RuntimeException(
                'Den centrale konfiguration indeholder ingen Files-liste.'
            );
        }

        return [
            'page'     => $page,
            'manifest' => $manifest,
        ];
    }

    private function decode_remote_configuration_file(array $manifest, $file_name) {
        foreach ($manifest['Files'] as $entry) {
            if (!is_array($entry) || (string) ($entry['Name'] ?? '') !== (string) $file_name) {
                continue;
            }

            $bytes = base64_decode((string) ($entry['ContentBase64'] ?? ''), true);

            if ($bytes === false) {
                throw new RuntimeException(
                    "Konfigurationsfilen '{$file_name}' har ugyldigt Base64-indhold."
                );
            }

            $expected_hash = strtolower(trim((string) ($entry['Sha256'] ?? '')));
            $calculated_hash = strtolower(hash('sha256', $bytes));

            if ($expected_hash !== '' && !hash_equals($expected_hash, $calculated_hash)) {
                throw new RuntimeException(
                    "SHA-256-validering fejlede for '{$file_name}'."
                );
            }

            $json = json_decode(
                $this->strip_utf8_bom($bytes),
                true
            );

            if (!is_array($json)) {
                throw new RuntimeException(
                    "Konfigurationsfilen '{$file_name}' indeholder ugyldig JSON."
                );
            }

            return [
                'data'   => $json,
                'hash'   => $calculated_hash,
                'length' => strlen($bytes),
                'entry'  => $entry,
            ];
        }

        return null;
    }

    private function import_power_shell_configuration($force = false) {
        $store_page = $this->get_configuration_store_page();

        if (!$store_page) {
            return $this->create_configuration_store_from_live_site();
        }

        $remote = $this->get_remote_configuration_manifest();
        $manifest = $remote['manifest'];

        $header = $this->decode_remote_configuration_file(
            $manifest,
            'Hangar18-HeaderDesign.json'
        );
        $menu = $this->decode_remote_configuration_file(
            $manifest,
            'Hangar18-MenuOrder.json'
        );
        $vehicle = $this->decode_remote_configuration_file(
            $manifest,
            'Hangar18-VehicleRegister.json'
        );
        $vehicle_fields = $this->decode_remote_configuration_file(
            $manifest,
            'Hangar18-VehicleFields.json'
        );

        $imported = [];
        $hashes = [];

        if ($header) {
            $normalized = $this->normalize_header_design($header['data']);
            update_option(self::HEADER_DESIGN_OPTION, $normalized, false);
            $imported[] = 'Hangar18-HeaderDesign.json';
            $hashes['Hangar18-HeaderDesign.json'] = $header['hash'];
        }

        if ($menu) {
            $normalized = $this->normalize_menu_order_settings($menu['data']);
            update_option(self::MENU_ORDER_OPTION, $normalized, false);
            $imported[] = 'Hangar18-MenuOrder.json';
            $hashes['Hangar18-MenuOrder.json'] = $menu['hash'];
        }

        if ($vehicle) {
            $normalized = $this->normalize_vehicle_register_settings($vehicle['data']);
            update_option(self::VEHICLE_REGISTER_OPTION, $normalized, false);
            $imported[] = 'Hangar18-VehicleRegister.json';
            $hashes['Hangar18-VehicleRegister.json'] = $vehicle['hash'];
        }

        if ($vehicle_fields) {
            $normalized = $this->normalize_vehicle_field_settings($vehicle_fields['data']);
            update_option(self::VEHICLE_FIELDS_OPTION, $normalized, false);
            $imported[] = 'Hangar18-VehicleFields.json';
            $hashes['Hangar18-VehicleFields.json'] = $vehicle_fields['hash'];
        }

        $meta = [
            'plugin_version'          => self::VERSION,
            'source'                  => 'WordPress Configuration Store',
            'source_page_id'          => (int) $remote['page']->ID,
            'source_page_modified_gmt'=> (string) $remote['page']->post_modified_gmt,
            'manifest_saved_utc'      => (string) ($manifest['SavedUtc'] ?? ''),
            'manifest_program'        => (string) ($manifest['Program'] ?? ''),
            'manifest_program_version'=> (string) ($manifest['ProgramVersion'] ?? ''),
            'imported_at_utc'         => gmdate('c'),
            'imported_files'          => $imported,
            'hashes'                  => $hashes,
            'success'                 => count($imported) > 0,
        ];

        update_option(self::CONFIG_IMPORT_META_OPTION, $meta, false);

        $this->log(
            'INFO',
            'CONFIG_1TO1_IMPORT_SUCCESS',
            'Central PowerShell-konfiguration importeret 1:1. Filer: ' .
            implode(', ', $imported) .
            '. ManifestProgram=' .
            (string) ($manifest['ProgramVersion'] ?? '')
        );

        return $meta;
    }

    public function maybe_import_power_shell_configuration() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        $meta = get_option(self::CONFIG_IMPORT_META_OPTION, []);

        if (
            is_array($meta) &&
            !empty($meta['success']) &&
            (string) ($meta['plugin_version'] ?? '') === self::VERSION
        ) {
            return;
        }

        try {
            $this->import_power_shell_configuration(false);
        } catch (Throwable $e) {
            // A missing store is no longer an error path: import_power_shell_configuration()
            // creates it automatically. Therefore reaching this catch means an existing
            // store or another dependency is malformed/unavailable.
            $failure_meta = [
                'plugin_version' => self::VERSION,
                'source'         => 'Central Configuration Store kunne ikke læses',
                'imported_at_utc'=> gmdate('c'),
                'success'        => false,
                'error'          => $e->getMessage(),
            ];

            update_option(
                self::CONFIG_IMPORT_META_OPTION,
                $failure_meta,
                false
            );

            $this->log(
                'WARN',
                'CONFIG_1TO1_IMPORT_FAILED',
                $e->getMessage()
            );
        }
    }

    private function get_header_design_settings() {
        $stored = get_option(self::HEADER_DESIGN_OPTION, []);

        if (!is_array($stored) || !$stored) {
            return $this->default_header_design();
        }

        return $this->normalize_header_design($stored);
    }

    private function get_vehicle_register_settings() {
        $stored = get_option(self::VEHICLE_REGISTER_OPTION, []);

        if (!is_array($stored) || !$stored) {
            return $this->default_vehicle_register_settings();
        }

        return $this->normalize_vehicle_register_settings($stored);
    }

    private function get_content_layout_settings() {
        $stored = get_option(self::CONTENT_LAYOUT_OPTION, []);

        if (!is_array($stored) || !$stored) {
            return $this->default_content_layout_settings();
        }

        return $this->normalize_content_layout_settings($stored);
    }

    private function get_menu_order_settings() {
        $stored = get_option(self::MENU_ORDER_OPTION, []);

        if (!is_array($stored) || !$stored) {
            return $this->default_menu_order_settings();
        }

        return $this->normalize_menu_order_settings($stored);
    }

    private function configuration_file_bytes(array $data) {
        $json = wp_json_encode(
            $data,
            JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
        );

        // Windows PowerShell 5.1 Set-Content -Encoding UTF8 writes BOM.
        // Preserve that byte-level behavior because SHA-256/Length in the
        // remote manifest are calculated over the file bytes.
        return "\xEF\xBB\xBF" . $json;
    }

    private function current_configuration_files_for_manifest() {
        $header = $this->get_header_design_settings();
        $header['Saved'] = gmdate('c');

        $menu = $this->get_menu_order_settings();
        $menu['Saved'] = gmdate('c');

        $vehicle = $this->get_vehicle_register_settings();
        $vehicle['Saved'] = gmdate('c');

        $vehicle_fields = $this->get_vehicle_field_settings();
        $vehicle_fields['Saved'] = gmdate('c');

        $content_layout = $this->get_content_layout_settings();
        $content_layout['Saved'] = gmdate('c');

        $static_content = $this->get_static_content_settings();
        $static_content['Saved'] = gmdate('c');

        $pages = [
            'Version' => '1.11',
            'Saved'   => gmdate('c'),
            'Pages'   => $this->get_page_editor_store(),
        ];

        return [
            'Hangar18-HeaderDesign.json'    => $header,
            'Hangar18-MenuOrder.json'       => $menu,
            'Hangar18-VehicleRegister.json' => $vehicle,
            'Hangar18-VehicleFields.json'   => $vehicle_fields,
            'Hangar18-ContentLayout.json'   => $content_layout,
            'Hangar18-StaticContent.json'   => $static_content,
            'Hangar18-Pages.json'           => $pages,
        ];
    }

    private function publish_configuration_file($file_name, array $data) {
        $existing_page = $this->get_configuration_store_page();
        $manifest = null;

        if ($existing_page) {
            try {
                $remote = $this->get_remote_configuration_manifest();
                $manifest = $remote['manifest'];
            } catch (Throwable $ignored) {
                $manifest = null;
            }
        }

        if (!is_array($manifest)) {
            $manifest = [
                'SchemaVersion'  => '1.0',
                'Program'        => 'Hangar18 Manager',
                'ProgramVersion' => self::VERSION,
                'SavedUtc'       => gmdate('c'),
                'Files'          => [],
            ];
        }

        $files_by_name = [];

        foreach (($manifest['Files'] ?? []) as $entry) {
            if (!is_array($entry)) {
                continue;
            }

            $name = (string) ($entry['Name'] ?? '');
            if ($name !== '') {
                $files_by_name[$name] = $entry;
            }
        }

        $all_current = $this->current_configuration_files_for_manifest();
        $all_current[$file_name] = $data;

        // Hold den interne WordPress-konfiguration komplet.
        foreach ($all_current as $name => $file_data) {
            if ($name !== $file_name && isset($files_by_name[$name])) {
                continue;
            }

            $bytes = $this->configuration_file_bytes($file_data);

            $files_by_name[$name] = [
                'Name'          => $name,
                'Sha256'        => hash('sha256', $bytes),
                'Length'        => strlen($bytes),
                'LastWriteUtc'  => gmdate('c'),
                'ContentBase64' => base64_encode($bytes),
            ];
        }

        $bytes = $this->configuration_file_bytes($data);

        $files_by_name[$file_name] = [
            'Name'          => $file_name,
            'Sha256'        => hash('sha256', $bytes),
            'Length'        => strlen($bytes),
            'LastWriteUtc'  => gmdate('c'),
            'ContentBase64' => base64_encode($bytes),
        ];

        $preferred_order = [
            'Hangar18-HeaderDesign.json',
            'Hangar18-MenuOrder.json',
            'Hangar18-VehicleRegister.json',
            'Hangar18-VehicleFields.json',
            'Hangar18-ContentLayout.json',
            'Hangar18-StaticContent.json',
            'Hangar18-Pages.json',
        ];

        $files = [];

        foreach ($preferred_order as $name) {
            if (isset($files_by_name[$name])) {
                $files[] = $files_by_name[$name];
                unset($files_by_name[$name]);
            }
        }

        foreach ($files_by_name as $entry) {
            $files[] = $entry;
        }

        $manifest['SchemaVersion']  = '1.0';
        $manifest['Program']        = 'Hangar18 Manager';
        $manifest['ProgramVersion'] = self::VERSION;
        $manifest['SavedUtc']       = gmdate('c');
        $manifest['Files']          = $files;

        $payload = base64_encode(
            wp_json_encode(
                $manifest,
                JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
            )
        );

        if ($existing_page) {
            $result = wp_update_post(
                [
                    'ID'             => $existing_page->ID,
                    'page_template'  => 'default',
                    'post_title'     => self::CONFIG_STORE_TITLE,
                    'post_name'      => self::CONFIG_STORE_SLUG,
                    'post_status'    => 'private',
                    'post_content'   => $payload,
                    'comment_status' => 'closed',
                    'ping_status'    => 'closed',
                ],
                true
            );
        } else {
            $result = wp_insert_post(
                [
                    'post_type'      => 'page',
                    'page_template'  => 'default',
                    'post_title'     => self::CONFIG_STORE_TITLE,
                    'post_name'      => self::CONFIG_STORE_SLUG,
                    'post_status'    => 'private',
                    'post_content'   => $payload,
                    'comment_status' => 'closed',
                    'ping_status'    => 'closed',
                ],
                true
            );
        }

        if (is_wp_error($result)) {
            throw new RuntimeException(
                'Central konfiguration kunne ikke gemmes: ' .
                $result->get_error_message()
            );
        }

        $this->log(
            'INFO',
            'CONFIG_REMOTE_FILE_PUBLISHED',
            "'{$file_name}' gemt i central WordPress Configuration Store. Page ID {$result}."
        );

        return (int) $result;
    }

    public function handle_import_power_shell_config() {
        $this->require_capability();
        check_admin_referer('h18_import_power_shell_config');

        try {
            $meta = $this->import_power_shell_configuration(true);

            $this->set_notice(
                'success',
                'Alle tre Hangar18-konfigurationer er indlæst 1:1. ' .
                'Kilde: ' .
                (string) ($meta['source'] ?? 'WordPress Configuration Store') .
                '; side ID ' .
                (int) ($meta['source_page_id'] ?? 0) . '.'
            );
        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'CONFIG_1TO1_MANUAL_IMPORT_FAILED',
                $e->getMessage()
            );

            $this->set_notice(
                'error',
                '1:1-import fejlede: ' . $e->getMessage()
            );
        }

        $this->redirect('hangar18-header-footer');
    }

    private function post_by_slug($slug) {
        $post = get_page_by_path($slug, OBJECT, 'page');
        return ($post && $post->post_type === 'page') ? $post : null;
    }

    private function get_child_pages($parent_slug, $published_only = false) {
        $parent = $this->post_by_slug($parent_slug);
        if (!$parent) {
            return [];
        }

        $statuses = $published_only
            ? ['publish']
            : ['publish', 'draft', 'private', 'pending', 'future'];

        $pages = get_posts([
            'post_type'        => 'page',
            'post_status'      => $statuses,
            'post_parent'      => (int) $parent->ID,
            'posts_per_page'   => -1,
            'orderby'          => 'title',
            'order'            => 'ASC',
            'suppress_filters' => false,
        ]);

        return array_values($pages);
    }

    private function get_vehicle_pages($published_only = false) {
        return array_values(array_filter(
            $this->get_child_pages(self::VEHICLE_PARENT_SLUG, $published_only),
            static function($page) {
                return $page->post_name !== 'koeretoejsskabelon';
            }
        ));
    }

    private function get_event_pages($published_only = false) {
        return array_values(array_filter(
            $this->get_child_pages(self::EVENT_PARENT_SLUG, $published_only),
            static function($page) {
                return $page->post_name !== 'eventskabelon';
            }
        ));
    }

    private function get_gallery_pages($published_only = false) {
        return $this->get_child_pages(self::GALLERY_PARENT_SLUG, $published_only);
    }

    private function encode_marker($marker, array $data) {
        $json = wp_json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        return '<!-- ' . $marker . ':' . base64_encode($json) . ' -->';
    }

    private function decode_marker($marker, $content) {
        if (!is_string($content) || trim($content) === '') {
            return null;
        }

        if (!preg_match('/<!--\s*' . preg_quote($marker, '/') . ':([A-Za-z0-9+\/=]+)\s*-->/', $content, $matches)) {
            return null;
        }

        $json = base64_decode($matches[1], true);
        if ($json === false) {
            return null;
        }

        $data = json_decode($json, true);
        return is_array($data) ? $data : null;
    }

    private function value(array $data, $key, $default = '') {
        return array_key_exists($key, $data) ? (string) $data[$key] : $default;
    }

    private function h($value) {
        return esc_html((string) $value);
    }

    private function hm($value) {
        return nl2br(esc_html((string) $value), false);
    }

    private function post_text($key) {
        return isset($_POST[$key]) ? sanitize_text_field(wp_unslash($_POST[$key])) : '';
    }

    private function post_textarea($key) {
        return isset($_POST[$key]) ? sanitize_textarea_field(wp_unslash($_POST[$key])) : '';
    }

    private function post_url($key) {
        return isset($_POST[$key]) ? esc_url_raw(wp_unslash($_POST[$key])) : '';
    }

    private function set_notice($type, $message) {
        set_transient(
            self::NOTICE_PREFIX . get_current_user_id(),
            ['type' => sanitize_key($type), 'message' => (string) $message],
            120
        );
    }

    private function render_notice() {
        $key = self::NOTICE_PREFIX . get_current_user_id();
        $notice = get_transient($key);

        if (!$notice || !is_array($notice)) {
            return;
        }

        delete_transient($key);

        $type = in_array($notice['type'] ?? '', ['success', 'warning', 'error', 'info'], true)
            ? $notice['type']
            : 'info';

        echo '<div class="notice notice-' . esc_attr($type) . ' is-dismissible"><p>' .
            esc_html($notice['message'] ?? '') .
            '</p></div>';
    }

    private function log($level, $checkpoint, $message) {
        $entries = get_option(self::LOG_OPTION, []);
        if (!is_array($entries)) {
            $entries = [];
        }

        $user = wp_get_current_user();

        $entries[] = [
            'time'       => current_time('mysql'),
            'level'      => strtoupper((string) $level),
            'checkpoint' => (string) $checkpoint,
            'message'    => (string) $message,
            'user'       => ($user && $user->exists()) ? $user->user_login : '',
        ];

        if (count($entries) > 750) {
            $entries = array_slice($entries, -750);
        }

        update_option(self::LOG_OPTION, $entries, false);
    }

    private function backup_dir() {
        $uploads = wp_upload_dir();

        if (!empty($uploads['error'])) {
            throw new RuntimeException('WordPress uploads-mappen er ikke tilgængelig: ' . $uploads['error']);
        }

        $dir = trailingslashit($uploads['basedir']) . 'hangar18-manager-backups';

        if (!wp_mkdir_p($dir)) {
            throw new RuntimeException('Kunne ikke oprette Hangar18 backup-mappen.');
        }

        return $dir;
    }

    private function backup_post($post_id, $reason) {
        $post = get_post($post_id);
        if (!$post) {
            return null;
        }

        if (function_exists('wp_save_post_revision')) {
            wp_save_post_revision($post_id);
        }

        $payload = [
            'created_utc'    => gmdate('c'),
            'reason'         => (string) $reason,
            'plugin_version' => self::VERSION,
            'post' => [
                'ID'           => (int) $post->ID,
                'post_title'   => $post->post_title,
                'post_name'    => $post->post_name,
                'post_status'  => $post->post_status,
                'post_parent'  => (int) $post->post_parent,
                'post_excerpt' => $post->post_excerpt,
                'post_content' => $post->post_content,
                'featured_id'  => (int) get_post_thumbnail_id($post->ID),
            ],
        ];

        $file = trailingslashit($this->backup_dir()) .
            sprintf('Hangar18-Web-Backup-%s-Post-%d.json', gmdate('Ymd-His'), $post->ID);

        if (file_put_contents(
            $file,
            wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
        ) === false) {
            throw new RuntimeException('Kunne ikke skrive backup-filen.');
        }

        $this->log('INFO', 'BACKUP_SUCCESS', 'Backup oprettet: ' . basename($file) . '. Årsag: ' . $reason);
        return $file;
    }

    private function create_full_managed_backup($reason) {
        $posts = $this->get_managed_pages();

        $payload = [
            'created_utc'    => gmdate('c'),
            'reason'         => (string) $reason,
            'plugin_version' => self::VERSION,
            'design'         => $this->get_design_settings(),
            'page_editor'    => $this->get_page_editor_store(),
            'page_versions'  => get_option(self::PAGE_VERSION_HISTORY_OPTION, []),
            'poll_votes'     => get_option(self::POLL_VOTES_OPTION, []),
            'posts'          => [],
        ];

        foreach ($posts as $post) {
            $payload['posts'][] = [
                'ID'           => (int) $post->ID,
                'post_title'   => $post->post_title,
                'post_name'    => $post->post_name,
                'post_status'  => $post->post_status,
                'post_parent'  => (int) $post->post_parent,
                'post_excerpt' => $post->post_excerpt,
                'post_content' => $post->post_content,
                'featured_id'  => (int) get_post_thumbnail_id($post->ID),
            ];
        }

        $file = trailingslashit($this->backup_dir()) .
            sprintf('Hangar18-Web-Full-Backup-%s.json', gmdate('Ymd-His'));

        if (file_put_contents(
            $file,
            wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
        ) === false) {
            throw new RuntimeException('Kunne ikke skrive den samlede backup-fil.');
        }

        $this->log('INFO', 'FULL_BACKUP_SUCCESS', 'Samlet backup oprettet: ' . basename($file) . '. Sider: ' . count($posts));
        return $file;
    }

    private function extract_block($content, $start, $end) {
        if (!is_string($content) || $content === '') {
            return '';
        }

        $pattern = '/' . preg_quote($start, '/') . '.*?' . preg_quote($end, '/') . '/s';
        if (preg_match($pattern, $content, $matches)) {
            return trim($matches[0]);
        }

        return '';
    }

    private function replace_block($content, $start, $end, $replacement) {
        $pattern = '/' . preg_quote($start, '/') . '.*?' . preg_quote($end, '/') . '/s';

        if (preg_match($pattern, $content)) {
            return preg_replace($pattern, $replacement, $content, 1);
        }

        return trim($content) . "\n\n" . trim($replacement) . "\n";
    }

    private function strip_block($content, $start, $end) {
        $pattern = '/' . preg_quote($start, '/') . '.*?' . preg_quote($end, '/') . '/s';
        return trim((string) preg_replace($pattern, '', (string) $content));
    }

    private function get_shell_source() {
        $home = $this->post_by_slug(self::HOME_SLUG);
        if ($home) {
            $header = $this->extract_block($home->post_content, self::HEADER_START, self::HEADER_END);
            $css    = $this->extract_block($home->post_content, self::CSS_START, self::CSS_END);
            $footer = $this->extract_block($home->post_content, self::FOOTER_START, self::FOOTER_END);

            if ($header && $css && $footer) {
                return [
                    'source' => $home,
                    'header' => $header,
                    'css'    => $css,
                    'footer' => $footer,
                ];
            }
        }

        foreach ($this->get_managed_pages() as $page) {
            $header = $this->extract_block($page->post_content, self::HEADER_START, self::HEADER_END);
            $css    = $this->extract_block($page->post_content, self::CSS_START, self::CSS_END);
            $footer = $this->extract_block($page->post_content, self::FOOTER_START, self::FOOTER_END);

            if ($header && $css && $footer) {
                return [
                    'source' => $page,
                    'header' => $header,
                    'css'    => $css,
                    'footer' => $footer,
                ];
            }
        }

        return null;
    }

    private function wrap_with_shell($core, $target_id = 0) {
        $shell = $this->get_shell_source();

        if (!$shell) {
            $this->log('WARN', 'SHELL_NOT_FOUND', 'Kunne ikke finde eksisterende Hangar18 header/footer-shell.');
            return $core;
        }

        $design = $this->get_header_design_settings();
        $header = $this->apply_design_to_header_html(
            $shell['header'],
            $design
        );
        $override = $this->build_design_override_block($design);

        return trim($header) . "\n\n" .
            trim($shell['css']) . "\n\n" .
            trim($override) . "\n\n" .
            "<!-- HANGAR18-PAGE-FRAME-START -->\n" .
            "<!-- wp:group {\"className\":\"h18-page-frame\",\"layout\":{\"type\":\"default\"}} -->\n" .
            "<div class=\"wp-block-group h18-page-frame\">\n\n" .
            trim($core) . "\n\n" .
            "</div>\n<!-- /wp:group -->\n" .
            "<!-- HANGAR18-PAGE-FRAME-END -->\n\n" .
            trim($shell['footer']);
    }

    private function get_design_settings() {
        return $this->get_header_design_settings();
    }

    private function css_number($value, $decimals = 3) {
        $formatted = number_format(
            (float) $value,
            (int) $decimals,
            '.',
            ''
        );

        $formatted = rtrim(rtrim($formatted, '0'), '.');
        return $formatted === '' ? '0' : $formatted;
    }

    private function fluid_css_length(
        $base_px,
        $size_percent,
        $large_width_px,
        $laptop_width_px,
        $laptop_scale_percent,
        $minimum_scale_percent,
        $minimum_absolute_px,
        $enabled
    ) {
        $maximum_px = (float) $base_px * ((float) $size_percent / 100.0);

        if ($maximum_px < (float) $minimum_absolute_px) {
            $maximum_px = (float) $minimum_absolute_px;
        }

        if (!$enabled || (int) $large_width_px <= (int) $laptop_width_px) {
            return $this->css_number($maximum_px) . 'px';
        }

        $laptop_scale = (float) $laptop_scale_percent / 100.0;

        $minimum_scale = (float) $minimum_scale_percent / 100.0;

        $minimum_px = $maximum_px * $minimum_scale;
        if ($minimum_px < (float) $minimum_absolute_px) {
            $minimum_px = (float) $minimum_absolute_px;
        }

        $scale_slope = (
            1.0 - $laptop_scale
        ) / (
            (float) $large_width_px - (float) $laptop_width_px
        );

        $scale_intercept = 1.0 - (
            $scale_slope * (float) $large_width_px
        );

        $preferred_vw = $maximum_px * $scale_slope * 100.0;
        $preferred_px = $maximum_px * $scale_intercept;

        return 'clamp(' .
            $this->css_number($minimum_px) . 'px,' .
            'calc(' .
            $this->css_number($preferred_vw, 4) . 'vw + ' .
            $this->css_number($preferred_px) . 'px),' .
            $this->css_number($maximum_px) . 'px)';
    }

    private function header_font_family_css($font_family) {
        switch ((string) $font_family) {
            case 'System':
                return '-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif';
            case 'Arial':
                return 'Arial,Helvetica,sans-serif';
            case 'Verdana':
                return 'Verdana,Geneva,sans-serif';
            case 'Tahoma':
                return 'Tahoma,Verdana,sans-serif';
            case 'Trebuchet MS':
                return '"Trebuchet MS",Arial,sans-serif';
            case 'Georgia':
                return 'Georgia,"Times New Roman",serif';
            case 'Times New Roman':
                return '"Times New Roman",Times,serif';
            case 'Courier New':
                return '"Courier New",Courier,monospace';
            case 'Segoe UI':
            default:
                return '"Segoe UI",Arial,sans-serif';
        }
    }

    private function header_font_weight_css($font_weight) {
        switch ((string) $font_weight) {
            case 'Medium':
                return '500';
            case 'Semibold':
                return '600';
            case 'Bold':
                return '700';
            case 'Normal':
            default:
                return '400';
        }
    }

    private function header_design_runtime_values(array $design) {
        $visual_factor = ((float) $design['VisualBaseScalePercent']) / 100.0;
        $identity_base_factor = 0.70;

        $enabled = !empty($design['ResponsiveScaleEnabled']);
        $large = (int) $design['ResponsiveLargeWidthPx'];
        $laptop = (int) $design['ResponsiveLaptopWidthPx'];
        $laptop_scale = (int) $design['ResponsiveLaptopScalePercent'];
        $minimum_scale = (int) $design['ResponsiveMinimumScalePercent'];

        $root_font = $this->fluid_css_length(
            16 * $visual_factor,
            100,
            $large,
            $laptop,
            $laptop_scale,
            $laptop_scale,
            14.4,
            $enabled
        );

        $logo = $this->fluid_css_length(
            ((float) $design['LogoWidthPx']) * $visual_factor * $identity_base_factor,
            (int) $design['LogoSizePercent'],
            $large,
            $laptop,
            $laptop_scale,
            $minimum_scale,
            24,
            $enabled
        );

        $brand = $this->fluid_css_length(
            ((float) $design['BrandFontSize']) * $visual_factor * $identity_base_factor,
            (int) $design['BrandSizePercent'],
            $large,
            $laptop,
            $laptop_scale,
            $minimum_scale,
            12,
            $enabled
        );

        $menu = $this->fluid_css_length(
            ((float) $design['MenuFontSize']) * $visual_factor,
            (int) $design['MenuSizePercent'],
            $large,
            $laptop,
            $laptop_scale,
            $minimum_scale,
            11,
            $enabled
        );

        $footer_body = $this->fluid_css_length(
            16 * $visual_factor,
            100,
            $large,
            $laptop,
            $laptop_scale,
            $minimum_scale,
            13,
            $enabled
        );

        $footer_title = $this->fluid_css_length(
            22 * $visual_factor,
            100,
            $large,
            $laptop,
            $laptop_scale,
            $minimum_scale,
            17,
            $enabled
        );

        $footer_heading = $this->fluid_css_length(
            16 * $visual_factor,
            100,
            $large,
            $laptop,
            $laptop_scale,
            $minimum_scale,
            13,
            $enabled
        );

        return [
            'root_font'      => $root_font,
            'logo'           => $logo,
            'brand'          => $brand,
            'menu'           => $menu,
            'footer_body'    => $footer_body,
            'footer_title'   => $footer_title,
            'footer_heading' => $footer_heading,
        ];
    }

    private function header_class_text(array $design) {
        $classes = [
            'h18-site-header',
            'h18-align-' . strtolower($design['MenuAlignment']),
            'h18-identity-align-' . strtolower($design['IdentityAlignment']),
            'h18-pos-' . strtolower($design['PositionMode']),
            !empty($design['StickyOnScroll'])
                ? 'h18-scroll-sticky'
                : 'h18-scroll-normal',
            'h18-bg-' . strtolower($design['BackgroundMode']),
            'h18-width-' . strtolower($design['WidthMode']),
            'h18-mobile-' . strtolower($design['MobileStyle']),
            !empty($design['ShowBrand'])
                ? 'h18-brandtext-visible'
                : 'h18-brandtext-hidden',
            !empty($design['ShowLogo'])
                ? 'h18-logo-visible'
                : 'h18-logo-hidden',
            (!empty($design['ShowBrand']) || !empty($design['ShowLogo']))
                ? 'h18-identity-visible'
                : 'h18-identity-hidden',
        ];

        return implode(' ', $classes);
    }

    private function header_inline_style(array $design) {
        $runtime = $this->header_design_runtime_values($design);

        return
            '--h18-menu-font-family:' .
            $this->header_font_family_css($design['MenuFontFamily']) . ';' .
            '--h18-menu-font-size:' . $runtime['menu'] . ';' .
            '--h18-menu-font-weight:' .
            $this->header_font_weight_css($design['MenuFontWeight']) . ';' .
            '--h18-menu-font-style:' .
            (!empty($design['MenuFontItalic']) ? 'italic' : 'normal') . ';' .
            '--h18-menu-text-transform:' .
            (!empty($design['MenuUppercase']) ? 'uppercase' : 'none') . ';' .
            '--h18-logo-width:' . $runtime['logo'] . ';' .
            '--h18-brand-font-size:' . $runtime['brand'] . ';';
    }

    private function runtime_layout_style(array $design) {
        $runtime = $this->header_design_runtime_values($design);

        $max_width = $design['ContentMaxWidth'] === 'None'
            ? 'none'
            : ((int) $design['ContentMaxWidth']) . 'px';

        return '<style id="hangar18-layout-runtime">' . "\n" .
            ':root {' . "\n" .
            '    --h18-site-width:' . (int) $design['DesktopContentWidthPercent'] . 'vw;' . "\n" .
            '    --h18-site-max-width:' . esc_attr($max_width) . ';' . "\n" .
            '    --h18-global-root-font-size:' . esc_attr($runtime['root_font']) . ';' . "\n" .
            '    --h18-footer-content-width:' . (int) $design['FooterWidthPercent'] . '%;' . "\n" .
            '    --h18-section-spacing:' . (int) $design['SectionSpacingPx'] . 'px;' . "\n" .
            '    --h18-mobile-section-spacing:' . (int) $design['MobileSectionSpacingPx'] . 'px;' . "\n" .
            '    --h18-content-top-spacing:' . (int) $design['ContentTopSpacingPx'] . 'px;' . "\n" .
            '    --h18-content-bottom-spacing:' . (int) $design['ContentBottomSpacingPx'] . 'px;' . "\n" .
            '    --h18-mobile-content-top-spacing:' . (int) $design['MobileContentTopSpacingPx'] . 'px;' . "\n" .
            '    --h18-mobile-content-bottom-spacing:' . (int) $design['MobileContentBottomSpacingPx'] . 'px;' . "\n" .
            '    --h18-footer-body-font-size:' . esc_attr($runtime['footer_body']) . ';' . "\n" .
            '    --h18-footer-title-font-size:' . esc_attr($runtime['footer_title']) . ';' . "\n" .
            '    --h18-footer-heading-font-size:' . esc_attr($runtime['footer_heading']) . ';' . "\n" .
            '}' . "\n" .
            '</style>';
    }

    private function apply_design_to_header_html($header, array $design) {
        $header = (string) $header;
        $class_text = esc_attr($this->header_class_text($design));
        $style_text = esc_attr($this->header_inline_style($design));

        $header = preg_replace(
            '/<header\s+class="[^"]*\bh18-site-header\b[^"]*"\s+role="banner"(?:\s+style="[^"]*")?>/i',
            '<header class="' . $class_text . '" role="banner" style="' . $style_text . '">',
            $header,
            1,
            $header_count
        );

        if ($header_count !== 1) {
            throw new RuntimeException(
                'Kunne ikke opdatere h18-site-header class/style 1:1.'
            );
        }

        $brand_text = esc_html((string) $design['BrandText']);
        $logo_html = '';

        if (!empty($design['ShowLogo']) && trim((string) $design['LogoUrl']) !== '') {
            $logo_html =
                '<img class="h18-site-logo" src="' .
                esc_url((string) $design['LogoUrl']) .
                '" alt="" />';
        }

        $brand_inner =
            '<a href="/">' .
            $logo_html .
            '<span class="h18-site-brand-text">' .
            $brand_text .
            '</span></a>';

        $header = preg_replace(
            '/(<div\s+class="h18-site-brand"\s*>).*?(<\/div>)/s',
            '$1' . $brand_inner . '$2',
            $header,
            1,
            $brand_count
        );

        if ($brand_count !== 1) {
            throw new RuntimeException(
                'Kunne ikke opdatere h18-site-brand 1:1.'
            );
        }

        $runtime_style = $this->runtime_layout_style($design);

        if (preg_match('/<style\s+id="hangar18-layout-runtime">.*?<\/style>/s', $header)) {
            $header = preg_replace(
                '/<style\s+id="hangar18-layout-runtime">.*?<\/style>/s',
                $runtime_style,
                $header,
                1
            );
        } else {
            $header = str_replace(
                self::HEADER_END,
                $runtime_style . "\n\n" . self::HEADER_END,
                $header
            );
        }

        return $header;
    }

    private function build_design_override_block(array $settings = null) {
        // v0.3.1 no longer replaces the imported PowerShell layout with
        // independent web defaults. The central schema 2.3 values are
        // applied directly to the existing PowerShell header structure.
        // This block contains only web-menu submenu compatibility and a
        // harmless horizontal overflow guard.
        return <<<'HTML'
<!-- HANGAR18-WEB-OVERRIDE-START -->
<!-- wp:html -->
<style id="hangar18-web-manager-override">
html,
body,
.site,
#page,
.wp-site-blocks,
.entry-content {
    overflow-x:clip !important;
}

/* Hangar18 bruger sin egen header inde i sideindholdet.
   Skjul Astra/WordPress' native sidetitel/header og fjern den reserverede topafstand. */
body.page .entry-header,
body.page header.entry-header,
body.page .page-header,
body.page .ast-page-title,
body.page .ast-page-title-wrap,
body.page .ast-single-entry-banner,
body.page .ast-single-entry-banner[data-post-type="page"],
body.page .ast-banner-title,
body.page .ast-banner-title-area,
body.page .ast-page-title-bar,
body.page .ast-title-bar-wrap,
body.page .ast-archive-description,
body.page .ast-advanced-headers-wrap,
body.page .ast-advanced-headers-layout,
body.page .ast-single-post-order > .entry-title,
body.page .entry-title,
body.page h1.entry-title,
body.page .wp-block-post-title {
    display:none !important;
    visibility:hidden !important;
    height:0 !important;
    min-height:0 !important;
    max-height:0 !important;
    margin:0 !important;
    padding:0 !important;
    border:0 !important;
    overflow:hidden !important;
}
body.page .site-content,
body.page .site-content > .ast-container,
body.page .content-area,
body.page .site-main,
body.page article.page,
body.page .ast-article-single,
body.page .entry-content {
    margin-top:0 !important;
    padding-top:0 !important;
}
.h18-site-header.h18-scroll-sticky {
    position:sticky !important;
    top:0 !important;
    z-index:10050 !important;
}
body.admin-bar .h18-site-header.h18-scroll-sticky {
    top:32px !important;
}
@media (max-width:782px) {
    body.admin-bar .h18-site-header.h18-scroll-sticky {
        top:46px !important;
    }
}
.h18-desktop-nav .h18-web-menu-root > .h18-menu-item {
    position:relative !important;
}
.h18-desktop-nav .h18-submenu {
    display:none !important;
    position:absolute !important;
    z-index:10020 !important;
    top:100% !important;
    left:0 !important;
    min-width:220px !important;
    margin:0 !important;
    padding:8px !important;
    flex-direction:column !important;
    align-items:stretch !important;
    background:#30382a !important;
    border-radius:0 0 6px 6px !important;
    box-shadow:0 6px 18px rgba(0,0,0,.22) !important;
}
.h18-desktop-nav .h18-menu-item-has-children:hover > .h18-submenu,
.h18-desktop-nav .h18-menu-item-has-children:focus-within > .h18-submenu {
    display:flex !important;
}
.h18-desktop-nav .h18-submenu > li {
    width:100% !important;
    display:block !important;
}
.h18-desktop-nav .h18-submenu a {
    display:block !important;
    white-space:nowrap !important;
}
.h18-mobile-menu-panel .h18-submenu {
    display:block !important;
    position:static !important;
    margin:4px 0 4px 14px !important;
    padding-left:12px !important;
    border-left:2px solid rgba(195,174,131,.55) !important;
}
</style>
<!-- /wp:html -->
<!-- HANGAR18-WEB-OVERRIDE-END -->
HTML;
    }

    private function get_managed_pages() {
        $all = get_posts([
            'post_type'        => 'page',
            'post_status'      => ['publish', 'draft', 'private', 'pending', 'future'],
            'posts_per_page'   => -1,
            'orderby'          => 'ID',
            'order'            => 'ASC',
            'suppress_filters' => false,
        ]);

        $fixed = [
            self::HOME_SLUG,
            'om-foreningen',
            self::VEHICLE_PARENT_SLUG,
            self::EVENT_PARENT_SLUG,
            self::GALLERY_PARENT_SLUG,
            'bliv-medlem',
            'kontakt',
            'koeretoejsskabelon',
            'eventskabelon',
        ];

        $root_ids = [];
        foreach ([self::VEHICLE_PARENT_SLUG, self::EVENT_PARENT_SLUG, self::GALLERY_PARENT_SLUG] as $slug) {
            $root = $this->post_by_slug($slug);
            if ($root) {
                $root_ids[] = (int) $root->ID;
            }
        }

        $managed = [];
        $managed_ids = [];

        foreach ($all as $page) {
            if ($page->post_name === 'hangar18-configuration-store') {
                continue;
            }

            if (in_array($page->post_name, $fixed, true)) {
                $managed[(int) $page->ID] = $page;
                $managed_ids[(int) $page->ID] = true;
            }
        }

        $changed = true;
        while ($changed) {
            $changed = false;

            foreach ($all as $page) {
                $id = (int) $page->ID;
                $parent = (int) $page->post_parent;

                if (isset($managed[$id])) {
                    continue;
                }

                if (in_array($parent, $root_ids, true) || isset($managed_ids[$parent])) {
                    $managed[$id] = $page;
                    $managed_ids[$id] = true;
                    $changed = true;
                }
            }
        }

        ksort($managed);
        return array_values($managed);
    }

    private function apply_design_override_to_post($post) {
        $content = $this->strip_block($post->post_content, self::OVERRIDE_START, self::OVERRIDE_END);
        $override = $this->build_design_override_block();

        $footer = $this->extract_block($content, self::FOOTER_START, self::FOOTER_END);

        if ($footer) {
            $content = str_replace($footer, trim($override) . "\n\n" . $footer, $content);
        } else {
            $content .= "\n\n" . trim($override);
        }

        return $content;
    }

    private function field($name, $label, $value, $type = 'text', $required = false, $help = '') {
        ?>
        <div class="h18-field">
            <label for="h18-<?php echo esc_attr($name); ?>"><strong><?php echo esc_html($label); ?></strong></label>
            <input
                id="h18-<?php echo esc_attr($name); ?>"
                type="<?php echo esc_attr($type); ?>"
                name="<?php echo esc_attr($name); ?>"
                value="<?php echo esc_attr($value); ?>"
                <?php echo $required ? 'required' : ''; ?>
            />
            <?php if ($help !== '') : ?>
                <p class="description"><?php echo esc_html($help); ?></p>
            <?php endif; ?>
        </div>
        <?php
    }

    private function textarea($name, $label, $value, $rows = 6) {
        ?>
        <div class="h18-field">
            <label for="h18-<?php echo esc_attr($name); ?>"><strong><?php echo esc_html($label); ?></strong></label>
            <textarea id="h18-<?php echo esc_attr($name); ?>" name="<?php echo esc_attr($name); ?>" rows="<?php echo esc_attr($rows); ?>"><?php echo esc_textarea($value); ?></textarea>
        </div>
        <?php
    }

    private function select_field($name, $label, $value, array $options, $help = '') {
        ?>
        <div class="h18-field">
            <label for="h18-<?php echo esc_attr($name); ?>"><strong><?php echo esc_html($label); ?></strong></label>
            <select id="h18-<?php echo esc_attr($name); ?>" name="<?php echo esc_attr($name); ?>">
                <?php foreach ($options as $key => $text) : ?>
                    <option value="<?php echo esc_attr($key); ?>" <?php selected((string) $value, (string) $key); ?>>
                        <?php echo esc_html($text); ?>
                    </option>
                <?php endforeach; ?>
            </select>
            <?php if ($help !== '') : ?>
                <p class="description"><?php echo esc_html($help); ?></p>
            <?php endif; ?>
        </div>
        <?php
    }

    private function render_media_field($media_id, $media_url, $prefix = 'main') {
        ?>
        <input id="h18-<?php echo esc_attr($prefix); ?>-media-id" type="hidden" name="<?php echo esc_attr($prefix); ?>_media_id" value="<?php echo esc_attr($media_id); ?>" />
        <input id="h18-<?php echo esc_attr($prefix); ?>-media-url" type="hidden" name="<?php echo esc_attr($prefix); ?>_media_url" value="<?php echo esc_attr($media_url); ?>" />

        <div
            id="h18-<?php echo esc_attr($prefix); ?>-media-preview"
            class="h18-media-preview"
            data-media-prefix="<?php echo esc_attr($prefix); ?>"
        >
            <?php if ($media_url) : ?>
                <img src="<?php echo esc_url($media_url); ?>" alt="" />
            <?php else : ?>
                <span>Intet hovedbillede valgt</span>
            <?php endif; ?>
        </div>

        <p>
            <button type="button" class="button button-secondary h18-select-media" data-media-prefix="<?php echo esc_attr($prefix); ?>">Vælg / upload billede</button>
            <button type="button" class="button h18-remove-media" data-media-prefix="<?php echo esc_attr($prefix); ?>">Fjern billede</button>
        </p>
        <?php
    }

    public function render_dashboard() {
        $this->require_capability();

        $vehicles = $this->get_vehicle_pages(false);
        $events   = $this->get_event_pages(false);
        $albums   = $this->get_gallery_pages(false);

        ?>
        <div class="wrap h18-admin">
            <h1>Hangar18 Manager</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-hero-panel">
                <div>
                    <span class="h18-kicker">Web Manager v<?php echo esc_html(self::VERSION); ?></span>
                    <h2>Aalborg Kaserners Veteran Panser- og Køretøjsforening</h2>
                    <p>Web-manageren arbejder direkte på de eksisterende WordPress-sider og gemmer indstillingerne centralt i WordPress.</p>
                </div>
                <div class="h18-safe-badge">WhatIf er FRA som standard</div>
            </div>

            <div class="h18-stat-grid">
                <div class="h18-stat-card"><strong><?php echo esc_html(count($vehicles)); ?></strong><span>Køretøjer</span></div>
                <div class="h18-stat-card"><strong><?php echo esc_html(count($events)); ?></strong><span>Events</span></div>
                <div class="h18-stat-card"><strong><?php echo esc_html(count($albums)); ?></strong><span>Gallerialbums</span></div>
                <div class="h18-stat-card"><strong><?php echo esc_html(count($this->get_managed_pages())); ?></strong><span>Styrede sider</span></div>
            </div>

            <div class="h18-module-grid">
                <?php
                $modules = [
                    ['hangar18-vehicles', 'dashicons-car', 'Køretøjer', 'Opret og redigér køretøjer, billeder, tekniske data og placering.', 'Aktiv'],
                    ['hangar18-events', 'dashicons-calendar-alt', 'Events', 'Opret arrangementer og forbind dem til et album i Billedgalleri.', 'Aktiv'],
                    ['hangar18-gallery', 'dashicons-format-gallery', 'Billedgalleri', 'Opret albums, vælg flere billeder og sortér med drag-and-drop.', 'Aktiv'],
                    ['hangar18-data', 'dashicons-database', 'Data', 'Byg egne datatyper og redigér validerede entries med tekst, tal, bool, dato og medier.', 'Aktiv'],
                    ['hangar18-pages', 'dashicons-layout', 'Sider', 'Redigér almindelige sider med indholdssektioner, mailformularer og afstemninger.', 'Aktiv'],
                    ['hangar18-menu', 'dashicons-menu', 'Menu', 'WordPress-menu, drag-and-drop, undermenuer, Hjem, dubletkontrol og Hangar18-header-synkronisering.', 'Aktiv'],
                    ['hangar18-header-footer', 'dashicons-layout', 'Header / Footer', 'Sticky header, bredde, skalaer, placering og global shell-synkronisering.', 'Aktiv'],
                    ['hangar18-backup', 'dashicons-backup', 'Backup', 'Manuel samlet backup og oversigt over automatisk oprettede JSON-backups.', 'Aktiv'],
                    ['hangar18-updates', 'dashicons-update', 'Opdateringer', 'GitHub-versionstjek, SHA-256, automatisk backup, installation og rollback.', 'Aktiv'],
                    ['hangar18-log', 'dashicons-list-view', 'Log', 'Web-managerens checkpoints, WhatIf, fejl og succeser.', 'Aktiv'],
                ];

                foreach ($modules as $module) :
                ?>
                    <a class="h18-module-card h18-module-active" href="<?php echo esc_url(admin_url('admin.php?page=' . $module[0])); ?>">
                        <span class="dashicons <?php echo esc_attr($module[1]); ?>"></span>
                        <h3><?php echo esc_html($module[2]); ?></h3>
                        <p><?php echo esc_html($module[3]); ?></p>
                        <span class="h18-module-status"><?php echo esc_html($module[4]); ?></span>
                    </a>
                <?php endforeach; ?>
            </div>
        </div>
        <?php
    }

    /* ================================================================
       VEHICLES
       ================================================================ */

    private function build_vehicle_core($page_id, array $data) {
        $id        = (int) $page_id;
        $name      = $this->h($this->value($data, 'Name'));
        $short     = $this->h($this->value($data, 'ShortDescription'));
        $type      = $this->h($this->value($data, 'Type'));
        $maker     = $this->h($this->value($data, 'Manufacturer'));
        $year      = $this->h($this->value($data, 'ProductionYear'));
        $engine    = $this->h($this->value($data, 'Engine'));
        $weight    = $this->h($this->value($data, 'Weight'));
        $crew      = $this->h($this->value($data, 'Crew'));
        $period    = $this->h($this->value($data, 'ServicePeriod'));
        $state     = $this->h($this->value($data, 'RestorationStatus'));
        $technical_rows = $this->build_vehicle_field_rows($data, 'detail');
        $history   = $this->hm($this->value($data, 'History'));
        $aalborg   = $this->hm($this->value($data, 'AalborgService'));
        $restore   = $this->hm($this->value($data, 'RestorationText'));
        $media_id  = absint($data['MainMediaId'] ?? 0);
        $media_url = esc_url((string) ($data['MainMediaUrl'] ?? ''));

        $register_settings = $this->get_vehicle_register_settings();
        $detail_alignment = strtolower(
            (string) $register_settings['DetailAlignment']
        );
        $detail_text_alignment = $detail_alignment === 'left' ? 'left' : 'center';
        $detail_outer_margin = $detail_alignment === 'left' ? '0 auto 0 0' : '0 auto';
        $detail_root_class = $detail_alignment === 'left' ? 'h18-align-left' : 'h18-align-center';
        $mobile_detail_alignment = strtolower(
            (string) $register_settings['MobileDetailAlignment']
        );
        $mobile_detail_text_alignment = $mobile_detail_alignment === 'left' ? 'left' : 'center';
        $mobile_detail_outer_margin = $mobile_detail_alignment === 'left' ? '0 auto 0 0' : '0 auto';

        $detail_class = in_array(
            $detail_alignment,
            ['left', 'center'],
            true
        )
            ? 'avpf-vehicle-detail-' . $detail_alignment
            : 'avpf-vehicle-detail-center';

        $image = '<div class="avpf-photo-placeholder"><p>Hovedbillede mangler</p></div>';
        if ($media_id > 0) {
            $url = wp_get_attachment_url($media_id);
            if ($url) {
                $media_url = esc_url($url);
            }
        }
        if ($media_url) {
            $image = '<figure class="wp-block-image size-large h18-vehicle-main-image"><img src="' .
                $media_url . '" alt="' . esc_attr($name) . '" /></figure>';
        }

        $lead = $short !== ''
            ? '<p class="h18-vehicle-lead">' . $short . '</p>'
            : '';

        $marker = $this->encode_marker(self::VEHICLE_MARKER, $data);

        return <<<HTML
{$marker}
<!-- wp:html -->
<style>
body.page-id-{$id} .entry-title, body.page-id-{$id} .wp-block-post-title{display:none}
body.page-id-{$id} .h18-vehicle-hero{background:#30382a;color:#f2f0e8;padding:48px 22px;text-align:{$detail_text_alignment}}
body.page-id-{$id} .h18-vehicle-hero h1, body.page-id-{$id} .h18-vehicle-hero p{color:#f2f0e8;text-align:{$detail_text_alignment}!important}
body.page-id-{$id} .h18-vehicle-content{padding:42px 20px}
body.page-id-{$id} .h18-vehicle-inner{width:min(1100px,100%);max-width:1100px;margin:{$detail_outer_margin}!important;text-align:{$detail_text_alignment}!important;box-sizing:border-box} body.page-id-{$id} .h18-vehicle-inner.h18-align-left{margin-left:0!important;margin-right:auto!important} body.page-id-{$id} .h18-vehicle-inner.h18-align-center{margin-left:auto!important;margin-right:auto!important}
body.page-id-{$id} .h18-vehicle-main-layout{display:grid!important;grid-template-columns:minmax(0,55fr) minmax(0,45fr)!important;gap:32px!important;align-items:start!important;width:min(1100px,100%)!important;max-width:1100px!important;box-sizing:border-box!important}
body.page-id-{$id} .h18-vehicle-main-layout>.wp-block-column{min-width:0!important;margin:0!important}
body.page-id-{$id} .h18-vehicle-main-layout.avpf-vehicle-detail-left{margin-left:0!important;margin-right:auto!important}
body.page-id-{$id} .h18-vehicle-main-layout.avpf-vehicle-detail-center{margin-left:auto!important;margin-right:auto!important}
body.page-id-{$id} .h18-vehicle-main-image img{width:100%;height:auto;border-radius:7px}
body.page-id-{$id} .avpf-photo-placeholder{min-height:260px;background:#f2f0e8;border:1px dashed #8b4a2b;display:flex;align-items:center;justify-content:center;border-radius:7px}
body.page-id-{$id} .h18-vehicle-table{width:100%;border-collapse:collapse;text-align:left}
body.page-id-{$id} .h18-vehicle-table th,body.page-id-{$id} .h18-vehicle-table td{padding:9px 11px;border-bottom:1px solid rgba(48,56,42,.14);vertical-align:top}
body.page-id-{$id} .h18-vehicle-table th{width:40%;background:#f2f0e8}
body.page-id-{$id} .h18-color-value{display:inline-flex;align-items:center;gap:8px}.h18-color-swatch{display:inline-block;width:18px;height:18px;border:1px solid rgba(48,56,42,.35);border-radius:4px}.h18-field-empty{opacity:.65}
body.page-id-{$id} .h18-vehicle-section{margin-top:32px}
@media(max-width:782px){body.page-id-{$id} .h18-vehicle-content{padding:30px 15px}body.page-id-{$id} .h18-vehicle-hero,body.page-id-{$id} .h18-vehicle-hero h1,body.page-id-{$id} .h18-vehicle-hero p,body.page-id-{$id} .h18-vehicle-inner{text-align:{$mobile_detail_text_alignment}!important}body.page-id-{$id} .h18-vehicle-inner,body.page-id-{$id} .h18-vehicle-inner.h18-align-left,body.page-id-{$id} .h18-vehicle-inner.h18-align-center{margin:{$mobile_detail_outer_margin}!important}body.page-id-{$id} .h18-vehicle-main-layout,body.page-id-{$id} .h18-vehicle-main-layout.avpf-vehicle-detail-left,body.page-id-{$id} .h18-vehicle-main-layout.avpf-vehicle-detail-center{grid-template-columns:minmax(0,1fr)!important;gap:24px!important;margin:{$mobile_detail_outer_margin}!important}body.page-id-{$id} .h18-vehicle-main-layout>.wp-block-column{width:100%!important;flex-basis:auto!important}}
</style>
<!-- /wp:html -->
<div class="h18-vehicle-hero">
<h1 class="has-text-align-center">{$name}</h1>
{$lead}
</div>
<div class="h18-vehicle-content">
<div class="h18-vehicle-inner {$detail_root_class}">
<div class="wp-block-columns h18-vehicle-main-layout {$detail_class}">
<div class="wp-block-column" style="flex-basis:55%">{$image}</div>
<div class="wp-block-column" style="flex-basis:45%">
<h2>Tekniske data</h2>
<table class="h18-vehicle-table"><tbody>
{$technical_rows}
</tbody></table>
</div>
</div>
<div class="h18-vehicle-section"><h2>Historik</h2><p>{$history}</p></div>
<div class="h18-vehicle-section"><h2>Tjeneste ved Aalborg Kaserner</h2><p>{$aalborg}</p></div>
<div class="h18-vehicle-section"><h2>Restaurering og status</h2><p>{$restore}</p></div>
</div>
</div>
HTML;
    }

    private function build_vehicle_register_core(array $vehicles) {
        $cards = '';

        $register_settings = $this->get_vehicle_register_settings();
        $register_alignment =
            ((string) $register_settings['RegisterAlignment'] === 'Left')
                ? 'left'
                : 'center';
        $register_alignment_class =
            $register_alignment === 'left'
                ? 'h18-register-align-left'
                : 'h18-register-align-center';
        $mobile_register_alignment =
            ((string) $register_settings['MobileRegisterAlignment'] === 'Left')
                ? 'left'
                : 'center';
        $mobile_register_justify = $mobile_register_alignment === 'left' ? 'start' : 'center';

        foreach ($vehicles as $vehicle) {
            $data = $this->decode_marker(self::VEHICLE_MARKER, $vehicle->post_content) ?: [];

            $featured = get_post_thumbnail_id($vehicle->ID);
            $image = '<div class="h18-register-placeholder">Billede kommer</div>';
            if ($featured) {
                $src = wp_get_attachment_image_url($featured, 'large');
                if ($src) {
                    $image = '<img src="' . esc_url($src) . '" alt="' . esc_attr($vehicle->post_title) . '" loading="lazy" />';
                }
            }

            $field_rows = $this->build_vehicle_field_rows($data, 'register');

            $cards .= '<article class="h18-vehicle-card">' .
                '<a href="' . esc_url(get_permalink($vehicle)) . '">' .
                '<div class="h18-vehicle-card-image">' . $image . '</div>' .
                '<div class="h18-vehicle-card-body">' .
                '<h3>' . esc_html($vehicle->post_title) . '</h3>' .
                '<table><tbody>' . $field_rows . '</tbody></table><span class="h18-card-link">Se køretøjet →</span>' .
                '</div></a></article>';
        }

        if ($cards === '') {
            $cards = '<div class="h18-register-empty"><strong>Der er endnu ikke publiceret køretøjer.</strong></div>';
        }

        return <<<HTML
<!-- wp:html -->
<style>
.h18-overview-title{margin:0 0 22px;font-size:clamp(2rem,4vw,3.2rem);line-height:1.08;color:#30382a}.h18-vehicle-register{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,350px));gap:24px;margin-top:30px;width:100%}
.h18-register-align-left{justify-content:start}
.h18-register-align-center{justify-content:center}
.h18-vehicle-card{width:100%;max-width:350px;overflow:hidden;border-radius:8px;background:#f2f0e8;border:1px solid rgba(48,56,42,.14);box-shadow:0 4px 16px rgba(0,0,0,.07)}
.h18-vehicle-card>a{display:block;height:100%;color:#30382a;text-decoration:none}
.h18-vehicle-card-image{aspect-ratio:16/10;overflow:hidden;background:#525a5f}
.h18-vehicle-card-image img{width:100%;height:100%;object-fit:cover;display:block}
.h18-register-placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:#f2f0e8;min-height:180px}
.h18-vehicle-card-body{padding:20px 22px 22px}
.h18-vehicle-card-body h3{margin:0 0 14px;font-size:1.35rem}
.h18-vehicle-card table{width:100%;border-collapse:collapse;table-layout:fixed}
.h18-vehicle-card th,.h18-vehicle-card td{padding:7px 8px;border-bottom:1px solid rgba(48,56,42,.12);vertical-align:top}
.h18-vehicle-card th{width:42%;text-align:left;background:rgba(195,174,131,.18)}
.h18-color-value{display:inline-flex;align-items:center;gap:7px}.h18-color-swatch{display:inline-block;width:16px;height:16px;border:1px solid rgba(48,56,42,.35);border-radius:4px}.h18-field-empty{opacity:.65}
.h18-card-link{display:inline-block;margin-top:12px;color:#8b4a2b;font-weight:700}
.h18-register-empty{grid-column:1/-1;padding:26px;background:#f2f0e8;text-align:center}
@media(max-width:782px){.h18-register-intro{text-align:{$mobile_register_alignment}!important}.h18-vehicle-register,.h18-vehicle-register.h18-register-align-left,.h18-vehicle-register.h18-register-align-center{grid-template-columns:1fr;justify-content:{$mobile_register_justify}!important}.h18-vehicle-card{max-width:none}.h18-vehicle-card-body{text-align:{$mobile_register_alignment}!important}.h18-vehicle-card table{text-align:left!important}}
</style>
<div class="h18-register-intro" style="text-align:{$register_alignment}">
<h1 class="h18-overview-title">Køretøjer og materiel</h1>
<h2>Historisk materiel</h2>
<p>Her finder du foreningens dokumenterede køretøjer og øvrige militærhistoriske materiel.</p>
</div>
<div class="h18-vehicle-register {$register_alignment_class}">{$cards}</div>
<!-- /wp:html -->
HTML;
    }

    private function rebuild_vehicle_register() {
        $parent = $this->post_by_slug(self::VEHICLE_PARENT_SLUG);
        if (!$parent) {
            throw new RuntimeException("Siden 'Køretøjer og materiel' blev ikke fundet.");
        }

        $core = $this->build_vehicle_register_core($this->get_vehicle_pages(true));
        $content = $this->wrap_with_shell($core, $parent->ID);

        $result = wp_update_post(['ID' => $parent->ID, 'post_content' => $content], true);
        if (is_wp_error($result)) {
            throw new RuntimeException($result->get_error_message());
        }

        $this->log('INFO', 'VEHICLE_REGISTER_UPDATED', 'Køretøjsregisteret blev genbygget.');
    }

    public function render_vehicles() {
        $this->require_capability();

        $vehicle_id = isset($_GET['vehicle_id']) ? absint($_GET['vehicle_id']) : 0;
        $vehicle = $vehicle_id ? get_post($vehicle_id) : null;
        $data = $vehicle ? ($this->decode_marker(self::VEHICLE_MARKER, $vehicle->post_content) ?: []) : [];

        $media_id = $vehicle ? (int) get_post_thumbnail_id($vehicle->ID) : absint($data['MainMediaId'] ?? 0);
        $media_url = $media_id ? wp_get_attachment_url($media_id) : (string) ($data['MainMediaUrl'] ?? '');

        ?>
        <div class="wrap h18-admin">
            <h1>Køretøjer</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan styres køretøjer:</strong>
                Vælg et eksisterende køretøj eller opret et nyt. WhatIf er slået fra som standard.
                <strong>Registerlayout</strong> er en global indstilling for køretøjsoversigten og detaljesiderne.
                Tekniske felter styres nu under <strong>Køretøjsfelter</strong>; de kan aktiveres/deaktiveres, omdøbes, flyttes og udvides uden at slette eksisterende værdier.
            </div>

            <?php $vehicle_layout = $this->get_vehicle_register_settings(); ?>
            <form class="h18-layout-card" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_vehicle_register_settings'); ?>
                <input type="hidden" name="action" value="h18_save_vehicle_register_settings" />

                <div class="h18-layout-card-header">
                    <h2>Placering af køretøjer</h2>
                    <p>Vælg placeringen særskilt for oversigten og de enkelte køretøjssider.</p>
                </div>

                <div class="h18-layout-devices">
                    <fieldset class="h18-layout-device">
                        <legend>Desktop</legend>
                        <div class="h18-layout-fields">
                            <div class="h18-field">
                                <label><strong>Oversigten</strong></label>
                                <select name="register_alignment">
                                    <option value="Left" <?php selected($vehicle_layout['RegisterAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($vehicle_layout['RegisterAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Overskrift, introduktion og køretøjskort.</p>
                            </div>
                            <div class="h18-field">
                                <label><strong>De enkelte køretøjer</strong></label>
                                <select name="detail_alignment">
                                    <option value="Left" <?php selected($vehicle_layout['DetailAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($vehicle_layout['DetailAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Indholdet på hver køretøjsside.</p>
                            </div>
                        </div>
                    </fieldset>

                    <fieldset class="h18-layout-device">
                        <legend>Mobil</legend>
                        <div class="h18-layout-fields">
                            <div class="h18-field">
                                <label><strong>Oversigten</strong></label>
                                <select name="mobile_register_alignment">
                                    <option value="Left" <?php selected($vehicle_layout['MobileRegisterAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($vehicle_layout['MobileRegisterAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Overskrift, introduktion og køretøjskort.</p>
                            </div>
                            <div class="h18-field">
                                <label><strong>De enkelte køretøjer</strong></label>
                                <select name="mobile_detail_alignment">
                                    <option value="Left" <?php selected($vehicle_layout['MobileDetailAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($vehicle_layout['MobileDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Indholdet på hver køretøjsside.</p>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div class="h18-layout-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér kun for at kontrollere valgene uden at gemme eller ændre sider.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-secondary" type="submit">Gem layout og anvend</button>
                        <div class="h18-action-copy"><strong>Gemmer placeringerne</strong><span>Opdaterer køretøjsoversigten og alle eksisterende køretøjssider.</span></div>
                    </div>
                </div>
            </form>

            <div class="h18-toolbar">
                <form method="get">
                    <input type="hidden" name="page" value="hangar18-vehicles" />
                    <label><strong>Eksisterende køretøj</strong></label>
                    <select name="vehicle_id" onchange="this.form.submit()">
                        <option value="0">— Nyt køretøj —</option>
                        <?php foreach ($this->get_vehicle_pages(false) as $item) : ?>
                            <option value="<?php echo esc_attr($item->ID); ?>" <?php selected($vehicle_id, $item->ID); ?>>
                                <?php echo esc_html($item->post_title . ' [' . $item->post_status . ']'); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <a class="button" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-vehicles')); ?>">Nyt</a>
                    <?php if ($vehicle) : ?>
                        <a class="button" target="_blank" rel="noopener" href="<?php echo esc_url(get_permalink($vehicle)); ?>">Åbn side</a>
                    <?php endif; ?>
                </form>
                <p class="h18-toolbar-note"><strong>Nyt</strong> åbner en tom formular. <strong>Åbn side</strong> viser køretøjet på hjemmesiden. <strong>Feltopsætning</strong> styrer de tekniske felter.</p>
                <a class="button button-secondary" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-vehicle-fields')); ?>">Feltopsætning</a>
            </div>

            <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_vehicle'); ?>
                <input type="hidden" name="action" value="h18_save_vehicle" />
                <input type="hidden" name="vehicle_id" value="<?php echo esc_attr($vehicle_id); ?>" />

                <div class="h18-form-header">
                    <div>
                        <h2><?php echo $vehicle ? 'Redigér: ' . esc_html($vehicle->post_title) : 'Nyt køretøj'; ?></h2>
                    </div>
                    <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                </div>

                <div class="h18-form-grid">
                    <section class="h18-panel">
                        <h3>Grunddata</h3>
                        <?php
                        $this->field('name', 'Navn', $vehicle ? $vehicle->post_title : $this->value($data, 'Name'), 'text', true);
                        $this->field('slug', 'Slug', $vehicle ? $vehicle->post_name : $this->value($data, 'Slug'));
                        $this->field('short_description', 'Kort beskrivelse', $this->value($data, 'ShortDescription'));
                        $this->field('technical_source_url', 'Teknisk kilde-URL', $this->value($data, 'TechnicalSourceUrl'), 'url');

                        $this->select_field(
                            'status',
                            'Status',
                            $vehicle ? $vehicle->post_status : 'draft',
                            ['draft' => 'Draft', 'publish' => 'Publiceret']
                        );
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Hovedbillede</h3>
                        <?php $this->render_media_field($media_id, $media_url, 'main'); ?>
                    </section>

                    <section class="h18-panel h18-panel-wide">
                        <div class="h18-panel-heading-row">
                            <h3>Tekniske felter</h3>
                            <a class="button button-small" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-vehicle-fields')); ?>">Feltopsætning</a>
                        </div>
                        <div class="h18-dynamic-fields-grid">
                            <?php
                            $active_vehicle_fields = $this->get_vehicle_fields(true);
                            if (!$active_vehicle_fields) {
                                echo '<p>Ingen tekniske felter er aktive.</p>';
                            } else {
                                foreach ($active_vehicle_fields as $vehicle_field) {
                                    $this->render_vehicle_dynamic_field(
                                        $vehicle_field,
                                        $this->vehicle_field_value($data, $vehicle_field['Key'])
                                    );
                                }
                            }
                            ?>
                        </div>
                    </section>

                    <section class="h18-panel h18-panel-wide">
                        <?php $this->textarea('history', 'Historik', $this->value($data, 'History'), 8); ?>
                    </section>
                    <section class="h18-panel h18-panel-wide">
                        <?php $this->textarea('aalborg_service', 'Tjeneste ved Aalborg Kaserner', $this->value($data, 'AalborgService'), 8); ?>
                    </section>
                    <section class="h18-panel h18-panel-wide">
                        <?php $this->textarea('restoration_text', 'Restaurering og status', $this->value($data, 'RestorationText'), 8); ?>
                    </section>
                </div>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Er simulering markeret, vises resultatet uden at noget bliver gemt.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary button-hero" type="submit">Gem / opdater køretøj</button>
                        <div class="h18-action-copy"><strong>Gemmer hele køretøjet</strong><span>Gemmer data, billede og status og opdaterer derefter køretøjsoversigten.</span></div>
                    </div>
                </div>
            </form>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_rebuild_vehicle_register'); ?>
                <input type="hidden" name="action" value="h18_rebuild_vehicle_register" />
                <div class="h18-whatif-help">
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér for at kontrollere handlingen uden at skrive ændringer.</span></div>
                </div>
                <div class="h18-action-submit">
                    <button class="button" type="submit">Genbyg køretøjsoversigten</button>
                    <div class="h18-action-copy"><strong>Reparation</strong><span>Brug kun hvis oversigten mangler eller ikke viser de gemte køretøjer korrekt. Køretøjsdata ændres ikke.</span></div>
                </div>
            </form>
        </div>
        <?php
    }

    public function render_vehicle_fields() {
        $this->require_capability();
        $settings = $this->get_vehicle_field_settings();
        $fields = $settings['Fields'] ?? [];
        $types = $this->vehicle_field_type_labels();
        ?>
        <div class="wrap h18-admin">
            <h1>Køretøjsfelter</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Feltregister:</strong>
                Her bestemmer du hvilke tekniske oplysninger et køretøj har. Felter kan deaktiveres, omdøbes, flyttes, vises separat på oversigt/detaljeside eller fjernes fra opsætningen.
                <strong>Eksisterende køretøjsdata slettes aldrig</strong>, når et felt deaktiveres eller fjernes. Genopretter du samme nøgle senere, kan værdien bruges igen.
            </div>

            <div class="h18-toolbar">
                <a class="button" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-vehicles')); ?>">← Tilbage til Køretøjer</a>
                <span><strong>Systemfelter</strong> som Navn, Slug, hovedbillede, publiceringsstatus, Historik, Tjeneste ved Aalborg og Restaurering/status ligger fast og slettes ikke her.</span>
            </div>

            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" class="h18-editor-form">
                <?php wp_nonce_field('h18_save_vehicle_fields'); ?>
                <input type="hidden" name="action" value="h18_save_vehicle_fields" />

                <section class="h18-panel h18-panel-wide">
                    <h2>Aktive og gemte felter</h2>
                    <p class="description">Træk i ↕ for at ændre rækkefølge. Feltnøglen kan ikke omdøbes efter oprettelse, fordi den identificerer de gemte værdier.</p>
                    <div class="h18-vehicle-fields-table-wrap">
                        <table class="widefat striped h18-vehicle-fields-table">
                            <thead>
                                <tr>
                                    <th class="h18-field-drag-col">↕</th>
                                    <th>Aktiv</th>
                                    <th>Feltnavn</th>
                                    <th>Nøgle</th>
                                    <th>Type</th>
                                    <th>Oversigt</th>
                                    <th>Detalje</th>
                                    <th>Dropdown-valg</th>
                                    <th>Fjern</th>
                                </tr>
                            </thead>
                            <tbody id="h18-vehicle-fields-sortable">
                            <?php foreach ($fields as $index => $field) : ?>
                                <tr class="h18-vehicle-field-row">
                                    <td><span class="dashicons dashicons-move h18-vehicle-field-drag-handle" title="Flyt"></span><input class="h18-vehicle-field-order" type="hidden" name="fields[<?php echo esc_attr($index); ?>][order]" value="<?php echo esc_attr($field['Order']); ?>" /></td>
                                    <td><input type="checkbox" name="fields[<?php echo esc_attr($index); ?>][active]" value="1" <?php checked(!empty($field['Active'])); ?> /></td>
                                    <td><input type="text" name="fields[<?php echo esc_attr($index); ?>][label]" value="<?php echo esc_attr($field['Label']); ?>" required /></td>
                                    <td><code><?php echo esc_html($field['Key']); ?></code><input type="hidden" name="fields[<?php echo esc_attr($index); ?>][key]" value="<?php echo esc_attr($field['Key']); ?>" /></td>
                                    <td>
                                        <select name="fields[<?php echo esc_attr($index); ?>][type]">
                                            <?php foreach ($types as $type_key => $type_label) : ?>
                                                <option value="<?php echo esc_attr($type_key); ?>" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option>
                                            <?php endforeach; ?>
                                        </select>
                                    </td>
                                    <td><input type="checkbox" name="fields[<?php echo esc_attr($index); ?>][show_register]" value="1" <?php checked(!empty($field['ShowOnRegister'])); ?> /></td>
                                    <td><input type="checkbox" name="fields[<?php echo esc_attr($index); ?>][show_detail]" value="1" <?php checked(!empty($field['ShowOnDetail'])); ?> /></td>
                                    <td><input type="text" name="fields[<?php echo esc_attr($index); ?>][options]" value="<?php echo esc_attr(implode(', ', $field['Options'] ?? [])); ?>" placeholder="Kun dropdown: valg 1, valg 2" /></td>
                                    <td><label><input type="checkbox" name="fields[<?php echo esc_attr($index); ?>][remove]" value="1" /> Fjern</label></td>
                                </tr>
                            <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </section>

                <section class="h18-panel h18-panel-wide">
                    <h2>Tilføj nyt felt</h2>
                    <div class="h18-new-field-grid">
                        <div class="h18-field"><label><strong>Feltnavn</strong></label><input id="h18-new-vehicle-field-label" type="text" name="new_field[label]" placeholder="Fx Farve" /></div>
                        <div class="h18-field"><label><strong>Nøgle</strong></label><input id="h18-new-vehicle-field-key" type="text" name="new_field[key]" placeholder="fx farve" /><p class="description">Genereres automatisk fra navnet, hvis den er tom.</p></div>
                        <div class="h18-field"><label><strong>Type</strong></label><select name="new_field[type]">
                            <?php foreach ($types as $type_key => $type_label) : ?><option value="<?php echo esc_attr($type_key); ?>"><?php echo esc_html($type_label); ?></option><?php endforeach; ?>
                        </select></div>
                        <div class="h18-field"><label><strong>Dropdown-valg</strong></label><input type="text" name="new_field[options]" placeholder="Fx Grøn, Sand, Sort" /></div>
                    </div>
                    <p>
                        <label><input type="checkbox" name="new_field[active]" value="1" checked /> Aktiv</label>&nbsp;&nbsp;
                        <label><input type="checkbox" name="new_field[show_register]" value="1" /> Vis på køretøjsoversigt</label>&nbsp;&nbsp;
                        <label><input type="checkbox" name="new_field[show_detail]" value="1" checked /> Vis på køretøjsdetalje</label>
                    </p>
                </section>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér for at kontrollere feltændringerne uden at gemme dem.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary button-hero" type="submit">Gem feltopsætning</button>
                        <div class="h18-action-copy"><strong>Opdaterer alle køretøjssider</strong><span>Gemmer aktive felter, navne, rækkefølge og visning. Eksisterende feltværdier slettes ikke.</span></div>
                    </div>
                </div>
            </form>
        </div>
        <?php
    }

    public function handle_save_vehicle_fields() {
        $this->require_capability();
        check_admin_referer('h18_save_vehicle_fields');

        $submitted = isset($_POST['fields']) && is_array($_POST['fields'])
            ? wp_unslash($_POST['fields'])
            : [];
        $new_field = isset($_POST['new_field']) && is_array($_POST['new_field'])
            ? wp_unslash($_POST['new_field'])
            : [];

        $raw_fields = [];
        $seen_keys = [];
        $order = 10;

        foreach ($submitted as $row) {
            if (!is_array($row) || !empty($row['remove'])) {
                continue;
            }

            $key = sanitize_key((string) ($row['key'] ?? ''));
            $label = sanitize_text_field((string) ($row['label'] ?? ''));
            if ($key === '' || $label === '') {
                continue;
            }
            if (isset($seen_keys[$key])) {
                $this->set_notice('error', "Feltnøglen '{$key}' findes mere end én gang.");
                $this->redirect('hangar18-vehicle-fields');
            }
            $seen_keys[$key] = true;

            $raw_fields[] = [
                'Key'            => $key,
                'Label'          => $label,
                'Type'           => sanitize_key((string) ($row['type'] ?? 'text')),
                'Active'         => !empty($row['active']),
                'ShowOnRegister' => !empty($row['show_register']),
                'ShowOnDetail'   => !empty($row['show_detail']),
                'Options'        => (string) ($row['options'] ?? ''),
                'Order'          => is_numeric($row['order'] ?? null) ? (int) $row['order'] : $order,
            ];
            $order += 10;
        }

        $new_label = sanitize_text_field((string) ($new_field['label'] ?? ''));
        if ($new_label !== '') {
            $new_key = sanitize_key((string) ($new_field['key'] ?? ''));
            if ($new_key === '') {
                $new_key = sanitize_key(str_replace('-', '_', sanitize_title($new_label)));
            }
            if ($new_key === '') {
                $this->set_notice('error', 'Det nye felt kunne ikke få en gyldig nøgle.');
                $this->redirect('hangar18-vehicle-fields');
            }
            if (isset($seen_keys[$new_key])) {
                $this->set_notice('error', "Feltnøglen '{$new_key}' findes allerede.");
                $this->redirect('hangar18-vehicle-fields');
            }

            $raw_fields[] = [
                'Key'            => $new_key,
                'Label'          => $new_label,
                'Type'           => sanitize_key((string) ($new_field['type'] ?? 'text')),
                'Active'         => !empty($new_field['active']),
                'ShowOnRegister' => !empty($new_field['show_register']),
                'ShowOnDetail'   => !empty($new_field['show_detail']),
                'Options'        => (string) ($new_field['options'] ?? ''),
                'Order'          => $order,
            ];
        }

        $settings = $this->normalize_vehicle_field_settings([
            'Version' => '1.0',
            'Fields'  => $raw_fields,
        ]);

        if (!empty($_POST['whatif'])) {
            $this->log('WARN', 'WHATIF_VEHICLE_FIELDS_SAVE', '[WHATIF] Ville gemme ' . count($settings['Fields']) . ' køretøjsfelter og genbygge køretøjssiderne.');
            $this->set_notice('warning', 'WHATIF: Feltopsætningen blev valideret, men intet blev gemt eller genbygget.');
            $this->redirect('hangar18-vehicle-fields');
        }

        try {
            $this->create_full_managed_backup('Før køretøjsfeltopsætning blev ændret');
            update_option(self::VEHICLE_FIELDS_OPTION, $settings, false);

            $published = $settings;
            $published['Saved'] = gmdate('c');
            $this->publish_configuration_file('Hangar18-VehicleFields.json', $published);

            $detail_pages = $this->apply_vehicle_detail_alignment_to_existing_pages(
                $this->get_vehicle_register_settings()
            );
            $this->rebuild_vehicle_register();

            $this->log('INFO', 'VEHICLE_FIELDS_SAVE_SUCCESS', 'Køretøjsfelter gemt: ' . count($settings['Fields']) . "; genbygget {$detail_pages} detaljesider.");
            $this->set_notice('success', 'Feltopsætningen er gemt. ' . count($settings['Fields']) . " felter er registreret, og {$detail_pages} køretøjssider er genbygget. Fjernede/deaktiverede feltværdier er bevaret.");
            $this->redirect('hangar18-vehicle-fields');
        } catch (Throwable $e) {
            $this->log('ERROR', 'VEHICLE_FIELDS_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Kunne ikke gemme feltopsætningen: ' . $e->getMessage());
            $this->redirect('hangar18-vehicle-fields');
        }
    }

    public function handle_save_vehicle() {
        $this->require_capability();
        check_admin_referer('h18_save_vehicle');

        $id = absint($_POST['vehicle_id'] ?? 0);
        $whatif = !empty($_POST['whatif']);
        $name = $this->post_text('name');

        if ($name === '') {
            $this->set_notice('error', 'Navn skal udfyldes.');
            $this->redirect('hangar18-vehicles', $id ? ['vehicle_id' => $id] : []);
        }

        $parent = $this->post_by_slug(self::VEHICLE_PARENT_SLUG);
        if (!$parent) {
            $this->set_notice('error', "Siden 'Køretøjer og materiel' findes ikke.");
            $this->redirect('hangar18-vehicles');
        }

        $slug = sanitize_title($this->post_text('slug') ?: $name);
        $status = ($_POST['status'] ?? '') === 'publish' ? 'publish' : 'draft';
        $media_id = absint($_POST['main_media_id'] ?? 0);
        $media_url = $media_id ? wp_get_attachment_url($media_id) : $this->post_url('main_media_url');

        if ($whatif) {
            $this->log('WARN', 'WHATIF_VEHICLE_SAVE', "[WHATIF] Ville gemme '{$name}' ({$slug}) status {$status}.");
            $this->set_notice('warning', "WHATIF: Ville gemme '{$name}'. Ingen data blev ændret.");
            $this->redirect('hangar18-vehicles', $id ? ['vehicle_id' => $id] : []);
        }

        try {
            $target = $id ? get_post($id) : null;

            if (!$target) {
                foreach ($this->get_vehicle_pages(false) as $candidate) {
                    if ($candidate->post_name === $slug) {
                        $target = $candidate;
                        break;
                    }
                }
            }

            $existing_data = $target
                ? ($this->decode_marker(self::VEHICLE_MARKER, $target->post_content) ?: [])
                : [];

            $data = is_array($existing_data) ? $existing_data : [];
            $custom_fields = isset($data['CustomFields']) && is_array($data['CustomFields'])
                ? $data['CustomFields']
                : [];

            // Flyt gamle hårdkodede værdier ind i CustomFields uden at slette legacy-data.
            foreach ($this->vehicle_legacy_field_map() as $field_key => $legacy_key) {
                if (!array_key_exists($field_key, $custom_fields) && array_key_exists($legacy_key, $data)) {
                    $custom_fields[$field_key] = (string) $data[$legacy_key];
                }
            }

            $posted_vehicle_fields = isset($_POST['vehicle_fields']) && is_array($_POST['vehicle_fields'])
                ? $_POST['vehicle_fields']
                : [];

            foreach ($this->get_vehicle_fields(true) as $field) {
                $field_key = (string) $field['Key'];
                $raw = array_key_exists($field_key, $posted_vehicle_fields)
                    ? $posted_vehicle_fields[$field_key]
                    : '';
                $custom_fields[$field_key] = $this->sanitize_vehicle_field_value($field, $raw);
            }

            $data['DataVersion']        = '1.2';
            $data['Name']               = $name;
            $data['Slug']               = $slug;
            $data['ShortDescription']   = $this->post_text('short_description');
            $data['MainMediaId']        = $media_id;
            $data['MainMediaUrl']       = $media_url ?: '';
            $data['History']            = $this->post_textarea('history');
            $data['AalborgService']     = $this->post_textarea('aalborg_service');
            $data['RestorationText']    = $this->post_textarea('restoration_text');
            $data['TechnicalSourceUrl'] = $this->post_url('technical_source_url');
            $data['CustomFields']       = $custom_fields;

            // Legacy aliases bevares for bagudkompatibilitet med eksisterende køretøjsdata.
            foreach ($this->vehicle_legacy_field_map() as $field_key => $legacy_key) {
                if (array_key_exists($field_key, $custom_fields)) {
                    $data[$legacy_key] = (string) $custom_fields[$field_key];
                }
            }

            if ($target) {
                $this->backup_post($target->ID, "Før gem køretøj '{$name}'");
                $id = (int) $target->ID;
            } else {
                $id = wp_insert_post([
                    'post_type'   => 'page',
                    'post_title'  => $name,
                    'post_name'   => $slug,
                    'post_status' => 'draft',
                    'post_parent' => (int) $parent->ID,
                ], true);

                if (is_wp_error($id)) {
                    throw new RuntimeException($id->get_error_message());
                }

                $this->log('INFO', 'VEHICLE_PAGE_CREATED', "Køretøjsside oprettet. ID {$id}.");
            }

            $content = $this->wrap_with_shell($this->build_vehicle_core($id, $data), $id);

            $result = wp_update_post([
                'ID'           => $id,
                'post_title'   => $name,
                'post_name'    => $slug,
                'post_status'  => $status,
                'post_parent'  => (int) $parent->ID,
                'post_excerpt' => $data['ShortDescription'],
                'post_content' => $content,
            ], true);

            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $media_id ? set_post_thumbnail($id, $media_id) : delete_post_thumbnail($id);

            $this->backup_post($parent->ID, "Før genbygning af køretøjsregister efter '{$name}'");
            $this->rebuild_vehicle_register();

            $this->log('INFO', 'VEHICLE_SAVE_SUCCESS', "Køretøj gemt: '{$name}' ID {$id}.");
            $this->set_notice('success', "Køretøjet '{$name}' er gemt, og registeret er genbygget.");
            $this->redirect('hangar18-vehicles', ['vehicle_id' => $id]);

        } catch (Throwable $e) {
            $this->log('ERROR', 'VEHICLE_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Kunne ikke gemme køretøjet: ' . $e->getMessage());
            $this->redirect('hangar18-vehicles', $id ? ['vehicle_id' => $id] : []);
        }
    }

    private function apply_vehicle_detail_alignment_to_existing_pages(array $settings) {
        $count = 0;

        foreach ($this->get_vehicle_pages(false) as $page) {
            $data = $this->decode_marker(
                self::VEHICLE_MARKER,
                $page->post_content
            );

            if (!$data) {
                continue;
            }

            $result = wp_update_post(
                [
                    'ID'           => $page->ID,
                    'post_content' => $this->wrap_with_shell(
                        $this->build_vehicle_core($page->ID, $data),
                        $page->ID
                    ),
                ],
                true
            );

            if (is_wp_error($result)) {
                throw new RuntimeException(
                    "Køretøj ID {$page->ID}: " .
                    $result->get_error_message()
                );
            }

            $count++;
        }

        return $count;
    }

    public function handle_save_vehicle_register_settings() {
        $this->require_capability();
        check_admin_referer('h18_save_vehicle_register_settings');

        $settings = $this->normalize_vehicle_register_settings([
            'Version'                   => '1.4',
            'RegisterAlignment'         => $this->post_text('register_alignment'),
            'CardAlignment'             => $this->post_text('register_alignment'),
            'DetailAlignment'           => $this->post_text('detail_alignment'),
            'MobileRegisterAlignment'   => $this->post_text('mobile_register_alignment'),
            'MobileDetailAlignment'     => $this->post_text('mobile_detail_alignment'),
        ]);

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_VEHICLE_REGISTER_SETTINGS',
                '[WHATIF] Ville gemme køretøjslayout: ' .
                'DesktopRegister=' . $settings['RegisterAlignment'] .
                '; DesktopDetail=' . $settings['DetailAlignment'] .
                '; MobileRegister=' . $settings['MobileRegisterAlignment'] .
                '; MobileDetail=' . $settings['MobileDetailAlignment'] . '.'
            );

            $this->set_notice(
                'warning',
                'WHATIF: Køretøjslayoutet ville blive gemt for desktop og mobil. Ingen data blev ændret.'
            );

            $this->redirect('hangar18-vehicles');
        }

        try {
            $this->create_full_managed_backup(
                'Før globalt køretøjsregister-layout blev ændret'
            );

            update_option(
                self::VEHICLE_REGISTER_OPTION,
                $settings,
                false
            );

            $central = $settings;
            $central['Saved'] = gmdate('c');

            $this->publish_configuration_file(
                'Hangar18-VehicleRegister.json',
                $central
            );

            $detail_pages = $this->apply_vehicle_detail_alignment_to_existing_pages(
                $settings
            );

            $parent = $this->post_by_slug(self::VEHICLE_PARENT_SLUG);
            if ($parent) {
                $this->backup_post(
                    $parent->ID,
                    'Før genbygning af køretøjsregister efter layoutændring'
                );
            }

            $this->rebuild_vehicle_register();

            $this->log(
                'INFO',
                'VEHICLE_REGISTER_SETTINGS_SAVED',
                'Køretøjslayout gemt. ' .
                'DesktopRegister=' . $settings['RegisterAlignment'] .
                '; DesktopDetail=' . $settings['DetailAlignment'] .
                '; MobileRegister=' . $settings['MobileRegisterAlignment'] .
                '; MobileDetail=' . $settings['MobileDetailAlignment'] .
                "; DetailPagesUpdated={$detail_pages}."
            );

            $this->set_notice(
                'success',
                'Køretøjslayoutet er gemt for desktop og mobil, og de eksisterende køretøjssider er opdateret.'
            );

        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'VEHICLE_REGISTER_SETTINGS_SAVE_FAILED',
                $e->getMessage()
            );

            $this->set_notice(
                'error',
                'Køretøjslayout kunne ikke gemmes: ' .
                $e->getMessage()
            );
        }

        $this->redirect('hangar18-vehicles');
    }

    public function handle_rebuild_vehicle_register() {
        $this->require_capability();
        check_admin_referer('h18_rebuild_vehicle_register');

        if (!empty($_POST['whatif'])) {
            $this->set_notice('warning', 'WHATIF: Køretøjsregisteret ville blive genbygget. Ingen data blev ændret.');
            $this->log('WARN', 'WHATIF_VEHICLE_REGISTER', '[WHATIF] Genbygning simuleret.');
            $this->redirect('hangar18-vehicles');
        }

        try {
            $parent = $this->post_by_slug(self::VEHICLE_PARENT_SLUG);
            if ($parent) {
                $this->backup_post($parent->ID, 'Før manuel genbygning af køretøjsregister');
            }
            $this->rebuild_vehicle_register();
            $this->set_notice('success', 'Køretøjsregisteret er genbygget.');
        } catch (Throwable $e) {
            $this->set_notice('error', $e->getMessage());
            $this->log('ERROR', 'VEHICLE_REGISTER_FAILED', $e->getMessage());
        }

        $this->redirect('hangar18-vehicles');
    }

    /* ================================================================
       EVENTS
       ================================================================ */

    private function gallery_album_choices() {
        $choices = [0 => 'Ingen billedalbum'];

        $items = [];
        foreach ($this->get_gallery_pages(true) as $page) {
            $data = $this->decode_marker(self::GALLERY_MARKER, $page->post_content);
            if (!$data) {
                continue;
            }

            $type = $this->value($data, 'AlbumType', 'Andet');
            $name = $this->value($data, 'AlbumName', $page->post_title);

            $items[] = [
                'id'    => (int) $page->ID,
                'type'  => $type,
                'name'  => $name,
                'sort'  => ($type === 'Event' ? '0' : '1') . '|' . $type . '|' . $name,
            ];
        }

        usort($items, static function($a, $b) {
            return strnatcasecmp($a['sort'], $b['sort']);
        });

        foreach ($items as $item) {
            $choices[$item['id']] = $item['type'] . ' – ' . $item['name'];
        }

        return $choices;
    }

    private function build_event_core($page_id, array $data) {
        $id = (int) $page_id;

        $layout = $this->get_content_layout_settings();
        $alignment = $layout['EventDetailAlignment'] === 'Center' ? 'center' : 'left';
        $detail_margin = $alignment === 'center' ? '0 auto' : '0 auto 0 0';
        $mobile_alignment = $layout['MobileEventDetailAlignment'] === 'Center' ? 'center' : 'left';
        $mobile_detail_margin = $mobile_alignment === 'center' ? '0 auto' : '0 auto 0 0';

        $name      = $this->h($this->value($data, 'EventName'));
        $short     = $this->h($this->value($data, 'ShortDescription'));
        $date      = $this->h($this->value($data, 'DisplayDate'));
        $start     = $this->h($this->value($data, 'StartTime'));
        $end       = $this->h($this->value($data, 'EndTime'));
        $venue     = $this->h($this->value($data, 'Venue'));
        $address   = $this->h($this->value($data, 'Address'));
        $contact   = $this->h($this->value($data, 'Contact'));
        $desc      = $this->hm($this->value($data, 'Description'));
        $program   = $this->hm($this->value($data, 'Program'));
        $practical = $this->hm($this->value($data, 'Practical'));

        $media_id = absint($data['MainMediaId'] ?? 0);
        if ($media_id <= 0) {
            // Ældre events kan have featured image uden MainMediaId i markøren.
            $media_id = (int) get_post_thumbnail_id($id);
        }

        $media_url = esc_url((string) ($data['MainMediaUrl'] ?? ''));
        if ($media_id > 0 && wp_get_attachment_url($media_id)) {
            $media_url = esc_url(wp_get_attachment_url($media_id));
        }

        $image = '';
        if ($media_url) {
            $image = '<div class="h18-event-image"><img src="' . $media_url . '" alt="' . esc_attr($name) . '" /></div>';
        }

        $gallery = '';
        $gallery_url = esc_url((string) ($data['GalleryAlbumUrl'] ?? ''));
        if ($gallery_url) {
            $gallery_name = $this->h($this->value($data, 'GalleryAlbumName'));
            $label = $gallery_name ? 'Se billeder fra arrangementet – ' . $gallery_name : 'Se billeder fra arrangementet';
            $gallery = '<div class="h18-event-gallery-link"><a href="' . $gallery_url . '">' . $label . '</a></div>';
        }

        $time = trim($start . ($end ? ' – ' . $end : ''));
        $marker = $this->encode_marker(self::EVENT_MARKER, $data);

        return <<<HTML
{$marker}
<!-- wp:html -->
<style>
body.page-id-{$id} .entry-title,body.page-id-{$id} .wp-block-post-title{display:none}
body.page-id-{$id} .h18-event-hero{padding:48px 22px;background:#30382a;color:#f2f0e8;text-align:{$alignment}}
body.page-id-{$id} .h18-event-hero h1,body.page-id-{$id} .h18-event-hero p{color:#f2f0e8}
body.page-id-{$id} .h18-event-main{max-width:1050px;margin:{$detail_margin};padding:42px 20px;text-align:{$alignment}}
body.page-id-{$id} .h18-event-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:24px 0}
body.page-id-{$id} .h18-event-meta>div{padding:14px;background:#f2f0e8;border-left:4px solid #c3ae83;text-align:{$alignment}}
body.page-id-{$id} .h18-event-section{margin-top:30px}
body.page-id-{$id} .h18-event-image img{width:100%;height:auto;max-height:540px;object-fit:cover;border-radius:8px}
body.page-id-{$id} .h18-event-gallery-link{text-align:{$alignment};margin-top:34px}
body.page-id-{$id} .h18-event-gallery-link a{display:inline-block;padding:13px 22px;background:#30382a;color:#f2f0e8!important;text-decoration:none;border-radius:6px;font-weight:700}
body.page-id-{$id} .h18-event-gallery-link a:hover{background:#8b4a2b}
@media (max-width:782px){body.page-id-{$id} .h18-event-hero,body.page-id-{$id} .h18-event-main,body.page-id-{$id} .h18-event-meta>div,body.page-id-{$id} .h18-event-gallery-link{text-align:{$mobile_alignment}!important}body.page-id-{$id} .h18-event-main{margin:{$mobile_detail_margin}!important}body.page-id-{$id} .h18-event-image{margin-left:auto!important;margin-right:auto!important}}
</style>
<!-- /wp:html -->
<div class="h18-event-hero"><h1>{$name}</h1><p>{$short}</p></div>
<div class="h18-event-main">
{$image}
<div class="h18-event-meta">
<div><strong>Dato</strong><br>{$date}</div>
<div><strong>Tid</strong><br>{$time}</div>
<div><strong>Sted</strong><br>{$venue}</div>
<div><strong>Adresse</strong><br>{$address}</div>
<div><strong>Kontakt</strong><br>{$contact}</div>
</div>
<div class="h18-event-section"><h2>Om arrangementet</h2><p>{$desc}</p></div>
<div class="h18-event-section"><h2>Program</h2><p>{$program}</p></div>
<div class="h18-event-section"><h2>Praktiske oplysninger</h2><p>{$practical}</p></div>
{$gallery}
</div>
HTML;
    }

    private function rebuild_event_register() {
        $parent = $this->post_by_slug(self::EVENT_PARENT_SLUG);
        if (!$parent) {
            throw new RuntimeException("Siden 'Events' blev ikke fundet.");
        }

        $layout = $this->get_content_layout_settings();
        $alignment = $layout['EventIndexAlignment'] === 'Center' ? 'center' : 'left';
        $justify = $layout['EventIndexAlignment'] === 'Center' ? 'center' : 'start';
        $mobile_alignment = $layout['MobileEventIndexAlignment'] === 'Center' ? 'center' : 'left';
        $mobile_justify = $layout['MobileEventIndexAlignment'] === 'Center' ? 'center' : 'start';
        $parent_id = (int) $parent->ID;

        $events = [];
        foreach ($this->get_event_pages(true) as $page) {
            $data = $this->decode_marker(self::EVENT_MARKER, $page->post_content);
            if (!$data) {
                continue;
            }

            $events[] = ['page' => $page, 'data' => $data];
        }

        usort($events, static function($a, $b) {
            return strcmp((string) ($a['data']['EventDate'] ?? ''), (string) ($b['data']['EventDate'] ?? ''));
        });

        $today = current_time('Y-m-d');
        $upcoming = '';
        $past = '';

        foreach ($events as $item) {
            $page = $item['page'];
            $data = $item['data'];
            $date = (string) ($data['EventDate'] ?? '');
            $target = ($date >= $today) ? 'upcoming' : 'past';

            $event_image = '';
            $featured = (int) get_post_thumbnail_id($page->ID);
            $image_url = '';

            if ($featured > 0) {
                $image_url = (string) wp_get_attachment_image_url($featured, 'large');
            }

            if ($image_url === '') {
                $marker_media_id = absint($data['MainMediaId'] ?? 0);
                if ($marker_media_id > 0) {
                    $image_url = (string) wp_get_attachment_image_url($marker_media_id, 'large');
                    if ($image_url === '') {
                        $image_url = (string) wp_get_attachment_url($marker_media_id);
                    }
                }
            }

            if ($image_url === '') {
                $image_url = (string) ($data['MainMediaUrl'] ?? '');
            }

            if ($image_url !== '') {
                $event_image = '<div class="h18-event-card-image"><img src="' .
                    esc_url($image_url) . '" alt="' . esc_attr($page->post_title) .
                    '" loading="lazy" /></div>';
            }

            $card = '<article class="h18-event-card"><a href="' . esc_url(get_permalink($page)) . '">' .
                $event_image .
                '<div class="h18-event-card-body">' .
                '<h3>' . esc_html($page->post_title) . '</h3>' .
                '<p><strong>' . esc_html($data['DisplayDate'] ?? $date) . '</strong>' .
                ($data['Venue'] ?? '' ? ' · ' . esc_html($data['Venue']) : '') .
                '</p><p>' . esc_html($data['ShortDescription'] ?? '') . '</p>' .
                '<span>Læs mere →</span></div></a></article>';

            if ($target === 'upcoming') {
                $upcoming .= $card;
            } else {
                $past .= $card;
            }
        }

        if ($upcoming === '') {
            $upcoming = '<p>Der er ingen kommende arrangementer registreret.</p>';
        }
        if ($past === '') {
            $past = '<p>Der er ingen tidligere arrangementer registreret.</p>';
        }

        $core = <<<HTML
<!-- wp:html -->
<style>
.h18-overview-heading h1{margin:0 0 28px;font-size:clamp(2rem,4vw,3.2rem);line-height:1.08;color:#30382a}.h18-event-register{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,360px));gap:18px;margin:20px 0 34px;justify-content:{$justify}}
.h18-event-card{background:#f2f0e8;border:1px solid rgba(48,56,42,.14);border-radius:8px;overflow:hidden}
.h18-event-card a{display:block;color:#30382a;text-decoration:none;text-align:{$alignment};height:100%}
.h18-event-card-image{aspect-ratio:16/10;overflow:hidden;background:#525a5f}
.h18-event-card-image img{width:100%;height:100%;object-fit:cover;display:block}
.h18-event-card-body{padding:20px}
.h18-event-card h3{margin-top:0}.h18-event-card span{color:#8b4a2b;font-weight:700}
@media (max-width:782px){body.page-id-{$parent_id} .h18-overview-heading,body.page-id-{$parent_id} .h18-event-section-heading,body.page-id-{$parent_id} .h18-event-card a,body.page-id-{$parent_id} .h18-event-register>p{text-align:{$mobile_alignment}!important}body.page-id-{$parent_id} .h18-event-register{justify-content:{$mobile_justify}!important}}
</style>
<div class="h18-overview-heading" style="text-align:{$alignment}"><h1>Events</h1></div>
<div class="h18-event-section-heading" style="text-align:{$alignment}"><h2>Kommende arrangementer</h2></div>
<div class="h18-event-register">{$upcoming}</div>
<div class="h18-event-section-heading" style="text-align:{$alignment}"><h2>Tidligere arrangementer</h2></div>
<div class="h18-event-register">{$past}</div>
<!-- /wp:html -->
HTML;

        $result = wp_update_post([
            'ID' => $parent->ID,
            'post_content' => $this->wrap_with_shell($core, $parent->ID),
        ], true);

        if (is_wp_error($result)) {
            throw new RuntimeException($result->get_error_message());
        }

        $this->log('INFO', 'EVENT_REGISTER_UPDATED', 'Eventregisteret blev genbygget.');
    }

    public function render_events() {
        $this->require_capability();

        $id = isset($_GET['event_id']) ? absint($_GET['event_id']) : 0;
        $post = $id ? get_post($id) : null;
        $data = $post ? ($this->decode_marker(self::EVENT_MARKER, $post->post_content) ?: []) : [];

        $media_id = $post ? (int) get_post_thumbnail_id($post->ID) : absint($data['MainMediaId'] ?? 0);
        $media_url = $media_id ? wp_get_attachment_url($media_id) : (string) ($data['MainMediaUrl'] ?? '');
        $content_layout = $this->get_content_layout_settings();

        ?>
        <div class="wrap h18-admin">
            <h1>Events</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan styres events:</strong>
                Opret eller vælg et event, udfyld dato/tid/sted og vælg eventuelt et eksisterende <strong>Billedalbum</strong>.
                Eventsiden indeholder ikke selv billederne; den viser kun knappen <strong>Se billeder fra arrangementet</strong>.
            </div>

            <form class="h18-layout-card" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_event_layout'); ?>
                <input type="hidden" name="action" value="h18_save_event_layout" />
                <div class="h18-layout-card-header">
                    <h2>Placering af events</h2>
                    <p>Vælg placeringen særskilt for eventoversigten og de enkelte eventsider.</p>
                </div>
                <div class="h18-layout-devices">
                    <fieldset class="h18-layout-device">
                        <legend>Desktop</legend>
                        <div class="h18-layout-fields">
                            <div class="h18-field">
                                <label><strong>Oversigten</strong></label>
                                <select name="event_index_alignment">
                                    <option value="Left" <?php selected($content_layout['EventIndexAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['EventIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Overskrifter og eventkort.</p>
                            </div>
                            <div class="h18-field">
                                <label><strong>De enkelte events</strong></label>
                                <select name="event_detail_alignment">
                                    <option value="Left" <?php selected($content_layout['EventDetailAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['EventDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Indholdet på hver eventside.</p>
                            </div>
                        </div>
                    </fieldset>
                    <fieldset class="h18-layout-device">
                        <legend>Mobil</legend>
                        <div class="h18-layout-fields">
                            <div class="h18-field">
                                <label><strong>Oversigten</strong></label>
                                <select name="mobile_event_index_alignment">
                                    <option value="Left" <?php selected($content_layout['MobileEventIndexAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['MobileEventIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Overskrifter og eventkort.</p>
                            </div>
                            <div class="h18-field">
                                <label><strong>De enkelte events</strong></label>
                                <select name="mobile_event_detail_alignment">
                                    <option value="Left" <?php selected($content_layout['MobileEventDetailAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['MobileEventDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Indholdet på hver eventside.</p>
                            </div>
                        </div>
                    </fieldset>
                </div>
                <div class="h18-layout-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér kun for at kontrollere valgene uden at gemme eller ændre sider.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-secondary" type="submit">Gem layout og anvend</button>
                        <div class="h18-action-copy"><strong>Gemmer placeringerne</strong><span>Opdaterer eventoversigten og alle eksisterende eventsider.</span></div>
                    </div>
                </div>
            </form>

            <div class="h18-toolbar">
                <form method="get">
                    <input type="hidden" name="page" value="hangar18-events" />
                    <label><strong>Eksisterende event</strong></label>
                    <select name="event_id" onchange="this.form.submit()">
                        <option value="0">— Nyt event —</option>
                        <?php foreach ($this->get_event_pages(false) as $item) : ?>
                            <option value="<?php echo esc_attr($item->ID); ?>" <?php selected($id, $item->ID); ?>>
                                <?php echo esc_html($item->post_title . ' [' . $item->post_status . ']'); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <a class="button" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-events')); ?>">Nyt</a>
                    <?php if ($post) : ?><a class="button" target="_blank" href="<?php echo esc_url(get_permalink($post)); ?>">Åbn side</a><?php endif; ?>
                </form>
                <p class="h18-toolbar-note"><strong>Nyt</strong> åbner en tom eventformular. <strong>Åbn side</strong> viser det valgte event på hjemmesiden.</p>
            </div>

            <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_event'); ?>
                <input type="hidden" name="action" value="h18_save_event" />
                <input type="hidden" name="event_id" value="<?php echo esc_attr($id); ?>" />

                <div class="h18-form-header">
                    <h2><?php echo $post ? 'Redigér: ' . esc_html($post->post_title) : 'Nyt event'; ?></h2>
                    <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                </div>

                <div class="h18-form-grid">
                    <section class="h18-panel">
                        <h3>Eventdata</h3>
                        <?php
                        $this->field('event_name', 'Navn', $post ? $post->post_title : $this->value($data, 'EventName'), 'text', true);
                        $this->field('slug', 'Slug', $post ? $post->post_name : $this->value($data, 'Slug'));
                        $this->field('short_description', 'Kort beskrivelse', $this->value($data, 'ShortDescription'));
                        $this->field('event_date', 'Dato', $this->value($data, 'EventDate'), 'date', true);
                        $this->field('start_time', 'Starttid', $this->value($data, 'StartTime'), 'time');
                        $this->field('end_time', 'Sluttid', $this->value($data, 'EndTime'), 'time');
                        $this->field('venue', 'Sted', $this->value($data, 'Venue'));
                        $this->field('address', 'Adresse', $this->value($data, 'Address'));
                        $this->field('contact', 'Kontakt', $this->value($data, 'Contact'));

                        $this->select_field(
                            'gallery_album_page_id',
                            'Billedalbum',
                            absint($data['GalleryAlbumPageId'] ?? 0),
                            $this->gallery_album_choices(),
                            'Vælg et publiceret album. Eventet linker til albummet i stedet for at have et separat galleri.'
                        );

                        $this->select_field(
                            'status',
                            'Status',
                            $post ? $post->post_status : 'draft',
                            ['draft' => 'Draft', 'publish' => 'Publiceret']
                        );
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Hovedbillede</h3>
                        <?php $this->render_media_field($media_id, $media_url, 'main'); ?>
                    </section>

                    <section class="h18-panel h18-panel-wide"><?php $this->textarea('description', 'Om arrangementet', $this->value($data, 'Description'), 8); ?></section>
                    <section class="h18-panel h18-panel-wide"><?php $this->textarea('program', 'Program', $this->value($data, 'Program'), 8); ?></section>
                    <section class="h18-panel h18-panel-wide"><?php $this->textarea('practical', 'Praktiske oplysninger', $this->value($data, 'Practical'), 8); ?></section>
                </div>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Er simulering markeret, vises resultatet uden at noget bliver gemt.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary button-hero" type="submit">Gem / opdater event</button>
                        <div class="h18-action-copy"><strong>Gemmer hele eventet</strong><span>Gemmer data, billede, albumlink og status og opdaterer eventoversigten.</span></div>
                    </div>
                </div>
            </form>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_rebuild_event_register'); ?>
                <input type="hidden" name="action" value="h18_rebuild_event_register" />
                <div class="h18-whatif-help">
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér for at kontrollere handlingen uden at skrive ændringer.</span></div>
                </div>
                <div class="h18-action-submit">
                    <button class="button" type="submit">Genbyg eventoversigten</button>
                    <div class="h18-action-copy"><strong>Reparation</strong><span>Brug kun hvis kommende eller tidligere events mangler på oversigten. Eventdata ændres ikke.</span></div>
                </div>
            </form>
        </div>
        <?php
    }

    public function handle_save_event_layout() {
        $this->require_capability();
        check_admin_referer('h18_save_event_layout');

        $settings = $this->get_content_layout_settings();
        $index_alignment = $this->post_text('event_index_alignment');
        $detail_alignment = $this->post_text('event_detail_alignment');
        $mobile_index_alignment = $this->post_text('mobile_event_index_alignment');
        $mobile_detail_alignment = $this->post_text('mobile_event_detail_alignment');

        if (!in_array($index_alignment, ['Left', 'Center'], true)) {
            $index_alignment = 'Left';
        }
        if (!in_array($detail_alignment, ['Left', 'Center'], true)) {
            $detail_alignment = 'Left';
        }
        if (!in_array($mobile_index_alignment, ['Left', 'Center'], true)) {
            $mobile_index_alignment = 'Center';
        }
        if (!in_array($mobile_detail_alignment, ['Left', 'Center'], true)) {
            $mobile_detail_alignment = 'Center';
        }

        $settings['EventIndexAlignment'] = $index_alignment;
        $settings['EventDetailAlignment'] = $detail_alignment;
        $settings['MobileEventIndexAlignment'] = $mobile_index_alignment;
        $settings['MobileEventDetailAlignment'] = $mobile_detail_alignment;
        $settings = $this->normalize_content_layout_settings($settings);

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_EVENT_LAYOUT',
                "[WHATIF] EventIndexAlignment={$index_alignment}; EventDetailAlignment={$detail_alignment}; MobileEventIndexAlignment={$mobile_index_alignment}; MobileEventDetailAlignment={$mobile_detail_alignment}."
            );
            $this->set_notice(
                'warning',
                'WHATIF: Eventoversigt og eventdetaljesider ville få de valgte desktop- og mobilplaceringer. Ingen data blev ændret.'
            );
            $this->redirect('hangar18-events');
        }

        try {
            $this->create_full_managed_backup(
                "Før ændring af event-layout: desktop oversigt={$index_alignment}; desktop detaljer={$detail_alignment}; mobil oversigt={$mobile_index_alignment}; mobil detaljer={$mobile_detail_alignment}"
            );

            update_option(self::CONTENT_LAYOUT_OPTION, $settings, false);

            $published = $settings;
            $published['Saved'] = gmdate('c');
            $this->publish_configuration_file('Hangar18-ContentLayout.json', $published);

            $updated = 0;
            foreach ($this->get_event_pages(false) as $page) {
                $data = $this->decode_marker(self::EVENT_MARKER, $page->post_content);
                if (!$data) {
                    continue;
                }

                $result = wp_update_post(
                    [
                        'ID'           => $page->ID,
                        'post_content' => $this->wrap_with_shell(
                            $this->build_event_core($page->ID, $data),
                            $page->ID
                        ),
                    ],
                    true
                );

                if (is_wp_error($result)) {
                    throw new RuntimeException(
                        "Event ID {$page->ID}: " . $result->get_error_message()
                    );
                }
                $updated++;
            }

            $this->rebuild_event_register();

            $this->log(
                'INFO',
                'EVENT_LAYOUT_SAVED',
                "EventIndexAlignment={$index_alignment}; EventDetailAlignment={$detail_alignment}; MobileEventIndexAlignment={$mobile_index_alignment}; MobileEventDetailAlignment={$mobile_detail_alignment}; DetailPagesUpdated={$updated}."
            );

            $this->set_notice(
                'success',
                "Event-layout gemt: desktop oversigt={$index_alignment}, desktop detaljesider={$detail_alignment}, mobil oversigt={$mobile_index_alignment}, mobil detaljesider={$mobile_detail_alignment}. {$updated} events er opdateret."
            );
        } catch (Throwable $e) {
            $this->log('ERROR', 'EVENT_LAYOUT_FAILED', $e->getMessage());
            $this->set_notice('error', 'Event-layout kunne ikke gemmes: ' . $e->getMessage());
        }

        $this->redirect('hangar18-events');
    }

    public function handle_save_event() {
        $this->require_capability();
        check_admin_referer('h18_save_event');

        $id = absint($_POST['event_id'] ?? 0);
        $whatif = !empty($_POST['whatif']);
        $name = $this->post_text('event_name');
        $date = $this->post_text('event_date');

        if ($name === '' || $date === '') {
            $this->set_notice('error', 'Eventnavn og dato skal udfyldes.');
            $this->redirect('hangar18-events', $id ? ['event_id' => $id] : []);
        }

        $parent = $this->post_by_slug(self::EVENT_PARENT_SLUG);
        if (!$parent) {
            $this->set_notice('error', "Siden 'Events' findes ikke.");
            $this->redirect('hangar18-events');
        }

        $slug = sanitize_title($this->post_text('slug') ?: $name);
        $status = ($_POST['status'] ?? '') === 'publish' ? 'publish' : 'draft';
        $media_id = absint($_POST['main_media_id'] ?? 0);
        $media_url = $media_id ? wp_get_attachment_url($media_id) : $this->post_url('main_media_url');

        $album_id = absint($_POST['gallery_album_page_id'] ?? 0);
        $album = $album_id ? get_post($album_id) : null;
        $album_name = '';
        $album_url = '';

        if ($album) {
            $album_data = $this->decode_marker(self::GALLERY_MARKER, $album->post_content) ?: [];
            $album_name = $this->value($album_data, 'AlbumName', $album->post_title);
            $album_url = get_permalink($album);
        } else {
            $album_id = 0;
        }

        $ts = strtotime($date . ' 12:00:00');
        $display_date = $ts ? wp_date('d-m-Y', $ts) : $date;

        $data = [
            'DataVersion'       => '1.1',
            'EventName'         => $name,
            'Slug'              => $slug,
            'ShortDescription'  => $this->post_text('short_description'),
            'EventDate'         => $date,
            'DisplayDate'       => $display_date,
            'StartTime'         => $this->post_text('start_time'),
            'EndTime'           => $this->post_text('end_time'),
            'Venue'             => $this->post_text('venue'),
            'Address'           => $this->post_text('address'),
            'Contact'           => $this->post_text('contact'),
            'Description'       => $this->post_textarea('description'),
            'Program'           => $this->post_textarea('program'),
            'Practical'         => $this->post_textarea('practical'),
            'MainMediaId'       => $media_id,
            'MainMediaUrl'      => $media_url ?: '',
            'GalleryAlbumPageId'=> $album_id,
            'GalleryAlbumName'  => $album_name,
            'GalleryAlbumUrl'   => $album_url ?: '',
        ];

        if ($whatif) {
            $this->log('WARN', 'WHATIF_EVENT_SAVE', "[WHATIF] Ville gemme event '{$name}' {$date}.");
            $this->set_notice('warning', "WHATIF: Ville gemme event '{$name}'. Ingen data blev ændret.");
            $this->redirect('hangar18-events', $id ? ['event_id' => $id] : []);
        }

        try {
            $target = $id ? get_post($id) : null;

            if (!$target) {
                foreach ($this->get_event_pages(false) as $candidate) {
                    if ($candidate->post_name === $slug) {
                        $target = $candidate;
                        break;
                    }
                }
            }

            if ($target) {
                $this->backup_post($target->ID, "Før gem event '{$name}'");
                $id = (int) $target->ID;
            } else {
                $id = wp_insert_post([
                    'post_type'   => 'page',
                    'post_title'  => $name,
                    'post_name'   => $slug,
                    'post_status' => 'draft',
                    'post_parent' => (int) $parent->ID,
                ], true);

                if (is_wp_error($id)) {
                    throw new RuntimeException($id->get_error_message());
                }
            }

            $result = wp_update_post([
                'ID'           => $id,
                'post_title'   => $name,
                'post_name'    => $slug,
                'post_status'  => $status,
                'post_parent'  => (int) $parent->ID,
                'post_excerpt' => $data['ShortDescription'],
                'post_content' => $this->wrap_with_shell($this->build_event_core($id, $data), $id),
            ], true);

            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $media_id ? set_post_thumbnail($id, $media_id) : delete_post_thumbnail($id);

            $this->backup_post($parent->ID, "Før genbygning af eventregister efter '{$name}'");
            $this->rebuild_event_register();

            $this->log('INFO', 'EVENT_SAVE_SUCCESS', "Event gemt: '{$name}' ID {$id}.");
            $this->set_notice('success', "Eventet '{$name}' er gemt, og eventregisteret er genbygget.");
            $this->redirect('hangar18-events', ['event_id' => $id]);

        } catch (Throwable $e) {
            $this->log('ERROR', 'EVENT_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Kunne ikke gemme eventet: ' . $e->getMessage());
            $this->redirect('hangar18-events', $id ? ['event_id' => $id] : []);
        }
    }

    public function handle_rebuild_event_register() {
        $this->require_capability();
        check_admin_referer('h18_rebuild_event_register');

        if (!empty($_POST['whatif'])) {
            $this->log('WARN', 'WHATIF_EVENT_REGISTER', '[WHATIF] Genbygning simuleret.');
            $this->set_notice('warning', 'WHATIF: Eventregisteret ville blive genbygget. Ingen data blev ændret.');
            $this->redirect('hangar18-events');
        }

        try {
            $parent = $this->post_by_slug(self::EVENT_PARENT_SLUG);
            if ($parent) {
                $this->backup_post($parent->ID, 'Før manuel genbygning af eventregister');
            }
            $this->rebuild_event_register();
            $this->set_notice('success', 'Eventregisteret er genbygget.');
        } catch (Throwable $e) {
            $this->log('ERROR', 'EVENT_REGISTER_FAILED', $e->getMessage());
            $this->set_notice('error', $e->getMessage());
        }

        $this->redirect('hangar18-events');
    }

    /* ================================================================
       GALLERY
       ================================================================ */

    private function sanitize_gallery_items($json) {
        $decoded = json_decode((string) $json, true);
        if (!is_array($decoded)) {
            return [];
        }

        $items = [];
        $order = 1;

        foreach ($decoded as $item) {
            if (!is_array($item)) {
                continue;
            }

            $id = absint($item['MediaId'] ?? $item['id'] ?? 0);
            if (!$id) {
                continue;
            }

            $url = wp_get_attachment_url($id);
            if (!$url) {
                continue;
            }

            $title = sanitize_text_field((string) ($item['Title'] ?? $item['title'] ?? get_the_title($id)));

            $items[] = [
                'MediaId'     => $id,
                'Url'         => esc_url_raw($url),
                'Title'       => $title,
                'Description' => sanitize_textarea_field((string) ($item['Description'] ?? '')),
                'Order'       => $order++,
            ];
        }

        return $items;
    }

    private function build_gallery_album_core($page_id, array $data) {
        $id = (int) $page_id;
        $layout = $this->get_content_layout_settings();
        $alignment = $layout['GalleryDetailAlignment'] === 'Center' ? 'center' : 'left';
        $justify = $layout['GalleryDetailAlignment'] === 'Center' ? 'center' : 'start';
        $grid_margin = $alignment === 'center' ? '36px auto' : '36px 0';
        $grid_class = $alignment === 'center' ? 'h18-align-center' : 'h18-align-left';
        $mobile_alignment = $layout['MobileGalleryDetailAlignment'] === 'Center' ? 'center' : 'left';
        $mobile_justify = $layout['MobileGalleryDetailAlignment'] === 'Center' ? 'center' : 'start';
        $mobile_grid_margin = $mobile_alignment === 'center' ? '36px auto' : '36px 0';

        $name = $this->h($this->value($data, 'AlbumName'));
        $type = $this->h($this->value($data, 'AlbumType'));
        $description = $this->hm($this->value($data, 'Description'));

        $images = '';
        foreach (($data['Items'] ?? []) as $item) {
            $media_id = absint($item['MediaId'] ?? 0);
            if (!$media_id) {
                continue;
            }

            $url = wp_get_attachment_image_url($media_id, 'large');
            if (!$url) {
                continue;
            }

            $title = esc_attr((string) ($item['Title'] ?? ''));
            $images .= '<figure class="h18-gallery-item"><a href="' . esc_url(wp_get_attachment_url($media_id)) . '">' .
                '<img src="' . esc_url($url) . '" alt="' . $title . '" loading="lazy" /></a>' .
                (($item['Title'] ?? '') !== '' ? '<figcaption>' . esc_html($item['Title']) . '</figcaption>' : '') .
                '</figure>';
        }

        if ($images === '') {
            $images = '<p>Der er endnu ingen billeder i dette album.</p>';
        }

        $marker = $this->encode_marker(self::GALLERY_MARKER, $data);

        return <<<HTML
{$marker}
<!-- wp:html -->
<style>
body.page-id-{$id} .entry-title,body.page-id-{$id} .wp-block-post-title{display:none}
body.page-id-{$id} .h18-gallery-hero{padding:46px 20px;background:#30382a;color:#f2f0e8;text-align:{$alignment}}
body.page-id-{$id} .h18-gallery-hero h1,body.page-id-{$id} .h18-gallery-hero p{color:#f2f0e8}
body.page-id-{$id} .h18-gallery-grid{width:min(1200px,100%);max-width:1200px;margin:{$grid_margin}!important;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,360px));gap:16px;padding:0;justify-content:{$justify}!important;box-sizing:border-box} body.page-id-{$id} .h18-gallery-grid.h18-align-left{margin-left:0!important;margin-right:auto!important;justify-content:start!important} body.page-id-{$id} .h18-gallery-grid.h18-align-center{margin-left:auto!important;margin-right:auto!important;justify-content:center!important}
body.page-id-{$id} .h18-gallery-item{margin:0;background:#f2f0e8;border-radius:7px;overflow:hidden}
body.page-id-{$id} .h18-gallery-item img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}
body.page-id-{$id} .h18-gallery-item figcaption{padding:8px 10px;text-align:{$alignment}}
@media (max-width:782px){body.page-id-{$id} .h18-gallery-hero,body.page-id-{$id} .h18-gallery-item figcaption,body.page-id-{$id} .h18-gallery-grid>p{text-align:{$mobile_alignment}!important}body.page-id-{$id} .h18-gallery-grid,body.page-id-{$id} .h18-gallery-grid.h18-align-left,body.page-id-{$id} .h18-gallery-grid.h18-align-center{margin:{$mobile_grid_margin}!important;justify-content:{$mobile_justify}!important}}
</style>
<!-- /wp:html -->
<div class="h18-gallery-hero"><h1>{$name}</h1><p>{$type}</p><p>{$description}</p></div>
<div class="h18-gallery-grid {$grid_class}">{$images}</div>
HTML;
    }

    private function rebuild_gallery_index() {
        $parent = $this->post_by_slug(self::GALLERY_PARENT_SLUG);
        if (!$parent) {
            throw new RuntimeException("Siden 'Billedgalleri' blev ikke fundet.");
        }

        $layout = $this->get_content_layout_settings();
        $alignment = $layout['GalleryIndexAlignment'] === 'Center' ? 'center' : 'left';
        $justify = $layout['GalleryIndexAlignment'] === 'Center' ? 'center' : 'start';
        $mobile_alignment = $layout['MobileGalleryIndexAlignment'] === 'Center' ? 'center' : 'left';
        $mobile_justify = $layout['MobileGalleryIndexAlignment'] === 'Center' ? 'center' : 'start';
        $parent_id = (int) $parent->ID;

        $groups = [
            'Køretøj'     => [],
            'Event'       => [],
            'Restaurering'=> [],
            'Foreningen'  => [],
            'Andet'       => [],
        ];

        foreach ($this->get_gallery_pages(true) as $page) {
            $data = $this->decode_marker(self::GALLERY_MARKER, $page->post_content);
            if (!$data) {
                continue;
            }

            $type = $this->value($data, 'AlbumType', 'Andet');
            if (!isset($groups[$type])) {
                $type = 'Andet';
            }

            $groups[$type][] = ['page' => $page, 'data' => $data];
        }

        $titles = [
            'Køretøj'      => 'Køretøjer',
            'Event'        => 'Events',
            'Restaurering' => 'Restaurering',
            'Foreningen'   => 'Foreningen',
            'Andet'        => 'Andet',
        ];

        $html = '<!-- wp:html --><style>.h18-overview-heading h1{margin:0 0 28px;font-size:clamp(2rem,4vw,3.2rem);line-height:1.08;color:#30382a}.h18-gallery-index{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,360px));gap:18px;margin:18px 0 32px;justify-content:' . $justify . '}.h18-album-card{background:#f2f0e8;border-radius:8px;overflow:hidden;border:1px solid rgba(48,56,42,.14)}.h18-album-card a{display:block;color:#30382a;text-decoration:none}.h18-album-card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block}.h18-album-card-body{padding:18px;text-align:' . $alignment . '}.h18-album-card h3{margin:0 0 8px}.h18-album-placeholder{aspect-ratio:16/10;background:#525a5f;color:#f2f0e8;display:flex;align-items:center;justify-content:center}';
        $html .= '@media (max-width:782px){body.page-id-' . $parent_id . ' .h18-overview-heading,body.page-id-' . $parent_id . ' .h18-gallery-group-heading,body.page-id-' . $parent_id . ' .h18-album-card-body{text-align:' . $mobile_alignment . '!important}body.page-id-' . $parent_id . ' .h18-gallery-index{justify-content:' . $mobile_justify . '!important}}</style>';

        $html .= '<div class="h18-overview-heading" style="text-align:' . esc_attr($alignment) . '"><h1>Billedgalleri</h1></div>';

        foreach ($groups as $type => $items) {
            if (!$items) {
                continue;
            }

            $html .= '<h2 class="h18-gallery-group-heading" style="text-align:' . esc_attr($alignment) . '">' . esc_html($titles[$type]) . '</h2><div class="h18-gallery-index">';

            foreach ($items as $item) {
                $page = $item['page'];
                $data = $item['data'];
                $items_data = is_array($data['Items'] ?? null) ? $data['Items'] : [];
                $count = count($items_data);

                $cover = '<div class="h18-album-placeholder">Album</div>';
                $featured = get_post_thumbnail_id($page->ID);

                if (!$featured && $count > 0) {
                    $featured = absint($items_data[0]['MediaId'] ?? 0);
                }

                if ($featured) {
                    $src = wp_get_attachment_image_url($featured, 'large');
                    if ($src) {
                        $cover = '<img src="' . esc_url($src) . '" alt="' . esc_attr($page->post_title) . '" loading="lazy" />';
                    }
                }

                $html .= '<article class="h18-album-card"><a href="' . esc_url(get_permalink($page)) . '">' .
                    $cover .
                    '<div class="h18-album-card-body"><h3>' . esc_html($data['AlbumName'] ?? $page->post_title) . '</h3>' .
                    '<p>' . esc_html($data['Description'] ?? '') . '</p>' .
                    '<strong>' . esc_html($count) . ' billeder</strong></div></a></article>';
            }

            $html .= '</div>';
        }

        $html .= '<!-- /wp:html -->';

        $result = wp_update_post([
            'ID' => $parent->ID,
            'page_template' => 'default',
            'post_content' => $this->wrap_with_shell($html, $parent->ID),
        ], true);

        if (is_wp_error($result)) {
            throw new RuntimeException($result->get_error_message());
        }

        $this->log('INFO', 'GALLERY_INDEX_UPDATED', 'Billedgalleri-indekset blev genbygget.');
    }

    public function render_gallery() {
        $this->require_capability();

        $id = isset($_GET['album_id']) ? absint($_GET['album_id']) : 0;
        $post = $id ? get_post($id) : null;
        $data = $post ? ($this->decode_marker(self::GALLERY_MARKER, $post->post_content) ?: []) : [];

        $items = is_array($data['Items'] ?? null) ? $data['Items'] : [];
        $items_json = wp_json_encode($items, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $content_layout = $this->get_content_layout_settings();

        ?>
        <div class="wrap h18-admin">
            <h1>Billedgalleri</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan styres Billedgalleri:</strong>
                Opret et album, vælg typen, klik <strong>Tilføj billeder</strong>, vælg flere billeder fra WordPress Media Library,
                og træk derefter billederne med musen for at ændre rækkefølgen.
                Events kan bagefter linke til publicerede albums af typen Event.
            </div>

            <form class="h18-layout-card" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_gallery_layout'); ?>
                <input type="hidden" name="action" value="h18_save_gallery_layout" />
                <div class="h18-layout-card-header">
                    <h2>Placering af billedgalleri</h2>
                    <p>Vælg placeringen særskilt for albumoversigten og billederne i de enkelte albums.</p>
                </div>
                <div class="h18-layout-devices">
                    <fieldset class="h18-layout-device">
                        <legend>Desktop</legend>
                        <div class="h18-layout-fields">
                            <div class="h18-field">
                                <label><strong>Albumoversigten</strong></label>
                                <select name="gallery_index_alignment">
                                    <option value="Left" <?php selected($content_layout['GalleryIndexAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['GalleryIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Overskrifter og albumkort.</p>
                            </div>
                            <div class="h18-field">
                                <label><strong>De enkelte albums</strong></label>
                                <select name="gallery_detail_alignment">
                                    <option value="Left" <?php selected($content_layout['GalleryDetailAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['GalleryDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Albumtekst, billeder og billedtekster.</p>
                            </div>
                        </div>
                    </fieldset>
                    <fieldset class="h18-layout-device">
                        <legend>Mobil</legend>
                        <div class="h18-layout-fields">
                            <div class="h18-field">
                                <label><strong>Albumoversigten</strong></label>
                                <select name="mobile_gallery_index_alignment">
                                    <option value="Left" <?php selected($content_layout['MobileGalleryIndexAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['MobileGalleryIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Overskrifter og albumkort.</p>
                            </div>
                            <div class="h18-field">
                                <label><strong>De enkelte albums</strong></label>
                                <select name="mobile_gallery_detail_alignment">
                                    <option value="Left" <?php selected($content_layout['MobileGalleryDetailAlignment'], 'Left'); ?>>Venstre</option>
                                    <option value="Center" <?php selected($content_layout['MobileGalleryDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                                </select>
                                <p class="description">Albumtekst, billeder og billedtekster.</p>
                            </div>
                        </div>
                    </fieldset>
                </div>
                <div class="h18-layout-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér kun for at kontrollere valgene uden at gemme eller ændre sider.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-secondary" type="submit">Gem layout og anvend</button>
                        <div class="h18-action-copy"><strong>Gemmer placeringerne</strong><span>Opdaterer albumoversigten og alle eksisterende albumsider.</span></div>
                    </div>
                </div>
            </form>

            <div class="h18-toolbar">
                <form method="get">
                    <input type="hidden" name="page" value="hangar18-gallery" />
                    <label><strong>Eksisterende album</strong></label>
                    <select name="album_id" onchange="this.form.submit()">
                        <option value="0">— Nyt album —</option>
                        <?php foreach ($this->get_gallery_pages(false) as $item) : ?>
                            <option value="<?php echo esc_attr($item->ID); ?>" <?php selected($id, $item->ID); ?>>
                                <?php echo esc_html($item->post_title . ' [' . $item->post_status . ']'); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <a class="button" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-gallery')); ?>">Nyt</a>
                    <?php if ($post) : ?><a class="button" target="_blank" href="<?php echo esc_url(get_permalink($post)); ?>">Åbn album</a><?php endif; ?>
                </form>
                <p class="h18-toolbar-note"><strong>Nyt</strong> åbner en tom albumformular. <strong>Åbn album</strong> viser det valgte album på hjemmesiden.</p>
            </div>

            <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_gallery_album'); ?>
                <input type="hidden" name="action" value="h18_save_gallery_album" />
                <input type="hidden" name="album_id" value="<?php echo esc_attr($id); ?>" />
                <input id="h18-gallery-items-json" type="hidden" name="gallery_items_json" value="<?php echo esc_attr($items_json); ?>" />

                <div class="h18-form-header">
                    <h2><?php echo $post ? 'Redigér album: ' . esc_html($post->post_title) : 'Nyt album'; ?></h2>
                    <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                </div>

                <div class="h18-form-grid">
                    <section class="h18-panel">
                        <h3>Albumdata</h3>
                        <?php
                        $this->field('album_name', 'Album-navn', $post ? $post->post_title : $this->value($data, 'AlbumName'), 'text', true);
                        $this->field('slug', 'Slug', $post ? $post->post_name : $this->value($data, 'Slug'));
                        $this->select_field(
                            'album_type',
                            'Albumtype',
                            $this->value($data, 'AlbumType', 'Andet'),
                            [
                                'Køretøj' => 'Køretøj',
                                'Event' => 'Event',
                                'Restaurering' => 'Restaurering',
                                'Foreningen' => 'Foreningen',
                                'Andet' => 'Andet',
                            ]
                        );
                        $this->textarea('description', 'Beskrivelse', $this->value($data, 'Description'), 6);
                        $this->select_field(
                            'status',
                            'Status',
                            $post ? $post->post_status : 'draft',
                            ['draft' => 'Draft', 'publish' => 'Publiceret']
                        );
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Albumstyring</h3>
                        <p>Antal billeder: <strong id="h18-gallery-count"><?php echo esc_html(count($items)); ?></strong></p>
                        <button id="h18-gallery-add" type="button" class="button button-secondary">Tilføj billeder</button>
                        <p class="description">Du kan vælge flere billeder på én gang.</p>
                    </section>

                    <section class="h18-panel h18-panel-wide">
                        <h3>Billeder – træk for at ændre rækkefølge</h3>
                        <div id="h18-gallery-sortable" class="h18-gallery-sortable">
                            <?php foreach ($items as $item) :
                                $mid = absint($item['MediaId'] ?? 0);
                                $thumb = $mid ? wp_get_attachment_image_url($mid, 'thumbnail') : '';
                                if (!$thumb) {
                                    continue;
                                }
                            ?>
                                <div class="h18-gallery-admin-item"
                                     data-id="<?php echo esc_attr($mid); ?>"
                                     data-url="<?php echo esc_attr(wp_get_attachment_url($mid)); ?>"
                                     data-title="<?php echo esc_attr($item['Title'] ?? get_the_title($mid)); ?>">
                                    <span class="dashicons dashicons-move h18-drag-handle"></span>
                                    <img src="<?php echo esc_url($thumb); ?>" alt="" />
                                    <div class="h18-gallery-admin-title"><?php echo esc_html($item['Title'] ?? get_the_title($mid)); ?></div>
                                    <button type="button" class="button-link-delete h18-gallery-remove">Fjern</button>
                                </div>
                            <?php endforeach; ?>
                        </div>
                        <div id="h18-gallery-empty" class="h18-gallery-empty" <?php echo count($items) ? 'style="display:none"' : ''; ?>>Albummet har ingen billeder endnu.</div>
                    </section>
                </div>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Er simulering markeret, vises resultatet uden at noget bliver gemt.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary button-hero" type="submit">Gem / opdater album</button>
                        <div class="h18-action-copy"><strong>Gemmer hele albummet</strong><span>Gemmer albumdata, billedrækkefølge og status og opdaterer gallerioversigten.</span></div>
                    </div>
                </div>
            </form>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_rebuild_gallery_index'); ?>
                <input type="hidden" name="action" value="h18_rebuild_gallery_index" />
                <div class="h18-whatif-help">
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér for at kontrollere handlingen uden at skrive ændringer.</span></div>
                </div>
                <div class="h18-action-submit">
                    <button class="button" type="submit">Genbyg gallerioversigten</button>
                    <div class="h18-action-copy"><strong>Reparation</strong><span>Brug kun hvis albumkort mangler eller står forkert. Albumdata og billeder ændres ikke.</span></div>
                </div>
            </form>
        </div>
        <?php
    }

    public function handle_save_gallery_layout() {
        $this->require_capability();
        check_admin_referer('h18_save_gallery_layout');

        $settings = $this->get_content_layout_settings();
        $index_alignment = $this->post_text('gallery_index_alignment');
        $detail_alignment = $this->post_text('gallery_detail_alignment');
        $mobile_index_alignment = $this->post_text('mobile_gallery_index_alignment');
        $mobile_detail_alignment = $this->post_text('mobile_gallery_detail_alignment');

        if (!in_array($index_alignment, ['Left', 'Center'], true)) {
            $index_alignment = 'Left';
        }
        if (!in_array($detail_alignment, ['Left', 'Center'], true)) {
            $detail_alignment = 'Left';
        }
        if (!in_array($mobile_index_alignment, ['Left', 'Center'], true)) {
            $mobile_index_alignment = 'Center';
        }
        if (!in_array($mobile_detail_alignment, ['Left', 'Center'], true)) {
            $mobile_detail_alignment = 'Center';
        }

        $settings['GalleryIndexAlignment'] = $index_alignment;
        $settings['GalleryDetailAlignment'] = $detail_alignment;
        $settings['MobileGalleryIndexAlignment'] = $mobile_index_alignment;
        $settings['MobileGalleryDetailAlignment'] = $mobile_detail_alignment;
        $settings = $this->normalize_content_layout_settings($settings);

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_GALLERY_LAYOUT',
                "[WHATIF] GalleryIndexAlignment={$index_alignment}; GalleryDetailAlignment={$detail_alignment}; MobileGalleryIndexAlignment={$mobile_index_alignment}; MobileGalleryDetailAlignment={$mobile_detail_alignment}."
            );
            $this->set_notice(
                'warning',
                'WHATIF: Gallerioversigt og albumsider ville få de valgte desktop- og mobilplaceringer. Ingen data blev ændret.'
            );
            $this->redirect('hangar18-gallery');
        }

        try {
            $this->create_full_managed_backup(
                "Før ændring af galleri-layout: desktop oversigt={$index_alignment}; desktop detaljer={$detail_alignment}; mobil oversigt={$mobile_index_alignment}; mobil detaljer={$mobile_detail_alignment}"
            );

            update_option(self::CONTENT_LAYOUT_OPTION, $settings, false);

            $published = $settings;
            $published['Saved'] = gmdate('c');
            $this->publish_configuration_file('Hangar18-ContentLayout.json', $published);

            $updated = 0;
            foreach ($this->get_gallery_pages(false) as $page) {
                $data = $this->decode_marker(self::GALLERY_MARKER, $page->post_content);
                if (!$data) {
                    continue;
                }

                $result = wp_update_post(
                    [
                        'ID'           => $page->ID,
                        'page_template'=> 'default',
                        'post_content' => $this->wrap_with_shell(
                            $this->build_gallery_album_core($page->ID, $data),
                            $page->ID
                        ),
                    ],
                    true
                );

                if (is_wp_error($result)) {
                    throw new RuntimeException(
                        "Gallerialbum ID {$page->ID}: " . $result->get_error_message()
                    );
                }
                $updated++;
            }

            $this->rebuild_gallery_index();

            $this->log(
                'INFO',
                'GALLERY_LAYOUT_SAVED',
                "GalleryIndexAlignment={$index_alignment}; GalleryDetailAlignment={$detail_alignment}; MobileGalleryIndexAlignment={$mobile_index_alignment}; MobileGalleryDetailAlignment={$mobile_detail_alignment}; DetailPagesUpdated={$updated}."
            );

            $this->set_notice(
                'success',
                "Galleri-layout gemt: desktop oversigt={$index_alignment}, desktop albumsider={$detail_alignment}, mobil oversigt={$mobile_index_alignment}, mobil albumsider={$mobile_detail_alignment}. {$updated} albumsider er opdateret."
            );
        } catch (Throwable $e) {
            $this->log('ERROR', 'GALLERY_LAYOUT_FAILED', $e->getMessage());
            $this->set_notice('error', 'Galleri-layout kunne ikke gemmes: ' . $e->getMessage());
        }

        $this->redirect('hangar18-gallery');
    }

    public function handle_save_gallery_album() {
        $this->require_capability();
        check_admin_referer('h18_save_gallery_album');

        $id = absint($_POST['album_id'] ?? 0);
        $whatif = !empty($_POST['whatif']);
        $name = $this->post_text('album_name');

        if ($name === '') {
            $this->set_notice('error', 'Album-navn skal udfyldes.');
            $this->redirect('hangar18-gallery', $id ? ['album_id' => $id] : []);
        }

        $parent = $this->post_by_slug(self::GALLERY_PARENT_SLUG);
        if (!$parent) {
            $this->set_notice('error', "Siden 'Billedgalleri' findes ikke.");
            $this->redirect('hangar18-gallery');
        }

        $slug = sanitize_title($this->post_text('slug') ?: $name);
        $status = ($_POST['status'] ?? '') === 'publish' ? 'publish' : 'draft';
        $type = $this->post_text('album_type');
        $allowed_types = ['Køretøj', 'Event', 'Restaurering', 'Foreningen', 'Andet'];
        if (!in_array($type, $allowed_types, true)) {
            $type = 'Andet';
        }

        $items = $this->sanitize_gallery_items(wp_unslash($_POST['gallery_items_json'] ?? '[]'));

        $data = [
            'DataVersion' => '1.1',
            'AlbumName'   => $name,
            'Slug'        => $slug,
            'AlbumType'   => $type,
            'Description' => $this->post_textarea('description'),
            'Items'       => $items,
        ];

        if ($whatif) {
            $this->log('WARN', 'WHATIF_GALLERY_SAVE', "[WHATIF] Ville gemme album '{$name}' med " . count($items) . ' billeder.');
            $this->set_notice('warning', "WHATIF: Ville gemme album '{$name}' med " . count($items) . ' billeder. Ingen data blev ændret.');
            $this->redirect('hangar18-gallery', $id ? ['album_id' => $id] : []);
        }

        try {
            $target = $id ? get_post($id) : null;

            if (!$target) {
                foreach ($this->get_gallery_pages(false) as $candidate) {
                    if ($candidate->post_name === $slug) {
                        $target = $candidate;
                        break;
                    }
                }
            }

            if ($target) {
                $this->backup_post($target->ID, "Før gem gallerialbum '{$name}'");
                $id = (int) $target->ID;
            } else {
                $id = wp_insert_post([
                    'post_type'   => 'page',
                    'post_title'  => $name,
                    'post_name'   => $slug,
                    'post_status' => 'draft',
                    'post_parent' => (int) $parent->ID,
                    'page_template' => 'default',
                ], true);

                if (is_wp_error($id)) {
                    throw new RuntimeException($id->get_error_message());
                }
            }

            $result = wp_update_post([
                'ID'           => $id,
                'page_template'=> 'default',
                'post_title'   => $name,
                'post_name'    => $slug,
                'post_status'  => $status,
                'post_parent'  => (int) $parent->ID,
                'post_content' => $this->wrap_with_shell($this->build_gallery_album_core($id, $data), $id),
            ], true);

            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            if ($items) {
                set_post_thumbnail($id, absint($items[0]['MediaId']));
            } else {
                delete_post_thumbnail($id);
            }

            $this->backup_post($parent->ID, "Før genbygning af Billedgalleri efter '{$name}'");
            $this->rebuild_gallery_index();

            $this->log('INFO', 'GALLERY_SAVE_SUCCESS', "Gallerialbum gemt: '{$name}' ID {$id}, billeder: " . count($items));
            $this->set_notice('success', "Albummet '{$name}' er gemt, og Billedgalleri-indekset er genbygget.");
            $this->redirect('hangar18-gallery', ['album_id' => $id]);

        } catch (Throwable $e) {
            $this->log('ERROR', 'GALLERY_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Kunne ikke gemme albummet: ' . $e->getMessage());
            $this->redirect('hangar18-gallery', $id ? ['album_id' => $id] : []);
        }
    }

    public function handle_rebuild_gallery_index() {
        $this->require_capability();
        check_admin_referer('h18_rebuild_gallery_index');

        if (!empty($_POST['whatif'])) {
            $this->log('WARN', 'WHATIF_GALLERY_INDEX', '[WHATIF] Genbygning simuleret.');
            $this->set_notice('warning', 'WHATIF: Billedgalleri-indekset ville blive genbygget. Ingen data blev ændret.');
            $this->redirect('hangar18-gallery');
        }

        try {
            $parent = $this->post_by_slug(self::GALLERY_PARENT_SLUG);
            if ($parent) {
                $this->backup_post($parent->ID, 'Før manuel genbygning af Billedgalleri');
            }
            $this->rebuild_gallery_index();
            $this->set_notice('success', 'Billedgalleri-indekset er genbygget.');
        } catch (Throwable $e) {
            $this->log('ERROR', 'GALLERY_INDEX_FAILED', $e->getMessage());
            $this->set_notice('error', $e->getMessage());
        }

        $this->redirect('hangar18-gallery');
    }




    /* ================================================================
       GENERIC DYNAMIC DATA ENGINE — v0.5.23 / E5 UD-051 + UD-052
       ================================================================ */

    public function register_dynamic_data_post_type() {
        register_post_type(self::DATA_ENTRY_POST_TYPE, [
            'labels' => ['name' => 'Hangar18 data', 'singular_name' => 'Hangar18 data-entry'],
            'public' => false,
            'show_ui' => false,
            'show_in_menu' => false,
            'show_in_rest' => false,
            'rewrite' => false,
            'query_var' => false,
            'supports' => ['title'],
            'capability_type' => 'page',
            'map_meta_cap' => true,
        ]);
        register_taxonomy(self::DATA_TAG_TAXONOMY, [self::DATA_ENTRY_POST_TYPE], [
            'labels' => ['name'=>'Data Tags','singular_name'=>'Data Tag'],
            'public' => false,
            'show_ui' => false,
            'show_in_rest' => false,
            'hierarchical' => false,
            'rewrite' => false,
            'query_var' => false,
        ]);
    }

    private function custom_data_field_types() {
        return [
            'text' => 'Tekst',
            'number' => 'Tal',
            'bool' => 'Ja/nej',
            'date' => 'Dato',
            'media' => 'Medie / billede',
            'relation' => 'Relation',
            'group' => 'Gruppe',
            'repeater' => 'Repeater',
        ];
    }

    private function custom_data_nested_field_types() {
        return [
            'text' => 'Tekst',
            'number' => 'Tal',
            'bool' => 'Ja/nej',
            'date' => 'Dato',
            'media' => 'Medie / billede',
        ];
    }

    private function normalize_custom_data_nested_fields($raw) {
        if (is_string($raw)) {
            $lines = preg_split('/\r\n|\r|\n/', $raw);
            $parsed = [];
            foreach ((array) $lines as $line) {
                $line = trim((string) $line); if ($line === '') { continue; }
                $parts = array_map('trim', explode('|', $line));
                $parsed[] = [
                    'Key' => $parts[0] ?? '',
                    'Label' => $parts[1] ?? ($parts[0] ?? ''),
                    'Type' => $parts[2] ?? 'text',
                    'Required' => in_array(strtolower((string) ($parts[3] ?? '')), ['1','true','yes','ja','required'], true),
                ];
            }
            $raw = $parsed;
        }
        if (!is_array($raw)) { return []; }
        $allowed = $this->custom_data_nested_field_types();
        $fields = []; $used = [];
        foreach (array_slice(array_values($raw), 0, 12) as $item) {
            if (!is_array($item)) { continue; }
            $key = sanitize_key((string) ($item['Key'] ?? ''));
            $label = sanitize_text_field((string) ($item['Label'] ?? ''));
            $type = sanitize_key((string) ($item['Type'] ?? 'text'));
            if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{0,47}$/', $key)) { throw new RuntimeException('Underfelter skal have en gyldig nøgle på højst 48 tegn.'); }
            if (isset($used[$key])) { throw new RuntimeException("Underfelt-nøglen '{$key}' findes mere end én gang."); }
            if ($label === '') { throw new RuntimeException("Underfeltet '{$key}' mangler et navn."); }
            if (!isset($allowed[$type])) { throw new RuntimeException("Underfeltet '{$key}' bruger en ikke-tilladt nested felttype."); }
            $used[$key] = true;
            $fields[] = ['Key'=>$key,'Label'=>$label,'Type'=>$type,'Required'=>!empty($item['Required']),'Order'=>count($fields)+1];
        }
        return $fields;
    }

    private function custom_data_nested_schema_text(array $fields) {
        $lines = [];
        foreach ($fields as $field) {
            $lines[] = (string) $field['Key'] . '|' . (string) $field['Label'] . '|' . (string) $field['Type'] . '|' . (!empty($field['Required']) ? 'required' : '');
        }
        return implode("\n", $lines);
    }

    private function normalize_custom_data_type(array $raw, $existing_key = '') {
        $key = sanitize_key((string) ($raw['Key'] ?? ''));
        $existing_key = sanitize_key((string) $existing_key);
        if ($existing_key !== '' && $key !== $existing_key) {
            throw new RuntimeException('Datatype-nøglen er permanent og kan ikke ændres efter oprettelse.');
        }
        if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{1,47}$/', $key)) {
            throw new RuntimeException('Datatype-nøglen skal være 2–48 tegn og kun bruge a-z, 0-9, bindestreg eller underscore.');
        }
        $singular = sanitize_text_field((string) ($raw['SingularLabel'] ?? ''));
        $plural = sanitize_text_field((string) ($raw['PluralLabel'] ?? ''));
        if ($singular === '') { throw new RuntimeException('Datatype skal have et navn i ental.'); }
        if ($plural === '') { $plural = $singular; }

        $allowed = $this->custom_data_field_types();
        $fields = [];
        $used = [];
        $raw_fields = isset($raw['Fields']) && is_array($raw['Fields']) ? array_slice($raw['Fields'], 0, 30) : [];
        foreach ($raw_fields as $field) {
            if (!is_array($field) || !empty($field['Remove'])) { continue; }
            $field_key = sanitize_key((string) ($field['Key'] ?? ''));
            $label = sanitize_text_field((string) ($field['Label'] ?? ''));
            $type = sanitize_key((string) ($field['Type'] ?? 'text'));
            if ($field_key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{0,47}$/', $field_key)) {
                throw new RuntimeException('Alle datafelter skal have en gyldig nøgle på højst 48 tegn.');
            }
            if (isset($used[$field_key])) { throw new RuntimeException("Felt-nøglen '{$field_key}' findes mere end én gang."); }
            if ($label === '') { throw new RuntimeException("Feltet '{$field_key}' mangler et navn."); }
            if (!isset($allowed[$type])) { throw new RuntimeException("Feltet '{$field_key}' har en ukendt felttype."); }
            $used[$field_key] = true;
            $relation_target = $type === 'relation' ? sanitize_key((string) ($field['RelationTargetType'] ?? '')) : '';
            if ($type === 'relation' && $relation_target === '') { throw new RuntimeException("Relationsfeltet '{$field_key}' skal vælge en mål-datatype."); }
            $nested_raw = $field['NestedFields'] ?? ($field['NestedSchemaText'] ?? []);
            $nested_fields = in_array($type, ['group','repeater'], true) ? $this->normalize_custom_data_nested_fields($nested_raw) : [];
            if (in_array($type, ['group','repeater'], true) && !$nested_fields) { throw new RuntimeException("Feltet '{$field_key}' skal have mindst ét underfelt."); }
            $fields[] = [
                'Key' => $field_key,
                'Label' => $label,
                'Type' => $type,
                'Required' => !empty($field['Required']),
                'RelationTargetType' => $relation_target,
                'NestedFields' => $nested_fields,
                'RepeaterMaxItems' => $type === 'repeater' ? $this->clamp_int($field['RepeaterMaxItems'] ?? 10, 1, 20, 10) : 0,
                'Order' => count($fields) + 1,
            ];
        }
        if (!$fields) { throw new RuntimeException('Datatype skal have mindst ét datafelt.'); }
        return [
            'Key' => $key,
            'SingularLabel' => $singular,
            'PluralLabel' => $plural,
            'Fields' => $fields,
            'SchemaVersion' => 2,
        ];
    }

    private function get_custom_data_types() {
        $stored = get_option(self::CUSTOM_DATA_TYPES_OPTION, []);
        if (!is_array($stored)) { return []; }
        $types = [];
        foreach (array_slice($stored, 0, 50, true) as $id => $raw) {
            if (!is_array($raw)) { continue; }
            $raw['Key'] = $raw['Key'] ?? $id;
            try { $type = $this->normalize_custom_data_type($raw, (string) ($raw['Key'] ?? $id)); }
            catch (Throwable $e) { $this->log('WARN', 'CUSTOM_DATA_TYPE_INVALID', (string) $e->getMessage()); continue; }
            $type['CreatedUtc'] = sanitize_text_field((string) ($raw['CreatedUtc'] ?? ''));
            $type['UpdatedUtc'] = sanitize_text_field((string) ($raw['UpdatedUtc'] ?? ''));
            $types[$type['Key']] = $type;
        }
        ksort($types, SORT_NATURAL | SORT_FLAG_CASE);
        return $types;
    }



    private function custom_data_relation_schema_usage($target_key) {
        $target_key = sanitize_key((string) $target_key);
        if ($target_key === '') { return []; }
        $usage = [];
        foreach ($this->get_custom_data_types() as $type_key => $type) {
            foreach ((array) ($type['Fields'] ?? []) as $field) {
                if (($field['Type'] ?? '') !== 'relation' || sanitize_key((string) ($field['RelationTargetType'] ?? '')) !== $target_key) { continue; }
                $usage[] = ['TypeKey'=>$type_key,'TypeLabel'=>(string)$type['SingularLabel'],'FieldKey'=>(string)$field['Key'],'FieldLabel'=>(string)$field['Label']];
            }
        }
        return $usage;
    }


    private function custom_data_entry_query($type_key, $limit = 100) {
        return get_posts([
            'post_type' => self::DATA_ENTRY_POST_TYPE,
            'post_status' => ['publish','draft','private'],
            'posts_per_page' => max(1, min(200, (int) $limit)),
            'meta_key' => '_h18_data_type',
            'meta_value' => sanitize_key((string) $type_key),
            'orderby' => 'modified',
            'order' => 'DESC',
        ]);
    }

    private function custom_data_entry_count($type_key) {
        return count($this->custom_data_entry_query($type_key, 200));
    }

    private function custom_data_entry_for_type($entry_id, $type_key) {
        $post = get_post((int) $entry_id);
        if (!$post instanceof WP_Post || $post->post_type !== self::DATA_ENTRY_POST_TYPE) { return null; }
        if (sanitize_key((string) get_post_meta($post->ID, '_h18_data_type', true)) !== sanitize_key((string) $type_key)) { return null; }
        return $post;
    }

    private function custom_data_entry_values($entry_id, array $schema) {
        $stored = get_post_meta((int) $entry_id, '_h18_data_values', true);
        $stored = is_array($stored) ? $stored : [];
        $values = [];
        foreach ($schema['Fields'] as $field) {
            $key = (string) $field['Key'];
            if (array_key_exists($key, $stored)) { $values[$key] = $stored[$key]; continue; }
            $meta = get_post_meta((int) $entry_id, '_h18_field_' . $key, true);
            $values[$key] = $field['Type'] === 'bool' ? ($meta === '1' || $meta === 1 || $meta === true) : $meta;
        }
        return $values;
    }



    private function custom_data_structured_has_content($value) {
        if (is_array($value)) {
            foreach ($value as $item) { if ($this->custom_data_structured_has_content($item)) { return true; } }
            return false;
        }
        if (is_bool($value)) { return true; }
        return $value !== null && trim((string) $value) !== '';
    }

    private function sanitize_custom_data_nested_values(array $fields, $raw, array &$errors, $path) {
        $raw = is_array($raw) ? $raw : [];
        $result = [];
        foreach ($fields as $nested) {
            $nested_errors = [];
            $nested_value = $this->sanitize_custom_data_value($nested, $raw[(string)$nested['Key']] ?? null, $nested_errors);
            foreach ($nested_errors as $error) { $errors[] = sanitize_text_field((string) $path) . ': ' . $error; }
            $result[(string)$nested['Key']] = $nested_value;
        }
        return $result;
    }


    private function sanitize_custom_data_value(array $field, $value, array &$errors) {
        $key = (string) $field['Key'];
        $label = (string) $field['Label'];
        $type = (string) $field['Type'];
        $required = !empty($field['Required']);
        if ($type === 'bool') { return !empty($value); }
        if ($type === 'relation') {
            $relation_id = absint(is_scalar($value) ? $value : 0);
            if ($required && $relation_id <= 0) { $errors[] = "Feltet '{$label}' er obligatorisk."; return 0; }
            if ($relation_id <= 0) { return 0; }
            $target = sanitize_key((string) ($field['RelationTargetType'] ?? ''));
            if ($target === '' || !$this->custom_data_entry_for_type($relation_id, $target)) { $errors[] = "Feltet '{$label}' peger ikke på en gyldig relation."; return 0; }
            return $relation_id;
        }
        if ($type === 'group') {
            $nested = $this->sanitize_custom_data_nested_values((array) ($field['NestedFields'] ?? []), is_array($value) ? $value : [], $errors, $label);
            if ($required && !$this->custom_data_structured_has_content($nested)) { $errors[] = "Feltet '{$label}' er obligatorisk."; }
            return $nested;
        }
        if ($type === 'repeater') {
            $source = is_array($value) && isset($value['items']) && is_array($value['items']) ? $value['items'] : (is_array($value) ? $value : []);
            $limit = $this->clamp_int($field['RepeaterMaxItems'] ?? 10, 1, 20, 10);
            $items = [];
            foreach (array_slice(array_values($source), 0, $limit) as $index => $item) {
                if (!is_array($item) || !empty($item['_remove'])) { continue; }
                $nested = $this->sanitize_custom_data_nested_values((array) ($field['NestedFields'] ?? []), $item, $errors, $label . ' #' . ($index + 1));
                if ($this->custom_data_structured_has_content($nested)) { $items[] = $nested; }
            }
            if ($required && !$items) { $errors[] = "Feltet '{$label}' skal have mindst én række."; }
            return array_slice($items, 0, $limit);
        }
        $value = is_scalar($value) ? trim((string) $value) : '';
        if ($required && $value === '') { $errors[] = "Feltet '{$label}' er obligatorisk."; return ''; }
        if ($value === '') { return $type === 'media' ? 0 : ''; }
        if ($type === 'text') { return sanitize_text_field($value); }
        if ($type === 'number') {
            if (!is_numeric($value)) { $errors[] = "Feltet '{$label}' skal være et tal."; return ''; }
            $number = (float) $value;
            return rtrim(rtrim(number_format($number, 10, '.', ''), '0'), '.');
        }
        if ($type === 'date') {
            $date = DateTime::createFromFormat('!Y-m-d', $value);
            $valid = $date && $date->format('Y-m-d') === $value;
            if (!$valid) { $errors[] = "Feltet '{$label}' skal være en gyldig dato (ÅÅÅÅ-MM-DD)."; return ''; }
            return $value;
        }
        if ($type === 'media') {
            $media_id = absint($value);
            $attachment = $media_id > 0 ? get_post($media_id) : null;
            if (!$attachment instanceof WP_Post || $attachment->post_type !== 'attachment') {
                $errors[] = "Feltet '{$label}' peger ikke på et gyldigt medie.";
                return 0;
            }
            return $media_id;
        }
        $errors[] = "Feltet '{$key}' har en ukendt felttype.";
        return '';
    }

    private function custom_data_redirect($type_key = '', array $args = []) {
        if ($type_key !== '') { $args['type'] = sanitize_key((string) $type_key); }
        $this->redirect('hangar18-data', $args);
    }

    public function handle_save_data_type() {
        if (!current_user_can('manage_options')) { wp_die('Du har ikke rettigheder til at ændre datatyper.'); }
        check_admin_referer('h18_save_data_type');
        $existing_key = sanitize_key((string) wp_unslash($_POST['existing_key'] ?? ''));
        $raw = [
            'Key' => wp_unslash($_POST['data_type_key'] ?? ''),
            'SingularLabel' => wp_unslash($_POST['data_type_singular'] ?? ''),
            'PluralLabel' => wp_unslash($_POST['data_type_plural'] ?? ''),
            'Fields' => isset($_POST['data_fields']) && is_array($_POST['data_fields']) ? wp_unslash($_POST['data_fields']) : [],
        ];
        try {
            $type = $this->normalize_custom_data_type($raw, $existing_key);
            $types = $this->get_custom_data_types();
            if ($existing_key === '' && isset($types[$type['Key']])) { throw new RuntimeException('Der findes allerede en datatype med denne nøgle.'); }
            $known_targets = $types; $known_targets[$type['Key']] = $type;
            foreach ($type['Fields'] as $field) {
                if (($field['Type'] ?? '') === 'relation' && !isset($known_targets[(string) ($field['RelationTargetType'] ?? '')])) {
                    throw new RuntimeException("Relationsfeltet '{$field['Label']}' peger på en datatype, der ikke findes.");
                }
            }
            $now = gmdate('c');
            $created = $existing_key !== '' && isset($types[$existing_key]) ? (string) ($types[$existing_key]['CreatedUtc'] ?? '') : $now;
            $type['CreatedUtc'] = $created !== '' ? $created : $now;
            $type['UpdatedUtc'] = $now;
            $types[$type['Key']] = $type;
            update_option(self::CUSTOM_DATA_TYPES_OPTION, $types, false);
            $this->log('INFO', 'CUSTOM_DATA_TYPE_SAVED', "Datatype '{$type['Key']}' gemt med " . count($type['Fields']) . ' felter.');
            $this->set_notice('success', "Datatypen '{$type['SingularLabel']}' er gemt.");
            $this->custom_data_redirect($type['Key']);
        } catch (Throwable $e) {
            $this->log('ERROR', 'CUSTOM_DATA_TYPE_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Datatypen kunne ikke gemmes: ' . $e->getMessage());
            $this->custom_data_redirect($existing_key !== '' ? $existing_key : 'new');
        }
    }

    public function handle_delete_data_type() {
        if (!current_user_can('manage_options')) { wp_die('Du har ikke rettigheder til at slette datatyper.'); }
        check_admin_referer('h18_delete_data_type');
        $key = sanitize_key((string) wp_unslash($_POST['data_type_key'] ?? ''));
        $types = $this->get_custom_data_types();
        if ($key === '' || !isset($types[$key])) { $this->set_notice('error', 'Datatypen blev ikke fundet.'); $this->custom_data_redirect(); }
        $count = $this->custom_data_entry_count($key);
        if ($count > 0) { $this->set_notice('error', "Datatypen kan ikke slettes, fordi den har {$count} entries."); $this->custom_data_redirect($key); }
        $relation_usage = $this->custom_data_relation_schema_usage($key);
        if ($relation_usage) { $this->set_notice('error', 'Datatypen kan ikke slettes, fordi ' . count($relation_usage) . ' relationsfelt(er) stadig peger på den.'); $this->custom_data_redirect($key); }
        $name = (string) $types[$key]['SingularLabel'];
        unset($types[$key]);
        update_option(self::CUSTOM_DATA_TYPES_OPTION, $types, false);
        $this->log('INFO', 'CUSTOM_DATA_TYPE_DELETED', "Datatype '{$key}' blev slettet.");
        $this->set_notice('success', "Datatypen '{$name}' er slettet.");
        $this->custom_data_redirect();
    }

    public function handle_save_data_entry() {
        $this->require_capability();
        check_admin_referer('h18_save_data_entry');
        $type_key = sanitize_key((string) wp_unslash($_POST['data_type_key'] ?? ''));
        $types = $this->get_custom_data_types();
        if ($type_key === '' || !isset($types[$type_key])) { $this->set_notice('error', 'Datatypen blev ikke fundet.'); $this->custom_data_redirect(); }
        $schema = $types[$type_key];
        $entry_id = absint($_POST['entry_id'] ?? 0);
        if ($entry_id > 0 && !$this->custom_data_entry_for_type($entry_id, $type_key)) { $this->set_notice('error', 'Data-entry blev ikke fundet i den valgte datatype.'); $this->custom_data_redirect($type_key); }
        $title = sanitize_text_field((string) wp_unslash($_POST['entry_title'] ?? ''));
        if ($title === '') { $this->set_notice('error', 'Entry skal have en titel.'); $this->custom_data_redirect($type_key, $entry_id ? ['entry_id' => $entry_id] : []); }
        $raw_values = isset($_POST['data_values']) && is_array($_POST['data_values']) ? wp_unslash($_POST['data_values']) : [];
        $values = [];
        $errors = [];
        foreach ($schema['Fields'] as $field) {
            $field_key = (string) $field['Key'];
            $values[$field_key] = $this->sanitize_custom_data_value($field, $raw_values[$field_key] ?? null, $errors);
        }
        if ($errors) { $this->set_notice('error', implode(' ', $errors)); $this->custom_data_redirect($type_key, $entry_id ? ['entry_id' => $entry_id] : []); }
        $postarr = ['post_type' => self::DATA_ENTRY_POST_TYPE, 'post_status' => 'publish', 'post_title' => $title];
        if ($entry_id > 0) { $postarr['ID'] = $entry_id; $result = wp_update_post($postarr, true); }
        else { $result = wp_insert_post($postarr, true); }
        if (is_wp_error($result)) { $this->set_notice('error', 'Entry kunne ikke gemmes: ' . $result->get_error_message()); $this->custom_data_redirect($type_key); }
        $entry_id = (int) $result;
        update_post_meta($entry_id, '_h18_data_type', $type_key);
        update_post_meta($entry_id, '_h18_data_values', $values);
        update_post_meta($entry_id, '_h18_data_schema_version', (int) ($schema['SchemaVersion'] ?? 1));
        $valid_meta = [];
        foreach ($values as $field_key => $value) {
            $meta_key = '_h18_field_' . sanitize_key((string) $field_key);
            $valid_meta[$meta_key] = true;
            update_post_meta($entry_id, $meta_key, is_bool($value) ? ($value ? '1' : '0') : $value);
        }
        foreach (array_keys((array) get_post_meta($entry_id)) as $meta_key) {
            if (strpos((string) $meta_key, '_h18_field_') === 0 && !isset($valid_meta[$meta_key])) { delete_post_meta($entry_id, $meta_key); }
        }
        $raw_tags = sanitize_text_field((string) wp_unslash($_POST['data_tags'] ?? ''));
        $tags = [];
        foreach (array_slice(preg_split('/\s*,\s*/', $raw_tags), 0, 20) as $tag) {
            $tag = sanitize_text_field((string) $tag); if ($tag !== '' && !in_array($tag, $tags, true)) { $tags[] = $tag; }
        }
        $term_result = wp_set_object_terms($entry_id, $tags, self::DATA_TAG_TAXONOMY, false);
        if (is_wp_error($term_result)) { $this->log('WARN','CUSTOM_DATA_TAG_SAVE_FAILED',$term_result->get_error_message()); }
        $this->log('INFO', 'CUSTOM_DATA_ENTRY_SAVED', "Data-entry ID {$entry_id} gemt i '{$type_key}'.");
        $this->set_notice('success', "Entry '{$title}' er gemt.");
        $this->custom_data_redirect($type_key, ['entry_id' => $entry_id]);
    }

    public function handle_delete_data_entry() {
        $this->require_capability();
        check_admin_referer('h18_delete_data_entry');
        $type_key = sanitize_key((string) wp_unslash($_POST['data_type_key'] ?? ''));
        $entry_id = absint($_POST['entry_id'] ?? 0);
        $entry = $this->custom_data_entry_for_type($entry_id, $type_key);
        if (!$entry) { $this->set_notice('error', 'Data-entry blev ikke fundet.'); $this->custom_data_redirect($type_key); }
        $title = (string) $entry->post_title;
        wp_delete_post($entry_id, true);
        $this->log('INFO', 'CUSTOM_DATA_ENTRY_DELETED', "Data-entry ID {$entry_id} slettet fra '{$type_key}'.");
        $this->set_notice('success', "Entry '{$title}' er slettet.");
        $this->custom_data_redirect($type_key);
    }



    private function render_custom_data_value_input(array $field, $value, $name) {
        $type = (string) $field['Type'];
        if ($type === 'bool') {
            echo '<input type="hidden" name="' . esc_attr($name) . '" value="0" /><label class="h18-data-bool"><input type="checkbox" name="' . esc_attr($name) . '" value="1" ' . checked(!empty($value), true, false) . ' /> Ja</label>'; return;
        }
        if ($type === 'number') { echo '<input type="number" step="any" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />'; return; }
        if ($type === 'date') { echo '<input type="date" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />'; return; }
        if ($type === 'media') {
            $media_id = absint($value); echo '<div class="h18-data-media-field"><input class="h18-data-media-id" type="hidden" name="' . esc_attr($name) . '" value="' . esc_attr($media_id) . '" /><div class="h18-data-media-preview">'; if ($media_id) { echo wp_get_attachment_image($media_id, 'thumbnail'); } echo '</div><button type="button" class="button h18-data-media-pick">Vælg medie</button> <button type="button" class="button-link-delete h18-data-media-clear">Fjern</button></div>'; return;
        }
        echo '<input type="text" name="' . esc_attr($name) . '" value="' . esc_attr(is_scalar($value) ? (string) $value : '') . '" />';
    }

    private function render_custom_data_nested_inputs(array $fields, $values, $name_prefix) {
        $values = is_array($values) ? $values : [];
        echo '<div class="h18-data-nested-fields">';
        foreach ($fields as $nested) {
            $key = (string) $nested['Key']; echo '<div class="h18-field"><label><strong>' . esc_html((string)$nested['Label']) . (!empty($nested['Required']) && $nested['Type'] !== 'bool' ? ' *' : '') . '</strong><small>' . esc_html($this->custom_data_nested_field_types()[$nested['Type']] ?? $nested['Type']) . '</small></label>';
            $this->render_custom_data_value_input($nested, $values[$key] ?? '', $name_prefix . '[' . $key . ']'); echo '</div>';
        }
        echo '</div>';
    }


    private function render_custom_data_field_input(array $field, $value) {
        $key = (string) $field['Key']; $name = 'data_values[' . $key . ']'; $type = (string) $field['Type'];
        if ($type === 'relation') {
            $target = sanitize_key((string) ($field['RelationTargetType'] ?? '')); $entries = $target !== '' ? $this->custom_data_entry_query($target, 200) : []; $current = absint($value);
            echo '<select name="' . esc_attr($name) . '"><option value="0">Ingen relation</option>'; foreach ($entries as $entry) { echo '<option value="' . (int)$entry->ID . '" ' . selected($current,(int)$entry->ID,false) . '>' . esc_html((string)$entry->post_title) . '</option>'; } echo '</select>'; return;
        }
        if ($type === 'group') { echo '<fieldset class="h18-data-group"><legend>' . esc_html((string)$field['Label']) . '</legend>'; $this->render_custom_data_nested_inputs((array)($field['NestedFields']??[]),is_array($value)?$value:[],$name); echo '</fieldset>'; return; }
        if ($type === 'repeater') {
            $items=is_array($value)?array_values($value):[]; if(!$items)$items=[[]]; $limit=$this->clamp_int($field['RepeaterMaxItems']??10,1,20,10); echo '<div class="h18-data-repeater" data-max-items="'.(int)$limit.'"><div class="h18-data-repeater-items">'; foreach(array_slice($items,0,$limit) as $i=>$item){echo '<fieldset class="h18-data-repeater-item" data-item-index="'.(int)$i.'"><legend>Række '.((int)$i+1).'</legend>'; $this->render_custom_data_nested_inputs((array)($field['NestedFields']??[]),is_array($item)?$item:[],$name.'[items]['.(int)$i.']'); echo '<button type="button" class="button-link-delete h18-data-repeater-remove">Fjern række</button></fieldset>';} echo '</div><template class="h18-data-repeater-template"><fieldset class="h18-data-repeater-item" data-item-index="__ITEM__"><legend>Række</legend>'; $this->render_custom_data_nested_inputs((array)($field['NestedFields']??[]),[],$name.'[items][__ITEM__]'); echo '<button type="button" class="button-link-delete h18-data-repeater-remove">Fjern række</button></fieldset></template><button type="button" class="button h18-data-repeater-add">+ Tilføj række</button></div>'; return;
        }
        $this->render_custom_data_value_input($field,$value,$name);
    }



    private function custom_data_query_operator_map($field_type) {
        $maps = [
            'text' => ['eq'=>'Er lig med','neq'=>'Er ikke lig med','contains'=>'Indeholder'],
            'number' => ['eq'=>'=','neq'=>'≠','gt'=>'>','gte'=>'≥','lt'=>'<','lte'=>'≤'],
            'bool' => ['eq'=>'Er lig med'],
            'date' => ['eq'=>'På dato','before'=>'Før','after'=>'Efter'],
            'media' => ['eq'=>'Er lig med','neq'=>'Er ikke lig med'],
        ];
        return $maps[(string) $field_type] ?? [];
    }

    private function normalize_custom_data_query(array $raw) {
        $types = $this->get_custom_data_types();
        $type_key = sanitize_key((string) ($raw['Type'] ?? $raw['type'] ?? ''));
        if ($type_key === '' || !isset($types[$type_key])) { throw new RuntimeException('Query Builder: vælg en gyldig datatype.'); }
        $schema = $types[$type_key];
        $field_map = [];
        foreach ($schema['Fields'] as $field) { $field_map[(string) $field['Key']] = $field; }

        $field_key = sanitize_key((string) ($raw['Field'] ?? $raw['field'] ?? ''));
        $operator = sanitize_key((string) ($raw['Operator'] ?? $raw['op'] ?? 'eq'));
        $value_raw = $raw['Value'] ?? $raw['value'] ?? '';
        $filter = null;
        if ($field_key !== '') {
            if (!isset($field_map[$field_key])) { throw new RuntimeException('Query Builder: filterfeltet findes ikke i datatypen.'); }
            $field = $field_map[$field_key];
            $field_type = (string) $field['Type'];
            $operators = $this->custom_data_query_operator_map($field_type);
            if (!isset($operators[$operator])) { throw new RuntimeException('Query Builder: operatoren er ikke tilladt for denne felttype.'); }
            if ($field_type === 'number') {
                if (!is_numeric($value_raw)) { throw new RuntimeException('Query Builder: filterværdien skal være et tal.'); }
                $value = (string) (0 + $value_raw);
            } elseif ($field_type === 'bool') {
                $value = $this->bool_value($value_raw, false) ? '1' : '0';
            } elseif ($field_type === 'date') {
                $value = sanitize_text_field((string) $value_raw);
                $date = DateTime::createFromFormat('!Y-m-d', $value);
                if (!$date || $date->format('Y-m-d') !== $value) { throw new RuntimeException('Query Builder: dato skal være ÅÅÅÅ-MM-DD.'); }
            } elseif ($field_type === 'media') {
                $value = (string) absint($value_raw);
            } else {
                $value = sanitize_text_field((string) $value_raw);
            }
            $filter = ['Field'=>$field_key,'FieldType'=>$field_type,'Operator'=>$operator,'Value'=>$value];
        }

        $sort_raw = (string) ($raw['Sort'] ?? $raw['sort'] ?? 'modified');
        $sort = in_array($sort_raw, ['title','modified','created'], true) ? $sort_raw : '';
        if ($sort === '' && strpos($sort_raw, 'field:') === 0) {
            $sort_field = sanitize_key(substr($sort_raw, 6));
            if ($sort_field !== '' && isset($field_map[$sort_field]) && in_array((string) $field_map[$sort_field]['Type'], ['text','number','date','media'], true)) {
                $sort = 'field:' . $sort_field;
            }
        }
        if ($sort === '') { $sort = 'modified'; }
        $order = strtoupper((string) ($raw['Order'] ?? $raw['order'] ?? 'DESC'));
        if (!in_array($order, ['ASC','DESC'], true)) { $order = 'DESC'; }
        $limit = $this->clamp_int($raw['Limit'] ?? $raw['limit'] ?? 10, 1, 100, 10);
        return [
            'Type' => $type_key,
            'Schema' => $schema,
            'Filter' => $filter,
            'Sort' => $sort,
            'Order' => $order,
            'Limit' => $limit,
        ];
    }

    private function custom_data_query_compare($operator) {
        $map = ['eq'=>'=','neq'=>'!=','contains'=>'LIKE','gt'=>'>','gte'=>'>=','lt'=>'<','lte'=>'<=','before'=>'<','after'=>'>'];
        return $map[(string) $operator] ?? '=';
    }

    private function run_custom_data_query(array $raw, &$normalized = null) {
        $query = $this->normalize_custom_data_query($raw);
        $normalized = $query;
        $meta_query = [[
            'key' => '_h18_data_type',
            'value' => $query['Type'],
            'compare' => '=',
        ]];
        if (is_array($query['Filter'])) {
            $filter = $query['Filter'];
            $meta_type = 'CHAR';
            if (in_array($filter['FieldType'], ['number','bool','media'], true)) { $meta_type = 'NUMERIC'; }
            elseif ($filter['FieldType'] === 'date') { $meta_type = 'DATE'; }
            $meta_query[] = [
                'key' => '_h18_field_' . $filter['Field'],
                'value' => $filter['Value'],
                'compare' => $this->custom_data_query_compare($filter['Operator']),
                'type' => $meta_type,
            ];
        }
        $args = [
            'post_type' => self::DATA_ENTRY_POST_TYPE,
            'post_status' => 'publish',
            'posts_per_page' => (int) $query['Limit'],
            'no_found_rows' => true,
            'meta_query' => $meta_query,
            'order' => $query['Order'],
        ];
        if ($query['Sort'] === 'title') { $args['orderby'] = 'title'; }
        elseif ($query['Sort'] === 'created') { $args['orderby'] = 'date'; }
        elseif ($query['Sort'] === 'modified') { $args['orderby'] = 'modified'; }
        else {
            $sort_field = sanitize_key(substr((string) $query['Sort'], 6));
            $field_map = [];
            foreach ($query['Schema']['Fields'] as $field) { $field_map[(string) $field['Key']] = $field; }
            $args['meta_key'] = '_h18_field_' . $sort_field;
            $args['orderby'] = isset($field_map[$sort_field]) && in_array((string) $field_map[$sort_field]['Type'], ['number','media'], true) ? 'meta_value_num' : 'meta_value';
        }
        return get_posts($args);
    }

    private function custom_data_query_shortcode_from_normalized(array $query) {
        $parts = ['type="' . esc_attr($query['Type']) . '"'];
        if (is_array($query['Filter'])) {
            $parts[] = 'field="' . esc_attr($query['Filter']['Field']) . '"';
            $parts[] = 'op="' . esc_attr($query['Filter']['Operator']) . '"';
            $parts[] = 'value="' . esc_attr($query['Filter']['Value']) . '"';
        }
        $parts[] = 'sort="' . esc_attr($query['Sort']) . '"';
        $parts[] = 'order="' . esc_attr($query['Order']) . '"';
        $parts[] = 'limit="' . (int) $query['Limit'] . '"';
        return '[hangar18_data_query ' . implode(' ', $parts) . ']';
    }

    public function shortcode_data_query($atts) {
        $atts = shortcode_atts(['type'=>'','field'=>'','op'=>'eq','value'=>'','sort'=>'modified','order'=>'DESC','limit'=>'10'], $atts, 'hangar18_data_query');
        try {
            $normalized = null;
            $posts = $this->run_custom_data_query($atts, $normalized);
        } catch (Throwable $e) {
            return current_user_can('edit_pages') ? '<p class="h18-data-query-error">' . esc_html($e->getMessage()) . '</p>' : '';
        }
        if (!$posts) { return '<div class="h18-data-query-results h18-data-query-results--empty">Ingen resultater.</div>'; }
        $hash = substr(hash('sha256', wp_json_encode($normalized)), 0, 16);
        $html = '<ul class="h18-data-query-results" data-query-hash="' . esc_attr($hash) . '">';
        foreach ($posts as $post) {
            if (!$post instanceof WP_Post) { continue; }
            $html .= '<li data-entry-id="' . (int) $post->ID . '">' . esc_html((string) $post->post_title) . '</li>';
        }
        return $html . '</ul>';
    }




    /* ================================================================
       ADVANCED QUERY ENGINE — v0.5.29 / E5 UD-056
       ================================================================ */

    private function advanced_data_query_field_map(array $schema) {
        $map=[]; foreach((array)($schema['Fields']??[]) as $field){if(is_array($field)&&!empty($field['Key']))$map[(string)$field['Key']]=$field;} return $map;
    }

    private function normalize_advanced_data_query(array $raw) {
        $types=$this->get_custom_data_types(); $type_key=sanitize_key((string)($raw['Type']??$raw['type']??''));
        if($type_key===''||!isset($types[$type_key]))throw new RuntimeException('Advanced Query: vælg en gyldig datatype.');
        $schema=$types[$type_key];$field_map=$this->advanced_data_query_field_map($schema);$group_relation=strtoupper((string)($raw['GroupRelation']??'AND'));if(!in_array($group_relation,['AND','OR'],true))$group_relation='AND';
        $groups_raw=$raw['Groups']??[];if(is_string($groups_raw)){ $decoded=json_decode($groups_raw,true);$groups_raw=is_array($decoded)?$decoded:[]; } if(!is_array($groups_raw))$groups_raw=[];
        $groups=[];
        foreach(array_slice(array_values($groups_raw),0,4) as $group_index=>$group){if(!is_array($group))continue;$relation=strtoupper((string)($group['Relation']??'AND'));if(!in_array($relation,['AND','OR'],true))$relation='AND';$filters=[];
            foreach(array_slice(array_values((array)($group['Filters']??[])),0,6) as $filter){if(!is_array($filter))continue;$kind=sanitize_key((string)($filter['Kind']??'field'));
                if($kind==='taxonomy'){$operator=sanitize_key((string)($filter['Operator']??'in'));if(!in_array($operator,['in','not_in'],true))$operator='in';$terms=[];foreach(array_slice(preg_split('/\\s*,\\s*/',(string)($filter['Value']??'')),0,10) as $term){$term=sanitize_title((string)$term);if($term!==''&&!in_array($term,$terms,true))$terms[]=$term;}if(!$terms)continue;$filters[]=['Kind'=>'taxonomy','Operator'=>$operator,'Terms'=>$terms];continue;}
                $field_key=sanitize_key((string)($filter['Field']??''));if($field_key===''||!isset($field_map[$field_key]))continue;$field=$field_map[$field_key];$field_type=(string)$field['Type'];if(in_array($field_type,['group','repeater'],true))continue;
                $operators=$field_type==='relation'?['eq','neq'] : array_keys($this->custom_data_query_operator_map($field_type));$operator=sanitize_key((string)($filter['Operator']??'eq'));if(!in_array($operator,$operators,true))continue;$value_raw=$filter['Value']??'';
                if(in_array($field_type,['number','relation','media'],true)){if(!is_numeric($value_raw))continue;$value=(string)(0+$value_raw);}elseif($field_type==='bool'){$value=$this->bool_value($value_raw,false)?'1':'0';}elseif($field_type==='date'){$value=sanitize_text_field((string)$value_raw);$date=DateTime::createFromFormat('!Y-m-d',$value);if(!$date||$date->format('Y-m-d')!==$value)continue;}else{$value=sanitize_text_field((string)$value_raw);}
                $filters[]=['Kind'=>'field','Field'=>$field_key,'FieldType'=>$field_type,'Operator'=>$operator,'Value'=>$value];
            }
            if($filters)$groups[]=['Relation'=>$relation,'Filters'=>$filters];
        }
        $sort_raw=(string)($raw['Sort']??'modified');$sort=in_array($sort_raw,['title','modified','created'],true)?$sort_raw:'';if($sort===''&&strpos($sort_raw,'field:')===0){$field_key=sanitize_key(substr($sort_raw,6));if(isset($field_map[$field_key])&&!in_array((string)$field_map[$field_key]['Type'],['bool','group','repeater'],true))$sort='field:'.$field_key;}if($sort==='')$sort='modified';
        $order=strtoupper((string)($raw['Order']??'DESC'));if(!in_array($order,['ASC','DESC'],true))$order='DESC';$per_page=$this->clamp_int($raw['PerPage']??12,1,50,12);$page=$this->clamp_int($raw['Page']??1,1,10000,1);
        return ['Type'=>$type_key,'Schema'=>$schema,'GroupRelation'=>$group_relation,'Groups'=>$groups,'Sort'=>$sort,'Order'=>$order,'PerPage'=>$per_page,'Page'=>$page];
    }

    private function advanced_data_query_compare_value($actual,array $filter) {
        $type=(string)($filter['FieldType']??'text');$op=(string)($filter['Operator']??'eq');$expected=$filter['Value']??'';
        if(in_array($type,['number','relation','media'],true)){$a=(float)$actual;$b=(float)$expected;}elseif($type==='bool'){$a=$this->bool_value($actual,false)?1:0;$b=$this->bool_value($expected,false)?1:0;}else{$a=(string)$actual;$b=(string)$expected;}
        if($op==='contains')return stripos((string)$a,(string)$b)!==false;if($op==='eq')return $a==$b;if($op==='neq')return $a!=$b;if($op==='gt'||$op==='after')return $a>$b;if($op==='gte')return $a>=$b;if($op==='lt'||$op==='before')return $a<$b;if($op==='lte')return $a<=$b;return false;
    }

    private function advanced_data_query_filter_matches(WP_Post $post,array $filter) {
        if(($filter['Kind']??'field')==='taxonomy'){$slugs=wp_get_object_terms($post->ID,self::DATA_TAG_TAXONOMY,['fields'=>'slugs']);if(is_wp_error($slugs))$slugs=[];$has=(bool)array_intersect((array)$filter['Terms'],array_map('strval',(array)$slugs));return ($filter['Operator']??'in')==='not_in'?!$has:$has;}
        $actual=get_post_meta($post->ID,'_h18_field_'.sanitize_key((string)$filter['Field']),true);return $this->advanced_data_query_compare_value($actual,$filter);
    }

    private function advanced_data_query_group_matches(WP_Post $post,array $group) {
        $results=[];foreach((array)$group['Filters'] as $filter)$results[]=$this->advanced_data_query_filter_matches($post,$filter);if(!$results)return true;return ($group['Relation']??'AND')==='OR'?in_array(true,$results,true):!in_array(false,$results,true);
    }

    private function advanced_data_query_post_matches(WP_Post $post,array $query) {
        if(!$query['Groups'])return true;$results=[];foreach($query['Groups'] as $group)$results[]=$this->advanced_data_query_group_matches($post,$group);return $query['GroupRelation']==='OR'?in_array(true,$results,true):!in_array(false,$results,true);
    }

    private function advanced_data_query_sort_value(WP_Post $post,array $query) {
        if($query['Sort']==='title')return mb_strtolower((string)$post->post_title);if($query['Sort']==='created')return strtotime((string)$post->post_date_gmt)?:0;if($query['Sort']==='modified')return strtotime((string)$post->post_modified_gmt)?:0;$field=sanitize_key(substr((string)$query['Sort'],6));$map=$this->advanced_data_query_field_map($query['Schema']);$value=get_post_meta($post->ID,'_h18_field_'.$field,true);$type=(string)($map[$field]['Type']??'text');return in_array($type,['number','relation','media'],true)?(float)$value:mb_strtolower((string)$value);
    }

    private function run_advanced_data_query(array $raw,&$normalized=null) {
        $query=$this->normalize_advanced_data_query($raw);$normalized=$query;$candidate_limit=2000;
        $candidates=get_posts(['post_type'=>self::DATA_ENTRY_POST_TYPE,'post_status'=>'publish','posts_per_page'=>$candidate_limit,'no_found_rows'=>true,'meta_key'=>'_h18_data_type','meta_value'=>$query['Type'],'orderby'=>'ID','order'=>'ASC']);
        $matches=[];foreach($candidates as $post){if($post instanceof WP_Post&&$this->advanced_data_query_post_matches($post,$query))$matches[]=$post;}
        usort($matches,function($a,$b)use($query){$av=$this->advanced_data_query_sort_value($a,$query);$bv=$this->advanced_data_query_sort_value($b,$query);$cmp=$av<=>$bv;if($cmp===0)$cmp=((int)$a->ID)<=>((int)$b->ID);return $query['Order']==='DESC'?-$cmp:$cmp;});
        $total=count($matches);$pages=max(1,(int)ceil($total/$query['PerPage']));$page=min($query['Page'],$pages);$offset=($page-1)*$query['PerPage'];$posts=array_slice($matches,$offset,$query['PerPage']);
        return ['Posts'=>$posts,'Total'=>$total,'TotalPages'=>$pages,'Page'=>$page,'PerPage'=>$query['PerPage'],'Truncated'=>count($candidates)>=$candidate_limit,'Query'=>$query];
    }

    private function advanced_data_query_public_config(array $query) {return ['Type'=>$query['Type'],'GroupRelation'=>$query['GroupRelation'],'Groups'=>$query['Groups'],'Sort'=>$query['Sort'],'Order'=>$query['Order'],'PerPage'=>$query['PerPage']];}
    private function advanced_data_query_encode(array $query) {$json=wp_json_encode($this->advanced_data_query_public_config($query));return rtrim(strtr(base64_encode((string)$json),'+/','-_'),'=');}
    private function advanced_data_query_decode($config) {$config=preg_replace('/[^A-Za-z0-9_-]/','',(string)$config);if($config===''||strlen($config)>12000)throw new RuntimeException('Advanced Query config mangler eller er for stor.');$pad=strlen($config)%4;if($pad)$config.=str_repeat('=',4-$pad);$json=base64_decode(strtr($config,'-_','+/'),true);$raw=$json!==false?json_decode($json,true):null;if(!is_array($raw))throw new RuntimeException('Advanced Query config er ugyldig.');return $raw;}
    private function advanced_data_query_shortcode(array $query) {return '[hangar18_data_query_advanced config="'.esc_attr($this->advanced_data_query_encode($query)).'"]';}

    public function shortcode_data_query_advanced($atts) {
        $atts=shortcode_atts(['config'=>''],$atts,'hangar18_data_query_advanced');try{$raw=$this->advanced_data_query_decode($atts['config']);$probe=$this->normalize_advanced_data_query($raw);$hash=substr(hash('sha256',$this->advanced_data_query_encode($probe)),0,12);$page_param='h18q_'.$hash;$raw['Page']=isset($_GET[$page_param])?absint($_GET[$page_param]):1;$normalized=null;$result=$this->run_advanced_data_query($raw,$normalized);}catch(Throwable $e){return current_user_can('edit_pages')?'<p class="h18-data-query-error">'.esc_html($e->getMessage()).'</p>':'';}
        if(!$result['Posts'])return '<div class="h18-data-query-results h18-data-query-results--empty">Ingen resultater.</div>';$html='<ul class="h18-data-query-results h18-data-query-results--advanced">';foreach($result['Posts'] as $post)$html.='<li data-entry-id="'.(int)$post->ID.'">'.esc_html((string)$post->post_title).'</li>';$html.='</ul>';
        if($result['TotalPages']>1){$html.='<nav class="h18-data-pagination" aria-label="Sider">';for($i=1;$i<=$result['TotalPages'];$i++){if($i>20&&abs($i-$result['Page'])>2&&$i!=$result['TotalPages'])continue;$url=add_query_arg($page_param,$i);$html.='<a '.($i===$result['Page']?'aria-current="page" ':'').'href="'.esc_url($url).'">'.(int)$i.'</a>';}$html.='</nav>';}
        return $html;
    }


    public function render_data() {
        $this->require_capability();
        $types = $this->get_custom_data_types();
        $requested = isset($_GET['type']) ? sanitize_key((string) wp_unslash($_GET['type'])) : '';
        if ($requested === '' && $types) { $requested = (string) array_key_first($types); }
        $is_new = $requested === 'new' || !$types;
        $selected = !$is_new && isset($types[$requested]) ? $types[$requested] : null;
        if (!$is_new && !$selected && $types) { $requested = (string) array_key_first($types); $selected = $types[$requested]; }
        $entry_id = absint($_GET['entry_id'] ?? 0);
        $entry = $selected && $entry_id ? $this->custom_data_entry_for_type($entry_id, $selected['Key']) : null;
        $entry_values = $entry && $selected ? $this->custom_data_entry_values($entry->ID, $selected) : [];
        $entry_tags = $entry ? wp_get_object_terms($entry->ID, self::DATA_TAG_TAXONOMY, ['fields'=>'names']) : [];
        if (is_wp_error($entry_tags)) { $entry_tags = []; }
        $entries = $selected ? $this->custom_data_entry_query($selected['Key'], 100) : [];
        $can_schema = current_user_can('manage_options');
        $blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'RelationTargetType'=>'','NestedFields'=>[],'RepeaterMaxItems'=>10,'Order'=>1];
        $query_preview = !empty($_GET['query_preview']) && $selected;
        $qb_raw = [
            'Type' => $selected ? $selected['Key'] : '',
            'Field' => isset($_GET['qb_field']) ? wp_unslash($_GET['qb_field']) : '',
            'Operator' => isset($_GET['qb_operator']) ? wp_unslash($_GET['qb_operator']) : 'eq',
            'Value' => isset($_GET['qb_value']) ? wp_unslash($_GET['qb_value']) : '',
            'Sort' => isset($_GET['qb_sort']) ? wp_unslash($_GET['qb_sort']) : 'modified',
            'Order' => isset($_GET['qb_order']) ? wp_unslash($_GET['qb_order']) : 'DESC',
            'Limit' => isset($_GET['qb_limit']) ? wp_unslash($_GET['qb_limit']) : 10,
        ];
        $qb_results = []; $qb_normalized = null; $qb_error = '';
        if ($query_preview) {
            try { $qb_results = $this->run_custom_data_query($qb_raw, $qb_normalized); }
            catch (Throwable $e) { $qb_error = $e->getMessage(); }
        }
        $advanced_preview = !empty($_GET['advanced_preview']) && $selected;
        $aq_groups_json = isset($_GET['aq_groups']) ? (string) wp_unslash($_GET['aq_groups']) : '';
        $aq_groups = $aq_groups_json !== '' ? json_decode($aq_groups_json,true) : [];
        if (!is_array($aq_groups)) { $aq_groups=[]; }
        $aq_raw=['Type'=>$selected?$selected['Key']:'','GroupRelation'=>isset($_GET['aq_group_relation'])?wp_unslash($_GET['aq_group_relation']):'AND','Groups'=>$aq_groups,'Sort'=>isset($_GET['aq_sort'])?wp_unslash($_GET['aq_sort']):'modified','Order'=>isset($_GET['aq_order'])?wp_unslash($_GET['aq_order']):'DESC','PerPage'=>isset($_GET['aq_per_page'])?wp_unslash($_GET['aq_per_page']):12,'Page'=>isset($_GET['aq_page'])?wp_unslash($_GET['aq_page']):1];
        $aq_result=null;$aq_normalized=null;$aq_error='';if($advanced_preview){try{$aq_result=$this->run_advanced_data_query($aq_raw,$aq_normalized);}catch(Throwable $e){$aq_error=$e->getMessage();}}
        $aq_tags=get_terms(['taxonomy'=>self::DATA_TAG_TAXONOMY,'hide_empty'=>false,'fields'=>'all']);if(is_wp_error($aq_tags))$aq_tags=[];
        ?>
        <div class="wrap h18-admin h18-data-admin">
            <h1>Data</h1>
            <?php $this->render_notice(); ?>
            <div class="h18-help-box"><strong>E5 Dynamic CMS:</strong> Datatyperne understøtter primitive felter samt Relation, Group og Repeater. Relationer peger på en konkret datatype; Group/Repeater bruger validerede typed underfelter.</div>
            <nav class="h18-page-tabs h18-data-type-tabs" aria-label="Vælg datatype">
                <?php foreach ($types as $type_key => $type) : ?><a class="<?php echo $selected && $selected['Key'] === $type_key ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($type_key))); ?>"><?php echo esc_html($type['PluralLabel']); ?></a><?php endforeach; ?>
                <?php if ($can_schema) : ?><a class="<?php echo $is_new ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=new')); ?>">+ Ny datatype</a><?php endif; ?>
            </nav>

            <?php if ($is_new && !$can_schema) : ?>
                <div class="notice notice-warning"><p>Der er endnu ingen datatyper. En administrator skal oprette den første datatype.</p></div>
            <?php elseif ($is_new) :
                $schema = ['Key'=>'','SingularLabel'=>'','PluralLabel'=>'','Fields'=>[$blank_field]]; ?>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" class="h18-panel h18-data-schema-form">
                    <?php wp_nonce_field('h18_save_data_type'); ?><input type="hidden" name="action" value="h18_save_data_type" /><input type="hidden" name="existing_key" value="" />
                    <h2>Ny datatype</h2>
                    <div class="h18-module-fields-grid h18-module-fields-grid--four">
                        <div class="h18-field"><label><strong>Nøgle</strong></label><input id="h18-data-type-key" type="text" name="data_type_key" value="" placeholder="fx museum_vehicle" required /></div>
                        <div class="h18-field"><label><strong>Navn – ental</strong></label><input id="h18-data-type-singular" type="text" name="data_type_singular" value="" required /></div>
                        <div class="h18-field"><label><strong>Navn – flertal</strong></label><input type="text" name="data_type_plural" value="" /></div>
                    </div>
                    <h3>Felter</h3><div id="h18-data-schema-fields" class="h18-data-schema-fields"><?php $this->render_data_schema_field_row($blank_field, 0); ?></div>
                    <button type="button" class="button" id="h18-data-add-field">+ Tilføj felt</button>
                    <p><button type="submit" class="button button-primary">Opret datatype</button></p>
                </form>
            <?php elseif ($selected) : ?>
                <div class="h18-data-summary"><div><h2><?php echo esc_html($selected['PluralLabel']); ?></h2><p><code><?php echo esc_html($selected['Key']); ?></code> · <?php echo esc_html(count($selected['Fields'])); ?> felter · <?php echo esc_html(count($entries)); ?> viste entries</p></div><a class="button button-primary" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($selected['Key']) . '&entry_id=0#h18-data-entry-form')); ?>">+ Ny <?php echo esc_html($selected['SingularLabel']); ?></a></div>


                <section class="h18-panel h18-data-query-builder">
                    <div class="h18-panel-heading-row"><div><h3>Query Builder v1</h3><p>Type + ét filter + sortering + limit. Advanced AND/OR og pagination kommer i UD-056.</p></div><span>UD-055</span></div>
                    <form method="get" action="<?php echo esc_url(admin_url('admin.php')); ?>" class="h18-data-query-form">
                        <input type="hidden" name="page" value="hangar18-data" /><input type="hidden" name="type" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="query_preview" value="1" />
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field"><label><strong>Filterfelt</strong></label><select id="h18-qb-field" name="qb_field"><option value="">Intet filter</option><?php foreach ($selected['Fields'] as $field) : if (!in_array($field['Type'], ['text','number','bool','date','media'], true)) continue; ?><option value="<?php echo esc_attr($field['Key']); ?>" data-field-type="<?php echo esc_attr($field['Type']); ?>" <?php selected((string) $qb_raw['Field'], (string) $field['Key']); ?>><?php echo esc_html($field['Label'] . ' · ' . $field['Type']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Operator</strong></label><select id="h18-qb-operator" name="qb_operator" data-current="<?php echo esc_attr((string) $qb_raw['Operator']); ?>"></select></div>
                            <div class="h18-field"><label><strong>Værdi</strong></label><input id="h18-qb-value" type="text" name="qb_value" value="<?php echo esc_attr((string) $qb_raw['Value']); ?>" /><p class="description">Bool: ja/nej. Dato: ÅÅÅÅ-MM-DD. Media: attachment-ID.</p></div>
                            <div class="h18-field"><label><strong>Sortér</strong></label><select name="qb_sort"><option value="modified" <?php selected($qb_raw['Sort'],'modified'); ?>>Senest ændret</option><option value="created" <?php selected($qb_raw['Sort'],'created'); ?>>Oprettet</option><option value="title" <?php selected($qb_raw['Sort'],'title'); ?>>Titel</option><?php foreach ($selected['Fields'] as $field) : if ($field['Type'] === 'bool') continue; ?><?php if (!in_array($field['Type'], ['text','number','date','media'], true)) continue; ?><option value="field:<?php echo esc_attr($field['Key']); ?>" <?php selected($qb_raw['Sort'],'field:' . $field['Key']); ?>><?php echo esc_html($field['Label']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Retning</strong></label><select name="qb_order"><option value="DESC" <?php selected(strtoupper((string)$qb_raw['Order']),'DESC'); ?>>Faldende</option><option value="ASC" <?php selected(strtoupper((string)$qb_raw['Order']),'ASC'); ?>>Stigende</option></select></div>
                            <div class="h18-field"><label><strong>Limit</strong></label><input type="number" name="qb_limit" min="1" max="100" value="<?php echo esc_attr((int) $qb_raw['Limit']); ?>" /></div>
                        </div>
                        <p><button type="submit" class="button button-primary">Kør preview</button></p>
                    </form>
                    <?php if ($query_preview) : ?>
                        <div class="h18-data-query-preview">
                            <?php if ($qb_error !== '') : ?><div class="notice notice-error inline"><p><?php echo esc_html($qb_error); ?></p></div>
                            <?php else : ?>
                                <p><strong><?php echo esc_html(count($qb_results)); ?> resultat(er)</strong> — samme server-query bruges af frontend-shortcode.</p>
                                <table class="widefat striped"><thead><tr><th>ID</th><th>Titel</th><th>Ændret</th></tr></thead><tbody><?php foreach ($qb_results as $qb_post) : ?><tr><td><?php echo esc_html((int)$qb_post->ID); ?></td><td><?php echo esc_html($qb_post->post_title); ?></td><td><?php echo esc_html(get_post_modified_time('Y-m-d H:i', false, $qb_post)); ?></td></tr><?php endforeach; ?></tbody></table>
                                <p><strong>Frontend:</strong> <code><?php echo esc_html($this->custom_data_query_shortcode_from_normalized($qb_normalized)); ?></code></p>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </section>




                <section class="h18-panel h18-data-advanced-query">
                    <div class="h18-panel-heading-row"><div><h3>Advanced Query</h3><p>AND/OR-grupper, relationer, Data Tags og pagination. Samme normalized evaluator bruges i preview og frontend.</p></div><span>UD-056</span></div>
                    <form method="get" action="<?php echo esc_url(admin_url('admin.php')); ?>" id="h18-advanced-query-form">
                        <input type="hidden" name="page" value="hangar18-data" /><input type="hidden" name="type" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="advanced_preview" value="1" /><input type="hidden" id="h18-aq-groups-json" name="aq_groups" value="<?php echo esc_attr(wp_json_encode($aq_groups)); ?>" />
                        <div class="h18-module-fields-grid h18-module-fields-grid--four"><div class="h18-field"><label><strong>Mellem grupper</strong></label><select name="aq_group_relation"><option value="AND" <?php selected(strtoupper((string)$aq_raw['GroupRelation']),'AND'); ?>>AND</option><option value="OR" <?php selected(strtoupper((string)$aq_raw['GroupRelation']),'OR'); ?>>OR</option></select></div><div class="h18-field"><label><strong>Sortér</strong></label><select name="aq_sort"><option value="modified" <?php selected($aq_raw['Sort'],'modified'); ?>>Senest ændret</option><option value="created" <?php selected($aq_raw['Sort'],'created'); ?>>Oprettet</option><option value="title" <?php selected($aq_raw['Sort'],'title'); ?>>Titel</option><?php foreach($selected['Fields'] as $field):if(in_array($field['Type'],['bool','group','repeater'],true))continue;?><option value="field:<?php echo esc_attr($field['Key']); ?>" <?php selected($aq_raw['Sort'],'field:'.$field['Key']); ?>><?php echo esc_html($field['Label']); ?></option><?php endforeach;?></select></div><div class="h18-field"><label><strong>Retning</strong></label><select name="aq_order"><option value="DESC" <?php selected(strtoupper((string)$aq_raw['Order']),'DESC'); ?>>Faldende</option><option value="ASC" <?php selected(strtoupper((string)$aq_raw['Order']),'ASC'); ?>>Stigende</option></select></div><div class="h18-field"><label><strong>Pr. side</strong></label><input type="number" min="1" max="50" name="aq_per_page" value="<?php echo esc_attr((int)$aq_raw['PerPage']); ?>" /></div></div>
                        <script id="h18-aq-schema" type="application/json"><?php echo wp_json_encode(['Fields'=>array_values($selected['Fields']),'Catalog'=>$this->dynamic_data_context_catalog_for_editor(),'Tags'=>array_map(static function($term){return ['slug'=>(string)$term->slug,'name'=>(string)$term->name];},(array)$aq_tags)],JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT); ?></script>
                        <div id="h18-aq-groups"></div><p><button type="button" class="button" id="h18-aq-add-group">+ Tilføj gruppe</button></p><p><button type="submit" class="button button-primary">Kør Advanced preview</button></p>
                    </form>
                    <?php if($advanced_preview):?><div class="h18-data-query-preview"><?php if($aq_error!==''):?><div class="notice notice-error inline"><p><?php echo esc_html($aq_error); ?></p></div><?php else:?><p><strong><?php echo esc_html((int)$aq_result['Total']); ?> resultat(er)</strong> · side <?php echo esc_html((int)$aq_result['Page']); ?>/<?php echo esc_html((int)$aq_result['TotalPages']); ?><?php echo !empty($aq_result['Truncated'])?' · kandidatgrænse nået':''; ?></p><table class="widefat striped"><thead><tr><th>ID</th><th>Titel</th></tr></thead><tbody><?php foreach($aq_result['Posts'] as $aq_post):?><tr><td><?php echo esc_html((int)$aq_post->ID); ?></td><td><?php echo esc_html($aq_post->post_title); ?></td></tr><?php endforeach;?></tbody></table><p><strong>Frontend:</strong> <code><?php echo esc_html($this->advanced_data_query_shortcode($aq_normalized)); ?></code></p><?php endif;?></div><?php endif;?>
                </section>


                <?php if ($can_schema) : ?><details class="h18-panel h18-data-schema-details"><summary><strong>Redigér datatype-schema</strong></summary>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" class="h18-data-schema-form">
                        <?php wp_nonce_field('h18_save_data_type'); ?><input type="hidden" name="action" value="h18_save_data_type" /><input type="hidden" name="existing_key" value="<?php echo esc_attr($selected['Key']); ?>" />
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field"><label><strong>Nøgle</strong></label><input type="text" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" readonly /></div>
                            <div class="h18-field"><label><strong>Navn – ental</strong></label><input type="text" name="data_type_singular" value="<?php echo esc_attr($selected['SingularLabel']); ?>" required /></div>
                            <div class="h18-field"><label><strong>Navn – flertal</strong></label><input type="text" name="data_type_plural" value="<?php echo esc_attr($selected['PluralLabel']); ?>" /></div>
                        </div>
                        <h3>Felter</h3><div id="h18-data-schema-fields" class="h18-data-schema-fields"><?php foreach ($selected['Fields'] as $field_index => $field) { $this->render_data_schema_field_row($field, $field_index); } ?></div>
                        <button type="button" class="button" id="h18-data-add-field">+ Tilføj felt</button>
                        <p><button type="submit" class="button button-primary">Gem schema</button></p>
                    </form>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" onsubmit="return confirm('Slet datatypen? Den kan kun slettes uden entries.');"><?php wp_nonce_field('h18_delete_data_type'); ?><input type="hidden" name="action" value="h18_delete_data_type" /><input type="hidden" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" /><button type="submit" class="button-link-delete">Slet datatype</button></form>
                </details><?php endif; ?>

                <div class="h18-data-layout">
                    <section class="h18-panel h18-data-entry-list"><h3><?php echo esc_html($selected['PluralLabel']); ?></h3>
                        <?php if (!$entries) : ?><p class="description">Ingen entries endnu.</p><?php else : ?><table class="widefat striped"><thead><tr><th>Titel</th><th>Ændret</th><th></th></tr></thead><tbody><?php foreach ($entries as $item) : ?><tr><td><strong><?php echo esc_html($item->post_title); ?></strong></td><td><?php echo esc_html(get_post_modified_time('Y-m-d H:i', false, $item)); ?></td><td><a class="button button-small" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($selected['Key']) . '&entry_id=' . (int) $item->ID . '#h18-data-entry-form')); ?>">Redigér</a></td></tr><?php endforeach; ?></tbody></table><?php endif; ?>
                    </section>
                    <section id="h18-data-entry-form" class="h18-panel h18-data-entry-form"><h3><?php echo $entry ? 'Redigér ' : 'Ny '; ?><?php echo esc_html($selected['SingularLabel']); ?></h3>
                        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>"><?php wp_nonce_field('h18_save_data_entry'); ?><input type="hidden" name="action" value="h18_save_data_entry" /><input type="hidden" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="entry_id" value="<?php echo esc_attr($entry ? $entry->ID : 0); ?>" />
                            <div class="h18-field"><label><strong>Titel</strong></label><input type="text" name="entry_title" value="<?php echo esc_attr($entry ? $entry->post_title : ''); ?>" required /></div>
                            <div class="h18-field"><label><strong>Data Tags</strong><small>Taxonomy · kommasepareret</small></label><input type="text" name="data_tags" value="<?php echo esc_attr(implode(', ', array_map('strval',(array)$entry_tags))); ?>" placeholder="fx aktiv, nordjylland" /></div>
                            <?php foreach ($selected['Fields'] as $field) : $value = $entry ? ($entry_values[$field['Key']] ?? '') : ''; ?><div class="h18-field"><label><strong><?php echo esc_html($field['Label']); ?><?php echo !empty($field['Required']) && $field['Type'] !== 'bool' ? ' *' : ''; ?></strong><small><?php echo esc_html($this->custom_data_field_types()[$field['Type']] ?? $field['Type']); ?></small></label><?php $this->render_custom_data_field_input($field, $value); ?></div><?php endforeach; ?>
                            <p><button type="submit" class="button button-primary">Gem entry</button></p>
                        </form>
                        <?php if ($entry) : ?><form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" onsubmit="return confirm('Slet denne entry permanent?');"><?php wp_nonce_field('h18_delete_data_entry'); ?><input type="hidden" name="action" value="h18_delete_data_entry" /><input type="hidden" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="entry_id" value="<?php echo esc_attr($entry->ID); ?>" /><button type="submit" class="button-link-delete">Slet entry</button></form><?php endif; ?>
                    </section>
                </div>
            <?php endif; ?>
            <template id="h18-data-field-template"><?php $this->render_data_schema_field_row($blank_field, '__INDEX__'); ?></template>
        </div>
        <?php
    }

    private function render_data_schema_field_row(array $field, $index) {
        $prefix = 'data_fields[' . $index . ']';
        ?>
        <div class="h18-data-field-row" data-field-index="<?php echo esc_attr($index); ?>">
            <span class="dashicons dashicons-move h18-data-field-drag" title="Flyt felt"></span>
            <div class="h18-field"><label><strong>Nøgle</strong></label><input class="h18-data-field-key" type="text" name="<?php echo esc_attr($prefix); ?>[Key]" value="<?php echo esc_attr($field['Key']); ?>" required /></div>
            <div class="h18-field"><label><strong>Navn</strong></label><input class="h18-data-field-label" type="text" name="<?php echo esc_attr($prefix); ?>[Label]" value="<?php echo esc_attr($field['Label']); ?>" required /></div>
            <div class="h18-field"><label><strong>Type</strong></label><select class="h18-data-field-type" name="<?php echo esc_attr($prefix); ?>[Type]"><?php foreach ($this->custom_data_field_types() as $type_key => $type_label) : ?><option value="<?php echo esc_attr($type_key); ?>" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option><?php endforeach; ?></select></div>
            <label class="h18-data-required"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[Required]" value="1" <?php checked(!empty($field['Required'])); ?> /> Obligatorisk</label>
            <div class="h18-field h18-data-relation-config"><label><strong>Mål-datatype</strong></label><select name="<?php echo esc_attr($prefix); ?>[RelationTargetType]"><option value="">Vælg datatype</option><?php foreach ($this->get_custom_data_types() as $target_key => $target_type) : ?><option value="<?php echo esc_attr($target_key); ?>" <?php selected((string)($field['RelationTargetType']??''),$target_key); ?>><?php echo esc_html($target_type['PluralLabel']); ?></option><?php endforeach; ?></select></div>
            <div class="h18-field h18-data-nested-config"><label><strong>Underfelter</strong></label><textarea name="<?php echo esc_attr($prefix); ?>[NestedSchemaText]" rows="4" placeholder="key|Navn|text|required"><?php echo esc_textarea($this->custom_data_nested_schema_text((array)($field['NestedFields']??[]))); ?></textarea><small>Én linje pr. felt: key|Navn|text|required. Tilladt: text, number, bool, date, media.</small></div>
            <div class="h18-field h18-data-repeater-config"><label><strong>Maks. rækker</strong></label><input type="number" min="1" max="20" name="<?php echo esc_attr($prefix); ?>[RepeaterMaxItems]" value="<?php echo esc_attr((int)($field['RepeaterMaxItems']??10)); ?>" /></div>
            <input class="h18-data-field-remove" type="hidden" name="<?php echo esc_attr($prefix); ?>[Remove]" value="0" />
            <button type="button" class="button-link-delete h18-data-remove-field">Fjern</button>
        </div>
        <?php
    }




    /* ================================================================
       DYNAMIC BINDING ENGINE — v0.5.24 / E5 UD-053
       ================================================================ */

    private function dynamic_binding_property_types() {
        return [
            'Title' => ['text','number','bool','date'],
            'Content' => ['text','number','bool','date'],
            'MediaId' => ['media'],
            'Button1Label' => ['text','number','bool','date'],
            'Button1Url' => ['text'],
            'Button2Label' => ['text','number','bool','date'],
            'Button2Url' => ['text'],
        ];
    }

    private function normalize_dynamic_bindings($raw) {
        if (is_string($raw) && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) { $raw = $decoded; }
        }
        if (!is_array($raw)) { return []; }
        $allowed = $this->dynamic_binding_property_types();
        $bindings = [];
        foreach ($raw as $property => $field_key) {
            $property = (string) $property;
            if (!isset($allowed[$property])) { continue; }
            $field_key = sanitize_key((string) $field_key);
            if ($field_key === '') { continue; }
            $bindings[$property] = $field_key;
        }
        return $bindings;
    }

    private function dynamic_binding_formatters() {
        return [
            'Auto'=>'Automatisk',
            'Text'=>'Tekst',
            'Upper'=>'STORE BOGSTAVER',
            'Lower'=>'små bogstaver',
            'Number0'=>'Tal · 0 decimaler',
            'Number1'=>'Tal · 1 decimal',
            'Number2'=>'Tal · 2 decimaler',
            'DateShort'=>'Dato · 31.12.2026',
            'DateIso'=>'Dato · 2026-12-31',
            'DateLong'=>'Dato · 31. december 2026',
            'BoolYesNo'=>'Ja / Nej',
        ];
    }

    private function normalize_dynamic_binding_options($raw) {
        if (is_string($raw) && $raw !== '') {
            $decoded=json_decode($raw,true); if(is_array($decoded))$raw=$decoded;
        }
        if(!is_array($raw))return[];
        $properties=$this->dynamic_binding_property_types();$formatters=$this->dynamic_binding_formatters();$out=[];
        foreach($raw as $property=>$option){
            $property=(string)$property;if(!isset($properties[$property])||!is_array($option))continue;
            $formatter=(string)($option['Formatter']??'Auto');if(!isset($formatters[$formatter]))$formatter='Auto';
            $fallback_mode=(string)($option['FallbackMode']??'Static');if(!in_array($fallback_mode,['Static','Custom','Empty'],true))$fallback_mode='Static';
            $fallback=sanitize_text_field((string)($option['Fallback']??''));if(strlen($fallback)>2000)$fallback=substr($fallback,0,2000);
            $prefix=sanitize_text_field((string)($option['Prefix']??''));if(strlen($prefix)>100)$prefix=substr($prefix,0,100);
            $suffix=sanitize_text_field((string)($option['Suffix']??''));if(strlen($suffix)>100)$suffix=substr($suffix,0,100);
            $out[$property]=['Formatter'=>$formatter,'FallbackMode'=>$fallback_mode,'Fallback'=>$fallback,'FallbackWhenEmpty'=>!empty($option['FallbackWhenEmpty']),'Prefix'=>$prefix,'Suffix'=>$suffix];
        }
        return$out;
    }

    private function dynamic_binding_option_for_property(array $options,$property) {
        return isset($options[$property])&&is_array($options[$property])?$options[$property]:['Formatter'=>'Auto','FallbackMode'=>'Static','Fallback'=>'','FallbackWhenEmpty'=>false,'Prefix'=>'','Suffix'=>''];
    }

    private function dynamic_binding_value_is_empty($value,$field_type='') {
        if($value===null||$value==='')return true;
        if(is_array($value)&&!$value)return true;
        if($field_type==='media'&&absint($value)<=0)return true;
        return false;
    }

    private function dynamic_binding_format_value($value,$field_type,$formatter) {
        $formatter=(string)$formatter;$field_type=(string)$field_type;
        if($formatter==='Auto')return $this->dynamic_binding_text_value($value);
        if($formatter==='Text')return $this->dynamic_binding_text_value($value);
        if($formatter==='Upper'||$formatter==='Lower'){
            if(!in_array($field_type,['text','number','bool','date'],true))return null;$text=$this->dynamic_binding_text_value($value);
            if($formatter==='Upper')return function_exists('mb_strtoupper')?mb_strtoupper($text,'UTF-8'):strtoupper($text);
            return function_exists('mb_strtolower')?mb_strtolower($text,'UTF-8'):strtolower($text);
        }
        if(in_array($formatter,['Number0','Number1','Number2'],true)){
            if(!is_numeric($value))return null;$decimals=(int)substr($formatter,-1);return number_format_i18n((float)$value,$decimals);
        }
        if(in_array($formatter,['DateShort','DateIso','DateLong'],true)){
            $raw=trim((string)$value);$date=DateTimeImmutable::createFromFormat('!Y-m-d',$raw,wp_timezone());$errors=DateTimeImmutable::getLastErrors();
            if(!$date||($errors!==false&&(((int)($errors['warning_count']??0))>0||((int)($errors['error_count']??0))>0))||$date->format('Y-m-d')!==$raw)return null;
            $format=$formatter==='DateShort'?'d.m.Y':($formatter==='DateIso'?'Y-m-d':'j. F Y');return wp_date($format,$date->getTimestamp(),wp_timezone());
        }
        if($formatter==='BoolYesNo')return $this->bool_value($value,false)?'Ja':'Nej';
        return null;
    }

    private function apply_dynamic_binding_output(array &$section,$property,$value) {
        if($property==='MediaId'){$section[$property]=absint($value);return;}
        $text=is_scalar($value)?(string)$value:'';
        if(in_array($property,['Button1Url','Button2Url'],true))$section[$property]=esc_url_raw($text);
        elseif($property==='Content')$section[$property]=wp_kses_post($text);
        else $section[$property]=sanitize_text_field($text);
    }

    private function apply_dynamic_binding_fallback(array &$section,$property,array $option) {
        $mode=(string)($option['FallbackMode']??'Static');if($mode==='Static')return;
        if($mode==='Empty'){$this->apply_dynamic_binding_output($section,$property,$property==='MediaId'?0:'');return;}
        $fallback=(string)($option['Fallback']??'');$this->apply_dynamic_binding_output($section,$property,$fallback);
    }

    private function dynamic_data_context_catalog_for_editor() {
        $types = $this->get_custom_data_types();
        $catalog = [];
        foreach ($types as $type_key => $type) {
            $catalog[$type_key] = [
                'Key' => $type_key,
                'SingularLabel' => (string) $type['SingularLabel'],
                'PluralLabel' => (string) $type['PluralLabel'],
                'Fields' => array_values((array) $type['Fields']),
                'Entries' => [],
            ];
        }
        if (!$catalog) { return []; }
        $entries = get_posts([
            'post_type' => self::DATA_ENTRY_POST_TYPE,
            'post_status' => ['publish','draft','private'],
            'posts_per_page' => 500,
            'orderby' => 'modified',
            'order' => 'DESC',
            'no_found_rows' => true,
        ]);
        foreach ($entries as $entry) {
            if (!$entry instanceof WP_Post) { continue; }
            $type_key = sanitize_key((string) get_post_meta($entry->ID, '_h18_data_type', true));
            if ($type_key === '' || !isset($catalog[$type_key]) || count($catalog[$type_key]['Entries']) >= 100) { continue; }
            $schema = $types[$type_key];
            $values = $this->custom_data_entry_values($entry->ID, $schema);
            $media_urls = [];
            foreach ($schema['Fields'] as $field) {
                if (($field['Type'] ?? '') !== 'media') { continue; }
                $field_key = (string) $field['Key'];
                $media_id = absint($values[$field_key] ?? 0);
                $url = $media_id ? wp_get_attachment_image_url($media_id, 'medium') : '';
                $media_urls[$field_key] = $url ? esc_url_raw($url) : '';
            }
            $catalog[$type_key]['Entries'][] = [
                'Id' => (int) $entry->ID,
                'Title' => (string) $entry->post_title,
                'Values' => $values,
                'MediaUrls' => $media_urls,
            ];
        }
        return array_values($catalog);
    }

    private function resolve_dynamic_data_context($type_key, $entry_id) {
        $type_key = sanitize_key((string) $type_key);
        $entry_id = absint($entry_id);
        if ($type_key === '' || $entry_id <= 0) { return null; }
        $types = $this->get_custom_data_types();
        if (!isset($types[$type_key])) { return null; }
        $entry = $this->custom_data_entry_for_type($entry_id, $type_key);
        if (!$entry instanceof WP_Post) { return null; }
        $field_map = [];
        foreach ($types[$type_key]['Fields'] as $field) {
            $field_map[(string) $field['Key']] = $field;
        }
        return [
            'TypeKey' => $type_key,
            'EntryId' => $entry_id,
            'EntryTitle' => (string) $entry->post_title,
            'Schema' => $types[$type_key],
            'Fields' => $field_map,
            'Values' => $this->custom_data_entry_values($entry_id, $types[$type_key]),
        ];
    }

    private function dynamic_binding_text_value($value) {
        if (is_bool($value)) { return $value ? 'Ja' : 'Nej'; }
        if (is_scalar($value)) { return (string) $value; }
        return '';
    }

    private function apply_dynamic_bindings_to_section(array $section, array $context) {
        $bindings=$this->normalize_dynamic_bindings($section['Bindings']??[]);if(!$bindings)return$section;
        $options=$this->normalize_dynamic_binding_options($section['BindingOptions']??[]);$property_types=$this->dynamic_binding_property_types();$fields=isset($context['Fields'])&&is_array($context['Fields'])?$context['Fields']:[];$values=isset($context['Values'])&&is_array($context['Values'])?$context['Values']:[];
        foreach($bindings as $property=>$field_key){
            $option=$this->dynamic_binding_option_for_property($options,$property);$resolved=false;
            if(isset($fields[$field_key])&&array_key_exists($field_key,$values)){
                $field_type=(string)($fields[$field_key]['Type']??'');
                if(in_array($field_type,$property_types[$property]??[],true)){
                    $value=$values[$field_key];$empty=$this->dynamic_binding_value_is_empty($value,$field_type);
                    if(!$empty||empty($option['FallbackWhenEmpty'])){
                        if($property==='MediaId'){$formatted=absint($value);$resolved=true;}
                        else{$formatted=$this->dynamic_binding_format_value($value,$field_type,(string)$option['Formatter']);if($formatted!==null){if(!in_array($property,['Button1Url','Button2Url'],true))$formatted=(string)$option['Prefix'].$formatted.(string)$option['Suffix'];$resolved=true;}}
                        if($resolved)$this->apply_dynamic_binding_output($section,$property,$formatted);
                    }
                }
            }
            if(!$resolved)$this->apply_dynamic_binding_fallback($section,$property,$option);
        }
        return$section;
    }



    /* ================================================================
       CONDITIONAL VISIBILITY ENGINE — v0.5.27 / E5 UD-058
       ================================================================ */

    private function normalize_page_conditions($raw) {
        if (is_string($raw) && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) { $raw = $decoded; }
        }
        if (!is_array($raw)) { return []; }
        $allowed = [
            'data' => ['empty','not_empty','eq','neq','gt','gte','lt','lte'],
            'user' => ['logged_in','logged_out','role','capability'],
            'date' => ['before','after','between'],
        ];
        $conditions = [];
        foreach (array_slice(array_values($raw), 0, 8) as $index => $item) {
            if (!is_array($item)) { continue; }
            $type = sanitize_key((string) ($item['Type'] ?? ''));
            $operator = sanitize_key((string) ($item['Operator'] ?? ''));
            if (!isset($allowed[$type]) || !in_array($operator, $allowed[$type], true)) { continue; }
            $field = sanitize_key((string) ($item['Field'] ?? ''));
            $value = sanitize_text_field((string) ($item['Value'] ?? ''));
            $value2 = sanitize_text_field((string) ($item['Value2'] ?? ''));
            if (strlen($value) > 300) { $value = substr($value, 0, 300); }
            if (strlen($value2) > 300) { $value2 = substr($value2, 0, 300); }
            if ($type === 'data' && $field === '') { continue; }
            if ($type === 'user' && in_array($operator, ['role','capability'], true)) {
                $value = sanitize_key($value);
                if ($value === '') { continue; }
            }
            if ($type === 'date') {
                if (!$this->page_condition_datetime_timestamp($value)) { continue; }
                if ($operator === 'between' && !$this->page_condition_datetime_timestamp($value2)) { continue; }
            }
            $id = sanitize_key((string) ($item['Id'] ?? ''));
            if ($id === '') { $id = 'condition-' . ($index + 1); }
            $conditions[] = [
                'Id' => $id,
                'Type' => $type,
                'Operator' => $operator,
                'Field' => $field,
                'Value' => $value,
                'Value2' => $value2,
            ];
        }
        return $conditions;
    }

    private function page_condition_datetime_timestamp($value) {
        $value = trim((string) $value);
        if ($value === '') { return 0; }
        $timezone = wp_timezone();
        $formats = ['!Y-m-d\TH:i', '!Y-m-d H:i', '!Y-m-d'];
        foreach ($formats as $format) {
            $date = DateTimeImmutable::createFromFormat($format, $value, $timezone);
            if ($date instanceof DateTimeImmutable) {
                $errors = DateTimeImmutable::getLastErrors();
                if ($errors === false || (((int) ($errors['warning_count'] ?? 0)) === 0 && ((int) ($errors['error_count'] ?? 0)) === 0)) {
                    $roundtrip = $date->format(str_replace('!', '', $format));
                    if ($roundtrip === $value) { return $date->getTimestamp(); }
                }
            }
        }
        return 0;
    }

    private function page_condition_value_is_empty($value, $field_type = '') {
        if ($value === null || $value === '') { return true; }
        if (is_array($value) && !$value) { return true; }
        if ($field_type === 'media' && absint($value) <= 0) { return true; }
        return false;
    }

    private function evaluate_page_condition(array $condition, $context = null, $timestamp = null) {
        $type = (string) ($condition['Type'] ?? '');
        $operator = (string) ($condition['Operator'] ?? '');
        if ($type === 'data') {
            $field_key = sanitize_key((string) ($condition['Field'] ?? ''));
            $fields = is_array($context) && isset($context['Fields']) && is_array($context['Fields']) ? $context['Fields'] : [];
            $values = is_array($context) && isset($context['Values']) && is_array($context['Values']) ? $context['Values'] : [];
            $field_type = isset($fields[$field_key]) ? (string) ($fields[$field_key]['Type'] ?? '') : '';
            $exists = $field_key !== '' && isset($fields[$field_key]) && array_key_exists($field_key, $values);
            $actual = $exists ? $values[$field_key] : null;
            $empty = !$exists || $this->page_condition_value_is_empty($actual, $field_type);
            if ($operator === 'empty') { return $empty; }
            if ($operator === 'not_empty') { return !$empty; }
            if (!$exists) { return false; }
            $expected = (string) ($condition['Value'] ?? '');
            if ($field_type === 'bool') {
                $actual = $this->bool_value($actual, false) ? 1 : 0;
                $expected = $this->bool_value($expected, false) ? 1 : 0;
            } elseif ($field_type === 'number' || (is_numeric($actual) && is_numeric($expected))) {
                $actual = (float) $actual;
                $expected = (float) $expected;
            } elseif ($field_type === 'date') {
                $actual_ts = $this->page_condition_datetime_timestamp((string) $actual);
                $expected_ts = $this->page_condition_datetime_timestamp((string) $expected);
                if (!$actual_ts || !$expected_ts) { return false; }
                $actual = $actual_ts;
                $expected = $expected_ts;
            } else {
                $actual = (string) $actual;
                $expected = (string) $expected;
            }
            if ($operator === 'eq') { return $actual == $expected; }
            if ($operator === 'neq') { return $actual != $expected; }
            if ($operator === 'gt') { return $actual > $expected; }
            if ($operator === 'gte') { return $actual >= $expected; }
            if ($operator === 'lt') { return $actual < $expected; }
            if ($operator === 'lte') { return $actual <= $expected; }
            return false;
        }
        if ($type === 'user') {
            if ($operator === 'logged_in') { return is_user_logged_in(); }
            if ($operator === 'logged_out') { return !is_user_logged_in(); }
            $value = sanitize_key((string) ($condition['Value'] ?? ''));
            if ($operator === 'role') {
                $user = wp_get_current_user();
                return $value !== '' && in_array($value, array_map('sanitize_key', (array) $user->roles), true);
            }
            if ($operator === 'capability') { return $value !== '' && current_user_can($value); }
            return false;
        }
        if ($type === 'date') {
            $now = $timestamp === null ? time() : (int) $timestamp;
            $first = $this->page_condition_datetime_timestamp((string) ($condition['Value'] ?? ''));
            if (!$first) { return false; }
            if ($operator === 'before') { return $now < $first; }
            if ($operator === 'after') { return $now > $first; }
            if ($operator === 'between') {
                $second = $this->page_condition_datetime_timestamp((string) ($condition['Value2'] ?? ''));
                if (!$second) { return false; }
                $min = min($first, $second); $max = max($first, $second);
                return $now >= $min && $now <= $max;
            }
        }
        return false;
    }

    private function evaluate_page_conditions(array $section, $context = null, $timestamp = null) {
        $conditions = $this->normalize_page_conditions($section['Conditions'] ?? []);
        if (!$conditions) { return true; }
        $mode = (string) ($section['ConditionMode'] ?? 'All');
        if (!in_array($mode, ['All','Any'], true)) { $mode = 'All'; }
        if ($mode === 'Any') {
            foreach ($conditions as $condition) {
                if ($this->evaluate_page_condition($condition, $context, $timestamp)) { return true; }
            }
            return false;
        }
        foreach ($conditions as $condition) {
            if (!$this->evaluate_page_condition($condition, $context, $timestamp)) { return false; }
        }
        return true;
    }


    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */

    private function editable_page_definitions() {
        $definitions = [
            self::HOME_SLUG => 'Hjem',
            'om-foreningen' => 'Om foreningen',
            'bliv-medlem'   => 'Bliv medlem',
            'kontakt'       => 'Kontakt',
        ];
        $managed = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish','draft','private'],
            'posts_per_page' => -1,
            'meta_key' => '_h18_page_editor_managed',
            'meta_value' => '1',
            'orderby' => 'title',
            'order' => 'ASC',
        ]);
        foreach ($managed as $page) {
            if (!$page instanceof WP_Post || $page->post_name === '') { continue; }
            if (!isset($definitions[$page->post_name])) { $definitions[$page->post_name] = $page->post_title; }
        }
        return $definitions;
    }

    private function page_section_type_labels() {
        return [
            'hero'       => 'Topbanner / hero',
            'text'       => 'Tekst',
            'text_image' => 'Tekst og billede',
            'image'      => 'Stort billede',
            'buttons'    => 'Handlingsknapper',
            'card'       => 'Indholdskort',
            'card_grid'  => 'Kort-række / kolonner',
            'highlight'  => 'Fremhævet tekst',
            'icon'       => 'Ikon / SVG',
            'divider'    => 'Skillelinje',
            'list'       => 'Liste',
            'badge'      => 'Badge / mærkat',
            'quote'      => 'Citat',
            'tabs'       => 'Faner / tabs',
            'accordion'  => 'Accordion',
            'carousel'   => 'Carousel / slider',
            'container'  => 'Container',
            'flex'       => 'Flex container',
            'grid'       => 'Grid container',
            'query_list' => 'Repeater / Query list',
            'component'  => 'Linked component',
            'embed'      => 'Embed / medie-URL',
            'shortcode'  => 'Shortcode (avanceret)',
            'spacer'     => 'Afstand',
            'html'       => 'Importeret blok / HTML',
            'css'        => 'Side-CSS (avanceret)',
            'mail_form'  => 'Mailformular',
            'poll'       => 'Afstemning',
            'legacy'     => 'Eksisterende indhold',
        ];
    }

    private function page_primitive_variant_options($type) {
        $type = sanitize_key((string) $type);
        $map = [
            'icon' => [
                'check' => 'Flueben', 'star' => 'Stjerne', 'info' => 'Info', 'location' => 'Placering',
                'calendar' => 'Kalender', 'phone' => 'Telefon', 'mail' => 'E-mail', 'wrench' => 'Værktøj',
                'shield' => 'Skjold', 'arrow' => 'Pil',
            ],
            'divider' => ['solid' => 'Hel linje', 'dashed' => 'Stiplet', 'dotted' => 'Prikket', 'double' => 'Dobbelt'],
            'list' => ['bullets' => 'Punkter', 'numbers' => 'Numre', 'checks' => 'Flueben'],
            'badge' => ['solid' => 'Fyldt', 'outline' => 'Outline'],
            'quote' => ['standard' => 'Standard', 'large' => 'Stort citat'],
        ];
        return $map[$type] ?? ['default' => 'Standard'];
    }

    private function page_editor_safe_icon_svg($name) {
        $name = sanitize_key((string) $name);
        $icons = [
            'check' => '<path d="M20 6 9 17l-5-5"/>',
            'star' => '<path d="m12 2 3.1 6.3 6.9 1-5 4.8 1.2 6.9-6.2-3.3L5.8 21 7 14.1l-5-4.8 6.9-1Z"/>',
            'info' => '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
            'location' => '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
            'calendar' => '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
            'phone' => '<path d="M5 3h4l2 5-2.5 1.8a15 15 0 0 0 5.7 5.7L16 13l5 2v4c0 1.1-.9 2-2 2C10.2 21 3 13.8 3 5c0-1.1.9-2 2-2Z"/>',
            'mail' => '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
            'wrench' => '<path d="M14.5 6.5a4 4 0 0 0-5-5L7 4l3 3-3 3-3-3-2.5 2.5a4 4 0 0 0 5 5L15 23l3-3-8.5-8.5a4 4 0 0 0 5-5Z"/>',
            'shield' => '<path d="M12 2 20 5v6c0 5.2-3.4 9.8-8 11-4.6-1.2-8-5.8-8-11V5Z"/><path d="m8 12 2.5 2.5L16 9"/>',
            'arrow' => '<path d="M5 12h14M14 7l5 5-5 5"/>',
        ];
        $shape = $icons[$name] ?? $icons['check'];
        return '<svg class="h18-safe-icon-svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' . $shape . '</svg>';
    }

    private function page_editor_carousel_script($section_id) {
        $root_json = wp_json_encode((string) $section_id);
        return '<script>(function(){' .
            'var section=document.getElementById(' . $root_json . ');if(!section)return;var root=section.querySelector(".h18-editor-carousel");if(!root)return;' .
            'var slides=Array.prototype.slice.call(root.querySelectorAll(".h18-editor-carousel-slide"));var dots=Array.prototype.slice.call(root.querySelectorAll(".h18-editor-carousel-dot"));var prev=root.querySelector(".h18-editor-carousel-prev");var next=root.querySelector(".h18-editor-carousel-next");var status=root.querySelector(".h18-editor-carousel-status");if(!slides.length)return;' .
            'var index=0;var timer=null;var startX=null;var loop=root.dataset.loop==="1";var autoplay=root.dataset.autoplay==="1";var interval=Math.max(2000,parseInt(root.dataset.interval||"5000",10)||5000);var reduced=window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;' .
            'function normalize(i){if(loop)return(i+slides.length)%slides.length;return Math.max(0,Math.min(slides.length-1,i));}' .
            'function show(i,user){index=normalize(i);slides.forEach(function(slide,n){var on=n===index;slide.hidden=!on;slide.setAttribute("aria-hidden",on?"false":"true");});dots.forEach(function(dot,n){var on=n===index;dot.setAttribute("aria-current",on?"true":"false");dot.tabIndex=on?0:-1;});if(prev)prev.disabled=!loop&&index===0;if(next)next.disabled=!loop&&index===slides.length-1;if(status)status.textContent=(index+1)+" af "+slides.length;if(user)restart();}' .
            'function advance(step,user){show(index+step,user);}' .
            'function stop(){if(timer){window.clearInterval(timer);timer=null;}}function restart(){stop();if(autoplay&&!reduced&&slides.length>1)timer=window.setInterval(function(){if(loop||index<slides.length-1)advance(1,false);else show(0,false);},interval);}' .
            'if(prev)prev.addEventListener("click",function(){advance(-1,true);});if(next)next.addEventListener("click",function(){advance(1,true);});dots.forEach(function(dot,n){dot.addEventListener("click",function(){show(n,true);});dot.addEventListener("keydown",function(e){var target=n;if(e.key==="ArrowRight")target=n+1;else if(e.key==="ArrowLeft")target=n-1;else if(e.key==="Home")target=0;else if(e.key==="End")target=dots.length-1;else return;e.preventDefault();show(target,true);dots[normalize(target)].focus();});});' .
            'root.addEventListener("keydown",function(e){if(e.target&&e.target.classList.contains("h18-editor-carousel-dot"))return;if(e.key==="ArrowRight"){e.preventDefault();advance(1,true);}else if(e.key==="ArrowLeft"){e.preventDefault();advance(-1,true);}});root.addEventListener("mouseenter",stop);root.addEventListener("mouseleave",restart);root.addEventListener("focusin",stop);root.addEventListener("focusout",function(e){if(!root.contains(e.relatedTarget))restart();});' .
            'root.addEventListener("touchstart",function(e){startX=e.touches&&e.touches[0]?e.touches[0].clientX:null;},{passive:true});root.addEventListener("touchend",function(e){if(startX===null)return;var end=e.changedTouches&&e.changedTouches[0]?e.changedTouches[0].clientX:startX;var dx=end-startX;startX=null;if(Math.abs(dx)>45)advance(dx<0?1:-1,true);},{passive:true});show(0,false);restart();' .
            '})();</script>';
    }

    private function page_editor_tabs_script($section_id) {
        $root_json = wp_json_encode((string) $section_id);
        return '<script>(function(){' .
            'var root=document.getElementById(' . $root_json . ');if(!root)return;' .
            'var tabs=Array.prototype.slice.call(root.querySelectorAll("[role=tab]"));' .
            'var panels=Array.prototype.slice.call(root.querySelectorAll("[role=tabpanel]"));if(!tabs.length)return;' .
            'function activate(index,focus){index=(index+tabs.length)%tabs.length;tabs.forEach(function(tab,i){var on=i===index;tab.setAttribute("aria-selected",on?"true":"false");tab.tabIndex=on?0:-1;});panels.forEach(function(panel,i){panel.hidden=i!==index;});if(focus)tabs[index].focus();}' .
            'tabs.forEach(function(tab,index){tab.addEventListener("click",function(){activate(index,false);});tab.addEventListener("keydown",function(e){var next=index;if(e.key==="ArrowRight"||e.key==="ArrowDown")next=index+1;else if(e.key==="ArrowLeft"||e.key==="ArrowUp")next=index-1;else if(e.key==="Home")next=0;else if(e.key==="End")next=tabs.length-1;else return;e.preventDefault();activate(next,true);});});activate(0,false);' .
            '})();</script>';
    }

    private function render_page_editor_list_primitive(array $section) {
        $content = trim((string) ($section['Content'] ?? ''));
        $variant = (string) ($section['PrimitiveVariant'] ?? 'bullets');
        if ($content === '') {
            return '';
        }
        if (preg_match('/<(?:ul|ol)\b/i', $content)) {
            $html = wp_kses_post($content);
            if ($variant === 'checks') {
                $html = preg_replace('/<ul\b/i', '<ul class="h18-editor-list-checks"', $html, 1);
            }
            return $html;
        }
        $plain = wp_strip_all_tags($content);
        $items = preg_split('/\r\n|\r|\n/', $plain);
        $items = array_values(array_filter(array_map('trim', (array) $items), static function($value) { return $value !== ''; }));
        if (!$items) { return ''; }
        $tag = $variant === 'numbers' ? 'ol' : 'ul';
        $class = $variant === 'checks' ? ' class="h18-editor-list-checks"' : '';
        $html = '<' . $tag . $class . '>';
        foreach (array_slice($items, 0, 100) as $item) {
            $html .= '<li>' . esc_html($item) . '</li>';
        }
        return $html . '</' . $tag . '>';
    }

    private function looks_like_page_css($content) {
        $content = trim((string) $content);
        return $content !== '' &&
            substr_count($content, '{') >= 2 &&
            substr_count($content, '}') >= 2 &&
            (bool) preg_match('/(?:^|\}|\s)(?:body|html|\.|#|@media)[^{]*\{/i', $content);
    }

    private function sanitize_page_section_css($css) {
        $css = html_entity_decode((string) $css, ENT_QUOTES, 'UTF-8');
        $css = (string) preg_replace('/<\/?style\b[^>]*>/i', '', $css);
        $css = (string) preg_replace('/@import\s+[^;]+;?/i', '', $css);
        $css = (string) preg_replace('/(?:expression|behavior|-moz-binding)\s*:/i', '', $css);
        $css = (string) preg_replace('/url\s*\(\s*["\']?\s*javascript\s*:/i', 'url(', $css);
        $css = str_ireplace(['</style', '<style'], '', $css);
        $css = (string) preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $css);
        return trim($css);
    }

    private function default_page_section($type = 'text', $order = 10) {
        $types = $this->page_section_type_labels();
        if (!isset($types[$type])) {
            $type = 'text';
        }

        return [
            'Key'                   => 'sektion-' . wp_generate_uuid4(),
            'Type'                  => $type,
            'Active'                => true,
            'NavigatorLabel'        => '',
            'NavigatorLocked'       => false,
            'ComponentId'           => '',
            'ComponentRevision'     => 0,
            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'Bindings'              => [],
            'BindingOptions'        => [],
            'ConditionMode'         => 'All',
            'Conditions'            => [],
            'QueryListType'         => '',
            'QueryListFilterField'  => '',
            'QueryListFilterOperator' => 'eq',
            'QueryListFilterValue'  => '',
            'QueryListSort'         => 'modified',
            'QueryListOrder'        => 'DESC',
            'QueryListLimit'        => 10,
            'QueryListComponentId'  => '',
            'QueryListComponentVariant' => '',
            'QueryListColumns'      => 1,
            'QueryListMobileColumns'=> 1,
            'QueryListGapPx'        => 18,
            'QueryListMobileGapPx'  => 14,
            'QueryListEmptyText'    => 'Ingen resultater.',
            'Order'                 => (int) $order,
            'Title'                 => '',
            'Content'               => '',
            'PrimitiveVariant'      => 'default',
            'AdvancedContentAuthorized' => false,
            'MediaId'               => 0,
            'MediaUrl'              => '',
            'ImagePosition'         => 'Right',
            'ImageAspectRatio'      => 'Auto',
            'ImageFit'              => 'Cover',
            'ImageFocalXPercent'    => 50,
            'ImageFocalYPercent'    => 50,
            'ImageHeightPx'         => 0,
            'MobileImageHeightPx'   => 0,
            'ElementWidthPercent'     => 100,
            'TabletWidthPercent'      => -1,
            'MobileWidthPercent'      => -1,
            'ElementMaxWidthPx'       => 0,
            'ElementMinHeightPx'      => 0,
            'TabletMinHeightPx'       => -1,
            'MobileMinHeightPx'       => -1,
            'ImageWidthPercent'       => 100,
            'MobileImageWidthPercent' => 100,
            'ImageMaxWidthPx'         => 0,
            'ImageAspectLocked'       => false,
            'Button1Label'          => '',
            'Button1Url'            => '',
            'Button2Label'          => '',
            'Button2Url'            => '',
            'RecipientEmail'        => sanitize_email((string) get_option('admin_email')),
            'SuccessMessage'        => 'Tak for din besked. Vi vender tilbage hurtigst muligt.',
            'StoreSubmissions'      => false,
            'ConsentLabel'          => '',
            'PollOptions'           => ['Ja', 'Nej'],
            'AllowMultiple'         => false,
            'ResultsMode'           => 'after_vote',
            'StartUtc'              => '',
            'EndUtc'                => '',
            'DesktopAlignment'      => 'Left',
            'MobileAlignment'       => 'Center',
            'Background'            => 'White',
            'Columns'               => 3,
            'MobileColumns'         => 1,
            'ColumnGapPx'           => 16,
            'MobileColumnGapPx'     => 14,
            'Cards'                 => [],
            'LayoutParentKey'       => '',
            'LayoutDirection'       => 'Row',
            'LayoutWrap'            => true,
            'LayoutJustify'         => 'Start',
            'LayoutAlign'           => 'Stretch',
            'LayoutGapPx'           => 16,
            'MobileLayoutGapPx'     => 12,
            'LayoutColumns'         => 2,
            'MobileLayoutColumns'   => 1,
            'MobileLayoutStack'     => true,
            'CarouselAutoplay'      => false,
            'CarouselIntervalMs'    => 5000,
            'CarouselLoop'          => true,
            'CarouselShowArrows'    => true,
            'CarouselShowDots'      => true,
            'TopSpacingPx'          => 0,
            'BottomSpacingPx'       => 24,
            'MobileTopSpacingPx'    => 0,
            'MobileBottomSpacingPx' => 18,
            'PaddingPx'             => 0,
            'HorizontalPaddingPx'   => 0,
            'MobilePaddingPx'       => 0,
            'MobileHorizontalPaddingPx' => 0,
            'RadiusPx'              => 7,
            'SpacerPx'              => 32,
            'MobileSpacerPx'        => 24,
            'HeroHeightPx'          => 320,
            'MobileHeroHeightPx'    => 220,
            'OverlayOpacityPercent' => 35,
            'DesignMode'             => 'Global',
            'CustomBackgroundColor'  => '#ffffff',
            'CustomTextColor'        => '#30382a',
            'CustomHeadingColor'     => '#30382a',
            'BorderWidthPx'          => 0,
            'CustomBorderColor'      => '#c3ae83',
            'ShadowStyle'            => 'None',
            'SectionBodyFontFamily' => 'Global',
            'SectionHeadingFontFamily' => 'Global',
            'BodyFontSizePx'         => 0,
            'H1FontSizePx'           => 0,
            'H2FontSizePx'           => 0,
            'H3FontSizePx'           => 0,
            'SectionOpacityPercent'  => 100,
            'BackgroundEffect'       => 'None',
            'GradientStartColor'     => '#30382a',
            'GradientEndColor'       => '#c3ae83',
            'GradientAngleDeg'       => 135,
            'BackgroundMediaId'      => 0,
            'BackgroundImageUrl'     => '',
            'BackgroundImagePosition'=> 'Center',
            'BackgroundImageSize'    => 'Cover',
            'RadiusTopLeftPx'        => -1,
            'RadiusTopRightPx'       => -1,
            'RadiusBottomRightPx'    => -1,
            'RadiusBottomLeftPx'     => -1,
            'HoverEffect'            => 'None',
            'HoverTransitionMs'      => 220,
            'HoverStyleMode'         => 'Inherit',
            'HoverBackgroundColor'   => '#ffffff',
            'HoverTextColor'         => '#30382a',
            'HoverHeadingColor'      => '#30382a',
            'HoverBorderColor'       => '#c3ae83',
            'HoverOpacityPercent'    => 100,
            'TransitionPreset'       => 'Inherit',
            'FocusRingStyle'         => 'Global',
            'FocusRingColor'         => '#8b4a2b',
            'FocusRingWidthPx'       => 3,
            'FocusRingOffsetPx'      => 2,
            'ActiveEffect'           => 'None',
            'DisabledOpacityPercent' => 55,
            'ShowDesktop'            => true,
            'ShowTablet'             => true,
            'ShowMobile'             => true,
            'TabletAlignment'        => 'Inherit',
            'TabletTopSpacingPx'     => -1,
            'TabletBottomSpacingPx'  => -1,
            'TabletPaddingPx'        => -1,
            'TabletHorizontalPaddingPx' => -1,
            'DesktopTranslateXPx'    => 0,
            'DesktopTranslateYPx'    => 0,
            'DesktopScalePercent'    => 100,
            'DesktopRotateDeg'       => 0,
            'TabletTranslateXPx'     => 0,
            'TabletTranslateYPx'     => 0,
            'TabletScalePercent'     => 100,
            'TabletRotateDeg'        => 0,
            'MobileTranslateXPx'     => 0,
            'MobileTranslateYPx'     => 0,
            'MobileScalePercent'     => 100,
            'MobileRotateDeg'        => 0,
            'ImportedGroupType'     => '',
            'LegacyHtml'            => '',
        ];
    }

    private function default_page_card($order = 10) {
        return [
            'Key'             => 'kort-' . wp_generate_uuid4(),
            'Active'          => true,
            'Order'           => (int) $order,
            'Title'           => '',
            'Content'         => '',
            'Background'      => 'OffWhite',
            'TextTone'        => 'Auto',
            'BorderColor'     => 'Sand',
            'BorderWidthPx'   => 0,
            'PaddingPx'       => 26,
            'MobilePaddingPx' => 20,
            'RadiusPx'        => 7,
            'DesktopAlignment'=> 'Left',
            'MobileAlignment' => 'Left',
        ];
    }

    private function normalize_page_card(array $raw, $index = 0) {
        $card = $this->default_page_card(((int) $index + 1) * 10);
        $key = sanitize_key((string) ($raw['Key'] ?? ''));
        if ($key === '') {
            $key = 'kort-' . substr(md5(wp_generate_uuid4()), 0, 12);
        }
        $background = (string) ($raw['Background'] ?? $card['Background']);
        if (!in_array($background, ['White', 'OffWhite', 'Sand', 'Olive', 'Steel'], true)) {
            $background = 'OffWhite';
        }
        $text_tone = (string) ($raw['TextTone'] ?? 'Auto');
        if (!in_array($text_tone, ['Auto', 'Dark', 'Light'], true)) {
            $text_tone = 'Auto';
        }
        $border_color = (string) ($raw['BorderColor'] ?? 'Sand');
        if (!in_array($border_color, ['None', 'Sand', 'Olive', 'Steel'], true)) {
            $border_color = 'Sand';
        }
        $desktop_alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
        if (!in_array($desktop_alignment, ['Left', 'Center'], true)) {
            $desktop_alignment = 'Left';
        }
        $mobile_alignment = (string) ($raw['MobileAlignment'] ?? 'Left');
        if (!in_array($mobile_alignment, ['Left', 'Center'], true)) {
            $mobile_alignment = 'Left';
        }

        return [
            'Key'              => $key,
            'Active'           => array_key_exists('Active', $raw) ? $this->bool_value($raw['Active'], false) : true,
            'Order'            => $this->clamp_int($raw['Order'] ?? $card['Order'], 1, 10000, $card['Order']),
            'Title'            => sanitize_text_field((string) ($raw['Title'] ?? '')),
            'Content'          => wp_kses_post((string) ($raw['Content'] ?? '')),
            'Background'       => $background,
            'TextTone'         => $text_tone,
            'BorderColor'      => $border_color,
            'BorderWidthPx'    => $this->clamp_int($raw['BorderWidthPx'] ?? 0, 0, 8, 0),
            'PaddingPx'        => $this->clamp_int($raw['PaddingPx'] ?? 26, 0, 80, 26),
            'MobilePaddingPx'  => $this->clamp_int($raw['MobilePaddingPx'] ?? 20, 0, 60, 20),
            'RadiusPx'         => $this->clamp_int($raw['RadiusPx'] ?? 7, 0, 30, 7),
            'DesktopAlignment' => $desktop_alignment,
            'MobileAlignment'  => $mobile_alignment,
        ];
    }

    private function normalize_page_section(array $raw, $index = 0, array $legacy_source = []) {
        $types = $this->page_section_type_labels();
        $type = sanitize_key((string) ($raw['Type'] ?? 'text'));
        if (!isset($types[$type])) {
            $type = 'text';
        }
        if (in_array($type, ['html', 'text'], true) && $this->looks_like_page_css((string) ($raw['Content'] ?? ''))) {
            $type = 'css';
        }

        $section = $this->default_page_section($type, ((int) $index + 1) * 10);
        $key = sanitize_key((string) ($raw['Key'] ?? ''));
        if ($key === '') {
            $key = 'sektion-' . substr(md5(wp_generate_uuid4()), 0, 12);
        }
        $navigator_label = sanitize_text_field((string) ($raw['NavigatorLabel'] ?? ''));
        $navigator_label = function_exists('mb_substr') ? mb_substr($navigator_label, 0, 80) : substr($navigator_label, 0, 80);
        $navigator_locked = array_key_exists('NavigatorLocked', $raw) ? $this->bool_value($raw['NavigatorLocked'], false) : false;
        $component_id = sanitize_key((string) ($raw['ComponentId'] ?? ''));
        $component_revision = max(0, (int) ($raw['ComponentRevision'] ?? 0));
        $component_variant = sanitize_key((string) ($raw['ComponentVariant'] ?? ''));
        $component_overrides_raw = $raw['ComponentOverrides'] ?? [];
        if ((!is_array($component_overrides_raw) || !$component_overrides_raw) && isset($raw['ComponentOverridesJson']) && is_string($raw['ComponentOverridesJson'])) {
            $decoded_component_overrides = json_decode((string) $raw['ComponentOverridesJson'], true);
            if (is_array($decoded_component_overrides)) { $component_overrides_raw = $decoded_component_overrides; }
        }
        $component_overrides = [];
        if (is_array($component_overrides_raw)) {
            foreach (array_slice($component_overrides_raw, 0, 40, true) as $override_id => $override_value) {
                $override_id = sanitize_key((string) $override_id);
                if ($override_id === '' || is_array($override_value) || is_object($override_value)) { continue; }
                $override_value = (string) $override_value;
                if (strlen($override_value) > 20000) { $override_value = substr($override_value, 0, 20000); }
                $component_overrides[$override_id] = wp_kses_post($override_value);
            }
        }
        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);
        $binding_options = $this->normalize_dynamic_binding_options($raw['BindingOptions'] ?? []);
        $condition_mode = (string) ($raw['ConditionMode'] ?? 'All');
        if (!in_array($condition_mode, ['All','Any'], true)) { $condition_mode = 'All'; }
        $conditions_raw = $raw['Conditions'] ?? [];
        if ((!is_array($conditions_raw) || !$conditions_raw) && isset($raw['ConditionsJson']) && is_string($raw['ConditionsJson'])) {
            $decoded_conditions = json_decode((string) $raw['ConditionsJson'], true);
            if (is_array($decoded_conditions)) { $conditions_raw = $decoded_conditions; }
        }
        $conditions = $this->normalize_page_conditions($conditions_raw);
        $query_list_type = sanitize_key((string) ($raw['QueryListType'] ?? ''));
        $query_list_filter_field = sanitize_key((string) ($raw['QueryListFilterField'] ?? ''));
        $query_list_filter_operator = sanitize_key((string) ($raw['QueryListFilterOperator'] ?? 'eq'));
        if (!in_array($query_list_filter_operator, ['eq','neq','contains','gt','gte','lt','lte','before','after'], true)) { $query_list_filter_operator = 'eq'; }
        $query_list_filter_value = sanitize_text_field((string) ($raw['QueryListFilterValue'] ?? ''));
        if (strlen($query_list_filter_value) > 500) { $query_list_filter_value = substr($query_list_filter_value, 0, 500); }
        $query_list_sort_raw = (string) ($raw['QueryListSort'] ?? 'modified');
        if (in_array($query_list_sort_raw, ['title','modified','created'], true)) { $query_list_sort = $query_list_sort_raw; }
        elseif (strpos($query_list_sort_raw, 'field:') === 0) { $query_list_sort = 'field:' . sanitize_key(substr($query_list_sort_raw, 6)); }
        else { $query_list_sort = 'modified'; }
        $query_list_order = strtoupper((string) ($raw['QueryListOrder'] ?? 'DESC'));
        if (!in_array($query_list_order, ['ASC','DESC'], true)) { $query_list_order = 'DESC'; }
        $query_list_component_id = sanitize_key((string) ($raw['QueryListComponentId'] ?? ''));
        $query_list_component_variant = sanitize_key((string) ($raw['QueryListComponentVariant'] ?? ''));
        $query_list_empty_text = sanitize_text_field((string) ($raw['QueryListEmptyText'] ?? 'Ingen resultater.'));
        if ($query_list_empty_text === '') { $query_list_empty_text = 'Ingen resultater.'; }

        $alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
        if (!in_array($alignment, ['Left', 'Center'], true)) {
            $alignment = 'Left';
        }
        $mobile_alignment = (string) ($raw['MobileAlignment'] ?? 'Center');
        if (!in_array($mobile_alignment, ['Left', 'Center'], true)) {
            $mobile_alignment = 'Center';
        }
        $background = (string) ($raw['Background'] ?? 'White');
        if (!in_array($background, ['White', 'OffWhite', 'Olive', 'Sand', 'Steel'], true)) {
            $background = 'White';
        }
        $image_position = (string) ($raw['ImagePosition'] ?? 'Right');
        if (!in_array($image_position, ['Left', 'Right'], true)) {
            $image_position = 'Right';
        }
        $image_aspect = (string) ($raw['ImageAspectRatio'] ?? 'Auto');
        if (!in_array($image_aspect, ['Auto', '1:1', '4:3', '3:2', '16:9'], true)) {
            $image_aspect = 'Auto';
        }
        $image_fit = (string) ($raw['ImageFit'] ?? 'Cover');
        if (!in_array($image_fit, ['Cover', 'Contain'], true)) {
            $image_fit = 'Cover';
        }
        $results_mode = (string) ($raw['ResultsMode'] ?? 'after_vote');
        if (!in_array($results_mode, ['always', 'after_vote', 'after_close'], true)) {
            $results_mode = 'after_vote';
        }

        $poll_options = $raw['PollOptions'] ?? $section['PollOptions'];
        if (is_string($poll_options)) {
            $poll_options = preg_split('/\r\n|\r|\n/', $poll_options);
        }
        if (!is_array($poll_options)) {
            $poll_options = $section['PollOptions'];
        }
        $clean_options = [];
        foreach (array_slice($poll_options, 0, 20) as $option) {
            $option = sanitize_text_field((string) $option);
            if ($option !== '' && !in_array($option, $clean_options, true)) {
                $clean_options[] = $option;
            }
        }
        if (count($clean_options) < 2) {
            $clean_options = ['Ja', 'Nej'];
        }

        $legacy_html = '';
        if ($type === 'legacy') {
            $legacy_html = (string) ($legacy_source['LegacyHtml'] ?? $raw['LegacyHtml'] ?? '');
        }

        $title = sanitize_text_field((string) ($raw['Title'] ?? ''));
        if ($title === '' && $type === 'poll') {
            $title = 'Afstemning';
        } elseif ($title === '' && $type === 'mail_form') {
            $title = 'Kontakt os';
        }
        $recipient = sanitize_email((string) ($raw['RecipientEmail'] ?? $section['RecipientEmail']));
        if ($recipient === '') {
            $recipient = sanitize_email((string) get_option('admin_email'));
        }
        $success_message = sanitize_text_field((string) ($raw['SuccessMessage'] ?? $section['SuccessMessage']));
        if ($success_message === '') {
            $success_message = $section['SuccessMessage'];
        }
        $imported_group_type = sanitize_key((string) ($raw['ImportedGroupType'] ?? ''));
        if (!in_array($imported_group_type, ['', 'columns'], true)) {
            $imported_group_type = '';
        }
        $primitive_options = $this->page_primitive_variant_options($type);
        $primitive_variant = sanitize_key((string) ($raw['PrimitiveVariant'] ?? ''));
        if ($primitive_variant === '' || !isset($primitive_options[$primitive_variant])) {
            $primitive_variant = (string) array_key_first($primitive_options);
        }
        $advanced_content_authorized = array_key_exists('AdvancedContentAuthorized', $raw)
            ? $this->bool_value($raw['AdvancedContentAuthorized'], false)
            : false;

        $design_mode = (string) ($raw['DesignMode'] ?? 'Global');
        if (!in_array($design_mode, ['Global', 'Custom'], true)) { $design_mode = 'Global'; }
        $shadow_style = (string) ($raw['ShadowStyle'] ?? 'None');
        if (!in_array($shadow_style, ['None', 'Soft', 'Medium', 'Strong'], true)) { $shadow_style = 'None'; }
        $custom_background = sanitize_hex_color((string) ($raw['CustomBackgroundColor'] ?? '#ffffff')) ?: '#ffffff';
        $custom_text = sanitize_hex_color((string) ($raw['CustomTextColor'] ?? '#30382a')) ?: '#30382a';
        $custom_heading = sanitize_hex_color((string) ($raw['CustomHeadingColor'] ?? '#30382a')) ?: '#30382a';
        $custom_border = sanitize_hex_color((string) ($raw['CustomBorderColor'] ?? '#c3ae83')) ?: '#c3ae83';
        $section_fonts = ['Global', 'System', 'Segoe UI', 'Arial', 'Verdana', 'Tahoma', 'Trebuchet MS', 'Georgia', 'Times New Roman', 'Courier New'];
        $section_body_font = (string) ($raw['SectionBodyFontFamily'] ?? 'Global');
        if (!in_array($section_body_font, $section_fonts, true)) { $section_body_font = 'Global'; }
        $section_heading_font = (string) ($raw['SectionHeadingFontFamily'] ?? 'Global');
        if (!in_array($section_heading_font, $section_fonts, true)) { $section_heading_font = 'Global'; }

        $background_effect = (string) ($raw['BackgroundEffect'] ?? 'None');
        if (!in_array($background_effect, ['None', 'Gradient', 'Image'], true)) { $background_effect = 'None'; }
        $gradient_start = sanitize_hex_color((string) ($raw['GradientStartColor'] ?? '#30382a')) ?: '#30382a';
        $gradient_end = sanitize_hex_color((string) ($raw['GradientEndColor'] ?? '#c3ae83')) ?: '#c3ae83';
        $background_position = (string) ($raw['BackgroundImagePosition'] ?? 'Center');
        if (!in_array($background_position, ['Center', 'Top', 'Bottom', 'Left', 'Right'], true)) { $background_position = 'Center'; }
        $background_size = (string) ($raw['BackgroundImageSize'] ?? 'Cover');
        if (!in_array($background_size, ['Cover', 'Contain', 'Auto'], true)) { $background_size = 'Cover'; }
        $hover_effect = (string) ($raw['HoverEffect'] ?? 'None');
        if (!in_array($hover_effect, ['None', 'Lift', 'Scale', 'Shadow'], true)) { $hover_effect = 'None'; }
        $hover_style_mode = (string) ($raw['HoverStyleMode'] ?? 'Inherit');
        if (!in_array($hover_style_mode, ['Inherit', 'Custom'], true)) { $hover_style_mode = 'Inherit'; }
        $hover_background = sanitize_hex_color((string) ($raw['HoverBackgroundColor'] ?? '#ffffff')) ?: '#ffffff';
        $hover_text = sanitize_hex_color((string) ($raw['HoverTextColor'] ?? '#30382a')) ?: '#30382a';
        $hover_heading = sanitize_hex_color((string) ($raw['HoverHeadingColor'] ?? '#30382a')) ?: '#30382a';
        $hover_border = sanitize_hex_color((string) ($raw['HoverBorderColor'] ?? '#c3ae83')) ?: '#c3ae83';
        $transition_preset = (string) ($raw['TransitionPreset'] ?? 'Inherit');
        if (!in_array($transition_preset, ['Inherit','Fast','Normal','Slow','Custom'], true)) { $transition_preset = 'Inherit'; }
        $focus_ring_style = (string) ($raw['FocusRingStyle'] ?? 'Global');
        if (!in_array($focus_ring_style, ['Global','Custom','None'], true)) { $focus_ring_style = 'Global'; }
        $focus_ring_color = sanitize_hex_color((string) ($raw['FocusRingColor'] ?? '#8b4a2b')) ?: '#8b4a2b';
        $active_effect = (string) ($raw['ActiveEffect'] ?? 'None');
        if (!in_array($active_effect, ['None','Press','ScaleDown'], true)) { $active_effect = 'None'; }
        $tablet_alignment = (string) ($raw['TabletAlignment'] ?? 'Inherit');
        if (!in_array($tablet_alignment, ['Inherit', 'Left', 'Center'], true)) { $tablet_alignment = 'Inherit'; }

        $layout_parent_key = sanitize_key((string) ($raw['LayoutParentKey'] ?? ''));
        $layout_direction = (string) ($raw['LayoutDirection'] ?? 'Row');
        if (!in_array($layout_direction, ['Row', 'Column'], true)) { $layout_direction = 'Row'; }
        $layout_justify = (string) ($raw['LayoutJustify'] ?? 'Start');
        if (!in_array($layout_justify, ['Start', 'Center', 'End', 'SpaceBetween'], true)) { $layout_justify = 'Start'; }
        $layout_align = (string) ($raw['LayoutAlign'] ?? 'Stretch');
        if (!in_array($layout_align, ['Start', 'Center', 'End', 'Stretch'], true)) { $layout_align = 'Stretch'; }

        $cards = [];
        $used_card_keys = [];
        $raw_cards = isset($raw['Cards']) && is_array($raw['Cards']) ? $raw['Cards'] : [];
        foreach (array_slice($raw_cards, 0, 12) as $card_index => $raw_card) {
            if (!is_array($raw_card) || !empty($raw_card['Remove'])) {
                continue;
            }
            $card = $this->normalize_page_card($raw_card, $card_index);
            $base_card_key = $card['Key'];
            $card_suffix = 2;
            while (isset($used_card_keys[$card['Key']])) {
                $card['Key'] = $base_card_key . '-' . $card_suffix++;
            }
            $used_card_keys[$card['Key']] = true;
            $cards[] = $card;
        }
        usort($cards, static function($a, $b) {
            return ((int) $a['Order']) <=> ((int) $b['Order']);
        });

        return [
            'Key'                   => $key,
            'Type'                  => $type,
            'Active'                => array_key_exists('Active', $raw) ? $this->bool_value($raw['Active'], false) : true,
            'NavigatorLabel'        => $navigator_label,
            'NavigatorLocked'       => $navigator_locked,
            'ComponentId'           => $component_id,
            'ComponentRevision'     => $component_revision,
            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'Bindings'              => $bindings,
            'BindingOptions'        => $binding_options,
            'ConditionMode'         => $condition_mode,
            'Conditions'            => $conditions,
            'QueryListType'         => $query_list_type,
            'QueryListFilterField'  => $query_list_filter_field,
            'QueryListFilterOperator' => $query_list_filter_operator,
            'QueryListFilterValue'  => $query_list_filter_value,
            'QueryListSort'         => $query_list_sort,
            'QueryListOrder'        => $query_list_order,
            'QueryListLimit'        => $this->clamp_int($raw['QueryListLimit'] ?? 10, 1, 100, 10),
            'QueryListComponentId'  => $query_list_component_id,
            'QueryListComponentVariant' => $query_list_component_variant,
            'QueryListColumns'      => $this->clamp_int($raw['QueryListColumns'] ?? 1, 1, 6, 1),
            'QueryListMobileColumns'=> $this->clamp_int($raw['QueryListMobileColumns'] ?? 1, 1, 2, 1),
            'QueryListGapPx'        => $this->clamp_int($raw['QueryListGapPx'] ?? 18, 0, 80, 18),
            'QueryListMobileGapPx'  => $this->clamp_int($raw['QueryListMobileGapPx'] ?? 14, 0, 60, 14),
            'QueryListEmptyText'    => $query_list_empty_text,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
            'Title'                 => $title,
            'Content'               => $type === 'css'
                ? $this->sanitize_page_section_css((string) ($raw['Content'] ?? ''))
                : ($type === 'shortcode'
                    ? sanitize_textarea_field((string) ($raw['Content'] ?? ''))
                    : ($type === 'embed'
                        ? esc_url_raw(trim((string) ($raw['Content'] ?? '')))
                        : wp_kses_post((string) ($raw['Content'] ?? '')))),
            'PrimitiveVariant'      => $primitive_variant,
            'AdvancedContentAuthorized' => $advanced_content_authorized,
            'MediaId'               => absint($raw['MediaId'] ?? 0),
            'MediaUrl'              => esc_url_raw((string) ($raw['MediaUrl'] ?? '')),
            'ImagePosition'         => $image_position,
            'ImageAspectRatio'      => $image_aspect,
            'ImageFit'              => $image_fit,
            'ImageFocalXPercent'    => $this->clamp_int($raw['ImageFocalXPercent'] ?? 50, 0, 100, 50),
            'ImageFocalYPercent'    => $this->clamp_int($raw['ImageFocalYPercent'] ?? 50, 0, 100, 50),
            'ImageHeightPx'         => $this->clamp_int($raw['ImageHeightPx'] ?? 0, 0, 1200, 0),
            'MobileImageHeightPx'   => $this->clamp_int($raw['MobileImageHeightPx'] ?? 0, 0, 900, 0),
            'ElementWidthPercent'     => $this->clamp_int($raw['ElementWidthPercent'] ?? 100, 20, 100, 100),
            'TabletWidthPercent'      => $this->clamp_int($raw['TabletWidthPercent'] ?? -1, -1, 100, -1),
            'MobileWidthPercent'      => $this->clamp_int($raw['MobileWidthPercent'] ?? -1, -1, 100, -1),
            'ElementMaxWidthPx'       => $this->clamp_int($raw['ElementMaxWidthPx'] ?? 0, 0, 2400, 0),
            'ElementMinHeightPx'      => $this->clamp_int($raw['ElementMinHeightPx'] ?? 0, 0, 1600, 0),
            'TabletMinHeightPx'       => $this->clamp_int($raw['TabletMinHeightPx'] ?? -1, -1, 1600, -1),
            'MobileMinHeightPx'       => $this->clamp_int($raw['MobileMinHeightPx'] ?? -1, -1, 1200, -1),
            'ImageWidthPercent'       => $this->clamp_int($raw['ImageWidthPercent'] ?? 100, 20, 100, 100),
            'MobileImageWidthPercent' => $this->clamp_int($raw['MobileImageWidthPercent'] ?? 100, 20, 100, 100),
            'ImageMaxWidthPx'         => $this->clamp_int($raw['ImageMaxWidthPx'] ?? 0, 0, 2000, 0),
            'ImageAspectLocked'       => array_key_exists('ImageAspectLocked', $raw) ? $this->bool_value($raw['ImageAspectLocked'], false) : false,
            'Button1Label'          => sanitize_text_field((string) ($raw['Button1Label'] ?? '')),
            'Button1Url'            => esc_url_raw((string) ($raw['Button1Url'] ?? '')),
            'Button2Label'          => sanitize_text_field((string) ($raw['Button2Label'] ?? '')),
            'Button2Url'            => esc_url_raw((string) ($raw['Button2Url'] ?? '')),
            'RecipientEmail'        => $recipient,
            'SuccessMessage'        => $success_message,
            'StoreSubmissions'      => !empty($raw['StoreSubmissions']),
            'ConsentLabel'          => sanitize_text_field((string) ($raw['ConsentLabel'] ?? '')),
            'PollOptions'           => $clean_options,
            'AllowMultiple'         => !empty($raw['AllowMultiple']),
            'ResultsMode'           => $results_mode,
            'StartUtc'              => sanitize_text_field((string) ($raw['StartUtc'] ?? '')),
            'EndUtc'                => sanitize_text_field((string) ($raw['EndUtc'] ?? '')),
            'DesktopAlignment'      => $alignment,
            'MobileAlignment'       => $mobile_alignment,
            'Background'            => $background,
            'Columns'               => $this->clamp_int($raw['Columns'] ?? 3, 1, 4, 3),
            'MobileColumns'         => $this->clamp_int($raw['MobileColumns'] ?? 1, 1, 2, 1),
            'ColumnGapPx'           => $this->clamp_int($raw['ColumnGapPx'] ?? 16, 0, 80, 16),
            'MobileColumnGapPx'     => $this->clamp_int($raw['MobileColumnGapPx'] ?? 14, 0, 60, 14),
            'Cards'                  => $cards,
            'LayoutParentKey'        => $layout_parent_key,
            'LayoutDirection'        => $layout_direction,
            'LayoutWrap'             => array_key_exists('LayoutWrap', $raw) ? $this->bool_value($raw['LayoutWrap'], true) : true,
            'LayoutJustify'          => $layout_justify,
            'LayoutAlign'            => $layout_align,
            'LayoutGapPx'            => $this->clamp_int($raw['LayoutGapPx'] ?? 16, 0, 120, 16),
            'MobileLayoutGapPx'      => $this->clamp_int($raw['MobileLayoutGapPx'] ?? 12, 0, 80, 12),
            'LayoutColumns'          => $this->clamp_int($raw['LayoutColumns'] ?? 2, 1, 6, 2),
            'MobileLayoutColumns'    => $this->clamp_int($raw['MobileLayoutColumns'] ?? 1, 1, 3, 1),
            'MobileLayoutStack'      => array_key_exists('MobileLayoutStack', $raw) ? $this->bool_value($raw['MobileLayoutStack'], true) : true,
            'CarouselAutoplay'       => array_key_exists('CarouselAutoplay', $raw) ? $this->bool_value($raw['CarouselAutoplay'], false) : false,
            'CarouselIntervalMs'     => $this->clamp_int($raw['CarouselIntervalMs'] ?? 5000, 2000, 20000, 5000),
            'CarouselLoop'           => array_key_exists('CarouselLoop', $raw) ? $this->bool_value($raw['CarouselLoop'], true) : true,
            'CarouselShowArrows'     => array_key_exists('CarouselShowArrows', $raw) ? $this->bool_value($raw['CarouselShowArrows'], true) : true,
            'CarouselShowDots'       => array_key_exists('CarouselShowDots', $raw) ? $this->bool_value($raw['CarouselShowDots'], true) : true,
            'TopSpacingPx'           => $this->clamp_int($raw['TopSpacingPx'] ?? 0, 0, 160, 0),
            'BottomSpacingPx'       => $this->clamp_int($raw['BottomSpacingPx'] ?? 24, 0, 160, 24),
            'MobileTopSpacingPx'    => $this->clamp_int($raw['MobileTopSpacingPx'] ?? 0, 0, 100, 0),
            'MobileBottomSpacingPx' => $this->clamp_int($raw['MobileBottomSpacingPx'] ?? 18, 0, 100, 18),
            'PaddingPx'             => $this->clamp_int($raw['PaddingPx'] ?? 0, 0, 100, 0),
            'HorizontalPaddingPx'   => $this->clamp_int($raw['HorizontalPaddingPx'] ?? ($raw['PaddingPx'] ?? 0), 0, 100, 0),
            'MobilePaddingPx'       => $this->clamp_int($raw['MobilePaddingPx'] ?? 0, 0, 80, 0),
            'MobileHorizontalPaddingPx' => $this->clamp_int($raw['MobileHorizontalPaddingPx'] ?? ($raw['MobilePaddingPx'] ?? 0), 0, 80, 0),
            'RadiusPx'              => $this->clamp_int($raw['RadiusPx'] ?? 7, 0, 30, 7),
            'SpacerPx'              => $this->clamp_int($raw['SpacerPx'] ?? 32, 0, 200, 32),
            'MobileSpacerPx'        => $this->clamp_int($raw['MobileSpacerPx'] ?? 24, 0, 140, 24),
            'HeroHeightPx'          => $this->clamp_int($raw['HeroHeightPx'] ?? 320, 140, 800, 320),
            'MobileHeroHeightPx'    => $this->clamp_int($raw['MobileHeroHeightPx'] ?? 220, 100, 600, 220),
            'OverlayOpacityPercent' => $this->clamp_int($raw['OverlayOpacityPercent'] ?? 35, 0, 90, 35),
            'DesignMode'             => $design_mode,
            'CustomBackgroundColor'  => $custom_background,
            'CustomTextColor'        => $custom_text,
            'CustomHeadingColor'     => $custom_heading,
            'BorderWidthPx'          => $this->clamp_int($raw['BorderWidthPx'] ?? 0, 0, 12, 0),
            'CustomBorderColor'      => $custom_border,
            'ShadowStyle'            => $shadow_style,
            'SectionBodyFontFamily' => $section_body_font,
            'SectionHeadingFontFamily' => $section_heading_font,
            'BodyFontSizePx'         => $this->clamp_int($raw['BodyFontSizePx'] ?? 0, 0, 32, 0),
            'H1FontSizePx'           => $this->clamp_int($raw['H1FontSizePx'] ?? 0, 0, 96, 0),
            'H2FontSizePx'           => $this->clamp_int($raw['H2FontSizePx'] ?? 0, 0, 80, 0),
            'H3FontSizePx'           => $this->clamp_int($raw['H3FontSizePx'] ?? 0, 0, 64, 0),
            'SectionOpacityPercent'  => $this->clamp_int($raw['SectionOpacityPercent'] ?? 100, 0, 100, 100),
            'BackgroundEffect'       => $background_effect,
            'GradientStartColor'     => $gradient_start,
            'GradientEndColor'       => $gradient_end,
            'GradientAngleDeg'       => $this->clamp_int($raw['GradientAngleDeg'] ?? 135, 0, 360, 135),
            'BackgroundMediaId'      => absint($raw['BackgroundMediaId'] ?? 0),
            'BackgroundImageUrl'     => esc_url_raw((string) ($raw['BackgroundImageUrl'] ?? '')),
            'BackgroundImagePosition'=> $background_position,
            'BackgroundImageSize'    => $background_size,
            'RadiusTopLeftPx'        => $this->clamp_int($raw['RadiusTopLeftPx'] ?? -1, -1, 60, -1),
            'RadiusTopRightPx'       => $this->clamp_int($raw['RadiusTopRightPx'] ?? -1, -1, 60, -1),
            'RadiusBottomRightPx'    => $this->clamp_int($raw['RadiusBottomRightPx'] ?? -1, -1, 60, -1),
            'RadiusBottomLeftPx'     => $this->clamp_int($raw['RadiusBottomLeftPx'] ?? -1, -1, 60, -1),
            'HoverEffect'            => $hover_effect,
            'HoverTransitionMs'      => $this->clamp_int($raw['HoverTransitionMs'] ?? 220, 0, 1000, 220),
            'HoverStyleMode'         => $hover_style_mode,
            'HoverBackgroundColor'   => $hover_background,
            'HoverTextColor'         => $hover_text,
            'HoverHeadingColor'      => $hover_heading,
            'HoverBorderColor'       => $hover_border,
            'HoverOpacityPercent'    => $this->clamp_int($raw['HoverOpacityPercent'] ?? 100, 0, 100, 100),
            'TransitionPreset'       => $transition_preset,
            'FocusRingStyle'         => $focus_ring_style,
            'FocusRingColor'         => $focus_ring_color,
            'FocusRingWidthPx'       => $this->clamp_int($raw['FocusRingWidthPx'] ?? 3, 1, 8, 3),
            'FocusRingOffsetPx'      => $this->clamp_int($raw['FocusRingOffsetPx'] ?? 2, 0, 12, 2),
            'ActiveEffect'           => $active_effect,
            'DisabledOpacityPercent' => $this->clamp_int($raw['DisabledOpacityPercent'] ?? 55, 10, 100, 55),
            'ShowDesktop'            => array_key_exists('ShowDesktop', $raw) ? !empty($raw['ShowDesktop']) : true,
            'ShowTablet'             => array_key_exists('ShowTablet', $raw) ? !empty($raw['ShowTablet']) : true,
            'ShowMobile'             => array_key_exists('ShowMobile', $raw) ? !empty($raw['ShowMobile']) : true,
            'TabletAlignment'        => $tablet_alignment,
            'TabletTopSpacingPx'     => $this->clamp_int($raw['TabletTopSpacingPx'] ?? -1, -1, 160, -1),
            'TabletBottomSpacingPx'  => $this->clamp_int($raw['TabletBottomSpacingPx'] ?? -1, -1, 160, -1),
            'TabletPaddingPx'        => $this->clamp_int($raw['TabletPaddingPx'] ?? -1, -1, 100, -1),
            'TabletHorizontalPaddingPx' => $this->clamp_int($raw['TabletHorizontalPaddingPx'] ?? -1, -1, 100, -1),
            'DesktopTranslateXPx'    => $this->clamp_int($raw['DesktopTranslateXPx'] ?? 0, -300, 300, 0),
            'DesktopTranslateYPx'    => $this->clamp_int($raw['DesktopTranslateYPx'] ?? 0, -300, 300, 0),
            'DesktopScalePercent'    => $this->clamp_int($raw['DesktopScalePercent'] ?? 100, 50, 150, 100),
            'DesktopRotateDeg'       => $this->clamp_int($raw['DesktopRotateDeg'] ?? 0, -180, 180, 0),
            'TabletTranslateXPx'     => $this->clamp_int($raw['TabletTranslateXPx'] ?? 0, -300, 300, 0),
            'TabletTranslateYPx'     => $this->clamp_int($raw['TabletTranslateYPx'] ?? 0, -300, 300, 0),
            'TabletScalePercent'     => $this->clamp_int($raw['TabletScalePercent'] ?? 100, 50, 150, 100),
            'TabletRotateDeg'        => $this->clamp_int($raw['TabletRotateDeg'] ?? 0, -180, 180, 0),
            'MobileTranslateXPx'     => $this->clamp_int($raw['MobileTranslateXPx'] ?? 0, -300, 300, 0),
            'MobileTranslateYPx'     => $this->clamp_int($raw['MobileTranslateYPx'] ?? 0, -300, 300, 0),
            'MobileScalePercent'     => $this->clamp_int($raw['MobileScalePercent'] ?? 100, 50, 150, 100),
            'MobileRotateDeg'        => $this->clamp_int($raw['MobileRotateDeg'] ?? 0, -180, 180, 0),
            'ImportedGroupType'     => $imported_group_type,
            'LegacyHtml'            => $legacy_html,
        ];
    }

    private function normalize_page_editor_data(array $raw, $page = null) {
        $slug = sanitize_title((string) ($raw['PageSlug'] ?? ($page ? $page->post_name : '')));
        $definitions = $this->editable_page_definitions();
        if (!isset($definitions[$slug])) {
            $slug = self::HOME_SLUG;
        }

        $sections = [];
        $used_keys = [];
        $raw_sections = isset($raw['Sections']) && is_array($raw['Sections']) ? $raw['Sections'] : [];
        foreach (array_slice($raw_sections, 0, 25) as $index => $raw_section) {
            if (!is_array($raw_section)) {
                continue;
            }
            $section = $this->normalize_page_section($raw_section, $index);
            $base_key = $section['Key'];
            $suffix = 2;
            while (isset($used_keys[$section['Key']])) {
                $section['Key'] = $base_key . '-' . $suffix++;
            }
            $used_keys[$section['Key']] = true;
            $sections[] = $section;
        }
        usort($sections, static function($a, $b) {
            return ((int) $a['Order']) <=> ((int) $b['Order']);
        });

        $layout_parent_types = ['container', 'flex', 'grid'];
        $sections_by_key = [];
        foreach ($sections as $section_index => $candidate) {
            $sections_by_key[(string) $candidate['Key']] = $section_index;
        }
        foreach ($sections as $section_index => &$candidate) {
            $parent_key = sanitize_key((string) ($candidate['LayoutParentKey'] ?? ''));
            if ($parent_key === '') { continue; }
            $self_key = (string) $candidate['Key'];
            $seen = [$self_key => true];
            $cursor = $parent_key;
            $depth = 0;
            $valid_parent = true;
            while ($cursor !== '') {
                $depth++;
                if ($depth > 2 || isset($seen[$cursor]) || !isset($sections_by_key[$cursor])) {
                    $valid_parent = false;
                    break;
                }
                $seen[$cursor] = true;
                $parent_section = $sections[$sections_by_key[$cursor]];
                if (!in_array((string) ($parent_section['Type'] ?? ''), $layout_parent_types, true)) {
                    $valid_parent = false;
                    break;
                }
                $cursor = sanitize_key((string) ($parent_section['LayoutParentKey'] ?? ''));
            }
            if (!$valid_parent) {
                $candidate['LayoutParentKey'] = '';
            }
        }
        unset($candidate);

        $title = sanitize_text_field((string) ($raw['PageTitle'] ?? ($page ? $page->post_title : $definitions[$slug])));
        if ($title === '') {
            $title = $definitions[$slug];
        }

        $content_version = $this->clamp_int($raw['ContentVersion'] ?? 0, 0, 9999, 0);
        if (
            $content_version === 0 &&
            $page instanceof WP_Post &&
            strpos((string) $page->post_content, self::PAGE_EDITOR_MARKER) !== false
        ) {
            $content_version = 1;
        }
        $data_context_type = sanitize_key((string) ($raw['DataContextType'] ?? ''));
        $data_context_entry_id = absint($raw['DataContextEntryId'] ?? 0);
        if ($data_context_type === '' || $data_context_entry_id <= 0 || !$this->resolve_dynamic_data_context($data_context_type, $data_context_entry_id)) {
            $data_context_type = '';
            $data_context_entry_id = 0;
        }

        return [
            'Version'            => '1.22',
            'PageSlug'           => $slug,
            'PageTitle'          => $title,
            'ContentVersion'     => $content_version,
            'DataContextType'    => $data_context_type,
            'DataContextEntryId' => $data_context_entry_id,
            'Sections'           => $sections,
        ];
    }

    private function get_page_editor_store() {
        $stored = get_option(self::PAGE_EDITOR_OPTION, []);
        return is_array($stored) ? $stored : [];
    }

    private function get_page_version_history($slug) {
        $slug = sanitize_title((string) $slug);
        $all = get_option(self::PAGE_VERSION_HISTORY_OPTION, []);
        if (!is_array($all) || !isset($all[$slug]) || !is_array($all[$slug])) {
            return [];
        }

        $history = [];
        foreach (array_slice($all[$slug], 0, 100) as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $history[] = [
                'Version'          => $this->clamp_int($entry['Version'] ?? 0, 1, 9999, 1),
                'SavedUtc'         => sanitize_text_field((string) ($entry['SavedUtc'] ?? '')),
                'UserId'           => absint($entry['UserId'] ?? 0),
                'UserDisplay'      => sanitize_text_field((string) ($entry['UserDisplay'] ?? 'Ukendt bruger')),
                'ChangeNote'       => sanitize_textarea_field((string) ($entry['ChangeNote'] ?? '')),
                'FullBackupFile'   => sanitize_file_name((string) ($entry['FullBackupFile'] ?? '')),
                'SnapshotFile'     => sanitize_file_name((string) ($entry['SnapshotFile'] ?? '')),
                'ContentHash'      => preg_replace('/[^a-f0-9]/i', '', (string) ($entry['ContentHash'] ?? '')),
                'ActiveSections'   => absint($entry['ActiveSections'] ?? 0),
            ];
        }
        usort($history, static function($a, $b) {
            return ((int) $b['Version']) <=> ((int) $a['Version']);
        });
        return $history;
    }

    private function append_page_version_history($slug, array $entry) {
        $slug = sanitize_title((string) $slug);
        $all = get_option(self::PAGE_VERSION_HISTORY_OPTION, []);
        if (!is_array($all)) {
            $all = [];
        }
        $history = isset($all[$slug]) && is_array($all[$slug]) ? $all[$slug] : [];
        array_unshift($history, $entry);
        $all[$slug] = array_slice($history, 0, 100);
        update_option(self::PAGE_VERSION_HISTORY_OPTION, $all, false);
    }

    private function extract_page_core_content($content) {
        $content = (string) $content;
        $start_marker = '<!-- HANGAR18-PAGE-FRAME-START -->';
        $end_marker = '<!-- HANGAR18-PAGE-FRAME-END -->';
        $start = strpos($content, $start_marker);
        $end = strpos($content, $end_marker);

        if ($start !== false && $end !== false && $end > $start) {
            $frame = substr($content, $start + strlen($start_marker), $end - $start - strlen($start_marker));
            $frame = preg_replace('/^\s*<!-- wp:group.*?-->\s*<div[^>]*class="[^"]*h18-page-frame[^"]*"[^>]*>/s', '', $frame, 1);
            $frame = preg_replace('/<\/div>\s*<!-- \/wp:group -->\s*$/s', '', (string) $frame, 1);
            return trim((string) $frame);
        }

        $core = $this->strip_block($content, self::HEADER_START, self::HEADER_END);
        $core = $this->strip_block($core, self::CSS_START, self::CSS_END);
        $core = $this->strip_block($core, self::OVERRIDE_START, self::OVERRIDE_END);
        $core = $this->strip_block($core, self::FOOTER_START, self::FOOTER_END);
        return trim($core);
    }

    private function migrate_static_content_to_page_editor($page, array $static) {
        $sections = [];
        $order = 10;
        $intro = $this->default_page_section('text', $order);
        $intro['Key'] = 'introduktion';
        $intro['Title'] = sanitize_text_field((string) ($static['Heading'] ?? ''));
        $intro['Content'] = nl2br(esc_html((string) ($static['Intro'] ?? '')));
        $intro['BottomSpacingPx'] = (int) ($static['CardsTopSpacingPx'] ?? 24);
        $intro['MobileBottomSpacingPx'] = (int) ($static['MobileCardsTopSpacingPx'] ?? 18);
        $sections[] = $intro;

        foreach (($static['Sections'] ?? []) as $static_section) {
            if (!is_array($static_section)) {
                continue;
            }
            $order += 10;
            $section = $this->default_page_section('card', $order);
            $section['Key'] = sanitize_key((string) ($static_section['Key'] ?? 'sektion-' . $order));
            $section['Title'] = sanitize_text_field((string) ($static_section['Title'] ?? ''));
            $section['Content'] = nl2br(esc_html((string) ($static_section['Body'] ?? '')));
            $section['Active'] = !empty($static_section['Active']);
            $section['Background'] = 'OffWhite';
            $section['PaddingPx'] = (int) ($static['CardPaddingPx'] ?? 26);
            $section['MobilePaddingPx'] = (int) ($static['MobileCardPaddingPx'] ?? 20);
            $section['RadiusPx'] = (int) ($static['CardRadiusPx'] ?? 7);
            $section['BottomSpacingPx'] = (int) ($static['CardGapPx'] ?? 20);
            $section['MobileBottomSpacingPx'] = (int) ($static['MobileCardGapPx'] ?? 14);
            $sections[] = $section;
        }

        return $this->normalize_page_editor_data([
            'PageSlug'  => $page->post_name,
            'PageTitle' => $page->post_title,
            'Sections'  => $sections,
        ], $page);
    }

    private function page_import_block_html(array $block) {
        $inner_content = isset($block['innerContent']) && is_array($block['innerContent'])
            ? $block['innerContent']
            : [];
        $inner_blocks = isset($block['innerBlocks']) && is_array($block['innerBlocks'])
            ? $block['innerBlocks']
            : [];

        if (!$inner_content) {
            return trim((string) ($block['innerHTML'] ?? ''));
        }

        $html = '';
        $child_index = 0;
        foreach ($inner_content as $piece) {
            if ($piece === null) {
                if (isset($inner_blocks[$child_index]) && is_array($inner_blocks[$child_index])) {
                    $html .= $this->page_import_block_html($inner_blocks[$child_index]);
                }
                $child_index++;
                continue;
            }
            $html .= (string) $piece;
        }
        return trim($html);
    }

    private function page_import_inner_blocks_html(array $block) {
        $html = '';
        foreach (($block['innerBlocks'] ?? []) as $inner_block) {
            if (is_array($inner_block)) {
                $html .= $this->page_import_block_html($inner_block);
            }
        }
        return trim($html);
    }

    private function page_import_extract_heading(&$html) {
        $html = (string) $html;
        if (!preg_match('/<h([1-6])\b[^>]*>(.*?)<\/h\1>/is', $html, $match)) {
            return '';
        }

        $title = sanitize_text_field(wp_strip_all_tags((string) $match[2]));
        $html = trim((string) preg_replace('/<h([1-6])\b[^>]*>.*?<\/h\1>/is', '', $html, 1));
        return $title;
    }

    private function page_import_image_data(array $block, $html = '') {
        $attrs = isset($block['attrs']) && is_array($block['attrs']) ? $block['attrs'] : [];
        $media_id = absint($attrs['id'] ?? $attrs['backgroundImageId'] ?? 0);
        $url = esc_url_raw((string) ($attrs['url'] ?? $attrs['backgroundImageUrl'] ?? ''));
        $html = (string) $html;

        if (!$media_id && preg_match('/\bwp-image-([0-9]+)\b/i', $html, $id_match)) {
            $media_id = absint($id_match[1]);
        }
        if ($url === '' && preg_match('/<img\b[^>]*\bsrc\s*=\s*(["\'])(.*?)\1/is', $html, $url_match)) {
            $url = esc_url_raw(html_entity_decode((string) $url_match[2], ENT_QUOTES, 'UTF-8'));
        }

        return ['id' => $media_id, 'url' => $url];
    }

    private function page_import_extract_buttons(&$html) {
        $html = (string) $html;
        $buttons = [];
        if (preg_match_all('/<a\b([^>]*)>(.*?)<\/a>/is', $html, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $match) {
                if (count($buttons) >= 2 || !preg_match('/\bhref\s*=\s*(["\'])(.*?)\1/is', (string) $match[1], $href_match)) {
                    continue;
                }
                $label = sanitize_text_field(wp_strip_all_tags((string) $match[2]));
                $url = esc_url_raw(html_entity_decode((string) $href_match[2], ENT_QUOTES, 'UTF-8'));
                if ($label === '' || $url === '') {
                    continue;
                }
                $buttons[] = ['label' => $label, 'url' => $url];
                $html = str_replace((string) $match[0], '', $html);
            }
        }

        for ($pass = 0; $pass < 3; $pass++) {
            $html = (string) preg_replace('/<(div|p)\b[^>]*class=(["\'])[^"\']*wp-block-(buttons|button)[^"\']*\2[^>]*>\s*<\/\1>/is', '', $html);
        }
        $html = trim($html);
        return $buttons;
    }

    private function page_import_extract_css(&$html) {
        $html = (string) $html;
        $css = '';
        if (preg_match_all('/<style\b[^>]*>(.*?)<\/style>/is', $html, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $match) {
                $css .= "\n" . (string) $match[1];
                $html = str_replace((string) $match[0], '', $html);
            }
        }
        $html = trim($html);
        return $this->sanitize_page_section_css($css);
    }

    private function clean_page_hero_content($content) {
        $content = (string) $content;
        $content = (string) preg_replace_callback('/<img\b[^>]*>/i', static function ($match) {
            return stripos((string) $match[0], 'wp-block-cover__image-background') !== false ? '' : (string) $match[0];
        }, $content);
        $content = (string) preg_replace('/<span\b[^>]*(?:wp-block-cover__background|has-background-dim)[^>]*>\s*<\/span>/is', '', $content);
        return trim($content);
    }

    private function page_import_section($type, $order, array $values = []) {
        $section = $this->default_page_section($type, $order);
        $section['Key'] = 'importeret-' . str_pad((string) max(1, (int) ($order / 10)), 2, '0', STR_PAD_LEFT);
        foreach ($values as $key => $value) {
            if (array_key_exists($key, $section)) {
                $section[$key] = $value;
            }
        }
        return $section;
    }

    private function page_import_append_text(array &$sections, $html, $title = '', $type = 'text') {
        $html = trim((string) $html);
        $title = sanitize_text_field((string) $title);
        if ($html === '' && $title === '') {
            return;
        }

        $last_index = count($sections) - 1;
        if (
            $type === 'text' &&
            $last_index >= 0 &&
            ($sections[$last_index]['Type'] ?? '') === 'text' &&
            $title === ''
        ) {
            $sections[$last_index]['Content'] = trim((string) $sections[$last_index]['Content'] . "\n" . $html);
            return;
        }

        $order = (count($sections) + 1) * 10;
        $sections[] = $this->page_import_section($type, $order, [
            'Title'   => $title,
            'Content' => $html,
        ]);
    }

    private function page_import_block(array $block, array &$sections) {
        if (count($sections) >= 25) {
            return;
        }

        $name = (string) ($block['blockName'] ?? '');
        $attrs = isset($block['attrs']) && is_array($block['attrs']) ? $block['attrs'] : [];
        $html = $this->page_import_block_html($block);
        $inner_html = $this->page_import_inner_blocks_html($block);

        if (stripos($html, '<style') !== false) {
            $remaining_html = $html;
            $css = $this->page_import_extract_css($remaining_html);
            if ($css !== '') {
                $sections[] = $this->page_import_section('css', (count($sections) + 1) * 10, [
                    'Content'         => $css,
                    'BottomSpacingPx' => 0,
                    'MobileBottomSpacingPx' => 0,
                ]);
            }
            if ($remaining_html !== '' && count($sections) < 25) {
                $this->page_import_append_text($sections, $remaining_html, '', 'html');
            }
            return;
        }

        if ($name === 'core/cover') {
            $copy = $inner_html !== '' ? $inner_html : $html;
            $title = $this->page_import_extract_heading($copy);
            $buttons = $this->page_import_extract_buttons($copy);
            $copy = $this->clean_page_hero_content($copy);
            $image = $this->page_import_image_data($block, $html);
            $order = (count($sections) + 1) * 10;
            $section = $this->page_import_section('hero', $order, [
                'Title'                 => $title,
                'Content'               => $copy,
                'MediaId'               => $image['id'],
                'MediaUrl'              => $image['url'],
                'DesktopAlignment'      => 'Center',
                'MobileAlignment'       => 'Center',
                'Background'            => 'Olive',
                'PaddingPx'             => 36,
                'MobilePaddingPx'       => 22,
                'HeroHeightPx'          => $this->clamp_int($attrs['minHeight'] ?? 320, 140, 800, 320),
                'MobileHeroHeightPx'    => $this->clamp_int($attrs['minHeight'] ?? 220, 100, 600, 220),
                'OverlayOpacityPercent' => $this->clamp_int($attrs['dimRatio'] ?? 35, 0, 90, 35),
            ]);
            if (isset($buttons[0])) {
                $section['Button1Label'] = $buttons[0]['label'];
                $section['Button1Url'] = $buttons[0]['url'];
            }
            if (isset($buttons[1])) {
                $section['Button2Label'] = $buttons[1]['label'];
                $section['Button2Url'] = $buttons[1]['url'];
            }
            $sections[] = $section;
            return;
        }

        if ($name === 'core/heading') {
            $heading_html = $html;
            $title = $this->page_import_extract_heading($heading_html);
            $this->page_import_append_text($sections, $heading_html, $title, 'text');
            return;
        }

        if ($name === 'core/list') {
            $sections[] = $this->page_import_section('list', (count($sections) + 1) * 10, [
                'Content' => $html,
                'PrimitiveVariant' => !empty($attrs['ordered']) ? 'numbers' : 'bullets',
            ]);
            return;
        }
        if ($name === 'core/quote') {
            $sections[] = $this->page_import_section('quote', (count($sections) + 1) * 10, [
                'Content' => $html,
                'PrimitiveVariant' => 'standard',
            ]);
            return;
        }
        if (in_array($name, ['core/paragraph', 'core/table', 'core/preformatted'], true)) {
            $this->page_import_append_text($sections, $html);
            return;
        }

        if ($name === 'core/image') {
            $image = $this->page_import_image_data($block, $html);
            $caption = '';
            if (preg_match('/<figcaption\b[^>]*>(.*?)<\/figcaption>/is', $html, $caption_match)) {
                $caption = wp_kses_post((string) $caption_match[1]);
            }
            $sections[] = $this->page_import_section('image', (count($sections) + 1) * 10, [
                'Content'  => $caption,
                'MediaId'  => $image['id'],
                'MediaUrl' => $image['url'],
            ]);
            return;
        }

        if ($name === 'core/buttons' || $name === 'core/button') {
            $button_html = $html;
            $buttons = $this->page_import_extract_buttons($button_html);
            $section = $this->page_import_section('buttons', (count($sections) + 1) * 10);
            if (isset($buttons[0])) {
                $section['Button1Label'] = $buttons[0]['label'];
                $section['Button1Url'] = $buttons[0]['url'];
            }
            if (isset($buttons[1])) {
                $section['Button2Label'] = $buttons[1]['label'];
                $section['Button2Url'] = $buttons[1]['url'];
            }
            $sections[] = $section;
            return;
        }

        if ($name === 'core/separator') {
            $sections[] = $this->page_import_section('divider', (count($sections) + 1) * 10, [
                'PrimitiveVariant' => 'solid',
                'BottomSpacingPx' => 24,
                'MobileBottomSpacingPx' => 18,
            ]);
            return;
        }
        if ($name === 'core/spacer') {
            $height = $this->clamp_int($attrs['height'] ?? 32, 0, 200, 32);
            $sections[] = $this->page_import_section('spacer', (count($sections) + 1) * 10, [
                'SpacerPx'       => $height,
                'MobileSpacerPx' => min($height, 140),
            ]);
            return;
        }

        if ($name === 'core/columns') {
            $columns = isset($block['innerBlocks']) && is_array($block['innerBlocks']) ? $block['innerBlocks'] : [];
            if (count($columns) === 2) {
                $column_html = [
                    $this->page_import_block_html($columns[0]),
                    $this->page_import_block_html($columns[1]),
                ];
                $image_index = preg_match('/<img\b/i', $column_html[0]) ? 0 : (preg_match('/<img\b/i', $column_html[1]) ? 1 : -1);
                if ($image_index >= 0) {
                    $copy_index = $image_index === 0 ? 1 : 0;
                    $copy = $column_html[$copy_index];
                    $title = $this->page_import_extract_heading($copy);
                    $image = $this->page_import_image_data($columns[$image_index], $column_html[$image_index]);
                    $sections[] = $this->page_import_section('text_image', (count($sections) + 1) * 10, [
                        'Title'         => $title,
                        'Content'       => $copy,
                        'MediaId'       => $image['id'],
                        'MediaUrl'      => $image['url'],
                        'ImagePosition' => $image_index === 0 ? 'Left' : 'Right',
                    ]);
                    return;
                }
            }

            $this->page_import_append_text($sections, $html, '', 'html');
            return;
        }

        if ($name === 'core/group' || $name === 'core/column') {
            $class_name = strtolower((string) ($attrs['className'] ?? ''));
            $background = strtolower((string) ($attrs['backgroundColor'] ?? ''));
            if (strpos($class_name, 'card') !== false || strpos($class_name, 'kort') !== false || $background !== '') {
                $copy = $inner_html !== '' ? $inner_html : $html;
                $title = $this->page_import_extract_heading($copy);
                $sections[] = $this->page_import_section('card', (count($sections) + 1) * 10, [
                    'Title'             => $title,
                    'Content'           => $copy,
                    'Background'        => 'OffWhite',
                    'PaddingPx'         => 26,
                    'MobilePaddingPx'   => 20,
                    'BottomSpacingPx'   => 20,
                    'MobileBottomSpacingPx' => 14,
                ]);
                return;
            }

            // Grupper med egne klasser er normalt bevidste designsektioner.
            // Bevar wrapperen, så eksisterende CSS, kolonner og luft fortsat virker.
            if ($class_name !== '' && strpos($class_name, 'h18-page-frame') === false) {
                $this->page_import_append_text($sections, $html, '', 'html');
                return;
            }

            if (!empty($block['innerBlocks'])) {
                foreach ($block['innerBlocks'] as $inner_block) {
                    if (is_array($inner_block)) {
                        $this->page_import_block($inner_block, $sections);
                    }
                }
                return;
            }
        }

        if ($html !== '') {
            $copy = $html;
            $title = $this->page_import_extract_heading($copy);
            $this->page_import_append_text($sections, $copy, $title, 'html');
        }
    }

    private function import_page_html_to_editor_sections($html) {
        $html = trim((string) $html);
        if ($html === '') {
            return [];
        }

        $sections = [];
        $blocks = function_exists('parse_blocks') ? parse_blocks($html) : [];
        if (is_array($blocks) && $blocks) {
            foreach ($blocks as $block) {
                if (is_array($block)) {
                    $this->page_import_block($block, $sections);
                }
            }
        }

        // Bevar altid hele siden. Meget komplekse sider samles i én redigerbar
        // HTML-sektion i stedet for at blive afkortet ved editorens grænse på 25.
        if (count($sections) >= 25) {
            $sections = [];
            $this->page_import_append_text($sections, $html, '', 'html');
        }

        if (!$sections) {
            $copy = $html;
            $title = $this->page_import_extract_heading($copy);
            $this->page_import_append_text($sections, $copy, $title, 'html');
        }

        foreach ($sections as $index => &$section) {
            $section['Order'] = ($index + 1) * 10;
            $section['Key'] = 'importeret-' . str_pad((string) ($index + 1), 2, '0', STR_PAD_LEFT);
        }
        unset($section);
        return array_slice($sections, 0, 25);
    }

    private function get_page_editor_data_for_admin($slug, $page, &$converted_sections = 0) {
        $data = $this->get_page_editor_data($slug, $page);
        $sections = [];
        $converted_sections = 0;

        foreach ($data['Sections'] as $section) {
            if (($section['Type'] ?? '') !== 'legacy') {
                $sections[] = $section;
                continue;
            }

            $imported = $this->import_page_html_to_editor_sections((string) ($section['LegacyHtml'] ?? ''));
            if (!$imported) {
                $sections[] = $section;
                continue;
            }
            foreach ($imported as $imported_section) {
                if (count($sections) >= 25) {
                    break;
                }
                $imported_section['Active'] = !empty($section['Active']);
                $sections[] = $imported_section;
                $converted_sections++;
            }
        }

        foreach ($sections as $index => &$section) {
            $section['Order'] = ($index + 1) * 10;
            if (strpos((string) ($section['Key'] ?? ''), 'importeret-') === 0) {
                $section['Key'] = 'importeret-' . str_pad((string) ($index + 1), 2, '0', STR_PAD_LEFT);
            }
        }
        unset($section);

        return $this->normalize_page_editor_data([
            'Version'        => '1.22',
            'PageSlug'       => $data['PageSlug'],
            'PageTitle'          => $data['PageTitle'],
            'ContentVersion'     => $data['ContentVersion'] ?? 0,
            'DataContextType'    => $data['DataContextType'] ?? '',
            'DataContextEntryId' => $data['DataContextEntryId'] ?? 0,
            'Sections'           => array_slice($sections, 0, 25),
        ], $page);
    }

    private function get_page_editor_data($slug, $page = null) {
        $slug = sanitize_title((string) $slug);
        if (!$page) {
            $page = $this->post_by_slug($slug);
        }

        $store = $this->get_page_editor_store();
        if (isset($store[$slug]) && is_array($store[$slug])) {
            return $this->normalize_page_editor_data($store[$slug], $page);
        }

        if ($page) {
            $marker_data = $this->decode_marker(self::PAGE_EDITOR_MARKER, $page->post_content);
            if (is_array($marker_data)) {
                return $this->normalize_page_editor_data($marker_data, $page);
            }

            $static_data = $this->decode_marker(self::STATIC_CONTENT_MARKER, $page->post_content);
            if ($slug === 'om-foreningen' && is_array($static_data)) {
                return $this->migrate_static_content_to_page_editor($page, $static_data);
            }

            $legacy = $this->extract_page_core_content($page->post_content);
            if ($legacy !== '') {
                $section = $this->default_page_section('legacy', 10);
                $section['Key'] = 'eksisterende-indhold';
                $section['Title'] = 'Eksisterende sideindhold';
                $section['LegacyHtml'] = $legacy;
                return $this->normalize_page_editor_data([
                    'PageSlug'  => $slug,
                    'PageTitle' => $page->post_title,
                    'Sections'  => [$section],
                ], $page);
            }
        }

        return $this->normalize_page_editor_data([
            'PageSlug'  => $slug,
            'PageTitle' => $page ? $page->post_title : ($this->editable_page_definitions()[$slug] ?? 'Side'),
            'Sections'  => [],
        ], $page);
    }

    private function save_page_editor_data($slug, array $data) {
        $store = $this->get_page_editor_store();
        $store[$slug] = $data;
        update_option(self::PAGE_EDITOR_OPTION, $store, false);
    }


    private function normalize_page_pattern_sections(array $raw_sections) {
        $raw_sections = array_slice($raw_sections, 0, 25);
        if (!$raw_sections) { throw new RuntimeException('Pattern skal indeholde mindst ét element.'); }
        foreach ($raw_sections as $raw_section) {
            if (!is_array($raw_section)) { continue; }
            $type = sanitize_key((string) ($raw_section['Type'] ?? 'text'));
            if (in_array($type, ['legacy','component'], true)) { throw new RuntimeException('Legacy og linked components kan ikke gemmes inde i et ikke-linked pattern.'); }
        }
        $data = $this->normalize_page_editor_data(['Version'=>'1.22','PageSlug'=>self::HOME_SLUG,'PageTitle'=>'Pattern','ContentVersion'=>0,'Sections'=>$raw_sections], null);
        $sections = array_values((array) $data['Sections']);
        $roots = array_values(array_filter($sections, static function($section){ return sanitize_key((string) ($section['LayoutParentKey'] ?? '')) === ''; }));
        if (count($roots) !== 1) { throw new RuntimeException('Et pattern skal have præcis ét root-element.'); }
        foreach ($sections as &$section) {
            $section['NavigatorLabel']=''; $section['NavigatorLocked']=false; $section['ComponentId']=''; $section['ComponentRevision']=0; $section['ComponentVariant']=''; $section['ComponentOverrides']=[];
        }
        unset($section);
        return $sections;
    }

    private function get_page_presets() {
        $stored = get_option(self::PAGE_PRESETS_OPTION, []);
        if (!is_array($stored)) { return []; }
        $presets=[];
        foreach (array_slice($stored,0,50,true) as $id=>$entry) {
            if (!is_array($entry)) { continue; }
            $raw_sections = isset($entry['Sections']) && is_array($entry['Sections']) ? $entry['Sections'] : (isset($entry['Section']) && is_array($entry['Section']) ? [$entry['Section']] : []);
            if (!$raw_sections) { continue; }
            $preset_id=sanitize_key((string)($entry['Id']??$id)); $name=sanitize_text_field((string)($entry['Name']??'Pattern'));
            if($preset_id===''||$name==='')continue;
            try{$sections=$this->normalize_page_pattern_sections($raw_sections);}catch(Throwable $e){$this->log('WARN','PAGE_PATTERN_INVALID',"{$preset_id}: ".$e->getMessage());continue;}
            $presets[$preset_id]=['Id'=>$preset_id,'Name'=>$name,'UpdatedUtc'=>sanitize_text_field((string)($entry['UpdatedUtc']??'')),'Sections'=>$sections,'Section'=>$sections[0]];
        }
        return $presets;
    }

    public function ajax_save_page_preset() {
        if (!current_user_can('edit_pages')) { wp_send_json_error(['message'=>'Du har ikke rettigheder til at gemme patterns.'],403); }
        check_ajax_referer('h18_page_presets_v051','nonce');
        $name=sanitize_text_field((string)wp_unslash($_POST['name']??'')); $name=function_exists('mb_substr')?mb_substr($name,0,80):substr($name,0,80);
        if($name==='')wp_send_json_error(['message'=>'Pattern skal have et navn.'],400);
        $sections_json=(string)wp_unslash($_POST['sections']??''); $section_json=(string)wp_unslash($_POST['section']??'');
        $json=$sections_json!==''?$sections_json:$section_json;
        if($json===''||strlen($json)>350000)wp_send_json_error(['message'=>'Patterndata mangler eller er for stor.'],400);
        $decoded=json_decode($json,true); if(!is_array($decoded)||json_last_error()!==JSON_ERROR_NONE)wp_send_json_error(['message'=>'Patterndata er ikke gyldig JSON.'],400);
        if($sections_json==='')$decoded=[$decoded];
        try{$sections=$this->normalize_page_pattern_sections($decoded);}catch(Throwable $e){wp_send_json_error(['message'=>$e->getMessage()],400);}
        $presets=$this->get_page_presets(); $preset_id=sanitize_key((string)wp_unslash($_POST['preset_id']??''));
        if($preset_id===''||!isset($presets[$preset_id]))$preset_id='preset-'.sanitize_key(wp_generate_uuid4());
        $entry=['Id'=>$preset_id,'Name'=>$name,'UpdatedUtc'=>gmdate('c'),'Sections'=>$sections,'Section'=>$sections[0]];
        $presets[$preset_id]=$entry; if(count($presets)>50)$presets=array_slice($presets,-50,null,true);
        update_option(self::PAGE_PRESETS_OPTION,$presets,false);
        $this->log('INFO','PAGE_PATTERN_SAVED',"Pattern '{$name}' gemt som {$preset_id} med ".count($sections).' element(er).');
        wp_send_json_success(['preset'=>$entry]);
    }

    public function ajax_delete_page_preset() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at slette patterns.'], 403);
        }
        check_ajax_referer('h18_page_presets_v051', 'nonce');

        $preset_id = sanitize_key((string) wp_unslash($_POST['preset_id'] ?? ''));
        $presets = $this->get_page_presets();
        if ($preset_id === '' || !isset($presets[$preset_id])) {
            wp_send_json_error(['message' => 'Pattern blev ikke fundet.'], 404);
        }
        $name = (string) $presets[$preset_id]['Name'];
        unset($presets[$preset_id]);
        update_option(self::PAGE_PRESETS_OPTION, $presets, false);
        $this->log('INFO', 'PAGE_PRESET_DELETED', "Pattern '{$name}' ({$preset_id}) blev slettet.");
        wp_send_json_success(['preset_id' => $preset_id]);
    }


    private function normalize_page_template_sections(array $raw_sections) {
        $raw_sections=array_slice($raw_sections,0,25); if(!$raw_sections)throw new RuntimeException('Sidetemplaten skal indeholde mindst ét element.');
        foreach($raw_sections as $raw_section){if(!is_array($raw_section))continue;$type=sanitize_key((string)($raw_section['Type']??'text'));if(in_array($type,['legacy','component'],true))throw new RuntimeException('Page Templates kan ikke indeholde legacy eller linked components; templaten skal være en selvstændig kopi.');}
        $data=$this->normalize_page_editor_data(['Version'=>'1.22','PageSlug'=>self::HOME_SLUG,'PageTitle'=>'Page Template','ContentVersion'=>0,'Sections'=>$raw_sections],null);
        $sections=array_values((array)$data['Sections']);
        foreach($sections as &$section){$section['ComponentId']='';$section['ComponentRevision']=0;$section['ComponentVariant']='';$section['ComponentOverrides']=[];}unset($section);
        return $sections;
    }

    private function get_page_templates() {
        $stored=get_option(self::PAGE_TEMPLATES_OPTION,[]);if(!is_array($stored))return[];$templates=[];
        foreach(array_slice($stored,0,30,true) as $id=>$entry){if(!is_array($entry)||empty($entry['Sections'])||!is_array($entry['Sections']))continue;$template_id=sanitize_key((string)($entry['Id']??$id));$name=sanitize_text_field((string)($entry['Name']??'Page Template'));if($template_id===''||$name==='')continue;try{$sections=$this->normalize_page_template_sections($entry['Sections']);}catch(Throwable $e){continue;}$templates[$template_id]=['Id'=>$template_id,'Name'=>$name,'PageTitle'=>sanitize_text_field((string)($entry['PageTitle']??$name)),'UpdatedUtc'=>sanitize_text_field((string)($entry['UpdatedUtc']??'')),'Sections'=>$sections];}
        return $templates;
    }

    private function get_page_template_usage($template_id) {
        $template_id=sanitize_key((string)$template_id);if($template_id==='')return[];$posts=get_posts(['post_type'=>'page','post_status'=>['publish','draft','private'],'posts_per_page'=>-1,'meta_key'=>'_h18_page_template_origin','meta_value'=>$template_id,'orderby'=>'title','order'=>'ASC']);$usage=[];
        foreach($posts as $page){if($page instanceof WP_Post)$usage[]=['PageId'=>(int)$page->ID,'PageSlug'=>(string)$page->post_name,'PageTitle'=>(string)$page->post_title];}
        return $usage;
    }

    private function get_page_templates_for_editor() {$templates=$this->get_page_templates();foreach($templates as $id=>&$template){$template['Usage']=$this->get_page_template_usage($id);$template['UsageCount']=count($template['Usage']);}unset($template);return$templates;}

    public function ajax_save_page_template() {
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at gemme Page Templates.'],403);check_ajax_referer('h18_page_templates_v0522','nonce');
        $name=sanitize_text_field((string)wp_unslash($_POST['name']??''));$page_title=sanitize_text_field((string)wp_unslash($_POST['page_title']??$name));$json=(string)wp_unslash($_POST['sections']??'');if($name===''||$json===''||strlen($json)>450000)wp_send_json_error(['message'=>'Template-navn eller indhold mangler.'],400);$raw=json_decode($json,true);if(!is_array($raw)||json_last_error()!==JSON_ERROR_NONE)wp_send_json_error(['message'=>'Template-data er ikke gyldig JSON.'],400);
        try{$sections=$this->normalize_page_template_sections($raw);}catch(Throwable $e){wp_send_json_error(['message'=>$e->getMessage()],400);}
        $templates=$this->get_page_templates();$id=sanitize_key((string)wp_unslash($_POST['template_id']??''));if($id===''||!isset($templates[$id]))$id='template-'.sanitize_key(wp_generate_uuid4());$entry=['Id'=>$id,'Name'=>$name,'PageTitle'=>$page_title!==''?$page_title:$name,'UpdatedUtc'=>gmdate('c'),'Sections'=>$sections];$templates[$id]=$entry;if(count($templates)>30)wp_send_json_error(['message'=>'Der kan højst gemmes 30 Page Templates.'],400);update_option(self::PAGE_TEMPLATES_OPTION,$templates,false);$entry['Usage']=$this->get_page_template_usage($id);$entry['UsageCount']=count($entry['Usage']);wp_send_json_success(['template'=>$entry]);
    }

    public function ajax_delete_page_template() {
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at slette Page Templates.'],403);check_ajax_referer('h18_page_templates_v0522','nonce');$id=sanitize_key((string)wp_unslash($_POST['template_id']??''));$templates=$this->get_page_templates();if($id===''||!isset($templates[$id]))wp_send_json_error(['message'=>'Page Template blev ikke fundet.'],404);unset($templates[$id]);update_option(self::PAGE_TEMPLATES_OPTION,$templates,false);wp_send_json_success(['template_id'=>$id]);
    }

    private function instantiate_page_template_sections(array $sections) {
        $map=[];foreach($sections as $section){$old=sanitize_key((string)($section['Key']??''));if($old!=='')$map[$old]='sektion-'.substr(md5(wp_generate_uuid4()),0,12);}$result=[];
        foreach($sections as $index=>$section){$old=sanitize_key((string)($section['Key']??''));$parent=sanitize_key((string)($section['LayoutParentKey']??''));$copy=$section;$copy['Key']=$map[$old]??('sektion-'.substr(md5(wp_generate_uuid4()),0,12));$copy['LayoutParentKey']=$parent!==''&&isset($map[$parent])?$map[$parent]:'';$copy['Order']=($index+1)*10;$copy['ComponentId']='';$copy['ComponentRevision']=0;$copy['ComponentVariant']='';$copy['ComponentOverrides']=[];$result[]=$copy;}
        return$result;
    }

    public function ajax_create_blank_page() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at oprette sider.'], 403);
        }
        check_ajax_referer('h18_page_templates_v0522', 'nonce');

        $title = sanitize_text_field((string) wp_unslash($_POST['page_title'] ?? ''));
        $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));

        if ($title === '' || $slug === '') {
            wp_send_json_error(['message' => 'Ny side skal have titel og slug.'], 400);
        }
        if (get_page_by_path($slug, OBJECT, 'page')) {
            wp_send_json_error(['message' => 'Der findes allerede en side med denne slug.'], 409);
        }

        $post_id = wp_insert_post([
            'post_type' => 'page',
            'post_status' => 'draft',
            'post_title' => $title,
            'post_name' => $slug,
            'post_content' => '',
        ], true);

        if (is_wp_error($post_id)) {
            wp_send_json_error(['message' => $post_id->get_error_message()], 400);
        }

        $page = get_post($post_id);
        update_post_meta($post_id, '_h18_page_editor_managed', '1');

        try {
            $data = $this->normalize_page_editor_data([
                'Version' => '1.22',
                'PageSlug' => $slug,
                'PageTitle' => $title,
                'ContentVersion' => 1,
                'DataContextType' => '',
                'DataContextEntryId' => 0,
                'Sections' => [],
            ], $page);

            $this->save_page_editor_data($slug, $data);
            $result = wp_update_post([
                'ID' => $post_id,
                'page_template' => 'default',
                'post_content' => $this->wrap_with_shell($this->build_page_editor_core($slug, $data), $post_id),
            ], true);

            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $this->log('INFO', 'PAGE_CREATE_BLANK', "Ny Hangar18-side '{$title}' ({$slug}) oprettet som kladde.");
            wp_send_json_success([
                'page_id' => $post_id,
                'page_slug' => $slug,
                'manager_url' => admin_url('admin.php?page=hangar18-pages&page_slug=' . rawurlencode($slug)),
                'edit_url' => get_edit_post_link($post_id, 'raw'),
            ]);
        } catch (Throwable $e) {
            wp_delete_post($post_id, true);
            wp_send_json_error(['message' => $e->getMessage()], 400);
        }
    }

    public function ajax_create_page_from_template() {
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at oprette sider.'],403);check_ajax_referer('h18_page_templates_v0522','nonce');$template_id=sanitize_key((string)wp_unslash($_POST['template_id']??''));$title=sanitize_text_field((string)wp_unslash($_POST['page_title']??''));$slug=sanitize_title((string)wp_unslash($_POST['page_slug']??''));$templates=$this->get_page_templates();if(!isset($templates[$template_id]))wp_send_json_error(['message'=>'Page Template blev ikke fundet.'],404);if($title===''||$slug==='')wp_send_json_error(['message'=>'Ny side skal have titel og slug.'],400);if(get_page_by_path($slug,OBJECT,'page'))wp_send_json_error(['message'=>'Der findes allerede en side med denne slug.'],409);
        $post_id=wp_insert_post(['post_type'=>'page','post_status'=>'draft','post_title'=>$title,'post_name'=>$slug,'post_content'=>''],true);if(is_wp_error($post_id))wp_send_json_error(['message'=>$post_id->get_error_message()],400);$page=get_post($post_id);update_post_meta($post_id,'_h18_page_editor_managed','1');
        try{$sections=$this->instantiate_page_template_sections($templates[$template_id]['Sections']);$data=$this->normalize_page_editor_data(['Version'=>'1.22','PageSlug'=>$slug,'PageTitle'=>$title,'ContentVersion'=>1,'Sections'=>$sections],$page);update_post_meta($post_id,'_h18_page_editor_managed','1');update_post_meta($post_id,'_h18_page_template_origin',$template_id);$this->save_page_editor_data($slug,$data);$result=wp_update_post(['ID'=>$post_id,'page_template'=>'default','post_content'=>$this->wrap_with_shell($this->build_page_editor_core($slug,$data),$post_id)],true);if(is_wp_error($result))throw new RuntimeException($result->get_error_message());wp_send_json_success(['page_id'=>$post_id,'page_slug'=>$slug,'manager_url'=>admin_url('admin.php?page=hangar18-pages&page_slug='.rawurlencode($slug)),'edit_url'=>get_edit_post_link($post_id,'raw')]);}
        catch(Throwable $e){wp_delete_post($post_id,true);wp_send_json_error(['message'=>$e->getMessage()],400);}
    }


    private function page_component_allowed_input_fields() {
        return ['Title', 'Content', 'MediaId', 'Button1Label', 'Button1Url', 'Button2Label', 'Button2Url'];
    }

    private function page_component_input_id($section_key, $field) {
        return 'input-' . substr(hash('sha256', sanitize_key((string) $section_key) . '|' . sanitize_key((string) $field)), 0, 16);
    }

    private function page_component_input_default(array $section, $field) {
        if ($field === 'MediaId') { return (string) absint($section['MediaId'] ?? 0); }
        return (string) ($section[$field] ?? '');
    }

    private function sanitize_page_component_override($field, $value) {
        if ($field === 'MediaId') { return absint($value); }
        if (in_array($field, ['Button1Url', 'Button2Url'], true)) { return esc_url_raw((string) $value); }
        if ($field === 'Content') { return wp_kses_post((string) $value); }
        return sanitize_text_field((string) $value);
    }

    private function normalize_page_component_definition(array $raw) {
        $raw_sections = isset($raw['Sections']) && is_array($raw['Sections']) ? array_slice($raw['Sections'], 0, 25) : [];
        if (!$raw_sections) { throw new RuntimeException('Komponenten skal indeholde mindst ét element.'); }
        foreach ($raw_sections as $raw_section) {
            if (!is_array($raw_section)) { continue; }
            $raw_type = sanitize_key((string) ($raw_section['Type'] ?? 'text'));
            if (in_array($raw_type, ['legacy', 'component', 'query_list'], true)) {
                throw new RuntimeException('Linked components kan ikke indeholde legacy-indhold, linked components eller Query List-elementer.');
            }
        }
        $normalized = $this->normalize_page_editor_data([
            'Version' => '1.17',
            'PageSlug' => self::HOME_SLUG,
            'PageTitle' => 'Linked component',
            'ContentVersion' => 0,
            'Sections' => $raw_sections,
        ], null);
        $sections = array_values((array) $normalized['Sections']);
        $roots = array_values(array_filter($sections, static function($section) {
            return sanitize_key((string) ($section['LayoutParentKey'] ?? '')) === '';
        }));
        if (count($roots) !== 1) {
            throw new RuntimeException('En linked component skal have præcis ét root-element.');
        }
        $section_by_key = [];
        foreach ($sections as &$section) {
            $section['ComponentId'] = '';
            $section['ComponentRevision'] = 0;
            $section['ComponentOverrides'] = [];
            $section_by_key[(string) $section['Key']] = $section;
        }
        unset($section);

        $inputs = [];
        $raw_inputs = isset($raw['Inputs']) && is_array($raw['Inputs']) ? array_slice($raw['Inputs'], 0, 40) : [];
        $allowed = $this->page_component_allowed_input_fields();
        foreach ($raw_inputs as $input) {
            if (!is_array($input)) { continue; }
            $section_key = sanitize_key((string) ($input['SectionKey'] ?? ''));
            $field = (string) ($input['Field'] ?? '');
            if ($section_key === '' || !isset($section_by_key[$section_key]) || !in_array($field, $allowed, true)) { continue; }
            $target = $section_by_key[$section_key];
            $target_type = (string) ($target['Type'] ?? 'text');
            if ($field === 'Content' && in_array($target_type, ['css','html','shortcode','embed'], true)) { continue; }
            if ($field === 'MediaId' && !in_array($target_type, ['hero','text_image','image'], true)) { continue; }
            if (in_array($field, ['Button1Label','Button1Url','Button2Label','Button2Url'], true) && !in_array($target_type, ['hero','buttons'], true)) { continue; }
            $input_id = $this->page_component_input_id($section_key, $field);
            $label = sanitize_text_field((string) ($input['Label'] ?? $field));
            if ($label === '') { $label = $field; }
            $inputs[$input_id] = [
                'InputId' => $input_id,
                'SectionKey' => $section_key,
                'Field' => $field,
                'Label' => $label,
            ];
        }
        return ['Sections' => $sections, 'Inputs' => array_values($inputs)];
    }


    private function normalize_page_component_variants($raw_variants, array $inputs, array $sections) {
        if(!is_array($raw_variants))return[];$input_map=[];foreach($inputs as $input){$id=sanitize_key((string)($input['InputId']??''));if($id!=='')$input_map[$id]=$input;}$section_map=[];foreach($sections as $section)$section_map[(string)$section['Key']]=$section;$variants=[];
        foreach(array_slice($raw_variants,0,12,true) as $id=>$variant){if(!is_array($variant))continue;$variant_id=sanitize_key((string)($variant['Id']??$id));$name=sanitize_text_field((string)($variant['Name']??'Variant'));if($variant_id===''||$name==='')continue;$values=[];$raw_values=isset($variant['Values'])&&is_array($variant['Values'])?$variant['Values']:[];foreach($raw_values as $input_id=>$value){$input_id=sanitize_key((string)$input_id);if(!isset($input_map[$input_id]))continue;$input=$input_map[$input_id];$field=(string)$input['Field'];$sanitized=$this->sanitize_page_component_override($field,$value);$section=$section_map[(string)$input['SectionKey']]??[];$base=$this->page_component_input_default($section,$field);if((string)$sanitized===(string)$base)continue;$values[$input_id]=$sanitized;}$variants[$variant_id]=['Id'=>$variant_id,'Name'=>$name,'Values'=>$values];}
        return$variants;
    }

    private function get_page_components() {
        $stored = get_option(self::PAGE_COMPONENTS_OPTION, []);
        if (!is_array($stored)) { return []; }
        $components = [];
        foreach (array_slice($stored, 0, 50, true) as $id => $entry) {
            if (!is_array($entry)) { continue; }
            $component_id = sanitize_key((string) ($entry['Id'] ?? $id));
            $name = sanitize_text_field((string) ($entry['Name'] ?? 'Linked component'));
            if ($component_id === '' || $name === '') { continue; }
            try {
                $definition = $this->normalize_page_component_definition([
                    'Sections' => $entry['Sections'] ?? [],
                    'Inputs' => $entry['Inputs'] ?? [],
                ]);
            } catch (Throwable $e) {
                $this->log('WARN', 'PAGE_COMPONENT_INVALID', "{$component_id}: " . $e->getMessage());
                continue;
            }
            $variants = $this->normalize_page_component_variants($entry['Variants'] ?? [], $definition['Inputs'], $definition['Sections']);
            $components[$component_id] = [
                'Id' => $component_id,
                'Name' => $name,
                'Revision' => max(1, (int) ($entry['Revision'] ?? 1)),
                'UpdatedUtc' => sanitize_text_field((string) ($entry['UpdatedUtc'] ?? '')),
                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
                'Variants' => $variants,
            ];
        }
        return $components;
    }

    private function get_page_component_usage($component_id) {
        $component_id = sanitize_key((string) $component_id);
        if ($component_id === '') { return []; }
        $usage = [];
        $store = $this->get_page_editor_store();
        $definitions = $this->editable_page_definitions();
        foreach ($store as $slug => $page_data) {
            if (!is_array($page_data) || empty($page_data['Sections']) || !is_array($page_data['Sections'])) { continue; }
            foreach ($page_data['Sections'] as $section) {
                if (!is_array($section)) { continue; }
                $reference_type = sanitize_key((string) ($section['Type'] ?? ''));
                if (!in_array($reference_type, ['component','query_list'], true)) { continue; }
                $referenced_component_id = $reference_type === 'query_list'
                    ? sanitize_key((string) ($section['QueryListComponentId'] ?? ''))
                    : sanitize_key((string) ($section['ComponentId'] ?? ''));
                if ($referenced_component_id !== $component_id) { continue; }
                $usage[] = [
                    'PageSlug' => sanitize_title((string) $slug),
                    'PageTitle' => sanitize_text_field((string) ($page_data['PageTitle'] ?? ($definitions[$slug] ?? $slug))),
                    'SectionKey' => sanitize_key((string) ($section['Key'] ?? '')),
                    'Variant' => sanitize_key((string) ($reference_type === 'query_list' ? ($section['QueryListComponentVariant'] ?? '') : ($section['ComponentVariant'] ?? ''))),
                    'ReferenceType' => $reference_type,
                ];
            }
        }
        return $usage;
    }

    private function get_page_components_for_editor() {
        $components = $this->get_page_components();
        foreach ($components as $id => &$component) {
            $component['Usage'] = $this->get_page_component_usage($id);
            $component['UsageCount'] = count($component['Usage']);
        }
        unset($component);
        return $components;
    }

    public function ajax_save_page_component() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at gemme linked components.'], 403);
        }
        check_ajax_referer('h18_page_components_v0521', 'nonce');
        $name = sanitize_text_field((string) wp_unslash($_POST['name'] ?? ''));
        $name = function_exists('mb_substr') ? mb_substr($name, 0, 80) : substr($name, 0, 80);
        $sections_json = (string) wp_unslash($_POST['sections'] ?? '');
        $inputs_json = (string) wp_unslash($_POST['inputs'] ?? '[]');
        if ($name === '') { wp_send_json_error(['message' => 'Komponenten skal have et navn.'], 400); }
        if ($sections_json === '' || strlen($sections_json) > 350000 || strlen($inputs_json) > 100000) {
            wp_send_json_error(['message' => 'Komponentdata mangler eller er for stor.'], 400);
        }
        $sections = json_decode($sections_json, true);
        $inputs = json_decode($inputs_json, true);
        if (!is_array($sections) || !is_array($inputs) || json_last_error() !== JSON_ERROR_NONE) {
            wp_send_json_error(['message' => 'Komponentdata er ikke gyldig JSON.'], 400);
        }
        try {
            $definition = $this->normalize_page_component_definition(['Sections' => $sections, 'Inputs' => $inputs]);
            $components = $this->get_page_components();
            $component_id = sanitize_key((string) wp_unslash($_POST['component_id'] ?? ''));
            $existing = ($component_id !== '' && isset($components[$component_id])) ? $components[$component_id] : null;
            if (!$existing) { $component_id = 'component-' . sanitize_key(wp_generate_uuid4()); }
            if ($existing) {
                $usage_before_update = $this->get_page_component_usage($component_id);
                if ($usage_before_update) {
                    $old_input_ids = array_values(array_filter(array_map(static function($input) { return sanitize_key((string) ($input['InputId'] ?? '')); }, (array) $existing['Inputs'])));
                    $new_input_ids = array_values(array_filter(array_map(static function($input) { return sanitize_key((string) ($input['InputId'] ?? '')); }, (array) $definition['Inputs'])));
                    sort($old_input_ids); sort($new_input_ids);
                    if ($old_input_ids !== $new_input_ids) {
                        throw new RuntimeException('Komponenten er i brug. Frigivne input-ID’er skal bevares ved global opdatering; opdater fra det oprindelige source-subtree eller fjern usage først.');
                    }
                }
            }
            $revision = $existing ? ((int) $existing['Revision'] + 1) : 1;
            $entry = [
                'Id' => $component_id,
                'Name' => $name,
                'Revision' => $revision,
                'UpdatedUtc' => gmdate('c'),
                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
                'Variants' => $existing ? ($existing['Variants'] ?? []) : [],
            ];
            $components[$component_id] = $entry;
            if (count($components) > 50) { throw new RuntimeException('Der kan højst gemmes 50 linked components.'); }
            update_option(self::PAGE_COMPONENTS_OPTION, $components, false);
            $entry['Usage'] = $this->get_page_component_usage($component_id);
            $entry['UsageCount'] = count($entry['Usage']);
            $this->log('INFO', 'PAGE_COMPONENT_SAVED', "Linked component '{$name}' {$component_id} revision {$revision} gemt atomisk.");
            wp_send_json_success(['component' => $entry]);
        } catch (Throwable $e) {
            wp_send_json_error(['message' => $e->getMessage()], 400);
        }
    }

    public function ajax_delete_page_component() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at slette linked components.'], 403);
        }
        check_ajax_referer('h18_page_components_v0521', 'nonce');
        $component_id = sanitize_key((string) wp_unslash($_POST['component_id'] ?? ''));
        $components = $this->get_page_components();
        if ($component_id === '' || !isset($components[$component_id])) {
            wp_send_json_error(['message' => 'Komponenten blev ikke fundet.'], 404);
        }
        $usage = $this->get_page_component_usage($component_id);
        if ($usage) {
            wp_send_json_error(['message' => 'Komponenten bruges stadig på ' . count($usage) . ' side(r) og kan ikke slettes.', 'usage' => $usage], 409);
        }
        $name = (string) $components[$component_id]['Name'];
        unset($components[$component_id]);
        update_option(self::PAGE_COMPONENTS_OPTION, $components, false);
        $this->log('INFO', 'PAGE_COMPONENT_DELETED', "Linked component '{$name}' ({$component_id}) blev slettet.");
        wp_send_json_success(['component_id' => $component_id]);
    }


    private function get_page_component_variant_usage($component_id,$variant_id){$usage=array_filter($this->get_page_component_usage($component_id),static function($item)use($variant_id){return sanitize_key((string)($item['Variant']??''))===sanitize_key((string)$variant_id);});return array_values($usage);}

    public function ajax_save_page_component_variant(){
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at gemme component variants.'],403);check_ajax_referer('h18_page_components_v0521','nonce');$component_id=sanitize_key((string)wp_unslash($_POST['component_id']??''));$variant_id=sanitize_key((string)wp_unslash($_POST['variant_id']??''));$name=sanitize_text_field((string)wp_unslash($_POST['name']??''));$json=(string)wp_unslash($_POST['values']??'{}');$components=$this->get_page_components();if(!isset($components[$component_id])||$name==='')wp_send_json_error(['message'=>'Komponent eller variantnavn mangler.'],400);$raw=json_decode($json,true);if(!is_array($raw)||json_last_error()!==JSON_ERROR_NONE)wp_send_json_error(['message'=>'Variantdata er ugyldig.'],400);$component=$components[$component_id];$input_map=[];foreach($component['Inputs'] as $input)$input_map[(string)$input['InputId']]=$input;$section_map=[];foreach($component['Sections'] as $section)$section_map[(string)$section['Key']]=$section;$values=[];foreach($raw as $input_id=>$value){$input_id=sanitize_key((string)$input_id);if(!isset($input_map[$input_id]))continue;$input=$input_map[$input_id];$field=(string)$input['Field'];$sanitized=$this->sanitize_page_component_override($field,$value);$base=$this->page_component_input_default($section_map[(string)$input['SectionKey']]??[],$field);if((string)$sanitized!==(string)$base)$values[$input_id]=$sanitized;}
        $variants=$component['Variants']??[];if($variant_id===''||!isset($variants[$variant_id]))$variant_id='variant-'.sanitize_key(wp_generate_uuid4());$variants[$variant_id]=['Id'=>$variant_id,'Name'=>$name,'Values'=>$values];if(count($variants)>12)wp_send_json_error(['message'=>'En komponent kan højst have 12 variants.'],400);$component['Variants']=$variants;$component['Revision']=(int)$component['Revision']+1;$component['UpdatedUtc']=gmdate('c');$components[$component_id]=$component;update_option(self::PAGE_COMPONENTS_OPTION,$components,false);$component['Usage']=$this->get_page_component_usage($component_id);$component['UsageCount']=count($component['Usage']);wp_send_json_success(['component'=>$component,'variant_id'=>$variant_id]);
    }

    public function ajax_delete_page_component_variant(){
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at slette component variants.'],403);check_ajax_referer('h18_page_components_v0521','nonce');$component_id=sanitize_key((string)wp_unslash($_POST['component_id']??''));$variant_id=sanitize_key((string)wp_unslash($_POST['variant_id']??''));$components=$this->get_page_components();if(!isset($components[$component_id])||empty($components[$component_id]['Variants'][$variant_id]))wp_send_json_error(['message'=>'Varianten blev ikke fundet.'],404);$usage=$this->get_page_component_variant_usage($component_id,$variant_id);if($usage)wp_send_json_error(['message'=>'Varianten bruges stadig på '.count($usage).' side(r).','usage'=>$usage],409);unset($components[$component_id]['Variants'][$variant_id]);$components[$component_id]['Revision']=(int)$components[$component_id]['Revision']+1;$components[$component_id]['UpdatedUtc']=gmdate('c');update_option(self::PAGE_COMPONENTS_OPTION,$components,false);wp_send_json_success(['component_id'=>$component_id,'variant_id'=>$variant_id]);
    }

    private function resolve_page_component_instance_sections($page_id, array $instance) {
        $component_id = sanitize_key((string) ($instance['ComponentId'] ?? ''));
        if ($component_id === '') { return [[], null]; }
        $components = $this->get_page_components();
        if (!isset($components[$component_id])) { return [[], null]; }
        $component = $components[$component_id];
        $sections = $component['Sections'];
        $variant_id = sanitize_key((string) ($instance['ComponentVariant'] ?? ''));
        $variant_values = ($variant_id !== '' && isset($component['Variants'][$variant_id]) && is_array($component['Variants'][$variant_id]['Values'] ?? null)) ? $component['Variants'][$variant_id]['Values'] : [];
        $local_overrides = isset($instance['ComponentOverrides']) && is_array($instance['ComponentOverrides']) ? $instance['ComponentOverrides'] : [];
        $overrides = array_replace($variant_values, $local_overrides);
        $section_index = [];
        foreach ($sections as $index => $section) { $section_index[(string) $section['Key']] = $index; }
        foreach ($component['Inputs'] as $input) {
            $input_id = sanitize_key((string) ($input['InputId'] ?? ''));
            $section_key = sanitize_key((string) ($input['SectionKey'] ?? ''));
            $field = (string) ($input['Field'] ?? '');
            if ($input_id === '' || !array_key_exists($input_id, $overrides) || !isset($section_index[$section_key])) { continue; }
            $value = $this->sanitize_page_component_override($field, $overrides[$input_id]);
            $target = &$sections[$section_index[$section_key]];
            $target[$field] = $value;
            if ($field === 'MediaId' && absint($value) > 0) { $target['MediaUrl'] = ''; }
            unset($target);
        }
        $prefix = 'cmp-' . substr(hash('sha256', (int) $page_id . '|' . sanitize_key((string) ($instance['Key'] ?? '')) . '|' . $component_id), 0, 12) . '-';
        $key_map = [];
        foreach ($sections as $section) { $key_map[(string) $section['Key']] = sanitize_key($prefix . (string) $section['Key']); }
        foreach ($sections as &$section) {
            $old_key = (string) $section['Key'];
            $old_parent = sanitize_key((string) ($section['LayoutParentKey'] ?? ''));
            $section['Key'] = $key_map[$old_key];
            $section['LayoutParentKey'] = $old_parent !== '' && isset($key_map[$old_parent]) ? $key_map[$old_parent] : '';
            $section['ComponentId'] = '';
            $section['ComponentRevision'] = 0;
            $section['ComponentVariant'] = '';
            $section['ComponentOverrides'] = [];
        }
        unset($section);
        return [$sections, $component];
    }

    private function page_module_storage_key($page_id, $section_key) {
        return substr(hash('sha256', (int) $page_id . '|' . sanitize_key((string) $section_key)), 0, 24);
    }

    private function find_page_module($page_id, $section_key, $expected_type, $must_be_active = true) {
        $page = get_post((int) $page_id);
        if (!$page instanceof WP_Post) {
            return [null, null];
        }
        $data = $this->get_page_editor_data($page->post_name, $page);
        foreach ($data['Sections'] as $section) {
            if (
                $section['Key'] === sanitize_key((string) $section_key) &&
                $section['Type'] === $expected_type &&
                (!$must_be_active || !empty($section['Active']))
            ) {
                return [$page, $section];
            }
        }
        return [$page, null];
    }

    private function page_editor_section_style(array $section) {
        $preset = (string) ($section['Background'] ?? 'White');
        $backgrounds = [
            'White' => 'var(--h18-color-background,#ffffff)',
            'OffWhite' => 'var(--h18-color-surface,#f2f0e8)',
            'Sand' => 'var(--h18-color-accent,#c3ae83)',
            'Olive' => 'var(--h18-color-primary,#30382a)',
            'Steel' => 'var(--h18-color-secondary,#525a5f)',
        ];
        $dark = in_array($preset, ['Olive', 'Steel'], true);
        if (($section['DesignMode'] ?? 'Global') === 'Custom') {
            $bg = (string) $section['CustomBackgroundColor'];
            $text = (string) $section['CustomTextColor'];
            $heading = (string) $section['CustomHeadingColor'];
        } else {
            $bg = $backgrounds[$preset] ?? $backgrounds['White'];
            $text = $dark ? 'var(--h18-color-light,#ffffff)' : 'var(--h18-color-text,#30382a)';
            $heading = $text;
        }
        $shadows = [
            'None' => 'none',
            'Soft' => '0 6px 18px rgba(0,0,0,.08)',
            'Medium' => '0 12px 30px rgba(0,0,0,.14)',
            'Strong' => '0 18px 44px rgba(0,0,0,.22)',
        ];
        $shadow = $shadows[$section['ShadowStyle'] ?? 'None'] ?? 'none';
        $body_font = ($section['SectionBodyFontFamily'] ?? 'Global') === 'Global' ? 'var(--h18-font-body,Segoe UI,Arial,sans-serif)' : $this->header_font_family_css($section['SectionBodyFontFamily']);
        $heading_font = ($section['SectionHeadingFontFamily'] ?? 'Global') === 'Global' ? 'var(--h18-font-heading,Segoe UI,Arial,sans-serif)' : $this->header_font_family_css($section['SectionHeadingFontFamily']);
        $body_size = (int) ($section['BodyFontSizePx'] ?? 0);
        $h1_size = (int) ($section['H1FontSizePx'] ?? 0);
        $h2_size = (int) ($section['H2FontSizePx'] ?? 0);
        $h3_size = (int) ($section['H3FontSizePx'] ?? 0);
        $opacity = max(0, min(100, (int) ($section['SectionOpacityPercent'] ?? 100))) / 100;
        $effect = (string) ($section['BackgroundEffect'] ?? 'None');
        $background_image_url = esc_url_raw((string) ($section['BackgroundImageUrl'] ?? ''));
        $background_media_id = absint($section['BackgroundMediaId'] ?? 0);
        if ($background_media_id > 0) {
            $resolved_background_url = wp_get_attachment_url($background_media_id);
            if ($resolved_background_url) {
                $background_image_url = esc_url_raw((string) $resolved_background_url);
            }
        }
        $effect_image = 'none';
        if ($effect === 'Gradient') {
            $effect_image = 'linear-gradient(' . (int) ($section['GradientAngleDeg'] ?? 135) . 'deg,' . (string) ($section['GradientStartColor'] ?? '#30382a') . ',' . (string) ($section['GradientEndColor'] ?? '#c3ae83') . ')';
        } elseif ($effect === 'Image' && $background_image_url !== '') {
            $effect_image = 'url(' . wp_json_encode($background_image_url) . ')';
        }
        $base_radius = (int) ($section['RadiusPx'] ?? 0);
        $radius_tl = (int) ($section['RadiusTopLeftPx'] ?? -1);
        $radius_tr = (int) ($section['RadiusTopRightPx'] ?? -1);
        $radius_br = (int) ($section['RadiusBottomRightPx'] ?? -1);
        $radius_bl = (int) ($section['RadiusBottomLeftPx'] ?? -1);
        $radius_tl = $radius_tl < 0 ? $base_radius : $radius_tl;
        $radius_tr = $radius_tr < 0 ? $base_radius : $radius_tr;
        $radius_br = $radius_br < 0 ? $base_radius : $radius_br;
        $radius_bl = $radius_bl < 0 ? $base_radius : $radius_bl;
        $hover_effect = (string) ($section['HoverEffect'] ?? 'None');
        $hover_style_custom = ($section['HoverStyleMode'] ?? 'Inherit') === 'Custom';
        $hover_background = $hover_style_custom ? (string) ($section['HoverBackgroundColor'] ?? '#ffffff') : $bg;
        $hover_text = $hover_style_custom ? (string) ($section['HoverTextColor'] ?? '#30382a') : $text;
        $hover_heading = $hover_style_custom ? (string) ($section['HoverHeadingColor'] ?? '#30382a') : $heading;
        $hover_border = $hover_style_custom ? (string) ($section['HoverBorderColor'] ?? '#c3ae83') : (string) ($section['CustomBorderColor'] ?? '#c3ae83');
        $hover_opacity = $hover_style_custom ? (max(0, min(100, (int) ($section['HoverOpacityPercent'] ?? 100))) / 100) : $opacity;
        $hover_background_image = $hover_style_custom ? 'none' : $effect_image;
        $transition_preset = (string) ($section['TransitionPreset'] ?? 'Inherit');
        $transition_css = 'var(--h18-motion-normal,220ms)';
        if ($transition_preset === 'Fast') { $transition_css = 'var(--h18-motion-fast,120ms)'; }
        elseif ($transition_preset === 'Slow') { $transition_css = 'var(--h18-motion-slow,420ms)'; }
        elseif ($transition_preset === 'Custom') { $transition_css = (int) ($section['HoverTransitionMs'] ?? 220) . 'ms'; }
        $focus_style = (string) ($section['FocusRingStyle'] ?? 'Global');
        $focus_color = $focus_style === 'Custom' ? (string) ($section['FocusRingColor'] ?? '#8b4a2b') : 'var(--h18-focus-ring,#8b4a2b)';
        $focus_width = $focus_style === 'Custom' ? (int) ($section['FocusRingWidthPx'] ?? 3) . 'px' : 'var(--h18-focus-ring-width,3px)';
        if ($focus_style === 'None') { $focus_width = '0px'; }
        $focus_offset = (int) ($section['FocusRingOffsetPx'] ?? 2) . 'px';
        $disabled_opacity = max(10, min(100, (int) ($section['DisabledOpacityPercent'] ?? 55))) / 100;
        $hover_y = '0px';
        $hover_scale = '1';
        $hover_shadow = $shadow;
        if ($hover_effect === 'Lift') {
            $hover_y = '-4px';
            $hover_shadow = '0 16px 38px rgba(0,0,0,.16)';
        } elseif ($hover_effect === 'Scale') {
            $hover_scale = '1.02';
            $hover_shadow = '0 12px 30px rgba(0,0,0,.14)';
        } elseif ($hover_effect === 'Shadow') {
            $hover_shadow = '0 18px 44px rgba(0,0,0,.22)';
        }
        $tablet_alignment = (string) ($section['TabletAlignment'] ?? 'Inherit');
        $tablet_align = $tablet_alignment === 'Center' ? 'center' : ($tablet_alignment === 'Left' ? 'left' : ($section['DesktopAlignment'] === 'Center' ? 'center' : 'left'));
        $tablet_justify = $tablet_align === 'center' ? 'center' : 'flex-start';
        $tablet_top = (int) ($section['TabletTopSpacingPx'] ?? -1);
        $tablet_bottom = (int) ($section['TabletBottomSpacingPx'] ?? -1);
        $tablet_pad = (int) ($section['TabletPaddingPx'] ?? -1);
        $tablet_pad_x = (int) ($section['TabletHorizontalPaddingPx'] ?? -1);
        if ($tablet_top < 0) { $tablet_top = (int) $section['TopSpacingPx']; }
        if ($tablet_bottom < 0) { $tablet_bottom = (int) $section['BottomSpacingPx']; }
        if ($tablet_pad < 0) { $tablet_pad = (int) $section['PaddingPx']; }
        if ($tablet_pad_x < 0) { $tablet_pad_x = (int) $section['HorizontalPaddingPx']; }
        return '--h18-top:' . (int) $section['TopSpacingPx'] . 'px;' .
            '--h18-bottom:' . (int) $section['BottomSpacingPx'] . 'px;' .
            '--h18-mobile-top:' . (int) $section['MobileTopSpacingPx'] . 'px;' .
            '--h18-mobile-bottom:' . (int) $section['MobileBottomSpacingPx'] . 'px;' .
            '--h18-pad:' . (int) $section['PaddingPx'] . 'px;' .
            '--h18-pad-x:' . (int) $section['HorizontalPaddingPx'] . 'px;' .
            '--h18-mobile-pad:' . (int) $section['MobilePaddingPx'] . 'px;' .
            '--h18-mobile-pad-x:' . (int) $section['MobileHorizontalPaddingPx'] . 'px;' .
            '--h18-radius:' . (int) $section['RadiusPx'] . 'px;' .
            '--h18-align:' . ($section['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
            '--h18-mobile-align:' . ($section['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';' .
            '--h18-justify:' . ($section['DesktopAlignment'] === 'Center' ? 'center' : 'flex-start') . ';' .
            '--h18-mobile-justify:' . ($section['MobileAlignment'] === 'Center' ? 'center' : 'flex-start') . ';' .
            '--h18-section-bg:' . $bg . ';' .
            '--h18-section-text:' . $text . ';' .
            '--h18-section-heading:' . $heading . ';' .
            '--h18-section-border:' . (string) $section['CustomBorderColor'] . ';' .
            '--h18-section-border-width:' . (int) $section['BorderWidthPx'] . 'px;' .
            '--h18-section-shadow:' . $shadow . ';' .
            '--h18-section-body-font:' . $body_font . ';' .
            '--h18-section-heading-font:' . $heading_font . ';' .
            '--h18-section-body-size:' . ($body_size > 0 ? $body_size . 'px' : 'var(--h18-font-body-size,16px)') . ';' .
            '--h18-section-h1-size:' . ($h1_size > 0 ? $h1_size . 'px' : 'clamp(2rem,5vw,var(--h18-font-h1-size,48px))') . ';' .
            '--h18-section-h2-size:' . ($h2_size > 0 ? $h2_size . 'px' : 'clamp(1.55rem,3.5vw,var(--h18-font-h2-size,32px))') . ';' .
            '--h18-section-h3-size:' . ($h3_size > 0 ? $h3_size . 'px' : 'clamp(1.2rem,2.5vw,var(--h18-font-h3-size,22px))') . ';' .
            '--h18-section-opacity:' . $opacity . ';' .
            '--h18-section-bg-image:' . $effect_image . ';' .
            '--h18-section-bg-position:' . strtolower((string) ($section['BackgroundImagePosition'] ?? 'Center')) . ';' .
            '--h18-section-bg-size:' . strtolower((string) ($section['BackgroundImageSize'] ?? 'Cover')) . ';' .
            '--h18-image-aspect:' . (($section['ImageAspectRatio'] ?? 'Auto') === 'Auto' ? 'auto' : str_replace(':', ' / ', (string) $section['ImageAspectRatio'])) . ';' .
            '--h18-image-fit:' . strtolower((string) ($section['ImageFit'] ?? 'Cover')) . ';' .
            '--h18-image-position:' . (int) ($section['ImageFocalXPercent'] ?? 50) . '% ' . (int) ($section['ImageFocalYPercent'] ?? 50) . '%;' .
            '--h18-image-height:' . (!empty($section['ImageAspectLocked']) && ($section['ImageAspectRatio'] ?? 'Auto') !== 'Auto' ? 'auto' : ((int) ($section['ImageHeightPx'] ?? 0) > 0 ? (int) $section['ImageHeightPx'] . 'px' : 'auto')) . ';' .
            '--h18-mobile-image-height:' . (!empty($section['ImageAspectLocked']) && ($section['ImageAspectRatio'] ?? 'Auto') !== 'Auto' ? 'auto' : ((int) ($section['MobileImageHeightPx'] ?? 0) > 0 ? (int) $section['MobileImageHeightPx'] . 'px' : 'auto')) . ';' .
            '--h18-element-width:' . (int) ($section['ElementWidthPercent'] ?? 100) . '%;' .
            '--h18-tablet-element-width:' . ((int) ($section['TabletWidthPercent'] ?? -1) >= 20 ? (int) $section['TabletWidthPercent'] . '%' : 'var(--h18-element-width,100%)') . ';' .
            '--h18-mobile-element-width:' . ((int) ($section['MobileWidthPercent'] ?? -1) >= 20 ? (int) $section['MobileWidthPercent'] . '%' : 'var(--h18-element-width,100%)') . ';' .
            '--h18-element-max-width:' . ((int) ($section['ElementMaxWidthPx'] ?? 0) > 0 ? (int) $section['ElementMaxWidthPx'] . 'px' : 'none') . ';' .
            '--h18-element-min-height:' . ((int) ($section['ElementMinHeightPx'] ?? 0) > 0 ? (int) $section['ElementMinHeightPx'] . 'px' : '0') . ';' .
            '--h18-tablet-element-min-height:' . ((int) ($section['TabletMinHeightPx'] ?? -1) >= 0 ? (int) $section['TabletMinHeightPx'] . 'px' : 'var(--h18-element-min-height,0)') . ';' .
            '--h18-mobile-element-min-height:' . ((int) ($section['MobileMinHeightPx'] ?? -1) >= 0 ? (int) $section['MobileMinHeightPx'] . 'px' : 'var(--h18-element-min-height,0)') . ';' .
            '--h18-image-width:' . (int) ($section['ImageWidthPercent'] ?? 100) . '%;' .
            '--h18-mobile-image-width:' . (int) ($section['MobileImageWidthPercent'] ?? 100) . '%;' .
            '--h18-image-max-width:' . ((int) ($section['ImageMaxWidthPx'] ?? 0) > 0 ? (int) $section['ImageMaxWidthPx'] . 'px' : 'none') . ';' .
            '--h18-radius-tl:' . $radius_tl . 'px;' .
            '--h18-radius-tr:' . $radius_tr . 'px;' .
            '--h18-radius-br:' . $radius_br . 'px;' .
            '--h18-radius-bl:' . $radius_bl . 'px;' .
            '--h18-tablet-top:' . $tablet_top . 'px;' .
            '--h18-tablet-bottom:' . $tablet_bottom . 'px;' .
            '--h18-tablet-pad:' . $tablet_pad . 'px;' .
            '--h18-tablet-pad-x:' . $tablet_pad_x . 'px;' .
            '--h18-tablet-align:' . $tablet_align . ';' .
            '--h18-tablet-justify:' . $tablet_justify . ';' .
            '--h18-desktop-transform-x:' . (int) ($section['DesktopTranslateXPx'] ?? 0) . 'px;' .
            '--h18-desktop-transform-y:' . (int) ($section['DesktopTranslateYPx'] ?? 0) . 'px;' .
            '--h18-desktop-transform-scale:' . ((int) ($section['DesktopScalePercent'] ?? 100) / 100) . ';' .
            '--h18-desktop-transform-rotate:' . (int) ($section['DesktopRotateDeg'] ?? 0) . 'deg;' .
            '--h18-tablet-transform-x:' . (int) ($section['TabletTranslateXPx'] ?? 0) . 'px;' .
            '--h18-tablet-transform-y:' . (int) ($section['TabletTranslateYPx'] ?? 0) . 'px;' .
            '--h18-tablet-transform-scale:' . ((int) ($section['TabletScalePercent'] ?? 100) / 100) . ';' .
            '--h18-tablet-transform-rotate:' . (int) ($section['TabletRotateDeg'] ?? 0) . 'deg;' .
            '--h18-mobile-transform-x:' . (int) ($section['MobileTranslateXPx'] ?? 0) . 'px;' .
            '--h18-mobile-transform-y:' . (int) ($section['MobileTranslateYPx'] ?? 0) . 'px;' .
            '--h18-mobile-transform-scale:' . ((int) ($section['MobileScalePercent'] ?? 100) / 100) . ';' .
            '--h18-mobile-transform-rotate:' . (int) ($section['MobileRotateDeg'] ?? 0) . 'deg;' .
            '--h18-transform-x:var(--h18-desktop-transform-x);' .
            '--h18-transform-y:var(--h18-desktop-transform-y);' .
            '--h18-transform-scale:var(--h18-desktop-transform-scale);' .
            '--h18-transform-rotate:var(--h18-desktop-transform-rotate);' .
            '--h18-hover-y:0px;' .
            '--h18-hover-scale:1;' .
            '--h18-hover-active-y:' . $hover_y . ';' .
            '--h18-hover-active-scale:' . $hover_scale . ';' .
            '--h18-hover-shadow:' . $hover_shadow . ';' .
            '--h18-hover-bg:' . $hover_background . ';' .
            '--h18-hover-bg-image:' . $hover_background_image . ';' .
            '--h18-hover-text:' . $hover_text . ';' .
            '--h18-hover-heading:' . $hover_heading . ';' .
            '--h18-hover-border:' . $hover_border . ';' .
            '--h18-hover-opacity:' . $hover_opacity . ';' .
            '--h18-hover-transition:' . (int) ($section['HoverTransitionMs'] ?? 220) . 'ms;' .
            '--h18-state-transition:' . $transition_css . ';' .
            '--h18-focus-color:' . $focus_color . ';' .
            '--h18-focus-width:' . $focus_width . ';' .
            '--h18-focus-offset:' . $focus_offset . ';' .
            '--h18-disabled-opacity:' . $disabled_opacity . ';';
    }

    private function page_editor_visibility_classes(array $section) {
        $classes = [];
        if (empty($section['ShowDesktop'])) { $classes[] = 'h18-hide-desktop'; }
        if (empty($section['ShowTablet'])) { $classes[] = 'h18-hide-tablet'; }
        if (empty($section['ShowMobile'])) { $classes[] = 'h18-hide-mobile'; }
        if (($section['HoverStyleMode'] ?? 'Inherit') === 'Custom') { $classes[] = 'h18-hover-style-custom'; }
        if (($section['ActiveEffect'] ?? 'None') === 'Press') { $classes[] = 'h18-active-effect-press'; }
        elseif (($section['ActiveEffect'] ?? 'None') === 'ScaleDown') { $classes[] = 'h18-active-effect-scale'; }
        return implode(' ', $classes);
    }

    private function render_page_editor_imported_group(array $section, $inner, $extra_class) {
        $background_class = strtolower((string) $section['Background']);
        $classes = 'h18-imported-group ' . implode(' ', array_map('sanitize_html_class', preg_split('/\s+/', trim((string) $extra_class)))) .
            ' h18-editor-section h18-editor-section--' . sanitize_html_class($background_class) . ' ' . $this->page_editor_visibility_classes($section);

        return '<div class="' . esc_attr($classes) . '" style="' .
            esc_attr($this->page_editor_section_style($section)) . '">' .
            (string) $inner . '</div>';
    }

    private function page_editor_frontend_css($page_id) {
        $id = (int) $page_id;
        $design = $this->get_header_design_settings();
        $mobile_breakpoint = (int) ($design['BreakpointMobileMaxPx'] ?? 782);
        $tablet_breakpoint = (int) ($design['BreakpointTabletMaxPx'] ?? 1199);
        $tablet_min = $mobile_breakpoint + 1;
        $desktop_min = $tablet_breakpoint + 1;
        return '<style id="h18-page-editor-style-' . $id . '">' .
            '.h18-editor-page{width:100%;box-sizing:border-box}.h18-editor-section{box-sizing:border-box;margin-top:var(--h18-top,0);margin-bottom:var(--h18-bottom,24px);padding:var(--h18-pad,0) var(--h18-pad-x,var(--h18-pad,0));border-radius:var(--h18-radius,0);text-align:var(--h18-align,left)}' .
            '.h18-editor-section--offwhite{background:#f2f0e8}.h18-editor-section--sand{background:#c3ae83;color:#30382a}.h18-editor-section--olive{background:#30382a;color:#fff}.h18-editor-section--steel{background:#525a5f;color:#fff}.h18-editor-section--olive h1,.h18-editor-section--olive h2,.h18-editor-section--olive h3,.h18-editor-section--steel h1,.h18-editor-section--steel h2,.h18-editor-section--steel h3{color:#fff}' .
            '.h18-editor-section h1,.h18-editor-section h2,.h18-editor-section h3{margin-top:0;color:#30382a}.h18-editor-section--olive h1,.h18-editor-section--olive h2,.h18-editor-section--olive h3,.h18-editor-section--steel h1,.h18-editor-section--steel h2,.h18-editor-section--steel h3{color:#fff}.h18-editor-section p:last-child{margin-bottom:0}.h18-editor-section .has-text-align-left,.h18-editor-section .has-text-align-center,.h18-editor-section .has-text-align-right{text-align:var(--h18-align,left)!important}' .
            '.h18-editor-card{border-top:4px solid #c3ae83}.h18-editor-highlight{border-left:5px solid #c3ae83}' .
            '.h18-editor-carousel{position:relative;outline:none}.h18-editor-carousel:focus-visible{outline:2px solid #2271b1;outline-offset:4px}.h18-editor-carousel-viewport{position:relative;overflow:hidden}.h18-editor-carousel-slide[hidden]{display:none!important}.h18-editor-carousel-arrow{position:absolute;top:50%;z-index:2;display:grid;place-items:center;width:44px;height:44px;margin-top:-22px;border:1px solid rgba(0,0,0,.18);border-radius:999px;background:rgba(255,255,255,.92);color:#30382a;font-size:30px;line-height:1;cursor:pointer}.h18-editor-carousel-arrow:focus-visible{outline:2px solid #2271b1;outline-offset:2px}.h18-editor-carousel-arrow:disabled{opacity:.35;cursor:not-allowed}.h18-editor-carousel-prev{left:12px}.h18-editor-carousel-next{right:12px}.h18-editor-carousel-dots{display:flex;justify-content:center;gap:8px;margin-top:12px}.h18-editor-carousel-dot{width:12px;height:12px;padding:0;border:1px solid currentColor;border-radius:999px;background:transparent;cursor:pointer}.h18-editor-carousel-dot[aria-current=true]{background:currentColor}.h18-editor-carousel-dot:focus-visible{outline:2px solid #2271b1;outline-offset:3px}@media(prefers-reduced-motion:reduce){.h18-editor-carousel *{scroll-behavior:auto!important;animation:none!important;transition:none!important}}' .
            '.h18-editor-tabs{display:grid;gap:0}.h18-editor-tabs-nav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:0;border-bottom:1px solid #c3c4c7}.h18-editor-tab{appearance:none;padding:10px 16px;border:1px solid transparent;border-bottom:0;border-radius:6px 6px 0 0;background:transparent;color:inherit;font:inherit;font-weight:700;cursor:pointer}.h18-editor-tab:hover{background:rgba(195,174,131,.14)}.h18-editor-tab[aria-selected=true]{border-color:#c3c4c7;background:#fff;color:#30382a}.h18-editor-tab:focus-visible{outline:2px solid #2271b1;outline-offset:2px}.h18-editor-tab-panel{margin-top:-1px;border-top-left-radius:0!important}.h18-editor-tab-panel[hidden]{display:none!important}.h18-editor-accordion{display:grid;gap:10px}.h18-editor-accordion-item{padding:0!important;overflow:hidden}.h18-editor-accordion-item summary{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:var(--h18-card-pad,20px);font-weight:700;cursor:pointer;list-style:none}.h18-editor-accordion-item summary::-webkit-details-marker{display:none}.h18-editor-accordion-item summary:after{content:"+";font-size:1.35em;line-height:1}.h18-editor-accordion-item[open] summary:after{content:"−"}.h18-editor-accordion-item summary:focus-visible{outline:2px solid #2271b1;outline-offset:-3px}.h18-editor-accordion-body{padding:0 var(--h18-card-pad,20px) var(--h18-card-pad,20px)}' .
            '.h18-editor-card-grid{display:grid;grid-template-columns:repeat(var(--h18-grid-columns,3),minmax(0,1fr));gap:var(--h18-grid-gap,16px);align-items:stretch}.h18-editor-grid-card{box-sizing:border-box;padding:var(--h18-card-pad,26px);border:var(--h18-card-border-width,0) solid var(--h18-card-border,#c3ae83);border-radius:var(--h18-card-radius,7px);text-align:var(--h18-card-align,left)}.h18-editor-grid-card h3{margin:0 0 12px;color:inherit}.h18-editor-grid-card--white{background:#fff}.h18-editor-grid-card--offwhite{background:#f2f0e8}.h18-editor-grid-card--sand{background:#c3ae83}.h18-editor-grid-card--olive{background:#30382a}.h18-editor-grid-card--steel{background:#525a5f}.h18-editor-grid-card--tone-dark{color:#30382a}.h18-editor-grid-card--tone-light{color:#fff}.h18-editor-grid-card--tone-light h3{color:#fff}' .
            '.h18-editor-text-image{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,.8fr);gap:28px;align-items:center}.h18-editor-text-image--left .h18-editor-media{order:-1}' .
            '.h18-editor-media img,.h18-editor-image img{display:block;width:var(--h18-image-width,100%);max-width:var(--h18-image-max-width,none);height:var(--h18-image-height,auto);margin-inline:auto;aspect-ratio:var(--h18-image-aspect,auto);object-fit:var(--h18-image-fit,cover);object-position:var(--h18-image-position,50% 50%);border-radius:inherit}.h18-editor-actions{display:flex;gap:12px;flex-wrap:wrap;justify-content:var(--h18-justify,flex-start)}' .
            '.h18-editor-hero{position:relative;display:grid;min-height:var(--h18-hero-height,320px);place-items:center;overflow:hidden;background-position:center;background-repeat:no-repeat;background-size:cover}.h18-editor-hero:before{position:absolute;inset:0;content:"";background:#20261d;opacity:var(--h18-overlay-opacity,.35)}.h18-editor-hero-inner{position:relative;z-index:1;width:min(100%,920px)}.h18-editor-hero .h18-editor-actions{margin-top:20px}.h18-editor-page .h18-editor-hero .h18-editor-hero-inner .wp-block-cover{display:block!important;min-height:0!important;padding:0!important;background:none!important}.h18-editor-page .h18-editor-hero .h18-editor-hero-inner .wp-block-cover__image-background,.h18-editor-page .h18-editor-hero .h18-editor-hero-inner .wp-block-cover__background{display:none!important}' .
            '.h18-editor-page .wp-block-columns{display:flex;align-items:stretch;gap:16px}.h18-editor-page .wp-block-column{flex:1 1 0;min-width:0}.h18-editor-page .wp-block-button__link{display:inline-flex;align-items:center;justify-content:center;text-decoration:none}' .
            '.h18-imported-group{box-sizing:border-box;width:100%}.h18-imported-group>.h18-editor-section{margin:0!important;padding:0!important;border-radius:0!important;background:transparent!important;text-align:var(--h18-align,left)!important}.h18-imported-composite .h18-editor-actions{justify-content:var(--h18-justify,flex-start)!important;margin-top:22px}.h18-editor-page .h18-imported-tagline.h18-imported-group{margin-top:var(--h18-top,0)!important;margin-bottom:var(--h18-bottom,0)!important}.h18-imported-group .h18-editor-button{min-height:52px;padding:13px 24px;border:0;border-radius:29px}.h18-imported-group.h18-editor-section--offwhite .h18-editor-button,.h18-imported-group.h18-editor-section--sand .h18-editor-button{background:#30382a;color:#fff}.h18-imported-group.h18-editor-section--olive .h18-editor-button{background:#c3ae83;color:#30382a}' .
            '.h18-editor-button{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:10px 20px;border:1px solid #c3ae83;border-radius:5px;background:#c3ae83;color:#20261d;text-decoration:none;font-weight:700}.h18-editor-button--secondary{background:transparent;color:inherit}' .
            '.h18-layout-children{box-sizing:border-box;min-width:0;gap:var(--h18-layout-gap,16px)}.h18-layout-container-children{display:grid;grid-template-columns:minmax(0,1fr)}.h18-layout-flex-children{display:flex;flex-direction:var(--h18-layout-direction,row);flex-wrap:var(--h18-layout-wrap,wrap);justify-content:var(--h18-layout-justify,flex-start);align-items:var(--h18-layout-align,stretch)}.h18-layout-grid-children{display:grid;grid-template-columns:repeat(var(--h18-layout-columns,2),minmax(0,1fr));align-items:var(--h18-layout-align,stretch)}.h18-layout-children>.h18-editor-section{min-width:0;margin-top:var(--h18-top,0);margin-bottom:var(--h18-bottom,24px);padding:var(--h18-pad,0) var(--h18-pad-x,var(--h18-pad,0));text-align:var(--h18-align,left)}@media(max-width:' . $mobile_breakpoint . 'px){.h18-layout-children{gap:var(--h18-layout-mobile-gap,12px)}.h18-layout-flex-children{flex-direction:var(--h18-layout-mobile-direction,column)}.h18-layout-grid-children{grid-template-columns:repeat(var(--h18-layout-mobile-columns,1),minmax(0,1fr))}}' .
            '.h18-page-form,.h18-page-poll{max-width:760px;margin-inline:auto;text-align:left}.h18-page-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.h18-page-form-field{display:flex;flex-direction:column;gap:6px}.h18-page-form-field--wide{grid-column:1/-1}.h18-page-form input,.h18-page-form textarea{box-sizing:border-box;width:100%;padding:11px;border:1px solid #8c8f94;border-radius:4px}.h18-page-form input[type=checkbox]{width:auto;padding:0}.h18-page-form button,.h18-page-poll button{min-height:44px;padding:10px 20px;border:0;border-radius:5px;background:#c3ae83;color:#20261d;font-weight:700;cursor:pointer}' .
            '.h18-module-message{padding:12px 14px;margin-bottom:16px;border-left:4px solid #2271b1;background:#f0f6fc}.h18-module-message--success{border-color:#2e7d32;background:#edf7ed}.h18-module-message--error{border-color:#b32d2e;background:#fcf0f1}' .
            '.h18-poll-options{display:grid;gap:10px;margin:18px 0}.h18-poll-option{display:flex;align-items:center;gap:9px}.h18-poll-results{display:grid;gap:10px;margin-top:20px}.h18-poll-result-bar{height:10px;background:#dcdcde;border-radius:99px;overflow:hidden}.h18-poll-result-bar span{display:block;height:100%;background:#c3ae83}' .
            '.h18-editor-icon{display:inline-flex;align-items:center;justify-content:center;font-size:clamp(42px,6vw,84px);line-height:1;color:var(--h18-section-heading,currentColor)}.h18-safe-icon-svg{display:block;width:1em;height:1em}.h18-editor-icon-copy{margin-top:12px}.h18-editor-divider{width:100%;height:0;margin:0;border:0;border-top:var(--h18-section-border-width,2px) solid var(--h18-section-border,#c3ae83)}.h18-editor-divider--dashed{border-top-style:dashed}.h18-editor-divider--dotted{border-top-style:dotted}.h18-editor-divider--double{border-top-style:double;border-top-width:max(3px,var(--h18-section-border-width,3px))}.h18-editor-list>ul,.h18-editor-list>ol{margin:0;padding-left:1.5em}.h18-editor-list-checks{list-style:none!important;padding-left:0!important}.h18-editor-list-checks li{position:relative;padding-left:1.7em}.h18-editor-list-checks li:before{position:absolute;left:0;content:"✓";font-weight:800}.h18-editor-badge{display:inline-flex;align-items:center;min-height:30px;padding:5px 12px;border-radius:999px;background:var(--h18-section-heading,#30382a);color:var(--h18-section-bg,#fff);font-size:.88em;font-weight:700;line-height:1.2}.h18-editor-badge--outline{background:transparent;color:inherit;border:1px solid currentColor}.h18-editor-quote{margin:0;padding:18px 22px;border-left:4px solid var(--h18-section-border,#c3ae83)}.h18-editor-quote blockquote{margin:0;font-size:1.15em}.h18-editor-quote--large blockquote{font-size:clamp(1.35em,2.6vw,2em);line-height:1.35}.h18-editor-quote figcaption{margin-top:12px;font-weight:600}.h18-editor-embed{position:relative;max-width:100%;overflow:hidden}.h18-editor-embed iframe,.h18-editor-embed video{max-width:100%}.h18-editor-shortcode-locked{white-space:pre-wrap;padding:12px;border:1px dashed #b32d2e;background:#fcf0f1}' .
            '.h18-editor-spacer{height:var(--h18-spacer,32px)}' .
            ':is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section){box-sizing:border-box;width:var(--h18-element-width,100%);max-width:var(--h18-element-max-width,none);min-height:var(--h18-element-min-height,0);margin-left:auto;margin-right:auto;background-color:var(--h18-section-bg)!important;background-image:var(--h18-section-bg-image,none);background-position:var(--h18-section-bg-position,center);background-size:var(--h18-section-bg-size,cover);background-repeat:no-repeat;color:var(--h18-section-text)!important;border:var(--h18-section-border-width,0) solid var(--h18-section-border,transparent);border-radius:var(--h18-radius-tl,var(--h18-radius,0)) var(--h18-radius-tr,var(--h18-radius,0)) var(--h18-radius-br,var(--h18-radius,0)) var(--h18-radius-bl,var(--h18-radius,0));box-shadow:var(--h18-section-shadow,none);opacity:var(--h18-section-opacity,1);font-family:var(--h18-section-body-font);font-size:var(--h18-section-body-size);transform:translate(var(--h18-transform-x,0px),var(--h18-transform-y,0px)) translateY(var(--h18-hover-y,0px)) scale(var(--h18-transform-scale,1)) scale(var(--h18-hover-scale,1)) rotate(var(--h18-transform-rotate,0deg));transition:transform var(--h18-hover-transition,220ms) ease,box-shadow var(--h18-hover-transition,220ms) ease,opacity var(--h18-hover-transition,220ms) ease,background-color var(--h18-hover-transition,220ms) ease,color var(--h18-hover-transition,220ms) ease,border-color var(--h18-hover-transition,220ms) ease}' .
            '@media(hover:hover){:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section):hover{--h18-hover-y:var(--h18-hover-active-y,0px);--h18-hover-scale:var(--h18-hover-active-scale,1);background-color:var(--h18-hover-bg,var(--h18-section-bg))!important;background-image:var(--h18-hover-bg-image,var(--h18-section-bg-image,none));color:var(--h18-hover-text,var(--h18-section-text))!important;border-color:var(--h18-hover-border,var(--h18-section-border,transparent));opacity:var(--h18-hover-opacity,var(--h18-section-opacity,1));box-shadow:var(--h18-hover-shadow,var(--h18-section-shadow,none))}:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section):hover h1,:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section):hover h2,:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section):hover h3{color:var(--h18-hover-heading,var(--h18-section-heading))!important}:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section):hover .h18-editor-grid-card h3{color:inherit!important}body.page .h18-editor-page .h18-hover-style-custom:hover{background-image:none!important}}' .
            '.h18-editor-section :is(a,button,input,select,textarea,[tabindex]):focus-visible{outline:var(--h18-focus-width,var(--h18-focus-ring-width,3px)) solid var(--h18-focus-color,var(--h18-focus-ring,#8b4a2b));outline-offset:var(--h18-focus-offset,2px);transition:outline-color var(--h18-state-transition,var(--h18-motion-normal,220ms)) ease,box-shadow var(--h18-state-transition,var(--h18-motion-normal,220ms)) ease}.h18-editor-section.h18-active-effect-press :is(a,button,[role=button]):active{transform:translateY(1px)}.h18-editor-section.h18-active-effect-scale :is(a,button,[role=button]):active{transform:scale(.97)}.h18-editor-section :is(button,input,select,textarea):disabled,.h18-editor-section [aria-disabled=true]{opacity:var(--h18-disabled-opacity,.55);cursor:not-allowed}.h18-editor-section :is(a,button,[role=button]){transition-duration:var(--h18-state-transition,var(--h18-motion-normal,220ms))}' .
            '@media(prefers-reduced-motion:reduce){:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section){transition:none!important}:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section):hover{--h18-hover-y:0px;--h18-hover-scale:1}}' .
            '@media(min-width:' . $desktop_min . 'px){body.page .h18-editor-page .h18-hide-desktop{display:none!important}}' .
            '@media(min-width:' . $tablet_min . 'px) and (max-width:' . $tablet_breakpoint . 'px){body.page .h18-editor-page .h18-hide-tablet{display:none!important}:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section){margin-top:var(--h18-tablet-top,var(--h18-top,0));margin-bottom:var(--h18-tablet-bottom,var(--h18-bottom,24px));padding:var(--h18-tablet-pad,var(--h18-pad,0)) var(--h18-tablet-pad-x,var(--h18-pad-x,var(--h18-pad,0)));text-align:var(--h18-tablet-align,var(--h18-align,left));width:var(--h18-tablet-element-width,var(--h18-element-width,100%));min-height:var(--h18-tablet-element-min-height,var(--h18-element-min-height,0));--h18-transform-x:var(--h18-tablet-transform-x);--h18-transform-y:var(--h18-tablet-transform-y);--h18-transform-scale:var(--h18-tablet-transform-scale);--h18-transform-rotate:var(--h18-tablet-transform-rotate)}:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) .has-text-align-left,:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) .has-text-align-center,:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) .has-text-align-right{ text-align:var(--h18-tablet-align,var(--h18-align,left))!important}body.page .h18-editor-page>.h18-imported-group>.h18-editor-section{text-align:var(--h18-tablet-align,var(--h18-align,left))!important}body.page .h18-editor-page>.h18-imported-composite .h18-editor-actions,:is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) .h18-editor-actions{justify-content:var(--h18-tablet-justify,var(--h18-justify,flex-start))!important}}' .
            ':is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) h1{color:var(--h18-section-heading)!important;font-family:var(--h18-section-heading-font);font-size:var(--h18-section-h1-size)}' .
            ':is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) h2{color:var(--h18-section-heading)!important;font-family:var(--h18-section-heading-font);font-size:var(--h18-section-h2-size)}' .
            ':is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) h3{color:var(--h18-section-heading)!important;font-family:var(--h18-section-heading-font);font-size:var(--h18-section-h3-size)}' .
            ':is(body.page .h18-editor-page>.h18-editor-section,body.page .h18-editor-page .h18-layout-children>.h18-editor-section) .h18-editor-grid-card h3{color:inherit!important}' .
            '@media(max-width:' . $mobile_breakpoint . 'px){body.page .h18-editor-page .h18-hide-mobile{display:none!important}.h18-editor-section{margin-top:var(--h18-mobile-top,0);margin-bottom:var(--h18-mobile-bottom,18px);padding:var(--h18-mobile-pad,0) var(--h18-mobile-pad-x,var(--h18-mobile-pad,0));text-align:var(--h18-mobile-align,center);width:var(--h18-mobile-element-width,var(--h18-element-width,100%));min-height:var(--h18-mobile-element-min-height,var(--h18-element-min-height,0));--h18-transform-x:var(--h18-mobile-transform-x);--h18-transform-y:var(--h18-mobile-transform-y);--h18-transform-scale:var(--h18-mobile-transform-scale);--h18-transform-rotate:var(--h18-mobile-transform-rotate)}.h18-editor-section .has-text-align-left,.h18-editor-section .has-text-align-center,.h18-editor-section .has-text-align-right{ text-align:var(--h18-mobile-align,center)!important}.h18-imported-group>.h18-editor-section{text-align:var(--h18-mobile-align,center)!important}.h18-imported-composite .h18-editor-actions{justify-content:var(--h18-mobile-justify,center)!important}.h18-editor-text-image{grid-template-columns:1fr}.h18-editor-text-image .h18-editor-media{order:-1}.h18-editor-media img,.h18-editor-image img{width:var(--h18-mobile-image-width,var(--h18-image-width,100%));height:var(--h18-mobile-image-height,var(--h18-image-height,auto))}.h18-page-form-grid{grid-template-columns:1fr}.h18-editor-actions{justify-content:var(--h18-mobile-justify,center)}.h18-editor-spacer{height:var(--h18-mobile-spacer,24px)}.h18-editor-hero{min-height:var(--h18-mobile-hero-height,220px)}.h18-editor-card-grid{grid-template-columns:repeat(var(--h18-mobile-grid-columns,1),minmax(0,1fr));gap:var(--h18-mobile-grid-gap,14px)}.h18-editor-grid-card{padding:var(--h18-card-mobile-pad,20px);text-align:var(--h18-card-mobile-align,left)}.h18-editor-page .wp-block-columns{flex-direction:column}}' .
            '</style>';
    }

    private function format_page_section_content($content) {
        return wpautop(wp_kses_post((string) $content));
    }

    private function poll_option_id($label) {
        return substr(hash('sha256', (string) $label), 0, 16);
    }

    private function get_poll_state($storage_key, array $options) {
        $all = get_option(self::POLL_VOTES_OPTION, []);
        $state = is_array($all) && isset($all[$storage_key]) && is_array($all[$storage_key])
            ? $all[$storage_key]
            : [];
        $counts = isset($state['Counts']) && is_array($state['Counts']) ? $state['Counts'] : [];
        foreach ($options as $option) {
            $id = $this->poll_option_id($option);
            if (!isset($counts[$id])) {
                $counts[$id] = 0;
            }
        }
        return [
            'Counts' => $counts,
            'Voters' => isset($state['Voters']) && is_array($state['Voters']) ? $state['Voters'] : [],
            'UpdatedUtc' => (string) ($state['UpdatedUtc'] ?? ''),
        ];
    }

    private function is_poll_closed(array $section) {
        $now = time();
        $start = $section['StartUtc'] !== '' ? strtotime($section['StartUtc']) : false;
        $end = $section['EndUtc'] !== '' ? strtotime($section['EndUtc']) : false;
        return ($start !== false && $now < $start) || ($end !== false && $now > $end);
    }

    private function render_poll_results(array $section, array $state) {
        $total = 0;
        foreach ($section['PollOptions'] as $option) {
            $total += (int) ($state['Counts'][$this->poll_option_id($option)] ?? 0);
        }
        $html = '<div class="h18-poll-results"><strong>Resultat – ' . esc_html($total) . ' stemmer</strong>';
        foreach ($section['PollOptions'] as $option) {
            $count = (int) ($state['Counts'][$this->poll_option_id($option)] ?? 0);
            $percent = $total > 0 ? round(($count / $total) * 100, 1) : 0;
            $html .= '<div><div><span>' . esc_html($option) . '</span> <strong>' . esc_html($count) . ' (' . esc_html($percent) . '%)</strong></div>' .
                '<div class="h18-poll-result-bar"><span style="width:' . esc_attr($percent) . '%"></span></div></div>';
        }
        return $html . '</div>';
    }



    private function query_list_query_from_section(array $section) {
        return [
            'Type' => (string) ($section['QueryListType'] ?? ''),
            'Field' => (string) ($section['QueryListFilterField'] ?? ''),
            'Operator' => (string) ($section['QueryListFilterOperator'] ?? 'eq'),
            'Value' => (string) ($section['QueryListFilterValue'] ?? ''),
            'Sort' => (string) ($section['QueryListSort'] ?? 'modified'),
            'Order' => (string) ($section['QueryListOrder'] ?? 'DESC'),
            'Limit' => (int) ($section['QueryListLimit'] ?? 10),
        ];
    }

    private function render_page_editor_query_list($page_id, array $section) {
        $component_id = sanitize_key((string) ($section['QueryListComponentId'] ?? ''));
        if ($component_id === '') {
            return current_user_can('edit_pages') ? '<div class="h18-query-list-error">Query List mangler en template-komponent.</div>' : '';
        }
        if (in_array($component_id, $this->active_query_list_stack, true) || count($this->active_query_list_stack) >= 3) {
            return current_user_can('edit_pages') ? '<div class="h18-query-list-error">Query List-loop blev blokeret.</div>' : '';
        }

        try {
            $normalized = null;
            $posts = $this->run_custom_data_query($this->query_list_query_from_section($section), $normalized);
        } catch (Throwable $e) {
            return current_user_can('edit_pages') ? '<div class="h18-query-list-error">' . esc_html($e->getMessage()) . '</div>' : '';
        }

        $background_class = strtolower((string) ($section['Background'] ?? 'White'));
        $classes = trim('h18-editor-section h18-editor-query-list h18-editor-section--' . sanitize_html_class($background_class) . ' ' . $this->page_editor_visibility_classes($section));
        $id = 'h18-section-' . sanitize_html_class((string) ($section['Key'] ?? 'query-list'));
        $style = $this->page_editor_section_style($section);
        $columns = $this->clamp_int($section['QueryListColumns'] ?? 1, 1, 6, 1);
        $mobile_columns = $this->clamp_int($section['QueryListMobileColumns'] ?? 1, 1, 2, 1);
        $gap = $this->clamp_int($section['QueryListGapPx'] ?? 18, 0, 80, 18);
        $mobile_gap = $this->clamp_int($section['QueryListMobileGapPx'] ?? 14, 0, 60, 14);
        $design = $this->get_header_design_settings();
        $mobile_breakpoint = (int) ($design['BreakpointMobileMaxPx'] ?? 782);
        $title_html = trim((string) ($section['Title'] ?? '')) !== '' ? '<h2>' . esc_html((string) $section['Title']) . '</h2>' : '';
        $empty_text = sanitize_text_field((string) ($section['QueryListEmptyText'] ?? 'Ingen resultater.'));
        $query_hash = substr(hash('sha256', wp_json_encode($normalized) . '|' . $component_id . '|' . sanitize_key((string) ($section['QueryListComponentVariant'] ?? ''))), 0, 16);
        $responsive_css = '<style>@media(max-width:' . $mobile_breakpoint . 'px){#' . esc_attr($id) . '>.h18-query-list-items{grid-template-columns:repeat(' . $mobile_columns . ',minmax(0,1fr));gap:' . $mobile_gap . 'px}}</style>';

        if (!$posts) {
            return $responsive_css . '<section id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" style="' . esc_attr($style) . '" data-query-hash="' . esc_attr($query_hash) . '">' . $title_html . '<p class="h18-query-list-empty">' . esc_html($empty_text) . '</p></section>';
        }

        $previous_context = $this->active_dynamic_data_context;
        $this->active_query_list_stack[] = $component_id;
        $items = '';
        try {
            foreach ($posts as $post) {
                if (!$post instanceof WP_Post) { continue; }
                $context = $this->resolve_dynamic_data_context((string) $normalized['Type'], (int) $post->ID);
                if (!is_array($context)) { continue; }
                $instance = [
                    'Key' => sanitize_key((string) ($section['Key'] ?? 'query-list') . '-entry-' . (int) $post->ID),
                    'ComponentId' => $component_id,
                    'ComponentRevision' => 0,
                    'ComponentVariant' => sanitize_key((string) ($section['QueryListComponentVariant'] ?? '')),
                    'ComponentOverrides' => [],
                ];
                [$component_sections, $component] = $this->resolve_page_component_instance_sections($page_id, $instance);
                if (!$component || !$component_sections) { continue; }
                $this->active_dynamic_data_context = $context;
                $items .= '<div class="h18-query-list-item" data-entry-id="' . (int) $post->ID . '" data-component-id="' . esc_attr($component_id) . '">' . $this->render_page_editor_layout_tree($page_id, $component_sections) . '</div>';
            }
        } finally {
            $this->active_dynamic_data_context = $previous_context;
            array_pop($this->active_query_list_stack);
        }

        if ($items === '') {
            $items = '<p class="h18-query-list-empty">' . esc_html($empty_text) . '</p>';
        } else {
            $items = '<div class="h18-query-list-items" style="display:grid;grid-template-columns:repeat(' . $columns . ',minmax(0,1fr));gap:' . $gap . 'px">' . $items . '</div>';
        }
        return $responsive_css . '<section id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" style="' . esc_attr($style) . '" data-query-hash="' . esc_attr($query_hash) . '">' . $title_html . $items . '</section>';
    }


    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
        if (empty($section['Active'])) {
            return '';
        }
        if (!$this->evaluate_page_conditions($section, $this->active_dynamic_data_context)) {
            return '';
        }
        if (is_array($this->active_dynamic_data_context)) {
            $section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);
        }
        if ($section['Type'] === 'query_list') {
            return $this->render_page_editor_query_list($page_id, $section);
        }
        if ($section['Type'] === 'component') {
            [$component_sections, $component] = $this->resolve_page_component_instance_sections($page_id, $section);
            if (!$component || !$component_sections) { return ''; }
            $classes = trim('h18-editor-component ' . $this->page_editor_visibility_classes($section));
            $id = 'h18-section-' . sanitize_html_class((string) $section['Key']);
            return '<div id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" data-h18-component="' . esc_attr($component['Id']) . '" data-h18-component-revision="' . esc_attr($component['Revision']) . '">' . $this->render_page_editor_layout_tree($page_id, $component_sections) . '</div>';
        }
        if ($section['Type'] === 'legacy') {
            return (string) $section['LegacyHtml'];
        }
        if ($section['Type'] === 'css') {
            $css = $this->sanitize_page_section_css((string) $section['Content']);
            return $css !== '' ? '<style id="h18-imported-css-' . sanitize_html_class($section['Key']) . '">' . $css . '</style>' : '';
        }

        $background_class = strtolower((string) $section['Background']);
        $style = $this->page_editor_section_style($section);
        $classes = 'h18-editor-section h18-editor-section--' . $background_class . ' ' . $this->page_editor_visibility_classes($section);
        if ($section['Type'] === 'card') {
            $classes .= ' h18-editor-card';
        } elseif ($section['Type'] === 'highlight') {
            $classes .= ' h18-editor-highlight';
        }
        $id = 'h18-section-' . sanitize_html_class($section['Key']);
        $title = $section['Title'] !== '' ? '<h2>' . esc_html($section['Title']) . '</h2>' : '';
        $content_source = (string) $section['Content'];
        if ($section['Type'] === 'hero') {
            $content_source = $this->clean_page_hero_content($content_source);
        }
        if ($section['Type'] === 'html') {
            $content = wp_kses_post($content_source);
        } elseif ($section['Type'] === 'shortcode') {
            $content = !empty($section['AdvancedContentAuthorized'])
                ? do_shortcode((string) $content_source)
                : '<pre class="h18-editor-shortcode-locked"><code>' . esc_html((string) $content_source) . '</code></pre>';
        } else {
            $content = $this->format_page_section_content($content_source);
        }
        $inner = $title . $content;

        if (in_array($section['Type'], ['container', 'flex', 'grid'], true)) {
            $justify_map = ['Start'=>'flex-start','Center'=>'center','End'=>'flex-end','SpaceBetween'=>'space-between'];
            $align_map = ['Start'=>'flex-start','Center'=>'center','End'=>'flex-end','Stretch'=>'stretch'];
            $style .= '--h18-layout-gap:' . (int) $section['LayoutGapPx'] . 'px;' .
                '--h18-layout-mobile-gap:' . (int) $section['MobileLayoutGapPx'] . 'px;' .
                '--h18-layout-columns:' . (int) $section['LayoutColumns'] . ';' .
                '--h18-layout-mobile-columns:' . (int) $section['MobileLayoutColumns'] . ';' .
                '--h18-layout-direction:' . strtolower((string) $section['LayoutDirection']) . ';' .
                '--h18-layout-wrap:' . (!empty($section['LayoutWrap']) ? 'wrap' : 'nowrap') . ';' .
                '--h18-layout-justify:' . ($justify_map[$section['LayoutJustify']] ?? 'flex-start') . ';' .
                '--h18-layout-align:' . ($align_map[$section['LayoutAlign']] ?? 'stretch') . ';' .
                '--h18-layout-mobile-direction:' . (!empty($section['MobileLayoutStack']) ? 'column' : strtolower((string) $section['LayoutDirection'])) . ';';
            $layout_class = 'h18-layout-' . sanitize_html_class((string) $section['Type']) . '-children';
            $inner = $title . $content . '<div class="h18-layout-children ' . esc_attr($layout_class) . '">' . (string) $layout_children . '</div>';
        } elseif ($section['Type'] === 'icon') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'check');
            $label = $section['Title'] !== '' ? $section['Title'] : ($this->page_primitive_variant_options('icon')[$variant] ?? 'Ikon');
            $inner = '<div class="h18-editor-icon" role="img" aria-label="' . esc_attr($label) . '">' . $this->page_editor_safe_icon_svg($variant) . '</div>' .
                ($section['Content'] !== '' ? '<div class="h18-editor-icon-copy">' . $this->format_page_section_content($section['Content']) . '</div>' : '');
        } elseif ($section['Type'] === 'divider') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'solid');
            $inner = '<hr class="h18-editor-divider h18-editor-divider--' . esc_attr($variant) . '" aria-hidden="true" />';
        } elseif ($section['Type'] === 'list') {
            $inner = $title . '<div class="h18-editor-list">' . $this->render_page_editor_list_primitive($section) . '</div>';
        } elseif ($section['Type'] === 'badge') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'solid');
            $badge_text = $section['Title'] !== '' ? $section['Title'] : wp_strip_all_tags((string) $section['Content']);
            $inner = '<span class="h18-editor-badge h18-editor-badge--' . esc_attr($variant) . '">' . esc_html($badge_text) . '</span>';
        } elseif ($section['Type'] === 'quote') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'standard');
            $inner = '<figure class="h18-editor-quote h18-editor-quote--' . esc_attr($variant) . '"><blockquote>' . $this->format_page_section_content($section['Content']) . '</blockquote>' .
                ($section['Title'] !== '' ? '<figcaption>— ' . esc_html($section['Title']) . '</figcaption>' : '') . '</figure>';
        } elseif ($section['Type'] === 'embed') {
            $embed_url = esc_url_raw(trim((string) $section['Content']));
            $embed_html = $embed_url !== '' ? wp_oembed_get($embed_url) : '';
            if (!$embed_html && $embed_url !== '') {
                $embed_html = '<p><a href="' . esc_url($embed_url) . '">' . esc_html($embed_url) . '</a></p>';
            }
            $inner = $title . '<div class="h18-editor-embed">' . (string) $embed_html . '</div>';
        } elseif ($section['Type'] === 'hero') {
            $image_url = $section['MediaId'] ? wp_get_attachment_image_url($section['MediaId'], 'full') : '';
            if (!$image_url) {
                $image_url = $section['MediaUrl'];
            }
            $style .= '--h18-hero-height:' . (int) $section['HeroHeightPx'] . 'px;' .
                '--h18-mobile-hero-height:' . (int) $section['MobileHeroHeightPx'] . 'px;' .
                '--h18-overlay-opacity:' . ((int) $section['OverlayOpacityPercent'] / 100) . ';';
            if ($image_url !== '' && ($section['BackgroundEffect'] ?? 'None') === 'None') {
                $style .= 'background-image:url(' . wp_json_encode(esc_url_raw((string) $image_url)) . ');';
            }
            $classes .= ' h18-editor-hero';
            $buttons = '';
            if ($section['Button1Label'] !== '' && $section['Button1Url'] !== '') {
                $buttons .= '<a class="h18-editor-button" href="' . esc_url($section['Button1Url']) . '">' . esc_html($section['Button1Label']) . '</a>';
            }
            if ($section['Button2Label'] !== '' && $section['Button2Url'] !== '') {
                $buttons .= '<a class="h18-editor-button h18-editor-button--secondary" href="' . esc_url($section['Button2Url']) . '">' . esc_html($section['Button2Label']) . '</a>';
            }
            $inner = '<div class="h18-editor-hero-inner">' . $title . $content . ($buttons !== '' ? '<div class="h18-editor-actions">' . $buttons . '</div>' : '') . '</div>';
        } elseif ($section['Type'] === 'text_image') {
            $image = $section['MediaId'] ? wp_get_attachment_image($section['MediaId'], 'large', false, ['loading' => 'lazy']) : '';
            if ($image === '' && $section['MediaUrl'] !== '') {
                $image = '<img src="' . esc_url($section['MediaUrl']) . '" alt="" loading="lazy" />';
            }
            $position = $section['ImagePosition'] === 'Left' ? ' h18-editor-text-image--left' : '';
            $inner = '<div class="h18-editor-text-image' . $position . '"><div class="h18-editor-copy">' . $title . $content . '</div><div class="h18-editor-media">' . $image . '</div></div>';
        } elseif ($section['Type'] === 'image') {
            $image = $section['MediaId'] ? wp_get_attachment_image($section['MediaId'], 'full', false, ['loading' => 'lazy']) : '';
            if ($image === '' && $section['MediaUrl'] !== '') {
                $image = '<img src="' . esc_url($section['MediaUrl']) . '" alt="" loading="lazy" />';
            }
            $inner = $title . '<figure class="h18-editor-image">' . $image . ($section['Content'] !== '' ? '<figcaption>' . wp_kses_post($section['Content']) . '</figcaption>' : '') . '</figure>';
        } elseif ($section['Type'] === 'buttons') {
            $buttons = '';
            if ($section['Button1Label'] !== '' && $section['Button1Url'] !== '') {
                $buttons .= '<a class="h18-editor-button" href="' . esc_url($section['Button1Url']) . '">' . esc_html($section['Button1Label']) . '</a>';
            }
            if ($section['Button2Label'] !== '' && $section['Button2Url'] !== '') {
                $buttons .= '<a class="h18-editor-button h18-editor-button--secondary" href="' . esc_url($section['Button2Url']) . '">' . esc_html($section['Button2Label']) . '</a>';
            }
            $inner = $title . $content . '<div class="h18-editor-actions">' . $buttons . '</div>';
        } elseif ($section['Type'] === 'carousel') {
            $border_colors = ['None'=>'transparent','Sand'=>'#c3ae83','Olive'=>'#30382a','Steel'=>'#525a5f'];
            $items = [];
            foreach ((array) $section['Cards'] as $card) { if (!empty($card['Active'])) { $items[] = $card; } }
            $slides = '';
            $dots = '';
            $slide_count = count($items);
            foreach ($items as $item_index => $card) {
                $tone = (string) $card['TextTone'];
                if ($tone === 'Auto') { $tone = in_array($card['Background'], ['Olive','Steel'], true) ? 'Light' : 'Dark'; }
                $card_background = strtolower((string) $card['Background']);
                $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                    '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                    '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                    '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                    '--h18-card-border:' . $card_border . ';' .
                    '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                    '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                $label = $card['Title'] !== '' ? (string) $card['Title'] : 'Slide ' . ($item_index + 1);
                $slides .= '<article class="h18-editor-carousel-slide h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '" role="group" aria-roledescription="slide" aria-label="' . esc_attr(($item_index + 1) . ' af ' . $slide_count . ': ' . $label) . '" aria-hidden="' . ($item_index === 0 ? 'false' : 'true') . '"' . ($item_index === 0 ? '' : ' hidden') . '>' .
                    ($card['Title'] !== '' ? '<h3>' . esc_html($card['Title']) . '</h3>' : '') . $this->format_page_section_content($card['Content']) . '</article>';
                if (!empty($section['CarouselShowDots'])) {
                    $dots .= '<button type="button" class="h18-editor-carousel-dot" aria-label="Gå til slide ' . esc_attr($item_index + 1) . '" aria-current="' . ($item_index === 0 ? 'true' : 'false') . '" tabindex="' . ($item_index === 0 ? '0' : '-1') . '"></button>';
                }
            }
            $controls = '';
            if (!empty($section['CarouselShowArrows']) && $slide_count > 1) {
                $controls = '<button type="button" class="h18-editor-carousel-arrow h18-editor-carousel-prev" aria-label="Forrige slide">‹</button><button type="button" class="h18-editor-carousel-arrow h18-editor-carousel-next" aria-label="Næste slide">›</button>';
            }
            $dots_html = $dots !== '' ? '<div class="h18-editor-carousel-dots" role="group" aria-label="Vælg slide">' . $dots . '</div>' : '';
            $carousel_label = $section['Title'] !== '' ? (string) $section['Title'] : 'Carousel';
            $inner = $title . $content . '<div class="h18-editor-carousel" role="region" aria-roledescription="carousel" aria-label="' . esc_attr($carousel_label) . '" tabindex="0" data-autoplay="' . (!empty($section['CarouselAutoplay']) ? '1' : '0') . '" data-interval="' . (int) $section['CarouselIntervalMs'] . '" data-loop="' . (!empty($section['CarouselLoop']) ? '1' : '0') . '"><div class="h18-editor-carousel-viewport">' . $slides . '</div>' . $controls . $dots_html . '<span class="screen-reader-text h18-editor-carousel-status" aria-live="polite">' . ($slide_count > 0 ? '1 af ' . $slide_count : 'Ingen slides') . '</span></div>' . $this->page_editor_carousel_script($id);
        } elseif (in_array($section['Type'], ['tabs', 'accordion'], true)) {
            $border_colors = [
                'None'  => 'transparent',
                'Sand'  => '#c3ae83',
                'Olive' => '#30382a',
                'Steel' => '#525a5f',
            ];
            $items = [];
            foreach ((array) $section['Cards'] as $card) {
                if (empty($card['Active'])) { continue; }
                $items[] = $card;
            }
            if ($section['Type'] === 'tabs') {
                $tabs = '';
                $panels = '';
                foreach ($items as $item_index => $card) {
                    $card_key = sanitize_html_class((string) ($card['Key'] ?? 'panel-' . $item_index));
                    $tab_id = $id . '-tab-' . $card_key;
                    $panel_id = $id . '-panel-' . $card_key;
                    $label = $card['Title'] !== '' ? (string) $card['Title'] : 'Fane ' . ($item_index + 1);
                    $tone = (string) $card['TextTone'];
                    if ($tone === 'Auto') { $tone = in_array($card['Background'], ['Olive', 'Steel'], true) ? 'Light' : 'Dark'; }
                    $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                    $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                        '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                        '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                        '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                        '--h18-card-border:' . $card_border . ';' .
                        '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                        '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                    $card_background = strtolower((string) $card['Background']);
                    $selected = $item_index === 0;
                    $tabs .= '<button type="button" role="tab" id="' . esc_attr($tab_id) . '" aria-controls="' . esc_attr($panel_id) . '" aria-selected="' . ($selected ? 'true' : 'false') . '" tabindex="' . ($selected ? '0' : '-1') . '" class="h18-editor-tab">' . esc_html($label) . '</button>';
                    $panels .= '<div role="tabpanel" id="' . esc_attr($panel_id) . '" aria-labelledby="' . esc_attr($tab_id) . '" class="h18-editor-tab-panel h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '"' . ($selected ? '' : ' hidden') . '>' . $this->format_page_section_content($card['Content']) . '</div>';
                }
                $inner = $title . $content . '<div class="h18-editor-tabs"><div class="h18-editor-tabs-nav" role="tablist" aria-label="' . esc_attr($section['Title'] !== '' ? $section['Title'] : 'Faner') . '">' . $tabs . '</div>' . $panels . '</div>' . $this->page_editor_tabs_script($id);
            } else {
                $details = '';
                foreach ($items as $item_index => $card) {
                    $label = $card['Title'] !== '' ? (string) $card['Title'] : 'Punkt ' . ($item_index + 1);
                    $tone = (string) $card['TextTone'];
                    if ($tone === 'Auto') { $tone = in_array($card['Background'], ['Olive', 'Steel'], true) ? 'Light' : 'Dark'; }
                    $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                    $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                        '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                        '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                        '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                        '--h18-card-border:' . $card_border . ';' .
                        '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                        '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                    $card_background = strtolower((string) $card['Background']);
                    $details .= '<details class="h18-editor-accordion-item h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '"><summary>' . esc_html($label) . '</summary><div class="h18-editor-accordion-body">' . $this->format_page_section_content($card['Content']) . '</div></details>';
                }
                $inner = $title . $content . '<div class="h18-editor-accordion">' . $details . '</div>';
            }
        } elseif ($section['Type'] === 'card_grid') {
            $border_colors = [
                'None'  => 'transparent',
                'Sand'  => '#c3ae83',
                'Olive' => '#30382a',
                'Steel' => '#525a5f',
            ];
            $cards_html = '';
            foreach ((array) $section['Cards'] as $card) {
                if (empty($card['Active'])) {
                    continue;
                }
                $card_background = strtolower((string) $card['Background']);
                $tone = (string) $card['TextTone'];
                if ($tone === 'Auto') {
                    $tone = in_array($card['Background'], ['Olive', 'Steel'], true) ? 'Light' : 'Dark';
                }
                $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                    '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                    '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                    '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                    '--h18-card-border:' . $card_border . ';' .
                    '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                    '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                $card_title = $card['Title'] !== '' ? '<h3>' . esc_html($card['Title']) . '</h3>' : '';
                $cards_html .= '<article class="h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '">' .
                    $card_title . $this->format_page_section_content($card['Content']) . '</article>';
            }
            $style .= '--h18-grid-columns:' . (int) $section['Columns'] . ';' .
                '--h18-mobile-grid-columns:' . (int) $section['MobileColumns'] . ';' .
                '--h18-grid-gap:' . (int) $section['ColumnGapPx'] . 'px;' .
                '--h18-mobile-grid-gap:' . (int) $section['MobileColumnGapPx'] . 'px;';
            $inner = $title . $content . '<div class="h18-editor-card-grid">' . $cards_html . '</div>';
        } elseif ($section['Type'] === 'spacer') {
            return '<div class="h18-editor-spacer" aria-hidden="true" style="--h18-spacer:' . (int) $section['SpacerPx'] . 'px;--h18-mobile-spacer:' . (int) $section['MobileSpacerPx'] . 'px"></div>';
        } elseif ($section['Type'] === 'mail_form') {
            $module_key = isset($_GET['h18_module']) ? sanitize_key(wp_unslash($_GET['h18_module'])) : '';
            $status = $module_key === $section['Key'] && isset($_GET['h18_form']) ? sanitize_key(wp_unslash($_GET['h18_form'])) : '';
            $message = '';
            if ($status === 'success') {
                $message = '<div class="h18-module-message h18-module-message--success">' . esc_html($section['SuccessMessage']) . '</div>';
            } elseif ($status === 'error') {
                $message = '<div class="h18-module-message h18-module-message--error">Beskeden kunne ikke sendes. Kontrollér felterne og prøv igen.</div>';
            }
            $consent = $section['ConsentLabel'] !== ''
                ? '<label class="h18-page-form-field h18-page-form-field--wide"><span><input type="checkbox" name="consent" value="1" required /> ' . esc_html($section['ConsentLabel']) . '</span></label>'
                : '';
            $inner = $title . $content . $message . '<form class="h18-page-form" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">' .
                '<input type="hidden" name="action" value="h18_send_page_form" /><input type="hidden" name="page_id" value="' . (int) $page_id . '" /><input type="hidden" name="section_key" value="' . esc_attr($section['Key']) . '" />' .
                wp_nonce_field('h18_send_page_form_' . (int) $page_id . '_' . $section['Key'], 'h18_form_nonce', true, false) .
                '<input type="hidden" name="started" value="' . time() . '" /><div style="position:absolute;left:-10000px" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off" /></label></div>' .
                '<div class="h18-page-form-grid"><label class="h18-page-form-field"><span>Navn</span><input type="text" name="sender_name" required /></label><label class="h18-page-form-field"><span>E-mail</span><input type="email" name="sender_email" required /></label>' .
                '<label class="h18-page-form-field h18-page-form-field--wide"><span>Emne</span><input type="text" name="sender_subject" required /></label><label class="h18-page-form-field h18-page-form-field--wide"><span>Besked</span><textarea name="sender_message" rows="7" required></textarea></label>' . $consent .
                '<div class="h18-page-form-field h18-page-form-field--wide"><button type="submit">Send besked</button></div></div></form>';
        } elseif ($section['Type'] === 'poll') {
            $storage_key = $this->page_module_storage_key($page_id, $section['Key']);
            $state = $this->get_poll_state($storage_key, $section['PollOptions']);
            $cookie_name = 'h18_poll_' . $storage_key;
            $voted = !empty($_COOKIE[$cookie_name]);
            $closed = $this->is_poll_closed($section);
            $module_key = isset($_GET['h18_module']) ? sanitize_key(wp_unslash($_GET['h18_module'])) : '';
            $status = $module_key === $section['Key'] && isset($_GET['h18_poll']) ? sanitize_key(wp_unslash($_GET['h18_poll'])) : '';
            $message = $status === 'success' ? '<div class="h18-module-message h18-module-message--success">Tak for din stemme.</div>' : '';
            if ($status === 'duplicate') {
                $message = '<div class="h18-module-message">Du har allerede stemt i denne afstemning.</div>';
            } elseif ($status === 'error') {
                $message = '<div class="h18-module-message h18-module-message--error">Stemmen kunne ikke registreres.</div>';
            }
            $input_type = !empty($section['AllowMultiple']) ? 'checkbox' : 'radio';
            $options_html = '';
            foreach ($section['PollOptions'] as $option) {
                $options_html .= '<label class="h18-poll-option"><input type="' . $input_type . '" name="answers[]" value="' . esc_attr($this->poll_option_id($option)) . '" /> <span>' . esc_html($option) . '</span></label>';
            }
            $form = '';
            if (!$closed && !$voted) {
                $form = '<form class="h18-page-poll" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="h18_submit_poll" /><input type="hidden" name="page_id" value="' . (int) $page_id . '" /><input type="hidden" name="section_key" value="' . esc_attr($section['Key']) . '" />' .
                    wp_nonce_field('h18_submit_poll_' . (int) $page_id . '_' . $section['Key'], 'h18_poll_nonce', true, false) . '<input type="hidden" name="started" value="' . time() . '" /><div style="position:absolute;left:-10000px" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off" /></label></div><div class="h18-poll-options">' . $options_html . '</div><button type="submit">Afgiv stemme</button></form>';
            } elseif ($closed) {
                $form = '<p><strong>Afstemningen er ikke åben.</strong></p>';
            }
            $show_results = $section['ResultsMode'] === 'always' || ($section['ResultsMode'] === 'after_vote' && ($voted || in_array($status, ['success', 'duplicate'], true))) || ($section['ResultsMode'] === 'after_close' && $closed);
            $inner = $title . $content . $message . $form . ($show_results ? $this->render_poll_results($section, $state) : '');
        }

        return '<section id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" style="' . esc_attr($style) . '">' . $inner . '</section>';
    }

    private function render_page_editor_layout_tree($page_id, array $sections, $parent_key = '', $depth = 0) {
        if ($depth > 2) { return ''; }
        $html = '';
        foreach ($sections as $section) {
            if (sanitize_key((string) ($section['LayoutParentKey'] ?? '')) !== sanitize_key((string) $parent_key)) { continue; }
            $children = '';
            if (in_array((string) ($section['Type'] ?? ''), ['container','flex','grid'], true)) {
                $children = $this->render_page_editor_layout_tree($page_id, $sections, (string) $section['Key'], $depth + 1);
            }
            $html .= $this->render_page_editor_section_front($page_id, $section, $children);
        }
        return $html;
    }

    private function render_page_editor_front($page_id, array $data) {
        $this->active_dynamic_data_context = $this->resolve_dynamic_data_context(
            (string) ($data['DataContextType'] ?? ''),
            (int) ($data['DataContextEntryId'] ?? 0)
        );
        $html = $this->page_editor_frontend_css($page_id) . '<div class="h18-editor-page">';
        $sections = array_values((array) $data['Sections']);
        $has_layout_hierarchy = false;
        foreach ($sections as $layout_candidate) {
            if (sanitize_key((string) ($layout_candidate['LayoutParentKey'] ?? '')) !== '') { $has_layout_hierarchy = true; break; }
        }
        if ($has_layout_hierarchy) {
            return $html . $this->render_page_editor_layout_tree($page_id, $sections) . '</div>';
        }
        $count = count($sections);
        for ($index = 0; $index < $count; $index++) {
            $section = $sections[$index];
            $key = (string) ($section['Key'] ?? '');
            $is_imported = strpos($key, 'importeret-') === 0;

            if (
                $is_imported &&
                ($section['Type'] ?? '') === 'text' &&
                ($section['Title'] ?? '') === '' &&
                $index > 0 &&
                ($sections[$index - 1]['Type'] ?? '') === 'hero'
            ) {
                $html .= $this->render_page_editor_imported_group(
                    $section,
                    $this->render_page_editor_section_front($page_id, $section),
                    'avpf-home-tagline h18-imported-tagline'
                );
                continue;
            }

            if (
                $is_imported &&
                ($section['Type'] ?? '') === 'html' &&
                (
                    strpos((string) ($section['Content'] ?? ''), 'wp-block-columns') !== false ||
                    ($section['ImportedGroupType'] ?? '') === 'columns'
                )
            ) {
                $html .= $this->render_page_editor_imported_group(
                    $section,
                    $this->render_page_editor_section_front($page_id, $section),
                    'avpf-section h18-imported-columns'
                );
                continue;
            }

            $next = $index + 1 < $count ? $sections[$index + 1] : null;
            if (
                $is_imported &&
                ($section['Type'] ?? '') === 'text' &&
                is_array($next) &&
                strpos((string) ($next['Key'] ?? ''), 'importeret-') === 0 &&
                ($next['Type'] ?? '') === 'buttons'
            ) {
                $html .= $this->render_page_editor_imported_group(
                    $section,
                    $this->render_page_editor_section_front($page_id, $section) .
                        $this->render_page_editor_section_front($page_id, $next),
                    'avpf-section h18-imported-composite'
                );
                $index++;
                continue;
            }

            $html .= $this->render_page_editor_section_front($page_id, $section);
        }
        return $html . '</div>';
    }

    private function build_page_editor_core($slug, array $data) {
        $marker = $this->encode_marker(self::PAGE_EDITOR_MARKER, $data);
        return $marker . "\n<!-- wp:shortcode -->\n[hangar18_page_editor slug=\"" . esc_attr($slug) . "\"]\n<!-- /wp:shortcode -->";
    }

    private function build_page_editor_test_core($slug, array $data) {
        $marker = $this->encode_marker(self::PAGE_EDITOR_MARKER, $data);
        return $marker . "\n<!-- wp:shortcode -->\n[hangar18_page_editor slug=\"" . esc_attr($slug) . "\" test=\"1\"]\n<!-- /wp:shortcode -->";
    }

    public function shortcode_page_editor($atts) {
        $atts = shortcode_atts(['slug' => '', 'test' => '0'], $atts, 'hangar18_page_editor');
        $slug = sanitize_title((string) $atts['slug']);
        $page_id = (int) get_the_ID();
        $page = $page_id ? get_post($page_id) : $this->post_by_slug($slug);
        if (!$page instanceof WP_Post) {
            return '';
        }
        if ($slug === '') {
            $slug = $page->post_name;
        }
        $is_test = in_array(strtolower((string) $atts['test']), ['1', 'true', 'yes'], true) &&
            (int) get_post_meta($page->ID, '_h18_conversion_test_source_id', true) > 0;
        if ($is_test) {
            $marker_data = $this->decode_marker(self::PAGE_EDITOR_MARKER, $page->post_content);
            if (!is_array($marker_data)) {
                return '';
            }
            // En konverteringstest læser altid sin egen indlejrede kladde.
            // Den må ikke falde tilbage til originalsiden eller det centrale store.
            $data = $this->normalize_page_editor_data($marker_data, $page);
        } else {
            $data = $this->get_page_editor_data($slug, $page);
        }
        return $this->render_page_editor_front($page->ID, $data);
    }

    private function page_form_submission_count($page_id, $section_key) {
        $all = get_option(self::FORM_SUBMISSIONS_OPTION, []);
        $storage_key = $this->page_module_storage_key($page_id, $section_key);
        return is_array($all) && isset($all[$storage_key]) && is_array($all[$storage_key])
            ? count($all[$storage_key])
            : 0;
    }

    private function page_poll_vote_count($page_id, array $section) {
        $storage_key = $this->page_module_storage_key($page_id, $section['Key']);
        $state = $this->get_poll_state($storage_key, $section['PollOptions']);
        return array_sum(array_map('intval', $state['Counts']));
    }

    private function render_page_editor_card_admin(array $card, $section_index, $card_index) {
        $prefix = 'sections[' . $section_index . '][Cards][' . $card_index . ']';
        ?>
        <article class="h18-page-card-row" data-card-index="<?php echo esc_attr($card_index); ?>">
            <input class="h18-page-card-order" type="hidden" name="<?php echo esc_attr($prefix); ?>[Order]" value="<?php echo esc_attr($card['Order']); ?>" />
            <input class="h18-page-card-key" type="hidden" name="<?php echo esc_attr($prefix); ?>[Key]" value="<?php echo esc_attr($card['Key']); ?>" />
            <input class="h18-page-card-remove" type="hidden" name="<?php echo esc_attr($prefix); ?>[Remove]" value="0" />
            <header class="h18-page-card-header">
                <span class="dashicons dashicons-move h18-page-card-drag" title="Flyt kasse"></span>
                <strong>Kasse: <span class="h18-page-card-title-summary"><?php echo esc_html($card['Title'] !== '' ? $card['Title'] : 'Uden overskrift'); ?></span></strong>
                <div class="h18-page-card-actions"><label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[Active]" value="1" <?php checked(!empty($card['Active'])); ?> /> Vis</label><button class="button h18-page-card-duplicate" type="button">Duplikér</button><button class="button-link-delete h18-page-card-delete" type="button">Fjern</button></div>
            </header>
            <div class="h18-page-card-body">
                <div class="h18-module-fields-grid">
                    <div class="h18-field"><label><strong>Overskrift</strong></label><input class="h18-page-card-title" type="text" name="<?php echo esc_attr($prefix); ?>[Title]" value="<?php echo esc_attr($card['Title']); ?>" /></div>
                    <div class="h18-field h18-field-wide"><label><strong>Tekst</strong></label><textarea name="<?php echo esc_attr($prefix); ?>[Content]" rows="4"><?php echo esc_textarea($card['Content']); ?></textarea></div>
                    <div class="h18-field"><label><strong>Baggrund</strong></label><select name="<?php echo esc_attr($prefix); ?>[Background]"><option value="White" <?php selected($card['Background'], 'White'); ?>>Hvid</option><option value="OffWhite" <?php selected($card['Background'], 'OffWhite'); ?>>Knækket hvid</option><option value="Sand" <?php selected($card['Background'], 'Sand'); ?>>Sandfarvet</option><option value="Olive" <?php selected($card['Background'], 'Olive'); ?>>Mørk olivengrøn</option><option value="Steel" <?php selected($card['Background'], 'Steel'); ?>>Stålgrå</option></select></div>
                    <div class="h18-field"><label><strong>Tekstfarve</strong></label><select name="<?php echo esc_attr($prefix); ?>[TextTone]"><option value="Auto" <?php selected($card['TextTone'], 'Auto'); ?>>Automatisk</option><option value="Dark" <?php selected($card['TextTone'], 'Dark'); ?>>Mørk</option><option value="Light" <?php selected($card['TextTone'], 'Light'); ?>>Lys</option></select></div>
                    <div class="h18-field"><label><strong>Kantfarve</strong></label><select name="<?php echo esc_attr($prefix); ?>[BorderColor]"><option value="None" <?php selected($card['BorderColor'], 'None'); ?>>Ingen</option><option value="Sand" <?php selected($card['BorderColor'], 'Sand'); ?>>Sandfarvet</option><option value="Olive" <?php selected($card['BorderColor'], 'Olive'); ?>>Mørk olivengrøn</option><option value="Steel" <?php selected($card['BorderColor'], 'Steel'); ?>>Stålgrå</option></select></div>
                    <div class="h18-field"><label><strong>Kanttykkelse (px)</strong></label><input type="number" min="0" max="8" name="<?php echo esc_attr($prefix); ?>[BorderWidthPx]" value="<?php echo esc_attr($card['BorderWidthPx']); ?>" /></div>
                    <div class="h18-field"><label><strong>Indvendig luft desktop (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[PaddingPx]" value="<?php echo esc_attr($card['PaddingPx']); ?>" /></div>
                    <div class="h18-field"><label><strong>Indvendig luft mobil (px)</strong></label><input type="number" min="0" max="60" name="<?php echo esc_attr($prefix); ?>[MobilePaddingPx]" value="<?php echo esc_attr($card['MobilePaddingPx']); ?>" /></div>
                    <div class="h18-field"><label><strong>Hjørneafrunding (px)</strong></label><input type="number" min="0" max="30" name="<?php echo esc_attr($prefix); ?>[RadiusPx]" value="<?php echo esc_attr($card['RadiusPx']); ?>" /></div>
                    <div class="h18-field"><label><strong>Placering desktop</strong></label><select name="<?php echo esc_attr($prefix); ?>[DesktopAlignment]"><option value="Left" <?php selected($card['DesktopAlignment'], 'Left'); ?>>Venstre</option><option value="Center" <?php selected($card['DesktopAlignment'], 'Center'); ?>>Midtstillet</option></select></div>
                    <div class="h18-field"><label><strong>Placering mobil</strong></label><select name="<?php echo esc_attr($prefix); ?>[MobileAlignment]"><option value="Left" <?php selected($card['MobileAlignment'], 'Left'); ?>>Venstre</option><option value="Center" <?php selected($card['MobileAlignment'], 'Center'); ?>>Midtstillet</option></select></div>
                </div>
            </div>
        </article>
        <?php
    }

    private function render_page_editor_section_admin($page, array $section, $index, $is_template = false) {
        $prefix = 'sections[' . $index . ']';
        $type_labels = $this->page_section_type_labels();
        $component_options = $this->get_page_components();
        $export_poll = '';
        $export_forms = '';
        $test_form = '';
        if (!$is_template && $section['Type'] === 'poll') {
            $export_poll = wp_nonce_url(
                admin_url('admin-post.php?action=h18_export_poll&page_id=' . (int) $page->ID . '&section_key=' . rawurlencode($section['Key'])),
                'h18_export_poll_' . (int) $page->ID . '_' . $section['Key']
            );
        }
        if (!$is_template && $section['Type'] === 'mail_form') {
            $export_forms = wp_nonce_url(
                admin_url('admin-post.php?action=h18_export_form_submissions&page_id=' . (int) $page->ID . '&section_key=' . rawurlencode($section['Key'])),
                'h18_export_form_submissions_' . (int) $page->ID . '_' . $section['Key']
            );
            $test_form = wp_nonce_url(
                admin_url('admin-post.php?action=h18_test_page_form&page_id=' . (int) $page->ID . '&section_key=' . rawurlencode($section['Key'])),
                'h18_test_page_form_' . (int) $page->ID . '_' . $section['Key']
            );
        }
        ?>
        <article class="h18-page-section-row" data-section-index="<?php echo esc_attr($index); ?>" data-section-type="<?php echo esc_attr($section['Type']); ?>">
            <input class="h18-page-section-order" type="hidden" name="<?php echo esc_attr($prefix); ?>[Order]" value="<?php echo esc_attr($section['Order']); ?>" />
            <input class="h18-page-section-key" type="hidden" name="<?php echo esc_attr($prefix); ?>[Key]" value="<?php echo esc_attr($section['Key']); ?>" />
            <input class="h18-page-section-remove" type="hidden" name="<?php echo esc_attr($prefix); ?>[Remove]" value="0" />
            <input class="h18-page-section-imported-group" type="hidden" name="<?php echo esc_attr($prefix); ?>[ImportedGroupType]" value="<?php echo esc_attr($section['ImportedGroupType']); ?>" />
            <input class="h18-section-navigator-label" type="hidden" name="<?php echo esc_attr($prefix); ?>[NavigatorLabel]" value="<?php echo esc_attr($section['NavigatorLabel']); ?>" />
            <input class="h18-section-navigator-locked" type="hidden" name="<?php echo esc_attr($prefix); ?>[NavigatorLocked]" value="<?php echo !empty($section['NavigatorLocked']) ? '1' : '0'; ?>" />

            <header class="h18-page-section-header">
                <span class="dashicons dashicons-move h18-page-section-drag" title="Flyt sektion"></span>
                <div>
                    <strong class="h18-page-section-summary"><?php echo esc_html($type_labels[$section['Type']] ?? 'Sektion'); ?></strong>
                    <span class="h18-page-section-title-summary"><?php echo esc_html($section['Title']); ?></span>
                </div>
                <div class="h18-page-section-header-actions">
                    <button class="button h18-page-section-edit" type="button">Rediger</button>
                    <label><input class="h18-section-active" type="checkbox" name="<?php echo esc_attr($prefix); ?>[Active]" value="1" <?php checked(!empty($section['Active'])); ?> /> Vis</label>
                    <?php if ($section['Type'] !== 'legacy') : ?><button class="button h18-page-section-duplicate" type="button">Duplikér</button><?php endif; ?>
                    <button class="button-link-delete h18-page-section-delete" type="button">Fjern</button>
                </div>
            </header>

            <div class="h18-page-section-body">
                <?php if ($section['Type'] === 'legacy') : ?>
                    <input type="hidden" name="<?php echo esc_attr($prefix); ?>[Type]" value="legacy" />
                    <div class="h18-legacy-content-note">
                        <strong>Eksisterende indhold er bevaret uændret</strong>
                        <p>Dette er sidens indhold fra før den nye editor. Tilføj nye sektioner omkring det, eller fjern sektionen, når siden er bygget færdig i editoren.</p>
                    </div>
                <?php else : ?>
                    <div class="h18-page-section-main-grid">
                        <div class="h18-field">
                            <label><strong>Sektionstype</strong></label>
                            <select class="h18-page-section-type" name="<?php echo esc_attr($prefix); ?>[Type]">
                                <?php foreach ($type_labels as $value => $label) : if ($value === 'legacy') { continue; } ?>
                                    <option value="<?php echo esc_attr($value); ?>" <?php selected($section['Type'], $value); ?>><?php echo esc_html($label); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="h18-field h18-section-type-field" data-types="hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list badge quote html mail_form poll">
                            <label><strong class="h18-section-title-label"><?php echo $section['Type'] === 'poll' ? 'Spørgsmål' : 'Overskrift'; ?></strong></label>
                            <input class="h18-section-title-input" type="text" name="<?php echo esc_attr($prefix); ?>[Title]" value="<?php echo esc_attr($section['Title']); ?>" />
                        </div>

                        <div class="h18-field h18-section-type-field h18-page-section-content" data-types="hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list quote embed shortcode html css mail_form poll">
                            <label><strong><?php echo $section['Type'] === 'image' ? 'Billedtekst' : ($section['Type'] === 'css' ? 'CSS' : 'Tekst'); ?></strong></label>
                            <div class="h18-mini-editor-toolbar h18-section-type-field" data-types="hero text text_image image buttons card card_grid highlight list quote html mail_form poll"><button type="button" class="button h18-mini-format" data-format="bold"><strong>B</strong></button><button type="button" class="button h18-mini-format" data-format="italic"><em>I</em></button><button type="button" class="button h18-mini-format" data-format="link">Link</button><button type="button" class="button h18-mini-format" data-format="list">Punktliste</button></div>
                            <textarea name="<?php echo esc_attr($prefix); ?>[Content]" rows="5"><?php echo esc_textarea($section['Content']); ?></textarea>
                            <p class="description h18-standard-content-help">Almindelig tekst samt enkel formatering som fed, kursiv, links og lister er tilladt.</p>
                            <p class="description h18-section-type-field" data-types="html"><strong>Importeret blok:</strong> HTML-koden er bevaret for at fastholde det nuværende udseende. Tekst og links kan redigeres direkte her.</p>
                            <p class="description h18-section-type-field" data-types="css"><strong>Avanceret side-CSS:</strong> Bevarer den eksisterende sides farver, kolonner og responsive regler. Ret kun feltet, hvis du kender CSS.</p>
                            <p class="description h18-section-type-field" data-types="embed"><strong>Embed:</strong> Indsæt kun en HTTPS-URL fra en WordPress oEmbed-understøttet tjeneste. Ukendte URL'er vises som et almindeligt link.</p>
                            <p class="description h18-section-type-field" data-types="shortcode"><strong>Shortcode:</strong> Koden udføres kun, når den er gemt af en bruger med avanceret indholdsrettighed. Ellers vises den som kode på siden.</p>
                        </div>
                        <div class="h18-field h18-section-type-field" data-types="icon divider list badge quote">
                            <label><strong>Variant</strong></label>
                            <select class="h18-primitive-variant" name="<?php echo esc_attr($prefix); ?>[PrimitiveVariant]">
                                <?php foreach ($this->page_primitive_variant_options($section['Type']) as $variant_value => $variant_label) : ?>
                                    <option value="<?php echo esc_attr($variant_value); ?>" <?php selected($section['PrimitiveVariant'], $variant_value); ?>><?php echo esc_html($variant_label); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        <input class="h18-advanced-content-authorized" type="hidden" name="<?php echo esc_attr($prefix); ?>[AdvancedContentAuthorized]" value="<?php echo !empty($section['AdvancedContentAuthorized']) ? '1' : '0'; ?>" />
                    </div>


                    <div class="h18-section-module-box h18-dynamic-binding-box">
                        <h4>Dynamic data binding</h4>
                        <p class="description">Bind sikre elementegenskaber til current data context. Hvis context/field ikke findes, bruges elementets statiske værdi.</p>
                        <?php
                        $binding_rows = [
                            'Title' => ['Overskrift', 'hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list badge quote mail_form poll', 'text number bool date'],
                            'Content' => ['Tekst / indhold', 'hero text text_image buttons card card_grid tabs accordion carousel container flex grid highlight icon list quote mail_form poll', 'text number bool date'],
                            'MediaId' => ['Billede', 'hero text_image image', 'media'],
                            'Button1Label' => ['Knap 1 – tekst', 'hero buttons', 'text number bool date'],
                            'Button1Url' => ['Knap 1 – link', 'hero buttons', 'text'],
                            'Button2Label' => ['Knap 2 – tekst', 'hero buttons', 'text number bool date'],
                            'Button2Url' => ['Knap 2 – link', 'hero buttons', 'text'],
                        ];
                        foreach ($binding_rows as $binding_property => $binding_config) :
                            $binding_value = (string) (($section['Bindings'][$binding_property] ?? ''));
                            $binding_option = $this->dynamic_binding_option_for_property((array)($section['BindingOptions'] ?? []), $binding_property);
                        ?>
                            <div class="h18-field h18-dynamic-binding-row" data-types="<?php echo esc_attr($binding_config[1]); ?>">
                                <label><strong><?php echo esc_html($binding_config[0]); ?></strong></label>
                                <select class="h18-dynamic-binding-select" name="<?php echo esc_attr($prefix); ?>[Bindings][<?php echo esc_attr($binding_property); ?>]" data-binding-property="<?php echo esc_attr($binding_property); ?>" data-allowed-types="<?php echo esc_attr($binding_config[2]); ?>" data-binding-value="<?php echo esc_attr($binding_value); ?>"><option value="">Statisk værdi</option></select>
                                <div class="h18-binding-options" data-binding-property="<?php echo esc_attr($binding_property); ?>">
                                    <select class="h18-binding-formatter" name="<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Formatter]"><?php foreach($this->dynamic_binding_formatters() as $formatter_key=>$formatter_label):?><option value="<?php echo esc_attr($formatter_key); ?>" <?php selected($binding_option['Formatter'],$formatter_key); ?>><?php echo esc_html($formatter_label); ?></option><?php endforeach;?></select>
                                    <select class="h18-binding-fallback-mode" name="<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][FallbackMode]"><option value="Static" <?php selected($binding_option['FallbackMode'],'Static'); ?>>Fallback: statisk elementværdi</option><option value="Custom" <?php selected($binding_option['FallbackMode'],'Custom'); ?>>Fallback: egen værdi</option><option value="Empty" <?php selected($binding_option['FallbackMode'],'Empty'); ?>>Fallback: tom</option></select>
                                    <input class="h18-binding-fallback" type="text" maxlength="2000" name="<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Fallback]" value="<?php echo esc_attr($binding_option['Fallback']); ?>" placeholder="Egen fallback" />
                                    <label class="h18-binding-empty-toggle"><input class="h18-binding-fallback-empty" type="checkbox" name="<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][FallbackWhenEmpty]" value="1" <?php checked(!empty($binding_option['FallbackWhenEmpty'])); ?> /> Brug fallback når feltet er tomt</label>
                                    <input class="h18-binding-prefix" type="text" maxlength="100" name="<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Prefix]" value="<?php echo esc_attr($binding_option['Prefix']); ?>" placeholder="Prefix" />
                                    <input class="h18-binding-suffix" type="text" maxlength="100" name="<?php echo esc_attr($prefix); ?>[BindingOptions][<?php echo esc_attr($binding_property); ?>][Suffix]" value="<?php echo esc_attr($binding_option['Suffix']); ?>" placeholder="Suffix" />
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>


                    <div class="h18-section-module-box h18-condition-editor" data-condition-editor>
                        <h4>Conditions / synlighed</h4>
                        <p class="description">Vis eller skjul elementet ud fra data, bruger eller dato/tid. Conditions er præsentationslogik og må ikke bruges som adgangskontrol eller sikkerhedsgrænse.</p>
                        <div class="h18-module-fields-grid h18-module-fields-grid--two">
                            <div class="h18-field"><label><strong>Kombinér betingelser</strong></label><select class="h18-condition-mode" name="<?php echo esc_attr($prefix); ?>[ConditionMode]"><option value="All" <?php selected($section['ConditionMode'],'All'); ?>>Alle skal være opfyldt (AND)</option><option value="Any" <?php selected($section['ConditionMode'],'Any'); ?>>Mindst én skal være opfyldt (OR)</option></select></div>
                        </div>
                        <input class="h18-conditions-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[ConditionsJson]" value="<?php echo esc_attr(wp_json_encode(array_values((array) $section['Conditions']))); ?>" />
                        <div class="h18-condition-list"></div>
                        <p><button type="button" class="button h18-condition-add">Tilføj condition</button> <span class="description">Maks. 8 pr. element.</span></p>
                    </div>


                    <div class="h18-section-type-field h18-section-module-box h18-query-list-editor" data-types="query_list">
                        <h4>Repeater / Query list</h4>
                        <p class="description">Kører Query Builder v1 og renderer den valgte linked component én gang pr. resultat. Hvert resultat bliver current data context inde i templaten.</p>
                        <?php
                        $h18_query_types = $this->get_custom_data_types();
                        $h18_query_components = $this->get_page_components();
                        $h18_query_schema = isset($h18_query_types[$section['QueryListType']]) ? $h18_query_types[$section['QueryListType']] : null;
                        $h18_query_fields = $h18_query_schema ? (array) $h18_query_schema['Fields'] : [];
                        $h18_query_component = isset($h18_query_components[$section['QueryListComponentId']]) ? $h18_query_components[$section['QueryListComponentId']] : null;
                        ?>
                        <div class="h18-module-fields-grid h18-module-fields-grid--two">
                            <div class="h18-field"><label><strong>Datatype</strong></label><select class="h18-query-list-type" name="<?php echo esc_attr($prefix); ?>[QueryListType]"><option value="">Vælg datatype</option><?php foreach ($h18_query_types as $h18_type_key => $h18_type) : ?><option value="<?php echo esc_attr($h18_type_key); ?>" <?php selected($section['QueryListType'], $h18_type_key); ?>><?php echo esc_html($h18_type['PluralLabel']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Template-komponent</strong></label><select class="h18-query-list-component" name="<?php echo esc_attr($prefix); ?>[QueryListComponentId]"><option value="">Vælg linked component</option><?php foreach ($h18_query_components as $h18_component_id => $h18_component) : ?><option value="<?php echo esc_attr($h18_component_id); ?>" <?php selected($section['QueryListComponentId'], $h18_component_id); ?>><?php echo esc_html($h18_component['Name']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Variant</strong></label><select class="h18-query-list-component-variant" data-current="<?php echo esc_attr($section['QueryListComponentVariant']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListComponentVariant]"><option value="">Base</option><?php if ($h18_query_component) : foreach ((array) ($h18_query_component['Variants'] ?? []) as $h18_variant_id => $h18_variant) : ?><option value="<?php echo esc_attr($h18_variant_id); ?>" <?php selected($section['QueryListComponentVariant'], $h18_variant_id); ?>><?php echo esc_html($h18_variant['Name']); ?></option><?php endforeach; endif; ?></select></div>
                            <div class="h18-field"><label><strong>Filterfelt</strong></label><select class="h18-query-list-filter-field" data-current="<?php echo esc_attr($section['QueryListFilterField']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListFilterField]"><option value="">Intet filter</option><?php foreach ($h18_query_fields as $h18_field) : ?><option value="<?php echo esc_attr($h18_field['Key']); ?>" data-field-type="<?php echo esc_attr($h18_field['Type']); ?>" <?php selected($section['QueryListFilterField'], $h18_field['Key']); ?>><?php echo esc_html($h18_field['Label']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Operator</strong></label><select class="h18-query-list-filter-operator" data-current="<?php echo esc_attr($section['QueryListFilterOperator']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListFilterOperator]"><option value="eq">Er lig med</option></select></div>
                            <div class="h18-field"><label><strong>Filterværdi</strong></label><input class="h18-query-list-filter-value" type="text" name="<?php echo esc_attr($prefix); ?>[QueryListFilterValue]" value="<?php echo esc_attr($section['QueryListFilterValue']); ?>" /></div>
                            <div class="h18-field"><label><strong>Sortering</strong></label><select class="h18-query-list-sort" data-current="<?php echo esc_attr($section['QueryListSort']); ?>" name="<?php echo esc_attr($prefix); ?>[QueryListSort]"><option value="modified">Senest ændret</option><option value="created">Oprettet</option><option value="title">Titel</option><?php foreach ($h18_query_fields as $h18_field) : if (($h18_field['Type'] ?? '') === 'bool') continue; ?><option value="field:<?php echo esc_attr($h18_field['Key']); ?>" <?php selected($section['QueryListSort'], 'field:' . $h18_field['Key']); ?>><?php echo esc_html($h18_field['Label']); ?></option><?php endforeach; ?></select></div>
                            <div class="h18-field"><label><strong>Retning</strong></label><select name="<?php echo esc_attr($prefix); ?>[QueryListOrder]"><option value="DESC" <?php selected($section['QueryListOrder'],'DESC'); ?>>Faldende</option><option value="ASC" <?php selected($section['QueryListOrder'],'ASC'); ?>>Stigende</option></select></div>
                            <div class="h18-field"><label><strong>Maks. resultater</strong></label><input type="number" min="1" max="100" name="<?php echo esc_attr($prefix); ?>[QueryListLimit]" value="<?php echo esc_attr($section['QueryListLimit']); ?>" /></div>
                            <div class="h18-field"><label><strong>Kolonner desktop</strong></label><input type="number" min="1" max="6" name="<?php echo esc_attr($prefix); ?>[QueryListColumns]" value="<?php echo esc_attr($section['QueryListColumns']); ?>" /></div>
                            <div class="h18-field"><label><strong>Kolonner mobil</strong></label><input type="number" min="1" max="2" name="<?php echo esc_attr($prefix); ?>[QueryListMobileColumns]" value="<?php echo esc_attr($section['QueryListMobileColumns']); ?>" /></div>
                            <div class="h18-field"><label><strong>Gap desktop (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[QueryListGapPx]" value="<?php echo esc_attr($section['QueryListGapPx']); ?>" /></div>
                            <div class="h18-field"><label><strong>Gap mobil (px)</strong></label><input type="number" min="0" max="60" name="<?php echo esc_attr($prefix); ?>[QueryListMobileGapPx]" value="<?php echo esc_attr($section['QueryListMobileGapPx']); ?>" /></div>
                            <div class="h18-field h18-field--full"><label><strong>Tomt resultat</strong></label><input type="text" maxlength="160" name="<?php echo esc_attr($prefix); ?>[QueryListEmptyText]" value="<?php echo esc_attr($section['QueryListEmptyText']); ?>" /></div>
                        </div>
                    </div>


                    <div class="h18-section-type-field h18-section-module-box h18-component-instance-editor" data-types="component">
                        <h4>Linked component</h4>
                        <p class="description">Definitionen er global. Kun eksplicit frigivne inputs kan overskrives lokalt; layout og design forbliver linked.</p>
                        <div class="h18-field">
                            <label><strong>Komponent</strong></label>
                            <select class="h18-component-select" name="<?php echo esc_attr($prefix); ?>[ComponentId]">
                                <option value="">Vælg linked component</option>
                                <?php foreach ($component_options as $component_option) : ?>
                                    <option value="<?php echo esc_attr($component_option['Id']); ?>" <?php selected($section['ComponentId'], $component_option['Id']); ?>><?php echo esc_html($component_option['Name'] . ' · r' . $component_option['Revision']); ?></option>
                                <?php endforeach; ?>
                            </select>
                            <input class="h18-component-revision" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentRevision]" value="<?php echo esc_attr($section['ComponentRevision']); ?>" />
                            <label><strong>Variant</strong></label>
                            <select class="h18-component-variant-select" name="<?php echo esc_attr($prefix); ?>[ComponentVariant]"><option value="">Base</option></select>
                            <input class="h18-component-overrides-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentOverridesJson]" value="<?php echo esc_attr(wp_json_encode($section['ComponentOverrides'])); ?>" />
                        </div>
                        <div class="h18-component-instance-status"></div>
                        <div class="h18-component-overrides-editor"></div>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="hero text_image image">
                        <h4>Billede</h4>
                        <div class="h18-module-fields-grid">
                            <div class="h18-field">
                                <label><strong>Mediebibliotek</strong></label>
                                <input class="h18-section-media-id" type="hidden" name="<?php echo esc_attr($prefix); ?>[MediaId]" value="<?php echo esc_attr($section['MediaId']); ?>" />
                                <input class="h18-section-media-url" type="hidden" name="<?php echo esc_attr($prefix); ?>[MediaUrl]" value="<?php echo esc_attr($section['MediaUrl']); ?>" />
                                <div class="h18-section-media-preview"><?php if ($section['MediaId']) { echo wp_get_attachment_image($section['MediaId'], 'thumbnail'); } ?></div>
                                <button class="button h18-page-select-media" type="button">Vælg billede</button>
                                <button class="button-link-delete h18-page-remove-media" type="button">Fjern billede</button>
                            </div>
                            <div class="h18-field h18-section-type-field" data-types="text_image">
                                <label><strong>Billedplacering på desktop</strong></label>
                                <select name="<?php echo esc_attr($prefix); ?>[ImagePosition]"><option value="Left" <?php selected($section['ImagePosition'], 'Left'); ?>>Venstre</option><option value="Right" <?php selected($section['ImagePosition'], 'Right'); ?>>Højre</option></select>
                                <p class="description">På mobil vises billedet automatisk over teksten.</p>
                            </div>
                            <div class="h18-section-type-field h18-field-wide h18-image-design-fields" data-types="text_image image">
                                <h4>Billedudsnit og fokus</h4>
                                <p class="description">Auto bevarer den nuværende billedhøjde. Vælg et format eller en højde for at aktivere beskæring. Fokuspunktet styrer, hvilken del af billedet der prioriteres.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Format</strong></label><select name="<?php echo esc_attr($prefix); ?>[ImageAspectRatio]"><option value="Auto" <?php selected($section['ImageAspectRatio'], 'Auto'); ?>>Auto / original</option><option value="1:1" <?php selected($section['ImageAspectRatio'], '1:1'); ?>>1:1</option><option value="4:3" <?php selected($section['ImageAspectRatio'], '4:3'); ?>>4:3</option><option value="3:2" <?php selected($section['ImageAspectRatio'], '3:2'); ?>>3:2</option><option value="16:9" <?php selected($section['ImageAspectRatio'], '16:9'); ?>>16:9</option></select></div>
                                    <div class="h18-field"><label><strong>Tilpasning</strong></label><select name="<?php echo esc_attr($prefix); ?>[ImageFit]"><option value="Cover" <?php selected($section['ImageFit'], 'Cover'); ?>>Fyld / beskær</option><option value="Contain" <?php selected($section['ImageFit'], 'Contain'); ?>>Vis hele billedet</option></select></div>
                                    <div class="h18-field"><label><strong>Fokus vandret (%)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[ImageFocalXPercent]" value="<?php echo esc_attr($section['ImageFocalXPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Fokus lodret (%)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[ImageFocalYPercent]" value="<?php echo esc_attr($section['ImageFocalYPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Højde desktop/tablet (px)</strong></label><input type="number" min="0" max="1200" name="<?php echo esc_attr($prefix); ?>[ImageHeightPx]" value="<?php echo esc_attr($section['ImageHeightPx']); ?>" /><p class="description">0 = automatisk.</p></div>
                                    <div class="h18-field"><label><strong>Højde mobil (px)</strong></label><input type="number" min="0" max="900" name="<?php echo esc_attr($prefix); ?>[MobileImageHeightPx]" value="<?php echo esc_attr($section['MobileImageHeightPx']); ?>" /><p class="description">0 = automatisk.</p></div>
                                    <div class="h18-field"><label><strong>Billedbredde desktop/tablet (%)</strong></label><input type="number" min="20" max="100" name="<?php echo esc_attr($prefix); ?>[ImageWidthPercent]" value="<?php echo esc_attr($section['ImageWidthPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Billedbredde mobil (%)</strong></label><input type="number" min="20" max="100" name="<?php echo esc_attr($prefix); ?>[MobileImageWidthPercent]" value="<?php echo esc_attr($section['MobileImageWidthPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Maks. billedbredde (px)</strong></label><input type="number" min="0" max="2000" name="<?php echo esc_attr($prefix); ?>[ImageMaxWidthPx]" value="<?php echo esc_attr($section['ImageMaxWidthPx']); ?>" /><p class="description">0 = ingen grænse.</p></div>
                                    <div class="h18-field h18-checkbox-setting"><label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[ImageAspectLocked]" value="1" <?php checked(!empty($section['ImageAspectLocked'])); ?> /> <strong>Lås valgt billedformat</strong></label><p class="description">Når formatet er låst og ikke står på Auto, styres højden af formatet.</p></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="hero buttons">
                        <h4>Knapper</h4>
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field"><label><strong>Knap 1 – tekst</strong></label><input type="text" name="<?php echo esc_attr($prefix); ?>[Button1Label]" value="<?php echo esc_attr($section['Button1Label']); ?>" /></div>
                            <div class="h18-field"><label><strong>Knap 1 – link</strong></label><input type="text" name="<?php echo esc_attr($prefix); ?>[Button1Url]" value="<?php echo esc_attr($section['Button1Url']); ?>" placeholder="https:// eller /kontakt/" /></div>
                            <div class="h18-field"><label><strong>Knap 2 – tekst</strong></label><input type="text" name="<?php echo esc_attr($prefix); ?>[Button2Label]" value="<?php echo esc_attr($section['Button2Label']); ?>" /></div>
                            <div class="h18-field"><label><strong>Knap 2 – link</strong></label><input type="text" name="<?php echo esc_attr($prefix); ?>[Button2Url]" value="<?php echo esc_attr($section['Button2Url']); ?>" placeholder="https:// eller /bliv-medlem/" /></div>
                        </div>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="hero">
                        <h4>Topbanner / hero</h4>
                        <p>Billedet bruges som baggrund. Mørkningen gør den hvide tekst læsbar oven på billedet.</p>
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field"><label><strong>Højde desktop (px)</strong></label><input type="number" min="140" max="800" name="<?php echo esc_attr($prefix); ?>[HeroHeightPx]" value="<?php echo esc_attr($section['HeroHeightPx']); ?>" /></div>
                            <div class="h18-field"><label><strong>Højde mobil (px)</strong></label><input type="number" min="100" max="600" name="<?php echo esc_attr($prefix); ?>[MobileHeroHeightPx]" value="<?php echo esc_attr($section['MobileHeroHeightPx']); ?>" /></div>
                            <div class="h18-field"><label><strong>Mørkning (%)</strong></label><input type="number" min="0" max="90" name="<?php echo esc_attr($prefix); ?>[OverlayOpacityPercent]" value="<?php echo esc_attr($section['OverlayOpacityPercent']); ?>" /></div>
                        </div>
                    </div>

                    <div class="h18-section-module-box h18-layout-parent-box">
                        <h4>Layout-hierarki</h4>
                        <input class="h18-layout-parent-key" type="hidden" name="<?php echo esc_attr($prefix); ?>[LayoutParentKey]" value="<?php echo esc_attr($section['LayoutParentKey']); ?>" />
                        <div class="h18-field"><label><strong>Placér element i</strong></label><select class="h18-layout-parent-select"><option value="">Topniveau på siden</option></select></div>
                        <p class="description">Kun Container, Flex container og Grid container kan være parent. Cyklusser og mere end tre niveauer afvises også server-side.</p>
                    </div>
                    <div class="h18-section-type-field h18-section-module-box" data-types="container flex grid">
                        <h4>Container-layout</h4>
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field h18-section-type-field" data-types="flex"><label><strong>Retning</strong></label><select name="<?php echo esc_attr($prefix); ?>[LayoutDirection]"><option value="Row" <?php selected($section['LayoutDirection'],'Row'); ?>>Vandret</option><option value="Column" <?php selected($section['LayoutDirection'],'Column'); ?>>Lodret</option></select></div>
                            <label class="h18-section-type-field" data-types="flex"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[LayoutWrap]" value="1" <?php checked(!empty($section['LayoutWrap'])); ?> /> <strong>Tillad wrap</strong></label>
                            <div class="h18-field h18-section-type-field" data-types="flex"><label><strong>Fordeling</strong></label><select name="<?php echo esc_attr($prefix); ?>[LayoutJustify]"><option value="Start" <?php selected($section['LayoutJustify'],'Start'); ?>>Start</option><option value="Center" <?php selected($section['LayoutJustify'],'Center'); ?>>Center</option><option value="End" <?php selected($section['LayoutJustify'],'End'); ?>>Slut</option><option value="SpaceBetween" <?php selected($section['LayoutJustify'],'SpaceBetween'); ?>>Space between</option></select></div>
                            <div class="h18-field h18-section-type-field" data-types="flex grid"><label><strong>Vertikal/track placering</strong></label><select name="<?php echo esc_attr($prefix); ?>[LayoutAlign]"><option value="Start" <?php selected($section['LayoutAlign'],'Start'); ?>>Start</option><option value="Center" <?php selected($section['LayoutAlign'],'Center'); ?>>Center</option><option value="End" <?php selected($section['LayoutAlign'],'End'); ?>>Slut</option><option value="Stretch" <?php selected($section['LayoutAlign'],'Stretch'); ?>>Stretch</option></select></div>
                            <div class="h18-field"><label><strong>Gap desktop (px)</strong></label><input type="number" min="0" max="120" name="<?php echo esc_attr($prefix); ?>[LayoutGapPx]" value="<?php echo esc_attr($section['LayoutGapPx']); ?>" /></div>
                            <div class="h18-field"><label><strong>Gap mobil (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[MobileLayoutGapPx]" value="<?php echo esc_attr($section['MobileLayoutGapPx']); ?>" /></div>
                            <div class="h18-field h18-section-type-field" data-types="grid"><label><strong>Grid kolonner</strong></label><input type="number" min="1" max="6" name="<?php echo esc_attr($prefix); ?>[LayoutColumns]" value="<?php echo esc_attr($section['LayoutColumns']); ?>" /></div>
                            <div class="h18-field h18-section-type-field" data-types="grid"><label><strong>Grid kolonner mobil</strong></label><input type="number" min="1" max="3" name="<?php echo esc_attr($prefix); ?>[MobileLayoutColumns]" value="<?php echo esc_attr($section['MobileLayoutColumns']); ?>" /></div>
                            <label class="h18-section-type-field" data-types="flex"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[MobileLayoutStack]" value="1" <?php checked(!empty($section['MobileLayoutStack'])); ?> /> <strong>Stack lodret på mobil</strong></label>
                        </div>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="carousel">
                        <h4>Carousel / slider</h4>
                        <p>Autoplay er FRA som standard. Reduced Motion i brugerens system slår automatisk autoplay fra.</p>
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[CarouselAutoplay]" value="1" <?php checked(!empty($section['CarouselAutoplay'])); ?> /> <strong>Autoplay</strong></label>
                            <div class="h18-field"><label><strong>Interval (ms)</strong></label><input type="number" min="2000" max="20000" step="250" name="<?php echo esc_attr($prefix); ?>[CarouselIntervalMs]" value="<?php echo esc_attr($section['CarouselIntervalMs']); ?>" /></div>
                            <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[CarouselLoop]" value="1" <?php checked(!empty($section['CarouselLoop'])); ?> /> <strong>Loop</strong></label>
                            <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[CarouselShowArrows]" value="1" <?php checked(!empty($section['CarouselShowArrows'])); ?> /> <strong>Vis pile</strong></label>
                            <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[CarouselShowDots]" value="1" <?php checked(!empty($section['CarouselShowDots'])); ?> /> <strong>Vis priknavigation</strong></label>
                        </div>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box h18-card-grid-editor h18-collection-editor" data-types="card_grid tabs accordion carousel">
                        <h4 class="h18-collection-editor-title"><?php echo $section['Type'] === 'tabs' ? 'Faner / tabs' : ($section['Type'] === 'accordion' ? 'Accordion' : ($section['Type'] === 'carousel' ? 'Carousel / slider' : 'Kort-række / kolonner')); ?></h4>
                        <p class="h18-collection-editor-description"><?php echo in_array($section['Type'], ['tabs','accordion','carousel'], true) ? 'Hvert panel bruger den eksisterende kassemodel og kan flyttes, farves og tilpasses separat.' : 'Hver kasse kan flyttes, farves og tilpasses separat. På mobil placeres kasserne som standard under hinanden.'; ?></p>
                        <div class="h18-module-fields-grid h18-module-fields-grid--four h18-card-grid-layout-fields">
                            <div class="h18-field"><label><strong>Kolonner desktop</strong></label><select name="<?php echo esc_attr($prefix); ?>[Columns]"><?php for ($columns = 1; $columns <= 4; $columns++) : ?><option value="<?php echo esc_attr($columns); ?>" <?php selected($section['Columns'], $columns); ?>><?php echo esc_html($columns); ?></option><?php endfor; ?></select></div>
                            <div class="h18-field"><label><strong>Kolonner mobil</strong></label><select name="<?php echo esc_attr($prefix); ?>[MobileColumns]"><option value="1" <?php selected($section['MobileColumns'], 1); ?>>1 – under hinanden</option><option value="2" <?php selected($section['MobileColumns'], 2); ?>>2 ved siden af hinanden</option></select></div>
                            <div class="h18-field"><label><strong>Afstand mellem kasser desktop (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[ColumnGapPx]" value="<?php echo esc_attr($section['ColumnGapPx']); ?>" /></div>
                            <div class="h18-field"><label><strong>Afstand mellem kasser mobil (px)</strong></label><input type="number" min="0" max="60" name="<?php echo esc_attr($prefix); ?>[MobileColumnGapPx]" value="<?php echo esc_attr($section['MobileColumnGapPx']); ?>" /></div>
                        </div>
                        <div class="h18-page-cards-sortable">
                            <?php foreach ((array) $section['Cards'] as $card_index => $card) { $this->render_page_editor_card_admin($card, $index, $card_index); } ?>
                        </div>
                        <button class="button h18-add-page-card" type="button"><span class="h18-add-page-card-label"><?php echo in_array($section['Type'], ['tabs','accordion','carousel'], true) ? 'Tilføj panel' : 'Tilføj kasse'; ?></span></button>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="html">
                        <h4>Importerede kolonner</h4>
                        <p>Hvis blokken indeholder WordPress-kolonner, kan de udskilles som selvstændige kasser. Ændringen sker først på den offentlige side, når den gemmes som en ny version.</p>
                        <button class="button h18-split-imported-cards" type="button">Opdel importerede kasser</button>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="mail_form">
                        <h4>Mailformular</h4>
                        <p>Modtageradressen læses kun fra den gemte opsætning og sendes aldrig med formularen til besøgerens browser.</p>
                        <div class="h18-module-fields-grid">
                            <div class="h18-field"><label><strong>Modtageradresse</strong></label><input type="email" name="<?php echo esc_attr($prefix); ?>[RecipientEmail]" value="<?php echo esc_attr($section['RecipientEmail']); ?>" /></div>
                            <div class="h18-field"><label><strong>Bekræftelse efter afsendelse</strong></label><input type="text" name="<?php echo esc_attr($prefix); ?>[SuccessMessage]" value="<?php echo esc_attr($section['SuccessMessage']); ?>" /></div>
                            <div class="h18-field h18-field-wide"><label><strong>Samtykketekst (valgfri)</strong></label><input type="text" name="<?php echo esc_attr($prefix); ?>[ConsentLabel]" value="<?php echo esc_attr($section['ConsentLabel']); ?>" placeholder="Jeg accepterer, at foreningen behandler min henvendelse." /></div>
                            <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[StoreSubmissions]" value="1" <?php checked(!empty($section['StoreSubmissions'])); ?> /> Gem også henvendelser i WordPress</label>
                        </div>
                        <?php if (!$is_template) : ?>
                            <div class="h18-module-status"><strong><?php echo esc_html($this->page_form_submission_count($page->ID, $section['Key'])); ?> gemte henvendelser</strong><?php if ($export_forms) : ?> · <a href="<?php echo esc_url($export_forms); ?>">Eksportér CSV</a><?php endif; ?><?php if ($test_form) : ?> · <a href="<?php echo esc_url($test_form); ?>">Send testmail</a><?php endif; ?></div>
                        <?php endif; ?>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="poll">
                        <h4>Afstemning</h4>
                        <div class="h18-module-fields-grid">
                            <div class="h18-field h18-field-wide"><label><strong>Svarmuligheder – én pr. linje</strong></label><textarea name="<?php echo esc_attr($prefix); ?>[PollOptions]" rows="5"><?php echo esc_textarea(implode("\n", $section['PollOptions'])); ?></textarea></div>
                            <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[AllowMultiple]" value="1" <?php checked(!empty($section['AllowMultiple'])); ?> /> Tillad flere svar</label>
                            <div class="h18-field"><label><strong>Vis resultat</strong></label><select name="<?php echo esc_attr($prefix); ?>[ResultsMode]"><option value="after_vote" <?php selected($section['ResultsMode'], 'after_vote'); ?>>Efter besøgeren har stemt</option><option value="always" <?php selected($section['ResultsMode'], 'always'); ?>>Altid</option><option value="after_close" <?php selected($section['ResultsMode'], 'after_close'); ?>>Efter afslutning</option></select></div>
                            <div class="h18-field"><label><strong>Start (valgfri)</strong></label><input type="datetime-local" name="<?php echo esc_attr($prefix); ?>[StartUtc]" value="<?php echo esc_attr($section['StartUtc']); ?>" /></div>
                            <div class="h18-field"><label><strong>Slut (valgfri)</strong></label><input type="datetime-local" name="<?php echo esc_attr($prefix); ?>[EndUtc]" value="<?php echo esc_attr($section['EndUtc']); ?>" /></div>
                            <?php if (!$is_template) : ?><label class="h18-remove-choice"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[ResetVotes]" value="1" /> Nulstil alle stemmer ved næste gemning</label><?php endif; ?>
                        </div>
                        <?php if (!$is_template) : ?>
                            <div class="h18-module-status"><strong><?php echo esc_html($this->page_poll_vote_count($page->ID, $section)); ?> registrerede stemmer</strong><?php if ($export_poll) : ?> · <a href="<?php echo esc_url($export_poll); ?>">Eksportér CSV</a><?php endif; ?></div>
                        <?php endif; ?>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="spacer">
                        <h4>Afstand</h4>
                        <div class="h18-module-fields-grid"><div class="h18-field"><label><strong>Desktop (px)</strong></label><input type="number" min="0" max="200" name="<?php echo esc_attr($prefix); ?>[SpacerPx]" value="<?php echo esc_attr($section['SpacerPx']); ?>" /></div><div class="h18-field"><label><strong>Mobil (px)</strong></label><input type="number" min="0" max="140" name="<?php echo esc_attr($prefix); ?>[MobileSpacerPx]" value="<?php echo esc_attr($section['MobileSpacerPx']); ?>" /></div></div>
                    </div>

                    <details class="h18-page-section-layout h18-section-type-field" data-types="hero text text_image image buttons card card_grid highlight html mail_form poll spacer">
                        <summary>Luft, baggrund og placering</summary>
                        <div class="h18-layout-devices">
                            <fieldset class="h18-layout-device"><legend>Desktop</legend><div class="h18-layout-fields">
                                <div class="h18-field"><label><strong>Placering</strong></label><select name="<?php echo esc_attr($prefix); ?>[DesktopAlignment]"><option value="Left" <?php selected($section['DesktopAlignment'], 'Left'); ?>>Venstre</option><option value="Center" <?php selected($section['DesktopAlignment'], 'Center'); ?>>Midtstillet</option></select></div>
                                <div class="h18-field"><label><strong>Luft før (px)</strong></label><input type="number" min="0" max="160" name="<?php echo esc_attr($prefix); ?>[TopSpacingPx]" value="<?php echo esc_attr($section['TopSpacingPx']); ?>" /></div>
                                <div class="h18-field"><label><strong>Luft efter (px)</strong></label><input type="number" min="0" max="160" name="<?php echo esc_attr($prefix); ?>[BottomSpacingPx]" value="<?php echo esc_attr($section['BottomSpacingPx']); ?>" /></div>
                                <div class="h18-field"><label><strong>Indvendig luft – lodret (px)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[PaddingPx]" value="<?php echo esc_attr($section['PaddingPx']); ?>" /><p class="description">Luft over og under indholdet inde i sektionen.</p></div>
                                <div class="h18-field"><label><strong>Indvendig luft – vandret (px)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[HorizontalPaddingPx]" value="<?php echo esc_attr($section['HorizontalPaddingPx']); ?>" /><p class="description">Luft i venstre og højre side inde i sektionen.</p></div>
                            </div></fieldset>
                            <fieldset class="h18-layout-device"><legend>Mobil</legend><div class="h18-layout-fields">
                                <div class="h18-field"><label><strong>Placering</strong></label><select name="<?php echo esc_attr($prefix); ?>[MobileAlignment]"><option value="Left" <?php selected($section['MobileAlignment'], 'Left'); ?>>Venstre</option><option value="Center" <?php selected($section['MobileAlignment'], 'Center'); ?>>Midtstillet</option></select></div>
                                <div class="h18-field"><label><strong>Luft før (px)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[MobileTopSpacingPx]" value="<?php echo esc_attr($section['MobileTopSpacingPx']); ?>" /></div>
                                <div class="h18-field"><label><strong>Luft efter (px)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[MobileBottomSpacingPx]" value="<?php echo esc_attr($section['MobileBottomSpacingPx']); ?>" /></div>
                                <div class="h18-field"><label><strong>Indvendig luft – lodret (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[MobilePaddingPx]" value="<?php echo esc_attr($section['MobilePaddingPx']); ?>" /><p class="description">Luft over og under indholdet på mobil.</p></div>
                                <div class="h18-field"><label><strong>Indvendig luft – vandret (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[MobileHorizontalPaddingPx]" value="<?php echo esc_attr($section['MobileHorizontalPaddingPx']); ?>" /><p class="description">Luft i siderne på mobil.</p></div>
                            </div></fieldset>
                        </div>
                        <div class="h18-module-fields-grid"><div class="h18-field"><label><strong>Baggrund</strong></label><select name="<?php echo esc_attr($prefix); ?>[Background]"><option value="White" <?php selected($section['Background'], 'White'); ?>>Hvid</option><option value="OffWhite" <?php selected($section['Background'], 'OffWhite'); ?>>Knækket hvid</option><option value="Sand" <?php selected($section['Background'], 'Sand'); ?>>Sandfarvet</option><option value="Olive" <?php selected($section['Background'], 'Olive'); ?>>Mørk olivengrøn</option><option value="Steel" <?php selected($section['Background'], 'Steel'); ?>>Stålgrå</option></select><p class="description">Bruges når elementet følger Globalt design.</p></div><div class="h18-field"><label><strong>Hjørneafrunding (px)</strong></label><input type="number" min="0" max="30" name="<?php echo esc_attr($prefix); ?>[RadiusPx]" value="<?php echo esc_attr($section['RadiusPx']); ?>" /></div></div>
                        <div class="h18-element-design-box">
                            <h4>Individuelt elementdesign</h4>
                            <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                <div class="h18-field"><label><strong>Farvetilstand</strong></label><select class="h18-section-design-mode" name="<?php echo esc_attr($prefix); ?>[DesignMode]"><option value="Global" <?php selected($section['DesignMode'], 'Global'); ?>>Globalt design</option><option value="Custom" <?php selected($section['DesignMode'], 'Custom'); ?>>Tilpasset</option></select></div>
                                <div class="h18-field"><label><strong>Kantbredde (px)</strong></label><input type="number" min="0" max="12" name="<?php echo esc_attr($prefix); ?>[BorderWidthPx]" value="<?php echo esc_attr($section['BorderWidthPx']); ?>" /></div>
                                <div class="h18-field"><label><strong>Kantfarve</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[CustomBorderColor]" value="<?php echo esc_attr($section['CustomBorderColor']); ?>" /></div>
                                <div class="h18-field"><label><strong>Skygge</strong></label><select name="<?php echo esc_attr($prefix); ?>[ShadowStyle]"><option value="None" <?php selected($section['ShadowStyle'], 'None'); ?>>Ingen</option><option value="Soft" <?php selected($section['ShadowStyle'], 'Soft'); ?>>Blød</option><option value="Medium" <?php selected($section['ShadowStyle'], 'Medium'); ?>>Mellem</option><option value="Strong" <?php selected($section['ShadowStyle'], 'Strong'); ?>>Kraftig</option></select></div>
                            </div>
                            <div class="h18-element-size-fields">
                                <h4>Elementstørrelse</h4>
                                <p class="description">Bredde er procent af sideområdet. 0 px max-bredde betyder ingen grænse. Tablet/mobil med -1 arver desktop.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Bredde desktop (%)</strong></label><input type="number" min="20" max="100" name="<?php echo esc_attr($prefix); ?>[ElementWidthPercent]" value="<?php echo esc_attr($section['ElementWidthPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Bredde tablet (%)</strong></label><input type="number" min="-1" max="100" name="<?php echo esc_attr($prefix); ?>[TabletWidthPercent]" value="<?php echo esc_attr($section['TabletWidthPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Bredde mobil (%)</strong></label><input type="number" min="-1" max="100" name="<?php echo esc_attr($prefix); ?>[MobileWidthPercent]" value="<?php echo esc_attr($section['MobileWidthPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Maks. bredde (px)</strong></label><input type="number" min="0" max="2400" name="<?php echo esc_attr($prefix); ?>[ElementMaxWidthPx]" value="<?php echo esc_attr($section['ElementMaxWidthPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Min. højde desktop (px)</strong></label><input type="number" min="0" max="1600" name="<?php echo esc_attr($prefix); ?>[ElementMinHeightPx]" value="<?php echo esc_attr($section['ElementMinHeightPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Min. højde tablet (px)</strong></label><input type="number" min="-1" max="1600" name="<?php echo esc_attr($prefix); ?>[TabletMinHeightPx]" value="<?php echo esc_attr($section['TabletMinHeightPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Min. højde mobil (px)</strong></label><input type="number" min="-1" max="1200" name="<?php echo esc_attr($prefix); ?>[MobileMinHeightPx]" value="<?php echo esc_attr($section['MobileMinHeightPx']); ?>" /></div>
                                </div>
                            </div>
                            <div class="h18-custom-design-fields">
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Baggrund</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[CustomBackgroundColor]" value="<?php echo esc_attr($section['CustomBackgroundColor']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Tekst</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[CustomTextColor]" value="<?php echo esc_attr($section['CustomTextColor']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Overskrifter</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[CustomHeadingColor]" value="<?php echo esc_attr($section['CustomHeadingColor']); ?>" /></div>
                                </div>
                            </div>
                            <div class="h18-element-typography-box">
                                <h4>Typografi for dette element</h4>
                                <p class="description">Global font og værdien 0 arver det centrale designsystem.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Brødtekst-font</strong></label><select name="<?php echo esc_attr($prefix); ?>[SectionBodyFontFamily]"><?php foreach (['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'] as $font) : ?><option value="<?php echo esc_attr($font); ?>" <?php selected($section['SectionBodyFontFamily'], $font); ?>><?php echo esc_html($font === 'Global' ? 'Global font' : $font); ?></option><?php endforeach; ?></select></div>
                                    <div class="h18-field"><label><strong>Overskrift-font</strong></label><select name="<?php echo esc_attr($prefix); ?>[SectionHeadingFontFamily]"><?php foreach (['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'] as $font) : ?><option value="<?php echo esc_attr($font); ?>" <?php selected($section['SectionHeadingFontFamily'], $font); ?>><?php echo esc_html($font === 'Global' ? 'Global font' : $font); ?></option><?php endforeach; ?></select></div>
                                    <div class="h18-field"><label><strong>Brødtekst (px)</strong></label><input type="number" min="0" max="32" name="<?php echo esc_attr($prefix); ?>[BodyFontSizePx]" value="<?php echo esc_attr($section['BodyFontSizePx']); ?>" /><p class="description">0 = global størrelse</p></div>
                                    <div class="h18-field"><label><strong>H1 (px)</strong></label><input type="number" min="0" max="96" name="<?php echo esc_attr($prefix); ?>[H1FontSizePx]" value="<?php echo esc_attr($section['H1FontSizePx']); ?>" /><p class="description">0 = global størrelse</p></div>
                                    <div class="h18-field"><label><strong>H2 (px)</strong></label><input type="number" min="0" max="80" name="<?php echo esc_attr($prefix); ?>[H2FontSizePx]" value="<?php echo esc_attr($section['H2FontSizePx']); ?>" /><p class="description">0 = global størrelse</p></div>
                                    <div class="h18-field"><label><strong>H3 (px)</strong></label><input type="number" min="0" max="64" name="<?php echo esc_attr($prefix); ?>[H3FontSizePx]" value="<?php echo esc_attr($section['H3FontSizePx']); ?>" /><p class="description">0 = global størrelse</p></div>
                                </div>
                            </div>
                            <div class="h18-element-effects-box">
                                <h4>Effekter og baggrund</h4>
                                <p class="description">Alle standardværdier svarer til v0.5.3. Effekter aktiveres kun, når du vælger dem.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Opacity (%)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[SectionOpacityPercent]" value="<?php echo esc_attr($section['SectionOpacityPercent']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Baggrundseffekt</strong></label><select class="h18-section-background-effect" name="<?php echo esc_attr($prefix); ?>[BackgroundEffect]"><option value="None" <?php selected($section['BackgroundEffect'], 'None'); ?>>Ingen</option><option value="Gradient" <?php selected($section['BackgroundEffect'], 'Gradient'); ?>>Gradient</option><option value="Image" <?php selected($section['BackgroundEffect'], 'Image'); ?>>Baggrundsbillede</option></select></div>
                                    <div class="h18-field"><label><strong>Hover-effekt</strong></label><select name="<?php echo esc_attr($prefix); ?>[HoverEffect]"><option value="None" <?php selected($section['HoverEffect'], 'None'); ?>>Ingen</option><option value="Lift" <?php selected($section['HoverEffect'], 'Lift'); ?>>Løft</option><option value="Scale" <?php selected($section['HoverEffect'], 'Scale'); ?>>Zoom let</option><option value="Shadow" <?php selected($section['HoverEffect'], 'Shadow'); ?>>Mere skygge</option></select></div>
                                    <div class="h18-field"><label><strong>Hover-transition (ms)</strong></label><input type="number" min="0" max="1000" step="10" name="<?php echo esc_attr($prefix); ?>[HoverTransitionMs]" value="<?php echo esc_attr($section['HoverTransitionMs']); ?>" /></div>
                                </div>
                                <div class="h18-hover-state-box">
                                    <h4>Hover-state</h4>
                                    <div class="h18-field"><label><strong>Hover-farver</strong></label><select class="h18-hover-style-mode" name="<?php echo esc_attr($prefix); ?>[HoverStyleMode]"><option value="Inherit" <?php selected($section['HoverStyleMode'], 'Inherit'); ?>>Arv Normal</option><option value="Custom" <?php selected($section['HoverStyleMode'], 'Custom'); ?>>Tilpasset solid state</option></select></div>
                                    <div class="h18-hover-style-fields h18-module-fields-grid h18-module-fields-grid--four">
                                        <div class="h18-field"><label><strong>Baggrund</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[HoverBackgroundColor]" value="<?php echo esc_attr($section['HoverBackgroundColor']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Tekst</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[HoverTextColor]" value="<?php echo esc_attr($section['HoverTextColor']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Overskrift</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[HoverHeadingColor]" value="<?php echo esc_attr($section['HoverHeadingColor']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Kant</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[HoverBorderColor]" value="<?php echo esc_attr($section['HoverBorderColor']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Opacity (%)</strong></label><input type="number" min="0" max="100" name="<?php echo esc_attr($prefix); ?>[HoverOpacityPercent]" value="<?php echo esc_attr($section['HoverOpacityPercent']); ?>" /></div>
                                    </div>
                                </div>
                                <div class="h18-interaction-state-box">
                                    <h4>Interaktions-states</h4>
                                    <p class="description">Focus, Active og Disabled gælder interaktive kontroller inde i dette element. Standarderne arver det globale designsystem.</p>
                                    <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                        <div class="h18-field"><label><strong>Transition</strong></label><select name="<?php echo esc_attr($prefix); ?>[TransitionPreset]"><option value="Inherit" <?php selected($section['TransitionPreset'],'Inherit'); ?>>Global Normal</option><option value="Fast" <?php selected($section['TransitionPreset'],'Fast'); ?>>Fast</option><option value="Normal" <?php selected($section['TransitionPreset'],'Normal'); ?>>Normal</option><option value="Slow" <?php selected($section['TransitionPreset'],'Slow'); ?>>Slow</option><option value="Custom" <?php selected($section['TransitionPreset'],'Custom'); ?>>Brug Hover-transition</option></select></div>
                                        <div class="h18-field"><label><strong>Focus ring</strong></label><select name="<?php echo esc_attr($prefix); ?>[FocusRingStyle]"><option value="Global" <?php selected($section['FocusRingStyle'],'Global'); ?>>Global</option><option value="Custom" <?php selected($section['FocusRingStyle'],'Custom'); ?>>Tilpasset</option><option value="None" <?php selected($section['FocusRingStyle'],'None'); ?>>Ingen</option></select></div>
                                        <div class="h18-field"><label><strong>Focus farve</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[FocusRingColor]" value="<?php echo esc_attr($section['FocusRingColor']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Focus bredde (px)</strong></label><input type="number" min="1" max="8" name="<?php echo esc_attr($prefix); ?>[FocusRingWidthPx]" value="<?php echo esc_attr($section['FocusRingWidthPx']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Focus offset (px)</strong></label><input type="number" min="0" max="12" name="<?php echo esc_attr($prefix); ?>[FocusRingOffsetPx]" value="<?php echo esc_attr($section['FocusRingOffsetPx']); ?>" /></div>
                                        <div class="h18-field"><label><strong>Active-effekt</strong></label><select name="<?php echo esc_attr($prefix); ?>[ActiveEffect]"><option value="None" <?php selected($section['ActiveEffect'],'None'); ?>>Ingen</option><option value="Press" <?php selected($section['ActiveEffect'],'Press'); ?>>Tryk 1 px</option><option value="ScaleDown" <?php selected($section['ActiveEffect'],'ScaleDown'); ?>>Scale 97%</option></select></div>
                                        <div class="h18-field"><label><strong>Disabled opacity (%)</strong></label><input type="number" min="10" max="100" name="<?php echo esc_attr($prefix); ?>[DisabledOpacityPercent]" value="<?php echo esc_attr($section['DisabledOpacityPercent']); ?>" /></div>
                                    </div>
                                </div>
                                <div class="h18-bg-gradient-fields h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Gradient start</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[GradientStartColor]" value="<?php echo esc_attr($section['GradientStartColor']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Gradient slut</strong></label><input type="color" name="<?php echo esc_attr($prefix); ?>[GradientEndColor]" value="<?php echo esc_attr($section['GradientEndColor']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Vinkel (grader)</strong></label><input type="number" min="0" max="360" name="<?php echo esc_attr($prefix); ?>[GradientAngleDeg]" value="<?php echo esc_attr($section['GradientAngleDeg']); ?>" /></div>
                                </div>
                                <div class="h18-bg-image-fields">
                                    <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                        <div class="h18-field h18-field-wide"><label><strong>Baggrundsbillede</strong></label><input class="h18-section-bg-media-id" type="hidden" name="<?php echo esc_attr($prefix); ?>[BackgroundMediaId]" value="<?php echo esc_attr($section['BackgroundMediaId']); ?>" /><input class="h18-section-bg-media-url" type="url" name="<?php echo esc_attr($prefix); ?>[BackgroundImageUrl]" value="<?php echo esc_attr($section['BackgroundImageUrl']); ?>" placeholder="https://..." /><div class="h18-section-bg-media-preview"><?php if ($section['BackgroundMediaId']) { echo wp_get_attachment_image($section['BackgroundMediaId'], 'thumbnail'); } ?></div><button class="button h18-page-select-bg-media" type="button">Vælg fra mediebibliotek</button> <button class="button-link-delete h18-page-remove-bg-media" type="button">Fjern</button></div>
                                        <div class="h18-field"><label><strong>Placering</strong></label><select name="<?php echo esc_attr($prefix); ?>[BackgroundImagePosition]"><option value="Center" <?php selected($section['BackgroundImagePosition'], 'Center'); ?>>Center</option><option value="Top" <?php selected($section['BackgroundImagePosition'], 'Top'); ?>>Top</option><option value="Bottom" <?php selected($section['BackgroundImagePosition'], 'Bottom'); ?>>Bund</option><option value="Left" <?php selected($section['BackgroundImagePosition'], 'Left'); ?>>Venstre</option><option value="Right" <?php selected($section['BackgroundImagePosition'], 'Right'); ?>>Højre</option></select></div>
                                        <div class="h18-field"><label><strong>Skalering</strong></label><select name="<?php echo esc_attr($prefix); ?>[BackgroundImageSize]"><option value="Cover" <?php selected($section['BackgroundImageSize'], 'Cover'); ?>>Fyld området</option><option value="Contain" <?php selected($section['BackgroundImageSize'], 'Contain'); ?>>Vis hele billedet</option><option value="Auto" <?php selected($section['BackgroundImageSize'], 'Auto'); ?>>Original størrelse</option></select></div>
                                    </div>
                                </div>
                                <h4>Individuelle hjørner</h4>
                                <p class="description">-1 bruger den almindelige hjørneafrunding. 0 giver et helt skarpt hjørne.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Top venstre</strong></label><input type="number" min="-1" max="60" name="<?php echo esc_attr($prefix); ?>[RadiusTopLeftPx]" value="<?php echo esc_attr($section['RadiusTopLeftPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Top højre</strong></label><input type="number" min="-1" max="60" name="<?php echo esc_attr($prefix); ?>[RadiusTopRightPx]" value="<?php echo esc_attr($section['RadiusTopRightPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Bund højre</strong></label><input type="number" min="-1" max="60" name="<?php echo esc_attr($prefix); ?>[RadiusBottomRightPx]" value="<?php echo esc_attr($section['RadiusBottomRightPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Bund venstre</strong></label><input type="number" min="-1" max="60" name="<?php echo esc_attr($prefix); ?>[RadiusBottomLeftPx]" value="<?php echo esc_attr($section['RadiusBottomLeftPx']); ?>" /></div>
                                </div>
                            </div>
                            <div class="h18-responsive-controls-box">
                                <h4>Responsiv elementstyring</h4>
                                <div class="h18-responsive-visibility">
                                    <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[ShowDesktop]" value="1" <?php checked(!empty($section['ShowDesktop'])); ?> /> Desktop</label>
                                    <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[ShowTablet]" value="1" <?php checked(!empty($section['ShowTablet'])); ?> /> Tablet</label>
                                    <label><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[ShowMobile]" value="1" <?php checked(!empty($section['ShowMobile'])); ?> /> Mobil</label>
                                </div>
                                <h4>Tablet-layout</h4>
                                <p class="description">Inherit/-1 bruger desktop-værdien.</p>
                                <div class="h18-module-fields-grid h18-module-fields-grid--four">
                                    <div class="h18-field"><label><strong>Placering</strong></label><select name="<?php echo esc_attr($prefix); ?>[TabletAlignment]"><option value="Inherit" <?php selected($section['TabletAlignment'], 'Inherit'); ?>>Arv desktop</option><option value="Left" <?php selected($section['TabletAlignment'], 'Left'); ?>>Venstre</option><option value="Center" <?php selected($section['TabletAlignment'], 'Center'); ?>>Midt</option></select></div>
                                    <div class="h18-field"><label><strong>Luft før</strong></label><input type="number" min="-1" max="160" name="<?php echo esc_attr($prefix); ?>[TabletTopSpacingPx]" value="<?php echo esc_attr($section['TabletTopSpacingPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Luft efter</strong></label><input type="number" min="-1" max="160" name="<?php echo esc_attr($prefix); ?>[TabletBottomSpacingPx]" value="<?php echo esc_attr($section['TabletBottomSpacingPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Indvendig lodret</strong></label><input type="number" min="-1" max="100" name="<?php echo esc_attr($prefix); ?>[TabletPaddingPx]" value="<?php echo esc_attr($section['TabletPaddingPx']); ?>" /></div>
                                    <div class="h18-field"><label><strong>Indvendig vandret</strong></label><input type="number" min="-1" max="100" name="<?php echo esc_attr($prefix); ?>[TabletHorizontalPaddingPx]" value="<?php echo esc_attr($section['TabletHorizontalPaddingPx']); ?>" /></div>
                                </div>
                                <h4>Transform pr. enhed</h4>
                                <div class="h18-responsive-device-grid">
                                    <?php foreach ([
                                        'Desktop' => ['DesktopTranslateXPx','DesktopTranslateYPx','DesktopScalePercent','DesktopRotateDeg'],
                                        'Tablet' => ['TabletTranslateXPx','TabletTranslateYPx','TabletScalePercent','TabletRotateDeg'],
                                        'Mobil' => ['MobileTranslateXPx','MobileTranslateYPx','MobileScalePercent','MobileRotateDeg']
                                    ] as $device_label => $device_fields) : ?>
                                        <fieldset class="h18-responsive-transform-device"><legend><?php echo esc_html($device_label); ?></legend>
                                            <div class="h18-field"><label><strong>X (px)</strong></label><input type="number" min="-300" max="300" name="<?php echo esc_attr($prefix); ?>[<?php echo esc_attr($device_fields[0]); ?>]" value="<?php echo esc_attr($section[$device_fields[0]]); ?>" /></div>
                                            <div class="h18-field"><label><strong>Y (px)</strong></label><input type="number" min="-300" max="300" name="<?php echo esc_attr($prefix); ?>[<?php echo esc_attr($device_fields[1]); ?>]" value="<?php echo esc_attr($section[$device_fields[1]]); ?>" /></div>
                                            <div class="h18-field"><label><strong>Skala (%)</strong></label><input type="number" min="50" max="150" name="<?php echo esc_attr($prefix); ?>[<?php echo esc_attr($device_fields[2]); ?>]" value="<?php echo esc_attr($section[$device_fields[2]]); ?>" /></div>
                                            <div class="h18-field"><label><strong>Rotation (°)</strong></label><input type="number" min="-180" max="180" name="<?php echo esc_attr($prefix); ?>[<?php echo esc_attr($device_fields[3]); ?>]" value="<?php echo esc_attr($section[$device_fields[3]]); ?>" /></div>
                                        </fieldset>
                                    <?php endforeach; ?>
                                </div>
                            </div>
                        </div>
                    </details>
                <?php endif; ?>
            </div>
        </article>
        <?php
    }

    private function conversion_test_page_for_source($source_id) {
        $source_id = absint($source_id);
        if ($source_id <= 0) {
            return null;
        }

        $pages = get_posts([
            'post_type'      => 'page',
            'post_status'    => ['draft', 'pending', 'private', 'publish'],
            'posts_per_page' => 1,
            'meta_key'       => '_h18_conversion_test_source_id',
            'meta_value'     => $source_id,
            'orderby'        => 'ID',
            'order'          => 'DESC',
        ]);
        return isset($pages[0]) && $pages[0] instanceof WP_Post ? $pages[0] : null;
    }

    private function adapt_page_editor_data_to_test_page(array $data, $source_id, $test_id) {
        $source_id = absint($source_id);
        $test_id = absint($test_id);
        if ($source_id <= 0 || $test_id <= 0 || $source_id === $test_id) {
            return $data;
        }

        foreach ($data['Sections'] as &$section) {
            foreach (['Content', 'LegacyHtml'] as $field) {
                if (!isset($section[$field]) || !is_string($section[$field])) {
                    continue;
                }
                $section[$field] = str_replace(
                    'page-id-' . $source_id,
                    'page-id-' . $test_id,
                    $section[$field]
                );
            }
        }
        unset($section);
        return $data;
    }

    private function page_snapshot_before_editor($page) {
        if (!$page instanceof WP_Post) {
            return null;
        }

        $revisions = function_exists('wp_get_post_revisions')
            ? wp_get_post_revisions($page->ID, [
                'posts_per_page' => 100,
                'orderby'        => 'date ID',
                'order'          => 'DESC',
                'check_enabled'  => false,
            ])
            : [];
        foreach ((array) $revisions as $revision) {
            if (!$revision instanceof WP_Post) {
                continue;
            }
            $content = (string) $revision->post_content;
            if ($content === '' || strpos($content, self::PAGE_EDITOR_MARKER) !== false) {
                continue;
            }
            return [
                'source'       => 'WordPress-revision ' . (int) $revision->ID,
                'revision_id'  => (int) $revision->ID,
                'post_title'   => (string) $revision->post_title,
                'post_excerpt' => (string) $revision->post_excerpt,
                'post_content' => $content,
                'featured_id'  => (int) get_post_thumbnail_id($page->ID),
            ];
        }

        $paths = glob(trailingslashit($this->backup_dir()) . 'Hangar18-Web-*.json') ?: [];
        usort($paths, static function($a, $b) {
            return filemtime($b) <=> filemtime($a);
        });
        foreach (array_slice($paths, 0, 200) as $path) {
            try {
                $payload = $this->read_managed_backup_file(basename($path));
            } catch (Throwable $ignored) {
                continue;
            }
            $posts = isset($payload['posts']) && is_array($payload['posts'])
                ? $payload['posts']
                : (isset($payload['post']) && is_array($payload['post']) ? [$payload['post']] : []);
            foreach ($posts as $post) {
                if (!is_array($post)) {
                    continue;
                }
                $same_page = absint($post['ID'] ?? 0) === (int) $page->ID ||
                    sanitize_title((string) ($post['post_name'] ?? '')) === sanitize_title((string) $page->post_name);
                $content = (string) ($post['post_content'] ?? '');
                if (!$same_page || $content === '' || strpos($content, self::PAGE_EDITOR_MARKER) !== false) {
                    continue;
                }
                return [
                    'source'       => 'backup ' . basename($path),
                    'revision_id'  => 0,
                    'post_title'   => (string) ($post['post_title'] ?? $page->post_title),
                    'post_excerpt' => (string) ($post['post_excerpt'] ?? ''),
                    'post_content' => $content,
                    'featured_id'  => absint($post['featured_id'] ?? 0),
                ];
            }
        }

        return null;
    }

    public function render_pages() {
        $this->require_capability();
        $definitions = $this->editable_page_definitions();
        $slug = isset($_GET['page_slug']) ? sanitize_title(wp_unslash($_GET['page_slug'])) : self::HOME_SLUG;
        if (!isset($definitions[$slug])) {
            $slug = self::HOME_SLUG;
        }
        $page = $this->post_by_slug($slug);
        $converted_sections = 0;
        $data = $page ? $this->get_page_editor_data_for_admin($slug, $page, $converted_sections) : null;
        $is_converted = $page instanceof WP_Post && strpos((string) $page->post_content, self::PAGE_EDITOR_MARKER) !== false;
        $conversion_test = $page instanceof WP_Post ? $this->conversion_test_page_for_source($page->ID) : null;
        $versions = $page instanceof WP_Post ? $this->get_page_version_history($slug) : [];
        $page_presets = $this->get_page_presets();
        $page_components = $this->get_page_components_for_editor();
        $page_templates = $this->get_page_templates_for_editor();
        $dynamic_data_catalog = $this->dynamic_data_context_catalog_for_editor();
        ?>
        <div class="wrap h18-admin h18-pages-admin">
            <h1>Sider</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box"><strong>Hangar18 sideeditor:</strong> Byg almindelige sider af indholdssektioner og funktionsmoduler. Header og footer ligger uden for editoren og kan derfor ikke slettes her. Køretøjer, Events og Billedgalleri har fortsat deres egne redigeringssider.</div>

            <div class="h18-pages-create-bar">
                <div class="h18-pages-create-copy">
                    <strong>Opret ny side</strong>
                    <span>Start med en tom Hangar18-side, eller brug en gemt Page Template.</span>
                </div>
                <div class="h18-pages-create-actions">
                    <button type="button" class="button button-primary" id="h18-create-blank-page"><span class="dashicons dashicons-plus-alt2" aria-hidden="true"></span> Ny tom side</button>
                    <button type="button" class="button" id="h18-create-from-template"><span class="dashicons dashicons-layout" aria-hidden="true"></span> Fra Page Template…</button>
                </div>
            </div>

            <nav class="h18-page-tabs" aria-label="Vælg side">
                <?php foreach ($definitions as $page_slug => $label) : ?>
                    <a class="<?php echo $page_slug === $slug ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-pages&page_slug=' . rawurlencode($page_slug))); ?>"><?php echo esc_html($label); ?></a>
                <?php endforeach; ?>
            </nav>

            <?php if (!$page) : ?>
                <div class="notice notice-error"><p>Siden <strong><?php echo esc_html($definitions[$slug]); ?></strong> blev ikke fundet.</p></div>
            <?php else : ?>
                <div class="h18-toolbar"><div><strong>Redigerer:</strong> <?php echo esc_html($page->post_title); ?> · <strong>Version:</strong> <?php echo (int) ($data['ContentVersion'] ?? 0) > 0 ? 'v' . esc_html($data['ContentVersion']) : 'Ikke versioneret endnu'; ?></div><p class="h18-toolbar-note">Nuværende indhold indlæses som redigerbare sektioner. Den offentlige side ændres først, når du vælger Gem siden.</p><a class="button" target="_blank" rel="noopener" href="<?php echo esc_url(get_permalink($page)); ?>">Åbn offentlig side</a></div>

                <?php if ($converted_sections > 0) : ?>
                    <div class="notice notice-info inline h18-page-import-notice"><p><strong>Nuværende sideindhold er gjort redigerbart.</strong> Editorens kladde indeholder <?php echo esc_html($converted_sections); ?> importerede sektioner. Gennemgå desktop og mobil, og vælg først <strong>Gem siden</strong>, når opdelingen ser rigtig ud. Indtil da er den offentlige side helt uændret.</p></div>
                <?php endif; ?>

                <?php if (!$is_converted && !empty($data['Sections'])) : ?>
                    <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <?php wp_nonce_field('h18_create_page_conversion_test_' . $slug); ?>
                        <input type="hidden" name="action" value="h18_create_page_conversion_test" />
                        <input type="hidden" name="page_slug" value="<?php echo esc_attr($slug); ?>" />
                        <div class="h18-action-copy">
                            <strong>Test konverteringen uden at ændre originalsiden</strong>
                            <span>Opretter eller opdaterer en separat offentlig testkopi. Kopien føjes ikke til menuen og skjules for søgemaskiner. Brug den til at sammenligne desktop og mobil før Gem siden.</span>
                        </div>
                        <div class="h18-action-submit">
                            <?php if ($conversion_test instanceof WP_Post) : ?>
                                <a class="button" target="_blank" rel="noopener" href="<?php echo esc_url(get_permalink($conversion_test)); ?>">Åbn eksisterende test</a>
                            <?php endif; ?>
                            <button class="button button-secondary" type="submit"><?php echo $conversion_test instanceof WP_Post ? 'Opdatér konverteringstest' : 'Opret konverteringstest'; ?></button>
                        </div>
                    </form>
                <?php endif; ?>

                <?php if ($is_converted) : ?>
                    <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <?php wp_nonce_field('h18_restore_page_before_editor_' . $slug); ?>
                        <input type="hidden" name="action" value="h18_restore_page_before_editor" />
                        <input type="hidden" name="page_slug" value="<?php echo esc_attr($slug); ?>" />
                        <div class="h18-action-copy">
                            <strong>Fortryd konverteringen af denne side</strong>
                            <span>Finder den seneste WordPress-revision eller JSON-backup fra før sideeditoren, tager først en ny sikkerhedskopi og rydder derefter kun denne side fra editorlageret. Menu, header, footer og andre sider ændres ikke.</span>
                        </div>
                        <div class="h18-action-submit">
                            <button class="button" type="submit" onclick="return confirm('Gendan denne side til versionen fra før Hangar18 sideeditor? Der tages først en ny backup af den nuværende version.');">Gendan siden fra før editoren</button>
                        </div>
                    </form>
                <?php endif; ?>

                <form id="h18-page-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <?php wp_nonce_field('h18_save_page_editor'); ?>
                    <input type="hidden" name="action" value="h18_save_page_editor" />
                    <input type="hidden" name="page_slug" value="<?php echo esc_attr($slug); ?>" />

                    <div class="h18-form-header">
                        <div><h2><?php echo esc_html($definitions[$slug]); ?></h2><p>Tilføj sektioner, træk dem i den ønskede rækkefølge, og kontrollér desktop- og mobilvisningen.</p></div>
                        <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                    </div>

                    <div class="h18-page-editor-title h18-layout-card">
                        <div class="h18-field"><label><strong>WordPress-sidetitel</strong></label><input type="text" name="editor_page_title" value="<?php echo esc_attr($data['PageTitle']); ?>" required /><p class="description">Menupunktets viste navn ændres fortsat under Menu.</p></div>
                        <div class="h18-field"><label><strong>Hvad er ændret?</strong></label><textarea name="page_change_note" rows="3" maxlength="500" placeholder="Fx Rettet overskrift, ændret luft mellem kort og udskiftet kontaktknappen."></textarea><p class="description">Skal udfyldes ved en rigtig gemning. Teksten gemmes sammen med versionsnummer, tidspunkt, bruger og backup. Ved WhatIf er feltet valgfrit.</p></div>
                    </div>


                    <div class="h18-page-data-context h18-layout-card">
                        <div class="h18-field">
                            <label><strong>Current data context – datatype</strong></label>
                            <select id="h18-page-data-context-type" name="data_context_type">
                                <option value="">Ingen – brug statiske værdier</option>
                                <?php foreach ($dynamic_data_catalog as $context_type) : ?>
                                    <option value="<?php echo esc_attr($context_type['Key']); ?>" <?php selected((string) ($data['DataContextType'] ?? ''), (string) $context_type['Key']); ?>><?php echo esc_html($context_type['PluralLabel']); ?></option>
                                <?php endforeach; ?>
                            </select>
                            <p class="description">Bindings bruger kun den valgte entry. Static elementværdier bevares som fallback.</p>
                        </div>
                        <div class="h18-field">
                            <label><strong>Current data context – entry</strong></label>
                            <select id="h18-page-data-context-entry" name="data_context_entry_id" data-current-entry="<?php echo esc_attr((int) ($data['DataContextEntryId'] ?? 0)); ?>"><option value="0">Ingen entry</option></select>
                        </div>
                    </div>

                    <div class="h18-page-preview-toolbar">
                        <strong>Editorvisning:</strong>
                        <button type="button" class="button h18-preview-device is-active" data-device="desktop">Desktop</button>
                        <button type="button" class="button h18-preview-device" data-device="tablet">Tablet</button>
                        <button type="button" class="button h18-preview-device" data-device="mobile">Mobil</button>
                        <span class="h18-editor-history-controls">
                            <button type="button" class="button" id="h18-editor-undo" disabled title="Fortryd sidste ændring (Ctrl/Cmd+Z)">↶ Fortryd</button>
                            <button type="button" class="button" id="h18-editor-redo" disabled title="Gendan ændring (Ctrl/Cmd+Shift+Z)">↷ Gendan</button>
                            <span id="h18-editor-history-status" class="h18-editor-history-status" aria-live="polite">Ingen ugemte ændringer</span>
                        </span>
                        <span class="h18-editor-draft-controls">
                            <span id="h18-editor-autosave-status" class="h18-editor-autosave-status" aria-live="polite">Lokal kladde: klar</span>
                            <span id="h18-editor-recovery-actions" class="h18-editor-recovery-actions" hidden>
                                <button type="button" class="button button-small button-primary" id="h18-editor-restore-draft">Gendan kladde</button>
                                <button type="button" class="button button-small" id="h18-editor-discard-draft">Kassér kladde</button>
                            </span>
                        </span>
                        <div class="h18-editor-save-controls">
                            <button type="submit" class="button button-primary" id="h18-editor-save-top" title="Gem som permanent version (Ctrl/Cmd+S)">Gem</button>
                            <span id="h18-editor-save-status" class="h18-editor-save-status" aria-live="polite">Gemt</span>
                        </div>
                        <button type="button" class="button h18-command-palette-open" id="h18-command-palette-open" aria-haspopup="dialog" aria-controls="h18-command-palette" aria-expanded="false" title="Åbn kommandopaletten (Ctrl/Cmd+K)">⌘K Kommandoer</button>
                        <span>Visningen gør arbejdsområdet smallere. Den offentlige side åbnes med knappen ovenfor.</span>
                    </div>

                    <div id="h18-command-palette" class="h18-command-palette" hidden>
                        <div class="h18-command-palette-backdrop" data-command-close="1"></div>
                        <section class="h18-command-palette-dialog" role="dialog" aria-modal="true" aria-labelledby="h18-command-palette-title">
                            <header class="h18-command-palette-header">
                                <div><strong id="h18-command-palette-title">Kommandoer og hurtignavigation</strong><small>Søg efter handlinger eller elementer på siden.</small></div>
                                <button type="button" class="button-link h18-command-palette-close" aria-label="Luk kommandopaletten">Esc</button>
                            </header>
                            <label class="screen-reader-text" for="h18-command-palette-search">Søg i kommandoer</label>
                            <input id="h18-command-palette-search" class="h18-command-palette-search" type="search" autocomplete="off" spellcheck="false" placeholder="Søg: hero, mobil, fortryd, kontakt …" aria-controls="h18-command-palette-results" />
                            <div id="h18-command-palette-results" class="h18-command-palette-results" role="listbox" aria-label="Kommandoresultater"></div>
                            <div id="h18-command-palette-empty" class="h18-command-palette-empty" hidden>Ingen kommandoer matcher søgningen.</div>
                            <footer class="h18-command-palette-footer"><span>↑↓ vælg</span><span>Enter udfør</span><span>Esc luk</span><span>Alt+↑/↓ skift element</span></footer>
                        </section>
                    </div>

                    <div class="h18-visual-builder">
                        <aside class="h18-builder-palette">
                            <div class="h18-builder-sidebar-tabs" role="tablist" aria-label="Builderpanel">
                                <button type="button" class="h18-builder-sidebar-tab is-active" data-builder-tab="elements">Elementer</button>
                                <button type="button" class="h18-builder-sidebar-tab" data-builder-tab="layers">Lag</button>
                                <button type="button" class="h18-builder-sidebar-tab" data-builder-tab="components">Komponenter</button>
                            </div>

                            <div class="h18-builder-sidebar-panel is-active" data-builder-panel="elements">
                                <h3>Elementer og funktioner</h3>
                                <p>Træk et element ind på siden, eller klik for at tilføje det nederst.</p>
                                <div class="h18-builder-palette-list">
                                    <?php foreach ($this->page_section_type_labels() as $value => $label) : if (in_array($value, ['legacy', 'css'], true)) { continue; } ?>
                                        <button class="h18-builder-palette-item" type="button" draggable="true" data-section-type="<?php echo esc_attr($value); ?>"><span class="dashicons dashicons-plus-alt2"></span><?php echo esc_html($label); ?></button>
                                    <?php endforeach; ?>
                                </div>
                                <details><summary>Avanceret</summary><button class="h18-builder-palette-item" type="button" draggable="true" data-section-type="css"><span class="dashicons dashicons-editor-code"></span>Side-CSS</button></details>
                            </div>

                            <div class="h18-builder-sidebar-panel" data-builder-panel="layers">
                                <div class="h18-builder-panel-heading"><h3>Navigator / lag</h3><span id="h18-page-navigator-count">0</span></div>
                                <p>Klik for at redigere. Træk lagene for at ændre rækkefølgen på siden.</p>
                                <div id="h18-page-navigator-list" class="h18-page-navigator-list"></div>
                            </div>

                            <div class="h18-builder-sidebar-panel" data-builder-panel="components">
                                <h3>Komponentbibliotek</h3>
                                <p>Færdige kombinationer du kan indsætte og derefter tilpasse.</p>
                                <div class="h18-builder-component-list">
                                    <button type="button" class="h18-builder-component-item" data-section-preset="hero-cta"><span class="dashicons dashicons-cover-image"></span><strong>Hero + handling</strong><small>Stor introduktion med knap</small></button>
                                    <button type="button" class="h18-builder-component-item" data-section-preset="text-image"><span class="dashicons dashicons-align-pull-left"></span><strong>Tekst + billede</strong><small>To-delt præsentation</small></button>
                                    <button type="button" class="h18-builder-component-item" data-section-preset="info-cards"><span class="dashicons dashicons-screenoptions"></span><strong>3 informationskort</strong><small>Responsivt kort-grid</small></button>
                                    <button type="button" class="h18-builder-component-item" data-section-preset="cta-band"><span class="dashicons dashicons-megaphone"></span><strong>CTA-bånd</strong><small>Fremhævet handlingssektion</small></button>
                                    <button type="button" class="h18-builder-component-item" data-section-preset="contact-form"><span class="dashicons dashicons-email-alt"></span><strong>Kontaktblok</strong><small>Tekst og mailformular</small></button>
                                </div>
                                <div class="h18-user-components-heading"><h4>Linked components</h4><span>Global definition</span></div>
                                <div id="h18-linked-components-list" class="h18-user-presets-list"><p class="description">Vælg et subtree og brug “Gem som linked component” i Inspector.</p></div>
                                <div class="h18-user-components-heading"><h4>Patterns</h4><span>Ikke-linked kopier</span></div>
                                <div id="h18-user-presets-list" class="h18-user-presets-list"><p class="description">Vælg en sektion og brug “Gem som pattern” i Inspector.</p></div>
                                <div class="h18-user-components-heading"><h4>Page Templates</h4><span>Frie sidekopier</span></div>
                                <button type="button" class="button" id="h18-save-page-template">Gem denne side som template</button>
                                <div id="h18-page-templates-list" class="h18-user-presets-list"><p class="description">Gem hele den aktuelle side som en ikke-linked template.</p></div>
                            </div>
                        </aside>

                        <div class="h18-builder-canvas">
                            <div class="h18-builder-canvas-heading"><h3>Sideopbygning</h3><span>Træk sektionerne i den ønskede rækkefølge</span></div>
                            <div id="h18-page-sections-sortable" class="h18-page-sections h18-preview-desktop">
                                <?php foreach ($data['Sections'] as $index => $section) { $this->render_page_editor_section_admin($page, $section, $index); } ?>
                            </div>
                            <div class="h18-builder-drop-hint">Slip et nyt element her</div>
                        </div>

                        <aside id="h18-page-inspector" class="h18-builder-inspector" data-inspector-panel="content">
                            <div class="h18-builder-inspector-heading"><h3>Inspector</h3><span>Vælg en sektion i sideopbygningen</span></div>
                            <div class="h18-inspector-tabs" role="tablist" aria-label="Elementindstillinger">
                                <button type="button" class="h18-inspector-tab is-active" data-inspector-tab="content">Indhold</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="typography">Typografi</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="design">Design</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="advanced">Avanceret</button>
                            </div>
                            <div id="h18-page-inspector-target"><p class="description">Klik på <strong>Rediger</strong> ved en sektion for at ændre indhold, design og responsive indstillinger.</p></div>
                            <div id="h18-inspector-advanced-panel" class="h18-inspector-advanced-panel">
                                <div class="h18-inspector-meta-grid">
                                    <div><span>Type</span><strong id="h18-inspector-type">–</strong></div>
                                    <div><span>Elementnøgle</span><code id="h18-inspector-key">–</code></div>
                                </div>
                                <div class="h18-inspector-advanced-actions">
                                    <button type="button" class="button" id="h18-inspector-copy-key" disabled>Kopiér nøgle</button>
                                    <button type="button" class="button" id="h18-inspector-duplicate" disabled>Duplikér element</button>
                                    <button type="button" class="button" id="h18-inspector-copy-design" disabled>Kopiér design</button>
                                    <button type="button" class="button" id="h18-inspector-paste-design" disabled>Indsæt design</button>
                                    <button type="button" class="button" id="h18-save-section-preset" disabled>Gem som pattern</button>
                                    <button type="button" class="button button-primary" id="h18-save-linked-component" disabled>Gem subtree som linked component</button>
                                </div>
                                <p class="description">Patterns indsættes som frie kopier. Linked components deler én global definition og kan kun overskrives gennem frigivne inputs.</p>
                            </div>
                        </aside>
                    </div>

                    <div class="h18-add-section-bar">
                        <div><strong>Alternativ til træk-og-slip</strong><p>Vælg en sektion eller funktion på listen, og tilføj den nederst.</p></div>
                        <select id="h18-new-section-type"><?php foreach ($this->page_section_type_labels() as $value => $label) : if ($value === 'legacy') { continue; } ?><option value="<?php echo esc_attr($value); ?>"><?php echo esc_html($label); ?></option><?php endforeach; ?></select>
                        <button id="h18-add-page-section" class="button button-secondary" type="button">Tilføj sektion</button>
                    </div>

                    <div class="h18-form-actions h18-explained-action">
                        <div class="h18-whatif-help"><div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Simulering kontrollerer opsætningen uden at gemme siden, nulstille stemmer eller sende noget.</span></div></div>
                        <div class="h18-action-submit"><button class="button button-primary button-hero" type="submit">Gem som ny version</button><div class="h18-action-copy"><strong>Backup, sidekopi og versionshistorik</strong><span>Gemmer ændringsbeskrivelsen, tager backup og bygger siden igen som næste versionsnummer.</span></div></div>
                    </div>
                </form>

                <section class="h18-layout-card" style="margin-top:18px;padding:18px;">
                    <h2>Versionshistorik</h2>
                    <p>Hver rigtig gemning får sit eget versionsnummer og en beskrivelse. WhatIf opretter ingen historik.</p>
                    <?php if (!$versions) : ?>
                        <p><em>Der er endnu ingen registrerede versioner. Den næste rigtige gemning bliver registreret her.</em></p>
                    <?php else : ?>
                        <div class="h18-log-table-wrap">
                            <table class="widefat striped">
                                <thead><tr><th>Version</th><th>Tid</th><th>Bruger</th><th>Ændringsbeskrivelse</th><th>Backup</th></tr></thead>
                                <tbody>
                                <?php foreach (array_slice($versions, 0, 30) as $version_entry) :
                                    $saved_timestamp = $version_entry['SavedUtc'] !== '' ? strtotime($version_entry['SavedUtc']) : false;
                                    $saved_display = $saved_timestamp ? wp_date('d-m-Y H:i:s', $saved_timestamp) : $version_entry['SavedUtc'];
                                ?>
                                    <tr>
                                        <td><strong>v<?php echo esc_html($version_entry['Version']); ?></strong></td>
                                        <td><?php echo esc_html($saved_display); ?></td>
                                        <td><?php echo esc_html($version_entry['UserDisplay']); ?></td>
                                        <td><?php echo nl2br(esc_html($version_entry['ChangeNote'])); ?></td>
                                        <td><details><summary>Vis filer</summary><code><?php echo esc_html($version_entry['FullBackupFile']); ?></code><br><code><?php echo esc_html($version_entry['SnapshotFile']); ?></code></details></td>
                                    </tr>
                                <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    <?php endif; ?>
                </section>

                <script id="h18-page-presets-data" type="application/json"><?php echo wp_json_encode(array_values($page_presets), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id="h18-page-components-data" type="application/json"><?php echo wp_json_encode(array_values($page_components), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id="h18-page-templates-data" type="application/json"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id="h18-dynamic-data-catalog" type="application/json"><?php echo wp_json_encode(array_values($dynamic_data_catalog), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id="h18-page-section-template"><?php $this->render_page_editor_section_admin($page, $this->default_page_section('text', 10), '__INDEX__', true); ?></template>
                <template id="h18-page-card-template"><?php $this->render_page_editor_card_admin($this->default_page_card(10), '__SECTION_INDEX__', '__CARD_INDEX__'); ?></template>
            <?php endif; ?>
        </div>
        <?php
    }

    private function redirect_page_editor($slug) {
        $this->redirect('hangar18-pages', ['page_slug' => sanitize_title((string) $slug)]);
    }

    public function handle_create_page_conversion_test() {
        $this->require_capability();
        $slug = sanitize_title($this->post_text('page_slug'));
        check_admin_referer('h18_create_page_conversion_test_' . $slug);

        $definitions = $this->editable_page_definitions();
        if (!isset($definitions[$slug])) {
            $this->set_notice('error', 'Den valgte side kan ikke bruges til en konverteringstest.');
            $this->redirect_page_editor(self::HOME_SLUG);
        }

        try {
            if (!current_user_can('publish_pages')) {
                throw new RuntimeException('Din bruger må ikke udgive den offentlige testkopi.');
            }

            $source = $this->post_by_slug($slug);
            if (!$source instanceof WP_Post) {
                throw new RuntimeException('Originalsiden blev ikke fundet.');
            }
            if (strpos((string) $source->post_content, self::PAGE_EDITOR_MARKER) !== false) {
                throw new RuntimeException('Siden er allerede konverteret til Hangar18 sideeditor.');
            }

            $converted_sections = 0;
            $data = $this->get_page_editor_data_for_admin($slug, $source, $converted_sections);
            if (empty($data['Sections'])) {
                throw new RuntimeException('Der blev ikke fundet indhold, som kunne vises i testen.');
            }

            $test = $this->conversion_test_page_for_source($source->ID);
            if ($test instanceof WP_Post) {
                $test_id = (int) $test->ID;
            } else {
                $test_id = wp_insert_post([
                    'post_type'      => 'page',
                    'post_status'    => 'draft',
                    'post_title'     => $source->post_title . ' – konverteringstest',
                    'post_name'      => $slug . '-editor-test',
                    'post_content'   => '<!-- Hangar18 konverteringstest oprettes -->',
                    'post_excerpt'   => 'Sikker sammenligningskopi. Originalsiden og menuen ændres ikke.',
                    'comment_status' => 'closed',
                    'ping_status'    => 'closed',
                    'page_template'  => 'default',
                ], true);
                if (is_wp_error($test_id)) {
                    throw new RuntimeException($test_id->get_error_message());
                }
                $test_id = (int) $test_id;
            }

            $data = $this->adapt_page_editor_data_to_test_page($data, $source->ID, $test_id);
            $content = $this->wrap_with_shell(
                $this->build_page_editor_test_core($slug, $data),
                $test_id
            );
            $updated = wp_update_post([
                'ID'            => $test_id,
                'post_status'   => 'publish',
                'post_title'    => $source->post_title . ' – konverteringstest',
                'post_name'     => $slug . '-editor-test',
                'post_content'  => $content,
                'post_excerpt'  => 'Sikker sammenligningskopi. Originalsiden og menuen ændres ikke.',
                'page_template' => 'default',
            ], true);
            if (is_wp_error($updated)) {
                throw new RuntimeException($updated->get_error_message());
            }

            update_post_meta($test_id, '_h18_conversion_test_source_id', (int) $source->ID);
            update_post_meta($test_id, '_h18_conversion_test_source_slug', $slug);
            update_post_meta($test_id, '_h18_conversion_test_updated_utc', gmdate('c'));
            update_post_meta($test_id, '_h18_conversion_test_content_hash', hash('sha256', wp_json_encode($data)));

            $this->log(
                'INFO',
                'PAGE_CONVERSION_TEST_READY',
                "Konverteringstest klar for {$slug}. OriginalID={$source->ID}; TestID={$test_id}; Sektioner=" . count($data['Sections']) . ". Originalsiden er uændret."
            );
            $this->set_notice(
                'success',
                'Konverteringstesten er klar. Åbn den med knappen “Åbn eksisterende test”. Originalsiden og menuen er uændret.'
            );
        } catch (Throwable $e) {
            $this->log('ERROR', 'PAGE_CONVERSION_TEST_FAILED', $e->getMessage());
            $this->set_notice('error', 'Konverteringstesten kunne ikke oprettes: ' . $e->getMessage());
        }

        $this->redirect_page_editor($slug);
    }

    public function handle_restore_page_before_editor() {
        $this->require_capability();
        $slug = sanitize_title($this->post_text('page_slug'));
        check_admin_referer('h18_restore_page_before_editor_' . $slug);

        $definitions = $this->editable_page_definitions();
        if (!isset($definitions[$slug])) {
            $this->set_notice('error', 'Den valgte side kan ikke gendannes her.');
            $this->redirect_page_editor(self::HOME_SLUG);
        }

        try {
            $page = $this->post_by_slug($slug);
            if (!$page instanceof WP_Post) {
                throw new RuntimeException('Siden blev ikke fundet.');
            }
            if (strpos((string) $page->post_content, self::PAGE_EDITOR_MARKER) === false) {
                throw new RuntimeException('Siden bruger ikke Hangar18 sideeditor og skal derfor ikke gendannes.');
            }

            $snapshot = $this->page_snapshot_before_editor($page);
            if (!is_array($snapshot)) {
                throw new RuntimeException('Der blev ikke fundet en WordPress-revision eller JSON-backup fra før sideeditoren.');
            }

            $this->create_full_managed_backup("Før gendannelse af {$slug} fra sideeditor");
            $this->backup_post($page->ID, "Konverteret {$slug} før gendannelse");

            $result = wp_update_post([
                'ID'            => $page->ID,
                'post_title'    => sanitize_text_field((string) $snapshot['post_title']),
                'post_excerpt'  => (string) $snapshot['post_excerpt'],
                'post_content'  => (string) $snapshot['post_content'],
                'page_template' => 'default',
            ], true);
            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $featured_id = absint($snapshot['featured_id'] ?? 0);
            if ($featured_id > 0 && get_post($featured_id) instanceof WP_Post) {
                set_post_thumbnail($page->ID, $featured_id);
            }

            $store = $this->get_page_editor_store();
            unset($store[$slug]);
            update_option(self::PAGE_EDITOR_OPTION, $store, false);
            $central_warning = '';
            try {
                $this->publish_configuration_file('Hangar18-Pages.json', [
                    'Version' => '1.22',
                    'Saved'   => gmdate('c'),
                    'Pages'   => $store,
                ]);
            } catch (Throwable $central_error) {
                $central_warning = $central_error->getMessage();
                $this->log('WARN', 'PAGE_EDITOR_RESTORE_CONFIG_WARNING', $central_warning);
            }

            $this->log(
                'INFO',
                'PAGE_EDITOR_RESTORE_SUCCESS',
                "{$slug} er gendannet fra {$snapshot['source']}. SideID={$page->ID}. Editorlageret for siden er ryddet."
            );
            if ($central_warning !== '') {
                $this->set_notice(
                    'warning',
                    $definitions[$slug] . ' er gendannet, men den centrale konfigurationskopi kunne ikke synkroniseres: ' . $central_warning
                );
            } else {
                $this->set_notice(
                    'success',
                    $definitions[$slug] . ' er gendannet til versionen fra før sideeditoren. Den konverterede version blev sikkerhedskopieret først.'
                );
            }
        } catch (Throwable $e) {
            $this->log('ERROR', 'PAGE_EDITOR_RESTORE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Siden kunne ikke gendannes: ' . $e->getMessage());
        }

        $this->redirect_page_editor($slug);
    }

    private function reset_poll_storage($page_id, $section_key) {
        $all = get_option(self::POLL_VOTES_OPTION, []);
        if (!is_array($all)) {
            $all = [];
        }
        unset($all[$this->page_module_storage_key($page_id, $section_key)]);
        update_option(self::POLL_VOTES_OPTION, $all, false);
    }

    public function handle_save_page_editor() {
        $this->require_capability();
        check_admin_referer('h18_save_page_editor');

        $slug = sanitize_title($this->post_text('page_slug'));
        $definitions = $this->editable_page_definitions();
        if (!isset($definitions[$slug])) {
            $this->set_notice('error', 'Den valgte side kan ikke redigeres i Hangar18 sideeditor.');
            $this->redirect_page_editor(self::HOME_SLUG);
        }
        $page = $this->post_by_slug($slug);
        if (!$page) {
            $this->set_notice('error', 'Siden blev ikke fundet.');
            $this->redirect_page_editor($slug);
        }

        $current = $this->get_page_editor_data($slug, $page);
        $change_note = sanitize_textarea_field((string) wp_unslash($_POST['page_change_note'] ?? ''));
        $current_content_version = $this->clamp_int($current['ContentVersion'] ?? 0, 0, 9999, 0);
        $next_content_version = min(9999, $current_content_version + 1);
        if ($next_content_version < 1) {
            $next_content_version = 1;
        }
        $legacy_by_key = [];
        $current_by_key = [];
        foreach ($current['Sections'] as $existing) {
            if (!empty($existing['Key'])) {
                $current_by_key[(string) $existing['Key']] = $existing;
            }
            if ($existing['Type'] === 'legacy') {
                $legacy_by_key[$existing['Key']] = $existing;
            }
        }

        $submitted = isset($_POST['sections']) && is_array($_POST['sections'])
            ? wp_unslash($_POST['sections'])
            : [];
        $sections = [];
        $reset_keys = [];
        foreach (array_slice($submitted, 0, 25) as $index => $raw) {
            if (!is_array($raw) || !empty($raw['Remove'])) {
                continue;
            }
            $raw['Active'] = !empty($raw['Active']);
            $raw['StoreSubmissions'] = !empty($raw['StoreSubmissions']);
            $raw['AllowMultiple'] = !empty($raw['AllowMultiple']);
            $raw['ShowDesktop'] = !empty($raw['ShowDesktop']);
            $raw['ShowTablet'] = !empty($raw['ShowTablet']);
            $raw['ShowMobile'] = !empty($raw['ShowMobile']);
            $raw['CarouselAutoplay'] = !empty($raw['CarouselAutoplay']);
            $raw['CarouselLoop'] = !empty($raw['CarouselLoop']);
            $raw['CarouselShowArrows'] = !empty($raw['CarouselShowArrows']);
            $raw['CarouselShowDots'] = !empty($raw['CarouselShowDots']);
            $raw['LayoutWrap'] = !empty($raw['LayoutWrap']);
            $raw['MobileLayoutStack'] = !empty($raw['MobileLayoutStack']);
            $raw['NavigatorLocked'] = !empty($raw['NavigatorLocked']);
            $key = sanitize_key((string) ($raw['Key'] ?? ''));
            $existing_section = isset($current_by_key[$key]) && is_array($current_by_key[$key]) ? $current_by_key[$key] : [];
            $submitted_type = sanitize_key((string) ($raw['Type'] ?? 'text'));
            if ($submitted_type === 'shortcode') {
                $can_author_advanced = current_user_can('unfiltered_html') || current_user_can('manage_options');
                $same_existing_shortcode = !empty($existing_section) &&
                    ($existing_section['Type'] ?? '') === 'shortcode' &&
                    !empty($existing_section['AdvancedContentAuthorized']) &&
                    (string) ($existing_section['Content'] ?? '') === sanitize_textarea_field((string) ($raw['Content'] ?? ''));
                $raw['AdvancedContentAuthorized'] = $can_author_advanced || $same_existing_shortcode;
            } else {
                $raw['AdvancedContentAuthorized'] = false;
            }
            $legacy = isset($legacy_by_key[$key]) ? $legacy_by_key[$key] : [];
            $section = $this->normalize_page_section($raw, $index, $legacy);
            $sections[] = $section;
            if ($section['Type'] === 'poll' && !empty($raw['ResetVotes'])) {
                $reset_keys[] = $section['Key'];
            }
        }

        $data = $this->normalize_page_editor_data([
            'Version'        => '1.22',
            'PageSlug'       => $slug,
            'PageTitle'          => $this->post_text('editor_page_title'),
            'ContentVersion'     => $next_content_version,
            'DataContextType'    => sanitize_key((string) wp_unslash($_POST['data_context_type'] ?? '')),
            'DataContextEntryId' => absint($_POST['data_context_entry_id'] ?? 0),
            'Sections'           => $sections,
        ], $page);

        if (!empty($_POST['whatif'])) {
            $active = count(array_filter($data['Sections'], static function($section) { return !empty($section['Active']); }));
            $this->log('WARN', 'WHATIF_PAGE_EDITOR_SAVE', "[WHATIF] {$slug} ville blive v{$next_content_version} med {$active} aktive sektioner.");
            $this->set_notice('warning', "WHATIF: Siden ville blive v{$next_content_version} med {$active} aktive sektioner. Ingen version, backup, stemmer eller data blev oprettet eller ændret.");
            $this->redirect_page_editor($slug);
        }

        if (trim($change_note) === '') {
            $this->set_notice('error', 'Skriv kort, hvad du har ændret, før siden gemmes som en ny version.');
            $this->redirect_page_editor($slug);
        }

        try {
            $full_backup = $this->create_full_managed_backup(
                "Før sideeditor gemte {$slug} som v{$next_content_version}. Ændring: {$change_note}"
            );
            foreach ($reset_keys as $reset_key) {
                $this->reset_poll_storage($page->ID, $reset_key);
            }

            $this->save_page_editor_data($slug, $data);
            $store = $this->get_page_editor_store();
            $published = [
                'Version' => '1.22',
                'Saved'   => gmdate('c'),
                'Pages'   => $store,
            ];
            $this->publish_configuration_file('Hangar18-Pages.json', $published);

            $result = wp_update_post([
                'ID'            => $page->ID,
                'post_title'    => $data['PageTitle'],
                'page_template' => 'default',
                'post_content'  => $this->wrap_with_shell($this->build_page_editor_core($slug, $data), $page->ID),
            ], true);
            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $active = count(array_filter($data['Sections'], static function($section) { return !empty($section['Active']); }));
            $snapshot_file = '';
            $snapshot_warning = '';
            try {
                $snapshot_path = $this->backup_post(
                    $page->ID,
                    "Sideeditor {$slug} v{$next_content_version}. Ændring: {$change_note}"
                );
                $snapshot_file = $snapshot_path ? basename($snapshot_path) : '';
            } catch (Throwable $snapshot_error) {
                $snapshot_warning = $snapshot_error->getMessage();
                $this->log('WARN', 'PAGE_VERSION_SNAPSHOT_WARNING', $snapshot_warning);
            }

            $user = wp_get_current_user();
            $user_display = trim((string) $user->display_name);
            if ($user_display === '') {
                $user_display = (string) $user->user_login;
            }
            $this->append_page_version_history($slug, [
                'Version'        => $next_content_version,
                'SavedUtc'       => gmdate('c'),
                'UserId'         => (int) $user->ID,
                'UserDisplay'    => $user_display !== '' ? $user_display : 'Ukendt bruger',
                'ChangeNote'     => $change_note,
                'FullBackupFile' => basename($full_backup),
                'SnapshotFile'   => $snapshot_file,
                'ContentHash'    => hash('sha256', wp_json_encode($data)),
                'ActiveSections' => $active,
            ]);

            $this->log(
                'INFO',
                'PAGE_EDITOR_SAVE_SUCCESS',
                "Sideeditor gemte {$slug} som v{$next_content_version}. Ændring={$change_note}; AktiveSektioner={$active}; NulstilledeAfstemninger=" . count($reset_keys) . '.'
            );
            if ($snapshot_warning !== '') {
                $this->set_notice('warning', "Siden er gemt som v{$next_content_version}, og den fulde før-backup er oprettet. Sidekopien efter gemning fejlede: {$snapshot_warning}");
            } else {
                $this->set_notice('success', "Siden er gemt som v{$next_content_version} med {$active} aktive sektioner. Ændringsbeskrivelse, fuld backup, sidekopi og WordPress-revision er oprettet.");
            }
        } catch (Throwable $e) {
            $this->log('ERROR', 'PAGE_EDITOR_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Siden kunne ikke gemmes: ' . $e->getMessage());
        }
        $this->redirect_page_editor($slug);
    }

    private function public_module_redirect($page, $section_key, $parameter, $status) {
        $url = add_query_arg([
            sanitize_key($parameter) => sanitize_key($status),
            'h18_module'              => sanitize_key((string) $section_key),
        ], get_permalink($page));
        $url .= '#h18-section-' . sanitize_html_class((string) $section_key);
        wp_safe_redirect($url);
        exit;
    }

    private function request_fingerprint() {
        $ip = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash($_SERVER['REMOTE_ADDR'])) : '';
        $agent = isset($_SERVER['HTTP_USER_AGENT']) ? sanitize_text_field(wp_unslash($_SERVER['HTTP_USER_AGENT'])) : '';
        return hash_hmac('sha256', $ip . '|' . $agent, wp_salt('nonce'));
    }

    public function handle_send_page_form() {
        $page_id = absint($_POST['page_id'] ?? 0);
        $section_key = sanitize_key((string) wp_unslash($_POST['section_key'] ?? ''));
        [$page, $section] = $this->find_page_module($page_id, $section_key, 'mail_form');
        if (!$page || !$section) {
            wp_die('Mailformularen findes ikke længere.', 'Hangar18', ['response' => 404]);
        }

        $nonce = isset($_POST['h18_form_nonce']) ? sanitize_text_field(wp_unslash($_POST['h18_form_nonce'])) : '';
        if (!wp_verify_nonce($nonce, 'h18_send_page_form_' . $page_id . '_' . $section_key)) {
            $this->public_module_redirect($page, $section_key, 'h18_form', 'error');
        }
        if (!empty($_POST['website'])) {
            $this->public_module_redirect($page, $section_key, 'h18_form', 'success');
        }
        $started = absint($_POST['started'] ?? 0);
        if ($started <= 0 || time() - $started < 2 || time() - $started > 7200) {
            $this->public_module_redirect($page, $section_key, 'h18_form', 'error');
        }

        $fingerprint = $this->request_fingerprint();
        $rate_key = 'h18_form_rate_' . substr(hash('sha256', $page_id . '|' . $section_key . '|' . $fingerprint), 0, 32);
        if (get_transient($rate_key)) {
            $this->public_module_redirect($page, $section_key, 'h18_form', 'error');
        }

        $name = sanitize_text_field((string) wp_unslash($_POST['sender_name'] ?? ''));
        $email = sanitize_email((string) wp_unslash($_POST['sender_email'] ?? ''));
        $subject = sanitize_text_field((string) wp_unslash($_POST['sender_subject'] ?? ''));
        $message = sanitize_textarea_field((string) wp_unslash($_POST['sender_message'] ?? ''));
        if ($name === '' || !is_email($email) || $subject === '' || $message === '') {
            $this->public_module_redirect($page, $section_key, 'h18_form', 'error');
        }
        if ($section['ConsentLabel'] !== '' && empty($_POST['consent'])) {
            $this->public_module_redirect($page, $section_key, 'h18_form', 'error');
        }

        $recipient = is_email($section['RecipientEmail']) ? $section['RecipientEmail'] : sanitize_email((string) get_option('admin_email'));
        $mail_subject = '[' . wp_specialchars_decode(get_bloginfo('name'), ENT_QUOTES) . '] ' . $subject;
        $mail_body = "Ny henvendelse fra hjemmesiden\n\nNavn: {$name}\nE-mail: {$email}\nSide: " . get_permalink($page) . "\n\nEmne: {$subject}\n\nBesked:\n{$message}\n";
        $headers = ['Reply-To: ' . $name . ' <' . $email . '>'];
        set_transient($rate_key, 1, MINUTE_IN_SECONDS);
        $sent = wp_mail($recipient, $mail_subject, $mail_body, $headers);
        if (!$sent) {
            $this->log('ERROR', 'PAGE_FORM_MAIL_FAILED', "Mailformular kunne ikke sende fra side ID {$page_id}, sektion {$section_key}.");
            $this->public_module_redirect($page, $section_key, 'h18_form', 'error');
        }

        if (!empty($section['StoreSubmissions'])) {
            $all = get_option(self::FORM_SUBMISSIONS_OPTION, []);
            if (!is_array($all)) {
                $all = [];
            }
            $storage_key = $this->page_module_storage_key($page_id, $section_key);
            $items = isset($all[$storage_key]) && is_array($all[$storage_key]) ? $all[$storage_key] : [];
            $items[] = ['ReceivedUtc' => gmdate('c'), 'Name' => $name, 'Email' => $email, 'Subject' => $subject, 'Message' => $message];
            $all[$storage_key] = array_slice($items, -200);
            update_option(self::FORM_SUBMISSIONS_OPTION, $all, false);
        }

        $this->log('INFO', 'PAGE_FORM_MAIL_SENT', "Mailformular sendte fra side ID {$page_id}, sektion {$section_key}.");
        $this->public_module_redirect($page, $section_key, 'h18_form', 'success');
    }

    public function handle_submit_poll() {
        $page_id = absint($_POST['page_id'] ?? 0);
        $section_key = sanitize_key((string) wp_unslash($_POST['section_key'] ?? ''));
        [$page, $section] = $this->find_page_module($page_id, $section_key, 'poll');
        if (!$page || !$section) {
            wp_die('Afstemningen findes ikke længere.', 'Hangar18', ['response' => 404]);
        }
        $nonce = isset($_POST['h18_poll_nonce']) ? sanitize_text_field(wp_unslash($_POST['h18_poll_nonce'])) : '';
        if (!wp_verify_nonce($nonce, 'h18_submit_poll_' . $page_id . '_' . $section_key) || $this->is_poll_closed($section)) {
            $this->public_module_redirect($page, $section_key, 'h18_poll', 'error');
        }
        $started = absint($_POST['started'] ?? 0);
        if (!empty($_POST['website']) || $started <= 0 || time() - $started < 1 || time() - $started > 7200) {
            $this->public_module_redirect($page, $section_key, 'h18_poll', 'error');
        }

        $answers = isset($_POST['answers']) && is_array($_POST['answers']) ? array_map('sanitize_key', wp_unslash($_POST['answers'])) : [];
        $answers = array_values(array_unique($answers));
        $allowed = [];
        foreach ($section['PollOptions'] as $option) {
            $allowed[$this->poll_option_id($option)] = $option;
        }
        $answers = array_values(array_filter($answers, static function($answer) use ($allowed) { return isset($allowed[$answer]); }));
        if (!$answers || (empty($section['AllowMultiple']) && count($answers) !== 1)) {
            $this->public_module_redirect($page, $section_key, 'h18_poll', 'error');
        }

        $storage_key = $this->page_module_storage_key($page_id, $section_key);
        $state = $this->get_poll_state($storage_key, $section['PollOptions']);
        $fingerprint = $this->request_fingerprint();
        $cookie_name = 'h18_poll_' . $storage_key;
        if (isset($state['Voters'][$fingerprint]) || !empty($_COOKIE[$cookie_name])) {
            $this->public_module_redirect($page, $section_key, 'h18_poll', 'duplicate');
        }
        foreach ($answers as $answer) {
            $state['Counts'][$answer] = (int) ($state['Counts'][$answer] ?? 0) + 1;
        }
        $state['Voters'][$fingerprint] = gmdate('c');
        if (count($state['Voters']) > 5000) {
            $state['Voters'] = array_slice($state['Voters'], -5000, null, true);
        }
        $state['UpdatedUtc'] = gmdate('c');
        $all = get_option(self::POLL_VOTES_OPTION, []);
        if (!is_array($all)) {
            $all = [];
        }
        $all[$storage_key] = $state;
        update_option(self::POLL_VOTES_OPTION, $all, false);
        setcookie($cookie_name, '1', ['expires' => time() + YEAR_IN_SECONDS, 'path' => COOKIEPATH ?: '/', 'secure' => is_ssl(), 'httponly' => true, 'samesite' => 'Lax']);
        $this->public_module_redirect($page, $section_key, 'h18_poll', 'success');
    }

    private function csv_safe_cell($value) {
        $value = (string) $value;
        return preg_match('/^\s*[=+\-@]/', $value) ? "'" . $value : $value;
    }

    private function start_csv_download($filename) {
        nocache_headers();
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="' . sanitize_file_name($filename) . '"');
        echo "\xEF\xBB\xBF";
        return fopen('php://output', 'w');
    }

    public function handle_test_page_form() {
        $this->require_capability();
        $page_id = absint($_GET['page_id'] ?? 0);
        $section_key = sanitize_key((string) wp_unslash($_GET['section_key'] ?? ''));
        check_admin_referer('h18_test_page_form_' . $page_id . '_' . $section_key);
        [$page, $section] = $this->find_page_module($page_id, $section_key, 'mail_form', false);
        if (!$page || !$section) {
            wp_die('Mailformularen blev ikke fundet.');
        }
        $recipient = is_email($section['RecipientEmail']) ? $section['RecipientEmail'] : sanitize_email((string) get_option('admin_email'));
        $subject = '[Hangar18] Test af mailformular';
        $message = "Dette er en test fra Hangar18 sideeditor.\n\nSide: " . get_permalink($page) . "\nSektion: {$section_key}\nTid UTC: " . gmdate('c');
        if (wp_mail($recipient, $subject, $message)) {
            $this->log('INFO', 'PAGE_FORM_TEST_SENT', "Testmail sendt til {$recipient} fra side ID {$page_id}.");
            $this->set_notice('success', "Testmailen er afleveret til WordPress' mailsystem for {$recipient}.");
        } else {
            $this->log('ERROR', 'PAGE_FORM_TEST_FAILED', "Testmail kunne ikke sendes til {$recipient} fra side ID {$page_id}.");
            $this->set_notice('error', 'Testmailen kunne ikke afleveres. Kontrollér SMTP/mailopsætningen på WordPress-serveren.');
        }
        $this->redirect_page_editor($page->post_name);
    }

    public function handle_export_poll() {
        $this->require_capability();
        $page_id = absint($_GET['page_id'] ?? 0);
        $section_key = sanitize_key((string) wp_unslash($_GET['section_key'] ?? ''));
        check_admin_referer('h18_export_poll_' . $page_id . '_' . $section_key);
        [$page, $section] = $this->find_page_module($page_id, $section_key, 'poll', false);
        if (!$page || !$section) {
            wp_die('Afstemningen blev ikke fundet.');
        }
        $state = $this->get_poll_state($this->page_module_storage_key($page_id, $section_key), $section['PollOptions']);
        $total = 0;
        foreach ($section['PollOptions'] as $option) {
            $total += (int) ($state['Counts'][$this->poll_option_id($option)] ?? 0);
        }
        $out = $this->start_csv_download('Hangar18-Afstemning-' . $page->post_name . '-' . gmdate('Ymd-His') . '.csv');
        fputcsv($out, ['Spørgsmål', $this->csv_safe_cell($section['Title'])], ';');
        fputcsv($out, ['Eksporteret UTC', gmdate('c')], ';');
        fputcsv($out, ['Svar', 'Stemmer', 'Procent'], ';');
        foreach ($section['PollOptions'] as $option) {
            $count = (int) ($state['Counts'][$this->poll_option_id($option)] ?? 0);
            $percent = $total > 0 ? round(($count / $total) * 100, 1) : 0;
            fputcsv($out, [$this->csv_safe_cell($option), $count, $percent], ';');
        }
        fclose($out);
        exit;
    }

    public function handle_export_form_submissions() {
        $this->require_capability();
        $page_id = absint($_GET['page_id'] ?? 0);
        $section_key = sanitize_key((string) wp_unslash($_GET['section_key'] ?? ''));
        check_admin_referer('h18_export_form_submissions_' . $page_id . '_' . $section_key);
        [$page, $section] = $this->find_page_module($page_id, $section_key, 'mail_form', false);
        if (!$page || !$section) {
            wp_die('Mailformularen blev ikke fundet.');
        }
        $all = get_option(self::FORM_SUBMISSIONS_OPTION, []);
        $storage_key = $this->page_module_storage_key($page_id, $section_key);
        $items = is_array($all) && isset($all[$storage_key]) && is_array($all[$storage_key]) ? $all[$storage_key] : [];
        $out = $this->start_csv_download('Hangar18-Henvendelser-' . $page->post_name . '-' . gmdate('Ymd-His') . '.csv');
        fputcsv($out, ['Modtaget UTC', 'Navn', 'E-mail', 'Emne', 'Besked'], ';');
        foreach ($items as $item) {
            fputcsv($out, [
                $this->csv_safe_cell($item['ReceivedUtc'] ?? ''),
                $this->csv_safe_cell($item['Name'] ?? ''),
                $this->csv_safe_cell($item['Email'] ?? ''),
                $this->csv_safe_cell($item['Subject'] ?? ''),
                $this->csv_safe_cell($item['Message'] ?? ''),
            ], ';');
        }
        fclose($out);
        exit;
    }

    /* ================================================================
       STATIC PAGE CONTENT (legacy compatibility)
       ================================================================ */

    private function build_static_content_core($page_id, array $settings) {
        $settings = $this->normalize_static_content_settings($settings);
        $id = (int) $page_id;
        $heading = esc_html((string) $settings['Heading']);
        $intro = wpautop(esc_html((string) $settings['Intro']));
        $cards = '';

        foreach ($settings['Sections'] as $section) {
            if (empty($section['Active'])) {
                continue;
            }

            $title = esc_html((string) $section['Title']);
            $body = wpautop(esc_html((string) $section['Body']));
            $key = esc_attr((string) $section['Key']);

            $cards .= '<section class="h18-content-card" data-section="' . $key . '">' .
                '<h2>' . $title . '</h2>' . $body . '</section>';
        }

        $marker = $this->encode_marker(self::STATIC_CONTENT_MARKER, $settings);
        $top = (int) $settings['CardsTopSpacingPx'];
        $gap = (int) $settings['CardGapPx'];
        $mobile_top = (int) $settings['MobileCardsTopSpacingPx'];
        $mobile_gap = (int) $settings['MobileCardGapPx'];
        $padding = (int) $settings['CardPaddingPx'];
        $mobile_padding = (int) $settings['MobileCardPaddingPx'];
        $radius = (int) $settings['CardRadiusPx'];

        return <<<HTML
{$marker}
<!-- wp:html -->
<style>
body.page-id-{$id} .h18-static-content{width:100%;box-sizing:border-box}
body.page-id-{$id} .h18-static-intro h1{margin:0 0 10px;color:#30382a;font-size:clamp(2rem,4vw,3.2rem);line-height:1.08}
body.page-id-{$id} .h18-static-intro p{margin:0 0 8px}
body.page-id-{$id} .h18-content-section-list{display:grid;grid-template-columns:minmax(0,1fr);gap:{$gap}px;margin-top:{$top}px}
body.page-id-{$id} .h18-content-card{box-sizing:border-box;margin:0;padding:{$padding}px;background:#f2f0e8;border-top:4px solid #c3ae83;border-radius:{$radius}px}
body.page-id-{$id} .h18-content-card h2{margin:0 0 8px;color:#30382a}
body.page-id-{$id} .h18-content-card p{margin:0}
body.page-id-{$id} .h18-content-card p+p{margin-top:8px}
@media(max-width:782px){body.page-id-{$id} .h18-content-section-list{gap:{$mobile_gap}px;margin-top:{$mobile_top}px}body.page-id-{$id} .h18-content-card{padding:{$mobile_padding}px}}
</style>
<!-- /wp:html -->
<div class="h18-static-content">
<div class="h18-static-intro"><h1>{$heading}</h1>{$intro}</div>
<div class="h18-content-section-list">{$cards}</div>
</div>
HTML;
    }

    public function render_static_content() {
        $this->require_capability();
        $settings = $this->get_static_content_settings();
        $page = $this->post_by_slug('om-foreningen');
        ?>
        <div class="wrap h18-admin">
            <h1>Sideindhold</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Indholdssektioner på Om foreningen:</strong>
                Hver kasse er en sektion. Slå <strong>Vis på siden</strong> fra for at skjule den uden at slette teksten,
                træk sektionerne for at ændre rækkefølgen, eller tilføj en ny sektion nederst.
                <strong>Fjern permanent</strong> bruges kun, når sektionen ikke længere skal kunne genaktiveres.
            </div>

            <div class="h18-toolbar">
                <div><strong>Styret side:</strong> Om foreningen</div>
                <p class="h18-toolbar-note">Version 0.4.17 starter med denne side. Samme model kan senere udvides til Hjem, Bliv medlem og Kontakt.</p>
                <?php if ($page) : ?><a class="button" target="_blank" rel="noopener" href="<?php echo esc_url(get_permalink($page)); ?>">Åbn siden</a><?php endif; ?>
            </div>

            <?php if (!$page) : ?>
                <div class="notice notice-error"><p>Siden <strong>Om foreningen</strong> blev ikke fundet.</p></div>
            <?php else : ?>
            <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_static_content'); ?>
                <input type="hidden" name="action" value="h18_save_static_content" />

                <div class="h18-form-header">
                    <div>
                        <h2>Introduktion og indholdskasser</h2>
                        <p>Ændringerne gælder kun siden Om foreningen.</p>
                    </div>
                    <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                </div>

                <div class="h18-form-grid">
                    <section class="h18-panel h18-panel-wide">
                        <h3>Introduktion over kasserne</h3>
                        <?php $this->field('static_heading', 'Overskrift', $settings['Heading'], 'text', true); ?>
                        <?php $this->textarea('static_intro', 'Introduktion', $settings['Intro'], 5); ?>
                    </section>

                    <section class="h18-panel h18-panel-wide">
                        <div class="h18-panel-heading-row">
                            <h3>Indholdssektioner – træk for at ændre rækkefølge</h3>
                            <span><?php echo esc_html(count($settings['Sections'])); ?> sektioner</span>
                        </div>
                        <div id="h18-static-sections-sortable" class="h18-static-sections-sortable">
                            <?php foreach ($settings['Sections'] as $index => $section) : ?>
                                <div class="h18-static-section-row">
                                    <span class="dashicons dashicons-move h18-static-section-drag" title="Flyt sektion"></span>
                                    <input class="h18-static-section-order" type="hidden" name="sections[<?php echo esc_attr($index); ?>][Order]" value="<?php echo esc_attr($section['Order']); ?>" />
                                    <input type="hidden" name="sections[<?php echo esc_attr($index); ?>][Key]" value="<?php echo esc_attr($section['Key']); ?>" />
                                    <div class="h18-field">
                                        <label><strong>Overskrift</strong></label>
                                        <input type="text" name="sections[<?php echo esc_attr($index); ?>][Title]" value="<?php echo esc_attr($section['Title']); ?>" required />
                                    </div>
                                    <div class="h18-field h18-static-section-body">
                                        <label><strong>Tekst</strong></label>
                                        <textarea name="sections[<?php echo esc_attr($index); ?>][Body]" rows="3"><?php echo esc_textarea($section['Body']); ?></textarea>
                                    </div>
                                    <div class="h18-static-section-controls">
                                        <label><input type="checkbox" name="sections[<?php echo esc_attr($index); ?>][Active]" value="1" <?php checked(!empty($section['Active'])); ?> /> Vis på siden</label>
                                        <label class="h18-remove-choice"><input type="checkbox" name="sections[<?php echo esc_attr($index); ?>][Remove]" value="1" /> Fjern permanent</label>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </section>

                    <section class="h18-panel h18-panel-wide">
                        <h3>Tilføj ny sektion</h3>
                        <div class="h18-static-new-section">
                            <div class="h18-field"><label><strong>Overskrift</strong></label><input type="text" name="new_section[Title]" value="" placeholder="Fx Aktiviteter" /></div>
                            <div class="h18-field"><label><strong>Tekst</strong></label><textarea name="new_section[Body]" rows="3" placeholder="Skriv teksten til den nye indholdskasse"></textarea></div>
                            <label><input type="checkbox" name="new_section[Active]" value="1" checked /> Vis på siden med det samme</label>
                        </div>
                    </section>
                </div>

                <section class="h18-layout-card h18-static-spacing-card">
                    <div class="h18-layout-card-header">
                        <h2>Luft og udseende</h2>
                        <p>Disse værdier styrer kun indholdskasserne på Om foreningen.</p>
                    </div>
                    <div class="h18-layout-devices">
                        <fieldset class="h18-layout-device">
                            <legend>Desktop</legend>
                            <div class="h18-layout-fields">
                                <?php $this->field('cards_top_spacing_px', 'Luft før første kasse (px)', $settings['CardsTopSpacingPx'], 'number'); ?>
                                <?php $this->field('card_gap_px', 'Luft mellem kasser (px)', $settings['CardGapPx'], 'number'); ?>
                                <?php $this->field('card_padding_px', 'Luft inde i kasser (px)', $settings['CardPaddingPx'], 'number'); ?>
                                <?php $this->field('card_radius_px', 'Hjørneafrunding (px)', $settings['CardRadiusPx'], 'number'); ?>
                            </div>
                        </fieldset>
                        <fieldset class="h18-layout-device">
                            <legend>Mobil</legend>
                            <div class="h18-layout-fields">
                                <?php $this->field('mobile_cards_top_spacing_px', 'Luft før første kasse (px)', $settings['MobileCardsTopSpacingPx'], 'number'); ?>
                                <?php $this->field('mobile_card_gap_px', 'Luft mellem kasser (px)', $settings['MobileCardGapPx'], 'number'); ?>
                                <?php $this->field('mobile_card_padding_px', 'Luft inde i kasser (px)', $settings['MobileCardPaddingPx'], 'number'); ?>
                                <div class="h18-runtime-note"><strong>Hjørneafrunding</strong><br>Samme værdi som desktop bruges på mobil.</div>
                            </div>
                        </fieldset>
                    </div>
                </section>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Er simulering markeret, ændres hverken indhold, rækkefølge eller luft.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary button-hero" type="submit">Gem sideindhold og opdater siden</button>
                        <div class="h18-action-copy"><strong>Gemmer hele opsætningen</strong><span>Tager backup og opdaterer introduktion, synlige sektioner, rækkefølge og afstande.</span></div>
                    </div>
                </div>
            </form>
            <?php endif; ?>
        </div>
        <?php
    }

    public function handle_save_static_content() {
        $this->require_capability();
        check_admin_referer('h18_save_static_content');

        $submitted = isset($_POST['sections']) && is_array($_POST['sections'])
            ? wp_unslash($_POST['sections'])
            : [];
        $sections = [];

        foreach ($submitted as $row) {
            if (!is_array($row) || !empty($row['Remove'])) {
                continue;
            }
            $sections[] = [
                'Key'    => sanitize_key((string) ($row['Key'] ?? '')),
                'Title'  => sanitize_text_field((string) ($row['Title'] ?? '')),
                'Body'   => sanitize_textarea_field((string) ($row['Body'] ?? '')),
                'Active' => !empty($row['Active']),
                'Order'  => $row['Order'] ?? 10,
            ];
        }

        $new = isset($_POST['new_section']) && is_array($_POST['new_section'])
            ? wp_unslash($_POST['new_section'])
            : [];
        $new_title = sanitize_text_field((string) ($new['Title'] ?? ''));
        $new_body = sanitize_textarea_field((string) ($new['Body'] ?? ''));
        if ($new_title !== '' || $new_body !== '') {
            $sections[] = [
                'Key'    => sanitize_key(sanitize_title($new_title)),
                'Title'  => $new_title,
                'Body'   => $new_body,
                'Active' => !empty($new['Active']),
                'Order'  => (count($sections) + 1) * 10,
            ];
        }

        $settings = $this->normalize_static_content_settings([
            'Version'                 => '1.0',
            'PageSlug'                => 'om-foreningen',
            'Heading'                 => $this->post_text('static_heading'),
            'Intro'                   => $this->post_textarea('static_intro'),
            'CardsTopSpacingPx'       => $_POST['cards_top_spacing_px'] ?? 24,
            'CardGapPx'               => $_POST['card_gap_px'] ?? 20,
            'MobileCardsTopSpacingPx' => $_POST['mobile_cards_top_spacing_px'] ?? 18,
            'MobileCardGapPx'         => $_POST['mobile_card_gap_px'] ?? 14,
            'CardPaddingPx'           => $_POST['card_padding_px'] ?? 26,
            'MobileCardPaddingPx'     => $_POST['mobile_card_padding_px'] ?? 20,
            'CardRadiusPx'            => $_POST['card_radius_px'] ?? 7,
            'Sections'                => $sections,
        ]);

        if (!empty($_POST['whatif'])) {
            $active = count(array_filter($settings['Sections'], static function($section) {
                return !empty($section['Active']);
            }));
            $this->log('WARN', 'WHATIF_STATIC_CONTENT', "[WHATIF] Om foreningen ville få {$active} synlige indholdssektioner.");
            $this->set_notice('warning', "WHATIF: Om foreningen ville få {$active} synlige indholdssektioner. Ingen data blev ændret.");
            $this->redirect('hangar18-static-content');
        }

        try {
            $page = $this->post_by_slug('om-foreningen');
            if (!$page) {
                throw new RuntimeException("Siden 'Om foreningen' blev ikke fundet.");
            }

            $this->create_full_managed_backup('Før ændring af indholdssektioner på Om foreningen');
            update_option(self::STATIC_CONTENT_OPTION, $settings, false);

            $central = $settings;
            $central['Saved'] = gmdate('c');
            $this->publish_configuration_file('Hangar18-StaticContent.json', $central);

            $result = wp_update_post([
                'ID'            => $page->ID,
                'page_template' => 'default',
                'post_content'  => $this->wrap_with_shell(
                    $this->build_static_content_core($page->ID, $settings),
                    $page->ID
                ),
            ], true);

            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $active = count(array_filter($settings['Sections'], static function($section) {
                return !empty($section['Active']);
            }));
            $this->log('INFO', 'STATIC_CONTENT_SAVED', "Om foreningen opdateret med {$active} synlige indholdssektioner.");
            $this->set_notice('success', "Sideindholdet er gemt. Om foreningen viser nu {$active} aktive sektioner.");
        } catch (Throwable $e) {
            $this->log('ERROR', 'STATIC_CONTENT_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Sideindholdet kunne ikke gemmes: ' . $e->getMessage());
        }

        $this->redirect('hangar18-static-content');
    }


    /* ================================================================
       MENU
       ================================================================ */

    private function get_active_menu_id() {
        $saved = absint(get_option(self::ACTIVE_MENU_OPTION, 0));

        if ($saved && wp_get_nav_menu_object($saved)) {
            return $saved;
        }

        $menus = wp_get_nav_menus();

        if ($menus) {
            return (int) $menus[0]->term_id;
        }

        return 0;
    }

    private function get_selected_menu_id() {
        $requested = isset($_GET['menu_id']) ? absint($_GET['menu_id']) : 0;

        if ($requested && wp_get_nav_menu_object($requested)) {
            return $requested;
        }

        return $this->get_active_menu_id();
    }

    private function get_menu_items($menu_id) {
        if (!$menu_id) {
            return [];
        }

        $items = wp_get_nav_menu_items($menu_id, [
            'post_status' => 'publish',
        ]);

        if (!is_array($items)) {
            return [];
        }

        usort($items, static function($a, $b) {
            $order_compare = ((int) $a->menu_order) <=> ((int) $b->menu_order);
            if ($order_compare !== 0) {
                return $order_compare;
            }
            return ((int) $a->ID) <=> ((int) $b->ID);
        });

        return $items;
    }

    private function get_default_menu_page_definitions() {
        $config = $this->get_menu_order_settings();

        $fallback_titles = [
            'hjem'                    => 'Hjem',
            'om-foreningen'           => 'Om foreningen',
            'koeretoejer-og-materiel' => 'Køretøjer og materiel',
            'events'                  => 'Events',
            'billedgalleri'           => 'Billedgalleri',
            'bliv-medlem'             => 'Bliv medlem',
            'kontakt'                 => 'Kontakt',
        ];

        $definitions = [];
        $order = 1;

        foreach ((array) ($config['Order'] ?? []) as $slug_value) {
            $slug = sanitize_title((string) $slug_value);

            if ($slug === '') {
                continue;
            }

            $page = $this->post_by_slug($slug);
            $title = $page
                ? (string) $page->post_title
                : (string) ($fallback_titles[$slug] ?? $slug);

            $definitions[] = [
                'title' => $title,
                'slug'  => $slug,
                'order' => $order++,
            ];
        }

        return $definitions;
    }

    private function menu_order_config_from_nav_menu($menu_id) {
        $order = [];

        foreach ($this->get_menu_items($menu_id) as $menu_item) {
            if ($menu_item->type !== 'post_type' || $menu_item->object !== 'page') {
                continue;
            }

            $page = get_post((int) $menu_item->object_id);

            if (!$page || $page->post_type !== 'page') {
                continue;
            }

            $slug = sanitize_title((string) $page->post_name);

            if ($slug !== '' && !in_array($slug, $order, true)) {
                $order[] = $slug;
            }
        }

        return [
            'Version' => '1.0',
            'Saved'   => gmdate('c'),
            'Order'   => $order,
        ];
    }

    private function sync_menu_order_configuration_from_nav_menu($menu_id) {
        $config = $this->menu_order_config_from_nav_menu($menu_id);

        update_option(
            self::MENU_ORDER_OPTION,
            $this->normalize_menu_order_settings($config),
            false
        );

        $this->publish_configuration_file(
            'Hangar18-MenuOrder.json',
            $config
        );

        $this->log(
            'INFO',
            'MENU_ORDER_CONFIG_SYNCED',
            "Hangar18-MenuOrder.json schema 1.0 opdateret fra WordPress Menu ID {$menu_id}. " .
            'PageItems=' . count($config['Order']) . '.'
        );
    }

    private function get_menu_page_candidates() {
        $pages = get_posts([
            'post_type'        => 'page',
            'post_status'      => 'publish',
            'posts_per_page'   => -1,
            'orderby'          => 'title',
            'order'            => 'ASC',
            'suppress_filters' => false,
        ]);

        return array_values(array_filter($pages, static function($page) {
            return $page->post_name !== 'hangar18-configuration-store' &&
                !get_post_meta($page->ID, '_h18_conversion_test_source_id', true);
        }));
    }

    private function get_menu_analysis($menu_id) {
        $items = $this->get_menu_items($menu_id);

        $home = $this->post_by_slug(self::HOME_SLUG);
        $home_found = false;
        $duplicate_ids = [];
        $seen_page_objects = [];

        foreach ($items as $item) {
            if ($item->type !== 'post_type' || $item->object !== 'page') {
                continue;
            }

            $object_id = (int) $item->object_id;

            if ($home && $object_id === (int) $home->ID) {
                $home_found = true;
            }

            if (isset($seen_page_objects[$object_id])) {
                $duplicate_ids[] = (int) $item->ID;
            } else {
                $seen_page_objects[$object_id] = (int) $item->ID;
            }
        }

        return [
            'items'          => $items,
            'home_found'     => $home_found,
            'duplicate_ids'  => $duplicate_ids,
            'duplicate_count'=> count($duplicate_ids),
        ];
    }

    private function backup_menu($menu_id, $reason) {
        $menu = wp_get_nav_menu_object($menu_id);

        if (!$menu) {
            return null;
        }

        $items = [];
        foreach ($this->get_menu_items($menu_id) as $item) {
            $items[] = [
                'ID'               => (int) $item->ID,
                'title'            => $item->title,
                'menu_order'       => (int) $item->menu_order,
                'menu_item_parent' => (int) $item->menu_item_parent,
                'type'             => $item->type,
                'object'           => $item->object,
                'object_id'        => (int) $item->object_id,
                'url'              => $item->url,
                'target'           => $item->target,
                'attr_title'       => $item->attr_title,
                'description'      => $item->description,
                'classes'          => array_values(array_filter((array) $item->classes)),
                'xfn'              => $item->xfn,
            ];
        }

        $payload = [
            'created_utc'    => gmdate('c'),
            'reason'         => (string) $reason,
            'plugin_version' => self::VERSION,
            'menu' => [
                'term_id' => (int) $menu->term_id,
                'name'    => $menu->name,
                'slug'    => $menu->slug,
            ],
            'theme_locations' => get_theme_mod('nav_menu_locations', []),
            'active_hangar18_menu_id' => $this->get_active_menu_id(),
            'items' => $items,
        ];

        $file = trailingslashit($this->backup_dir()) .
            sprintf(
                'Hangar18-Web-Menu-Backup-%s-Menu-%d.json',
                gmdate('Ymd-His'),
                (int) $menu->term_id
            );

        if (file_put_contents(
            $file,
            wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
        ) === false) {
            throw new RuntimeException('Kunne ikke skrive menu-backup.');
        }

        $this->log(
            'INFO',
            'MENU_BACKUP_SUCCESS',
            'Menu-backup oprettet: ' . basename($file) . '. Årsag: ' . $reason
        );

        return $file;
    }

    private function update_nav_item_preserving($menu_id, $item, array $changes = []) {
        $classes = array_values(array_filter((array) $item->classes));

        $args = [
            'menu-item-object-id'   => (int) $item->object_id,
            'menu-item-object'      => (string) $item->object,
            'menu-item-parent-id'   => (int) $item->menu_item_parent,
            'menu-item-position'    => (int) $item->menu_order,
            'menu-item-type'        => (string) $item->type,
            'menu-item-title'       => (string) $item->title,
            'menu-item-url'         => (string) $item->url,
            'menu-item-description' => (string) $item->description,
            'menu-item-attr-title'  => (string) $item->attr_title,
            'menu-item-target'      => (string) $item->target,
            'menu-item-classes'     => implode(' ', $classes),
            'menu-item-xfn'         => (string) $item->xfn,
            'menu-item-status'      => 'publish',
        ];

        $args = array_merge($args, $changes);

        $result = wp_update_nav_menu_item(
            $menu_id,
            (int) $item->ID,
            $args
        );

        if (is_wp_error($result)) {
            throw new RuntimeException($result->get_error_message());
        }

        return (int) $result;
    }

    private function create_page_menu_item($menu_id, $page, $title = '', $position = 0, $parent_id = 0) {
        $title = trim((string) $title);
        if ($title === '') {
            $title = $page->post_title;
        }

        $result = wp_update_nav_menu_item(
            $menu_id,
            0,
            [
                'menu-item-object-id' => (int) $page->ID,
                'menu-item-object'    => 'page',
                'menu-item-parent-id' => (int) $parent_id,
                'menu-item-position'  => (int) $position,
                'menu-item-type'      => 'post_type',
                'menu-item-title'     => $title,
                'menu-item-status'    => 'publish',
            ]
        );

        if (is_wp_error($result)) {
            throw new RuntimeException($result->get_error_message());
        }

        return (int) $result;
    }

    private function build_menu_tree(array $items) {
        $by_parent = [];

        foreach ($items as $item) {
            $parent_id = (int) $item->menu_item_parent;
            if (!isset($by_parent[$parent_id])) {
                $by_parent[$parent_id] = [];
            }
            $by_parent[$parent_id][] = $item;
        }

        foreach ($by_parent as &$children) {
            usort($children, static function($a, $b) {
                return ((int) $a->menu_order) <=> ((int) $b->menu_order);
            });
        }
        unset($children);

        return $by_parent;
    }

    private function render_menu_tree_html(array $tree, $parent_id = 0, array $visited = []) {
        if (!isset($tree[$parent_id])) {
            return '';
        }

        $html = '';

        foreach ($tree[$parent_id] as $item) {
            $item_id = (int) $item->ID;

            if (isset($visited[$item_id])) {
                continue;
            }

            $visited[$item_id] = true;

            $children = $this->render_menu_tree_html($tree, $item_id, $visited);
            $has_children = $children !== '';

            $classes = [
                'h18-menu-item',
                'h18-menu-item-' . $item_id,
            ];

            if ($has_children) {
                $classes[] = 'h18-menu-item-has-children';
            }

            $url = esc_url($item->url ?: '#');
            $title = esc_html($item->title);

            $html .= '<li class="' . esc_attr(implode(' ', $classes)) . '">';
            $html .= '<a href="' . $url . '">' . $title . '</a>';

            if ($has_children) {
                $html .= '<ul class="h18-submenu">' . $children . '</ul>';
            }

            $html .= '</li>';
        }

        return $html;
    }

    private function build_hangar18_menu_nav_blocks($menu_id) {
        $items = $this->get_menu_items($menu_id);
        $tree = $this->build_menu_tree($items);
        $links = $this->render_menu_tree_html($tree, 0);

        if ($links === '') {
            $links = '<li class="h18-menu-item"><a href="/">Hjem</a></li>';
        }

        $desktop = <<<HTML
<nav class="h18-desktop-nav" aria-label="Hovedmenu">
    <div class="h18-menu-box">
        <!-- HANGAR18-WEB-MENU-DESKTOP-START -->
        <ul class="h18-web-menu-root">
            {$links}
        </ul>
        <!-- HANGAR18-WEB-MENU-DESKTOP-END -->
    </div>
</nav>
HTML;

        $mobile = <<<HTML
<nav class="h18-mobile-nav" aria-label="Mobilmenu">
    <details>
        <summary aria-label="Åbn menu">
            <span class="h18-hamburger" aria-hidden="true"></span>
        </summary>
        <div class="h18-mobile-menu-panel">
            <!-- HANGAR18-WEB-MENU-MOBILE-START -->
            <ul class="h18-web-menu-root">
                {$links}
            </ul>
            <!-- HANGAR18-WEB-MENU-MOBILE-END -->
        </div>
    </details>
</nav>
HTML;

        return [
            'desktop' => $desktop,
            'mobile'  => $mobile,
        ];
    }

    private function replace_header_nav_blocks($header, $menu_id) {
        $blocks = $this->build_hangar18_menu_nav_blocks($menu_id);

        $desktop_pattern = '/<nav\s+class="h18-desktop-nav"[^>]*>.*?<\/nav>/s';
        $mobile_pattern  = '/<nav\s+class="h18-mobile-nav"[^>]*>.*?<\/nav>/s';

        $new_header = preg_replace(
            $desktop_pattern,
            $blocks['desktop'],
            $header,
            1,
            $desktop_count
        );

        if ($desktop_count !== 1) {
            throw new RuntimeException(
                'Kunne ikke finde præcis én h18-desktop-nav i Hangar18-headeren.'
            );
        }

        $new_header = preg_replace(
            $mobile_pattern,
            $blocks['mobile'],
            $new_header,
            1,
            $mobile_count
        );

        if ($mobile_count !== 1) {
            throw new RuntimeException(
                'Kunne ikke finde præcis én h18-mobile-nav i Hangar18-headeren.'
            );
        }

        return $new_header;
    }

    private function apply_menu_to_managed_shell($menu_id) {
        $shell = $this->get_shell_source();

        if (!$shell) {
            throw new RuntimeException(
                'Kunne ikke finde en komplet Hangar18 header/footer-shell.'
            );
        }

        $new_header = $this->replace_header_nav_blocks(
            $shell['header'],
            $menu_id
        );

        $new_header = $this->apply_design_to_header_html(
            $new_header,
            $this->get_header_design_settings()
        );

        $count = 0;

        foreach ($this->get_managed_pages() as $page) {
            $content = $page->post_content;

            $existing_header = $this->extract_block(
                $content,
                self::HEADER_START,
                self::HEADER_END
            );

            if (!$existing_header) {
                continue;
            }

            $content = $this->replace_block(
                $content,
                self::HEADER_START,
                self::HEADER_END,
                $new_header
            );

            $content = $this->strip_block(
                $content,
                self::OVERRIDE_START,
                self::OVERRIDE_END
            );

            $footer = $this->extract_block(
                $content,
                self::FOOTER_START,
                self::FOOTER_END
            );

            if ($footer) {
                $content = str_replace(
                    $footer,
                    trim($this->build_design_override_block()) . "\n\n" . $footer,
                    $content
                );
            }

            $result = wp_update_post(
                [
                    'ID'           => $page->ID,
                    'post_content' => $content,
                ],
                true
            );

            if (is_wp_error($result)) {
                throw new RuntimeException(
                    "Header-menu kunne ikke opdateres på side ID {$page->ID}: " .
                    $result->get_error_message()
                );
            }

            $count++;
        }

        $this->log(
            'INFO',
            'MENU_SHELL_APPLY_SUCCESS',
            "Menu ID {$menu_id} anvendt i Hangar18-headeren på {$count} sider."
        );

        return $count;
    }

    private function assign_menu_location($menu_id, $location) {
        $location = sanitize_key((string) $location);

        if ($location === '') {
            return false;
        }

        $registered = get_registered_nav_menus();

        if (!isset($registered[$location])) {
            throw new RuntimeException(
                "Temaets menu-location '{$location}' findes ikke."
            );
        }

        $locations = get_theme_mod('nav_menu_locations', []);
        if (!is_array($locations)) {
            $locations = [];
        }

        $locations[$location] = (int) $menu_id;
        set_theme_mod('nav_menu_locations', $locations);

        $this->log(
            'INFO',
            'MENU_LOCATION_ASSIGNED',
            "Menu ID {$menu_id} tildelt theme location '{$location}'."
        );

        return true;
    }

    public function render_menu() {
        $this->require_capability();

        $menus = wp_get_nav_menus();
        $menu_id = $this->get_selected_menu_id();
        $menu = $menu_id ? wp_get_nav_menu_object($menu_id) : null;
        $analysis = $menu_id
            ? $this->get_menu_analysis($menu_id)
            : [
                'items' => [],
                'home_found' => false,
                'duplicate_ids' => [],
                'duplicate_count' => 0,
            ];

        $items = $analysis['items'];
        $header_design = $this->get_header_design_settings();
        $menu_pinned = !empty($header_design['StickyOnScroll']);

        $item_payload = [];
        foreach ($items as $item) {
            $item_payload[] = [
                'id'       => (int) $item->ID,
                'title'    => $item->title,
                'parent'   => (int) $item->menu_item_parent,
                'remove'   => false,
            ];
        }

        $locations = get_registered_nav_menus();
        $assigned_locations = get_theme_mod('nav_menu_locations', []);
        if (!is_array($assigned_locations)) {
            $assigned_locations = [];
        }

        $selected_location = '';
        foreach ($assigned_locations as $location => $assigned_menu_id) {
            if ((int) $assigned_menu_id === (int) $menu_id) {
                $selected_location = $location;
                break;
            }
        }

        $item_object_ids = [];
        foreach ($items as $item) {
            if ($item->type === 'post_type' && $item->object === 'page') {
                $item_object_ids[(int) $item->object_id] = true;
            }
        }

        ?>
        <div class="wrap h18-admin">
            <h1>Menu</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan styres menuen:</strong>
                Vælg WordPress-menuen, træk punkterne for at ændre rækkefølge,
                ret det viste navn direkte i feltet, og vælg eventuelt
                <strong>Undermenu under</strong>.
                <strong>Fjern</strong> markerer et punkt til sletning.
                Først når WhatIf slås fra og du trykker <strong>Gem menu</strong>,
                ændres WordPress. Derefter opdateres Hangar18-headeren automatisk på alle styrede sider.
            </div>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_menu_pin'); ?>
                <input type="hidden" name="action" value="h18_save_menu_pin" />
                <div class="h18-whatif-help">
                    <label class="h18-safe-switch">
                        <input type="checkbox" name="pin_menu" value="1" <?php checked($menu_pinned); ?> />
                        <span><strong>Pin menu/header ved scroll</strong></span>
                    </label>
                    <div class="h18-action-copy"><span>Slå til, hvis headeren skal blive siddende øverst, mens siden ruller.</span></div>
                </div>
                <div class="h18-action-submit">
                    <button class="button button-secondary" type="submit">Gem pinning</button>
                    <div class="h18-action-copy"><strong>Anvendes på alle sider</strong><span><label><input type="checkbox" name="whatif" value="1" /> WhatIf – kontrollér først uden at gemme</label></span></div>
                </div>
            </form>

            <?php if (!$menus) : ?>
                <div class="notice notice-warning">
                    <p>Der findes ingen klassisk WordPress-menu endnu. Opret Hangar18 Hovedmenu nedenfor.</p>
                </div>

                <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <?php wp_nonce_field('h18_create_menu'); ?>
                    <input type="hidden" name="action" value="h18_create_menu" />
                    <div class="h18-whatif-help">
                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér for at se hvad der ville blive oprettet.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary" type="submit">Opret Hangar18 Hovedmenu</button>
                        <div class="h18-action-copy"><strong>Kun når ingen menu findes</strong><span>Opretter hovedmenuen med Hangar18-standardsiderne.</span></div>
                    </div>
                </form>
            <?php else : ?>

                <div class="h18-toolbar">
                    <form method="get">
                        <input type="hidden" name="page" value="hangar18-menu" />
                        <label><strong>WordPress-menu</strong></label>
                        <select name="menu_id" onchange="this.form.submit()">
                            <?php foreach ($menus as $menu_option) : ?>
                                <option value="<?php echo esc_attr($menu_option->term_id); ?>" <?php selected($menu_id, $menu_option->term_id); ?>>
                                    <?php echo esc_html($menu_option->name . ' [ID ' . $menu_option->term_id . ']'); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </form>

                    <div class="h18-menu-health">
                        <span class="<?php echo $analysis['home_found'] ? 'h18-health-ok' : 'h18-health-bad'; ?>">
                            Hjem: <?php echo $analysis['home_found'] ? 'OK' : 'MANGLER'; ?>
                        </span>
                        <span class="<?php echo $analysis['duplicate_count'] === 0 ? 'h18-health-ok' : 'h18-health-bad'; ?>">
                            Dubletter: <?php echo esc_html($analysis['duplicate_count']); ?>
                        </span>
                    </div>
                </div>

                <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <?php wp_nonce_field('h18_save_menu'); ?>
                    <input type="hidden" name="action" value="h18_save_menu" />
                    <input type="hidden" name="menu_id" value="<?php echo esc_attr($menu_id); ?>" />
                    <input
                        id="h18-menu-items-json"
                        type="hidden"
                        name="menu_items_json"
                        value="<?php echo esc_attr(wp_json_encode($item_payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)); ?>"
                    />

                    <div class="h18-form-header">
                        <div>
                            <h2><?php echo esc_html($menu ? $menu->name : 'Menu'); ?></h2>
                            <p>Menu ID <?php echo esc_html($menu_id); ?> · <?php echo esc_html(count($items)); ?> punkter</p>
                        </div>
                        <label class="h18-safe-switch">
                            <input type="checkbox" name="whatif" value="1" />
                            <span>WhatIf / simulering</span>
                        </label>
                    </div>

                    <section class="h18-panel">
                        <div class="h18-menu-settings-row">
                            <div class="h18-field">
                                <label for="h18-theme-location"><strong>Tema menu-location</strong></label>
                                <select id="h18-theme-location" name="theme_location">
                                    <option value="">— Behold eksisterende theme-location —</option>
                                    <?php foreach ($locations as $location => $description) : ?>
                                        <option value="<?php echo esc_attr($location); ?>" <?php selected($selected_location, $location); ?>>
                                            <?php echo esc_html($description . ' [' . $location . ']'); ?>
                                        </option>
                                    <?php endforeach; ?>
                                </select>
                                <p class="description">Hangar18-headeren bruger den valgte menu uanset theme-location; denne indstilling er kun til WordPress-temaets egen menuplacering.</p>
                            </div>
                        </div>

                        <h3>Menupunkter – træk for at ændre rækkefølge</h3>

                        <div id="h18-menu-sortable" class="h18-menu-sortable">
                            <?php foreach ($items as $item) : ?>
                                <div
                                    class="h18-menu-admin-item"
                                    data-id="<?php echo esc_attr($item->ID); ?>"
                                    data-parent="<?php echo esc_attr((int) $item->menu_item_parent); ?>"
                                    data-remove="0"
                                >
                                    <span class="dashicons dashicons-move h18-menu-drag-handle"></span>

                                    <div class="h18-menu-item-fields">
                                        <div class="h18-field">
                                            <label><strong>Vist navn</strong></label>
                                            <input class="h18-menu-title-input" type="text" value="<?php echo esc_attr($item->title); ?>" />
                                        </div>

                                        <div class="h18-field">
                                            <label><strong>Undermenu under</strong></label>
                                            <select class="h18-menu-parent-select">
                                                <option value="0">— Hovedmenu —</option>
                                                <?php foreach ($items as $parent_item) :
                                                    if ((int) $parent_item->ID === (int) $item->ID) {
                                                        continue;
                                                    }
                                                ?>
                                                    <option
                                                        value="<?php echo esc_attr($parent_item->ID); ?>"
                                                        <?php selected((int) $item->menu_item_parent, (int) $parent_item->ID); ?>
                                                    >
                                                        <?php echo esc_html($parent_item->title); ?>
                                                    </option>
                                                <?php endforeach; ?>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="h18-menu-item-meta">
                                        <code>ID <?php echo esc_html($item->ID); ?></code>
                                        <span><?php echo esc_html($item->type . ' / ' . $item->object); ?></span>
                                        <small><?php echo esc_html($item->url); ?></small>
                                    </div>

                                    <button type="button" class="button-link-delete h18-menu-remove">Fjern</button>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </section>

                    <div class="h18-form-actions h18-explained-action">
                        <div class="h18-whatif-help">
                            <div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Er simulering markeret, ændres hverken menuen eller siderne.</span></div>
                        </div>
                        <div class="h18-action-submit">
                            <button class="button button-primary button-hero" type="submit">Gem menu</button>
                            <div class="h18-action-copy"><strong>Gemmer hele menustrukturen</strong><span>Gemmer rækkefølge, navne, undermenuer og fjernelser og opdaterer headeren.</span></div>
                        </div>
                    </div>
                </form>

                <div class="h18-two-action-grid">
                    <form class="h18-panel" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <?php wp_nonce_field('h18_add_menu_page'); ?>
                        <input type="hidden" name="action" value="h18_add_menu_page" />
                        <input type="hidden" name="menu_id" value="<?php echo esc_attr($menu_id); ?>" />

                        <h3>Tilføj side til menu</h3>

                        <div class="h18-field">
                            <label><strong>WordPress-side</strong></label>
                            <select name="page_id" required>
                                <option value="">— Vælg side —</option>
                                <?php foreach ($this->get_menu_page_candidates() as $page_candidate) :
                                    $already = isset($item_object_ids[(int) $page_candidate->ID]);
                                ?>
                                    <option value="<?php echo esc_attr($page_candidate->ID); ?>" <?php disabled($already); ?>>
                                        <?php echo esc_html($page_candidate->post_title . ($already ? ' – allerede i menu' : '')); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="h18-field">
                            <label><strong>Vist navn (valgfrit)</strong></label>
                            <input type="text" name="custom_title" value="" />
                        </div>

                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <p><button class="button button-secondary" type="submit">Tilføj side</button></p>
                    </form>

                    <form class="h18-panel" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <?php wp_nonce_field('h18_repair_menu'); ?>
                        <input type="hidden" name="action" value="h18_repair_menu" />
                        <input type="hidden" name="menu_id" value="<?php echo esc_attr($menu_id); ?>" />

                        <h3>Sikr central menu-konfiguration</h3>
                        <p>Sikrer standardsiderne og den ønskede rækkefølge i hovedmenuen.</p>
                        <p><strong><?php echo esc_html(implode(' · ', array_map(static function($definition) { return $definition['title']; }, $this->get_default_menu_page_definitions()))); ?></strong></p>
                        <p>Dubletter af de samme WordPress-sider fjernes. Andre/manuelle menupunkter bevares bagefter.</p>

                        <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                        <p><button class="button button-secondary" type="submit">Sikr Hjem / standardsider og ryd dubletter</button></p>
                    </form>
                </div>
            <?php endif; ?>
        </div>
        <?php
    }

    public function handle_save_menu_pin() {
        $this->require_capability();
        check_admin_referer('h18_save_menu_pin');

        $settings = $this->get_header_design_settings();
        $pinned = !empty($_POST['pin_menu']);
        $settings['StickyOnScroll'] = $pinned;
        $settings = $this->normalize_header_design($settings);

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_MENU_PIN',
                '[WHATIF] Menu/header ville blive ' . ($pinned ? 'pinnet' : 'frigivet') . ' på alle styrede sider.'
            );
            $this->set_notice(
                'warning',
                'WHATIF: Menu/header ville blive ' . ($pinned ? 'pinnet' : 'frigivet') . '. Ingen data blev ændret.'
            );
            $this->redirect('hangar18-menu');
        }

        try {
            $this->create_full_managed_backup(
                'Før ændring af menu/header pinning'
            );

            update_option(
                self::HEADER_DESIGN_OPTION,
                $settings,
                false
            );

            $published = $settings;
            $published['Saved'] = gmdate('c');

            $this->publish_configuration_file(
                'Hangar18-HeaderDesign.json',
                $published
            );

            $count = $this->apply_header_design_to_managed_pages(
                $settings
            );

            $this->log(
                'INFO',
                'MENU_PIN_SAVED',
                'Pinning=' . ($pinned ? 'True' : 'False') .
                "; header opdateret på {$count} sider."
            );

            $this->set_notice(
                'success',
                $pinned
                    ? "Menu/header er pinnet og opdateret på {$count} sider."
                    : "Menu/header er frigivet og opdateret på {$count} sider."
            );

        } catch (Throwable $e) {
            $this->log('ERROR', 'MENU_PIN_FAILED', $e->getMessage());
            $this->set_notice('error', 'Pinning kunne ikke gemmes: ' . $e->getMessage());
        }

        $this->redirect('hangar18-menu');
    }

    public function handle_create_menu() {
        $this->require_capability();
        check_admin_referer('h18_create_menu');

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_MENU_CREATE',
                '[WHATIF] Ville oprette Hangar18 Hovedmenu og tilføje standardsider.'
            );
            $this->set_notice(
                'warning',
                'WHATIF: Hangar18 Hovedmenu med standardsider ville blive oprettet. Ingen data blev ændret.'
            );
            $this->redirect('hangar18-menu');
        }

        try {
            $this->create_full_managed_backup(
                'Før oprettelse af Hangar18 Hovedmenu'
            );

            $menu_id = wp_create_nav_menu('Hangar18 Hovedmenu');

            if (is_wp_error($menu_id)) {
                throw new RuntimeException($menu_id->get_error_message());
            }

            $position = 1;

            foreach ($this->get_default_menu_page_definitions() as $definition) {
                $page = $this->post_by_slug($definition['slug']);

                if (!$page || $page->post_status !== 'publish') {
                    continue;
                }

                $this->create_page_menu_item(
                    $menu_id,
                    $page,
                    $definition['title'],
                    $position++
                );
            }

            update_option(
                self::ACTIVE_MENU_OPTION,
                (int) $menu_id,
                false
            );

            $count = $this->apply_menu_to_managed_shell($menu_id);

            $this->sync_menu_order_configuration_from_nav_menu(
                $menu_id
            );

            $this->log(
                'INFO',
                'MENU_CREATE_SUCCESS',
                "Hangar18 Hovedmenu oprettet. ID {$menu_id}; header opdateret på {$count} sider."
            );

            $this->set_notice(
                'success',
                "Hangar18 Hovedmenu er oprettet og anvendt i headeren på {$count} sider."
            );

            $this->redirect(
                'hangar18-menu',
                ['menu_id' => (int) $menu_id]
            );

        } catch (Throwable $e) {
            $this->log('ERROR', 'MENU_CREATE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Menuen kunne ikke oprettes: ' . $e->getMessage());
            $this->redirect('hangar18-menu');
        }
    }

    public function handle_save_menu() {
        $this->require_capability();
        check_admin_referer('h18_save_menu');

        $menu_id = absint($_POST['menu_id'] ?? 0);
        $menu = wp_get_nav_menu_object($menu_id);

        if (!$menu) {
            $this->set_notice('error', 'Den valgte WordPress-menu findes ikke.');
            $this->redirect('hangar18-menu');
        }

        $payload = json_decode(
            wp_unslash($_POST['menu_items_json'] ?? '[]'),
            true
        );

        if (!is_array($payload)) {
            $this->set_notice('error', 'Menu-data kunne ikke læses.');
            $this->redirect('hangar18-menu', ['menu_id' => $menu_id]);
        }

        $theme_location = sanitize_key(
            wp_unslash($_POST['theme_location'] ?? '')
        );

        $removed = [];
        $kept_ids = [];

        foreach ($payload as $row) {
            $id = absint($row['id'] ?? 0);
            if (!$id) {
                continue;
            }

            if (!empty($row['remove'])) {
                $removed[$id] = true;
            } else {
                $kept_ids[$id] = true;
            }
        }

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_MENU_SAVE',
                "[WHATIF] Ville gemme Menu ID {$menu_id}. Punkter=" .
                count($kept_ids) . '; Fjernes=' . count($removed) .
                ($theme_location ? "; ThemeLocation={$theme_location}" : '')
            );

            $this->set_notice(
                'warning',
                'WHATIF: Menuen ville blive gemt, og Hangar18-headeren ville blive opdateret. Ingen data blev ændret.'
            );

            $this->redirect(
                'hangar18-menu',
                ['menu_id' => $menu_id]
            );
        }

        try {
            $this->backup_menu(
                $menu_id,
                "Før gem menu '{$menu->name}'"
            );

            $this->create_full_managed_backup(
                "Før menu '{$menu->name}' blev anvendt i Hangar18-headeren"
            );

            $current_items = $this->get_menu_items($menu_id);
            $current_by_id = [];

            foreach ($current_items as $item) {
                $current_by_id[(int) $item->ID] = $item;
            }

            foreach (array_keys($removed) as $remove_id) {
                if (isset($current_by_id[$remove_id])) {
                    wp_delete_post($remove_id, true);
                    $this->log(
                        'INFO',
                        'MENU_ITEM_DELETED',
                        "Menupunkt ID {$remove_id} blev fjernet fra Menu ID {$menu_id}."
                    );
                }
            }

            $order = 1;

            foreach ($payload as $row) {
                $item_id = absint($row['id'] ?? 0);

                if (!$item_id || isset($removed[$item_id])) {
                    continue;
                }

                if (!isset($current_by_id[$item_id])) {
                    continue;
                }

                $parent_id = absint($row['parent'] ?? 0);

                if (
                    $parent_id === $item_id ||
                    isset($removed[$parent_id]) ||
                    !isset($kept_ids[$parent_id])
                ) {
                    $parent_id = 0;
                }

                $title = sanitize_text_field(
                    (string) ($row['title'] ?? '')
                );

                if ($title === '') {
                    $title = $current_by_id[$item_id]->title;
                }

                $this->update_nav_item_preserving(
                    $menu_id,
                    $current_by_id[$item_id],
                    [
                        'menu-item-title'     => $title,
                        'menu-item-position'  => $order++,
                        'menu-item-parent-id' => $parent_id,
                    ]
                );
            }

            update_option(
                self::ACTIVE_MENU_OPTION,
                $menu_id,
                false
            );

            if ($theme_location !== '') {
                $this->assign_menu_location(
                    $menu_id,
                    $theme_location
                );
            }

            $page_count = $this->apply_menu_to_managed_shell(
                $menu_id
            );

            $this->sync_menu_order_configuration_from_nav_menu(
                $menu_id
            );

            $this->log(
                'INFO',
                'MENU_SAVE_SUCCESS',
                "Menu ID {$menu_id} gemt. Header opdateret på {$page_count} sider."
            );

            $this->set_notice(
                'success',
                "Menuen '{$menu->name}' er gemt og anvendt i Hangar18-headeren på {$page_count} sider."
            );

        } catch (Throwable $e) {
            $this->log('ERROR', 'MENU_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Menuen kunne ikke gemmes: ' . $e->getMessage());
        }

        $this->redirect(
            'hangar18-menu',
            ['menu_id' => $menu_id]
        );
    }

    public function handle_add_menu_page() {
        $this->require_capability();
        check_admin_referer('h18_add_menu_page');

        $menu_id = absint($_POST['menu_id'] ?? 0);
        $page_id = absint($_POST['page_id'] ?? 0);

        $menu = wp_get_nav_menu_object($menu_id);
        $page = $page_id ? get_post($page_id) : null;

        if (!$menu || !$page || $page->post_type !== 'page') {
            $this->set_notice('error', 'Menu eller side kunne ikke findes.');
            $this->redirect('hangar18-menu', ['menu_id' => $menu_id]);
        }

        foreach ($this->get_menu_items($menu_id) as $item) {
            if (
                $item->type === 'post_type' &&
                $item->object === 'page' &&
                (int) $item->object_id === (int) $page_id
            ) {
                $this->set_notice(
                    'warning',
                    "'{$page->post_title}' findes allerede i menuen. Der blev ikke oprettet en dublet."
                );
                $this->redirect(
                    'hangar18-menu',
                    ['menu_id' => $menu_id]
                );
            }
        }

        $custom_title = $this->post_text('custom_title');

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_MENU_ITEM_ADD',
                "[WHATIF] Ville tilføje side ID {$page_id} '{$page->post_title}' til Menu ID {$menu_id}."
            );
            $this->set_notice(
                'warning',
                "WHATIF: '{$page->post_title}' ville blive tilføjet til menuen. Ingen data blev ændret."
            );
            $this->redirect(
                'hangar18-menu',
                ['menu_id' => $menu_id]
            );
        }

        try {
            $this->backup_menu(
                $menu_id,
                "Før tilføjelse af '{$page->post_title}'"
            );

            $this->create_full_managed_backup(
                "Før nyt menupunkt '{$page->post_title}' blev anvendt i Hangar18-headeren"
            );

            $position = count($this->get_menu_items($menu_id)) + 1;

            $item_id = $this->create_page_menu_item(
                $menu_id,
                $page,
                $custom_title,
                $position
            );

            update_option(
                self::ACTIVE_MENU_OPTION,
                $menu_id,
                false
            );

            $page_count = $this->apply_menu_to_managed_shell(
                $menu_id
            );

            $this->sync_menu_order_configuration_from_nav_menu(
                $menu_id
            );

            $this->log(
                'INFO',
                'MENU_ITEM_ADD_SUCCESS',
                "Side ID {$page_id} tilføjet som menupunkt ID {$item_id}. HeaderPages={$page_count}."
            );

            $this->set_notice(
                'success',
                "'{$page->post_title}' er tilføjet til menuen og Hangar18-headeren er opdateret."
            );

        } catch (Throwable $e) {
            $this->log('ERROR', 'MENU_ITEM_ADD_FAILED', $e->getMessage());
            $this->set_notice('error', 'Menupunktet kunne ikke tilføjes: ' . $e->getMessage());
        }

        $this->redirect(
            'hangar18-menu',
            ['menu_id' => $menu_id]
        );
    }

    public function handle_repair_menu() {
        $this->require_capability();
        check_admin_referer('h18_repair_menu');

        $menu_id = absint($_POST['menu_id'] ?? 0);
        $menu = wp_get_nav_menu_object($menu_id);

        if (!$menu) {
            $this->set_notice('error', 'Den valgte WordPress-menu findes ikke.');
            $this->redirect('hangar18-menu');
        }

        $definitions = $this->get_default_menu_page_definitions();
        $items = $this->get_menu_items($menu_id);

        $seen = [];
        $duplicates = [];
        $present_pages = [];

        foreach ($items as $item) {
            if ($item->type !== 'post_type' || $item->object !== 'page') {
                continue;
            }

            $object_id = (int) $item->object_id;

            if (isset($seen[$object_id])) {
                $duplicates[] = (int) $item->ID;
            } else {
                $seen[$object_id] = (int) $item->ID;
                $present_pages[$object_id] = (int) $item->ID;
            }
        }

        $missing = [];

        foreach ($definitions as $definition) {
            $page = $this->post_by_slug($definition['slug']);

            if (!$page || $page->post_status !== 'publish') {
                continue;
            }

            if (!isset($present_pages[(int) $page->ID])) {
                $missing[] = [
                    'page'  => $page,
                    'title' => $definition['title'],
                ];
            }
        }

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_MENU_REPAIR',
                "[WHATIF] Menu ID {$menu_id}: mangler " .
                count($missing) . ' standardsider; dubletter=' .
                count($duplicates) . '.'
            );

            $this->set_notice(
                'warning',
                'WHATIF: Menuen ville blive repareret. Manglende standardsider: ' .
                count($missing) . '; dubletter der ville blive fjernet: ' .
                count($duplicates) . '. Ingen data blev ændret.'
            );

            $this->redirect(
                'hangar18-menu',
                ['menu_id' => $menu_id]
            );
        }

        try {
            $this->backup_menu(
                $menu_id,
                "Før reparation af menu '{$menu->name}'"
            );

            $this->create_full_managed_backup(
                "Før repareret menu '{$menu->name}' blev anvendt i Hangar18-headeren"
            );

            foreach ($duplicates as $duplicate_id) {
                wp_delete_post($duplicate_id, true);
                $this->log(
                    'INFO',
                    'MENU_DUPLICATE_REMOVED',
                    "Dublet-menupunkt ID {$duplicate_id} fjernet."
                );
            }

            foreach ($missing as $entry) {
                $this->create_page_menu_item(
                    $menu_id,
                    $entry['page'],
                    $entry['title'],
                    0
                );
            }

            $fresh_items = $this->get_menu_items($menu_id);
            $by_page_id = [];
            $extras = [];

            foreach ($fresh_items as $item) {
                if ($item->type === 'post_type' && $item->object === 'page') {
                    $by_page_id[(int) $item->object_id] = $item;
                }
            }

            $standard_item_ids = [];
            $order = 1;

            foreach ($definitions as $definition) {
                $page = $this->post_by_slug($definition['slug']);

                if (!$page || !isset($by_page_id[(int) $page->ID])) {
                    continue;
                }

                $item = $by_page_id[(int) $page->ID];
                $standard_item_ids[(int) $item->ID] = true;

                $this->update_nav_item_preserving(
                    $menu_id,
                    $item,
                    [
                        'menu-item-position'  => $order++,
                        'menu-item-parent-id' => 0,
                    ]
                );
            }

            $fresh_items = $this->get_menu_items($menu_id);

            foreach ($fresh_items as $item) {
                if (isset($standard_item_ids[(int) $item->ID])) {
                    continue;
                }

                $this->update_nav_item_preserving(
                    $menu_id,
                    $item,
                    [
                        'menu-item-position' => $order++,
                    ]
                );
            }

            update_option(
                self::ACTIVE_MENU_OPTION,
                $menu_id,
                false
            );

            $page_count = $this->apply_menu_to_managed_shell(
                $menu_id
            );

            $this->sync_menu_order_configuration_from_nav_menu(
                $menu_id
            );

            $this->log(
                'INFO',
                'MENU_REPAIR_SUCCESS',
                "Menu ID {$menu_id} repareret. Tilføjet=" .
                count($missing) . '; FjernetDubletter=' .
                count($duplicates) . "; HeaderPages={$page_count}."
            );

            $this->set_notice(
                'success',
                'Menuen er repareret. Tilføjede standardsider: ' .
                count($missing) . '; fjernede dubletter: ' .
                count($duplicates) . '. Hangar18-headeren er opdateret.'
            );

        } catch (Throwable $e) {
            $this->log('ERROR', 'MENU_REPAIR_FAILED', $e->getMessage());
            $this->set_notice('error', 'Menu-reparation fejlede: ' . $e->getMessage());
        }

        $this->redirect(
            'hangar18-menu',
            ['menu_id' => $menu_id]
        );
    }


    /* ================================================================
       HEADER / FOOTER / DESIGN
       ================================================================ */

    private function render_checkbox_setting($name, $label, $checked, $help = '') {
        ?>
        <div class="h18-field h18-checkbox-setting">
            <label>
                <input type="checkbox" name="<?php echo esc_attr($name); ?>" value="1" <?php checked(!empty($checked)); ?> />
                <strong><?php echo esc_html($label); ?></strong>
            </label>
            <?php if ($help !== '') : ?>
                <p class="description"><?php echo esc_html($help); ?></p>
            <?php endif; ?>
        </div>
        <?php
    }

    private function header_design_from_post() {
        return $this->normalize_header_design([
            'Version'                           => '2.3',
            'DesignerSchemaVersion'             => '1.1',
            'PrimaryColor'                      => $this->post_text('PrimaryColor'),
            'SecondaryColor'                    => $this->post_text('SecondaryColor'),
            'AccentColor'                       => $this->post_text('AccentColor'),
            'SurfaceColor'                      => $this->post_text('SurfaceColor'),
            'BackgroundColor'                   => $this->post_text('BackgroundColor'),
            'TextColor'                         => $this->post_text('TextColor'),
            'LightTextColor'                    => $this->post_text('LightTextColor'),
            'ActionColor'                       => $this->post_text('ActionColor'),
            'BodyFontFamily'                    => $this->post_text('BodyFontFamily'),
            'HeadingFontFamily'                 => $this->post_text('HeadingFontFamily'),
            'BodyFontSize'                      => $_POST['BodyFontSize'] ?? 16,
            'H1FontSize'                        => $_POST['H1FontSize'] ?? 48,
            'H2FontSize'                        => $_POST['H2FontSize'] ?? 32,
            'H3FontSize'                        => $_POST['H3FontSize'] ?? 22,
            'RadiusSmallPx'                     => $_POST['RadiusSmallPx'] ?? 4,
            'RadiusMediumPx'                    => $_POST['RadiusMediumPx'] ?? 7,
            'RadiusLargePx'                     => $_POST['RadiusLargePx'] ?? 12,
            'SpacingXsPx'                       => $_POST['SpacingXsPx'] ?? 4,
            'SpacingSmallPx'                    => $_POST['SpacingSmallPx'] ?? 8,
            'SpacingMediumPx'                   => $_POST['SpacingMediumPx'] ?? 16,
            'SpacingLargePx'                    => $_POST['SpacingLargePx'] ?? 24,
            'SpacingXlPx'                       => $_POST['SpacingXlPx'] ?? 40,
            'BreakpointMobileMaxPx'             => $_POST['BreakpointMobileMaxPx'] ?? 782,
            'BreakpointTabletMaxPx'             => $_POST['BreakpointTabletMaxPx'] ?? 1199,
            'MotionFastMs'                      => $_POST['MotionFastMs'] ?? 120,
            'MotionNormalMs'                    => $_POST['MotionNormalMs'] ?? 220,
            'MotionSlowMs'                      => $_POST['MotionSlowMs'] ?? 420,
            'FocusRingColor'                    => $this->post_text('FocusRingColor'),
            'FocusRingWidthPx'                  => $_POST['FocusRingWidthPx'] ?? 3,
            'MenuPresentation'                  => $this->post_text('MenuPresentation'),
            'MenuHoverEffect'                   => $this->post_text('MenuHoverEffect'),
            'MenuActiveStyle'                   => $this->post_text('MenuActiveStyle'),
            'MenuTransitionMs'                  => $_POST['MenuTransitionMs'] ?? 180,
            'SubmenuAnimation'                  => $this->post_text('SubmenuAnimation'),
            'VisualBaseScalePercent'            => $_POST['VisualBaseScalePercent'] ?? 90,
            'MenuAlignment'                     => $this->post_text('MenuAlignment'),
            'PositionMode'                      => $this->post_text('PositionMode'),
            'StickyOnScroll'                    => !empty($_POST['StickyOnScroll']),
            'BackgroundMode'                    => $this->post_text('BackgroundMode'),
            'WidthMode'                         => $this->post_text('WidthMode'),
            'ShowBrand'                         => !empty($_POST['ShowBrand']),
            'BrandText'                         => $this->post_text('BrandText'),
            'IdentityAlignment'                 => $this->post_text('IdentityAlignment'),
            'BrandFontSize'                     => $_POST['BrandFontSize'] ?? 22,
            'BrandSizePercent'                  => $_POST['BrandSizePercent'] ?? 100,
            'ShowLogo'                          => !empty($_POST['ShowLogo']),
            'LogoMediaId'                       => absint($_POST['logo_media_id'] ?? 0),
            'LogoUrl'                           => $this->post_url('logo_media_url'),
            'LogoWidthPx'                       => $_POST['LogoWidthPx'] ?? 52,
            'LogoSizePercent'                   => $_POST['LogoSizePercent'] ?? 100,
            'MobileStyle'                       => $this->post_text('MobileStyle'),
            'MenuFontSize'                      => $_POST['MenuFontSize'] ?? 15,
            'MenuSizePercent'                   => $_POST['MenuSizePercent'] ?? 100,
            'MenuFontFamily'                    => $this->post_text('MenuFontFamily'),
            'MenuFontWeight'                    => $this->post_text('MenuFontWeight'),
            'MenuFontItalic'                    => !empty($_POST['MenuFontItalic']),
            'MenuUppercase'                     => !empty($_POST['MenuUppercase']),
            'ResponsiveScaleEnabled'            => !empty($_POST['ResponsiveScaleEnabled']),
            'ResponsiveLargeWidthPx'            => $_POST['ResponsiveLargeWidthPx'] ?? 2560,
            'ResponsiveLaptopWidthPx'           => $_POST['ResponsiveLaptopWidthPx'] ?? 1920,
            'ResponsiveLaptopScalePercent'      => $_POST['ResponsiveLaptopScalePercent'] ?? 90,
            'ResponsiveMinimumScalePercent'     => $_POST['ResponsiveMinimumScalePercent'] ?? 90,
            'DesktopContentWidthPercent'        => $_POST['DesktopContentWidthPercent'] ?? 80,
            'LaptopContentWidthPercent'         => $_POST['LaptopContentWidthPercent'] ?? 90,
            'MaximumDesktopContentWidthPercent' => $_POST['MaximumDesktopContentWidthPercent'] ?? 90,
            'ContentMaxWidth'                   => $this->post_text('ContentMaxWidth'),
            'FooterWidthPercent'                => $_POST['FooterWidthPercent'] ?? 100,
            'SectionSpacingPx'                  => $_POST['SectionSpacingPx'] ?? 32,
            'MobileSectionSpacingPx'            => $_POST['MobileSectionSpacingPx'] ?? 24,
            'ContentTopSpacingPx'               => $_POST['ContentTopSpacingPx'] ?? 32,
            'ContentBottomSpacingPx'            => $_POST['ContentBottomSpacingPx'] ?? 32,
            'MobileContentTopSpacingPx'         => $_POST['MobileContentTopSpacingPx'] ?? 24,
            'MobileContentBottomSpacingPx'      => $_POST['MobileContentBottomSpacingPx'] ?? 24,
        ]);
    }

    private function apply_header_design_to_managed_pages(array $settings) {
        $shell = $this->get_shell_source();

        if (!$shell) {
            throw new RuntimeException(
                'Kunne ikke finde en komplet Hangar18 header/footer-shell.'
            );
        }

        $master_header = $shell['header'];

        $active_menu_id = $this->get_active_menu_id();
        if ($active_menu_id) {
            try {
                $master_header = $this->replace_header_nav_blocks(
                    $master_header,
                    $active_menu_id
                );
            } catch (Throwable $ignored) {
                // Preserve existing menu HTML when it is not in the newer
                // web-menu structure yet.
            }
        }

        $master_header = $this->apply_design_to_header_html(
            $master_header,
            $settings
        );

        $override = $this->build_design_override_block($settings);
        $count = 0;

        foreach ($this->get_managed_pages() as $page) {
            $content = (string) $page->post_content;

            $existing_header = $this->extract_block(
                $content,
                self::HEADER_START,
                self::HEADER_END
            );

            if (!$existing_header) {
                continue;
            }

            $content = $this->replace_block(
                $content,
                self::HEADER_START,
                self::HEADER_END,
                $master_header
            );

            $content = $this->strip_block(
                $content,
                self::OVERRIDE_START,
                self::OVERRIDE_END
            );

            $footer = $this->extract_block(
                $content,
                self::FOOTER_START,
                self::FOOTER_END
            );

            if ($footer) {
                $content = str_replace(
                    $footer,
                    trim($override) . "\n\n" . $footer,
                    $content
                );
            } else {
                $content .= "\n\n" . trim($override);
            }

            $result = wp_update_post(
                [
                    'ID'           => $page->ID,
                    'post_content' => $content,
                ],
                true
            );

            if (is_wp_error($result)) {
                throw new RuntimeException(
                    "Side ID {$page->ID}: " .
                    $result->get_error_message()
                );
            }

            $count++;
        }

        return $count;
    }

    public function render_header_footer() {
        $this->require_capability();

        $s = $this->get_header_design_settings();
        $shell = $this->get_shell_source();

        $logo_media_id = (int) $s['LogoMediaId'];
        $logo_url = (string) $s['LogoUrl'];

        if ($logo_media_id > 0 && wp_get_attachment_url($logo_media_id)) {
            $logo_url = wp_get_attachment_url($logo_media_id);
        }

        ?>
        <div class="wrap h18-admin">
            <h1>Header / Footer og design</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan styres designet:</strong>
                Ændringer gemmes centralt i WordPress og anvendes på alle styrede sider. Der oprettes automatisk backup før rigtige ændringer.
            </div>

            <div class="h18-status-line">
                Shell-kilde:
                <strong><?php echo $shell ? esc_html($shell['source']->post_title . ' (ID ' . $shell['source']->ID . ')') : 'IKKE FUNDET'; ?></strong>
                · Styrede sider: <strong><?php echo esc_html(count($this->get_managed_pages())); ?></strong>
            </div>

            <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_design'); ?>
                <input type="hidden" name="action" value="h18_save_design" />

                <div class="h18-form-header">
                    <div>
                        <h2>Designindstillinger</h2>
                        <p>Indstillinger for header, menu, sidebredde, afstande og footer.</p>
                    </div>
                    <label class="h18-safe-switch">
                        <input type="checkbox" name="whatif" value="1" />
                        <span>WhatIf / simulering</span>
                    </label>
                </div>

                <div class="h18-settings-groups">
                    <section class="h18-panel h18-panel-wide">
                        <h3>Globalt designsystem</h3>
                        <p class="description">Fælles design tokens for sidebyggeren. Standardværdierne matcher v0.4.27.</p>
                        <div class="h18-dynamic-fields-grid">
                            <?php
                            $this->field('PrimaryColor', 'Primærfarve', $s['PrimaryColor'], 'color');
                            $this->field('SecondaryColor', 'Sekundærfarve', $s['SecondaryColor'], 'color');
                            $this->field('AccentColor', 'Accentfarve', $s['AccentColor'], 'color');
                            $this->field('SurfaceColor', 'Lys flade', $s['SurfaceColor'], 'color');
                            $this->field('BackgroundColor', 'Sidebaggrund', $s['BackgroundColor'], 'color');
                            $this->field('TextColor', 'Tekstfarve', $s['TextColor'], 'color');
                            $this->field('LightTextColor', 'Lys tekst', $s['LightTextColor'], 'color');
                            $this->field('ActionColor', 'Links / handlinger', $s['ActionColor'], 'color');
                            ?>
                        </div>
                    </section>
                    <section class="h18-panel">
                        <h3>Global typografi</h3>
                        <?php
                        $font_options = ['System'=>'System','Segoe UI'=>'Segoe UI','Arial'=>'Arial','Verdana'=>'Verdana','Tahoma'=>'Tahoma','Trebuchet MS'=>'Trebuchet MS','Georgia'=>'Georgia','Times New Roman'=>'Times New Roman','Courier New'=>'Courier New'];
                        $this->select_field('BodyFontFamily', 'Brødtekst-font', $s['BodyFontFamily'], $font_options);
                        $this->select_field('HeadingFontFamily', 'Overskrift-font', $s['HeadingFontFamily'], $font_options);
                        $this->field('BodyFontSize', 'Brødtekst (px)', $s['BodyFontSize'], 'number');
                        $this->field('H1FontSize', 'H1 maksimum (px)', $s['H1FontSize'], 'number');
                        $this->field('H2FontSize', 'H2 maksimum (px)', $s['H2FontSize'], 'number');
                        $this->field('H3FontSize', 'H3 maksimum (px)', $s['H3FontSize'], 'number');
                        ?>
                    </section>
                    <section class="h18-panel">
                        <h3>Afstande og hjørner</h3>
                        <?php
                        $this->field('SpacingXsPx', 'Afstand XS (px)', $s['SpacingXsPx'], 'number');
                        $this->field('SpacingSmallPx', 'Afstand S (px)', $s['SpacingSmallPx'], 'number');
                        $this->field('SpacingMediumPx', 'Afstand M (px)', $s['SpacingMediumPx'], 'number');
                        $this->field('SpacingLargePx', 'Afstand L (px)', $s['SpacingLargePx'], 'number');
                        $this->field('SpacingXlPx', 'Afstand XL (px)', $s['SpacingXlPx'], 'number');
                        $this->field('RadiusSmallPx', 'Afrunding S (px)', $s['RadiusSmallPx'], 'number');
                        $this->field('RadiusMediumPx', 'Afrunding M (px)', $s['RadiusMediumPx'], 'number');
                        $this->field('RadiusLargePx', 'Afrunding L (px)', $s['RadiusLargePx'], 'number');
                        ?>
                    </section>
                    <section class="h18-panel">
                        <h3>Responsive breakpoints</h3>
                        <p class="description">Globale breakpoints for sidebyggerens Desktop/Tablet/Mobil. Standard 782/1199 bevarer det nuværende layout.</p>
                        <?php
                        $this->field('BreakpointMobileMaxPx', 'Mobil maks. bredde (px)', $s['BreakpointMobileMaxPx'], 'number');
                        $this->field('BreakpointTabletMaxPx', 'Tablet maks. bredde (px)', $s['BreakpointTabletMaxPx'], 'number');
                        ?>
                    </section>
                    <section class="h18-panel">
                        <h3>Motion og fokus</h3>
                        <p class="description">Globale tokens for transitioner og keyboard-fokus. Reduced Motion respekteres fortsat.</p>
                        <?php
                        $this->field('MotionFastMs', 'Motion Fast (ms)', $s['MotionFastMs'], 'number');
                        $this->field('MotionNormalMs', 'Motion Normal (ms)', $s['MotionNormalMs'], 'number');
                        $this->field('MotionSlowMs', 'Motion Slow (ms)', $s['MotionSlowMs'], 'number');
                        $this->field('FocusRingColor', 'Global fokusfarve', $s['FocusRingColor'], 'color');
                        $this->field('FocusRingWidthPx', 'Global fokusbredde (px)', $s['FocusRingWidthPx'], 'number');
                        ?>
                    </section>
                    <section class="h18-panel">
                        <h3>Menu – præsentation og effekter</h3>
                        <?php
                        $this->select_field('MenuPresentation', 'Præsentation', $s['MenuPresentation'], ['Classic'=>'Klassisk','FloatingPill'=>'Flydende pill','Framed'=>'Indrammet']);
                        $this->select_field('MenuHoverEffect', 'Hover-effekt', $s['MenuHoverEffect'], ['None'=>'Ingen','Underline'=>'Animeret understregning','Lift'=>'Løft','Pill'=>'Pill-baggrund']);
                        $this->select_field('MenuActiveStyle', 'Aktiv side', $s['MenuActiveStyle'], ['None'=>'Ingen','Underline'=>'Understregning','Pill'=>'Pill','Dot'=>'Punkt']);
                        $this->select_field('SubmenuAnimation', 'Undermenu-animation', $s['SubmenuAnimation'], ['None'=>'Ingen','Fade'=>'Fade','FadeSlide'=>'Fade + slide','Scale'=>'Scale']);
                        $this->field('MenuTransitionMs', 'Animationshastighed (ms)', $s['MenuTransitionMs'], 'number');
                        ?>
                    </section>
                    <section class="h18-panel">
                        <h3>Generelt / position / baggrund</h3>
                        <?php
                        $this->field('VisualBaseScalePercent', 'VisualBaseScalePercent (%)', $s['VisualBaseScalePercent'], 'number');
                        $this->select_field('PositionMode', 'PositionMode', $s['PositionMode'], [
                            'Normal'   => 'Normal',
                            'Floating' => 'Floating',
                            'Overlay'  => 'Overlay',
                        ], 'Sticky ved scroll styres separat med feltet nedenfor.');
                        $this->render_checkbox_setting('StickyOnScroll', 'Pin menu/header ved scroll (StickyOnScroll)', $s['StickyOnScroll']);
                        $this->select_field('BackgroundMode', 'BackgroundMode', $s['BackgroundMode'], [
                            'None'  => 'None',
                            'Bar'   => 'Bar',
                            'Box'   => 'Box',
                            'Glass' => 'Glass',
                        ]);
                        $this->select_field('WidthMode', 'WidthMode', $s['WidthMode'], [
                            'Full'      => 'Full',
                            'Contained' => 'Contained',
                            'Narrow'    => 'Narrow',
                        ]);
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Identitet / foreningsnavn</h3>
                        <?php
                        $this->render_checkbox_setting('ShowBrand', 'ShowBrand', $s['ShowBrand']);
                        $this->field('BrandText', 'BrandText', $s['BrandText']);
                        $this->select_field('IdentityAlignment', 'IdentityAlignment', $s['IdentityAlignment'], [
                            'Left'   => 'Left',
                            'Center' => 'Center',
                            'Right'  => 'Right',
                        ]);
                        $this->field('BrandFontSize', 'BrandFontSize (px)', $s['BrandFontSize'], 'number');
                        $this->field('BrandSizePercent', 'BrandSizePercent (%)', $s['BrandSizePercent'], 'number');
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Logo</h3>
                        <?php $this->render_checkbox_setting('ShowLogo', 'ShowLogo', $s['ShowLogo']); ?>
                        <?php $this->render_media_field($logo_media_id, $logo_url, 'logo'); ?>
                        <?php
                        $this->field('LogoWidthPx', 'LogoWidthPx', $s['LogoWidthPx'], 'number');
                        $this->field('LogoSizePercent', 'LogoSizePercent (%)', $s['LogoSizePercent'], 'number');
                        ?>
                        <p class="description">Det valgte logo gemmes og anvendes på alle styrede sider.</p>
                    </section>

                    <section class="h18-panel">
                        <h3>Menu typografi / placering</h3>
                        <?php
                        $this->select_field('MenuAlignment', 'MenuAlignment', $s['MenuAlignment'], [
                            'Left'   => 'Left',
                            'Center' => 'Center',
                            'Right'  => 'Right',
                        ]);
                        $this->field('MenuFontSize', 'MenuFontSize (px)', $s['MenuFontSize'], 'number');
                        $this->field('MenuSizePercent', 'MenuSizePercent (%)', $s['MenuSizePercent'], 'number');
                        $this->select_field('MenuFontFamily', 'MenuFontFamily', $s['MenuFontFamily'], [
                            'System'          => 'System',
                            'Segoe UI'        => 'Segoe UI',
                            'Arial'           => 'Arial',
                            'Verdana'         => 'Verdana',
                            'Tahoma'          => 'Tahoma',
                            'Trebuchet MS'    => 'Trebuchet MS',
                            'Georgia'         => 'Georgia',
                            'Times New Roman' => 'Times New Roman',
                            'Courier New'     => 'Courier New',
                        ]);
                        $this->select_field('MenuFontWeight', 'MenuFontWeight', $s['MenuFontWeight'], [
                            'Normal'   => 'Normal',
                            'Medium'   => 'Medium',
                            'Semibold' => 'Semibold',
                            'Bold'     => 'Bold',
                        ]);
                        $this->render_checkbox_setting('MenuFontItalic', 'MenuFontItalic', $s['MenuFontItalic']);
                        $this->render_checkbox_setting('MenuUppercase', 'MenuUppercase', $s['MenuUppercase']);
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Mobil</h3>
                        <?php
                        $this->select_field('MobileStyle', 'MobileStyle', $s['MobileStyle'], [
                            'Dark'        => 'Dark',
                            'Transparent' => 'Transparent',
                        ]);
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Responsiv skalering</h3>
                        <?php
                        $this->render_checkbox_setting('ResponsiveScaleEnabled', 'ResponsiveScaleEnabled', $s['ResponsiveScaleEnabled']);
                        $this->field('ResponsiveLargeWidthPx', 'ResponsiveLargeWidthPx', $s['ResponsiveLargeWidthPx'], 'number');
                        $this->field('ResponsiveLaptopWidthPx', 'ResponsiveLaptopWidthPx', $s['ResponsiveLaptopWidthPx'], 'number');
                        $this->field('ResponsiveLaptopScalePercent', 'ResponsiveLaptopScalePercent (%)', $s['ResponsiveLaptopScalePercent'], 'number');
                        $this->field('ResponsiveMinimumScalePercent', 'ResponsiveMinimumScalePercent (%)', $s['ResponsiveMinimumScalePercent'], 'number', false, 'Mindste tilladte responsive skalering.');
                        ?>
                    </section>

                    <section class="h18-panel">
                        <h3>Indhold / bredde / footer</h3>
                        <?php
                        $this->field('DesktopContentWidthPercent', 'DesktopContentWidthPercent (%)', $s['DesktopContentWidthPercent'], 'number');
                        $this->field('LaptopContentWidthPercent', 'LaptopContentWidthPercent (%)', $s['LaptopContentWidthPercent'], 'number');
                        $this->field('MaximumDesktopContentWidthPercent', 'MaximumDesktopContentWidthPercent (%)', $s['MaximumDesktopContentWidthPercent'], 'number', false, 'Øvre grænse for indholdets bredde på desktop.');
                        $this->select_field('ContentMaxWidth', 'ContentMaxWidth', $s['ContentMaxWidth'], [
                            'None' => 'None',
                            '1400' => '1400 px',
                            '1600' => '1600 px',
                            '1800' => '1800 px',
                            '2000' => '2000 px',
                        ]);
                        $this->field('FooterWidthPercent', 'FooterWidthPercent (%)', $s['FooterWidthPercent'], 'number');
                        $this->field('SectionSpacingPx', 'Afstand mellem hovedsektioner – desktop (px)', $s['SectionSpacingPx'], 'number', false, 'Astra-lignende standard: 32 px. Første sektion får ingen ekstra topafstand.');
                        $this->field('MobileSectionSpacingPx', 'Afstand mellem hovedsektioner – mobil (px)', $s['MobileSectionSpacingPx'], 'number', false, 'Standard: 24 px på skærme op til 782 px.');
                        $this->field('ContentTopSpacingPx', 'Afstand fra header til indhold – desktop (px)', $s['ContentTopSpacingPx'], 'number', false, 'Luft under headeren uden at flytte headeren væk fra 0 px. Standard: 32 px.');
                        $this->field('ContentBottomSpacingPx', 'Afstand fra indhold til footer – desktop (px)', $s['ContentBottomSpacingPx'], 'number', false, 'Luft over footeren. Standard: 32 px.');
                        $this->field('MobileContentTopSpacingPx', 'Afstand fra header til indhold – mobil (px)', $s['MobileContentTopSpacingPx'], 'number', false, 'Mobil luft under headeren. Standard: 24 px.');
                        $this->field('MobileContentBottomSpacingPx', 'Afstand fra indhold til footer – mobil (px)', $s['MobileContentBottomSpacingPx'], 'number', false, 'Mobil luft over footeren. Standard: 24 px.');
                        ?>
                        <div class="h18-runtime-note">
                            <strong>Aktuel runtime:</strong><br>
                            Desktop-, laptop- og maksimumsbredderne anvendes direkte på header, indhold og footer. På mobil bruges 100 % bredde.
                        </div>
                    </section>
                </div>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-whatif-help">
                        <div class="h18-action-copy"><strong>WhatIf styres øverst</strong><span>Brug simulering til at kontrollere indstillingerne uden at ændre siderne.</span></div>
                    </div>
                    <div class="h18-action-submit">
                        <button class="button button-primary button-hero" type="submit">Gem design og opdater alle sider</button>
                        <div class="h18-action-copy"><strong>Normal gemning</strong><span>Gemmer header, footer, bredder og afstande og anvender dem på alle styrede sider.</span></div>
                    </div>
                </div>
            </form>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_sync_shell'); ?>
                <input type="hidden" name="action" value="h18_sync_shell" />
                <div class="h18-whatif-help">
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <div class="h18-action-copy"><strong>Kun simulering</strong><span>Markér for at kontrollere hvor mange sider der ville blive synkroniseret.</span></div>
                </div>
                <div class="h18-action-submit">
                    <button class="button button-secondary" type="submit">Kopiér header/footer fra Hjem</button>
                    <div class="h18-action-copy"><strong>Reparation</strong><span>Brug kun hvis Hjem er korrekt, men header eller footer på andre sider er kommet ud af sync.</span></div>
                </div>
            </form>
        </div>
        <?php
    }

    public function handle_save_design() {
        $this->require_capability();
        check_admin_referer('h18_save_design');

        $settings = $this->header_design_from_post();

        if (!empty($_POST['whatif'])) {
            $this->log(
                'WARN',
                'WHATIF_HEADER_DESIGN_1TO1',
                '[WHATIF] HeaderDesign schema 2.3 + Designer schema 1.0 ville blive gemt centralt og anvendt på ' .
                count($this->get_managed_pages()) .
                ' sider. StickyOnScroll=' .
                ($settings['StickyOnScroll'] ? 'True' : 'False') .
                '; Identity=' .
                $settings['IdentityAlignment'] .
                '; Menu=' .
                $settings['MenuAlignment'] .
                '; BrandSize=' .
                $settings['BrandSizePercent'] .
                '%; LogoSize=' .
                $settings['LogoSizePercent'] .
                '%; MenuSize=' .
                $settings['MenuSizePercent'] .
                '%.'
            );

            $this->set_notice(
                'warning',
                'WHATIF: Designindstillingerne ville blive gemt og anvendt på alle styrede sider. Ingen data blev ændret.'
            );

            $this->redirect('hangar18-header-footer');
        }

        try {
            $this->create_full_managed_backup(
                'Før HeaderDesign schema 2.3 + Designer schema 1.0 blev ændret fra web-manager'
            );

            update_option(
                self::HEADER_DESIGN_OPTION,
                $settings,
                false
            );

            $central = $settings;
            $central['Saved'] = gmdate('c');

            $this->publish_configuration_file(
                'Hangar18-HeaderDesign.json',
                $central
            );

            $count = $this->apply_header_design_to_managed_pages(
                $settings
            );

            $this->log(
                'INFO',
                'HEADER_DESIGN_1TO1_SAVED',
                'HeaderDesign schema 2.3 + Designer schema 1.0 gemt centralt og anvendt på ' .
                $count .
                ' sider. StickyOnScroll=' .
                ($settings['StickyOnScroll'] ? 'True' : 'False') .
                '; PositionMode=' .
                $settings['PositionMode'] .
                '; Identity=' .
                $settings['IdentityAlignment'] .
                '; Menu=' .
                $settings['MenuAlignment'] .
                '.'
            );

            $this->set_notice(
                'success',
                "Designindstillingerne er gemt centralt i WordPress, og {$count} sider er opdateret."
            );

        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'HEADER_DESIGN_1TO1_SAVE_FAILED',
                $e->getMessage()
            );

            $this->set_notice(
                'error',
                'HeaderDesign kunne ikke gemmes: ' .
                $e->getMessage()
            );
        }

        $this->redirect('hangar18-header-footer');
    }

    public function handle_sync_shell() {
        $this->require_capability();
        check_admin_referer('h18_sync_shell');

        $shell = $this->get_shell_source();
        if (!$shell) {
            $this->set_notice('error', 'Kunne ikke finde en komplet Hangar18 header/footer-shell.');
            $this->redirect('hangar18-header-footer');
        }

        $pages = $this->get_managed_pages();

        if (!empty($_POST['whatif'])) {
            $this->log('WARN', 'WHATIF_SHELL_SYNC', '[WHATIF] Header/footer ville blive synkroniseret til ' . count($pages) . ' sider.');
            $this->set_notice('warning', 'WHATIF: Header/footer ville blive synkroniseret til ' . count($pages) . ' sider. Ingen data blev ændret.');
            $this->redirect('hangar18-header-footer');
        }

        try {
            $this->create_full_managed_backup('Før header/footer-synkronisering');

            $synced_header = $this->apply_design_to_header_html(
                $shell['header'],
                $this->get_header_design_settings()
            );

            $active_menu_id = $this->get_active_menu_id();
            if ($active_menu_id) {
                try {
                    $synced_header = $this->replace_header_nav_blocks(
                        $synced_header,
                        $active_menu_id
                    );
                } catch (Throwable $ignored) {
                    // Preserve current header menu if web-nav replacement
                    // cannot be applied to an older header structure.
                }
            }

            $count = 0;
            foreach ($pages as $page) {
                if ((int) $page->ID === (int) $shell['source']->ID) {
                    continue;
                }

                $content = $page->post_content;
                $content = $this->replace_block($content, self::HEADER_START, self::HEADER_END, $synced_header);
                $content = $this->replace_block($content, self::CSS_START, self::CSS_END, $shell['css']);
                $content = $this->replace_block($content, self::FOOTER_START, self::FOOTER_END, $shell['footer']);
                $content = $this->strip_block($content, self::OVERRIDE_START, self::OVERRIDE_END);

                $footer = $this->extract_block($content, self::FOOTER_START, self::FOOTER_END);
                if ($footer) {
                    $content = str_replace($footer, trim($this->build_design_override_block()) . "\n\n" . $footer, $content);
                }

                $result = wp_update_post(['ID' => $page->ID, 'post_content' => $content], true);
                if (is_wp_error($result)) {
                    throw new RuntimeException("Side ID {$page->ID}: " . $result->get_error_message());
                }

                $count++;
            }

            $this->log('INFO', 'SHELL_SYNC_SUCCESS', "Header/footer synkroniseret til {$count} sider.");
            $this->set_notice('success', "Header/footer er synkroniseret til {$count} sider.");

        } catch (Throwable $e) {
            $this->log('ERROR', 'SHELL_SYNC_FAILED', $e->getMessage());
            $this->set_notice('error', 'Synkronisering fejlede: ' . $e->getMessage());
        }

        $this->redirect('hangar18-header-footer');
    }


    /* ================================================================
       GITHUB UPDATER
       ================================================================ */

    private function default_update_settings() {
        return [
            'Version'          => '1.0',
            'Repository'       => 'phenixdk2020/hangar18-manager',
            'Branch'           => 'main',
            'ManifestPath'     => 'update.json',
            'PackagePath'      => 'dist/hangar18-manager.zip',
            'AutoCheckEnabled' => true,
            'CheckIntervalHours' => 6,
            'AutoInstallEnabled' => false,
        ];
    }

    private function normalize_update_settings(array $saved) {
        $default = $this->default_update_settings();

        $repository = trim((string) ($saved['Repository'] ?? ''));
        if (!preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/', $repository)) {
            $repository = $default['Repository'];
        }

        $branch = trim((string) ($saved['Branch'] ?? ''));
        if ($branch === '' || strlen($branch) > 200) {
            $branch = $default['Branch'];
        }

        $manifest_path = ltrim(trim((string) ($saved['ManifestPath'] ?? '')), '/');
        if ($manifest_path === '' || strpos($manifest_path, '..') !== false) {
            $manifest_path = $default['ManifestPath'];
        }

        $package_path = ltrim(trim((string) ($saved['PackagePath'] ?? '')), '/');
        if ($package_path === '' || strpos($package_path, '..') !== false) {
            $package_path = $default['PackagePath'];
        }

        return [
            'Version'            => '1.0',
            'Repository'         => $repository,
            'Branch'             => $branch,
            'ManifestPath'       => $manifest_path,
            'PackagePath'        => $package_path,
            'AutoCheckEnabled'   => array_key_exists('AutoCheckEnabled', $saved)
                ? $this->bool_value($saved['AutoCheckEnabled'], true)
                : true,
            'CheckIntervalHours' => $this->clamp_int(
                $saved['CheckIntervalHours'] ?? 6,
                1,
                168,
                6
            ),
            'AutoInstallEnabled' => array_key_exists('AutoInstallEnabled', $saved)
                ? $this->bool_value($saved['AutoInstallEnabled'], false)
                : false,
        ];
    }

    private function get_update_settings() {
        $stored = get_option(self::UPDATE_SETTINGS_OPTION, []);

        if (!is_array($stored) || !$stored) {
            return $this->default_update_settings();
        }

        return $this->normalize_update_settings($stored);
    }

    private function get_update_state() {
        $state = get_option(self::UPDATE_STATE_OPTION, []);

        return is_array($state) ? $state : [];
    }

    private function github_token() {
        if (defined('HANGAR18_GITHUB_TOKEN')) {
            return trim((string) constant('HANGAR18_GITHUB_TOKEN'));
        }

        return '';
    }

    private function github_headers() {
        $headers = [
            'Accept'               => 'application/vnd.github+json',
            'User-Agent'           => 'Hangar18-Manager/' . self::VERSION,
            'X-GitHub-Api-Version' => '2022-11-28',
        ];

        $token = $this->github_token();

        if ($token !== '') {
            $headers['Authorization'] = 'Bearer ' . $token;
        }

        return $headers;
    }

    private function github_contents_url($repository, $path, $branch) {
        return 'https://api.github.com/repos/' .
            rawurlencode(explode('/', $repository, 2)[0]) . '/' .
            rawurlencode(explode('/', $repository, 2)[1]) .
            '/contents/' .
            str_replace('%2F', '/', rawurlencode(ltrim($path, '/'))) .
            '?ref=' .
            rawurlencode($branch);
    }

    private function github_fetch_file_bytes($repository, $path, $branch) {
        $url = $this->github_contents_url(
            $repository,
            $path,
            $branch
        );

        $response = wp_remote_get($url, [
            'timeout'     => 30,
            'redirection' => 3,
            'headers'     => $this->github_headers(),
        ]);

        if (is_wp_error($response)) {
            throw new RuntimeException(
                'GitHub kunne ikke kontaktes: ' .
                $response->get_error_message()
            );
        }

        $status = (int) wp_remote_retrieve_response_code($response);
        $body = (string) wp_remote_retrieve_body($response);

        if ($status === 404) {
            $token_configured = $this->github_token() !== '';

            if ($token_configured) {
                throw new RuntimeException(
                    "GitHub returnerede 404 for '{$path}' i {$repository}@{$branch}. " .
                    'Kontrollér filsti og branch, og kontrollér at HANGAR18_GITHUB_TOKEN har adgang til repositoryet.'
                );
            }

            throw new RuntimeException(
                "GitHub returnerede 404 for '{$path}' i {$repository}@{$branch}. " .
                'Hvis repositoryet er public, kontrollér Repository, Branch og filsti. ' .
                'Hvis repositoryet er privat, skal HANGAR18_GITHUB_TOKEN være defineret i wp-config.php med Contents: Read.'
            );
        }

        if ($status === 401 || $status === 403) {
            throw new RuntimeException(
                'GitHub afviste adgang. Hvis repository er privat, skal ' .
                'HANGAR18_GITHUB_TOKEN defineres i wp-config.php med Contents: Read.'
            );
        }

        if ($status < 200 || $status >= 300) {
            throw new RuntimeException(
                "GitHub API svarede HTTP {$status}."
            );
        }

        $payload = json_decode($body, true);

        if (!is_array($payload)) {
            throw new RuntimeException(
                'GitHub API returnerede ugyldigt JSON.'
            );
        }

        if (($payload['type'] ?? '') !== 'file') {
            throw new RuntimeException(
                "'{$path}' er ikke en fil i GitHub."
            );
        }

        $encoding = strtolower((string) ($payload['encoding'] ?? ''));
        $content = (string) ($payload['content'] ?? '');

        if ($encoding !== 'base64' || $content === '') {
            throw new RuntimeException(
                "GitHub returnerede ikke Base64-indhold for '{$path}'."
            );
        }

        $bytes = base64_decode(
            preg_replace('/\s+/', '', $content),
            true
        );

        if ($bytes === false) {
            throw new RuntimeException(
                "GitHub Base64-indhold kunne ikke afkodes for '{$path}'."
            );
        }

        return [
            'bytes' => $bytes,
            'sha'   => (string) ($payload['sha'] ?? ''),
            'size'  => (int) ($payload['size'] ?? strlen($bytes)),
            'url'   => (string) ($payload['html_url'] ?? ''),
        ];
    }

    private function normalize_update_manifest(array $manifest) {
        $schema = trim((string) ($manifest['schema_version'] ?? ''));

        if ($schema !== '1.0') {
            throw new RuntimeException(
                'Ukendt update.json schema_version: ' . $schema
            );
        }

        $plugin = trim((string) ($manifest['plugin'] ?? ''));
        if ($plugin !== 'hangar18-manager') {
            throw new RuntimeException(
                'update.json tilhører ikke hangar18-manager.'
            );
        }

        $version = trim((string) ($manifest['version'] ?? ''));
        if (!preg_match('/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/', $version)) {
            throw new RuntimeException(
                'update.json indeholder ugyldigt versionsnummer.'
            );
        }

        $package_path = ltrim(
            trim((string) ($manifest['package_path'] ?? '')),
            '/'
        );

        if ($package_path === '' || strpos($package_path, '..') !== false) {
            throw new RuntimeException(
                'update.json mangler gyldig package_path.'
            );
        }

        $sha256 = strtolower(
            trim((string) ($manifest['package_sha256'] ?? ''))
        );

        if (!preg_match('/^[a-f0-9]{64}$/', $sha256)) {
            throw new RuntimeException(
                'update.json mangler gyldig package_sha256.'
            );
        }

        $changelog = $manifest['changelog'] ?? [];
        if (!is_array($changelog)) {
            $changelog = [(string) $changelog];
        }

        $clean_changelog = [];
        foreach ($changelog as $line) {
            $line = trim((string) $line);
            if ($line !== '') {
                $clean_changelog[] = $line;
            }
        }

        return [
            'schema_version' => '1.0',
            'plugin'         => 'hangar18-manager',
            'version'        => $version,
            'min_wp'         => trim((string) ($manifest['min_wp'] ?? '6.4')),
            'min_php'        => trim((string) ($manifest['min_php'] ?? '8.0')),
            'published_utc'  => trim((string) ($manifest['published_utc'] ?? '')),
            'package_path'   => $package_path,
            'package_sha256' => $sha256,
            'changelog'      => $clean_changelog,
        ];
    }

    private function fetch_update_manifest(array $settings = null) {
        $settings = $settings ?: $this->get_update_settings();

        $file = $this->github_fetch_file_bytes(
            $settings['Repository'],
            $settings['ManifestPath'],
            $settings['Branch']
        );

        $manifest = json_decode(
            $this->strip_utf8_bom($file['bytes']),
            true
        );

        if (!is_array($manifest)) {
            throw new RuntimeException(
                'update.json kunne ikke afkodes.'
            );
        }

        return $this->normalize_update_manifest($manifest);
    }

    private function check_update_now($manual = false) {
        $settings = $this->get_update_settings();

        try {
            $manifest = $this->fetch_update_manifest($settings);

            $available = version_compare(
                $manifest['version'],
                self::VERSION,
                '>'
            );

            $compatible_wp = version_compare(
                get_bloginfo('version'),
                $manifest['min_wp'],
                '>='
            );

            $compatible_php = version_compare(
                PHP_VERSION,
                $manifest['min_php'],
                '>='
            );

            $state = [
                'checked_at_utc'  => gmdate('c'),
                'success'         => true,
                'repository'      => $settings['Repository'],
                'branch'          => $settings['Branch'],
                'current_version' => self::VERSION,
                'manifest'        => $manifest,
                'update_available'=> $available,
                'compatible_wp'   => $compatible_wp,
                'compatible_php'  => $compatible_php,
                'error'           => '',
            ];

            update_option(
                self::UPDATE_STATE_OPTION,
                $state,
                false
            );

            $this->log(
                'INFO',
                'UPDATE_CHECK_SUCCESS',
                'GitHub update check: current=' .
                self::VERSION .
                '; latest=' .
                $manifest['version'] .
                '; available=' .
                ($available ? 'True' : 'False') .
                '; repository=' .
                $settings['Repository'] .
                '.'
            );

            return $state;

        } catch (Throwable $e) {
            $state = [
                'checked_at_utc'  => gmdate('c'),
                'success'         => false,
                'repository'      => $settings['Repository'],
                'branch'          => $settings['Branch'],
                'current_version' => self::VERSION,
                'manifest'        => [],
                'update_available'=> false,
                'compatible_wp'   => false,
                'compatible_php'  => false,
                'error'           => $e->getMessage(),
            ];

            update_option(
                self::UPDATE_STATE_OPTION,
                $state,
                false
            );

            $this->log(
                $manual ? 'ERROR' : 'WARN',
                'UPDATE_CHECK_FAILED',
                $e->getMessage()
            );

            if ($manual) {
                throw $e;
            }

            return $state;
        }
    }

    public function maybe_check_for_updates() {
        if (!is_admin() || !current_user_can('edit_pages')) {
            return;
        }

        $settings = $this->get_update_settings();

        if (empty($settings['AutoCheckEnabled'])) {
            return;
        }

        $state = $this->get_update_state();

        $last = isset($state['checked_at_utc'])
            ? strtotime((string) $state['checked_at_utc'])
            : 0;

        $interval = max(
            3600,
            (int) $settings['CheckIntervalHours'] * HOUR_IN_SECONDS
        );

        if ($last && (time() - $last) < $interval) {
            return;
        }

        $this->check_update_now(false);
    }

    private function updates_dir() {
        $uploads = wp_upload_dir();

        if (!empty($uploads['error'])) {
            throw new RuntimeException(
                'Uploads-mappen er ikke tilgængelig: ' .
                $uploads['error']
            );
        }

        $dir = trailingslashit($uploads['basedir']) .
            'hangar18-manager-updates';

        if (!wp_mkdir_p($dir)) {
            throw new RuntimeException(
                'Kunne ikke oprette hangar18-manager-updates.'
            );
        }

        return $dir;
    }

    private function add_directory_to_zip($zip, $source_dir, $zip_prefix) {
        $source_dir = rtrim($source_dir, DIRECTORY_SEPARATOR);

        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator(
                $source_dir,
                FilesystemIterator::SKIP_DOTS
            ),
            RecursiveIteratorIterator::SELF_FIRST
        );

        foreach ($iterator as $item) {
            $full_path = $item->getPathname();
            $relative = substr(
                $full_path,
                strlen($source_dir) + 1
            );

            $zip_path = trim($zip_prefix, '/') .
                '/' .
                str_replace(DIRECTORY_SEPARATOR, '/', $relative);

            if ($item->isDir()) {
                $zip->addEmptyDir($zip_path);
            } else {
                $zip->addFile($full_path, $zip_path);
            }
        }
    }

    private function create_plugin_code_backup() {
        if (!class_exists('ZipArchive')) {
            throw new RuntimeException(
                'PHP ZipArchive er ikke installeret; plugin-kodebackup kan ikke oprettes.'
            );
        }

        $plugin_dir = plugin_dir_path(__FILE__);
        $backup_dir = trailingslashit($this->updates_dir()) . 'backups';

        if (!wp_mkdir_p($backup_dir)) {
            throw new RuntimeException(
                'Kunne ikke oprette update-backupmappen.'
            );
        }

        $file = trailingslashit($backup_dir) .
            'hangar18-manager-code-' .
            self::VERSION .
            '-' .
            gmdate('Ymd-His') .
            '.zip';

        $zip = new ZipArchive();

        if ($zip->open(
            $file,
            ZipArchive::CREATE | ZipArchive::OVERWRITE
        ) !== true) {
            throw new RuntimeException(
                'Kunne ikke oprette plugin-kodebackup.'
            );
        }

        $this->add_directory_to_zip(
            $zip,
            $plugin_dir,
            'hangar18-manager'
        );

        $zip->close();

        if (!is_file($file) || filesize($file) <= 0) {
            throw new RuntimeException(
                'Plugin-kodebackup blev ikke skrevet korrekt.'
            );
        }

        $this->log(
            'INFO',
            'UPDATE_CODE_BACKUP_SUCCESS',
            'Plugin-kodebackup: ' . basename($file)
        );

        return $file;
    }

    private function download_update_package(
        array $settings,
        array $manifest
    ) {
        $package = $this->github_fetch_file_bytes(
            $settings['Repository'],
            $manifest['package_path'],
            $settings['Branch']
        );

        $calculated = strtolower(
            hash('sha256', $package['bytes'])
        );

        if (!hash_equals(
            strtolower($manifest['package_sha256']),
            $calculated
        )) {
            throw new RuntimeException(
                'SHA-256-validering af update-pakken fejlede.'
            );
        }

        $file = trailingslashit($this->updates_dir()) .
            'hangar18-manager-' .
            sanitize_file_name($manifest['version']) .
            '-' .
            gmdate('Ymd-His') .
            '.zip';

        if (file_put_contents(
            $file,
            $package['bytes']
        ) === false) {
            throw new RuntimeException(
                'Update-pakken kunne ikke gemmes lokalt.'
            );
        }

        if (!is_file($file) || filesize($file) <= 0) {
            throw new RuntimeException(
                'Update-pakken er tom efter download.'
            );
        }

        $this->log(
            'INFO',
            'UPDATE_PACKAGE_VERIFIED',
            'Update-pakke downloadet og SHA-256-verificeret. Version=' .
            $manifest['version'] .
            '; Bytes=' .
            filesize($file) .
            '.'
        );

        return $file;
    }

    private function install_local_plugin_zip(
        $zip_file,
        $activate_after = true
    ) {
        if (!function_exists('request_filesystem_credentials')) {
            require_once ABSPATH . 'wp-admin/includes/file.php';
        }

        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
        require_once ABSPATH . 'wp-admin/includes/plugin.php';

        if (!WP_Filesystem()) {
            throw new RuntimeException(
                'WordPress Filesystem API kunne ikke initialiseres.'
            );
        }

        $skin = new Automatic_Upgrader_Skin();
        $upgrader = new Plugin_Upgrader($skin);

        $result = $upgrader->install(
            $zip_file,
            [
                'overwrite_package' => true,
            ]
        );

        if (is_wp_error($result)) {
            throw new RuntimeException(
                'Plugin-installation fejlede: ' .
                $result->get_error_message()
            );
        }

        if ($result !== true) {
            $messages = method_exists($skin, 'get_errors')
                ? $skin->get_errors()
                : null;

            if (is_wp_error($messages) && $messages->has_errors()) {
                throw new RuntimeException(
                    'Plugin-installation fejlede: ' .
                    $messages->get_error_message()
                );
            }

            throw new RuntimeException(
                'Plugin-installation returnerede ikke succes.'
            );
        }

        if ($activate_after) {
            $activate = activate_plugin(
                'hangar18-manager/hangar18-manager.php',
                '',
                false,
                true
            );

            if (is_wp_error($activate)) {
                throw new RuntimeException(
                    'Plugin blev installeret, men kunne ikke aktiveres: ' .
                    $activate->get_error_message()
                );
            }
        }

        return true;
    }

    private function acquire_update_lock() {
        $existing = get_option(self::UPDATE_LOCK_OPTION, []);

        if (
            is_array($existing) &&
            !empty($existing['created_at']) &&
            (time() - (int) $existing['created_at']) < 15 * MINUTE_IN_SECONDS
        ) {
            throw new RuntimeException(
                'En Hangar18-opdatering er allerede i gang.'
            );
        }

        update_option(
            self::UPDATE_LOCK_OPTION,
            [
                'created_at' => time(),
                'user_id'    => get_current_user_id(),
            ],
            false
        );
    }

    private function release_update_lock() {
        delete_option(self::UPDATE_LOCK_OPTION);
    }

    public function render_updates() {
        $this->require_capability();

        $settings = $this->get_update_settings();
        $state = $this->get_update_state();
        $manifest = is_array($state['manifest'] ?? null)
            ? $state['manifest']
            : [];

        $token_configured = $this->github_token() !== '';

        ?>
        <div class="wrap h18-admin">
            <h1>Opdateringer</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>GitHub updater:</strong>
                Hangar18 Manager læser <code><?php echo esc_html($settings['ManifestPath']); ?></code>
                fra det konfigurerede repository. Ved opdatering laves først
                WordPress-data-backup og plugin-kodebackup, derefter downloades ZIP-filen,
                SHA-256 verificeres, pluginet installeres og aktiveres igen.
                Hvis installationen fejler efter kodebackup, forsøges automatisk rollback.
            </div>

            <div class="h18-update-status-grid">
                <div class="h18-stat-card">
                    <strong><?php echo esc_html(self::VERSION); ?></strong>
                    <span>Installeret version</span>
                </div>

                <div class="h18-stat-card">
                    <strong><?php echo esc_html((string) ($manifest['version'] ?? '—')); ?></strong>
                    <span>Seneste GitHub-version</span>
                </div>

                <div class="h18-stat-card">
                    <strong><?php echo !empty($state['update_available']) ? 'JA' : 'NEJ'; ?></strong>
                    <span>Opdatering tilgængelig</span>
                </div>

                <div class="h18-stat-card">
                    <strong><?php echo $token_configured ? 'TOKEN' : 'PUBLIC'; ?></strong>
                    <span>GitHub adgangstilstand</span>
                </div>
            </div>

            <?php if (!empty($state['error'])) : ?>
                <div class="notice notice-warning">
                    <p><strong>Seneste update-check:</strong> <?php echo esc_html($state['error']); ?></p>
                </div>
            <?php endif; ?>

            <div class="h18-status-line">
                Repository:
                <strong><?php echo esc_html($settings['Repository']); ?></strong>
                · Branch:
                <strong><?php echo esc_html($settings['Branch']); ?></strong>
                · Adgang:
                <strong><?php echo $token_configured ? 'Token via wp-config.php' : 'Public / uden token'; ?></strong>
                · Sidst kontrolleret:
                <strong><?php echo esc_html((string) ($state['checked_at_utc'] ?? 'aldrig')); ?></strong>
            </div>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_check_updates'); ?>
                <input type="hidden" name="action" value="h18_check_updates" />
                <div class="h18-action-copy"><strong>Manuel kontrol</strong><span>Brug når du vil undersøge GitHub med det samme i stedet for at vente på næste automatiske kontrol.</span></div>
                <div class="h18-action-submit"><button class="button button-secondary" type="submit">Kontrollér GitHub nu</button></div>
            </form>

            <?php if (!empty($manifest)) : ?>
                <section class="h18-panel h18-update-release">
                    <h2>Version <?php echo esc_html($manifest['version']); ?></h2>
                    <p>
                        Publiceret UTC:
                        <strong><?php echo esc_html($manifest['published_utc'] ?: 'ukendt'); ?></strong>
                        · Kræver WordPress <?php echo esc_html($manifest['min_wp']); ?>+
                        · PHP <?php echo esc_html($manifest['min_php']); ?>+
                    </p>

                    <?php if (!empty($manifest['changelog'])) : ?>
                        <h3>Ændringer</h3>
                        <ul>
                            <?php foreach ($manifest['changelog'] as $line) : ?>
                                <li><?php echo esc_html($line); ?></li>
                            <?php endforeach; ?>
                        </ul>
                    <?php endif; ?>

                    <?php if (!empty($state['update_available'])) : ?>
                        <?php if (empty($state['compatible_wp']) || empty($state['compatible_php'])) : ?>
                            <div class="notice notice-error inline">
                                <p>Denne version er ikke kompatibel med den aktuelle WordPress/PHP-version.</p>
                            </div>
                        <?php else : ?>
                            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                                <?php wp_nonce_field('h18_install_update'); ?>
                                <input type="hidden" name="action" value="h18_install_update" />
                                <button
                                    class="button button-primary button-hero"
                                    type="submit"
                                    onclick="return confirm('Tag backup og opdater Hangar18 Manager til <?php echo esc_js($manifest['version']); ?>?');"
                                >
                                    Tag backup og opdater til <?php echo esc_html($manifest['version']); ?>
                                </button>
                                <p class="description">Brug når en nyere kompatibel version er fundet. Der tages automatisk backup før installationen.</p>
                            </form>
                        <?php endif; ?>
                    <?php else : ?>
                        <p><strong>Den installerede version er ajour.</strong></p>
                    <?php endif; ?>
                </section>
            <?php endif; ?>

            <form class="h18-editor-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_update_settings'); ?>
                <input type="hidden" name="action" value="h18_save_update_settings" />

                <div class="h18-form-header">
                    <h2>GitHub-indstillinger</h2>
                </div>

                <div class="h18-form-grid">
                    <section class="h18-panel">
                        <?php
                        $this->field('Repository', 'Repository (owner/name)', $settings['Repository']);
                        $this->field('Branch', 'Branch', $settings['Branch']);
                        $this->field('ManifestPath', 'Manifest path', $settings['ManifestPath']);
                        $this->field('PackagePath', 'Standard package path', $settings['PackagePath']);
                        $this->field('CheckIntervalHours', 'Automatisk check hver X time', $settings['CheckIntervalHours'], 'number');
                        ?>
                    </section>

                    <section class="h18-panel">
                        <?php
                        $this->render_checkbox_setting(
                            'AutoCheckEnabled',
                            'Kontrollér automatisk for opdateringer',
                            $settings['AutoCheckEnabled']
                        );
                        $this->render_checkbox_setting(
                            'AutoInstallEnabled',
                            'Installer automatisk (reserveret – ikke aktiv i v0.4.0)',
                            false,
                            'v0.4.0 kræver stadig et manuelt klik for installation.'
                        );
                        ?>

                        <div class="h18-runtime-note">
                            <strong>GitHub-adgang:</strong><br>
                            Public repository kræver intet token. Hvis repositoryet senere gøres privat,
                            kan et read-only token defineres i <code>wp-config.php</code>:
                            <pre>define('HANGAR18_GITHUB_TOKEN', 'github_pat_...');</pre>
                            Token behøver kun repository <strong>Contents: Read</strong> og gemmes ikke i WordPress-databasen.
                        </div>
                    </section>
                </div>

                <div class="h18-form-actions h18-explained-action">
                    <div class="h18-action-copy"><strong>Normalt ikke nødvendig</strong><span>Ret kun disse felter hvis repository, branch eller kontrolinterval skal ændres.</span></div>
                    <div class="h18-action-submit">
                        <button class="button button-primary" type="submit">Gem GitHub-indstillinger</button>
                        <div class="h18-action-copy"><strong>Gemmer updaterens forbindelse</strong><span>Nulstiller seneste kontrol, så de nye indstillinger bruges ved næste opslag.</span></div>
                    </div>
                </div>
            </form>
        </div>
        <?php
    }

    public function handle_save_update_settings() {
        $this->require_capability();
        check_admin_referer('h18_save_update_settings');

        $settings = $this->normalize_update_settings([
            'Version'            => '1.0',
            'Repository'         => $this->post_text('Repository'),
            'Branch'             => $this->post_text('Branch'),
            'ManifestPath'       => $this->post_text('ManifestPath'),
            'PackagePath'        => $this->post_text('PackagePath'),
            'AutoCheckEnabled'   => !empty($_POST['AutoCheckEnabled']),
            'CheckIntervalHours' => $_POST['CheckIntervalHours'] ?? 6,
            'AutoInstallEnabled' => false,
        ]);

        update_option(
            self::UPDATE_SETTINGS_OPTION,
            $settings,
            false
        );

        delete_option(self::UPDATE_STATE_OPTION);

        $this->log(
            'INFO',
            'UPDATE_SETTINGS_SAVED',
            'GitHub updater-indstillinger gemt. Repository=' .
            $settings['Repository'] .
            '; Branch=' .
            $settings['Branch'] .
            '.'
        );

        $this->set_notice(
            'success',
            'GitHub updater-indstillingerne er gemt.'
        );

        $this->redirect('hangar18-updates');
    }

    public function handle_check_updates() {
        $this->require_capability();
        check_admin_referer('h18_check_updates');

        try {
            $state = $this->check_update_now(true);

            if (!empty($state['update_available'])) {
                $version = (string) ($state['manifest']['version'] ?? '');
                $this->set_notice(
                    'success',
                    "Ny Hangar18 Manager version {$version} er tilgængelig."
                );
            } else {
                $this->set_notice(
                    'success',
                    'Ingen nyere Hangar18 Manager-version blev fundet.'
                );
            }
        } catch (Throwable $e) {
            $this->set_notice(
                'error',
                'GitHub update-check fejlede: ' .
                $e->getMessage()
            );
        }

        $this->redirect('hangar18-updates');
    }

    public function handle_install_update() {
        $this->require_capability();
        check_admin_referer('h18_install_update');

        if (!current_user_can('update_plugins')) {
            $this->set_notice(
                'error',
                'Din WordPress-bruger har ikke update_plugins-rettighed.'
            );
            $this->redirect('hangar18-updates');
        }

        $this->acquire_update_lock();

        $code_backup = '';
        $package_file = '';

        try {
            $state = $this->check_update_now(true);
            $manifest = $state['manifest'] ?? [];

            if (empty($state['update_available'])) {
                throw new RuntimeException(
                    'Der er ingen nyere version at installere.'
                );
            }

            if (empty($state['compatible_wp'])) {
                throw new RuntimeException(
                    'Ny version kræver WordPress ' .
                    (string) ($manifest['min_wp'] ?? '') .
                    ' eller nyere.'
                );
            }

            if (empty($state['compatible_php'])) {
                throw new RuntimeException(
                    'Ny version kræver PHP ' .
                    (string) ($manifest['min_php'] ?? '') .
                    ' eller nyere.'
                );
            }

            $settings = $this->get_update_settings();

            $this->log(
                'INFO',
                'UPDATE_START',
                'Starter Hangar18 Manager update: ' .
                self::VERSION .
                ' -> ' .
                (string) $manifest['version'] .
                '.'
            );

            $this->create_full_managed_backup(
                'Automatisk backup før Hangar18 Manager update til ' .
                (string) $manifest['version']
            );

            $code_backup = $this->create_plugin_code_backup();

            $package_file = $this->download_update_package(
                $settings,
                $manifest
            );

            $this->install_local_plugin_zip(
                $package_file,
                true
            );

            // Since the executing PHP file remains loaded for this request,
            // verify the installed file on disk instead of self::VERSION.
            $installed_file = WP_PLUGIN_DIR .
                '/hangar18-manager/hangar18-manager.php';

            if (!is_file($installed_file)) {
                throw new RuntimeException(
                    'Efter update mangler pluginets hovedfil.'
                );
            }

            $installed_source = file_get_contents($installed_file);
            $expected = preg_quote(
                (string) $manifest['version'],
                '/'
            );

            if (
                $installed_source === false ||
                !preg_match(
                    '/\*\s+Version:\s*' . $expected . '\s*$/m',
                    $installed_source
                )
            ) {
                throw new RuntimeException(
                    'Den installerede pluginfil har ikke forventet version ' .
                    (string) $manifest['version'] .
                    '.'
                );
            }

            $this->log(
                'INFO',
                'UPDATE_SUCCESS',
                'Hangar18 Manager opdateret til ' .
                (string) $manifest['version'] .
                '.'
            );

            $this->set_notice(
                'success',
                'Hangar18 Manager er opdateret til ' .
                (string) $manifest['version'] .
                '.'
            );

        } catch (Throwable $e) {
            $this->log(
                'ERROR',
                'UPDATE_FAILED',
                $e->getMessage()
            );

            $rollback_error = '';

            if ($code_backup && is_file($code_backup)) {
                try {
                    $this->log(
                        'WARN',
                        'UPDATE_ROLLBACK_START',
                        'Forsøger rollback fra ' .
                        basename($code_backup) .
                        '.'
                    );

                    $this->install_local_plugin_zip(
                        $code_backup,
                        true
                    );

                    $this->log(
                        'INFO',
                        'UPDATE_ROLLBACK_SUCCESS',
                        'Plugin-kode blev rullet tilbage til backup.'
                    );
                } catch (Throwable $rollback_exception) {
                    $rollback_error = $rollback_exception->getMessage();

                    $this->log(
                        'ERROR',
                        'UPDATE_ROLLBACK_FAILED',
                        $rollback_error
                    );
                }
            }

            $message = 'Opdatering fejlede: ' . $e->getMessage();

            if ($rollback_error !== '') {
                $message .= ' Rollback fejlede også: ' . $rollback_error;
            } elseif ($code_backup !== '') {
                $message .= ' Plugin-koden blev forsøgt rullet tilbage automatisk.';
            }

            $this->set_notice(
                'error',
                $message
            );
        } finally {
            $this->release_update_lock();
        }

        $this->redirect('hangar18-updates');
    }


    /* ================================================================
       BACKUP / LOG
       ================================================================ */

    private function read_managed_backup_file($filename) {
        $filename = sanitize_file_name((string) $filename);
        if (
            $filename === '' ||
            !preg_match('/^Hangar18-Web-(?:Full-Backup|Backup)-\d{8}-\d{6}(?:-Post-\d+)?\.json$/', $filename)
        ) {
            throw new RuntimeException('Det valgte backupfilnavn er ugyldigt.');
        }

        $dir = realpath($this->backup_dir());
        $path = $dir ? realpath(trailingslashit($dir) . $filename) : false;
        if (
            !$dir ||
            !$path ||
            wp_normalize_path(dirname($path)) !== wp_normalize_path($dir) ||
            !is_readable($path)
        ) {
            throw new RuntimeException('Den valgte backupfil kunne ikke findes eller læses.');
        }

        $size = filesize($path);
        if ($size === false || $size <= 0 || $size > 20 * MB_IN_BYTES) {
            throw new RuntimeException('Backupfilens størrelse er ugyldig.');
        }

        $json = file_get_contents($path);
        $payload = is_string($json) ? json_decode($json, true) : null;
        if (!is_array($payload) || json_last_error() !== JSON_ERROR_NONE) {
            throw new RuntimeException('Backupfilen indeholder ikke gyldig JSON.');
        }

        return $payload;
    }

    private function home_post_from_backup(array $payload) {
        $posts = [];
        if (isset($payload['posts']) && is_array($payload['posts'])) {
            $posts = $payload['posts'];
        } elseif (isset($payload['post']) && is_array($payload['post'])) {
            $posts = [$payload['post']];
        }

        foreach ($posts as $post) {
            if (!is_array($post)) {
                continue;
            }
            if (sanitize_title((string) ($post['post_name'] ?? '')) === self::HOME_SLUG) {
                return $post;
            }
        }
        return null;
    }

    private function backup_home_summary($filename) {
        try {
            $payload = $this->read_managed_backup_file($filename);
            $home = $this->home_post_from_backup($payload);
            $content = is_array($home) ? (string) ($home['post_content'] ?? '') : '';
            $reason = sanitize_text_field((string) ($payload['reason'] ?? 'Ikke angivet'));
            $is_original = is_array($home) && strpos($content, self::PAGE_EDITOR_MARKER) === false;
            return [
                'reason'      => $reason,
                'created_utc' => sanitize_text_field((string) ($payload['created_utc'] ?? '')),
                'has_home'    => is_array($home),
                'is_original' => $is_original,
                'recommended' => $is_original && stripos($reason, 'Før sideeditor gemte hjem') !== false,
            ];
        } catch (Throwable $e) {
            return [
                'reason'      => 'Kunne ikke læse backupen',
                'created_utc' => '',
                'has_home'    => false,
                'is_original' => false,
                'recommended' => false,
            ];
        }
    }

    private function comparison_page_for_backup($filename) {
        $posts = get_posts([
            'post_type'      => 'page',
            'post_status'    => ['draft', 'pending', 'private', 'publish'],
            'posts_per_page' => 1,
            'meta_key'       => '_h18_comparison_backup_file',
            'meta_value'     => sanitize_file_name((string) $filename),
            'orderby'        => 'ID',
            'order'          => 'DESC',
        ]);
        return isset($posts[0]) && $posts[0] instanceof WP_Post ? $posts[0] : null;
    }

    public function render_backup() {
        $this->require_capability();

        $files = [];
        try {
            $dir = $this->backup_dir();
            $paths = glob(trailingslashit($dir) . '*.json') ?: [];

            usort($paths, static function($a, $b) {
                return filemtime($b) <=> filemtime($a);
            });

            foreach (array_slice($paths, 0, 100) as $path) {
                $name = basename($path);
                $files[] = [
                    'name'       => $name,
                    'size'       => size_format(filesize($path)),
                    'time'       => wp_date('d-m-Y H:i:s', filemtime($path)),
                    'summary'    => $this->backup_home_summary($name),
                    'comparison' => $this->comparison_page_for_backup($name),
                ];
            }
        } catch (Throwable $e) {
            $this->set_notice('error', $e->getMessage());
        }

        ?>
        <div class="wrap h18-admin">
            <h1>Backup</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan styres backup:</strong>
                Web-manageren opretter automatisk JSON-backup før rigtige ændringer.
                Her kan du også lave en samlet backup af alle styrede Hangar18-sider.
                Filerne ligger i <code>wp-content/uploads/hangar18-manager-backups/</code>.
            </div>

            <div class="h18-help-box">
                <strong>Sammenlign den gamle Hjem-side:</strong>
                Brug kun knappen ved en backup markeret <strong>Oprindelig Hjem</strong>.
                Der oprettes en separat WordPress-kladde med backupens gamle indhold. Den aktive forside,
                menuen og side ID 9 ændres ikke.
            </div>

            <form class="h18-secondary-action h18-explained-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_create_full_backup'); ?>
                <input type="hidden" name="action" value="h18_create_full_backup" />
                <div class="h18-action-copy"><strong>Ekstra manuel sikkerhedskopi</strong><span>Brug før større manuelle ændringer. Web-manageren tager allerede automatisk backup før sine egne ændringer.</span></div>
                <div class="h18-action-submit"><button class="button button-primary" type="submit">Opret samlet backup nu</button></div>
            </form>

            <div class="h18-log-table-wrap">
                <table class="widefat striped">
                    <thead><tr><th>Tid</th><th>Fil</th><th>Backupgrund</th><th>Hjem-indhold</th><th>Størrelse</th><th>Handling</th></tr></thead>
                    <tbody>
                    <?php if (!$files) : ?>
                        <tr><td colspan="6">Ingen backup-filer fundet endnu.</td></tr>
                    <?php else : foreach ($files as $file) : ?>
                        <tr>
                            <td><?php echo esc_html($file['time']); ?></td>
                            <td><code><?php echo esc_html($file['name']); ?></code></td>
                            <td><?php echo esc_html($file['summary']['reason']); ?></td>
                            <td>
                                <?php if ($file['summary']['is_original']) : ?>
                                    <strong>Oprindelig Hjem<?php echo $file['summary']['recommended'] ? ' – anbefalet' : ''; ?></strong>
                                <?php elseif ($file['summary']['has_home']) : ?>
                                    Hjem fra sideeditor
                                <?php else : ?>
                                    Ingen Hjem-side
                                <?php endif; ?>
                            </td>
                            <td><?php echo esc_html($file['size']); ?></td>
                            <td>
                                <?php if ($file['comparison'] instanceof WP_Post) : ?>
                                    <a class="button" href="<?php echo esc_url(get_edit_post_link($file['comparison']->ID, '')); ?>">Åbn sammenligningskladde</a>
                                <?php elseif ($file['summary']['is_original']) : ?>
                                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                                        <?php wp_nonce_field('h18_create_home_comparison_' . $file['name']); ?>
                                        <input type="hidden" name="action" value="h18_create_home_comparison" />
                                        <input type="hidden" name="backup_file" value="<?php echo esc_attr($file['name']); ?>" />
                                        <button class="button button-primary" type="submit">Opret Hjem som sammenligningskladde</button>
                                    </form>
                                <?php else : ?>
                                    <span aria-hidden="true">—</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; endif; ?>
                    </tbody>
                </table>
            </div>
        </div>
        <?php
    }

    public function handle_create_full_backup() {
        $this->require_capability();
        check_admin_referer('h18_create_full_backup');

        try {
            $file = $this->create_full_managed_backup('Manuel samlet backup fra web-manager');
            $this->set_notice('success', 'Samlet backup oprettet: ' . basename($file));
        } catch (Throwable $e) {
            $this->log('ERROR', 'FULL_BACKUP_FAILED', $e->getMessage());
            $this->set_notice('error', 'Backup fejlede: ' . $e->getMessage());
        }

        $this->redirect('hangar18-backup');
    }

    public function handle_create_home_comparison() {
        $this->require_capability();
        $filename = isset($_POST['backup_file']) ? sanitize_file_name(wp_unslash($_POST['backup_file'])) : '';
        check_admin_referer('h18_create_home_comparison_' . $filename);

        try {
            $existing = $this->comparison_page_for_backup($filename);
            if ($existing instanceof WP_Post) {
                wp_safe_redirect(admin_url('post.php?post=' . (int) $existing->ID . '&action=edit'));
                exit;
            }

            $payload = $this->read_managed_backup_file($filename);
            $home = $this->home_post_from_backup($payload);
            if (!is_array($home)) {
                throw new RuntimeException('Backupen indeholder ikke Hjem-siden.');
            }

            $content = (string) ($home['post_content'] ?? '');
            if ($content === '' || strpos($content, self::PAGE_EDITOR_MARKER) !== false) {
                throw new RuntimeException('Backupen er ikke en oprindelig Hjem-side fra før sideeditoren.');
            }

            $source_id = absint($home['ID'] ?? 0);
            $created = sanitize_text_field((string) ($payload['created_utc'] ?? ''));
            $created_timestamp = $created !== '' ? strtotime($created) : false;
            $display_time = $created_timestamp
                ? wp_date('d-m-Y H:i:s', $created_timestamp)
                : preg_replace('/\D+/', '-', $filename);
            $draft_id = wp_insert_post([
                'post_type'      => 'page',
                'post_status'    => 'draft',
                'post_title'     => 'Hjem – gammel backup til sammenligning (' . $display_time . ')',
                'post_content'   => $content,
                'post_excerpt'   => (string) ($home['post_excerpt'] ?? ''),
                'post_parent'    => 0,
                'comment_status' => 'closed',
                'ping_status'    => 'closed',
                'page_template'  => 'default',
            ], true);
            if (is_wp_error($draft_id)) {
                throw new RuntimeException($draft_id->get_error_message());
            }

            $draft_id = (int) $draft_id;
            if ($source_id > 0) {
                $adapted = str_replace('page-id-' . $source_id, 'page-id-' . $draft_id, $content);
                if ($adapted !== $content) {
                    $updated = wp_update_post(['ID' => $draft_id, 'post_content' => $adapted], true);
                    if (is_wp_error($updated)) {
                        wp_delete_post($draft_id, true);
                        throw new RuntimeException($updated->get_error_message());
                    }
                }
            }

            $featured_id = absint($home['featured_id'] ?? 0);
            if ($featured_id > 0 && get_post($featured_id) instanceof WP_Post) {
                set_post_thumbnail($draft_id, $featured_id);
            }
            update_post_meta($draft_id, '_h18_comparison_backup_file', $filename);
            update_post_meta($draft_id, '_h18_comparison_source_id', $source_id);
            update_post_meta($draft_id, '_h18_comparison_created_utc', $created);

            $this->log('INFO', 'HOME_COMPARISON_CREATED', 'Sammenligningskladde oprettet fra ' . $filename . '. KladdeID=' . $draft_id . '.');
            wp_safe_redirect(admin_url('post.php?post=' . $draft_id . '&action=edit'));
            exit;
        } catch (Throwable $e) {
            $this->log('ERROR', 'HOME_COMPARISON_FAILED', $e->getMessage());
            $this->set_notice('error', 'Sammenligningskladden kunne ikke oprettes: ' . $e->getMessage());
            $this->redirect('hangar18-backup');
        }
    }

    public function render_log() {
        $this->require_capability();

        $entries = get_option(self::LOG_OPTION, []);
        if (!is_array($entries)) {
            $entries = [];
        }

        $entries = array_reverse($entries);

        ?>
        <div class="wrap h18-admin">
            <h1>Log</h1>
            <?php $this->render_notice(); ?>

            <div class="h18-help-box">
                <strong>Sådan bruges loggen:</strong>
                Brug checkpoint-kolonnen ved fejlmelding. Kopiér gerne hele fejllinjen med tidspunkt, niveau, checkpoint og besked.
            </div>

            <div class="h18-toolbar">
                <p>Seneste <?php echo esc_html(count($entries)); ?> poster.</p>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <?php wp_nonce_field('h18_clear_log'); ?>
                    <input type="hidden" name="action" value="h18_clear_log" />
                    <button class="button" type="submit" onclick="return confirm('Ryd loggen?');">Ryd log</button>
                </form>
            </div>

            <div class="h18-log-table-wrap">
                <table class="widefat striped h18-log-table">
                    <thead><tr><th>Tid</th><th>Niveau</th><th>Checkpoint</th><th>Bruger</th><th>Besked</th></tr></thead>
                    <tbody>
                    <?php if (!$entries) : ?>
                        <tr><td colspan="5">Ingen logposter endnu.</td></tr>
                    <?php else : foreach ($entries as $entry) : ?>
                        <tr>
                            <td><?php echo esc_html($entry['time'] ?? ''); ?></td>
                            <td><span class="h18-log-level h18-level-<?php echo esc_attr(strtolower($entry['level'] ?? 'info')); ?>"><?php echo esc_html($entry['level'] ?? ''); ?></span></td>
                            <td><code><?php echo esc_html($entry['checkpoint'] ?? ''); ?></code></td>
                            <td><?php echo esc_html($entry['user'] ?? ''); ?></td>
                            <td><?php echo esc_html($entry['message'] ?? ''); ?></td>
                        </tr>
                    <?php endforeach; endif; ?>
                    </tbody>
                </table>
            </div>
        </div>
        <?php
    }

    public function handle_clear_log() {
        $this->require_capability();
        check_admin_referer('h18_clear_log');

        delete_option(self::LOG_OPTION);
        $this->set_notice('success', 'Loggen er ryddet.');
        $this->redirect('hangar18-log');
    }

    private function redirect($page, array $args = []) {
        $url = admin_url('admin.php?page=' . rawurlencode($page));
        if ($args) {
            $url = add_query_arg($args, $url);
        }

        wp_safe_redirect($url);
        exit;
    }
}

Hangar18_Manager::instance();
