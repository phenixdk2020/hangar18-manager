<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

use Hangar18\Clean\Diagnostics\DiagnosticStore;
use Hangar18\Clean\Frontend\Renderer;
use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Update\GitHubUpdater;

final class EditorController
{
    private const MENU = 'h18-clean-editor';
    private const SAVE_ACTION = 'h18_clean_save';
    private const RESTORE_ACTION = 'h18_clean_restore';
    private const PREVIEW_ACTION = 'h18_clean_preview';
    private const NONCE_SAVE = 'h18_clean_save';
    private const NONCE_RESTORE = 'h18_clean_restore';
    private const NONCE_PREVIEW = 'h18_clean_preview';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);
        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);
        add_action('admin_post_' . self::PREVIEW_ACTION, [self::class, 'preview']);
    }

    public static function menu(): void
    {
        add_menu_page(
            'Hangar18 Designer',
            'Hangar18 Designer',
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
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
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
        $model = LayoutModel::get($postId);
        $history = array_reverse(LayoutModel::history($postId));
        $status = isset($_GET['h18_clean_status']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_status'])) : '';
        $message = isset($_GET['h18_clean_message']) ? sanitize_text_field((string) wp_unslash($_GET['h18_clean_message'])) : '';

        echo '<div class="wrap h18-clean-admin">';
        echo '<h1>Hangar18 Designer · ' . esc_html((string) $post->post_title) . '</h1>';
        echo '<p class="description">Clean editor ' . esc_html(H18_CLEAN_VERSION) . ' · 120 layout-units · modeldrevet Save/Reload · ingen legacy editor-runtime.</p>';
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

        echo '<div class="h18-clean-toolbar">';
        echo '<button type="button" class="button" id="h18-clean-undo" disabled>↶ Fortryd</button>';
        echo '<button type="button" class="button" id="h18-clean-redo" disabled>↷ Gentag</button>';
        echo '<span class="h18-clean-grid-label">120 units · 8 px lodret snap</span>';
        echo '<button type="button" class="button" id="h18-clean-preview" data-url="' . esc_attr(admin_url('admin-post.php')) . '" data-nonce="' . esc_attr(wp_create_nonce(self::NONCE_PREVIEW)) . '" data-post-id="' . esc_attr((string) $postId) . '">Forhåndsvis</button>';
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
            echo '<p>Ingen gemte clean-versioner endnu.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Version</th><th>Gemt</th><th>Note</th><th>Digest</th><th>Restore</th></tr></thead><tbody>';
            foreach (array_slice($history, 0, 20) as $entry) {
                $version = (int) ($entry['version'] ?? 0);
                echo '<tr><td><strong>v' . esc_html((string) $version) . '</strong></td>';
                echo '<td>' . esc_html((string) ($entry['savedUtc'] ?? '')) . '</td>';
                echo '<td>' . esc_html((string) ($entry['note'] ?? '')) . '</td>';
                echo '<td><code>' . esc_html(substr((string) ($entry['digest'] ?? ''), 0, 14)) . '…</code></td><td>';
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-clean-restore-form">';
                wp_nonce_field(self::NONCE_RESTORE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::RESTORE_ACTION) . '">';
                echo '<input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '">';
                echo '<input type="hidden" name="version" value="' . esc_attr((string) $version) . '">';
                echo '<button class="button" type="submit" onclick="return confirm(\'Restore clean version v' . esc_js((string) $version) . '? Den nuværende gemte version ligger fortsat i historikken.\');">Restore</button>';
                echo '</form></td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</section></div>';
    }

    public static function save(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
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
            $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gem fra clean editor');
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
                    wp_safe_redirect($permalink);
                    exit;
                }
            }
            self::redirect($postId, 'success', 'Clean layout gemt og verificeret som version v' . $version . '.');
        } catch (\Throwable $error) {
            DiagnosticStore::append($postId, 'save_error', ['errorType' => get_class($error), 'message' => $error->getMessage()]);
            self::redirect($postId, 'error', 'Gem fejlede: ' . $error->getMessage());
        }
    }

    public static function preview(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
        check_admin_referer(self::NONCE_PREVIEW);
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            wp_die(esc_html__('Ugyldig side.', 'hangar18-manager-clean'));
        }
        $rawJson = isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '';
        if ($rawJson === '' || strlen($rawJson) > 2 * 1024 * 1024) {
            wp_die(esc_html__('Preview-modellen mangler eller er for stor.', 'hangar18-manager-clean'));
        }
        $decoded = json_decode($rawJson, true);
        if (!is_array($decoded)) {
            wp_die(esc_html__('Preview-modellen er ikke gyldig JSON.', 'hangar18-manager-clean'));
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

    public static function restore(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
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
                throw new \RuntimeException('Den valgte clean-version findes ikke længere i historikken.');
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
        $pages = get_pages(['sort_column' => 'post_title', 'sort_order' => 'ASC']);
        echo '<div class="wrap"><h1>Hangar18 Designer</h1><p>Vælg en WordPress-side. Der importeres intet gammelt editor-state automatisk.</p>';
        echo '<table class="widefat striped"><thead><tr><th>Side</th><th>Slug</th><th>Clean version</th><th></th></tr></thead><tbody>';
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post) {
                continue;
            }
            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);
            echo '<tr><td>' . esc_html((string) $page->post_title) . '</td><td><code>' . esc_html((string) $page->post_name) . '</code></td><td>' . esc_html($version > 0 ? 'v' . $version : 'Ikke clean endnu') . '</td><td><a class="button button-primary" href="' . esc_url(admin_url('admin.php?page=' . self::MENU . '&post=' . $page->ID)) . '">Åbn designer</a></td></tr>';
        }
        echo '</tbody></table></div>';
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
