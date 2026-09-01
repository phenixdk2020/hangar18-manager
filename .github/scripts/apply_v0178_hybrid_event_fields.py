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
        raise SystemExit(f'{rel}: expected one anchor, found {count}: {old[:160]!r}')
    write(rel, value.replace(old, new, 1))


def regex_once(rel: str, pattern: str, replacement: str) -> None:
    value = read(rel)
    if re.search(re.escape(replacement[:80]), value):
        return
    updated, count = re.subn(pattern, replacement, value, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{rel}: regex anchor count {count}: {pattern[:160]!r}')
    write(rel, updated)


EVENT_FIELD_REGISTRY = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Modules;

final class EventFieldRegistry
{
    public const OPTION = 'h18_event_fields_v1';
    public const SCHEMA = 1;
    private const MAX_FIELDS = 80;

    /** @return array<int,array<string,mixed>> */
    public static function all(): array
    {
        $raw = get_option(self::OPTION, null);
        return is_array($raw) ? self::normalize($raw) : self::defaults();
    }

    /** @param array<int,mixed> $rows @return array<int,array<string,mixed>> */
    public static function normalize(array $rows): array
    {
        $out = [];
        $used = [];
        foreach (array_slice(array_values($rows), 0, self::MAX_FIELDS) as $index => $row) {
            if (!is_array($row)) { continue; }
            $label = sanitize_text_field((string) ($row['label'] ?? ''));
            if ($label === '') { continue; }
            $id = sanitize_key((string) ($row['id'] ?? ''));
            if ($id === '') { $id = sanitize_key($label); }
            if ($id === '') { $id = 'event_field_' . ($index + 1); }
            $base = substr($id, 0, 54); $candidate = $base; $suffix = 2;
            while (isset($used[$candidate])) { $candidate = substr($base, 0, 48) . '_' . $suffix++; }
            $used[$candidate] = true;
            $type = strtolower((string) ($row['type'] ?? 'richtext'));
            if (!in_array($type, ['text','textarea','richtext','number','integer','boolean','date','datetime','url'], true)) { $type = 'text'; }
            $out[] = [
                'id' => $candidate,
                'label' => $label,
                'type' => $type,
                'enabled' => array_key_exists('enabled', $row) ? (bool) $row['enabled'] : true,
                'required' => !empty($row['required']),
                'showCard' => !empty($row['showCard']),
                'showDetail' => array_key_exists('showDetail', $row) ? (bool) $row['showDetail'] : true,
                'order' => max(0, min(100000, (int) ($row['order'] ?? (($index + 1) * 10)))),
            ];
        }
        usort($out, static function (array $a, array $b): int {
            $cmp = ((int) $a['order']) <=> ((int) $b['order']);
            return $cmp !== 0 ? $cmp : strnatcasecmp((string) $a['label'], (string) $b['label']);
        });
        return array_values($out);
    }

    /** @param array<int,mixed> $rows */
    public static function save(array $rows): bool
    {
        return update_option(self::OPTION, self::normalize($rows), false);
    }

    /** @return array<string,array<string,mixed>> */
    public static function byId(): array
    {
        $out = [];
        foreach (self::all() as $row) { $out[(string) $row['id']] = $row; }
        return $out;
    }

    /** @return array<int,array<string,mixed>> */
    private static function defaults(): array
    {
        return self::normalize([
            ['id'=>'about','label'=>'Om arrangementet','type'=>'richtext','enabled'=>true,'required'=>false,'showCard'=>false,'showDetail'=>true,'order'=>10],
            ['id'=>'program','label'=>'Program','type'=>'richtext','enabled'=>true,'required'=>false,'showCard'=>false,'showDetail'=>true,'order'=>20],
            ['id'=>'practical','label'=>'Praktiske oplysninger','type'=>'richtext','enabled'=>true,'required'=>false,'showCard'=>false,'showDetail'=>true,'order'=>30],
        ]);
    }

    private function __construct() {}
}
'''

HYBRID_SLOTS = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Model\LayoutModel;

final class HybridModuleSlots
{
    /** @return string */
    public static function render(int $postId, string $slot): string
    {
        $slot = in_array($slot, ['before','between','after'], true) ? $slot : 'before';
        if (!metadata_exists('post', $postId, LayoutModel::META)) { return ''; }
        $model = LayoutModel::get($postId);
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $roots = [];
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['parentId'] ?? '') !== '' || (string) ($node['type'] ?? '') !== 'section') { continue; }
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ((string) ($props['moduleSlot'] ?? 'before') !== $slot) { continue; }
            $roots[(string) $node['id']] = true;
        }
        if (!$roots) { return ''; }

        $keep = [];
        $changed = true;
        while ($changed) {
            $changed = false;
            foreach ($nodes as $node) {
                if (!is_array($node)) { continue; }
                $id = (string) ($node['id'] ?? ''); $parent = (string) ($node['parentId'] ?? '');
                if ($id === '' || isset($keep[$id])) { continue; }
                if (isset($roots[$id]) || ($parent !== '' && isset($keep[$parent]))) { $keep[$id] = true; $changed = true; }
            }
        }
        $filtered = array_values(array_filter($nodes, static fn($node): bool => is_array($node) && isset($keep[(string) ($node['id'] ?? '')])));
        $hasContent = false;
        foreach ($filtered as $node) { if ((string) ($node['type'] ?? '') !== 'section') { $hasContent = true; break; } }
        if (!$hasContent) { return ''; }
        $fragment = $model; $fragment['nodes'] = $filtered;
        return '<div class="h18-vd-hybrid-slot h18-vd-hybrid-slot-' . esc_attr($slot) . '">' . Renderer::renderFragment($fragment) . '</div>';
    }

    private function __construct() {}
}
'''

HYBRID_MIGRATION = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class HybridModulePageMigration
{
    public const META = '_h18_vd_hybrid_module_slots_v0178';
    private const BACKUP_META = '_h18_vd_hybrid_module_backup_v0178';
    private const DETAIL_META = '_h18_vd_module_detail_template_v0178';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'ensure'], 27);
    }

    public static function ensure(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        foreach ([
            'events' => ['module'=>'events','detailSlug'=>'event-detalje','detailTitle'=>'Eventdetalje','detailType'=>'eventdetail','query'=>'h18_event'],
            'billedgalleri' => ['module'=>'galleries','detailSlug'=>'album-detalje','detailTitle'=>'Albumdetalje','detailType'=>'gallerydetail','query'=>'h18_gallery'],
            'koeretoejer-og-materiel' => ['module'=>'vehicles','detailSlug'=>'koeretoej-detalje','detailTitle'=>'Køretøjsdetalje','detailType'=>'vehicledetail','query'=>'h18_vehicle'],
        ] as $slug => $config) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post) { continue; }
            $postId = (int) $page->ID;
            $detailId = self::ensureDetailPage($postId, $config);
            if (get_post_meta($postId, self::META, true)) { continue; }
            $old = LayoutModel::get($postId);
            update_post_meta($postId, self::BACKUP_META, $old);
            $model = self::slotModel();
            LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'v0.1.78 hybrid modulside: Designer-slots + dynamisk modul');
            update_post_meta($postId, self::META, ['module'=>$config['module'],'detailPageId'=>$detailId,'migratedUtc'=>gmdate('c')]);
        }
    }

    public static function detailPageId(string $module): int
    {
        $module = sanitize_key($module);
        $slug = ['events'=>'event-detalje','galleries'=>'album-detalje','vehicles'=>'koeretoej-detalje'][$module] ?? '';
        if ($slug === '') { return 0; }
        $page = get_page_by_path($slug, OBJECT, 'page');
        return $page instanceof \WP_Post ? (int) $page->ID : 0;
    }

    /** @param array<string,string> $config */
    private static function ensureDetailPage(int $collectionId, array $config): int
    {
        $page = get_page_by_path((string) $config['detailSlug'], OBJECT, 'page');
        if (!$page instanceof \WP_Post) {
            $id = wp_insert_post([
                'post_type'=>'page','post_title'=>(string) $config['detailTitle'],'post_name'=>(string) $config['detailSlug'],
                'post_status'=>current_user_can('publish_pages') ? 'publish' : 'draft','post_content'=>'',
            ], true);
            if (is_wp_error($id)) { return 0; }
            $page = get_post((int) $id);
        }
        if (!$page instanceof \WP_Post) { return 0; }
        $detailId = (int) $page->ID;
        if (!get_post_meta($detailId, self::DETAIL_META, true)) {
            $model = self::detailModel((string) $config['detailType'], $collectionId, (string) $config['module']);
            LayoutModel::saveVersion($detailId, $model, get_current_user_id(), 'v0.1.78 dynamisk detaljeskabelon');
            update_post_meta($detailId, self::DETAIL_META, ['module'=>$config['module'],'collectionPageId'=>$collectionId,'createdUtc'=>gmdate('c')]);
        }
        return $detailId;
    }

    /** @return array<string,mixed> */
    private static function slotModel(): array
    {
        $nodes = []; $order = 10; $y = 0;
        foreach ([['before',12],['between',12],['after',12]] as $item) {
            $slot = (string) $item[0]; $h = (int) $item[1];
            $nodes[] = [
                'id'=>'hybrid-'.$slot,'type'=>'section','parentId'=>'','order'=>$order,
                'geometry'=>self::geometry(0,$y,120,$h),
                'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>$h,'moduleSlot'=>$slot],
            ];
            $order += 10; $y += $h + 2;
        }
        return ['schemaVersion'=>1,'units'=>120,'rowPx'=>8,'nodes'=>$nodes];
    }

    /** @return array<string,mixed> */
    private static function detailModel(string $detailType, int $collectionId, string $module): array
    {
        $nodes = [[
            'id'=>'detail-section','type'=>'section','parentId'=>'','order'=>10,'geometry'=>self::geometry(0,0,120,120),
            'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>120],
        ],[
            'id'=>'detail-back','type'=>'button','parentId'=>'detail-section','order'=>10,'geometry'=>self::geometry(3,2,30,7),
            'props'=>['text'=>$module==='events'?'← Tilbage til Events':($module==='galleries'?'← Tilbage til Billedgalleri':'← Tilbage til Køretøjer'),'linkType'=>'page','pageId'=>$collectionId,'autoSize'=>true,'background'=>'#30382a','textColor'=>'#ffffff','paddingX'=>16,'paddingY'=>8,'radius'=>4],
        ],[
            'id'=>'detail-module','type'=>$detailType,'parentId'=>'detail-section','order'=>20,'geometry'=>self::geometry(3,12,114,70),
            'props'=>['recordId'=>'','showImage'=>true,'showDate'=>true,'showLocation'=>true,'showSummary'=>true,'showDescription'=>true,'showGallery'=>true,'showCategory'=>true,'showAttributes'=>true,'columns'=>4,'imageHeight'=>360,'background'=>'#ffffff','textColor'=>'#30382a','accentColor'=>'#536243','padding'=>16,'radius'=>4],
        ]];
        if ($module === 'events') {
            $row = 84; $order = 30;
            foreach (['about','program','practical'] as $key) {
                $nodes[] = ['id'=>'eventfield-'.$key,'type'=>'eventfield','parentId'=>'detail-section','order'=>$order,'geometry'=>self::geometry(3,$row,114,10),'props'=>['fieldKey'=>$key,'recordId'=>'','showHeading'=>true,'background'=>'','textColor'=>'#30382a','padding'=>0,'radius'=>0]];
                $row += 12; $order += 10;
            }
            $nodes[0]['geometry'] = self::geometry(0,0,120,124); $nodes[0]['props']['minHeightRows'] = 124;
        }
        return ['schemaVersion'=>1,'units'=>120,'rowPx'=>8,'nodes'=>$nodes];
    }

    /** @return array<string,mixed> */
    private static function geometry(int $x,int $y,int $w,int $h): array
    {
        return ['desktop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],'laptop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],'tablet'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],'mobile'=>['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false]];
    }

    private function __construct() {}
}
'''

EVENT_ADMIN_JS = r'''(function(){'use strict';
function rowHtml(order){return '<div class="h18-vd-field-row" data-event-field-row><input type="hidden" name="event_field_id[]" value=""><label>Navn<input required type="text" name="event_field_label[]"></label><label>Type<select name="event_field_type[]"><option value="richtext">Rich text</option><option value="text">Tekst</option><option value="textarea">Flere linjer</option><option value="number">Tal</option><option value="integer">Heltal</option><option value="boolean">Ja/nej</option><option value="date">Dato</option><option value="datetime">Dato/tid</option><option value="url">Link</option></select></label><label>Rækkefølge<input type="number" name="event_field_order[]" value="'+order+'"></label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_enabled[]" value="1" checked> Aktiv</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_required[]" value="1"> Påkrævet</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_card[]" value="1"> På kort</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_detail[]" value="1" checked> På detalje</label><button type="button" class="button-link-delete h18-vd-remove-event-field">Fjern</button></div>';}
document.addEventListener('click',function(e){const add=e.target&&e.target.closest?e.target.closest('#h18-vd-add-event-field'):null;if(add){e.preventDefault();const host=document.getElementById('h18-vd-event-field-rows');if(!host)return;host.insertAdjacentHTML('beforeend',rowHtml((host.children.length+1)*10));const inputs=host.querySelectorAll('input[name="event_field_label[]"]');if(inputs.length)inputs[inputs.length-1].focus();return;}const remove=e.target&&e.target.closest?e.target.closest('.h18-vd-remove-event-field'):null;if(remove){e.preventDefault();const row=remove.closest('[data-event-field-row]');if(row)row.remove();}});
}());
'''

V0178_STATUS = '''# Visual Designer Manager v0.1.78 – Hybrid modulsider + Eventfelter\n\n**Dato:** 1. september 2026  \n**Status:** Release candidate; central ZIP/manifest-build kræves efter grøn QA.\n\n## Scope\n- Events, Billedgalleri og Køretøjer kan nu have almindelige Visual Designer-elementer i flow-slots **før / mellem / efter** det dynamiske modulindhold.\n- Den dynamiske CollectionPageRenderer bevares, så søgning, sortering, eventarkiv og naturlig indholdshøjde ikke erstattes af faste grid-kort.\n- Moduldesign fra v0.1.77 bevares i en separat **Moduldesign**-tilstand; standardtilstanden på de tre sider er almindelig indholdsredigering.\n- Detailvisninger får publicerede, genbrugelige Designer-skabelonsider: Eventdetalje, Albumdetalje og Køretøjsdetalje.\n- Eventfelter er fleksible og centrale med stabile felt-IDer, type, aktiv/påkrævet, kort/detalje-visning og rækkefølge.\n- Standard Eventfelter: **Om arrangementet**, **Program**, **Praktiske oplysninger**.\n- Nyt Designer-element **Eventfelt** kan placere et bestemt fleksibelt Eventfelt på Eventdetalje-skabelonen.\n- Eksisterende modulrecords ændres ikke; tidligere layout gemmes i v0.1.78-backup-meta før slot-migration.\n'''

# New files.
write('clean/hangar18-manager/src/Modules/EventFieldRegistry.php', EVENT_FIELD_REGISTRY)
write('clean/hangar18-manager/src/Frontend/HybridModuleSlots.php', HYBRID_SLOTS)
write('clean/hangar18-manager/src/Migration/HybridModulePageMigration.php', HYBRID_MIGRATION)
write('clean/hangar18-manager/assets/admin-v0178-events.js', EVENT_ADMIN_JS)
write('docs/v0178-status.md', V0178_STATUS)

# Plugin bootstrap + localization.
replace_once('clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Modules/VehicleFieldRegistry.php';",
    "require_once H18_CLEAN_DIR . 'src/Modules/VehicleFieldRegistry.php';\nrequire_once H18_CLEAN_DIR . 'src/Modules/EventFieldRegistry.php';")
replace_once('clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Migration/FormPageProvisioner.php';",
    "require_once H18_CLEAN_DIR . 'src/Migration/FormPageProvisioner.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/HybridModulePageMigration.php';")
replace_once('clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Frontend/CollectionPageRenderer.php';",
    "require_once H18_CLEAN_DIR . 'src/Frontend/HybridModuleSlots.php';\nrequire_once H18_CLEAN_DIR . 'src/Frontend/CollectionPageRenderer.php';")
replace_once('clean/hangar18-manager/hangar18-manager.php',
    "\\VisualDesignerManager\\Migration\\FormPageProvisioner::register();",
    "\\VisualDesignerManager\\Migration\\FormPageProvisioner::register();\n    \\VisualDesignerManager\\Migration\\HybridModulePageMigration::register();")
replace_once('clean/hangar18-manager/hangar18-manager.php',
    "'fields' => isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [],\n        ];\n    }, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('events'",
    "'fields' => isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [],\n            'attributes' => isset($record['attributes']) && is_array($record['attributes']) ? $record['attributes'] : [],\n        ];\n    }, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('events'")
replace_once('clean/hangar18-manager/hangar18-manager.php',
    "'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events'),",
    "'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events'),\n        'eventFieldDefinitions' => \\VisualDesignerManager\\Modules\\EventFieldRegistry::all(),")

# LayoutModel: slot property and Eventfelt type.
replace_once('clean/hangar18-manager/src/Model/LayoutModel.php',
    "'gallerylist', 'gallerydetail', 'contactform', 'membershipform'",
    "'gallerylist', 'gallerydetail', 'eventfield', 'contactform', 'membershipform'")
replace_once('clean/hangar18-manager/src/Model/LayoutModel.php',
    "'minHeightRows' => self::clamp($raw['minHeightRows'] ?? 0, 0, 4000, 0),",
    "'minHeightRows' => self::clamp($raw['minHeightRows'] ?? 0, 0, 4000, 0),\n                'moduleSlot' => $type === 'section' && in_array((string) ($raw['moduleSlot'] ?? 'before'), ['before','between','after'], true) ? (string) ($raw['moduleSlot'] ?? 'before') : 'before',")
# Insert eventfield normalization before gallerylist block.
anchor = "        if ($type === 'gallerylist') {"
eventfield_php = r'''        if ($type === 'eventfield') {
            $fieldKey = sanitize_key((string) ($raw['fieldKey'] ?? 'about'));
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            return array_merge([
                'fieldKey' => $fieldKey !== '' ? $fieldKey : 'about',
                'recordId' => $recordId,
                'showHeading' => array_key_exists('showHeading', $raw) ? (bool) $raw['showHeading'] : true,
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '')) ?: '',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 80, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 60, 0),
            ], $border);
        }
'''
replace_once('clean/hangar18-manager/src/Model/LayoutModel.php', anchor, eventfield_php + anchor)

# Renderer: public fragment entry + EventField render.
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php',
    "use VisualDesignerManager\\Modules\\ModuleStore;",
    "use VisualDesignerManager\\Modules\\ModuleStore;\nuse VisualDesignerManager\\Modules\\EventFieldRegistry;")
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php',
    "    /** @param array<string,mixed> $model */\n    private static function renderModel(array $model): string",
    "    /** @param array<string,mixed> $model */\n    public static function renderFragment(array $model): string\n    {\n        return self::renderModel(LayoutModel::normalize($model));\n    }\n\n    /** @param array<string,mixed> $model */\n    private static function renderModel(array $model): string")
renderer_anchor = "        if ($type === 'gallerylist') {"
eventfield_render = r'''        if ($type === 'eventfield') {
            $recordId=strtolower(trim((string)($props['recordId']??''))); if($recordId===''){$recordId=strtolower(trim(sanitize_text_field((string)wp_unslash($_GET['h18_event']??''))));}
            if($recordId!==''&&!preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/',$recordId)){$recordId='';}
            $fieldKey=sanitize_key((string)($props['fieldKey']??'about')); $found=$recordId!==''?ModuleStore::findByRecordId('events',$recordId):null; $record=is_array($found)&&isset($found['record'])&&is_array($found['record'])?$found['record']:null;
            if($record===null){$message=self::$forceStandaloneCss?'Eventfelt · vælg record via ?h18_event=record-id.':'';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-field" style="'.esc_attr($style.$borderStyle.$spacingStyle).'">'.esc_html($message).'</div>';}
            $attribute=null;foreach((array)($record['attributes']??[]) as $row){if(is_array($row)&&(string)($row['key']??'')===$fieldKey){$attribute=$row;break;}}
            $defs=EventFieldRegistry::byId();$def=$defs[$fieldKey]??null;if(!is_array($attribute)||empty($attribute['enabled'])||!is_array($def)||empty($def['enabled'])){return '';}
            $value=$attribute['value']??'';if(is_bool($value)){$empty=!$value;}else{$empty=trim((string)$value)==='';}if($empty){return '';}
            $label=(string)($def['label']??($attribute['label']??$fieldKey));$type=(string)($def['type']??($attribute['type']??'text'));$content=$type==='richtext'?wp_kses_post((string)$value):($type==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value)));
            $heading=!empty($props['showHeading'])?'<h3 class="h18-clean-front-event-field-heading">'.esc_html($label).'</h3>':'';$bg=sanitize_hex_color((string)($props['background']??''))?:'';$color=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a';$padding=max(0,min(80,(int)($props['padding']??0)));$radius=max(0,min(60,(int)($props['radius']??0)));$extra=($bg!==''?'background:'.$bg.';':'').'color:'.$color.';padding:'.$padding.'px;border-radius:'.$radius.'px;';
            return '<section id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-field" style="'.esc_attr($style.$borderStyle.$spacingStyle.$extra).'">'.$heading.'<div class="h18-clean-front-event-field-value">'.$content.'</div></section>';
        }
'''
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php', renderer_anchor, eventfield_render + renderer_anchor)
# Eventdetail: append flexible field sections for direct eventdetail blocks, excluding separately placed ones is not possible; render only fields marked detail.
old_desc = "$description=!empty($props['showDescription'])&&trim((string)($fields['description']??''))!==''?'<div class=\"h18-clean-front-event-description\">'.wp_kses_post((string)$fields['description']).'</div>':'';$detailStyle="
new_desc = "$description=!empty($props['showDescription'])&&trim((string)($fields['description']??''))!==''?'<div class=\"h18-clean-front-event-description\">'.wp_kses_post((string)$fields['description']).'</div>':'';$custom='';$defs=EventFieldRegistry::byId();foreach((array)($record['attributes']??[]) as $attribute){if(!is_array($attribute)||empty($attribute['enabled'])){continue;}$key=(string)($attribute['key']??'');$def=$defs[$key]??null;if(!is_array($def)||empty($def['enabled'])||empty($def['showDetail'])){continue;}$value=$attribute['value']??'';$empty=is_bool($value)?!$value:trim((string)$value)==='';if($empty){continue;}$label=(string)($def['label']??($attribute['label']??$key));$atype=(string)($def['type']??($attribute['type']??'text'));$rendered=$atype==='richtext'?wp_kses_post((string)$value):($atype==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value)));$custom.='<section class=\"h18-clean-front-event-custom\"><h3>'.esc_html($label).'</h3><div>'.$rendered.'</div></section>';}$detailStyle="
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php', old_desc, new_desc)
replace_once('clean/hangar18-manager/src/Frontend/Renderer.php', ".$summary.$description.'</article>';", ".$summary.$description.$custom.'</article>';")

# Collection renderer: slots, detail-template links, flexible card/detail attributes.
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "use VisualDesignerManager\\Model\\ModuleDesignModel;",
    "use VisualDesignerManager\\Model\\ModuleDesignModel;\nuse VisualDesignerManager\\Modules\\EventFieldRegistry;\nuse VisualDesignerManager\\Migration\\HybridModulePageMigration;")
# Link destinations.
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$url = add_query_arg('h18_event', rawurlencode($id), get_permalink($postId));",
    "$detailPageId = HybridModulePageMigration::detailPageId('events'); $base = $detailPageId > 0 ? get_permalink($detailPageId) : get_permalink($postId); $url = add_query_arg('h18_event', rawurlencode($id), $base);")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$url = add_query_arg('h18_gallery', rawurlencode((string) ($record['id'] ?? '')), get_permalink($postId));",
    "$detailPageId = HybridModulePageMigration::detailPageId('galleries'); $base = $detailPageId > 0 ? get_permalink($detailPageId) : get_permalink($postId); $url = add_query_arg('h18_gallery', rawurlencode((string) ($record['id'] ?? '')), $base);")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$url = add_query_arg('h18_vehicle', rawurlencode((string) ($record['id'] ?? '')), get_permalink($postId));",
    "$detailPageId = HybridModulePageMigration::detailPageId('vehicles'); $base = $detailPageId > 0 ? get_permalink($detailPageId) : get_permalink($postId); $url = add_query_arg('h18_vehicle', rawurlencode((string) ($record['id'] ?? '')), $base);")
# Slots in collection flows.
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$html = self::openPage('events', $title) . self::controls('events', $query, $sort);",
    "$html = self::openPage('events', $title) . HybridModuleSlots::render($postId, 'before') . self::controls('events', $query, $sort);")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$html .= '<section class=\"h18-module-section\"><h2>Tidligere arrangementer</h2>'",
    "$html .= HybridModuleSlots::render($postId, 'between');\n        $html .= '<section class=\"h18-module-section\"><h2>Tidligere arrangementer</h2>'")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "return $html . '</main>';\n    }\n\n    /** @param array<int,array<string,mixed>> $records */",
    "return $html . HybridModuleSlots::render($postId, 'after') . '</main>';\n    }\n\n    /** @param array<int,array<string,mixed>> $records */")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$html = self::openPage('galleries', $title) . self::controls('galleries', $query, $sort) . '<section",
    "$html = self::openPage('galleries', $title) . HybridModuleSlots::render($postId, 'before') . self::controls('galleries', $query, $sort) . HybridModuleSlots::render($postId, 'between') . '<section")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "return $html . '</div></section></main>';\n    }\n\n    private static function vehicles",
    "return $html . '</div></section>' . HybridModuleSlots::render($postId, 'after') . '</main>';\n    }\n\n    private static function vehicles")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "$html = self::openPage('vehicles', $title) . self::controls('vehicles', $query, $sort);",
    "$html = self::openPage('vehicles', $title) . HybridModuleSlots::render($postId, 'before') . self::controls('vehicles', $query, $sort) . HybridModuleSlots::render($postId, 'between');")
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "return $html . '</div></section></main>';\n    }\n\n    private static function eventDetail",
    "return $html . '</div></section>' . HybridModuleSlots::render($postId, 'after') . '</main>';\n    }\n\n    private static function eventDetail")
# Event card configured attributes.
card_anchor = "            $summary = trim((string) ($record['summary'] ?? '')); if ($summary !== '') { $html .= '<p>' . esc_html($summary) . '</p>'; }\n"
card_extra = card_anchor + "            $defs = EventFieldRegistry::byId(); foreach ((array) ($record['attributes'] ?? []) as $attribute) { if (!is_array($attribute) || empty($attribute['enabled'])) { continue; } $key=(string)($attribute['key']??''); $def=$defs[$key]??null; if(!is_array($def)||empty($def['enabled'])||empty($def['showCard'])){continue;} $value=$attribute['value']??''; if(is_bool($value)?!$value:trim((string)$value)===''){continue;} $label=(string)($def['label']??($attribute['label']??$key)); $html .= '<p class=\"h18-module-event-extra\"><strong>'.esc_html($label).':</strong> '.esc_html(is_bool($value)?($value?'Ja':'Nej'):(string)$value).'</p>'; }\n"
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php', card_anchor, card_extra)
# Old direct detail custom fields.
detail_anchor = "        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class=\"h18-module-detail-text\">' . wp_kses_post($description) . '</div>'; }\n        $html .= self::eventGalleryLink($fields);"
detail_new = "        $description = trim((string) ($fields['description'] ?? '')); if ($description !== '') { $html .= '<div class=\"h18-module-detail-text\">' . wp_kses_post($description) . '</div>'; }\n        $defs=EventFieldRegistry::byId(); foreach((array)($record['attributes']??[]) as $attribute){if(!is_array($attribute)||empty($attribute['enabled'])){continue;}$key=(string)($attribute['key']??'');$def=$defs[$key]??null;if(!is_array($def)||empty($def['enabled'])||empty($def['showDetail'])){continue;}$value=$attribute['value']??'';if(is_bool($value)?!$value:trim((string)$value)===''){continue;}$label=(string)($def['label']??($attribute['label']??$key));$type=(string)($def['type']??($attribute['type']??'text'));$rendered=$type==='richtext'?wp_kses_post((string)$value):($type==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value)));$html.='<section class=\"h18-module-event-custom\"><h2>'.esc_html($label).'</h2><div>'.$rendered.'</div></section>';}\n        $html .= self::eventGalleryLink($fields);"
replace_once('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php', detail_anchor, detail_new)

# EventAdminController: targeted flexible-field integration plus field admin screen.
rel = 'clean/hangar18-manager/src/Admin/EventAdminController.php'
replace_once(rel, "use VisualDesignerManager\\Modules\\ModuleStore;", "use VisualDesignerManager\\Modules\\ModuleStore;\nuse VisualDesignerManager\\Modules\\EventFieldRegistry;")
replace_once(rel, "    public const PAGE = 'h18-clean-events';", "    public const PAGE = 'h18-clean-events';\n    public const FIELDS_PAGE = 'h18-clean-event-fields';")
replace_once(rel, "    private const DELETE_ACTION = 'h18_clean_delete_event';", "    private const DELETE_ACTION = 'h18_clean_delete_event';\n    private const FIELD_SAVE_ACTION = 'h18_clean_save_event_fields';")
replace_once(rel, "    private const NONCE_DELETE = 'h18_clean_delete_event';", "    private const NONCE_DELETE = 'h18_clean_delete_event';\n    private const NONCE_FIELDS = 'h18_clean_save_event_fields';")
replace_once(rel, "        add_action('admin_post_' . self::DELETE_ACTION, [self::class, 'deleteEvent']);", "        add_action('admin_post_' . self::DELETE_ACTION, [self::class, 'deleteEvent']);\n        add_action('admin_post_' . self::FIELD_SAVE_ACTION, [self::class, 'saveFields']);")
replace_once(rel, "        if (strpos($hook, self::PAGE) === false || !current_user_can('edit_pages')) { return; }", "        if ((strpos($hook, self::PAGE) === false && strpos($hook, self::FIELDS_PAGE) === false) || !current_user_can('edit_pages')) { return; }")
replace_once(rel, "        wp_enqueue_script('h18-vd-module-media', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.js', [], H18_CLEAN_VERSION, true);", "        wp_enqueue_script('h18-vd-module-media', H18_CLEAN_URL . 'assets/admin-v0170-vehicles.js', [], H18_CLEAN_VERSION, true);\n        wp_enqueue_script('h18-vd-event-fields-v0178', H18_CLEAN_URL . 'assets/admin-v0178-events.js', [], H18_CLEAN_VERSION, true);")
replace_once(rel, "        echo '<div class=\"wrap h18-clean-admin\"><h1>Events</h1><p class=\"description\">Canonical Event-data i fælles ModuleStore. Historiske events slettes ikke automatisk; de kan blive stående publiceret eller arkiveres.</p>';", "        echo '<div class=\"wrap h18-clean-admin\"><h1>Events</h1><p class=\"description\">Canonical Event-data i fælles ModuleStore. Historiske events slettes ikke automatisk; de kan blive stående publiceret eller arkiveres.</p><p><a class=\"button\" href=\"' . esc_url(admin_url('admin.php?page=' . self::FIELDS_PAGE)) . '\">Eventfelter</a></p>';")
# Initialize attribute map in editor.
replace_once(rel, "        $fields = $record !== null && is_array($record['fields'] ?? null) ? $record['fields'] : [];", "        $fields = $record !== null && is_array($record['fields'] ?? null) ? $record['fields'] : [];\n        $attributes = []; foreach ((array) ($record['attributes'] ?? []) as $attribute) { if (is_array($attribute) && !empty($attribute['key'])) { $attributes[(string) $attribute['key']] = $attribute; } }")
# Add custom field controls after description editor.
editor_anchor = "        wp_editor($description, 'h18_event_description', ['textarea_name' => 'description', 'textarea_rows' => 9, 'media_buttons' => false, 'teeny' => true]); echo '</label></div><aside>';"
editor_custom = r'''        wp_editor($description, 'h18_event_description', ['textarea_name' => 'description', 'textarea_rows' => 9, 'media_buttons' => false, 'teeny' => true]); echo '</label>';
        echo '<h3>Eventfelter</h3><p class="description">Felterne styres centralt under Eventfelter. Kun felter med indhold vises på frontend.</p>';
        foreach (EventFieldRegistry::all() as $definition) {
            if (empty($definition['enabled'])) { continue; }
            $key=(string)$definition['id']; $type=(string)$definition['type']; $label=(string)$definition['label']; $value=$attributes[$key]['value']??''; $name='event_custom['.$key.']'; $required=!empty($definition['required'])?' required':'';
            if ($type === 'boolean') { echo '<label class="h18-clean-checkbox"><input type="checkbox" name="'.esc_attr($name).'" value="1"'.checked((bool)$value,true,false).'> '.esc_html($label).'</label>'; }
            elseif ($type === 'richtext') { echo '<label><strong>'.esc_html($label).'</strong>'; wp_editor((string)$value,'h18_event_custom_'.$key,['textarea_name'=>$name,'textarea_rows'=>6,'media_buttons'=>false,'teeny'=>true]); echo '</label>'; }
            elseif ($type === 'textarea') { echo '<label><strong>'.esc_html($label).'</strong><textarea class="widefat" rows="5" name="'.esc_attr($name).'"'.$required.'>'.esc_textarea((string)$value).'</textarea></label>'; }
            else { $inputType=in_array($type,['number','integer'],true)?'number':($type==='date'?'date':($type==='datetime'?'datetime-local':($type==='url'?'url':'text'))); $step=$type==='number'?' step="any"':''; echo '<label><strong>'.esc_html($label).'</strong><input class="widefat" type="'.esc_attr($inputType).'"'.$step.' name="'.esc_attr($name).'" value="'.esc_attr((string)$value).'"'.$required.'></label>'; }
        }
        echo '</div><aside>';'''
replace_once(rel, editor_anchor, editor_custom)
# Save attributes.
save_anchor = "        $raw = ['title' => $title, 'status' => $status, 'summary' => sanitize_textarea_field((string) wp_unslash($_POST['summary'] ?? '')), 'sortOrder' => isset($_POST['sort_order']) ? (int) $_POST['sort_order'] : 0, 'featuredMediaId' => isset($_POST['featured_media_id']) ? absint($_POST['featured_media_id']) : 0, 'fields' => ['start' => $start, 'end' => $end, 'location' => sanitize_text_field((string) wp_unslash($_POST['location'] ?? '')), 'description' => wp_kses_post((string) wp_unslash($_POST['description'] ?? '')), 'galleryRecordId' => sanitize_text_field((string) wp_unslash($_POST['gallery_record_id'] ?? ''))]];"
save_new = r'''        $postedCustom = isset($_POST['event_custom']) && is_array($_POST['event_custom']) ? wp_unslash($_POST['event_custom']) : [];
        $attributes=[]; foreach(EventFieldRegistry::all() as $definition){$key=(string)$definition['id'];$type=(string)$definition['type'];$rawValue=$postedCustom[$key]??($type==='boolean'?false:'');if($type==='richtext'){$value=wp_kses_post((string)$rawValue);}elseif($type==='textarea'){$value=sanitize_textarea_field((string)$rawValue);}elseif($type==='boolean'){$value=!empty($rawValue);}elseif($type==='number'){$value=is_numeric($rawValue)?(float)$rawValue:0.0;}elseif($type==='integer'){$value=(int)$rawValue;}elseif(in_array($type,['date','datetime'],true)){$value=sanitize_text_field((string)$rawValue);}elseif($type==='url'){$value=esc_url_raw((string)$rawValue);}else{$value=sanitize_text_field((string)$rawValue);}if(!empty($definition['required'])&&(is_bool($value)?!$value:trim((string)$value)==='')){self::redirect('error','Feltet “'.(string)$definition['label'].'” er påkrævet.',$postId);} $attributes[]=['key'=>$key,'label'=>(string)$definition['label'],'type'=>$type,'value'=>$value,'enabled'=>!empty($definition['enabled']),'order'=>(int)$definition['order']];}
        $raw = ['title' => $title, 'status' => $status, 'summary' => sanitize_textarea_field((string) wp_unslash($_POST['summary'] ?? '')), 'sortOrder' => isset($_POST['sort_order']) ? (int) $_POST['sort_order'] : 0, 'featuredMediaId' => isset($_POST['featured_media_id']) ? absint($_POST['featured_media_id']) : 0, 'fields' => ['start' => $start, 'end' => $end, 'location' => sanitize_text_field((string) wp_unslash($_POST['location'] ?? '')), 'description' => wp_kses_post((string) wp_unslash($_POST['description'] ?? '')), 'galleryRecordId' => sanitize_text_field((string) wp_unslash($_POST['gallery_record_id'] ?? ''))], 'attributes'=>$attributes];'''
replace_once(rel, save_anchor, save_new)
# Insert renderFields/saveFields before deleteEvent.
field_admin = r'''
    public static function renderFields(): void
    {
        if (!current_user_can('edit_pages')) { wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager')); }
        $rows=EventFieldRegistry::all(); $state=sanitize_key((string)($_GET['h18_status']??'')); $message=sanitize_text_field((string)wp_unslash($_GET['h18_message']??''));
        echo '<div class="wrap h18-clean-admin"><h1>Eventfelter</h1><p class="description">Definér genbrugelige felter til arrangementer. Felt-ID bevares stabilt ved omdøbning.</p><p><a class="button" href="'.esc_url(admin_url('admin.php?page='.self::PAGE)).'">← Events</a></p>';
        if($message!==''){echo '<div class="notice '.($state==='error'?'notice-error':'notice-success').' is-dismissible"><p>'.esc_html($message).'</p></div>';}
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_FIELDS);echo '<input type="hidden" name="action" value="'.esc_attr(self::FIELD_SAVE_ACTION).'"><div class="h18-manager-card"><div class="h18-vd-field-toolbar"><h2>Felter</h2><button type="button" class="button" id="h18-vd-add-event-field">+ Tilføj felt</button></div><div id="h18-vd-event-field-rows">';
        foreach($rows as $row){self::eventFieldRow($row);} echo '</div><p><button class="button button-primary" type="submit">Gem Eventfelter</button></p></div></form></div>';
    }

    /** @param array<string,mixed> $row */
    private static function eventFieldRow(array $row): void
    {
        echo '<div class="h18-vd-field-row" data-event-field-row><input type="hidden" name="event_field_id[]" value="'.esc_attr((string)$row['id']).'"><label>Navn<input required type="text" name="event_field_label[]" value="'.esc_attr((string)$row['label']).'"></label><label>Type<select name="event_field_type[]">';
        foreach(['richtext'=>'Rich text','text'=>'Tekst','textarea'=>'Flere linjer','number'=>'Tal','integer'=>'Heltal','boolean'=>'Ja/nej','date'=>'Dato','datetime'=>'Dato/tid','url'=>'Link'] as $type=>$label){echo '<option value="'.esc_attr($type).'"'.selected((string)$row['type'],$type,false).'>'.esc_html($label).'</option>';}
        echo '</select></label><label>Rækkefølge<input type="number" name="event_field_order[]" value="'.esc_attr((string)(int)$row['order']).'"></label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_enabled[]" value="'.esc_attr((string)$row['id']).'"'.checked(!empty($row['enabled']),true,false).'> Aktiv</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_required[]" value="'.esc_attr((string)$row['id']).'"'.checked(!empty($row['required']),true,false).'> Påkrævet</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_card[]" value="'.esc_attr((string)$row['id']).'"'.checked(!empty($row['showCard']),true,false).'> På kort</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_detail[]" value="'.esc_attr((string)$row['id']).'"'.checked(!empty($row['showDetail']),true,false).'> På detalje</label><button type="button" class="button-link-delete h18-vd-remove-event-field">Fjern</button></div>';
    }

    public static function saveFields(): void
    {
        if(!current_user_can('edit_pages')){wp_die(esc_html__('Ingen adgang.','visual-designer-manager'));}check_admin_referer(self::NONCE_FIELDS);
        $ids=is_array($_POST['event_field_id']??null)?wp_unslash($_POST['event_field_id']):[];$labels=is_array($_POST['event_field_label']??null)?wp_unslash($_POST['event_field_label']):[];$types=is_array($_POST['event_field_type']??null)?wp_unslash($_POST['event_field_type']):[];$orders=is_array($_POST['event_field_order']??null)?wp_unslash($_POST['event_field_order']):[];
        $enabled=array_flip(array_map('sanitize_key',is_array($_POST['event_field_enabled']??null)?wp_unslash($_POST['event_field_enabled']):[]));$required=array_flip(array_map('sanitize_key',is_array($_POST['event_field_required']??null)?wp_unslash($_POST['event_field_required']):[]));$card=array_flip(array_map('sanitize_key',is_array($_POST['event_field_card']??null)?wp_unslash($_POST['event_field_card']):[]));$detail=array_flip(array_map('sanitize_key',is_array($_POST['event_field_detail']??null)?wp_unslash($_POST['event_field_detail']):[]));
        $rows=[];foreach($labels as $i=>$label){$id=sanitize_key((string)($ids[$i]??''));$rows[]=['id'=>$id,'label'=>sanitize_text_field((string)$label),'type'=>sanitize_key((string)($types[$i]??'text')),'order'=>(int)($orders[$i]??(($i+1)*10)),'enabled'=>$id===''?true:isset($enabled[$id]),'required'=>$id!==''&&isset($required[$id]),'showCard'=>$id!==''&&isset($card[$id]),'showDetail'=>$id===''?true:isset($detail[$id])];}
        EventFieldRegistry::save($rows);wp_safe_redirect(add_query_arg(['page'=>self::FIELDS_PAGE,'h18_status'=>'ok','h18_message'=>'Eventfelter gemt.'],admin_url('admin.php')));exit;
    }
'''
replace_once(rel, "    public static function deleteEvent(): void", field_admin + "\n    public static function deleteEvent(): void")

# Admin menu entry.
replace_once('clean/hangar18-manager/src/Admin/AdminController.php',
    "        add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [EventAdminController::class, 'render']);",
    "        add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [EventAdminController::class, 'render']);\n        add_submenu_page(self::MENU, 'Eventfelter', 'Eventfelter', $cap, 'h18-clean-event-fields', [EventAdminController::class, 'renderFields']);")

# EditorController: Eventfelt palette, content/module tabs, normal canvas by default on collection pages.
replace_once('clean/hangar18-manager/src/Admin/EditorController.php',
    "        $isCollectionPage = CollectionPageRenderer::supports($postId);",
    "        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $collectionMode = $isCollectionPage && sanitize_key((string) ($_GET['h18_collection_mode'] ?? 'content')) === 'module' ? 'module' : 'content';")
replace_once('clean/hangar18-manager/src/Admin/EditorController.php',
    "        echo '<a class=\"button\" target=\"_blank\" rel=\"noopener\" href=\"' . esc_url(get_permalink($postId)) . '\">Vis offentlig side</a>';",
    "        echo '<a class=\"button\" target=\"_blank\" rel=\"noopener\" href=\"' . esc_url(get_permalink($postId)) . '\">Vis offentlig side</a>';\n        if ($isCollectionPage) { echo '<a class=\"button ' . ($collectionMode === 'content' ? 'button-primary' : '') . '\" href=\"' . esc_url(add_query_arg(['page'=>self::MENU,'post'=>$postId,'h18_collection_mode'=>'content'], admin_url('admin.php'))) . '\">Indholdselementer</a><a class=\"button ' . ($collectionMode === 'module' ? 'button-primary' : '') . '\" href=\"' . esc_url(add_query_arg(['page'=>self::MENU,'post'=>$postId,'h18_collection_mode'=>'module'], admin_url('admin.php'))) . '\">Moduldesign</a>'; }")
replace_once('clean/hangar18-manager/src/Admin/EditorController.php', "        if ($isCollectionPage) {", "        if ($isCollectionPage && $collectionMode === 'module') {")
replace_once('clean/hangar18-manager/src/Admin/EditorController.php',
    "                'gallerylist' => 'Gallerioversigt', 'gallerydetail' => 'Albumvisning',",
    "                'gallerylist' => 'Gallerioversigt', 'gallerydetail' => 'Albumvisning', 'eventfield' => 'Eventfelt',")

# Core JS: slot property + Eventfelt support.
js='clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(js, "'gallerylist', 'gallerydetail', 'contactform'", "'gallerylist', 'gallerydetail', 'eventfield', 'contactform'")
replace_once(js, "gallerydetail:'Albumvisning',contactform", "gallerydetail:'Albumvisning',eventfield:'Eventfelt',contactform")
# Normalize section moduleSlot after minHeightRows marker.
replace_once(js, "minHeightRows: clamp(parseInt(raw.minHeightRows || 0, 10) || 0, 0, 4000)", "minHeightRows: clamp(parseInt(raw.minHeightRows || 0, 10) || 0, 0, 4000), moduleSlot: type === 'section' && ['before','between','after'].includes(String(raw.moduleSlot||'before')) ? String(raw.moduleSlot||'before') : 'before'")
# Eventfield normalize before gallerylist.
js_anchor="        if (type === 'gallerylist') {"
js_eventfield=r'''        if (type === 'eventfield') {
            const key=String(raw.fieldKey||'about').toLowerCase().replace(/[^a-z0-9_-]/g,''); const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{fieldKey:key||'about',recordId:recordId,showHeading:raw.showHeading!==false,background:/^#[0-9a-f]{6}$/i.test(String(raw.background||''))?String(raw.background).toLowerCase():'',textColor:normalizeColor(raw.textColor||'#30382a'),padding:clamp(parseInt(raw.padding||0,10)||0,0,80),radius:clamp(parseInt(raw.radius||0,10)||0,0,60)});
        }
'''
replace_once(js, js_anchor, js_eventfield+js_anchor)
replace_once(js, "gallerydetail: 52, contactform", "gallerydetail: 52, eventfield: 18, contactform")
# Eventfield preview before gallerylist preview.
preview_anchor="        } else if (node.type === 'gallerylist') {"
preview_code=r'''        } else if (node.type === 'eventfield') {
            wrap.classList.add('h18-clean-node-preview--eventfield'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; const def=defs.find(function(row){return String(row.id||'')===String(node.props.fieldKey||'');})||null; const attr=record&&Array.isArray(record.attributes)?record.attributes.find(function(row){return row&&String(row.key||'')===String(node.props.fieldKey||'');}):null; const box=document.createElement('div');box.style.padding=String(node.props.padding||0)+'px';box.style.borderRadius=String(node.props.radius||0)+'px';box.style.color=node.props.textColor||'#30382a';if(node.props.background){box.style.background=node.props.background;} if(!record||!attr||String(attr.value==null?'':attr.value)===''){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{if(node.props.showHeading!==false){const h=document.createElement('h3');h.textContent=String(def&&def.label||attr.label||node.props.fieldKey);box.appendChild(h);}const value=document.createElement('div'); if(String(def&&def.type||attr.type)==='richtext'){value.innerHTML=richPreviewHtml(String(attr.value||''));}else{value.textContent=typeof attr.value==='boolean'?(attr.value?'Ja':'Nej'):String(attr.value);}box.appendChild(value);}wrap.appendChild(box);
'''
replace_once(js, preview_anchor, preview_code+preview_anchor)
# Eventfield inspector before gallerylist inspector.
inspector_anchor="        } else if (node.type === 'gallerylist') {"
inspector_code=r'''        } else if (node.type === 'eventfield') {
            const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; html += '<div class="h18-vd-menu-group"><h3>Eventfelt</h3><label>Felt<select data-field="eventFieldKey">'+defs.map(function(row){return '<option value="'+escapeAttr(String(row.id||''))+'"'+(String(node.props.fieldKey||'')===String(row.id||'')?' selected':'')+'>'+escapeHtml(String(row.label||row.id||'Felt'))+'</option>';}).join('')+'</select></label><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label class="h18-clean-checkbox"><input data-field="eventFieldShowHeading" type="checkbox"'+(node.props.showHeading!==false?' checked':'')+'> Vis feltoverskrift</label><div class="h18-clean-field-grid"><label>Padding<input data-field="padding" type="number" min="0" max="80" value="'+String(node.props.padding||0)+'"></label><label>Hjørner<input data-field="radius" type="number" min="0" max="60" value="'+String(node.props.radius||0)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label></div></div>';
'''
replace_once(js, inspector_anchor, inspector_code+inspector_anchor)
# Input handlers.
replace_once(js, "                else if (field === 'eventShowDescription') { current.props.showDescription=!!control.checked; }", "                else if (field === 'eventShowDescription') { current.props.showDescription=!!control.checked; }\n                else if (field === 'eventFieldKey') { current.props.fieldKey=String(control.value||'about'); }\n                else if (field === 'eventFieldShowHeading') { current.props.showHeading=!!control.checked; }\n                else if (field === 'moduleSlot') { current.props.moduleSlot=['before','between','after'].includes(String(control.value||''))?String(control.value):'before'; }")
# Section inspector slot control: insert before closing section menu based on min height label anchor.
replace_once(js, "<label>Minimumshøjde", "<label>Placering på modulside<select data-field=\"moduleSlot\"><option value=\"before\"'+(node.props.moduleSlot==='before'?' selected':'')+'>Før modulindhold</option><option value=\"between\"'+(node.props.moduleSlot==='between'?' selected':'')+'>Mellem modulsektioner</option><option value=\"after\"'+(node.props.moduleSlot==='after'?' selected':'')+'>Efter modulindhold</option></select></label><label>Minimumshøjde")

# Version bump + release metadata.
replace_once('clean/hangar18-manager/hangar18-manager.php', 'Version: 0.1.77', 'Version: 0.1.78')
replace_once('clean/hangar18-manager/hangar18-manager.php', "H18_CLEAN_VERSION', '0.1.77'", "H18_CLEAN_VERSION', '0.1.78'")

history_path='clean/hangar18-manager/release-history.json'
history=json.loads(read(history_path)); versions=history.get('versions',[]) if isinstance(history,dict) else []
if not any(isinstance(row,dict) and row.get('version')=='0.1.78' for row in versions):
    versions.insert(0, {'version':'0.1.78','date':'2026-09-01','items':[
        'VD-HYBRID-MODULE-PAGES-001: Events, Billedgalleri og Køretøjer har Designer-slots før/mellem/efter den dynamiske flow-renderer.',
        'Moduldesign fra v0.1.77 bevares som separat Designer-tilstand, mens Indholdselementer er standardtilstand.',
        'Eventdetalje, Albumdetalje og Køretøjsdetalje provisioneres som normale Visual Designer-sider og bruges som nye detailmål.',
        'EVENT-FIELDS-001: fleksible Eventfelter med stabile IDer, typer, rækkefølge, aktiv/påkrævet og kort/detalje-visning.',
        'Standardfelter er Om arrangementet, Program og Praktiske oplysninger; Eventfelt kan placeres selvstændigt i Designer.',
        'Eksisterende modulrecords bevares; tidligere layouts sikkerhedskopieres før hybrid-slot migration.'
    ]})
    history['versions']=versions; write(history_path,json.dumps(history,ensure_ascii=False,indent=2)+'\n')

write('clean-release-notes.html', '''<h2>0.1.78 – Hybrid modulsider og fleksible Eventfelter</h2>\n<ul>\n<li><strong>Events, Billedgalleri og Køretøjer:</strong> almindelige Visual Designer-elementer kan placeres før, mellem og efter det dynamiske modulindhold.</li>\n<li>Den eksisterende flow-baserede CollectionPageRenderer bevares, så søgning, sortering, eventarkiv og automatisk indholdshøjde fortsat fungerer.</li>\n<li>Moduldesign fra 0.1.77 ligger fortsat som en separat tilstand; Indholdselementer er nu standardtilstanden.</li>\n<li>Eventdetalje, Albumdetalje og Køretøjsdetalje er genbrugelige Visual Designer-sider, hvor almindelige elementer kan sættes omkring de dynamiske detailblokke.</li>\n<li><strong>Eventfelter:</strong> opret, fjern, omdøb og sorter felter med type, aktiv/påkrævet og visning på kort/detalje.</li>\n<li>Standard Eventfelter: <strong>Om arrangementet</strong>, <strong>Program</strong> og <strong>Praktiske oplysninger</strong>.</li>\n<li>Nyt Designer-element <strong>Eventfelt</strong> kan vise et bestemt fleksibelt Eventfelt separat på detail-skabelonen.</li>\n</ul>\n''')

backlog='docs/clean-backlog-v0100.md'; value=read(backlog)
value=value.replace('**Aktuel release:** v0.1.77','**Aktuel release:** v0.1.78')
value=value.replace('## Aktuel milepælsstatus · v0.1.77','## Aktuel milepælsstatus · v0.1.78')
marker='8. **v0.1.76 – VD-MODULE-VISUAL-PARITY-002 — FÆRDIG:** Events, Billedgalleri og Køretøjer bruger samme canonical frontend-rendering i Designer-preview; kortgeometri, billeder, beige kortkrop, spacing og responsive regler er justeret mod `_old`.\n'
if marker in value and 'v0.1.78 – Hybrid modulsider' not in value:
    value=value.replace(marker,marker+'9. **v0.1.77 – Redigerbart moduldesign — FÆRDIG:** Moduldesign kan ændres for de tre dynamiske sider med canonical frontend-preview.\n10. **v0.1.78 – Hybrid modulsider + Eventfelter — FÆRDIG:** almindelige Designer-elementer i før/mellem/efter-slots, Designer-detailpages og fleksible Eventfelter.\n')
if '### VD-HYBRID-MODULE-PAGES-001' not in value:
    value += '\n### VD-HYBRID-MODULE-PAGES-001 — FÆRDIG I v0.1.78\n- Events, Billedgalleri og Køretøjer beholder flow-rendereren og får Designer-slots før/mellem/efter.\n- Moduldesign bevares som separat tilstand.\n- Detailvisninger provisioneres som normale Designer-sider.\n- EVENT-FIELDS-001 giver fleksible felter med standarderne Om arrangementet, Program og Praktiske oplysninger.\n- Eventfelt er et selvstændigt dynamisk Designer-element.\n'
write(backlog,value)

print('Applied Visual Designer Manager v0.1.78 hybrid pages + Event fields changes.')
