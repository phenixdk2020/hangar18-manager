from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f'Missing required file: {path}')
    return p.read_text(encoding='utf-8')


def write(path: str, value: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')


def replace_once(path: str, old: str, new: str) -> None:
    value = read(path)
    if new in value:
        return
    if old not in value:
        raise SystemExit(f'{path}: replacement anchor missing: {old[:110]}')
    write(path, value.replace(old, new, 1))


def append_once(path: str, marker: str, addition: str) -> None:
    value = read(path)
    if marker not in value:
        write(path, value.rstrip() + '\n\n' + addition.strip() + '\n')


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
ADMIN = 'clean/hangar18-manager/src/Admin/AdminController.php'
EDITOR = 'clean/hangar18-manager/src/Admin/EditorController.php'
STATUS = 'clean/hangar18-manager/assets/admin-v0123.js'
MODEL = 'clean/hangar18-manager/src/Model/LayoutModel.php'
CORE = 'clean/hangar18-manager/assets/editor-v018-core.js'
PREVIEW_CSS = 'clean/hangar18-manager/assets/editor-v0166-foundation.css'
RENDERER = 'clean/hangar18-manager/src/Frontend/Renderer.php'

# ---------------------------------------------------------------------------
# Version / bootstrap / editor data
# ---------------------------------------------------------------------------
replace_once(PLUGIN, ' * Version: 0.1.71', ' * Version: 0.1.72')
replace_once(PLUGIN, "define('H18_CLEAN_VERSION', '0.1.71');", "define('H18_CLEAN_VERSION', '0.1.72');")
replace_once(PLUGIN,
             "require_once H18_CLEAN_DIR . 'src/Migration/CanvasSectionMigration.php';",
             "require_once H18_CLEAN_DIR . 'src/Migration/CanvasSectionMigration.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/SiteDesignHarmonizer.php';")
replace_once(PLUGIN,
             "require_once H18_CLEAN_DIR . 'src/Admin/EventAdminController.php';",
             "require_once H18_CLEAN_DIR . 'src/Admin/EventAdminController.php';\nrequire_once H18_CLEAN_DIR . 'src/Admin/GalleryAdminController.php';")
replace_once(PLUGIN,
             '    \\VisualDesignerManager\\Migration\\CanvasSectionMigration::register();',
             '    \\VisualDesignerManager\\Migration\\CanvasSectionMigration::register();\n    \\VisualDesignerManager\\Migration\\SiteDesignHarmonizer::register();')
replace_once(PLUGIN,
             '    \\VisualDesignerManager\\Admin\\EventAdminController::register();',
             '    \\VisualDesignerManager\\Admin\\EventAdminController::register();\n    \\VisualDesignerManager\\Admin\\GalleryAdminController::register();')

GALLERY_RECORDS = r'''    $galleryRecords = array_values(array_map(static function (array $item): array {
        $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
        $featuredId = absint($record['featuredMediaId'] ?? 0);
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        if ($featuredId <= 0 && $imageIds) { $featuredId = (int) $imageIds[0]; }
        $featuredUrl = $featuredId > 0 ? wp_get_attachment_image_url($featuredId, 'large') : false;
        $imageUrls = [];
        foreach (array_slice($imageIds, 0, 100) as $imageId) {
            $url = wp_get_attachment_image_url($imageId, 'large');
            if (is_string($url) && $url !== '') { $imageUrls[] = ['id' => $imageId, 'url' => $url]; }
        }
        return [
            'postId' => (int) ($item['postId'] ?? 0),
            'id' => (string) ($record['id'] ?? ''),
            'title' => (string) ($record['title'] ?? ''),
            'status' => (string) ($record['status'] ?? 'draft'),
            'sortOrder' => (int) ($record['sortOrder'] ?? 0),
            'summary' => (string) ($record['summary'] ?? ''),
            'featuredMediaId' => $featuredId,
            'featuredUrl' => is_string($featuredUrl) ? $featuredUrl : '',
            'fields' => $fields,
            'imageUrls' => $imageUrls,
        ];
    }, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('galleries', ['status' => 'all', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC'])));

'''
replace_once(PLUGIN,
             "    wp_enqueue_script(\n        'h18-clean-editor-v0144-viewport',",
             GALLERY_RECORDS + "    wp_enqueue_script(\n        'h18-clean-editor-v0144-viewport',")
replace_once(PLUGIN,
             "        'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events'),",
             "        'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events'),\n        'galleryRecords' => $galleryRecords,\n        'galleryAdminUrl' => admin_url('admin.php?page=h18-clean-gallery'),")

# ---------------------------------------------------------------------------
# Gallery Manager CRUD
# ---------------------------------------------------------------------------
write('clean/hangar18-manager/src/Admin/GalleryAdminController.php', r'''<?php

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
''')
replace_once(ADMIN,
             "add_submenu_page(self::MENU, 'Billedgalleri', 'Billedgalleri', $cap, 'h18-clean-gallery', [self::class, 'gallery']);",
             "add_submenu_page(self::MENU, 'Billedgalleri', 'Billedgalleri', $cap, 'h18-clean-gallery', [GalleryAdminController::class, 'render']);")
replace_once(STATUS,
             "'h18-clean-gallery': ['Ikke færdig', 'planned']",
             "'h18-clean-gallery': ['Klar', 'ready']")

# ---------------------------------------------------------------------------
# Home-driven theme harmonization of the six main non-home pages
# ---------------------------------------------------------------------------
write('clean/hangar18-manager/src/Migration/SiteDesignHarmonizer.php', r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class SiteDesignHarmonizer
{
    public const CONTRACT = 'VD-SITE-DESIGN-HARMONY-001';
    public const BACKUP_META = '_h18_vd_layout_pre_theme_v0172';
    public const DONE_META = '_h18_vd_theme_harmonized_v0172';
    private const TARGET_SLUGS = ['om-foreningen', 'koeretoejer-og-materiel', 'events', 'billedgalleri', 'bliv-medlem', 'kontakt'];

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'run'], 40);
    }

    public static function run(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        if ($frontId <= 0 || !metadata_exists('post', $frontId, LayoutModel::META)) { return; }
        $home = LayoutModel::get($frontId);
        if (empty($home['nodes']) || !is_array($home['nodes'])) { return; }
        $tokens = self::tokens($home);
        $referenceDigest = LayoutModel::structuralDigest($home);
        foreach (self::TARGET_SLUGS as $slug) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post || (int) $page->ID === $frontId || !metadata_exists('post', (int) $page->ID, LayoutModel::META)) { continue; }
            $postId = (int) $page->ID;
            if (metadata_exists('post', $postId, self::DONE_META)) { continue; }
            self::harmonizePage($postId, $frontId, $referenceDigest, $tokens);
        }
    }

    /** @param array<string,mixed> $tokens */
    private static function harmonizePage(int $postId, int $frontId, string $referenceDigest, array $tokens): void
    {
        $raw = get_post_meta($postId, LayoutModel::META, true);
        if (!is_array($raw)) { return; }
        $before = LayoutModel::normalize($raw);
        $beforeFingerprint = self::layoutFingerprint($before);
        $after = self::applyTokens($before, $tokens);
        $after = LayoutModel::normalize($after);
        if ($beforeFingerprint !== self::layoutFingerprint($after)) {
            return; // Styling may never alter identity, hierarchy, order or geometry.
        }
        $beforeDigest = LayoutModel::structuralDigest($before);
        $afterDigest = LayoutModel::structuralDigest($after);
        if ($beforeDigest === $afterDigest) {
            update_post_meta($postId, self::DONE_META, ['version' => H18_CLEAN_VERSION, 'referencePostId' => $frontId, 'referenceDigest' => $referenceDigest, 'changed' => false]);
            return;
        }

        $oldHistory = get_post_meta($postId, LayoutModel::HISTORY_META, true);
        $oldVersion = get_post_meta($postId, LayoutModel::VERSION_META, true);
        if (!metadata_exists('post', $postId, self::BACKUP_META)) {
            update_post_meta($postId, self::BACKUP_META, ['savedUtc' => gmdate('c'), 'digest' => $beforeDigest, 'model' => $before]);
        }
        try {
            $version = LayoutModel::saveVersion($postId, $after, get_current_user_id(), 'Design harmoniseret med Hjem (v0.1.72)');
            $stored = LayoutModel::get($postId);
            if (self::layoutFingerprint($stored) !== $beforeFingerprint || LayoutModel::structuralDigest($stored) !== $afterDigest) {
                throw new \RuntimeException('Efterkontrol af harmoniseret layout fejlede.');
            }
            update_post_meta($postId, self::DONE_META, [
                'version' => H18_CLEAN_VERSION,
                'designerVersion' => $version,
                'referencePostId' => $frontId,
                'referenceDigest' => $referenceDigest,
                'beforeDigest' => $beforeDigest,
                'afterDigest' => $afterDigest,
                'changed' => true,
            ]);
        } catch (\Throwable $error) {
            update_post_meta($postId, LayoutModel::META, $raw);
            if (metadata_exists('post', $postId, LayoutModel::HISTORY_META)) { update_post_meta($postId, LayoutModel::HISTORY_META, $oldHistory); }
            if (metadata_exists('post', $postId, LayoutModel::VERSION_META)) { update_post_meta($postId, LayoutModel::VERSION_META, $oldVersion); }
            delete_post_meta($postId, self::DONE_META);
        }
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    private static function tokens(array $model): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $sections = [];
        $container = [];
        $text = [];
        $button = [];
        $image = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            $type = (string) ($node['type'] ?? '');
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ($type === 'section' && (string) ($node['parentId'] ?? '') === '') {
                $sections[] = self::pick($props, ['background', 'radius', 'padding', 'borderWidth', 'borderColor']);
            } elseif ($type === 'container' && !$container) {
                $container = self::pick($props, ['background', 'radius', 'padding', 'borderWidth', 'borderColor']);
            } elseif ($type === 'text' && !$text) {
                $text = self::pick($props, ['textColor', 'headingColor', 'fontFamily', 'fontWeight', 'lineHeight', 'letterSpacing', 'headingFontFamily', 'headingFontWeight', 'headingLineHeight', 'headingLetterSpacing']);
            } elseif ($type === 'button' && !$button) {
                $button = self::pick($props, ['background', 'textColor', 'hoverBackground', 'hoverTextColor', 'focusColor', 'fontFamily', 'fontWeight', 'radius', 'borderWidth', 'borderColor']);
            } elseif ($type === 'image' && !$image) {
                $image = self::pick($props, ['radius', 'borderWidth', 'borderColor']);
            }
        }
        if (!$sections) { $sections[] = ['background' => '', 'radius' => 0, 'padding' => 0, 'borderWidth' => 0, 'borderColor' => '#000000']; }
        $paletteText = (string) ($text['textColor'] ?? '#30382a');
        $paletteHeading = (string) ($text['headingColor'] ?? $paletteText);
        $paletteAccent = (string) ($button['focusColor'] ?? '#c3ae83');
        $paletteButton = (string) ($button['background'] ?? '#30382a');
        return ['sections' => $sections, 'container' => $container, 'text' => $text, 'button' => $button, 'image' => $image, 'palette' => ['text' => $paletteText, 'heading' => $paletteHeading, 'accent' => $paletteAccent, 'button' => $paletteButton]];
    }

    /** @param array<string,mixed> $model @param array<string,mixed> $tokens @return array<string,mixed> */
    private static function applyTokens(array $model, array $tokens): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $sectionIndex = 0;
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            $type = (string) ($node['type'] ?? '');
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ($type === 'section' && (string) ($node['parentId'] ?? '') === '') {
                $styles = (array) $tokens['sections'];
                $style = (array) $styles[$sectionIndex % max(1, count($styles))];
                $props = self::mergeStyle($props, $style);
                $sectionIndex++;
            } elseif ($type === 'container') {
                $props = self::mergeStyle($props, (array) ($tokens['container'] ?? []));
            } elseif ($type === 'text') {
                $props = self::mergeStyle($props, (array) ($tokens['text'] ?? []));
            } elseif ($type === 'button') {
                $props = self::mergeStyle($props, (array) ($tokens['button'] ?? []));
            } elseif ($type === 'image') {
                $props = self::mergeStyle($props, (array) ($tokens['image'] ?? []));
            } elseif (in_array($type, ['vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail'], true)) {
                $palette = (array) ($tokens['palette'] ?? []);
                if (array_key_exists('textColor', $props)) { $props['textColor'] = (string) ($palette['text'] ?? $props['textColor']); }
                if (array_key_exists('accentColor', $props)) { $props['accentColor'] = (string) ($palette['accent'] ?? $props['accentColor']); }
                if (array_key_exists('cardBackground', $props) && !empty($tokens['sections'][0]['background'])) { $props['cardBackground'] = (string) $tokens['sections'][0]['background']; }
                if (array_key_exists('background', $props) && !empty($tokens['sections'][0]['background'])) { $props['background'] = (string) $tokens['sections'][0]['background']; }
            }
            $node['props'] = $props;
        }
        unset($node);
        $model['nodes'] = $nodes;
        return $model;
    }

    /** @param array<string,mixed> $source @param array<int,string> $keys @return array<string,mixed> */
    private static function pick(array $source, array $keys): array
    {
        $out = [];
        foreach ($keys as $key) { if (array_key_exists($key, $source)) { $out[$key] = $source[$key]; } }
        return $out;
    }

    /** @param array<string,mixed> $props @param array<string,mixed> $style @return array<string,mixed> */
    private static function mergeStyle(array $props, array $style): array
    {
        foreach ($style as $key => $value) { $props[(string) $key] = $value; }
        return $props;
    }

    /** @param array<string,mixed> $model */
    private static function layoutFingerprint(array $model): string
    {
        $rows = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) { continue; }
            $rows[] = [
                'id' => (string) ($node['id'] ?? ''),
                'type' => (string) ($node['type'] ?? ''),
                'parentId' => (string) ($node['parentId'] ?? ''),
                'order' => (int) ($node['order'] ?? 0),
                'geometry' => $node['geometry'] ?? [],
            ];
        }
        return hash('sha256', (string) wp_json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    }

    private function __construct() {}
}
''')

# ---------------------------------------------------------------------------
# Canonical Gallery Designer elements
# ---------------------------------------------------------------------------
replace_once(MODEL,
             "'eventlist', 'eventdetail'",
             "'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail'")
GALLERY_MODEL = r'''        if ($type === 'gallerylist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'sortOrder'), ['sortOrder', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'sortOrder') : 'sortOrder';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'galleries', 'view' => 'list', 'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit]]);
            return array_merge(['binding' => $binding, 'limit' => $limit, 'orderBy' => $orderBy, 'order' => $order, 'detailPageId' => absint($raw['detailPageId'] ?? 0), 'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3), 'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18), 'cardPadding' => self::clamp($raw['cardPadding'] ?? 12, 0, 60, 12), 'imageHeight' => self::clamp($raw['imageHeight'] ?? 220, 80, 600, 220), 'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true, 'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true, 'showCount' => array_key_exists('showCount', $raw) ? (bool) $raw['showCount'] : true, 'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true, 'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'cardRadius' => self::clamp($raw['cardRadius'] ?? 4, 0, 60, 4)], $border);
        }
        if ($type === 'gallerydetail') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? ''))); if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'galleries', 'view' => 'detail', 'recordId' => $recordId]);
            return array_merge(['binding' => $binding, 'recordId' => $recordId, 'showDescription' => array_key_exists('showDescription', $raw) ? (bool) $raw['showDescription'] : true, 'columns' => self::clamp($raw['columns'] ?? 4, 1, 6, 4), 'gap' => self::clamp($raw['gap'] ?? 12, 0, 80, 12), 'imageHeight' => self::clamp($raw['imageHeight'] ?? 220, 80, 700, 220), 'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff', 'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a', 'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83', 'padding' => self::clamp($raw['padding'] ?? 16, 0, 80, 16), 'radius' => self::clamp($raw['radius'] ?? 4, 0, 60, 4)], $border);
        }
'''
replace_once(MODEL, "        if ($type === 'image') {", GALLERY_MODEL + "\n        if ($type === 'image') {")
replace_once(EDITOR,
             "            'eventdetail' => 'Eventdetalje',",
             "            'eventdetail' => 'Eventdetalje',\n            'gallerylist' => 'Gallerioversigt',\n            'gallerydetail' => 'Albumvisning',")

replace_once(CORE,
             "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail'];",
             "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail'];")
replace_once(CORE,
             "eventlist:'Eventliste',eventdetail:'Eventdetalje'",
             "eventlist:'Eventliste',eventdetail:'Eventdetalje',gallerylist:'Gallerioversigt',gallerydetail:'Albumvisning'")
replace_once(CORE,
             "    function eventIsPast(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const edge=String(fields.end||fields.start||''); if(!edge){return false;} const timestamp=Date.parse(edge); return Number.isFinite(timestamp)&&timestamp<Date.now(); }",
             "    function eventIsPast(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const edge=String(fields.end||fields.start||''); if(!edge){return false;} const timestamp=Date.parse(edge); return Number.isFinite(timestamp)&&timestamp<Date.now(); }\n    function galleryRecords() { return Array.isArray(CFG.galleryRecords) ? CFG.galleryRecords.filter(function (record) { return record && record.id; }) : []; }\n    function galleryRecordById(recordId) { recordId=String(recordId||''); return galleryRecords().find(function(record){return String(record.id||'')===recordId;})||null; }\n    function galleryImageCount(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; return Array.isArray(fields.imageIds)?fields.imageIds.length:(Array.isArray(record&&record.imageUrls)?record.imageUrls.length:0); }")

GALLERY_JS_MODEL = r'''        if (type === 'gallerylist') {
            const orderBy=['sortOrder','title','updatedAt'].includes(String(raw.orderBy||'sortOrder'))?String(raw.orderBy||'sortOrder'):'sortOrder'; const order=String(raw.order||'ASC').toUpperCase()==='DESC'?'DESC':'ASC'; const limit=clamp(parseInt(raw.limit||50,10)||50,1,100);
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'galleries',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},limit:limit,orderBy:orderBy,order:order,detailPageId:parseInt(raw.detailPageId||0,10)||0,columns:clamp(parseInt(raw.columns||3,10)||3,1,4),cardGap:clamp(parseInt(raw.cardGap||18,10)||18,0,80),cardPadding:clamp(parseInt(raw.cardPadding||12,10)||12,0,60),imageHeight:clamp(parseInt(raw.imageHeight||220,10)||220,80,600),showImage:raw.showImage!==false,showSummary:raw.showSummary!==false,showCount:raw.showCount!==false,linkCards:raw.linkCards!==false,cardBackground:normalizeColor(raw.cardBackground||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),cardRadius:clamp(parseInt(raw.cardRadius||4,10)||4,0,60)});
        }
        if (type === 'gallerydetail') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'galleries',view:'detail',recordId:recordId,query:{status:'publish',orderBy:'sortOrder',order:'ASC',limit:50},fieldMap:{}},recordId:recordId,showDescription:raw.showDescription!==false,columns:clamp(parseInt(raw.columns||4,10)||4,1,6),gap:clamp(parseInt(raw.gap||12,10)||12,0,80),imageHeight:clamp(parseInt(raw.imageHeight||220,10)||220,80,700),background:normalizeColor(raw.background||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),padding:clamp(parseInt(raw.padding||16,10)||16,0,80),radius:clamp(parseInt(raw.radius||4,10)||4,0,60)});
        }
'''
core = read(CORE)
if "if (type === 'gallerylist')" not in core:
    anchor = "        if (type === 'image') {"
    pos = core.find(anchor)
    if pos < 0: raise SystemExit('editor core: normalize image anchor missing')
    write(CORE, core[:pos] + GALLERY_JS_MODEL + '\n' + core[pos:])
replace_once(CORE,
             'eventlist: 38, eventdetail: 46',
             'eventlist: 38, eventdetail: 46, gallerylist: 40, gallerydetail: 52')

GALLERY_PREVIEW = r'''        } else if (node.type === 'gallerylist') {
            wrap.classList.add('h18-clean-node-preview--gallerylist'); const records=galleryRecords().filter(function(record){return String(record.status||'')==='publish';}).slice(0,node.props.limit||50); const grid=document.createElement('div'); grid.className='h18-vd-gallery-list-preview'; grid.style.gridTemplateColumns='repeat('+String(node.props.columns||3)+',minmax(0,1fr))'; grid.style.gap=String(node.props.cardGap||18)+'px'; if(!records.length){grid.textContent='Ingen publicerede album · opret dem under Manager → Billedgalleri';} records.forEach(function(record){const card=document.createElement('article');card.className='h18-vd-gallery-card-preview';card.style.padding=String(node.props.cardPadding||12)+'px';card.style.borderRadius=String(node.props.cardRadius||4)+'px';card.style.background=node.props.cardBackground||'#ffffff';card.style.color=node.props.textColor||'#30382a';if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||220)+'px';card.appendChild(img);}const title=document.createElement('strong');title.textContent=String(record.title||'Album');card.appendChild(title);if(node.props.showCount!==false){const count=document.createElement('small');count.textContent=String(galleryImageCount(record))+' billeder';count.style.color=node.props.accentColor||'#c3ae83';card.appendChild(count);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);card.appendChild(p);}grid.appendChild(card);});wrap.appendChild(grid);
        } else if (node.type === 'gallerydetail') {
            wrap.classList.add('h18-clean-node-preview--gallerydetail'); const record=galleryRecordById(node.props.recordId)||galleryRecords().find(function(item){return String(item.status||'')==='publish';})||null; const box=document.createElement('article');box.className='h18-vd-gallery-detail-preview';box.style.background=node.props.background||'#ffffff';box.style.color=node.props.textColor||'#30382a';box.style.padding=String(node.props.padding||16)+'px';box.style.borderRadius=String(node.props.radius||4)+'px';if(!record){box.textContent='Vælg et album i Inspector eller opret et under Manager → Billedgalleri';wrap.appendChild(box);}else{const h=document.createElement('h3');h.textContent=String(record.title||'Album');box.appendChild(h);const images=document.createElement('div');images.className='h18-vd-gallery-images-preview';images.style.gridTemplateColumns='repeat('+String(node.props.columns||4)+',minmax(0,1fr))';images.style.gap=String(node.props.gap||12)+'px';(Array.isArray(record.imageUrls)?record.imageUrls:[]).forEach(function(item){const img=document.createElement('img');img.src=String(item&&item.url||'');img.alt='';img.style.height=String(node.props.imageHeight||220)+'px';if(img.src){images.appendChild(img);}});box.appendChild(images);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDescription!==false&&fields.description){const desc=document.createElement('div');desc.innerHTML=richPreviewHtml(String(fields.description));box.appendChild(desc);}wrap.appendChild(box);}
'''
replace_once(CORE,
             "        } else if (node.type === 'image') {",
             GALLERY_PREVIEW + "\n        } else if (node.type === 'image') {")

GALLERY_INSPECTOR = r'''        } else if (node.type === 'gallerylist') {
            html += '<div class="h18-vd-menu-group"><h3>Gallerioversigt</h3><p class="description">Data kommer fra Manager → Billedgalleri. Kun publicerede album vises på frontend.</p><label>Album-detaljeside<select data-field="galleryDetailPageId"><option value="0">Ingen link / vælg senere</option>'+(Array.isArray(CFG.pages)?CFG.pages.map(function(page){const id=parseInt(page.id||0,10)||0;return '<option value="'+id+'"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>';}).join(''):'')+'</select></label><div class="h18-clean-field-grid"><label>Kolonner<input data-field="galleryColumns" type="number" min="1" max="4" value="'+String(node.props.columns||3)+'"></label><label>Maks. album<input data-field="galleryLimit" type="number" min="1" max="100" value="'+String(node.props.limit||50)+'"></label><label>Sortér<select data-field="galleryOrderBy"><option value="sortOrder"'+(node.props.orderBy==='sortOrder'?' selected':'')+'>Sortering</option><option value="title"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value="updatedAt"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field="galleryOrder"><option value="ASC"'+(node.props.order==='ASC'?' selected':'')+'>Stigende</option><option value="DESC"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Afstand<input data-field="galleryCardGap" type="number" min="0" max="80" value="'+String(node.props.cardGap||18)+'"></label><label>Padding<input data-field="galleryCardPadding" type="number" min="0" max="60" value="'+String(node.props.cardPadding||12)+'"></label><label>Billedhøjde<input data-field="galleryImageHeight" type="number" min="80" max="600" value="'+String(node.props.imageHeight||220)+'"></label><label>Hjørner<input data-field="galleryCardRadius" type="number" min="0" max="60" value="'+String(node.props.cardRadius||4)+'"></label></div><div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="galleryCardBackground" type="color" value="'+escapeHtml(node.props.cardBackground||'#ffffff')+'"></label><label>Tekst<input data-field="galleryTextColor" type="color" value="'+escapeHtml(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="galleryAccentColor" type="color" value="'+escapeHtml(node.props.accentColor||'#c3ae83')+'"></label></div><label class="h18-clean-checkbox"><input data-field="galleryShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis cover</label><label class="h18-clean-checkbox"><input data-field="galleryShowCount" type="checkbox"'+(node.props.showCount!==false?' checked':'')+'> Vis antal billeder</label><label class="h18-clean-checkbox"><input data-field="galleryShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="galleryLinkCards" type="checkbox"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside</label><p><a class="button" href="'+escapeHtml(String(CFG.galleryAdminUrl||'#'))+'">Åbn Billedgalleri</a></p></div>';
        } else if (node.type === 'gallerydetail') {
            const records=galleryRecords(); html += '<div class="h18-vd-menu-group"><h3>Albumvisning</h3><label>Preview-album<select data-field="galleryRecordId"><option value="">Fra URL / første publicerede</option>'+records.map(function(record){return '<option value="'+escapeHtml(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Album'))+'</option>';}).join('')+'</select></label><p class="description">Frontend kan vælge album via <code>?h18_gallery=record-id</code>.</p><div class="h18-clean-field-grid"><label>Kolonner<input data-field="galleryColumns" type="number" min="1" max="6" value="'+String(node.props.columns||4)+'"></label><label>Afstand<input data-field="galleryGap" type="number" min="0" max="80" value="'+String(node.props.gap||12)+'"></label><label>Billedhøjde<input data-field="galleryImageHeight" type="number" min="80" max="700" value="'+String(node.props.imageHeight||220)+'"></label><label>Padding<input data-field="galleryPadding" type="number" min="0" max="80" value="'+String(node.props.padding||16)+'"></label></div><div class="h18-clean-field-grid"><label>Baggrund<input data-field="galleryBackground" type="color" value="'+escapeHtml(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="galleryTextColor" type="color" value="'+escapeHtml(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="galleryAccentColor" type="color" value="'+escapeHtml(node.props.accentColor||'#c3ae83')+'"></label></div><label class="h18-clean-checkbox"><input data-field="galleryShowDescription" type="checkbox"'+(node.props.showDescription!==false?' checked':'')+'> Vis albumbeskrivelse</label><p><a class="button" href="'+escapeHtml(String(CFG.galleryAdminUrl||'#'))+'">Åbn Billedgalleri</a></p></div>';
'''
replace_once(CORE,
             "        } else if (node.type === 'image') {\n            html += '<div class=\"h18-vd-menu-group\"><h3>Billede</h3>',",
             GALLERY_INSPECTOR + "\n        } else if (node.type === 'image') {\n            html += '<div class=\"h18-vd-menu-group\"><h3>Billede</h3>',")

GALLERY_HANDLERS = r'''                else if (field === 'galleryDetailPageId') { current.props.detailPageId=parseInt(control.value||0,10)||0; }
                else if (field === 'galleryColumns') { current.props.columns=clamp(parseInt(control.value||(current.type==='gallerydetail'?4:3),10)||(current.type==='gallerydetail'?4:3),1,current.type==='gallerydetail'?6:4); }
                else if (field === 'galleryLimit') { current.props.limit=clamp(parseInt(control.value||50,10)||50,1,100); if(current.props.binding&&current.props.binding.query){current.props.binding.query.limit=current.props.limit;} }
                else if (field === 'galleryOrderBy') { current.props.orderBy=['sortOrder','title','updatedAt'].includes(control.value)?control.value:'sortOrder'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.orderBy=current.props.orderBy;} }
                else if (field === 'galleryOrder') { current.props.order=control.value==='DESC'?'DESC':'ASC'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.order=current.props.order;} }
                else if (field === 'galleryCardGap') { current.props.cardGap=clamp(parseInt(control.value||18,10)||18,0,80); }
                else if (field === 'galleryCardPadding') { current.props.cardPadding=clamp(parseInt(control.value||12,10)||12,0,60); }
                else if (field === 'galleryGap') { current.props.gap=clamp(parseInt(control.value||12,10)||12,0,80); }
                else if (field === 'galleryImageHeight') { current.props.imageHeight=clamp(parseInt(control.value||(current.type==='gallerydetail'?220:220),10)||220,80,current.type==='gallerydetail'?700:600); }
                else if (field === 'galleryCardRadius') { current.props.cardRadius=clamp(parseInt(control.value||4,10)||4,0,60); }
                else if (field === 'galleryPadding') { current.props.padding=clamp(parseInt(control.value||16,10)||16,0,80); }
                else if (field === 'galleryShowImage') { current.props.showImage=!!control.checked; }
                else if (field === 'galleryShowSummary') { current.props.showSummary=!!control.checked; }
                else if (field === 'galleryShowCount') { current.props.showCount=!!control.checked; }
                else if (field === 'galleryLinkCards') { current.props.linkCards=!!control.checked; }
                else if (field === 'galleryCardBackground') { current.props.cardBackground=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'galleryBackground') { current.props.background=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'galleryTextColor') { current.props.textColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'galleryAccentColor') { current.props.accentColor=normalizeColor(control.value||'#c3ae83'); }
                else if (field === 'galleryRecordId') { current.props.recordId=String(control.value||''); if(current.props.binding){current.props.binding.recordId=current.props.recordId;} }
                else if (field === 'galleryShowDescription') { current.props.showDescription=!!control.checked; }
'''
replace_once(CORE,
             "                else if (field === 'eventShowDescription') { current.props.showDescription=!!control.checked; }\n                else if (field === 'buttonText')",
             "                else if (field === 'eventShowDescription') { current.props.showDescription=!!control.checked; }\n" + GALLERY_HANDLERS + "                else if (field === 'buttonText')")

append_once(PREVIEW_CSS, '.h18-vd-gallery-list-preview', '.h18-vd-gallery-list-preview{display:grid;width:100%;box-sizing:border-box}.h18-vd-gallery-card-preview{display:flex;flex-direction:column;gap:6px;min-width:0;border:1px solid #dcdcde;box-sizing:border-box;overflow:hidden}.h18-vd-gallery-card-preview img{display:block;width:100%;object-fit:cover;max-width:none}.h18-vd-gallery-card-preview p,.h18-vd-gallery-detail-preview p,.h18-vd-gallery-detail-preview h3{margin:0}.h18-vd-gallery-detail-preview{display:flex;flex-direction:column;gap:12px;width:100%;box-sizing:border-box}.h18-vd-gallery-images-preview{display:grid;width:100%;box-sizing:border-box}.h18-vd-gallery-images-preview img{display:block;width:100%;object-fit:cover;max-width:none}.h18-clean-node-preview--gallerylist,.h18-clean-node-preview--gallerydetail{overflow:auto}')

# ---------------------------------------------------------------------------
# Frontend Gallery list/detail
# ---------------------------------------------------------------------------
replace_once(RENDERER,
             "        echo '.h18-vd-live-shell,.h18-vd-live-shell-part",
             "        echo '.h18-clean-front-gallery-list{display:grid;width:100%;box-sizing:border-box}.h18-clean-front-gallery-card{display:flex;flex-direction:column;gap:8px;min-width:0;box-sizing:border-box;text-decoration:none;color:inherit;overflow:hidden}.h18-clean-front-gallery-card img{display:block;width:100%;max-width:none;object-fit:cover}.h18-clean-front-gallery-card h3,.h18-clean-front-gallery-card p{margin:0}.h18-clean-front-gallery-count{font-weight:600}.h18-clean-front-gallery-detail{box-sizing:border-box}.h18-clean-front-gallery-images{display:grid;width:100%;box-sizing:border-box;margin-top:14px}.h18-clean-front-gallery-images a{display:block;min-width:0}.h18-clean-front-gallery-images img{display:block;width:100%;max-width:none;object-fit:cover}.h18-clean-front-gallery-description{margin-top:16px}@media(max-width:782px){.h18-clean-front-gallery-list,.h18-clean-front-gallery-images{grid-template-columns:1fr!important}}';\n        echo '.h18-vd-live-shell,.h18-vd-live-shell-part")
GALLERY_RENDERER = r'''        if ($type === 'gallerylist') {
            $binding=isset($props['binding'])&&is_array($props['binding'])?$props['binding']:[];$query=isset($binding['query'])&&is_array($binding['query'])?$binding['query']:[];$query['status']='publish';$query['limit']=max(1,min(100,(int)($props['limit']??($query['limit']??50))));$query['orderBy']=in_array((string)($props['orderBy']??($query['orderBy']??'sortOrder')),['sortOrder','title','updatedAt'],true)?(string)($props['orderBy']??($query['orderBy']??'sortOrder')):'sortOrder';$query['order']=strtoupper((string)($props['order']??($query['order']??'ASC')))==='DESC'?'DESC':'ASC';
            $records=ModuleStore::listRecords('galleries',$query);$columns=max(1,min(4,(int)($props['columns']??3)));$gap=max(0,min(80,(int)($props['cardGap']??18)));$padding=max(0,min(60,(int)($props['cardPadding']??12)));$imageHeight=max(80,min(600,(int)($props['imageHeight']??220)));$cardBg=sanitize_hex_color((string)($props['cardBackground']??'#ffffff'))?:'#ffffff';$textColor=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a';$accent=sanitize_hex_color((string)($props['accentColor']??'#c3ae83'))?:'#c3ae83';$radius=max(0,min(60,(int)($props['cardRadius']??4)));$detailPageId=absint($props['detailPageId']??0);$detailBase=$detailPageId>0?get_permalink($detailPageId):false;$cards='';
            foreach($records as $item){$record=isset($item['record'])&&is_array($item['record'])?$item['record']:[];if((string)($record['status']??'')!=='publish'){continue;}$fields=isset($record['fields'])&&is_array($record['fields'])?$record['fields']:[];$imageIds=isset($fields['imageIds'])&&is_array($fields['imageIds'])?array_values(array_filter(array_map('absint',$fields['imageIds']))):[];$featuredId=absint($record['featuredMediaId']??0);if($featuredId<=0&&$imageIds){$featuredId=(int)$imageIds[0];}$recordId=(string)($record['id']??'');$href=is_string($detailBase)&&$detailBase!==''&&!empty($props['linkCards'])?add_query_arg('h18_gallery',rawurlencode($recordId),$detailBase):'';$tag=$href!==''?'a':'article';$hrefAttr=$href!==''?' href="'.esc_url($href).'"':'';$image='';if(!empty($props['showImage'])&&$featuredId>0){$url=wp_get_attachment_image_url($featuredId,'large');if(is_string($url)&&$url!==''){$image='<img src="'.esc_url($url).'" alt="'.esc_attr((string)($record['title']??'')).'" style="height:'.esc_attr((string)$imageHeight).'px">';}}$count=!empty($props['showCount'])?'<span class="h18-clean-front-gallery-count" style="color:'.esc_attr($accent).'">'.esc_html((string)count($imageIds)).' billeder</span>':'';$summary=!empty($props['showSummary'])&&trim((string)($record['summary']??''))!==''?'<p>'.esc_html((string)$record['summary']).'</p>':'';$cardStyle='background:'.$cardBg.';color:'.$textColor.';padding:'.$padding.'px;border-radius:'.$radius.'px;';$cards.='<'.$tag.' class="h18-clean-front-gallery-card"'.$hrefAttr.' style="'.esc_attr($cardStyle).'">'.$image.'<h3>'.esc_html((string)($record['title']??'Album')).'</h3>'.$count.$summary.'</'.$tag.'>';}
            if($cards===''&&self::$forceStandaloneCss){$cards='<p>Ingen publicerede album.</p>';}$listStyle=$style.$borderStyle.$spacingStyle.'grid-template-columns:repeat('.$columns.',minmax(0,1fr));gap:'.$gap.'px;';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-gallery-list" style="'.esc_attr($listStyle).'">'.$cards.'</div>';
        }
        if ($type === 'gallerydetail') {
            $recordId=strtolower(trim((string)($props['recordId']??'')));if($recordId===''){$recordId=strtolower(trim(sanitize_text_field((string)wp_unslash($_GET['h18_gallery']??''))));}if($recordId!==''&&!preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/',$recordId)){$recordId='';}if($recordId===''){$message=self::$forceStandaloneCss?'Vælg et album i Inspector eller brug ?h18_gallery=record-id.':'Vælg et album fra oversigten.';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-gallery-detail" style="'.esc_attr($style.$borderStyle.$spacingStyle).'"><p>'.esc_html($message).'</p></div>';}
            $found=ModuleStore::findByRecordId('galleries',$recordId);$record=is_array($found)&&isset($found['record'])&&is_array($found['record'])?$found['record']:null;$allowDraft=self::$forceStandaloneCss&&current_user_can('edit_pages');if($record===null||((string)($record['status']??'draft')!=='publish'&&!$allowDraft)){return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-gallery-detail" style="'.esc_attr($style.$borderStyle.$spacingStyle).'"><p>Albummet findes ikke eller er ikke publiceret.</p></div>';}$fields=isset($record['fields'])&&is_array($record['fields'])?$record['fields']:[];$imageIds=isset($fields['imageIds'])&&is_array($fields['imageIds'])?array_values(array_filter(array_map('absint',$fields['imageIds']))):[];$background=sanitize_hex_color((string)($props['background']??'#ffffff'))?:'#ffffff';$textColor=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a';$accent=sanitize_hex_color((string)($props['accentColor']??'#c3ae83'))?:'#c3ae83';$padding=max(0,min(80,(int)($props['padding']??16)));$columns=max(1,min(6,(int)($props['columns']??4)));$gap=max(0,min(80,(int)($props['gap']??12)));$imageHeight=max(80,min(700,(int)($props['imageHeight']??220)));$images='';foreach($imageIds as $imageId){$large=wp_get_attachment_image_url($imageId,'large');$full=wp_get_attachment_image_url($imageId,'full');if(!is_string($large)||$large===''){continue;}$href=is_string($full)&&$full!==''?$full:$large;$images.='<a href="'.esc_url($href).'" target="_blank" rel="noopener"><img src="'.esc_url($large).'" alt="'.esc_attr((string)get_post_meta($imageId,'_wp_attachment_image_alt',true)).'" style="height:'.esc_attr((string)$imageHeight).'px"></a>';}$grid=$images!==''?'<div class="h18-clean-front-gallery-images" style="grid-template-columns:repeat('.esc_attr((string)$columns).',minmax(0,1fr));gap:'.esc_attr((string)$gap).'px">'.$images.'</div>':'';$description=!empty($props['showDescription'])&&trim((string)($fields['description']??''))!==''?'<div class="h18-clean-front-gallery-description">'.wp_kses_post((string)$fields['description']).'</div>':'';$detailStyle=$style.$borderStyle.$spacingStyle.$radiusStyle.'background:'.$background.';color:'.$textColor.';padding:'.$padding.'px;';return '<article id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-gallery-detail" style="'.esc_attr($detailStyle).'"><h2>'.esc_html((string)($record['title']??'Album')).'</h2><p class="h18-clean-front-gallery-count" style="color:'.esc_attr($accent).'">'.esc_html((string)count($imageIds)).' billeder</p>'.$grid.$description.'</article>';
        }
'''
replace_once(RENDERER, "        if ($type === 'image') {", GALLERY_RENDERER + "\n        if ($type === 'image') {")

# ---------------------------------------------------------------------------
# Documentation / release history / backlog
# ---------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(isinstance(row, dict) and row.get('version') == '0.1.72' for row in versions):
    versions.insert(0, {
        'version': '0.1.72',
        'date': '2026-09-01',
        'items': [
            'VD-GALLERY-MODULE-001: Billedgalleri er nu et fuldt modul oven på ModuleStore.',
            'Album har cover, beskrivelse, sortering og Media Library attachment-IDer.',
            'Designer har Gallerioversigt og Albumvisning med genbrugelig detailrouting via ?h18_gallery=<record-id>.',
            'VD-SITE-DESIGN-HARMONY-001 harmoniserer de seks øvrige hovedsider ud fra Hjem uden at ændre indhold eller geometri.',
            'Hver harmoniseret side får rå backup og en ny Designer-version med rollback via historikken.',
        ],
    })
    history['versions'] = versions
    write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

append_once('CLEAN-DESIGN-MANUAL.md', '## Billedgalleri – designprincip', '''## Billedgalleri – designprincip

**VD-GALLERY-MODULE-001** gør album til dynamiske records i den fælles ModuleStore. `Gallerioversigt` viser publicerede album, mens `Albumvisning` viser ét album fra et fast record-ID eller `?h18_gallery=<record-id>`. Layout-JSON indeholder aldrig billedbytes; kun modulbinding og design. Billeder forbliver WordPress Media Library attachments.

## Site-design harmonisering

**VD-SITE-DESIGN-HARMONY-001** bruger den aktive Designer-Hjem-side som visuel reference for `Om foreningen`, `Køretøjer og materiel`, `Events`, `Billedgalleri`, `Bliv medlem` og `Kontakt`. Harmonisering må kun ændre designprops: root-Sektion/Kasse-baggrund, padding, hjørner og rammer samt typografi, farver, knap- og billedstyling. Node-ID, type, hierarchy, order, geometri og indhold må ikke ændres. Hjems sektionstyper genbruges i rækkefølge, så de øvrige sider får samme tema uden at blive identiske kopier af Hjem.''')
append_once('CLEAN-TECHNICAL-MANUAL.md', 'VD-GALLERY-MODULE-001', '''### VD-GALLERY-MODULE-001
- `galleries` bruger `ModuleRegistry`, `ModuleRecord`, `ModuleBinding` og `ModuleStore`.
- `GalleryAdminController` gemmer cover som `featuredMediaId` og albumbilleder som `fields.imageIds`.
- `gallerylist` og `gallerydetail` er canonical Designer-elementer i PHP/JS og frontend Renderer.
- Public frontend accepterer kun `publish`; detailrouting bruger `?h18_gallery=<record-id>`.

### VD-SITE-DESIGN-HARMONY-001
- `SiteDesignHarmonizer` kører én gang pr. målside på `admin_init` efter Canvas/Section migration.
- Reference er WordPress' aktive `page_on_front` og kun hvis siden har canonical Designer-layout.
- Mål-slugs er eksplicit: `om-foreningen`, `koeretoejer-og-materiel`, `events`, `billedgalleri`, `bliv-medlem`, `kontakt`.
- Før ændring gemmes `_h18_vd_layout_pre_theme_v0172`; efter ændring oprettes en normal `LayoutModel::saveVersion()`.
- En fingerprint af ID/type/parent/order/geometri skal være identisk før og efter. Fejl ruller layout/historik/version tilbage.
- `_h18_vd_theme_harmonized_v0172` gør migreringen idempotent.''')
append_once('CLEAN-USER-MANUAL.md', 'Sådan bruger du Billedgalleriet', '''## Sådan bruger du Billedgalleriet
1. Gå til **Visual Designer Manager → Billedgalleri** og opret et album.
2. Vælg cover, flere billeder fra Media Library, titel, beskrivelse, sortering og status.
3. Tilføj **Gallerioversigt** på Billedgalleri-siden og vælg kolonner, kortdesign og en detaljeside.
4. Tilføj **Albumvisning** på detaljesiden. Frontend vælger album via `?h18_gallery=<record-id>`; Inspector kan vælge et fast preview-album.
5. Kladder og arkiverede album vises ikke offentligt.

## Automatisk designharmonisering i v0.1.72
Når v0.1.72 indlæses i WordPress Admin, bruger Visual Designer Manager den aktive **Hjem**-side som designreference for Om foreningen, Køretøjer og materiel, Events, Billedgalleri, Bliv medlem og Kontakt. Tekster, billeder, elementplacering og størrelser bevares. Kun tema-/designværdier synkroniseres. Før hver ændring gemmes en backup, og harmoniseringen bliver en ny Designer-version, så siden kan gendannes fra versionshistorikken.''')

backlog = read('docs/clean-backlog-v0100.md')
backlog = backlog.replace('**Statusdato:** 31. august 2026', '**Statusdato:** 1. september 2026')
backlog = backlog.replace('**Aktuel release:** v0.1.71', '**Aktuel release:** v0.1.72')
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.71', '## Aktuel milepælsstatus · v0.1.72')
if 'VD-GALLERY-MODULE-001 — IMPLEMENTERET I v0.1.72' not in backlog:
    backlog = backlog.replace('- **VD-EVENT-MODULE-001 — IMPLEMENTERET I v0.1.71:** Events har Manager-CRUD, dato/tid, sted, billede, kommende/afholdte regler og Designer list/detail-binding.', '- **VD-EVENT-MODULE-001 — IMPLEMENTERET I v0.1.71:** Events har Manager-CRUD, dato/tid, sted, billede, kommende/afholdte regler og Designer list/detail-binding.\n- **VD-GALLERY-MODULE-001 — IMPLEMENTERET I v0.1.72:** Album har CRUD, cover, Media Library-liste og Designer oversigt/detail.\n- **VD-SITE-DESIGN-HARMONY-001 — IMPLEMENTERET I v0.1.72:** de seks øvrige hovedsider harmoniseres sikkert med Hjem med backup og versionering.')
backlog = backlog.replace('4. **v0.1.72 – Billedgalleri — NÆSTE:** album, Media Library-referencer, sortering, cover og genbrugeligt Designer galleri/album-element.\n5. **Efter modulerne:** samlet data-/module-migrering fra legacy, med side-by-side QA før cutover.', '4. **v0.1.72 – Billedgalleri + site-design — FÆRDIG:** album, Media Library-referencer, sortering, cover, Designer oversigt/detail og sikker Hjem-baseret designharmonisering.\n5. **v0.1.73 – Modul-cutover/migrering — NÆSTE:** samlet legacy data-/module-migrering med side-by-side QA før cutover.')
backlog = backlog.replace('### VD-GALLERY-MODULE-001 — NÆSTE', '### VD-GALLERY-MODULE-001 — FÆRDIG I v0.1.72')
backlog += '\n\n### VD-SITE-DESIGN-HARMONY-001 — FÆRDIG I v0.1.72\n- Hjem er visuel reference; seks navngivne hovedsider er mål.\n- Kun designprops ændres; indhold, hierarchy og geometri bevares byte-/fingerprint-logisk.\n- Backup-meta + ny Designer-version fører til reversibel migration.\n\n## v0.1.72 Billedgalleri/design – QA-gate\n1. Opret et album som Kladde med cover, mindst 5 billeder og beskrivelse; reload og verificér stabile attachment-IDer.\n2. Publicér mindst tre album og test sortering samt Gallerioversigt.\n3. Test Albumvisning via `?h18_gallery=<record-id>`; Kladde/Arkiveret må ikke vises offentligt.\n4. Verificér at albumdata kun indeholder attachment-IDer, ikke billedbytes.\n5. Efter opdatering: verificér backup + ny Designer-version for hver målside der blev harmoniseret.\n6. Sammenlign node-ID, hierarchy og Desktop/Laptop/Tablet/Mobil-geometri før/efter; de skal være identiske.\n7. Vis alle seks sider og kontrollér visuelt samme farver, typografi, sektion/kasse-stil og knapper som Hjem.\n'
write('docs/clean-backlog-v0100.md', backlog)

write('docs/v0172-status.md', '''# Visual Designer Manager v0.1.72 status\n\nRelease candidate: **Billedgalleri + Site Design Harmony**.\n\n- VD-GALLERY-MODULE-001: GalleryAdminController, Gallery List/Detail, public-only frontend, attachment-ID storage.\n- VD-SITE-DESIGN-HARMONY-001: Hjem-baseret one-time styling af de seks øvrige hovedsider med backup, Designer-version og geometri-fingerprint.\n- Manualer, releasehistorik og backlog er synkroniseret.\n''')
write('clean-release-notes.html', '''<h2>0.1.72 – Billedgalleri + Site Design Harmony</h2>\n<ul>\n<li><strong>VD-GALLERY-MODULE-001:</strong> Billedgalleri har nu album-CRUD, cover, beskrivelse og Media Library-billeder.</li>\n<li>Designer har Gallerioversigt og Albumvisning med detailrouting via <code>?h18_gallery=&lt;record-id&gt;</code>.</li>\n<li><strong>VD-SITE-DESIGN-HARMONY-001:</strong> Om, Køretøjer, Events, Billedgalleri, Bliv medlem og Kontakt harmoniseres automatisk med Hjems tema.</li>\n<li>Harmonisering ændrer ikke indhold eller geometri og gemmer backup + ny Designer-version.</li>\n<li>Næste planlagte version er v0.1.73 – modul-cutover/migrering.</li>\n</ul>\n''')

print('Applied Visual Designer Manager v0.1.72 Gallery + Site Design Harmony candidate.')
