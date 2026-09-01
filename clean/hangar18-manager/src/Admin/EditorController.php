<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Diagnostics\DiagnosticStore;
use VisualDesignerManager\Frontend\Renderer;
use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;
use VisualDesignerManager\Update\GitHubUpdater;

final class EditorController
{
    private const MENU = 'h18-clean-editor';
    private const SAVE_ACTION = 'h18_clean_save';
    private const RESTORE_ACTION = 'h18_clean_restore';
    private const RESTORE_COPY_ACTION = 'h18_clean_restore_copy';
    private const PREVIEW_ACTION = 'h18_clean_preview';
    private const COMPOSITE_PREVIEW_ACTION = 'h18_clean_composite_preview';
    private const VERSION_PREVIEW_ACTION = 'h18_clean_version_preview';
    private const NONCE_SAVE = 'h18_clean_save';
    private const NONCE_RESTORE = 'h18_clean_restore';
    private const NONCE_RESTORE_COPY = 'h18_clean_restore_copy';
    private const NONCE_PREVIEW = 'h18_clean_preview';
    private const NONCE_COMPOSITE_PREVIEW = 'h18_clean_composite_preview';
    private const NONCE_VERSION_PREVIEW = 'h18_clean_version_preview';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);
        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);
        add_action('admin_post_' . self::RESTORE_COPY_ACTION, [self::class, 'restoreCopy']);
        add_action('admin_post_' . self::PREVIEW_ACTION, [self::class, 'preview']);
        add_action('admin_post_' . self::COMPOSITE_PREVIEW_ACTION, [self::class, 'compositePreview']);
        add_action('admin_post_' . self::VERSION_PREVIEW_ACTION, [self::class, 'previewVersion']);
    }

    public static function menu(): void
    {
        add_menu_page(
            'Visual Designer',
            'Visual Designer',
            'edit_pages',
            self::MENU,
            [self::class, 'render'],
            'dashicons-layout',
            21
        );
    }

    public static function enqueue(string $hook): void
    {
        if ($hook !== 'toplevel_page_' . self::MENU || !current_user_can('edit_pages')) {
            return;
        }
        wp_enqueue_media();
        wp_enqueue_style('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.css', [], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.js', ['jquery'], H18_CLEAN_VERSION, true);

        $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;
        $model = $postId > 0 && get_post_type($postId) === 'page' ? LayoutModel::get($postId) : LayoutModel::empty();
        wp_localize_script('h18-clean-editor', 'H18CleanEditor', [
            'version' => H18_CLEAN_VERSION,
            'schemaVersion' => LayoutModel::SCHEMA,
            'units' => LayoutModel::UNITS,
            'rowPx' => LayoutModel::ROW_PX,
            'postId' => $postId,
            'initialModel' => $model,
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'diagAction' => 'h18_clean_diag_append',
            'diagNonce' => wp_create_nonce('h18_clean_diag_append'),
        ]);
    }

    public static function render(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            self::renderPagePicker();
            return;
        }

        $post = get_post($postId);
        if (!$post instanceof \WP_Post) {
            self::renderPagePicker();
            return;
        }
        TemplateLayoutModel::ensureMigrated();
        $model = LayoutModel::get($postId);
        $headerTemplates = TemplateLayoutModel::all('header');
        $footerTemplates = TemplateLayoutModel::all('footer');
        $headerChoice = TemplateLayoutModel::pageChoice($postId, 'header');
        $footerChoice = TemplateLayoutModel::pageChoice($postId, 'footer');
        $history = array_reverse(LayoutModel::history($postId));
        $status = isset($_GET['h18_clean_status']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_status'])) : '';
        $message = isset($_GET['h18_clean_message']) ? sanitize_text_field((string) wp_unslash($_GET['h18_clean_message'])) : '';

        echo '<div class="wrap h18-clean-admin">';
        echo '<h1>Visual Designer · ' . esc_html((string) $post->post_title) . '</h1>';
        echo '<p class="description">Visual Designer ' . esc_html(H18_CLEAN_VERSION) . ' · 120 layout-units · modeldrevet Save/Reload · ingen legacy editor-runtime.</p>';
        if ($message !== '') {
            echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>';
        }

        echo '<div class="h18-clean-topbar">';
        echo '<a class="button" href="' . esc_url(admin_url('admin.php?page=' . self::MENU)) . '">← Vælg side</a>';
        echo '<a class="button" target="_blank" rel="noopener" href="' . esc_url(get_permalink($postId)) . '">Vis offentlig side</a>';
        echo '<button type="button" class="button" id="h18-clean-copy-diag" data-url="' . esc_attr(DiagnosticStore::supportUrl($postId)) . '">Kopiér diagnose-link</button>';
        echo GitHubUpdater::checkButtonHtml();
        echo '</div>';

        echo '<form id="h18-clean-save-form" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::NONCE_SAVE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '">';
        echo '<input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '">';
        echo '<input type="hidden" id="h18-clean-model-json" name="model_json" value="' . esc_attr((string) wp_json_encode($model)) . '">';
        echo '<input type="hidden" id="h18-clean-change-note" name="change_note" value="">';

        echo '<section class="h18-clean-page-shell"><strong>Header / Footer på denne side</strong><label>Header <select name="header_template_choice">';
        echo '<option value="auto"' . selected($headerChoice, 'auto', false) . '>Automatisk / standard</option><option value="none"' . selected($headerChoice, 'none', false) . '>Ingen Header</option>';
        foreach ($headerTemplates as $template) { if (!empty($template['active'])) { echo '<option value="' . esc_attr((string) $template['id']) . '"' . selected($headerChoice, (string) $template['id'], false) . '>' . esc_html((string) $template['name']) . '</option>'; } }
        echo '</select></label><label>Footer <select name="footer_template_choice">';
        echo '<option value="auto"' . selected($footerChoice, 'auto', false) . '>Automatisk / standard</option><option value="none"' . selected($footerChoice, 'none', false) . '>Ingen Footer</option>';
        foreach ($footerTemplates as $template) { if (!empty($template['active'])) { echo '<option value="' . esc_attr((string) $template['id']) . '"' . selected($footerChoice, (string) $template['id'], false) . '>' . esc_html((string) $template['name']) . '</option>'; } }
        echo '</select></label><span class="description">Header og Footer vælges uafhængigt. Theme-shell er aktiv på Visual Designer-sider; Automatisk bruger den aktive website-standard.</span></section>';

        echo '<div class="h18-clean-toolbar">';
        $isPublished = (string) $post->post_status === 'publish';
        $statusLabel = $isPublished ? 'Publiceret' : 'Kladde';
        echo '<span class="h18-vd-page-status ' . ($isPublished ? 'is-published' : 'is-draft') . '"><strong>Status:</strong> ' . esc_html($statusLabel) . '</span>';
        if ($isPublished) {
            echo '<button type="submit" class="button h18-vd-status-action" name="post_status_action" value="draft" onclick="return confirm(\'Gør siden til kladde? Den fjernes fra offentlig visning, og aktuelle Designer-ændringer gemmes samtidig.\');">Gem &amp; gør til kladde</button>';
        } elseif (current_user_can('publish_pages')) {
            echo '<button type="submit" class="button button-primary h18-vd-status-action" name="post_status_action" value="publish">Gem &amp; publicér</button>';
        }
        echo '<button type="button" class="button" id="h18-clean-undo" disabled>↶ Fortryd</button>';
        echo '<button type="button" class="button" id="h18-clean-redo" disabled>↷ Gentag</button>';
        echo '<span class="h18-clean-grid-label">120 units · 8 px lodret snap</span>';
        echo '<button type="button" class="button" id="h18-clean-preview" data-url="' . esc_attr(admin_url('admin-post.php')) . '" data-nonce="' . esc_attr(wp_create_nonce(self::NONCE_PREVIEW)) . '" data-post-id="' . esc_attr((string) $postId) . '">Forhåndsvis</button>';
        echo '<button type="button" class="button" id="h18-clean-composite-preview" data-url="' . esc_attr(admin_url('admin-post.php')) . '" data-nonce="' . esc_attr(wp_create_nonce(self::NONCE_COMPOSITE_PREVIEW)) . '" data-post-id="' . esc_attr((string) $postId) . '">Vis med Header + Footer</button>';
        echo '<button type="submit" class="button" name="after_save" value="preview" formtarget="_blank">Gem &amp; vis</button>';
        echo '<button type="submit" class="button button-primary h18-clean-save">Gem som ny version</button>';
        echo '</div>';

        echo '<div class="h18-clean-workspace">';
        echo '<aside class="h18-clean-palette"><h2>Elementer</h2>';
        foreach ([
            'section' => 'Sektion',
            'container' => 'Kasse',
            'text' => 'Tekst',
            'image' => 'Billede',
            'button' => 'Knap',
            'link' => 'Link',
            'spacer' => 'Mellemrum',
            'divider' => 'Skillelinje',
            'icon' => 'Ikon',
            'badge' => 'Badge',
            'datalist' => 'Data List',
            'table' => 'Tabel',
            'vehiclelist' => 'Køretøjsliste',
            'vehicledetail' => 'Køretøjsdetalje',
            'eventlist' => 'Eventliste',
            'eventdetail' => 'Eventdetalje',
        ] as $type => $label) {
            echo '<button type="button" draggable="true" class="button h18-clean-add" data-type="' . esc_attr($type) . '">+ ' . esc_html($label) . '</button>';
        }
        echo '<p class="description">Klik tilføjer på root. Træk et palette-element direkte til root, Sektion eller Kasse. Eksisterende elementer flyttes med ✥.</p></aside>';

        echo '<main class="h18-clean-canvas-column">';
        echo '<div id="h18-clean-canvas" class="h18-clean-surface h18-clean-root" data-parent-id=""></div>';
        echo '</main>';

        echo '<aside class="h18-clean-inspector"><h2>Inspector</h2><div id="h18-clean-inspector"><p class="description">Vælg et element på canvas.</p></div></aside>';
        echo '</div>';
        echo '</form>';

        echo '<section class="h18-clean-history"><h2>Gemte versioner</h2>';
        if (!$history) {
            echo '<p>Ingen gemte Visual Designer-versioner endnu.</p>';
        } else {
            echo '<p class="description">Hver Gem opretter en ny version. Gendan på original opretter også en ny version, så historikken aldrig overskrives.</p>';
            echo '<table class="widefat striped"><thead><tr><th>Version</th><th>Gemt</th><th>Note</th><th>Digest</th><th>Handlinger</th></tr></thead><tbody>';
            foreach (array_slice($history, 0, 20) as $entry) {
                $version = (int) ($entry['version'] ?? 0);
                echo '<tr><td><strong>v' . esc_html((string) $version) . '</strong></td>';
                echo '<td>' . esc_html((string) ($entry['savedUtc'] ?? '')) . '</td>';
                echo '<td>' . esc_html((string) ($entry['note'] ?? '')) . '</td>';
                echo '<td><code>' . esc_html(substr((string) ($entry['digest'] ?? ''), 0, 14)) . '…</code></td><td><div class="h18-clean-version-actions">';
                echo '<form method="post" target="_blank" action="' . esc_url(admin_url('admin-post.php')) . '">';
                wp_nonce_field(self::NONCE_VERSION_PREVIEW);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::VERSION_PREVIEW_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '"><input type="hidden" name="version" value="' . esc_attr((string) $version) . '">';
                echo '<button class="button" type="submit">Forhåndsvis</button></form>';
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
                wp_nonce_field(self::NONCE_RESTORE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::RESTORE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '"><input type="hidden" name="version" value="' . esc_attr((string) $version) . '">';
                echo '<button class="button" type="submit" onclick="return confirm(\'Gendan v' . esc_js((string) $version) . ' på original-siden? Den nuværende version bevares i historikken.\');">Gendan original</button></form>';
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
                wp_nonce_field(self::NONCE_RESTORE_COPY);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::RESTORE_COPY_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '"><input type="hidden" name="version" value="' . esc_attr((string) $version) . '">';
                echo '<button class="button" type="submit" onclick="return confirm(\'Opret en ny kladde som kopi af v' . esc_js((string) $version) . '? Original-siden ændres ikke.\');">Opret kopi</button></form>';
                echo '</div></td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</section></div>';
    }

    public static function save(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE_SAVE);
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            self::redirect($postId, 'error', 'Ugyldig side.');
        }
        $rawJson = isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '';
        if ($rawJson === '' || strlen($rawJson) > 2 * 1024 * 1024) {
            self::redirect($postId, 'error', 'Layoutmodellen mangler eller er for stor.');
        }
        $decoded = json_decode($rawJson, true);
        if (!is_array($decoded)) {
            self::redirect($postId, 'error', 'Layoutmodellen er ikke gyldig JSON.');
        }

        try {
            $normalized = LayoutModel::normalize($decoded);
            DiagnosticStore::append($postId, 'save_begin', [
                'currentVersion' => (int) get_post_meta($postId, LayoutModel::VERSION_META, true),
                'incoming' => DiagnosticStore::modelSummary($normalized),
            ]);
            $note = isset($_POST['change_note']) ? sanitize_text_field((string) wp_unslash($_POST['change_note'])) : '';
            TemplateLayoutModel::ensureMigrated();
            $headerChoice = sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto'));
            $footerChoice = sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto'));
            $currentVersion = max(0, (int) get_post_meta($postId, LayoutModel::VERSION_META, true));
            $sameModel = hash_equals(LayoutModel::structuralDigest(LayoutModel::get($postId)), LayoutModel::structuralDigest($normalized));
            $sameShell = TemplateLayoutModel::pageChoice($postId, 'header') === ($headerChoice !== '' ? $headerChoice : 'auto')
                && TemplateLayoutModel::pageChoice($postId, 'footer') === ($footerChoice !== '' ? $footerChoice : 'auto');
            $statusAction = sanitize_key((string) wp_unslash($_POST['post_status_action'] ?? ''));
            $desiredStatus = in_array($statusAction, ['publish', 'draft'], true) ? $statusAction : '';
            $currentPostStatus = (string) get_post_status($postId);
            $statusChanged = $desiredStatus !== '' && $desiredStatus !== $currentPostStatus;
            if ($desiredStatus === 'publish' && !current_user_can('publish_pages')) {
                throw new \RuntimeException('Du har ikke rettighed til at publicere sider.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell && !$statusChanged) {
                // A previous Designer save may already be canonical while a page cache still
                // contains older frontend HTML. Touching the page is therefore intentional
                // even on a canonical no-op save.
                self::touchFrontendPage($postId, '', $currentVersion);
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-and-shell-unchanged']);
                self::redirect($postId, 'success', 'Ingen layoutændringer siden seneste gemte version. Frontend-cache er blevet invalideret.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell) {
                $version = $currentVersion;
            } else {
                $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');
                TemplateLayoutModel::setPageChoice($postId, 'header', $headerChoice);
                TemplateLayoutModel::setPageChoice($postId, 'footer', $footerChoice);
            }
            // LayoutModel::saveVersion() writes canonical Designer data to post meta.
            // Touch the WordPress page only AFTER those writes so conventional WordPress,
            // host and plugin caches observe and purge against the new Designer state.
            self::touchFrontendPage($postId, $statusChanged ? $desiredStatus : '', $version);
            if ($statusChanged) {
                DiagnosticStore::append($postId, 'page_status_changed', ['from' => $currentPostStatus, 'to' => $desiredStatus, 'version' => $version]);
            }
            $saved = LayoutModel::get($postId);
            $incomingDigest = LayoutModel::structuralDigest($normalized);
            $savedDigest = LayoutModel::structuralDigest($saved);
            if (!hash_equals($incomingDigest, $savedDigest)) {
                throw new \RuntimeException('Save-verifikation fejlede: den gemte canonical model matcher ikke den indsendte model.');
            }
            DiagnosticStore::append($postId, 'save_result', [
                'version' => $version,
                'digest' => $savedDigest,
                'saved' => DiagnosticStore::modelSummary($saved),
            ]);
            if (isset($_POST['after_save']) && sanitize_key((string) wp_unslash($_POST['after_save'])) === 'preview') {
                $permalink = get_permalink($postId);
                if (is_string($permalink) && $permalink !== '') {
                    // The version query makes Gem & vis unambiguous even behind a cache layer
                    // that does not immediately honour a WordPress purge event.
                    wp_safe_redirect(add_query_arg('h18_vd_saved', $version, $permalink));
                    exit;
                }
            }
            $statusMessage = $statusChanged ? ($desiredStatus === 'publish' ? ' Siden er publiceret.' : ' Siden er nu kladde og ikke længere offentligt publiceret.') : '';
            self::redirect($postId, 'success', 'Visual Designer-layout gemt og verificeret som version v' . $version . '.' . $statusMessage);
        } catch (\Throwable $error) {
            DiagnosticStore::append($postId, 'save_error', ['errorType' => get_class($error), 'message' => $error->getMessage()]);
            self::redirect($postId, 'error', 'Gem fejlede: ' . $error->getMessage());
        }
    }

    public static function compositePreview(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE_COMPOSITE_PREVIEW);
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            wp_die(esc_html__('Ugyldig side.', 'visual-designer-manager'));
        }
        $decoded = json_decode(isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '', true);
        if (!is_array($decoded)) {
            wp_die(esc_html__('Preview-modellen er ikke gyldig JSON.', 'visual-designer-manager'));
        }
        try {
            $pageModel = LayoutModel::normalize($decoded);
            TemplateLayoutModel::ensureMigrated();
            $headerChoice = sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto'));
            $footerChoice = sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto'));
            $headerModel = self::templateModelForPreview('header', $headerChoice);
            $footerModel = self::templateModelForPreview('footer', $footerChoice);
            nocache_headers();
            header('Content-Type: text/html; charset=utf-8');
            echo Renderer::standaloneDocument($pageModel, $headerModel, $footerModel, 'Visual Designer · samlet preview');
            exit;
        } catch (\Throwable $error) {
            wp_die(esc_html('Samlet preview fejlede: ' . $error->getMessage()));
        }
    }

    public static function preview(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE_PREVIEW);
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            wp_die(esc_html__('Ugyldig side.', 'visual-designer-manager'));
        }
        $rawJson = isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '';
        if ($rawJson === '' || strlen($rawJson) > 2 * 1024 * 1024) {
            wp_die(esc_html__('Preview-modellen mangler eller er for stor.', 'visual-designer-manager'));
        }
        $decoded = json_decode($rawJson, true);
        if (!is_array($decoded)) {
            wp_die(esc_html__('Preview-modellen er ikke gyldig JSON.', 'visual-designer-manager'));
        }
        try {
            $normalized = LayoutModel::normalize($decoded);
            $token = strtolower(wp_generate_password(24, false, false));
            set_transient(Renderer::previewKey(get_current_user_id(), $postId, $token), $normalized, 10 * MINUTE_IN_SECONDS);
            DiagnosticStore::append($postId, 'preview_open', [
                'digest' => LayoutModel::structuralDigest($normalized),
                'state' => DiagnosticStore::modelSummary($normalized),
            ]);
            $permalink = get_permalink($postId);
            if (!is_string($permalink) || $permalink === '') {
                throw new \RuntimeException('Siden har ingen gyldig permalink.');
            }
            wp_safe_redirect(add_query_arg('h18_clean_preview', rawurlencode($token), $permalink));
            exit;
        } catch (\Throwable $error) {
            DiagnosticStore::append($postId, 'preview_error', ['errorType' => get_class($error), 'message' => $error->getMessage()]);
            wp_die(esc_html('Forhåndsvisning fejlede: ' . $error->getMessage()));
        }
    }

    public static function previewVersion(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE_VERSION_PREVIEW);
        $postId = absint($_POST['post_id'] ?? 0);
        $targetVersion = absint($_POST['version'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page' || $targetVersion <= 0) {
            wp_die(esc_html__('Ugyldig versionsanmodning.', 'visual-designer-manager'));
        }
        $target = LayoutModel::historyModel($postId, $targetVersion);
        if ($target === null) {
            wp_die(esc_html__('Den valgte Visual Designer-version findes ikke længere.', 'visual-designer-manager'));
        }
        $token = strtolower(wp_generate_password(24, false, false));
        set_transient(Renderer::previewKey(get_current_user_id(), $postId, $token), $target, 10 * MINUTE_IN_SECONDS);
        DiagnosticStore::append($postId, 'version_preview_open', ['targetVersion' => $targetVersion]);
        $permalink = get_permalink($postId);
        if (!is_string($permalink) || $permalink === '') {
            wp_die(esc_html__('Siden har ingen gyldig permalink.', 'visual-designer-manager'));
        }
        wp_safe_redirect(add_query_arg([
            'h18_clean_preview' => rawurlencode($token),
            'h18_clean_preview_version' => $targetVersion,
        ], $permalink));
        exit;
    }

    public static function restoreCopy(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE_RESTORE_COPY);
        $postId = absint($_POST['post_id'] ?? 0);
        $targetVersion = absint($_POST['version'] ?? 0);
        $source = get_post($postId);
        if (!$source instanceof \WP_Post || $source->post_type !== 'page' || $targetVersion <= 0) {
            self::redirect($postId, 'error', 'Ugyldig kopi-anmodning.');
        }
        try {
            $target = LayoutModel::historyModel($postId, $targetVersion);
            if ($target === null) {
                throw new \RuntimeException('Den valgte Visual Designer-version findes ikke længere i historikken.');
            }
            $copyId = wp_insert_post([
                'post_type' => 'page',
                'post_status' => 'draft',
                'post_title' => (string) $source->post_title . ' – kopi fra v' . $targetVersion,
                'post_content' => (string) $source->post_content,
                'post_excerpt' => (string) $source->post_excerpt,
                'post_parent' => (int) $source->post_parent,
                'menu_order' => (int) $source->menu_order,
                'post_author' => get_current_user_id(),
            ], true);
            if (is_wp_error($copyId)) {
                throw new \RuntimeException($copyId->get_error_message());
            }
            $copyId = (int) $copyId;
            $template = get_page_template_slug($postId);
            if (is_string($template) && $template !== '') {
                update_post_meta($copyId, '_wp_page_template', $template);
            }
            $thumb = get_post_thumbnail_id($postId);
            if ($thumb > 0) {
                set_post_thumbnail($copyId, $thumb);
            }
            $copyVersion = LayoutModel::saveVersion($copyId, $target, get_current_user_id(), 'Kopi fra side ' . $postId . ' · v' . $targetVersion);
            DiagnosticStore::append($postId, 'restore_copy_result', ['targetVersion' => $targetVersion, 'copyPostId' => $copyId, 'copyVersion' => $copyVersion]);
            self::redirect($copyId, 'success', 'Kopi oprettet som kladde fra v' . $targetVersion . '. Kopien starter sin egen historik ved v' . $copyVersion . '.');
        } catch (\Throwable $error) {
            DiagnosticStore::append($postId, 'restore_copy_error', ['targetVersion' => $targetVersion, 'errorType' => get_class($error), 'message' => $error->getMessage()]);
            self::redirect($postId, 'error', 'Kopi fejlede: ' . $error->getMessage());
        }
    }

    public static function restore(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE_RESTORE);
        $postId = absint($_POST['post_id'] ?? 0);
        $targetVersion = absint($_POST['version'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page' || $targetVersion <= 0) {
            self::redirect($postId, 'error', 'Ugyldig restore-anmodning.');
        }

        try {
            $target = LayoutModel::historyModel($postId, $targetVersion);
            if ($target === null) {
                throw new \RuntimeException('Den valgte Visual Designer-version findes ikke længere i historikken.');
            }
            $before = LayoutModel::get($postId);
            DiagnosticStore::append($postId, 'restore_begin', [
                'targetVersion' => $targetVersion,
                'before' => DiagnosticStore::modelSummary($before),
                'target' => DiagnosticStore::modelSummary($target),
            ]);
            $newVersion = LayoutModel::saveVersion(
                $postId,
                $target,
                get_current_user_id(),
                'Restore fra v' . $targetVersion
            );
            self::touchFrontendPage($postId, '', $newVersion);
            DiagnosticStore::append($postId, 'restore_result', [
                'targetVersion' => $targetVersion,
                'newVersion' => $newVersion,
                'saved' => DiagnosticStore::modelSummary(LayoutModel::get($postId)),
            ]);
            self::redirect($postId, 'success', 'Version v' . $targetVersion . ' restored som ny version v' . $newVersion . '.');
        } catch (\Throwable $error) {
            DiagnosticStore::append($postId, 'restore_error', ['targetVersion' => $targetVersion, 'errorType' => get_class($error), 'message' => $error->getMessage()]);
            self::redirect($postId, 'error', 'Restore fejlede: ' . $error->getMessage());
        }
    }

    private static function renderPagePicker(): void
    {
        $pages = get_pages(['sort_column' => 'post_title', 'sort_order' => 'ASC', 'post_status' => ['publish', 'draft', 'pending', 'private', 'future']]);
        echo '<div class="wrap"><h1>Visual Designer</h1><p>Vælg en WordPress-side. Der importeres intet gammelt editor-state automatisk.</p>';
        echo '<table class="widefat striped"><thead><tr><th>Side</th><th>Slug</th><th>WordPress-status</th><th>Designer-version</th><th></th></tr></thead><tbody>';
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post) {
                continue;
            }
            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);
            $statusObject = get_post_status_object((string) $page->post_status);
            $statusLabel = $statusObject ? (string) $statusObject->label : (string) $page->post_status;
            echo '<tr><td>' . esc_html((string) $page->post_title) . '</td><td><code>' . esc_html((string) $page->post_name) . '</code></td><td>' . esc_html($statusLabel) . '</td><td>' . esc_html($version > 0 ? 'v' . $version : 'Ikke gemt endnu') . '</td><td><a class="button button-primary" href="' . esc_url(admin_url('admin.php?page=' . self::MENU . '&post=' . $page->ID)) . '">Åbn designer</a></td></tr>';
        }
        echo '</tbody></table></div>';
    }

    /** @return array<string,mixed>|null */
    private static function templateModelForPreview(string $part, string $choice): ?array
    {
        $part = sanitize_key($part) === 'footer' ? 'footer' : 'header';
        $choice = sanitize_key($choice);
        $id = TemplateLayoutModel::resolveChoiceId($part, $choice);
        if ($id === '' || !TemplateLayoutModel::exists($id, $part)) { return null; }
        return TemplateLayoutModel::model($id);
    }

    /**
     * Make a Designer meta save visible through the normal WordPress post lifecycle.
     *
     * Canonical Designer data is already persisted before this method is called. The
     * subsequent wp_update_post() deliberately fires post_updated/save_post hooks so
     * WordPress and full-page cache integrations invalidate the old public rendering.
     */
    private static function touchFrontendPage(int $postId, string $desiredStatus, int $version): void
    {
        $post = get_post($postId);
        if (!$post instanceof \WP_Post || $post->post_type !== 'page') {
            throw new \RuntimeException('Frontend-cache kunne ikke invalideres: siden findes ikke længere.');
        }

        $update = ['ID' => $postId];
        if ($desiredStatus !== '') {
            $update['post_status'] = $desiredStatus;
        }

        $updatedPost = wp_update_post($update, true);
        if (is_wp_error($updatedPost)) {
            throw new \RuntimeException('Frontend-cache kunne ikke invalideres: ' . $updatedPost->get_error_message());
        }

        clean_post_cache($postId);
        do_action('h18_clean_designer_page_saved', $postId, $version, (string) get_post_status($postId));
        DiagnosticStore::append($postId, 'frontend_cache_invalidated', [
            'version' => $version,
            'status' => (string) get_post_status($postId),
            'strategy' => 'wp_update_post+clean_post_cache',
        ]);
    }

    private static function redirect(int $postId, string $status, string $message): void
    {
        $url = admin_url('admin.php?page=' . self::MENU);
        if ($postId > 0) {
            $url = add_query_arg('post', $postId, $url);
        }
        $url = add_query_arg([
            'h18_clean_status' => sanitize_key($status),
            'h18_clean_message' => rawurlencode($message),
        ], $url);
        wp_safe_redirect($url);
        exit;
    }
}
