from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f'Missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding='utf-8') == value:
        return
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    if new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one anchor, found {count}: {old[:180]!r}')
    write(rel, value.replace(old, new, 1))


def insert_before(rel: str, anchor: str, payload: str, marker: str) -> None:
    value = read(rel)
    if marker in value:
        return
    count = value.count(anchor)
    if count != 1:
        raise SystemExit(f'{rel}: expected one insertion anchor, found {count}: {anchor[:180]!r}')
    write(rel, value.replace(anchor, payload + anchor, 1))


# Runtime version.
replace_once('clean/hangar18-manager/hangar18-manager.php', ' * Version: 0.1.79', ' * Version: 0.1.80')
replace_once('clean/hangar18-manager/hangar18-manager.php', "define('H18_CLEAN_VERSION', '0.1.79');", "define('H18_CLEAN_VERSION', '0.1.80');")

# Data is no longer a user-facing Manager destination. Keep a hidden route so old
# bookmarks do not break and the internal data diagnostic remains available.
replace_once(
    'clean/hangar18-manager/src/Admin/AdminController.php',
    "        add_submenu_page(self::MENU, 'Data', 'Data', $cap, 'h18-clean-data', [self::class, 'data']);",
    "        // Internal compatibility/diagnostic route only; module data is managed through Events, Køretøjer and Billedgalleri.\n        add_submenu_page(null, 'Data (intern)', 'Data', $cap, 'h18-clean-data', [self::class, 'data']);",
)

# Collection-page H1 is now a normal Designer element in the before slot.
p = 'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php'
replace_once(p, "self::openPage('events', $title) . HybridModuleSlots::render", "self::openPage('events', $title, false) . HybridModuleSlots::render")
replace_once(p, "self::openPage('galleries', $title) . HybridModuleSlots::render", "self::openPage('galleries', $title, false) . HybridModuleSlots::render")
replace_once(p, "self::openPage('vehicles', $title) . HybridModuleSlots::render", "self::openPage('vehicles', $title, false) . HybridModuleSlots::render")
replace_once(
    p,
    "    private static function openPage(string $class, string $title): string { return '<main class=\"h18-module-page h18-module-page--' . esc_attr(sanitize_html_class($class)) . '\"><h1>' . esc_html($title) . '</h1>'; }",
    "    private static function openPage(string $class, string $title, bool $showTitle = true): string { return '<main class=\"h18-module-page h18-module-page--' . esc_attr(sanitize_html_class($class)) . '\">' . ($showTitle ? '<h1>' . esc_html($title) . '</h1>' : ''); }",
)

# H1 becomes a first-class Text heading and eventvalue/eventimage become canonical nodes.
p = 'clean/hangar18-manager/src/Model/LayoutModel.php'
replace_once(
    p,
    "'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail', 'eventfield', 'contactform'",
    "'eventlist', 'eventdetail', 'eventvalue', 'eventimage', 'gallerylist', 'gallerydetail', 'eventfield', 'contactform'",
)
replace_once(p, "['h2', 'h3', 'h4', 'h5', 'h6']", "['h1', 'h2', 'h3', 'h4', 'h5', 'h6']")

EVENT_MODEL_PROPS = r'''        if ($type === 'eventvalue') {
            $valueKey = strtolower((string) ($raw['valueKey'] ?? 'title'));
            if (!in_array($valueKey, ['title','date','location','summary','description'], true)) { $valueKey = 'title'; }
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $tag = strtolower((string) ($raw['tag'] ?? ($valueKey === 'title' ? 'h1' : ($valueKey === 'description' ? 'div' : 'p'))));
            if (!in_array($tag, ['div','p','h1','h2','h3','h4','h5','h6'], true)) { $tag = 'div'; }
            return array_merge([
                'valueKey' => $valueKey,
                'recordId' => $recordId,
                'tag' => $tag,
                'align' => in_array((string) ($raw['align'] ?? 'left'), ['left','center','right'], true) ? (string) $raw['align'] : 'left',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? ($valueKey === 'title' ? 44 : 16), 8, 160, $valueKey === 'title' ? 44 : 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? ($valueKey === 'title' || $valueKey === 'summary' ? 700 : 400), 100, 900, $valueKey === 'title' || $valueKey === 'summary' ? 700 : 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? ($valueKey === 'title' ? 1.1 : 1.5), 0.8, 3.0, $valueKey === 'title' ? 1.1 : 1.5),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $raw) ? (bool) $raw['backgroundTransparent'] : true,
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
            ], $border);
        }
        if ($type === 'eventimage') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $fit = strtolower((string) ($raw['fit'] ?? 'cover'));
            if (!in_array($fit, ['cover','contain'], true)) { $fit = 'cover'; }
            return array_merge([
                'recordId' => $recordId,
                'fit' => $fit,
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 1000, 360),
                'focalX' => self::clamp($raw['focalX'] ?? 50, 0, 100, 50),
                'focalY' => self::clamp($raw['focalY'] ?? 50, 0, 100, 50),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'radius' => self::clamp($raw['radius'] ?? 4, 0, 100, 4),
            ], $border);
        }

'''
insert_before(p, "        if ($type === 'eventfield') {", EVENT_MODEL_PROPS, "if ($type === 'eventvalue')")

# Frontend rendering for Text H1 + individual event values/images.
p = 'clean/hangar18-manager/src/Frontend/Renderer.php'
replace_once(p, "['h2', 'h3', 'h4', 'h5', 'h6']", "['h1', 'h2', 'h3', 'h4', 'h5', 'h6']")
replace_once(p, "['h2' => 32, 'h3' => 28, 'h4' => 24, 'h5' => 20, 'h6' => 18]", "['h1' => 44, 'h2' => 32, 'h3' => 28, 'h4' => 24, 'h5' => 20, 'h6' => 18]")

EVENT_RENDERERS = r'''        if ($type === 'eventvalue') {
            $recordId = strtolower(trim((string) ($props['recordId'] ?? '')));
            if ($recordId === '') { $recordId = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET['h18_event'] ?? '')))); }
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $found = $recordId !== '' ? ModuleStore::findByRecordId('events', $recordId) : null;
            $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
            $allowDraft = self::$forceStandaloneCss && current_user_can('edit_pages');
            $valueKey = (string) ($props['valueKey'] ?? 'title');
            $placeholder = ['title'=>'Eventtitel','date'=>'Dato / tid','location'=>'Sted','summary'=>'Kort beskrivelse','description'=>'Beskrivelse'][$valueKey] ?? 'Eventværdi';
            if ($record === null || ((string) ($record['status'] ?? 'draft') !== 'publish' && !$allowDraft)) {
                if (!self::$forceStandaloneCss) { return ''; }
                $value = $placeholder;
                $rich = false;
            } else {
                $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
                $rich = false;
                if ($valueKey === 'date') { $value = self::eventDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? '')); }
                elseif ($valueKey === 'location') { $value = trim((string) ($fields['location'] ?? '')); }
                elseif ($valueKey === 'summary') { $value = trim((string) ($record['summary'] ?? '')); }
                elseif ($valueKey === 'description') { $value = trim((string) ($fields['description'] ?? '')); $rich = true; }
                else { $value = trim((string) ($record['title'] ?? '')); }
                if ($value === '') {
                    if (!self::$forceStandaloneCss) { return ''; }
                    $value = $placeholder;
                    $rich = false;
                }
            }
            $tag = in_array((string) ($props['tag'] ?? 'div'), ['div','p','h1','h2','h3','h4','h5','h6'], true) ? (string) $props['tag'] : 'div';
            $fontSize = max(8, min(160, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 400)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.5)));
            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
            $background = !empty($props['backgroundTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff');
            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
            $valueStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';color:' . $textColor . ';padding:' . $padding . 'px;text-align:' . (in_array((string) ($props['align'] ?? 'left'), ['left','center','right'], true) ? (string) $props['align'] : 'left') . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;';
            $content = $rich ? wp_kses_post((string) $value) : esc_html((string) $value);
            return '<' . $tag . ' id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-event-value h18-clean-front-event-value--' . esc_attr($valueKey) . '" style="' . esc_attr($valueStyle) . '">' . $content . '</' . $tag . '>';
        }
        if ($type === 'eventimage') {
            $recordId = strtolower(trim((string) ($props['recordId'] ?? '')));
            if ($recordId === '') { $recordId = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET['h18_event'] ?? '')))); }
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $found = $recordId !== '' ? ModuleStore::findByRecordId('events', $recordId) : null;
            $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
            $allowDraft = self::$forceStandaloneCss && current_user_can('edit_pages');
            if ($record === null || ((string) ($record['status'] ?? 'draft') !== 'publish' && !$allowDraft)) {
                return self::$forceStandaloneCss ? '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($style . $borderStyle . $spacingStyle) . '">Eventbillede · vælg event eller brug ?h18_event=record-id</div>' : '';
            }
            $featuredId = absint($record['featuredMediaId'] ?? 0);
            $url = $featuredId > 0 ? wp_get_attachment_image_url($featuredId, 'large') : false;
            if (!is_string($url) || $url === '') { return self::$forceStandaloneCss ? '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($style . $borderStyle . $spacingStyle) . '">Eventet har intet billede</div>' : ''; }
            $height = max(80, min(1000, (int) ($props['imageHeight'] ?? 360)));
            $fit = (string) ($props['fit'] ?? 'cover') === 'contain' ? 'contain' : 'cover';
            $focalX = max(0, min(100, (int) ($props['focalX'] ?? 50))); $focalY = max(0, min(100, (int) ($props['focalY'] ?? 50)));
            $background = sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff';
            $imageStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';overflow:hidden;';
            return '<figure id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-event-image" style="' . esc_attr($imageStyle) . '"><img src="' . esc_url($url) . '" alt="' . esc_attr((string) ($record['title'] ?? '')) . '" style="display:block;width:100%;height:' . esc_attr((string) $height) . 'px;object-fit:' . esc_attr($fit) . ';object-position:' . esc_attr((string) $focalX) . '% ' . esc_attr((string) $focalY) . '%"></figure>';
        }

'''
insert_before(p, "        if ($type === 'eventfield') {", EVENT_RENDERERS, "if ($type === 'eventvalue')")

# v0.1.80 migration: Designer collection titles + composable Event detail template.
p = 'clean/hangar18-manager/src/Migration/HybridModulePageMigration.php'
replace_once(
    p,
    "    private const DETAIL_META = '_h18_vd_module_detail_template_v0178';",
    "    private const DETAIL_META = '_h18_vd_module_detail_template_v0178';\n    private const V0180_COLLECTION_META = '_h18_vd_collection_heading_v0180';\n    private const V0180_COLLECTION_BACKUP = '_h18_vd_collection_heading_backup_v0180';\n    private const V0180_EVENT_DETAIL_META = '_h18_vd_event_detail_composable_v0180';\n    private const V0180_EVENT_DETAIL_BACKUP = '_h18_vd_event_detail_backup_v0180';",
)
replace_once(
    p,
    "            update_post_meta($postId, self::META, ['module'=>$config['module'],'detailPageId'=>$detailId,'migratedUtc'=>gmdate('c')]);\n        }\n    }",
    "            update_post_meta($postId, self::META, ['module'=>$config['module'],'detailPageId'=>$detailId,'migratedUtc'=>gmdate('c')]);\n        }\n        self::upgradeV0180();\n    }",
)

MIGRATION_V0180 = r'''    private static function upgradeV0180(): void
    {
        foreach ([
            'events' => 'Events',
            'billedgalleri' => 'Billedgalleri',
            'koeretoejer-og-materiel' => 'Køretøjer og materiel',
        ] as $slug => $fallbackTitle) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post) { continue; }
            $postId = (int) $page->ID;
            if (get_post_meta($postId, self::V0180_COLLECTION_META, true)) { continue; }
            $before = LayoutModel::get($postId);
            update_post_meta($postId, self::V0180_COLLECTION_BACKUP, $before);
            $title = trim((string) $page->post_title); if ($title === '') { $title = $fallbackTitle; }
            $next = self::withCollectionHeading($before, $title);
            $version = LayoutModel::saveVersion($postId, $next, get_current_user_id(), 'v0.1.80: sideoverskrift flyttet ind i Visual Designer');
            update_post_meta($postId, self::V0180_COLLECTION_META, ['version'=>$version,'migratedUtc'=>gmdate('c')]);
        }

        $detailId = self::detailPageId('events');
        if ($detailId <= 0 || get_post_meta($detailId, self::V0180_EVENT_DETAIL_META, true)) { return; }
        $before = LayoutModel::get($detailId);
        update_post_meta($detailId, self::V0180_EVENT_DETAIL_BACKUP, $before);
        $next = self::withComposableEventDetail($before);
        $version = LayoutModel::saveVersion($detailId, $next, get_current_user_id(), 'v0.1.80: Eventdetalje opdelt i flytbare dataelementer');
        update_post_meta($detailId, self::V0180_EVENT_DETAIL_META, ['version'=>$version,'migratedUtc'=>gmdate('c')]);
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    private static function withCollectionHeading(array $model, string $title): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['type'] ?? '') !== 'text') { continue; }
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ((string) ($node['id'] ?? '') === 'module-page-title' || strcasecmp(trim((string) ($props['heading'] ?? '')), $title) === 0) { return $model; }
        }
        $beforeId = '';
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['parentId'] ?? '') !== '' || (string) ($node['type'] ?? '') !== 'section') { continue; }
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ((string) ($props['moduleSlot'] ?? '') === 'before') { $beforeId = (string) ($node['id'] ?? ''); break; }
        }
        if ($beforeId === '') {
            $beforeId = 'hybrid-before-v0180';
            $nodes[] = ['id'=>$beforeId,'type'=>'section','parentId'=>'','order'=>1,'geometry'=>self::geometry(0,0,120,22),'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>22,'moduleSlot'=>'before']];
        }
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            if ((string) ($node['parentId'] ?? '') === $beforeId) {
                foreach (['desktop','laptop','tablet','mobile'] as $device) {
                    if (isset($node['geometry'][$device]) && is_array($node['geometry'][$device])) { $node['geometry'][$device]['y'] = (int) ($node['geometry'][$device]['y'] ?? 0) + 10; }
                }
            }
            if ((string) ($node['id'] ?? '') === $beforeId) {
                $height = max(22, (int) ($node['geometry']['desktop']['h'] ?? 0) + 10);
                foreach (['desktop','laptop','tablet','mobile'] as $device) {
                    if (isset($node['geometry'][$device]) && is_array($node['geometry'][$device])) { $node['geometry'][$device]['h'] = max($height, (int) ($node['geometry'][$device]['h'] ?? 0)); }
                }
                if (!isset($node['props']) || !is_array($node['props'])) { $node['props'] = []; }
                $node['props']['minHeightRows'] = $height;
            }
        }
        unset($node);
        $nodes[] = [
            'id'=>'module-page-title','type'=>'text','parentId'=>$beforeId,'order'=>1,'geometry'=>self::geometry(0,0,120,8),
            'props'=>['heading'=>$title,'headingLevel'=>'h1','text'=>'','align'=>'left','verticalAlign'=>'top','background'=>'#ffffff','backgroundTransparent'=>true,'textColor'=>'#30382a','headingColor'=>'#30382a','padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>16,'fontWeight'=>400,'lineHeight'=>1.5,'letterSpacing'=>0,'headingFontFamily'=>'body','headingFontSize'=>44,'headingFontWeight'=>700,'headingLineHeight'=>1.08,'headingLetterSpacing'=>0],
        ];
        $model['nodes'] = $nodes;
        return $model;
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    private static function withComposableEventDetail(array $model): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        $sectionId = 'detail-section';
        $hasSection = false; $already = false;
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            if ((string) ($node['id'] ?? '') === $sectionId && (string) ($node['type'] ?? '') === 'section') { $hasSection = true; }
            if ((string) ($node['type'] ?? '') === 'eventvalue' || (string) ($node['id'] ?? '') === 'event-title') { $already = true; }
        }
        if ($already) { return $model; }
        if (!$hasSection) {
            $nodes[] = ['id'=>$sectionId,'type'=>'section','parentId'=>'','order'=>10,'geometry'=>self::geometry(0,0,120,145),'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>145]];
        }
        $nodes = array_values(array_filter($nodes, static fn($node): bool => !is_array($node) || (string) ($node['id'] ?? '') !== 'detail-module'));

        $eventNodes = [
            ['id'=>'event-title','type'=>'eventvalue','order'=>20,'geometry'=>self::geometry(3,12,114,8),'props'=>['valueKey'=>'title','recordId'=>'','tag'=>'h1','align'=>'left','fontFamily'=>'system','fontSize'=>44,'fontWeight'=>700,'lineHeight'=>1.08,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-date','type'=>'eventvalue','order'=>30,'geometry'=>self::geometry(3,22,114,5),'props'=>['valueKey'=>'date','recordId'=>'','tag'=>'p','align'=>'left','fontFamily'=>'system','fontSize'=>16,'fontWeight'=>500,'lineHeight'=>1.4,'letterSpacing'=>0,'textColor'=>'#536243','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-location','type'=>'eventvalue','order'=>40,'geometry'=>self::geometry(3,28,114,5),'props'=>['valueKey'=>'location','recordId'=>'','tag'=>'p','align'=>'left','fontFamily'=>'system','fontSize'=>16,'fontWeight'=>400,'lineHeight'=>1.4,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-summary','type'=>'eventvalue','order'=>50,'geometry'=>self::geometry(3,34,114,6),'props'=>['valueKey'=>'summary','recordId'=>'','tag'=>'p','align'=>'left','fontFamily'=>'system','fontSize'=>17,'fontWeight'=>700,'lineHeight'=>1.4,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-description','type'=>'eventvalue','order'=>60,'geometry'=>self::geometry(3,42,114,14),'props'=>['valueKey'=>'description','recordId'=>'','tag'=>'div','align'=>'left','fontFamily'=>'system','fontSize'=>16,'fontWeight'=>400,'lineHeight'=>1.5,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-image','type'=>'eventimage','order'=>100,'geometry'=>self::geometry(3,102,114,36),'props'=>['recordId'=>'','fit'=>'cover','imageHeight'=>360,'focalX'=>50,'focalY'=>50,'background'=>'#ffffff','radius'=>4]],
        ];
        foreach ($eventNodes as $row) { $row['parentId'] = $sectionId; $nodes[] = $row; }

        $fieldRows = ['eventfield-about'=>58,'eventfield-program'=>72,'eventfield-practical'=>86];
        $oldRows = ['eventfield-about'=>84,'eventfield-program'=>96,'eventfield-practical'=>108];
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            if ($id === $sectionId) {
                foreach (['desktop','laptop','tablet','mobile'] as $device) {
                    if (isset($node['geometry'][$device]) && is_array($node['geometry'][$device])) { $node['geometry'][$device]['h'] = max(145, (int) ($node['geometry'][$device]['h'] ?? 0)); }
                }
                if (!isset($node['props']) || !is_array($node['props'])) { $node['props'] = []; }
                $node['props']['minHeightRows'] = max(145, (int) ($node['props']['minHeightRows'] ?? 0));
                continue;
            }
            if (!isset($fieldRows[$id])) { continue; }
            foreach (['desktop','laptop','tablet','mobile'] as $device) {
                if (!isset($node['geometry'][$device]) || !is_array($node['geometry'][$device])) { continue; }
                if ((int) ($node['geometry'][$device]['y'] ?? -1) === $oldRows[$id]) { $node['geometry'][$device]['y'] = $fieldRows[$id]; }
                if ((int) ($node['geometry'][$device]['x'] ?? 3) === 3) { $node['geometry'][$device]['x'] = $device === 'mobile' ? 0 : 3; }
                if ((int) ($node['geometry'][$device]['w'] ?? 114) === 114) { $node['geometry'][$device]['w'] = $device === 'mobile' ? 120 : 114; }
            }
        }
        unset($node);
        $model['nodes'] = $nodes;
        return $model;
    }

'''
insert_before(p, "    public static function detailPageId(string $module): int", MIGRATION_V0180, "private static function upgradeV0180()")

# Editor core: new event elements, H1 Text support, previews and Inspector.
p = 'clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(
    p,
    "'eventlist', 'eventdetail', 'gallerylist', 'gallerydetail', 'eventfield'",
    "'eventlist', 'eventdetail', 'eventvalue', 'eventimage', 'gallerylist', 'gallerydetail', 'eventfield'",
)
replace_once(p, "({h2:32,h3:28,h4:24,h5:20,h6:18})", "({h1:44,h2:32,h3:28,h4:24,h5:20,h6:18})")
replace_once(
    p,
    "eventlist:'Eventliste',eventdetail:'Eventdetalje',gallerylist:'Gallerioversigt'",
    "eventlist:'Eventliste',eventdetail:'Eventdetalje',eventvalue:'Eventværdi',eventimage:'Eventbillede',gallerylist:'Gallerioversigt'",
)
replace_once(p, "['h2', 'h3', 'h4', 'h5', 'h6'].includes", "['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes")

EVENT_JS_PROPS = r'''        if (type === 'eventvalue') {
            const valueKey=['title','date','location','summary','description'].includes(String(raw.valueKey||''))?String(raw.valueKey):'title';
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            const defaultTag=valueKey==='title'?'h1':(valueKey==='description'?'div':'p'); const tag=['div','p','h1','h2','h3','h4','h5','h6'].includes(String(raw.tag||''))?String(raw.tag):defaultTag;
            return Object.assign(common,{valueKey:valueKey,recordId:recordId,tag:tag,align:['left','center','right'].includes(String(raw.align||''))?String(raw.align):'left',fontFamily:normalizeFontToken(raw.fontFamily||'system',false),fontSize:clamp(parseInt(raw.fontSize||(valueKey==='title'?44:16),10)||(valueKey==='title'?44:16),8,160),fontWeight:clamp(parseInt(raw.fontWeight||(valueKey==='title'||valueKey==='summary'?700:400),10)||(valueKey==='title'||valueKey==='summary'?700:400),100,900),lineHeight:Math.max(.8,Math.min(3,parseFloat(raw.lineHeight||(valueKey==='title'?1.1:1.5))||(valueKey==='title'?1.1:1.5))),letterSpacing:Math.max(-10,Math.min(30,parseFloat(raw.letterSpacing||0)||0)),textColor:normalizeColor(raw.textColor||'#30382a'),background:normalizeColor(raw.background||'#ffffff'),backgroundTransparent:raw.backgroundTransparent!==false,padding:clamp(parseInt(raw.padding||0,10)||0,0,120),radius:clamp(parseInt(raw.radius||0,10)||0,0,100)});
        }
        if (type === 'eventimage') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{recordId:recordId,fit:String(raw.fit||'cover')==='contain'?'contain':'cover',imageHeight:clamp(parseInt(raw.imageHeight||360,10)||360,80,1000),focalX:clamp(parseInt(raw.focalX||50,10)||50,0,100),focalY:clamp(parseInt(raw.focalY||50,10)||50,0,100),background:normalizeColor(raw.background||'#ffffff'),radius:clamp(parseInt(raw.radius||4,10)||4,0,100)});
        }

'''
insert_before(p, "        if (type === 'eventfield') {", EVENT_JS_PROPS, "if (type === 'eventvalue')")
replace_once(
    p,
    "gallerydetail: 52, eventfield: 18, contactform",
    "gallerydetail: 52, eventvalue: 10, eventimage: 40, eventfield: 18, contactform",
)

EVENT_JS_PREVIEW = r'''        } else if (node.type === 'eventvalue') {
            wrap.classList.add('h18-clean-node-preview--eventvalue'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const key=String(node.props.valueKey||'title'); let value=''; if(record){if(key==='date'){value=eventDateLabel(record);}else if(key==='location'){value=String(fields.location||'');}else if(key==='summary'){value=String(record.summary||'');}else if(key==='description'){value=String(fields.description||'');}else{value=String(record.title||'');}} const labels={title:'Eventtitel',date:'Dato / tid',location:'Sted',summary:'Kort beskrivelse',description:'Beskrivelse'}; const tag=document.createElement(['DIV','P','H1','H2','H3','H4','H5','H6'].includes(String(node.props.tag||'').toUpperCase())?String(node.props.tag):'div'); tag.style.fontFamily=fontCss(node.props.fontFamily||'system');tag.style.fontSize=String(node.props.fontSize||16)+'px';tag.style.fontWeight=String(node.props.fontWeight||400);tag.style.lineHeight=String(node.props.lineHeight||1.5);tag.style.letterSpacing=String(node.props.letterSpacing||0)+'px';tag.style.color=node.props.textColor||'#30382a';tag.style.textAlign=node.props.align||'left';tag.style.padding=String(node.props.padding||0)+'px';tag.style.borderRadius=String(node.props.radius||0)+'px';tag.style.background=node.props.backgroundTransparent===false?(node.props.background||'#ffffff'):'transparent';if(key==='description'&&value){tag.innerHTML=richPreviewHtml(value);}else{tag.textContent=value||labels[key]||'Eventværdi';}wrap.appendChild(tag);
        } else if (node.type === 'eventimage') {
            wrap.classList.add('h18-clean-node-preview--eventimage'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; if(!record||!record.featuredUrl){wrap.textContent='Eventbillede · eventet har intet billede';}else{const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt=String(record.title||'');img.style.display='block';img.style.width='100%';img.style.height=String(node.props.imageHeight||360)+'px';img.style.objectFit=node.props.fit==='contain'?'contain':'cover';img.style.objectPosition=String(node.props.focalX||50)+'% '+String(node.props.focalY||50)+'%';img.style.background=node.props.background||'#ffffff';img.style.borderRadius=String(node.props.radius||4)+'px';wrap.appendChild(img);}

'''
insert_before(p, "        } else if (node.type === 'eventfield') {", EVENT_JS_PREVIEW, "node.type === 'eventvalue'")

# Inspector heading map and H1 option.
replace_once(
    p,
    "eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',gallerylist:'GALLERIOVERSIGT'",
    "eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',eventvalue:'EVENTVÆRDI',eventimage:'EVENTBILLEDE',eventfield:'EVENTFELT',gallerylist:'GALLERIOVERSIGT'",
)
replace_once(
    p,
    "<option value=\"h2\"' + (node.props.headingLevel === 'h2' ? ' selected' : '') + '>H2</option>",
    "<option value=\"h1\"' + (node.props.headingLevel === 'h1' ? ' selected' : '') + '>H1</option><option value=\"h2\"' + (node.props.headingLevel === 'h2' ? ' selected' : '') + '>H2</option>",
)
replace_once(p, "['h2', 'h3', 'h4', 'h5', 'h6'].includes(control.value)", "['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(control.value)")

EVENT_JS_INSPECTOR = r'''        } else if (node.type === 'eventvalue') {
            html += '<div class="h18-vd-menu-group"><h3>Eventværdi</h3><label>Værdi<select data-field="eventValueKey"><option value="title"'+(node.props.valueKey==='title'?' selected':'')+'>Titel</option><option value="date"'+(node.props.valueKey==='date'?' selected':'')+'>Dato / tid</option><option value="location"'+(node.props.valueKey==='location'?' selected':'')+'>Sted</option><option value="summary"'+(node.props.valueKey==='summary'?' selected':'')+'>Kort beskrivelse</option><option value="description"'+(node.props.valueKey==='description'?' selected':'')+'>Beskrivelse</option></select></label><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label>HTML-element<select data-field="eventValueTag">'+['h1','h2','h3','h4','h5','h6','p','div'].map(function(tag){return '<option value="'+tag+'"'+(String(node.props.tag||'')===tag?' selected':'')+'>'+tag.toUpperCase()+'</option>';}).join('')+'</select></label><label>Justering<select data-field="align"><option value="left"'+(node.props.align==='left'?' selected':'')+'>Venstre</option><option value="center"'+(node.props.align==='center'?' selected':'')+'>Midt</option><option value="right"'+(node.props.align==='right'?' selected':'')+'>Højre</option></select></label><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="fontFamily">'+fontOptions(node.props.fontFamily||'system',false)+'</select></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="160" value="'+String(node.props.fontSize||16)+'"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.fontWeight||400)+'"></label><label>Linjeafstand<input data-field="lineHeight" type="number" min="0.8" max="3" step="0.1" value="'+String(node.props.lineHeight||1.5)+'"></label><label>Tekstfarve<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Padding<input data-field="padding" type="number" min="0" max="120" value="'+String(node.props.padding||0)+'"></label><label>Hjørner<input data-field="radius" type="number" min="0" max="100" value="'+String(node.props.radius||0)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label></div><label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"'+(node.props.backgroundTransparent!==false?' checked':'')+'> Gennemsigtig baggrund</label><p class="description">Værdien kommer automatisk fra eventet. Flyt og style elementet som alle andre Designer-elementer.</p></div>';
        } else if (node.type === 'eventimage') {
            html += '<div class="h18-vd-menu-group"><h3>Eventbillede</h3><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><div class="h18-clean-field-grid"><label>Højde px<input data-field="eventDynamicImageHeight" type="number" min="80" max="1000" value="'+String(node.props.imageHeight||360)+'"></label><label>Tilpasning<select data-field="eventDynamicImageFit"><option value="cover"'+(node.props.fit!=='contain'?' selected':'')+'>Fyld / beskær</option><option value="contain"'+(node.props.fit==='contain'?' selected':'')+'>Vis hele billedet</option></select></label><label>Fokus X %<input data-field="eventDynamicImageFocalX" type="number" min="0" max="100" value="'+String(node.props.focalX||50)+'"></label><label>Fokus Y %<input data-field="eventDynamicImageFocalY" type="number" min="0" max="100" value="'+String(node.props.focalY||50)+'"></label><label>Hjørner<input data-field="radius" type="number" min="0" max="100" value="'+String(node.props.radius||4)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label></div><p class="description">Viser eventets primære billede. Elementet kan flyttes eller slettes frit.</p></div>';

'''
insert_before(p, "        } else if (node.type === 'eventfield') {", EVENT_JS_INSPECTOR, "<h3>Eventværdi</h3>")

# Inspector handlers for the new event nodes.
replace_once(
    p,
    "                else if (field === 'eventFieldKey') { current.props.fieldKey=String(control.value||'about'); }",
    "                else if (field === 'eventValueKey') { current.props.valueKey=['title','date','location','summary','description'].includes(String(control.value||''))?String(control.value):'title'; }\n                else if (field === 'eventValueTag') { current.props.tag=['div','p','h1','h2','h3','h4','h5','h6'].includes(String(control.value||''))?String(control.value):'div'; }\n                else if (field === 'eventDynamicImageHeight') { current.props.imageHeight=clamp(parseInt(control.value||360,10)||360,80,1000); }\n                else if (field === 'eventDynamicImageFit') { current.props.fit=String(control.value||'cover')==='contain'?'contain':'cover'; }\n                else if (field === 'eventDynamicImageFocalX') { current.props.focalX=clamp(parseInt(control.value||50,10)||50,0,100); }\n                else if (field === 'eventDynamicImageFocalY') { current.props.focalY=clamp(parseInt(control.value||50,10)||50,0,100); }\n                else if (field === 'eventFieldKey') { current.props.fieldKey=String(control.value||'about'); }",
)

# Palette: expose composable pieces and hide the old all-in-one Eventdetalje from new designs.
p = 'clean/hangar18-manager/src/Admin/EditorController.php'
replace_once(
    p,
    "                'eventlist' => 'Eventliste', 'eventdetail' => 'Eventdetalje',\n                'gallerylist' => 'Gallerioversigt', 'gallerydetail' => 'Albumvisning', 'eventfield' => 'Eventfelt',",
    "                'eventlist' => 'Eventliste', 'eventvalue' => 'Eventværdi', 'eventimage' => 'Eventbillede',\n                'gallerylist' => 'Gallerioversigt', 'gallerydetail' => 'Albumvisning', 'eventfield' => 'Eventfelt',",
)
# H1 module-design control is obsolete for collection title after title cutover.
replace_once(p, "                'h1Size' => ['H1 størrelse (px)', 24, 72, 1],\n", "")

# Historical v0.1.79 QA must remain useful for newer releases.
p = '.github/scripts/v0179_responsive_qa.py'
s = read(p)
s = s.replace("req(header is not None and const is not None and header.group(1) == const.group(1) == '0.1.79', 'runtime version is exactly v0.1.79')", "req(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0,1,79), 'runtime version is v0.1.79 or newer')")
s = s.replace("req(bool(versions) and str(versions[0].get('version', '')) == '0.1.79', 'release history starts with v0.1.79')", "req(any(isinstance(row, dict) and str(row.get('version','')) == '0.1.79' for row in versions), 'release history retains v0.1.79')")
s = s.replace("req('0.1.79' in notes and 'Tablet' in notes and 'ResponsiveRenderer' in notes, 'release notes describe responsive Tablet completion')", "req(any(isinstance(row, dict) and str(row.get('version','')) == '0.1.79' and any('Tablet' in str(item) for item in row.get('items', [])) for row in versions), 'release history documents responsive Tablet completion')")
s = s.replace("req('**Aktuel release:** v0.1.79' in backlog and 'CLEAN-RESPONSIVE-009 — FÆRDIG I v0.1.79' in backlog, 'canonical backlog closes CLEAN-RESPONSIVE-009 in v0.1.79')", "req('CLEAN-RESPONSIVE-009 — FÆRDIG I v0.1.79' in backlog, 'canonical backlog closes CLEAN-RESPONSIVE-009 in v0.1.79')")
s = s.replace("req(str(manifest.get('version', '')) == '0.1.78', 'pre-release updater manifest remains on verified v0.1.78')\nreq((ROOT / 'dist/visual-designer-manager-v0.1.78.zip').is_file(), 'verified v0.1.78 ZIP remains present before release')", "req(tuple(map(int, str(manifest.get('version','0.0.0')).split('.'))) >= (0,1,79), 'updater manifest is v0.1.79 or newer')\nreq((ROOT / 'dist/visual-designer-manager-v0.1.79.zip').is_file(), 'verified v0.1.79 ZIP remains present')")
write(p, s)

# Release history.
p = 'clean/hangar18-manager/release-history.json'
data = json.loads(read(p))
versions = data.get('versions', []) if isinstance(data, dict) else []
if not any(isinstance(row, dict) and row.get('version') == '0.1.80' for row in versions):
    versions.insert(0, {
        'version': '0.1.80',
        'date': '2026-09-02',
        'items': [
            'VD-COMPOSABLE-MODULE-PAGES-002: Events, Billedgalleri og Køretøjer får sideoverskriften som normalt flytbart/stylbart Designer-element.',
            'Eventdetalje opdeles i Eventtitel, Dato/tid, Sted, Kort beskrivelse, Beskrivelse, Eventbillede og de eksisterende Eventfelter.',
            'Nye Designer-elementer Eventværdi og Eventbillede kan flyttes og styles pr. Desktop/Laptop/Tablet/Mobil.',
            'Standard Eventfelter flugter nu med de øvrige eventtekster uden skjult ekstra padding fra den tidligere samlede detailblok.',
            'Den gamle samlede Eventdetalje-node bevares for bagudkompatibilitet, men vises ikke længere i paletten.',
            'Manager-menuen Data skjules; den interne ModuleBinding/datamodel bevares og bruges fortsat automatisk af dynamiske moduler.'
        ]
    })
    data['versions'] = versions
write(p, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '''<h2>0.1.80 – Komponérbare modulsider og Eventdetalje</h2>
<ul>
<li><strong>Events, Billedgalleri og Køretøjer:</strong> den faste H1 er flyttet ind i Visual Designer som et normalt Tekst-element. Overskriften kan nu flyttes og styles frit.</li>
<li><strong>Eventdetalje:</strong> titel, dato/tid, sted, kort beskrivelse og længere beskrivelse er selvstændige <em>Eventværdi</em>-elementer.</li>
<li><strong>Eventbillede</strong> er et selvstændigt dynamisk Designer-element med højde, crop/contain, fokuspunkt og radius.</li>
<li>Om arrangementet, Program og Praktiske oplysninger fortsætter som selvstændige Eventfelt-elementer og flugter med de øvrige eventtekster.</li>
<li>Alle de nye dynamiske elementer bruger samme Desktop/Laptop/Tablet/Mobil-geometri som resten af Visual Designer.</li>
<li>Den tekniske <strong>Data</strong>-menu er fjernet fra den normale Manager-navigation. Den interne data-/bindingmodel er bevaret.</li>
<li>Migrationsbackup gemmes før både collection-overskrifter og Eventdetalje opgraderes.</li>
</ul>
''')

p = 'docs/clean-backlog-v0100.md'
s = read(p)
s = s.replace('**Aktuel release:** v0.1.79', '**Aktuel release:** v0.1.80', 1)
roadmap_anchor = '11. **v0.1.79 – CLEAN-RESPONSIVE-009 — FÆRDIG:** Tablet er et fuldt canonical breakpoint i toolbar, Inspector, viewport og frontend med isoleret Undo/Redo.\n'
roadmap_line = roadmap_anchor + '12. **v0.1.80 – VD-COMPOSABLE-MODULE-PAGES-002 — FÆRDIG:** collection-overskrifter og Eventdetaljens kernefelter er selvstændige Designer-elementer; Data-menuen er skjult.\n'
if roadmap_anchor in s and '12. **v0.1.80 – VD-COMPOSABLE-MODULE-PAGES-002' not in s:
    s = s.replace(roadmap_anchor, roadmap_line, 1)
section = '''\n### VD-COMPOSABLE-MODULE-PAGES-002 — FÆRDIG I v0.1.80\n- Events, Billedgalleri og Køretøjer viser ikke længere en hardcoded collection-H1; migrationen opretter den som almindeligt H1-Tekst-element i før-slotten.\n- Eventdetalje bruger selvstændige Eventværdi-elementer til titel, dato/tid, sted, kort beskrivelse og beskrivelse samt et separat Eventbillede-element.\n- Om arrangementet, Program og Praktiske oplysninger forbliver separate Eventfelt-elementer og starter på samme gridlinje som de øvrige eventtekster.\n- Den tidligere Eventdetalje-node forbliver understøttet til gamle layouts, men er skjult fra paletten for nye designs.\n- Data-menuen er ikke længere en synlig administrationsdestination; ModuleBinding og ModuleStore er fortsat canonical intern datainfrastruktur.\n- Der gemmes pre-migration backup-meta før collection- og eventdetail-layouts ændres.\n'''
if '### VD-COMPOSABLE-MODULE-PAGES-002 — FÆRDIG I v0.1.80' not in s:
    marker = '\n### CLEAN-THEME-010 — IMPLEMENTERET BASELINE / REGRESSION FORTSÆTTER'
    if marker in s: s = s.replace(marker, section + marker, 1)
    else: s += section
write(p, s)

write('docs/v0180-status.md', '''# Visual Designer Manager v0.1.80 – status

Status: release candidate implementeret.

## Scope
- Collection-H1 for Events, Billedgalleri og Køretøjer er et normalt Designer-element.
- Eventdetalje er opdelt i flytbare Eventværdi/Eventbillede/Eventfelt-elementer.
- H1 er understøttet som almindelig Tekst-overskrifttype.
- Data-menuen er skjult; intern ModuleBinding/ModuleStore bevares.
- Migration gemmer backup før ændring af eksisterende layouts.

## QA
Se `.github/scripts/v0180_composable_qa.py` og apply-workflowets fulde regression-gate.
''')

print('Applied Visual Designer Manager v0.1.80 composable module-page changes.')
