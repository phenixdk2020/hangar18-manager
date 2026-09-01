from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f'Missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    if new and new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one replacement anchor, found {count}: {old[:140]}')
    write(rel, value.replace(old, new, 1))


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
RENDERER = 'clean/hangar18-manager/src/Frontend/Renderer.php'
EDITOR = 'clean/hangar18-manager/src/Admin/EditorController.php'
UPDATER = 'clean/hangar18-manager/src/Update/GitHubUpdater.php'
HISTORY = 'clean/hangar18-manager/release-history.json'
BACKLOG = 'docs/clean-backlog-v0100.md'
RELEASE = '.github/workflows/visual-designer-release.yml'
COLLECTION = 'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php'

replace_once(PLUGIN, ' * Version: 0.1.73', ' * Version: 0.1.74')
replace_once(PLUGIN, "define('H18_CLEAN_VERSION', '0.1.73');", "define('H18_CLEAN_VERSION', '0.1.74');")
replace_once(PLUGIN,
             "require_once H18_CLEAN_DIR . 'src/Frontend/Renderer.php';",
             "require_once H18_CLEAN_DIR . 'src/Frontend/CollectionPageRenderer.php';\nrequire_once H18_CLEAN_DIR . 'src/Frontend/Renderer.php';")

write(COLLECTION, r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Modules\ModuleStore;

/**
 * v0.1.74 collection-page cutover.
 *
 * The three historical Hangar18 collection pages are data modules, not fixed
 * 8px Designer canvases. Their main content therefore flows naturally with
 * record count while Header/Footer remain owned by ThemeShell.
 */
final class CollectionPageRenderer
{
    /** @return string|null */
    public static function render(int $postId): ?string
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        if (!in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true)) {
            return null;
        }

        $title = trim((string) get_the_title($postId));
        if ($title === '') {
            $title = $slug === 'events' ? 'Events' : ($slug === 'billedgalleri' ? 'Billedgalleri' : 'Køretøjer og materiel');
        }

        if ($slug === 'events') {
            $detail = self::requestRecordId('h18_event');
            $body = $detail !== '' ? self::eventDetail($postId, $detail, $title) : self::events($postId, $title);
        } elseif ($slug === 'billedgalleri') {
            $detail = self::requestRecordId('h18_gallery');
            $body = $detail !== '' ? self::galleryDetail($postId, $detail, $title) : self::galleries($postId, $title);
        } else {
            $detail = self::requestRecordId('h18_vehicle');
            $body = $detail !== '' ? self::vehicleDetail($postId, $detail, $title) : self::vehicles($postId, $title);
        }

        return self::style() . $body;
    }

    public static function supports(int $postId): bool
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        return in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true);
    }

    private static function events(int $postId, string $title): string
    {
        $records = ModuleStore::listRecords('events', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'start', 'order' => 'ASC']);
        $upcoming = [];
        $past = [];
        $now = current_time('timestamp');
        foreach ($records as $item) {
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $start = self::dateTimeTimestamp((string) ($fields['start'] ?? ''));
            $end = self::dateTimeTimestamp((string) ($fields['end'] ?? ''));
            $edge = $end > 0 ? $end : $start;
            if ($edge > 0 && $edge < $now) { $past[] = $record; } else { $upcoming[] = $record; }
        }
        usort($upcoming, static fn(array $a, array $b): int => self::eventStart($a) <=> self::eventStart($b));
        usort($past, static fn(array $a, array $b): int => self::eventStart($b) <=> self::eventStart($a));

        $html = self::openPage('events', $title);
        $html .= '<section class="h18-module-section"><h2>Kommende arrangementer</h2>' . self::eventGrid($postId, $upcoming, 'Ingen kommende arrangementer.') . '</section>';
        $html .= '<section class="h18-module-section"><h2>Tidligere arrangementer</h2>' . self::eventGrid($postId, $past, 'Ingen tidligere arrangementer.') . '</section>';
        return $html . '</main>';
    }

    /** @param array<int,array<string,mixed>> $records */
    private static function eventGrid(int $postId, array $records, string $empty): string
    {
        if (!$records) { return '<p class="h18-module-empty">' . esc_html($empty) . '</p>'; }
        $html = '<div class="h18-module-card-grid h18-module-event-grid">';
        foreach ($records as $record) {
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_event', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-event-card">' . self::image($record, 'h18-module-card-image', 220, 140);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Event')) . '</h3>';
            $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? ''));
            $location = trim((string) ($fields['location'] ?? ''));
            if ($meta !== '' || $location !== '') {
                $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>';
            }
            $summary = trim((string) ($record['summary'] ?? ''));
            if ($summary !== '') { $html .= '<p>' . esc_html($summary) . '</p>'; }
            $html .= '<a class="h18-module-more" href="' . esc_url($url) . '">Læs mere →</a></div></article>';
        }
        return $html . '</div>';
    }

    private static function galleries(int $postId, string $title): string
    {
        $records = ModuleStore::listRecords('galleries', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC']);
        $html = self::openPage('galleries', $title) . '<section class="h18-module-section"><h2>Køretøjer</h2>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen publicerede album endnu.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-gallery-grid">';
        foreach ($records as $item) {
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $imageIds = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
            $cover = absint($record['featuredMediaId'] ?? 0); if ($cover <= 0 && $imageIds) { $cover = (int) $imageIds[0]; }
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_gallery', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-gallery-card">' . self::imageId($cover, (string) ($record['title'] ?? ''), 'h18-module-card-image', 245, 150);
            $html .= '<div class="h18-module-card-body"><h3><a href="' . esc_url($url) . '">' . esc_html((string) ($record['title'] ?? 'Album')) . '</a></h3>';
            $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<p>' . wp_kses_post($description) . '</p>'; }
            $count = count($imageIds); $html .= '<p class="h18-module-count"><strong>' . esc_html((string) $count) . ' ' . ($count === 1 ? 'billede' : 'billeder') . '</strong></p></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function vehicles(int $postId, string $title): string
    {
        $records = ModuleStore::listRecords('vehicles', ['status' => 'publish', 'limit' => 100, 'orderBy' => 'sortOrder', 'order' => 'ASC']);
        $html = self::openPage('vehicles', $title);
        $html .= '<section class="h18-module-section"><h2>Historisk materiel</h2><p class="h18-module-intro">Her finder du foreningens dokumenterede køretøjer og øvrige militærhistoriske materiel.</p>';
        if (!$records) { return $html . '<p class="h18-module-empty">Ingen publicerede køretøjer endnu.</p></section></main>'; }
        $html .= '<div class="h18-module-card-grid h18-module-vehicle-grid">';
        foreach ($records as $item) {
            $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
            if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $id = (string) ($record['id'] ?? '');
            $url = add_query_arg('h18_vehicle', rawurlencode($id), get_permalink($postId));
            $html .= '<article class="h18-module-card h18-module-vehicle-card">' . self::image($record, 'h18-module-card-image', 235, 150);
            $html .= '<div class="h18-module-card-body"><h3>' . esc_html((string) ($record['title'] ?? 'Køretøj')) . '</h3>';
            $rows = [];
            $category = trim((string) ($fields['category'] ?? '')); if ($category !== '') { $rows[] = ['Type', $category]; }
            foreach (isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [] as $attribute) {
                if (!is_array($attribute) || empty($attribute['enabled'])) { continue; }
                $value = self::attributeValue($attribute['value'] ?? ''); if ($value === '') { continue; }
                $label = trim((string) ($attribute['label'] ?? $attribute['key'] ?? '')); if ($label === '') { continue; }
                if (strcasecmp($label, 'Type') === 0 && $category !== '') { continue; }
                $rows[] = [$label, $value];
            }
            if ($rows) {
                $html .= '<table class="h18-module-spec-table"><tbody>';
                foreach (array_slice($rows, 0, 10) as $row) { $html .= '<tr><th>' . esc_html($row[0]) . '</th><td>' . esc_html($row[1]) . '</td></tr>'; }
                $html .= '</tbody></table>';
            }
            $html .= '<a class="h18-module-more" href="' . esc_url($url) . '">Se køretøjet →</a></div></article>';
        }
        return $html . '</div></section></main>';
    }

    private static function eventDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('events', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('events detail', (string) ($record['title'] ?? $pageTitle));
        $html .= '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Events</a></p>' . self::image($record, 'h18-module-detail-image', 900, 420);
        $meta = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? '')); $location = trim((string) ($fields['location'] ?? ''));
        if ($meta !== '' || $location !== '') { $html .= '<p class="h18-module-meta"><strong>' . esc_html($meta) . '</strong>' . ($location !== '' ? ' · ' . esc_html($location) : '') . '</p>'; }
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        return $html . '</main>';
    }

    private static function galleryDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('galleries', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : []; $ids = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
        $html = self::openPage('galleries detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Billedgalleri</a></p>';
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        $html .= '<div class="h18-module-image-grid">'; foreach ($ids as $imageId) { $html .= self::imageId($imageId, (string) ($record['title'] ?? ''), 'h18-module-gallery-image', 320, 220); } return $html . '</div></main>';
    }

    private static function vehicleDetail(int $postId, string $id, string $pageTitle): string
    {
        $found = ModuleStore::findByRecordId('vehicles', $id); $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($record === null || (string) ($record['status'] ?? '') !== 'publish') { return self::notFound($postId, $pageTitle); }
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $html = self::openPage('vehicles detail', (string) ($record['title'] ?? $pageTitle)) . '<p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage til Køretøjer</a></p>' . self::image($record, 'h18-module-detail-image', 900, 420);
        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class="h18-module-detail-text">' . wp_kses_post($description) . '</div>'; }
        return $html . '</main>';
    }

    private static function notFound(int $postId, string $pageTitle): string
    {
        return self::openPage('detail', $pageTitle) . '<p>Indholdet findes ikke eller er ikke publiceret.</p><p><a class="h18-module-back" href="' . esc_url(get_permalink($postId)) . '">← Tilbage</a></p></main>';
    }

    private static function openPage(string $class, string $title): string
    {
        return '<main class="h18-module-page h18-module-page-' . esc_attr(sanitize_html_class($class)) . '"><h1>' . esc_html($title) . '</h1>';
    }

    /** @param array<string,mixed> $record */
    private static function image(array $record, string $class, int $width, int $height): string
    {
        return self::imageId(absint($record['featuredMediaId'] ?? 0), (string) ($record['title'] ?? ''), $class, $width, $height);
    }

    private static function imageId(int $id, string $alt, string $class, int $width, int $height): string
    {
        if ($id <= 0) { return ''; }
        $url = wp_get_attachment_image_url($id, 'large'); if (!is_string($url) || $url === '') { return ''; }
        return '<img class="' . esc_attr($class) . '" src="' . esc_url($url) . '" alt="' . esc_attr($alt) . '" width="' . esc_attr((string) $width) . '" height="' . esc_attr((string) $height) . '">';
    }

    private static function requestRecordId(string $key): string
    {
        $value = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET[$key] ?? ''))));
        return preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $value) ? $value : '';
    }

    /** @param array<string,mixed> $record */
    private static function eventStart(array $record): int
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $time = self::dateTimeTimestamp((string) ($fields['start'] ?? '')); return $time > 0 ? $time : PHP_INT_MAX;
    }

    private static function dateTimeTimestamp(string $value): int
    {
        $value = trim($value); if ($value === '') { return 0; }
        try { return (new \DateTimeImmutable($value, wp_timezone()))->getTimestamp(); } catch (\Throwable $error) { return 0; }
    }

    private static function eventDateLabel(string $start, string $end): string
    {
        $startTs = self::dateTimeTimestamp($start); if ($startTs <= 0) { return ''; }
        $label = wp_date('d-m-Y', $startTs, wp_timezone()); $endTs = self::dateTimeTimestamp($end);
        if ($endTs > 0 && wp_date('Y-m-d', $endTs, wp_timezone()) !== wp_date('Y-m-d', $startTs, wp_timezone())) { $label .= ' – ' . wp_date('d-m-Y', $endTs, wp_timezone()); }
        return $label;
    }

    private static function attributeValue($value): string
    {
        if (is_bool($value)) { return $value ? 'Ja' : 'Nej'; }
        if (is_array($value) || is_object($value)) { return ''; }
        return trim(wp_strip_all_tags((string) $value));
    }

    private static function style(): string
    {
        return '<style id="h18-module-page-v0174">'
            . '.h18-module-page{width:90%;max-width:none;margin:0 auto;padding:42px 0 32px;box-sizing:border-box;color:#30382a;font-family:Arial,Helvetica,sans-serif}'
            . '.h18-module-page h1{margin:0 0 28px;font-size:32px;line-height:1.15;color:#30382a}.h18-module-section{margin:0}.h18-module-section+.h18-module-section{margin-top:30px}.h18-module-section h2{margin:0 0 18px;font-size:28px;line-height:1.2;color:#151329}.h18-module-intro{margin:-10px 0 22px;font-size:14px}'
            . '.h18-module-card-grid{display:grid;justify-content:start;align-items:start;gap:12px}.h18-module-event-grid{grid-template-columns:repeat(auto-fill,220px)}.h18-module-gallery-grid{grid-template-columns:repeat(auto-fill,245px)}.h18-module-vehicle-grid{grid-template-columns:repeat(auto-fill,235px)}'
            . '.h18-module-card{overflow:hidden;border:1px solid #d9d6ca;border-radius:5px;background:#f2f0e7;color:#30382a;box-sizing:border-box;box-shadow:0 1px 2px rgba(0,0,0,.04)}.h18-module-card-image{display:block;width:100%;height:150px;max-width:none;object-fit:cover;margin:0}.h18-module-event-card .h18-module-card-image{height:140px}.h18-module-card-body{padding:12px}.h18-module-card h3{margin:0 0 5px;font-size:18px;line-height:1.15;color:#30382a}.h18-module-card h3 a{color:inherit;text-decoration:none}.h18-module-card p{margin:5px 0;font-size:13px;line-height:1.35}.h18-module-meta{font-size:12px!important}.h18-module-count{margin-top:7px!important}.h18-module-more,.h18-module-back{display:inline-block;margin-top:7px;color:#843d19;font-weight:700;font-size:12px;text-decoration:none}.h18-module-more:hover,.h18-module-more:focus,.h18-module-back:hover,.h18-module-back:focus{text-decoration:underline}'
            . '.h18-module-spec-table{width:100%;margin:7px 0 4px;border-collapse:collapse;font-size:12px;line-height:1.35}.h18-module-spec-table th,.h18-module-spec-table td{padding:6px 5px;border-bottom:1px solid #d9d6ca;text-align:left;vertical-align:top}.h18-module-spec-table th{width:42%;background:#e7e1d2;font-weight:700}.h18-module-empty{margin:0 0 20px}.h18-module-detail-image{display:block;width:min(900px,100%);height:auto;max-height:520px;object-fit:cover;margin:16px 0}.h18-module-detail-text{max-width:900px;line-height:1.55}.h18-module-image-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:18px}.h18-module-gallery-image{display:block;width:100%;height:220px;object-fit:cover}'
            . '@media(max-width:782px){.h18-module-page{width:calc(100% - 32px);padding:28px 0 24px}.h18-module-page h1{font-size:28px;margin-bottom:22px}.h18-module-section h2{font-size:24px}.h18-module-card-grid{grid-template-columns:1fr!important}.h18-module-card{width:100%}.h18-module-card-image{height:auto;aspect-ratio:16/10}.h18-module-spec-table{font-size:13px}}'
            . '</style>';
    }

    private function __construct() {}
}
''')

# Known collection slugs bypass the fixed-row page canvas and render as flow modules.
replace_once(RENDERER,
             "        $postId = get_the_ID();\n",
             "        $postId = get_the_ID();\n        $collectionPage = CollectionPageRenderer::render($postId);\n        if ($collectionPage !== null) {\n            return ThemeShell::enabled() ? self::renderLiveShell($postId, $collectionPage) : $collectionPage;\n        }\n")

# Version history loader: release-history.json is an object containing a versions array.
replace_once(UPDATER,
             "        $rows = [];\n        foreach ($decoded as $row) {",
             "        $sourceRows = isset($decoded['versions']) && is_array($decoded['versions']) ? $decoded['versions'] : $decoded;\n        $rows = [];\n        foreach ($sourceRows as $row) {")

# Let a canonical no-op pass the mandatory change-note guard so EditorController can report it as info.
replace_once(UPDATER,
             "        $postId = absint($_POST['post_id'] ?? 0);\n        $url = admin_url('admin.php?page=h18-clean-editor');",
             "        $postId = absint($_POST['post_id'] ?? 0);\n        if ($postId > 0 && self::isNoopDesignerSave($postId)) {\n            return;\n        }\n        $url = admin_url('admin.php?page=h18-clean-editor');")

noop_helper = r'''
    private static function isNoopDesignerSave(int $postId): bool
    {
        try {
            $json = (string) wp_unslash($_POST['model_json'] ?? '');
            $decoded = json_decode($json, true);
            if (!is_array($decoded)) { return false; }
            $normalized = \VisualDesignerManager\Model\LayoutModel::normalize($decoded);
            $currentVersion = max(0, (int) get_post_meta($postId, \VisualDesignerManager\Model\LayoutModel::VERSION_META, true));
            if ($currentVersion <= 0) { return false; }
            $sameModel = hash_equals(
                \VisualDesignerManager\Model\LayoutModel::structuralDigest(\VisualDesignerManager\Model\LayoutModel::get($postId)),
                \VisualDesignerManager\Model\LayoutModel::structuralDigest($normalized)
            );
            \VisualDesignerManager\Model\TemplateLayoutModel::ensureMigrated();
            $headerChoice = sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto')) ?: 'auto';
            $footerChoice = sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto')) ?: 'auto';
            $sameShell = \VisualDesignerManager\Model\TemplateLayoutModel::pageChoice($postId, 'header') === $headerChoice
                && \VisualDesignerManager\Model\TemplateLayoutModel::pageChoice($postId, 'footer') === $footerChoice;
            $statusAction = sanitize_key((string) wp_unslash($_POST['post_status_action'] ?? ''));
            $statusChanged = in_array($statusAction, ['publish', 'draft'], true) && $statusAction !== (string) get_post_status($postId);
            return $sameModel && $sameShell && !$statusChanged;
        } catch (\Throwable $error) {
            return false;
        }
    }

'''
updater = read(UPDATER)
if 'private static function isNoopDesignerSave' not in updater:
    anchor = '    public static function manualCheck(): void\n'
    if anchor not in updater: raise SystemExit(f'{UPDATER}: helper insertion anchor missing')
    updater = updater.replace(anchor, noop_helper + anchor, 1)
    write(UPDATER, updater)

# Save feedback: success, no-op/info and failure are visually/semantically distinct.
replace_once(EDITOR,
             "echo '<div class=\"notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible\"><p>' . esc_html($message) . '</p></div>';",
             "echo '<div class=\"notice ' . ($status === 'error' ? 'notice-error' : ($status === 'info' ? 'notice-info' : 'notice-success')) . ' is-dismissible\"><p>' . esc_html($message) . '</p></div>';")
replace_once(EDITOR,
             "self::redirect($postId, 'success', 'Ingen layoutændringer siden seneste gemte version. Frontend-cache er blevet invalideret.');",
             "self::redirect($postId, 'info', 'Ingen ændringer at gemme.');")
replace_once(EDITOR,
             "self::redirect($postId, 'success', 'Visual Designer-layout gemt og verificeret som version v' . $version . '.' . $statusMessage);",
             "self::redirect($postId, 'success', 'Siden er gemt. Version v' . $version . ' er oprettet.' . $statusMessage);")
replace_once(EDITOR,
             "self::redirect($postId, 'error', 'Gem fejlede: ' . $error->getMessage());",
             "self::redirect($postId, 'error', 'Siden kunne ikke gemmes: ' . $error->getMessage());")

# History, notes and project status.
history = json.loads(read(HISTORY))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.74' for row in versions):
    versions.insert(0, {
        'version': '0.1.74',
        'date': '2026-09-01',
        'items': [
            'VD-MODULE-CUTOVER-001: Events, Billedgalleri og Køretøjer og materiel rendres som tre dynamiske flow-modulsider efter _old-referencerne.',
            'Events opdeles automatisk i Kommende arrangementer og Tidligere arrangementer; album- og køretøjskort er kompakte og indholdsdrevne.',
            'BUG-23: Versionshistorik læser nu release-history.json-formatets versions-array korrekt.',
            'BUG-24: Gem viser tydelig besked for gemt, ingen ændringer og reel gemmefejl.'
        ],
    })
history['versions'] = versions
write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '''<h2>0.1.74 – Modul-cutover</h2>\n<ul>\n<li><strong>VD-MODULE-CUTOVER-001:</strong> Events, Billedgalleri og Køretøjer og materiel er nu tre indholdsdrevne flow-modulsider efter de originale <code>_old</code>-referencer.</li>\n<li>Events opdeles automatisk i kommende og tidligere arrangementer med kompakte kort, billeder, dato/sted og Læs mere.</li>\n<li>Billedgalleri viser kompakte albumkort med cover, beskrivelse og billedantal; Køretøjer viser billede, tekniske data og Se køretøjet.</li>\n<li>De tre modulsider bruger naturlig indholdshøjde i stedet for faste 8-px canvas-rækker; global Header/Footer kommer fortsat fra Visual Designer Manager.</li>\n<li><strong>BUG-23:</strong> Versionshistorikken kan igen læses. <strong>BUG-24:</strong> Gem viser særskilt status for gemt, ingen ændringer og fejl.</li>\n</ul>\n''')

backlog = read(BACKLOG)
backlog = backlog.replace('**Aktuel release:** v0.1.73', '**Aktuel release:** v0.1.74', 1)
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.73', '## Aktuel milepælsstatus · v0.1.74', 1)
line = '- **VD-MODULE-CUTOVER-001 — IMPLEMENTERET I v0.1.74:** Events, Billedgalleri og Køretøjer/materiel bruger dynamisk flow-rendering efter `_old`-referencerne; Header/Footer forbliver globale.\n'
marker = '- **VD-EDITOR-FRONTEND-PARITY-001 — IMPLEMENTERET I v0.1.73:** editor-chrome ligger som overlay og påvirker ikke længere den visuelle nodegeometri for sider, Header eller Footer.\n'
if line not in backlog and marker in backlog:
    backlog = backlog.replace(marker, marker + line, 1)
backlog = backlog.replace('6. **v0.1.74 – Modul-cutover/migrering — NÆSTE:** samlet legacy data-/module-migrering med side-by-side QA før cutover.', '6. **v0.1.74 – Modul-cutover — FÆRDIG:** de tre dynamiske samlingssider følger `_old`-layoutet og har flow-højde; versionshistorik og Save-feedback er rettet.', 1)
write(BACKLOG, backlog)

write('docs/v0174-status.md', '''# Visual Designer Manager v0.1.74\n\nStatus: release candidate\n\n## VD-MODULE-CUTOVER-001\n- `events`, `billedgalleri` og `koeretoejer-og-materiel` er dedikerede ModuleStore-sider.\n- `_old`-screenshots er visuel reference for kort, overskrifter, tekniske data og spacing.\n- Modulerne bruger almindeligt dokumentflow, så recordantal bestemmer højden og Footeren følger efter indholdet.\n- ThemeShell ejer fortsat Header/Footer.\n- Eventdato afgør automatisk Kommende/Tidligere; historiske records slettes ikke.\n\n## BUG-23 / BUG-24\n- Release-history loader understøtter canonical `{\"versions\":[...]}`.\n- Side-save viser `Siden er gemt`, `Ingen ændringer at gemme` eller reel fejl med årsag.\n\n## QA-gate\n- Alle tidligere module-, canvas-, Header/Footer- og editor/frontend-paritetstests skal forblive grønne.\n- Central release skal pakke `CollectionPageRenderer.php` og genkøre v0.1.74-QA før ZIP/SHA-256-manifest.\n''')

# Central release must re-run latest parity/cutover QA and prove the renderer is in the ZIP.
release = read(RELEASE)
if 'v0173_editor_frontend_parity_qa.py' not in release:
    release = release.replace('          python3 .github/scripts/v0172_gallery_design_qa.py\n', '          python3 .github/scripts/v0172_gallery_design_qa.py\n          python3 .github/scripts/v0173_editor_frontend_parity_qa.py\n', 1)
if 'v0174_module_cutover_qa.py' not in release:
    release = release.replace('          python3 .github/scripts/v0173_editor_frontend_parity_qa.py\n', '          python3 .github/scripts/v0173_editor_frontend_parity_qa.py\n          python3 .github/scripts/v0174_module_cutover_qa.py\n', 1)
if "CollectionPageRenderer.php$')\" = '1'" not in release:
    anchor = "          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/src/Frontend/Renderer.php$')\" = '1'\n"
    addition = anchor + "          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/src/Frontend/CollectionPageRenderer.php$')\" = '1'\n"
    if anchor not in release: raise SystemExit(f'{RELEASE}: package assertion anchor missing')
    release = release.replace(anchor, addition, 1)
write(RELEASE, release)

print('Applied Visual Designer Manager v0.1.74 module cutover and UX fixes')
