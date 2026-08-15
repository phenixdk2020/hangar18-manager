<?php
/**
 * Plugin Name: Hangar18 Manager
 * Plugin URI: https://hangar18.dk/
 * Description: Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.
 * Version: 0.4.15
 * Author: Hangar18
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Text Domain: hangar18-manager
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Hangar18_Manager {
    const VERSION = '0.4.15';

    const MENU_SLUG = 'hangar18-manager';

    const VEHICLE_PARENT_SLUG = 'koeretoejer-og-materiel';
    const EVENT_PARENT_SLUG   = 'events';
    const GALLERY_PARENT_SLUG = 'billedgalleri';
    const HOME_SLUG           = 'hjem';

    const VEHICLE_MARKER = 'HANGAR18-VEHICLE-DATA';
    const EVENT_MARKER   = 'HANGAR18-EVENT-DATA';
    const GALLERY_MARKER = 'HANGAR18-GALLERY-ALBUM-DATA';

    const LOG_OPTION               = 'hangar18_manager_log';
    const DESIGN_OPTION            = 'hangar18_manager_design'; // v0.3.0 legacy
    const HEADER_DESIGN_OPTION     = 'hangar18_manager_header_design_v25';
    const VEHICLE_REGISTER_OPTION  = 'hangar18_manager_vehicle_register_v12';
    const VEHICLE_FIELDS_OPTION    = 'hangar18_manager_vehicle_fields_v1';
    const CONTENT_LAYOUT_OPTION     = 'hangar18_manager_content_layout_v1';
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

    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_init', [$this, 'maybe_run_frontend_repair_046'], 15);
        add_action('admin_init', [$this, 'maybe_repair_astra_banner_047'], 16);
        add_action('admin_init', [$this, 'maybe_repair_vehicle_layout_049'], 17);
        add_action('admin_init', [$this, 'maybe_repair_legacy_page_templates_0411'], 18);
        add_action('admin_init', [$this, 'maybe_repair_mobile_content_layout_0414'], 19);
        add_action('admin_init', [$this, 'maybe_cleanup_legacy_startup_and_vehicle_mobile_0415'], 19);
        add_action('admin_init', [$this, 'maybe_check_for_updates'], 20);
        add_action('wp', [$this, 'disable_astra_banner_for_managed_pages'], 1);
        add_action('wp_head', [$this, 'render_frontend_runtime_fixes'], 999);
        add_action('wp_footer', [$this, 'render_header_origin_guard'], PHP_INT_MAX);
        add_action('admin_menu', [$this, 'register_admin_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_assets']);

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

        add_action('admin_post_h18_create_menu', [$this, 'handle_create_menu']);
        add_action('admin_post_h18_save_menu', [$this, 'handle_save_menu']);
        add_action('admin_post_h18_save_menu_pin', [$this, 'handle_save_menu_pin']);
        add_action('admin_post_h18_add_menu_page', [$this, 'handle_add_menu_page']);
        add_action('admin_post_h18_repair_menu', [$this, 'handle_repair_menu']);

        add_action('admin_post_h18_save_design', [$this, 'handle_save_design']);
        add_action('admin_post_h18_sync_shell', [$this, 'handle_sync_shell']);

        add_action('admin_post_h18_create_full_backup', [$this, 'handle_create_full_backup']);

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
            strpos($content, self::GALLERY_MARKER) !== false
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

        return [
            'Hangar18-HeaderDesign.json'    => $header,
            'Hangar18-MenuOrder.json'       => $menu,
            'Hangar18-VehicleRegister.json' => $vehicle,
            'Hangar18-VehicleFields.json'   => $vehicle_fields,
            'Hangar18-ContentLayout.json'   => $content_layout,
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
            <form class="h18-config-strip" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_vehicle_register_settings'); ?>
                <input type="hidden" name="action" value="h18_save_vehicle_register_settings" />

                <div class="h18-config-strip-title">
                    <strong>Placering af køretøjer</strong>
                    <span>Separate indstillinger for desktop og mobil</span>
                </div>

                <div class="h18-field">
                    <label><strong>Køretøjssiden / oversigten – desktop</strong></label>
                    <select name="register_alignment">
                        <option value="Left" <?php selected($vehicle_layout['RegisterAlignment'], 'Left'); ?>>Venstre</option>
                        <option value="Center" <?php selected($vehicle_layout['RegisterAlignment'], 'Center'); ?>>Midtstillet</option>
                    </select>
                    <p class="description">Placering af indhold og køretøjskort på desktop.</p>
                </div>

                <div class="h18-field">
                    <label><strong>Selve køretøjerne / detaljesider – desktop</strong></label>
                    <select name="detail_alignment">
                        <option value="Left" <?php selected($vehicle_layout['DetailAlignment'], 'Left'); ?>>Venstre</option>
                        <option value="Center" <?php selected($vehicle_layout['DetailAlignment'], 'Center'); ?>>Midtstillet</option>
                    </select>
                    <p class="description">Placering på de enkelte køretøjssider på desktop.</p>
                </div>

                <div class="h18-field">
                    <label><strong>Køretøjssiden / oversigten – mobil</strong></label>
                    <select name="mobile_register_alignment">
                        <option value="Left" <?php selected($vehicle_layout['MobileRegisterAlignment'], 'Left'); ?>>Venstre</option>
                        <option value="Center" <?php selected($vehicle_layout['MobileRegisterAlignment'], 'Center'); ?>>Midtstillet</option>
                    </select>
                    <p class="description">Placering af indhold og køretøjskort på mobil.</p>
                </div>

                <div class="h18-field">
                    <label><strong>Selve køretøjerne / detaljesider – mobil</strong></label>
                    <select name="mobile_detail_alignment">
                        <option value="Left" <?php selected($vehicle_layout['MobileDetailAlignment'], 'Left'); ?>>Venstre</option>
                        <option value="Center" <?php selected($vehicle_layout['MobileDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                    </select>
                    <p class="description">Placering på de enkelte køretøjssider på mobil.</p>
                </div>

                <label class="h18-inline-check">
                    <input type="checkbox" name="whatif" value="1" />
                    WhatIf
                </label>

                <button class="button button-secondary" type="submit">Gem køretøjslayout og anvend</button>
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

                <div class="h18-form-actions">
                    <button class="button button-primary button-hero" type="submit">Gem / opdater køretøj</button>
                    <span class="description">WhatIf = ingen skrivning. Slå den fra, når simuleringen er godkendt.</span>
                </div>
            </form>

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_rebuild_vehicle_register'); ?>
                <input type="hidden" name="action" value="h18_rebuild_vehicle_register" />
                <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                <button class="button" type="submit">Genbyg køretøjsregister</button>
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

                <div class="h18-form-actions">
                    <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                    <button class="button button-primary button-hero" type="submit">Gem feltopsætning og opdater køretøjssider</button>
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

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_event_layout'); ?>
                <input type="hidden" name="action" value="h18_save_event_layout" />
                <div class="h18-menu-settings-row">
                    <div class="h18-field">
                        <label><strong>Eventsiden / oversigten – desktop</strong></label>
                        <select name="event_index_alignment">
                            <option value="Left" <?php selected($content_layout['EventIndexAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['EventIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på desktop.</p>
                    </div>
                    <div class="h18-field">
                        <label><strong>Selve events / detaljesider – desktop</strong></label>
                        <select name="event_detail_alignment">
                            <option value="Left" <?php selected($content_layout['EventDetailAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['EventDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på desktop.</p>
                    </div>
                    <div class="h18-field">
                        <label><strong>Eventsiden / oversigten – mobil</strong></label>
                        <select name="mobile_event_index_alignment">
                            <option value="Left" <?php selected($content_layout['MobileEventIndexAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['MobileEventIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på skærme op til 782 px.</p>
                    </div>
                    <div class="h18-field">
                        <label><strong>Selve events / detaljesider – mobil</strong></label>
                        <select name="mobile_event_detail_alignment">
                            <option value="Left" <?php selected($content_layout['MobileEventDetailAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['MobileEventDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på skærme op til 782 px.</p>
                    </div>
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <button class="button button-secondary" type="submit">Gem event-layout og anvend</button>
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

                <div class="h18-form-actions"><button class="button button-primary button-hero" type="submit">Gem / opdater event</button></div>
            </form>

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_rebuild_event_register'); ?>
                <input type="hidden" name="action" value="h18_rebuild_event_register" />
                <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                <button class="button" type="submit">Genbyg eventregister</button>
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

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_gallery_layout'); ?>
                <input type="hidden" name="action" value="h18_save_gallery_layout" />
                <div class="h18-menu-settings-row">
                    <div class="h18-field">
                        <label><strong>Billedgalleri-siden / oversigten – desktop</strong></label>
                        <select name="gallery_index_alignment">
                            <option value="Left" <?php selected($content_layout['GalleryIndexAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['GalleryIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på desktop.</p>
                    </div>
                    <div class="h18-field">
                        <label><strong>Selve albums / detaljesider – desktop</strong></label>
                        <select name="gallery_detail_alignment">
                            <option value="Left" <?php selected($content_layout['GalleryDetailAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['GalleryDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på desktop.</p>
                    </div>
                    <div class="h18-field">
                        <label><strong>Billedgalleri-siden / oversigten – mobil</strong></label>
                        <select name="mobile_gallery_index_alignment">
                            <option value="Left" <?php selected($content_layout['MobileGalleryIndexAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['MobileGalleryIndexAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Placering på skærme op til 782 px.</p>
                    </div>
                    <div class="h18-field">
                        <label><strong>Selve albums / detaljesider – mobil</strong></label>
                        <select name="mobile_gallery_detail_alignment">
                            <option value="Left" <?php selected($content_layout['MobileGalleryDetailAlignment'], 'Left'); ?>>Venstre</option>
                            <option value="Center" <?php selected($content_layout['MobileGalleryDetailAlignment'], 'Center'); ?>>Midtstillet</option>
                        </select>
                        <p class="description">Billeder og albumtekst på skærme op til 782 px.</p>
                    </div>
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <button class="button button-secondary" type="submit">Gem galleri-layout og anvend</button>
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

                <div class="h18-form-actions"><button class="button button-primary button-hero" type="submit">Gem / opdater album</button></div>
            </form>

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_rebuild_gallery_index'); ?>
                <input type="hidden" name="action" value="h18_rebuild_gallery_index" />
                <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                <button class="button" type="submit">Genbyg Billedgalleri-indeks</button>
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
            return $page->post_name !== 'hangar18-configuration-store';
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

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_save_menu_pin'); ?>
                <input type="hidden" name="action" value="h18_save_menu_pin" />
                <div class="h18-menu-settings-row">
                    <label class="h18-safe-switch">
                        <input type="checkbox" name="pin_menu" value="1" <?php checked($menu_pinned); ?> />
                        <span><strong>Pin menu/header ved scroll</strong></span>
                    </label>
                    <span class="description">Når den er slået til, bliver Hangar18-headeren siddende øverst på alle styrede sider.</span>
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <button class="button button-secondary" type="submit">Gem pinning</button>
                </div>
            </form>

            <?php if (!$menus) : ?>
                <div class="notice notice-warning">
                    <p>Der findes ingen klassisk WordPress-menu endnu. Opret Hangar18 Hovedmenu nedenfor.</p>
                </div>

                <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <?php wp_nonce_field('h18_create_menu'); ?>
                    <input type="hidden" name="action" value="h18_create_menu" />
                    <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                    <button class="button button-primary" type="submit">Opret Hangar18 Hovedmenu med standardsider</button>
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

                    <div class="h18-form-actions">
                        <button class="button button-primary button-hero" type="submit">Gem menu</button>
                        <span class="description">Gemmer rækkefølge, viste navne, undermenuer, fjernelser og opdaterer Hangar18-headeren.</span>
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

                <div class="h18-form-actions">
                    <button class="button button-primary button-hero" type="submit">Gem HeaderDesign og opdater alle sider</button>
                    <span class="description">Ved rigtig gemning opdateres både web-manager-option, central Configuration Store og de styrede sider.</span>
                </div>
            </form>

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_sync_shell'); ?>
                <input type="hidden" name="action" value="h18_sync_shell" />
                <label><input type="checkbox" name="whatif" value="1" /> WhatIf</label>
                <button class="button button-secondary" type="submit">Kopiér header/footer fra Hjem til alle sider</button>
                <span class="description">Reparation: bruges kun hvis Hjem er korrekt, men andre sider er kommet ud af sync.</span>
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
                '[WHATIF] HeaderDesign schema 2.3 ville blive gemt centralt og anvendt på ' .
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
                'Før HeaderDesign schema 2.3 blev ændret fra web-manager'
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
                'HeaderDesign schema 2.3 gemt centralt og anvendt på ' .
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

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_check_updates'); ?>
                <input type="hidden" name="action" value="h18_check_updates" />
                <button class="button button-secondary" type="submit">Kontrollér GitHub nu</button>
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

                <div class="h18-form-actions">
                    <button class="button button-primary" type="submit">Gem GitHub-indstillinger</button>
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
                $files[] = [
                    'name' => basename($path),
                    'size' => size_format(filesize($path)),
                    'time' => wp_date('d-m-Y H:i:s', filemtime($path)),
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

            <form class="h18-secondary-action" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('h18_create_full_backup'); ?>
                <input type="hidden" name="action" value="h18_create_full_backup" />
                <button class="button button-primary" type="submit">Opret samlet backup nu</button>
            </form>

            <div class="h18-log-table-wrap">
                <table class="widefat striped">
                    <thead><tr><th>Tid</th><th>Fil</th><th>Størrelse</th></tr></thead>
                    <tbody>
                    <?php if (!$files) : ?>
                        <tr><td colspan="3">Ingen backup-filer fundet endnu.</td></tr>
                    <?php else : foreach ($files as $file) : ?>
                        <tr>
                            <td><?php echo esc_html($file['time']); ?></td>
                            <td><code><?php echo esc_html($file['name']); ?></code></td>
                            <td><?php echo esc_html($file['size']); ?></td>
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
