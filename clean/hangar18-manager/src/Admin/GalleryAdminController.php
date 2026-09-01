<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Modules\ModuleStore;

final class GalleryAdminController
{
    public const PAGE = 'h18-clean-gallery';
    private const SAVE_ACTION = 'h18_clean_save_gallery';
    private const DELETE_ACTION = 'h18_clean_delete_gallery';
    private const SAVE_NONCE = 'h18_clean_save_gallery';
    private const DELETE_NONCE = 'h18_clean_delete_gallery';

    public static function register(): void
    {
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'saveGallery']);
        add_action('admin_post_' . self::DELETE_ACTION, [self::class, 'deleteGallery']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function enqueue(string $hook): void
    {
        if (strpos($hook, self::PAGE) === false || !current_user_can('edit_pages')) { return; }
        wp_enqueue_media();
        wp_enqueue_script('h18-vd-module-media', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.js', [], H18_CLEAN_VERSION, true);
        wp_enqueue_style('h18-vd-gallery-admin', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.css', [], H18_CLEAN_VERSION);
    }

    public static function render(): void
    {
        self::guard();
        $editId = isset($_GET['edit']) ? absint($_GET['edit']) : 0;
        $record = $editId > 0 ? ModuleStore::get($editId) : null;
        if ($record !== null && (string) ($record['module'] ?? '') !== 'galleries') { $record = null; $editId = 0; }
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));
        echo '<div class="wrap h18-clean-admin"><h1>Billedgalleri</h1><p class="description">Album gemmes som canonical records i den fælles ModuleStore. Billeder forbliver WordPress Media Library-attachments; albumdata gemmer kun attachment-IDer.</p>';
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }
        self::renderList($editId);
        self::renderEditor($editId, $record);
        echo '</div>';
    }

    private static function renderList(int $editId): void
    {
        $items = ModuleStore::listRecords('galleries', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC']);
        echo '<h2>Albumoversigt</h2>';
        if (!$items) { echo '<p>Ingen album endnu.</p>'; return; }
        echo '<table class="widefat striped"><thead><tr><th>Album</th><th>Billeder</th><th>Status</th><th>Sortering</th><th>Record-ID</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($items as $item) {
            $postId = (int) ($item['postId'] ?? 0);
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? $fields['imageIds'] : [];
            echo '<tr' . ($editId === $postId ? ' class="is-active"' : '') . '><td><strong>' . esc_html((string) ($record['title'] ?? 'Album')) . '</strong></td><td>' . esc_html((string) count($imageIds)) . '</td><td>' . esc_html(self::statusLabel((string) ($record['status'] ?? 'draft'))) . '</td><td>' . esc_html((string) ((int) ($record['sortOrder'] ?? 0))) . '</td><td><code>' . esc_html((string) ($record['id'] ?? '')) . '</code></td><td>';
            echo '<a class="button button-small" href="' . esc_url(admin_url('admin.php?page=' . self::PAGE . '&edit=' . $postId)) . '">Redigér</a> <form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
            wp_nonce_field(self::DELETE_NONCE);
            echo '<input type="hidden" name="action" value="' . esc_attr(self::DELETE_ACTION) . '"><input type="hidden" name="record_post_id" value="' . esc_attr((string) $postId) . '"><button type="submit" class="button button-small button-link-delete" onclick="return confirm(\'Slet albummet permanent? Billederne i Media Library slettes ikke.\');">Slet</button></form></td></tr>';
        }
        echo '</tbody></table>';
    }

    /** @param array<string,mixed>|null $record */
    private static function renderEditor(int $postId, ?array $record): void
    {
        $fields = $record !== null && is_array($record['fields'] ?? null) ? $record['fields'] : [];
        $title = (string) ($record['title'] ?? '');
        $status = (string) ($record['status'] ?? 'draft');
        $summary = (string) ($record['summary'] ?? '');
        $sortOrder = (int) ($record['sortOrder'] ?? 0);
        $featuredId = absint($record['featuredMediaId'] ?? 0);
        $description = (string) ($fields['description'] ?? '');
        $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        echo '<hr><h2>' . ($postId > 0 ? 'Redigér album' : 'Opret album') . '</h2><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::SAVE_NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '"><input type="hidden" name="record_post_id" value="' . esc_attr((string) $postId) . '"><div class="h18-vd-vehicle-layout"><div>';
        echo '<label><strong>Albumtitel</strong><input class="widefat" required type="text" name="title" value="' . esc_attr($title) . '"></label><label><strong>Kort beskrivelse</strong><textarea class="widefat" rows="3" name="summary">' . esc_textarea($summary) . '</textarea></label><label><strong>Beskrivelse</strong>';
        wp_editor($description, 'h18_gallery_description', ['textarea_name' => 'description', 'textarea_rows' => 8, 'media_buttons' => false, 'teeny' => true]);
        echo '</label><label><strong>Album-billeder</strong><input id="h18-gallery-images" type="hidden" name="image_ids" value="' . esc_attr(implode(',', $imageIds)) . '"></label><p><button type="button" class="button h18-vd-media-pick" data-target="h18-gallery-images" data-multiple="1">Vælg billeder</button> <button type="button" class="button h18-vd-media-clear" data-target="h18-gallery-images">Ryd billeder</button></p><div class="h18-vd-media-preview" data-media-preview="h18-gallery-images">' . self::imagePreview($imageIds) . '</div></div><aside>';
        echo '<label><strong>Status</strong><select class="widefat" name="status"><option value="draft"' . selected($status, 'draft', false) . '>Kladde</option><option value="publish"' . selected($status, 'publish', false) . '>Publiceret</option><option value="archive"' . selected($status, 'archive', false) . '>Arkiveret</option></select></label><label><strong>Sortering</strong><input class="widefat" type="number" name="sort_order" value="' . esc_attr((string) $sortOrder) . '"></label><label><strong>Cover</strong><input id="h18-gallery-featured" type="hidden" name="featured_media_id" value="' . esc_attr((string) $featuredId) . '"></label><p><button type="button" class="button h18-vd-media-pick" data-target="h18-gallery-featured">Vælg cover</button> <button type="button" class="button h18-vd-media-clear" data-target="h18-gallery-featured">Ryd</button></p><div class="h18-vd-media-preview" data-media-preview="h18-gallery-featured">' . self::imagePreview($featuredId > 0 ? [$featuredId] : []) . '</div><p><button type="submit" class="button button-primary">' . ($postId > 0 ? 'Gem album' : 'Opret album') . '</button>'; if ($postId > 0) { echo ' <a class="button" href="' . esc_url(admin_url('admin.php?page=' . self::PAGE)) . '">Annullér</a>'; } echo '</p></aside></div></form>';
    }

    public static function saveGallery(): void
    {
        self::guard();
        check_admin_referer(self::SAVE_NONCE);
        $postId = absint($_POST['record_post_id'] ?? 0);
        $title = sanitize_text_field((string) wp_unslash($_POST['title'] ?? ''));
        if ($title === '') { self::redirect('error', 'Albummet skal have en titel.'); }
        $imageIds = self::mediaIds((string) wp_unslash($_POST['image_ids'] ?? ''));
        $featuredId = absint($_POST['featured_media_id'] ?? 0);
        if ($featuredId <= 0 && $imageIds) { $featuredId = (int) $imageIds[0]; }
        $raw = [
            'title' => $title,
            'status' => sanitize_key((string) ($_POST['status'] ?? 'draft')),
            'sortOrder' => (int) ($_POST['sort_order'] ?? 0),
            'featuredMediaId' => $featuredId,
            'summary' => sanitize_textarea_field((string) wp_unslash($_POST['summary'] ?? '')),
            'fields' => [
                'description' => wp_kses_post((string) wp_unslash($_POST['description'] ?? '')),
                'imageIds' => $imageIds,
            ],
        ];
        $result = ModuleStore::save('galleries', $raw, $postId);
        if (is_wp_error($result)) { self::redirect('error', $result->get_error_message()); }
        self::redirect('ok', $postId > 0 ? 'Albummet er gemt.' : 'Albummet er oprettet.');
    }

    public static function deleteGallery(): void
    {
        self::guard();
        check_admin_referer(self::DELETE_NONCE);
        $postId = absint($_POST['record_post_id'] ?? 0);
        $result = ModuleStore::delete($postId);
        if (is_wp_error($result) || !$result) { self::redirect('error', is_wp_error($result) ? $result->get_error_message() : 'Albummet kunne ikke slettes.'); }
        self::redirect('ok', 'Albummet er slettet. Billederne er bevaret i Media Library.');
    }

    /** @return array<int,int> */
    private static function mediaIds(string $value): array
    {
        $ids = [];
        foreach (preg_split('/[^0-9]+/', $value) ?: [] as $part) {
            $id = absint($part);
            if ($id > 0) { $ids[$id] = $id; }
            if (count($ids) >= 500) { break; }
        }
        return array_values($ids);
    }

    /** @param array<int,int> $ids */
    private static function imagePreview(array $ids): string
    {
        $html = '';
        foreach (array_slice(array_values(array_unique(array_filter(array_map('absint', $ids)))), 0, 30) as $id) {
            $src = wp_get_attachment_image_url($id, 'thumbnail');
            if (is_string($src) && $src !== '') { $html .= '<img src="' . esc_url($src) . '" alt="">'; }
        }
        return $html !== '' ? $html : '<span class="description">Ingen billeder valgt</span>';
    }

    private static function statusLabel(string $status): string
    {
        return ['publish' => 'Publiceret', 'archive' => 'Arkiveret', 'draft' => 'Kladde'][$status] ?? 'Kladde';
    }

    private static function redirect(string $status, string $message): void
    {
        wp_safe_redirect(add_query_arg(['page' => self::PAGE, 'vd_status' => $status, 'vd_message' => $message], admin_url('admin.php')));
        exit;
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_pages')) { wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager')); }
    }

    private function __construct() {}
}
