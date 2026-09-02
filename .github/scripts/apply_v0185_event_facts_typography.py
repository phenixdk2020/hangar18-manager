from pathlib import Path
import json

VERSION = '0.1.85'
PREVIOUS = '0.1.84'


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, value):
    Path(path).write_text(value, encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Bootstrap/version
# ---------------------------------------------------------------------------
plugin_path = Path('clean/hangar18-manager/hangar18-manager.php')
plugin = read(plugin_path)
if f'Version: {VERSION}' not in plugin:
    plugin = replace_once(plugin, f' * Version: {PREVIOUS}', f' * Version: {VERSION}', 'plugin header version')
    plugin = replace_once(plugin, f"define('VDM_VERSION', '{PREVIOUS}');", f"define('VDM_VERSION', '{VERSION}');", 'VDM version')
    plugin = replace_once(plugin, f"define('H18_CLEAN_VERSION', '{PREVIOUS}');", f"define('H18_CLEAN_VERSION', '{VERSION}');", 'compat version')

migration_require = "require_once H18_CLEAN_DIR . 'src/Migration/EventDetailFactsMigration.php';\n"
if migration_require not in plugin:
    anchor = "require_once H18_CLEAN_DIR . 'src/Migration/HybridModulePageMigration.php';\n"
    plugin = replace_once(plugin, anchor, anchor + migration_require, 'event facts migration require')

migration_register = "    \\VisualDesignerManager\\Migration\\EventDetailFactsMigration::register();\n"
if migration_register not in plugin:
    anchor = "    \\VisualDesignerManager\\Migration\\HybridModulePageMigration::register();\n"
    plugin = replace_once(plugin, anchor, anchor + migration_register, 'event facts migration register')
write(plugin_path, plugin)


# ---------------------------------------------------------------------------
# LayoutModel: Eventfaktabånd + Eventfelt typography
# ---------------------------------------------------------------------------
layout_path = Path('clean/hangar18-manager/src/Model/LayoutModel.php')
layout = read(layout_path)
layout = replace_once(
    layout,
    "'eventlist', 'eventdetail', 'eventvalue', 'eventimage', 'gallerylist', 'gallerydetail', 'eventfield'",
    "'eventlist', 'eventdetail', 'eventvalue', 'eventimage', 'eventfacts', 'gallerylist', 'gallerydetail', 'eventfield'",
    'LayoutModel allowed eventfacts type',
) if "'eventfacts'" not in layout.split('if ($type === \'eventfield\')', 1)[0] else layout

if "if ($type === 'eventfacts')" not in layout:
    anchor = """        if ($type === 'eventfield') {
"""
    eventfacts_block = """        if ($type === 'eventfacts') {
            $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            return array_merge([
                'recordId' => $recordId,
                'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true,
                'showTime' => array_key_exists('showTime', $raw) ? (bool) $raw['showTime'] : true,
                'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true,
                'showAddress' => array_key_exists('showAddress', $raw) ? (bool) $raw['showAddress'] : true,
                'showContact' => array_key_exists('showContact', $raw) ? (bool) $raw['showContact'] : true,
                'gap' => self::clamp($raw['gap'] ?? 12, 0, 80, 12),
                'minCardWidth' => self::clamp($raw['minCardWidth'] ?? 150, 100, 360, 150),
                'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#f4f1e8')) ?: '#f4f1e8',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'labelColor' => sanitize_hex_color((string) ($raw['labelColor'] ?? '#30382a')) ?: '#30382a',
                'valueColor' => sanitize_hex_color((string) ($raw['valueColor'] ?? '#30382a')) ?: '#30382a',
                'paddingX' => self::clamp($raw['paddingX'] ?? 16, 0, 80, 16),
                'paddingY' => self::clamp($raw['paddingY'] ?? 16, 0, 80, 16),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 60, 0),
                'labelFontFamily' => self::fontToken($raw['labelFontFamily'] ?? 'system', false),
                'labelFontSize' => self::clamp($raw['labelFontSize'] ?? 16, 8, 80, 16),
                'labelFontWeight' => self::clamp($raw['labelFontWeight'] ?? 700, 100, 900, 700),
                'valueFontFamily' => self::fontToken($raw['valueFontFamily'] ?? 'system', false),
                'valueFontSize' => self::clamp($raw['valueFontSize'] ?? 16, 8, 80, 16),
                'valueFontWeight' => self::clamp($raw['valueFontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.35, 0.8, 3.0, 1.35),
            ], $border);
        }

"""
    layout = replace_once(layout, anchor, eventfacts_block + anchor, 'LayoutModel eventfacts props')

old_eventfield = """            return array_merge([
                'fieldKey' => $fieldKey !== '' ? $fieldKey : 'about',
                'recordId' => $recordId,
                'showHeading' => array_key_exists('showHeading', $raw) ? (bool) $raw['showHeading'] : true,
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '')) ?: '',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 80, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 60, 0),
            ], $border);
"""
new_eventfield = """            return array_merge([
                'fieldKey' => $fieldKey !== '' ? $fieldKey : 'about',
                'recordId' => $recordId,
                'showHeading' => array_key_exists('showHeading', $raw) ? (bool) $raw['showHeading'] : true,
                'showWhenEmpty' => array_key_exists('showWhenEmpty', $raw) ? (bool) $raw['showWhenEmpty'] : false,
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '')) ?: '',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 400, 100, 900, 400),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.5, 0.8, 3.0, 1.5),
                'headingColor' => sanitize_hex_color((string) ($raw['headingColor'] ?? '#30382a')) ?: '#30382a',
                'headingFontFamily' => self::fontToken($raw['headingFontFamily'] ?? 'body', true),
                'headingFontSize' => self::clamp($raw['headingFontSize'] ?? 40, 8, 160, 40),
                'headingFontWeight' => self::clamp($raw['headingFontWeight'] ?? 400, 100, 900, 400),
                'headingLineHeight' => self::clampFloat($raw['headingLineHeight'] ?? 1.15, 0.8, 3.0, 1.15),
                'headingGap' => self::clamp($raw['headingGap'] ?? 12, 0, 80, 12),
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 80, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 60, 0),
            ], $border);
"""
if "'showWhenEmpty'" not in layout:
    layout = replace_once(layout, old_eventfield, new_eventfield, 'LayoutModel eventfield typography')
write(layout_path, layout)


# ---------------------------------------------------------------------------
# Renderer: Eventfaktabånd + Eventfelt typography/empty heading
# ---------------------------------------------------------------------------
renderer_path = Path('clean/hangar18-manager/src/Frontend/Renderer.php')
renderer = read(renderer_path)
if "if ($type === 'eventfacts')" not in renderer:
    anchor = """        if ($type === 'eventfield') {
"""
    block = """        if ($type === 'eventfacts') {
            $recordId = strtolower(trim((string) ($props['recordId'] ?? '')));
            if ($recordId === '') { $recordId = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET['h18_event'] ?? '')))); }
            if ($recordId !== '' && !preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) { $recordId = ''; }
            $found = $recordId !== '' ? ModuleStore::findByRecordId('events', $recordId) : null;
            $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
            $allowDraft = self::$forceStandaloneCss && current_user_can('edit_pages');
            if ($record === null || ((string) ($record['status'] ?? 'draft') !== 'publish' && !$allowDraft)) {
                return self::$forceStandaloneCss ? '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($style . $borderStyle . $spacingStyle) . '">Eventfaktabånd · vælg event eller brug ?h18_event=record-id</div>' : '';
            }
            $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
            $facts = [];
            if (!empty($props['showDate'])) { $facts[] = ['Dato', self::eventFactDateLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? ''))]; }
            if (!empty($props['showTime'])) { $facts[] = ['Tid', self::eventFactTimeLabel((string) ($fields['start'] ?? ''), (string) ($fields['end'] ?? ''))]; }
            if (!empty($props['showLocation'])) { $facts[] = ['Sted', (string) ($fields['location'] ?? '')]; }
            if (!empty($props['showAddress'])) { $facts[] = ['Adresse', (string) ($fields['address'] ?? '')]; }
            if (!empty($props['showContact'])) { $facts[] = ['Kontakt', (string) ($fields['contact'] ?? '')]; }
            if (!$facts) { return ''; }
            $gap = max(0, min(80, (int) ($props['gap'] ?? 12)));
            $minCardWidth = max(100, min(360, (int) ($props['minCardWidth'] ?? 150)));
            $cardBackground = sanitize_hex_color((string) ($props['cardBackground'] ?? '#f4f1e8')) ?: '#f4f1e8';
            $accentColor = sanitize_hex_color((string) ($props['accentColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $labelColor = sanitize_hex_color((string) ($props['labelColor'] ?? '#30382a')) ?: '#30382a';
            $valueColor = sanitize_hex_color((string) ($props['valueColor'] ?? '#30382a')) ?: '#30382a';
            $paddingX = max(0, min(80, (int) ($props['paddingX'] ?? 16)));
            $paddingY = max(0, min(80, (int) ($props['paddingY'] ?? 16)));
            $radius = max(0, min(60, (int) ($props['radius'] ?? 0)));
            $labelSize = max(8, min(80, (int) ($props['labelFontSize'] ?? 16)));
            $labelWeight = max(100, min(900, (int) ($props['labelFontWeight'] ?? 700)));
            $valueSize = max(8, min(80, (int) ($props['valueFontSize'] ?? 16)));
            $valueWeight = max(100, min(900, (int) ($props['valueFontWeight'] ?? 400)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.35)));
            $labelFamily = self::fontCss((string) ($props['labelFontFamily'] ?? 'system'));
            $valueFamily = self::fontCss((string) ($props['valueFontFamily'] ?? 'system'));
            $cards = '';
            foreach ($facts as $fact) {
                $cardStyle = 'min-width:0;background:' . $cardBackground . ';border-left:4px solid ' . $accentColor . ';border-radius:' . $radius . 'px;padding:' . $paddingY . 'px ' . $paddingX . 'px;';
                $labelStyle = 'display:block;color:' . $labelColor . ';font-family:' . $labelFamily . ';font-size:' . $labelSize . 'px;font-weight:' . $labelWeight . ';line-height:' . $lineHeight . ';margin:0 0 4px;';
                $valueStyle = 'display:block;color:' . $valueColor . ';font-family:' . $valueFamily . ';font-size:' . $valueSize . 'px;font-weight:' . $valueWeight . ';line-height:' . $lineHeight . ';overflow-wrap:anywhere;';
                $cards .= '<div class="h18-clean-front-event-fact" style="' . esc_attr($cardStyle) . '"><strong style="' . esc_attr($labelStyle) . '">' . esc_html((string) $fact[0]) . '</strong><span style="' . esc_attr($valueStyle) . '">' . esc_html((string) $fact[1]) . '</span></div>';
            }
            $gridStyle = $style . $borderStyle . $spacingStyle . 'display:grid;grid-template-columns:repeat(auto-fit,minmax(' . $minCardWidth . 'px,1fr));gap:' . $gap . 'px;align-items:stretch;';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-event-facts" style="' . esc_attr($gridStyle) . '">' . $cards . '</div>';
        }

"""
    renderer = replace_once(renderer, anchor, block + anchor, 'Renderer eventfacts')

old_render_field = """            $value=$attribute['value']??'';if(is_bool($value)){$empty=!$value;}else{$empty=trim((string)$value)==='';}if($empty){return '';}
            $label=(string)($def['label']??($attribute['label']??$fieldKey));$type=(string)($def['type']??($attribute['type']??'text'));$content=$type==='richtext'?wp_kses_post((string)$value):($type==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value)));
            $heading=!empty($props['showHeading'])?'<h3 class="h18-clean-front-event-field-heading">'.esc_html($label).'</h3>':'';$bg=sanitize_hex_color((string)($props['background']??''))?:'';$color=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a';$padding=max(0,min(80,(int)($props['padding']??0)));$radius=max(0,min(60,(int)($props['radius']??0)));$extra=($bg!==''?'background:'.$bg.';':'').'color:'.$color.';padding:'.$padding.'px;border-radius:'.$radius.'px;';
            return '<section id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-field" style="'.esc_attr($style.$borderStyle.$spacingStyle.$extra).'">'.$heading.'<div class="h18-clean-front-event-field-value">'.$content.'</div></section>';
"""
new_render_field = """            $value=$attribute['value']??'';if(is_bool($value)){$empty=!$value;}else{$empty=trim((string)$value)==='';}if($empty&&empty($props['showWhenEmpty'])){return '';}
            $label=(string)($def['label']??($attribute['label']??$fieldKey));$type=(string)($def['type']??($attribute['type']??'text'));$content=$empty?'':($type==='richtext'?wp_kses_post((string)$value):($type==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value))));
            $bg=sanitize_hex_color((string)($props['background']??''))?:'';$color=sanitize_hex_color((string)($props['textColor']??'#30382a'))?:'#30382a';$headingColor=sanitize_hex_color((string)($props['headingColor']??'#30382a'))?:'#30382a';$padding=max(0,min(80,(int)($props['padding']??0)));$radius=max(0,min(60,(int)($props['radius']??0)));$fontSize=max(8,min(120,(int)($props['fontSize']??16)));$fontWeight=max(100,min(900,(int)($props['fontWeight']??400)));$lineHeight=max(0.8,min(3.0,(float)($props['lineHeight']??1.5)));$headingSize=max(8,min(160,(int)($props['headingFontSize']??40)));$headingWeight=max(100,min(900,(int)($props['headingFontWeight']??400)));$headingLineHeight=max(0.8,min(3.0,(float)($props['headingLineHeight']??1.15)));$headingGap=max(0,min(80,(int)($props['headingGap']??12)));$extra=($bg!==''?'background:'.$bg.';':'').'color:'.$color.';font-family:'.self::fontCss((string)($props['fontFamily']??'system')).';font-size:'.$fontSize.'px;font-weight:'.$fontWeight.';line-height:'.$lineHeight.';padding:'.$padding.'px;border-radius:'.$radius.'px;';
            $headingStyle='margin:0 0 '.$headingGap.'px;color:'.$headingColor.';font-family:'.self::fontCss((string)($props['headingFontFamily']??'body')).';font-size:'.$headingSize.'px;font-weight:'.$headingWeight.';line-height:'.$headingLineHeight.';';$heading=!empty($props['showHeading'])?'<h3 class="h18-clean-front-event-field-heading" style="'.esc_attr($headingStyle).'">'.esc_html($label).'</h3>':'';$valueHtml=$content!==''?'<div class="h18-clean-front-event-field-value">'.$content.'</div>':'';
            return '<section id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-field" style="'.esc_attr($style.$borderStyle.$spacingStyle.$extra).'">'.$heading.$valueHtml.'</section>';
"""
if "headingGap=max(0,min(80" not in renderer:
    renderer = replace_once(renderer, old_render_field, new_render_field, 'Renderer eventfield typography')

if 'private static function eventFactDateLabel' not in renderer:
    anchor = """    private static function eventDateLabel(string $start, string $end = ''): string
"""
    helpers = """    private static function eventFactDateLabel(string $start, string $end = ''): string
    {
        $render = static function (string $value): string {
            $value = trim($value);
            if (preg_match('/^(\\d{4})-(\\d{2})-(\\d{2})T\\d{2}:\\d{2}/', $value, $m) !== 1) { return ''; }
            return $m[3] . '-' . $m[2] . '-' . $m[1];
        };
        $startLabel = $render($start); $endLabel = $render($end);
        if ($startLabel === '') { return $endLabel; }
        return $endLabel !== '' && $endLabel !== $startLabel ? ($startLabel . ' – ' . $endLabel) : $startLabel;
    }

    private static function eventFactTimeLabel(string $start, string $end = ''): string
    {
        $render = static function (string $value): string {
            $value = trim($value);
            return preg_match('/^\\d{4}-\\d{2}-\\d{2}T(\\d{2}:\\d{2})/', $value, $m) === 1 ? $m[1] : '';
        };
        $startLabel = $render($start); $endLabel = $render($end);
        if ($startLabel === '') { return $endLabel; }
        return $endLabel !== '' ? ($startLabel . ' – ' . $endLabel) : $startLabel;
    }

"""
    renderer = replace_once(renderer, anchor, helpers + anchor, 'Renderer fact date/time helpers')
write(renderer_path, renderer)


# ---------------------------------------------------------------------------
# Event manager: address/contact + row-index-safe EventFieldRegistry form
# ---------------------------------------------------------------------------
event_admin_path = Path('clean/hangar18-manager/src/Admin/EventAdminController.php')
event_admin = read(event_admin_path)
old_vars = "$start = self::dateTimeInput((string) ($fields['start'] ?? '')); $end = self::dateTimeInput((string) ($fields['end'] ?? '')); $location = (string) ($fields['location'] ?? ''); $description = (string) ($fields['description'] ?? '');"
new_vars = "$start = self::dateTimeInput((string) ($fields['start'] ?? '')); $end = self::dateTimeInput((string) ($fields['end'] ?? '')); $location = (string) ($fields['location'] ?? ''); $address = (string) ($fields['address'] ?? ''); $contact = (string) ($fields['contact'] ?? ''); $description = (string) ($fields['description'] ?? '');"
if "$address = (string) ($fields['address']" not in event_admin:
    event_admin = replace_once(event_admin, old_vars, new_vars, 'Event admin address/contact vars')

old_location_html = "</label></div><label><strong>Sted</strong><input class=\"widefat\" type=\"text\" name=\"location\" value=\"' . esc_attr($location) . '\"></label><label><strong>Kort beskrivelse</strong>"
new_location_html = "</label></div><label><strong>Sted</strong><input class=\"widefat\" type=\"text\" name=\"location\" value=\"' . esc_attr($location) . '\"></label><div class=\"h18-clean-field-grid\"><label><strong>Adresse</strong><input class=\"widefat\" type=\"text\" name=\"address\" value=\"' . esc_attr($address) . '\"></label><label><strong>Kontakt</strong><input class=\"widefat\" type=\"text\" name=\"contact\" value=\"' . esc_attr($contact) . '\"></label></div><label><strong>Kort beskrivelse</strong>"
if 'name="address"' not in event_admin:
    event_admin = replace_once(event_admin, old_location_html, new_location_html, 'Event admin address/contact inputs')

old_fields_save = "'fields' => ['start' => $start, 'end' => $end, 'location' => sanitize_text_field((string) wp_unslash($_POST['location'] ?? '')), 'description'"
new_fields_save = "'fields' => ['start' => $start, 'end' => $end, 'location' => sanitize_text_field((string) wp_unslash($_POST['location'] ?? '')), 'address' => sanitize_text_field((string) wp_unslash($_POST['address'] ?? '')), 'contact' => sanitize_text_field((string) wp_unslash($_POST['contact'] ?? '')), 'description'"
if "'address' => sanitize_text_field" not in event_admin:
    event_admin = replace_once(event_admin, old_fields_save, new_fields_save, 'Event admin address/contact save')

if "eventFieldRow($row,$index)" not in event_admin:
    event_admin = replace_once(event_admin, "foreach($rows as $row){self::eventFieldRow($row);}", "foreach($rows as $index=>$row){self::eventFieldRow($row,(int)$index);}", 'indexed event field render loop')
    event_admin = replace_once(event_admin, "private static function eventFieldRow(array $row): void", "private static function eventFieldRow(array $row, int $index): void", 'indexed event field method')
    old_row = """        echo '<div class="h18-vd-field-row" data-event-field-row><input type="hidden" name="event_field_id[]" value="'.esc_attr((string)$row['id']).'"><label>Navn<input required type="text" name="event_field_label[]" value="'.esc_attr((string)$row['label']).'"></label><label>Type<select name="event_field_type[]">';
"""
    new_row = """        echo '<div class="h18-vd-field-row" data-event-field-row data-event-field-index="'.esc_attr((string)$index).'"><input type="hidden" name="event_field_id['.$index.']" value="'.esc_attr((string)$row['id']).'"><label>Navn<input required type="text" name="event_field_label['.$index.']" value="'.esc_attr((string)$row['label']).'"></label><label>Type<select name="event_field_type['.$index.']">';
"""
    event_admin = replace_once(event_admin, old_row, new_row, 'indexed event field row start')
    event_admin = replace_once(event_admin, "name=\"event_field_order[]\"", "name=\"event_field_order['.$index.']\"", 'indexed event field order')
    event_admin = replace_once(event_admin, "name=\"event_field_enabled[]\" value=\"'.esc_attr((string)$row['id']).'\"", "name=\"event_field_enabled['.$index.']\" value=\"1\"", 'indexed enabled checkbox')
    event_admin = replace_once(event_admin, "name=\"event_field_required[]\" value=\"'.esc_attr((string)$row['id']).'\"", "name=\"event_field_required['.$index.']\" value=\"1\"", 'indexed required checkbox')
    event_admin = replace_once(event_admin, "name=\"event_field_card[]\" value=\"'.esc_attr((string)$row['id']).'\"", "name=\"event_field_card['.$index.']\" value=\"1\"", 'indexed card checkbox')
    event_admin = replace_once(event_admin, "name=\"event_field_detail[]\" value=\"'.esc_attr((string)$row['id']).'\"", "name=\"event_field_detail['.$index.']\" value=\"1\"", 'indexed detail checkbox')
    old_sets = "$enabled=array_flip(array_map('sanitize_key',is_array($_POST['event_field_enabled']??null)?wp_unslash($_POST['event_field_enabled']):[]));$required=array_flip(array_map('sanitize_key',is_array($_POST['event_field_required']??null)?wp_unslash($_POST['event_field_required']):[]));$card=array_flip(array_map('sanitize_key',is_array($_POST['event_field_card']??null)?wp_unslash($_POST['event_field_card']):[]));$detail=array_flip(array_map('sanitize_key',is_array($_POST['event_field_detail']??null)?wp_unslash($_POST['event_field_detail']):[]));"
    new_sets = "$enabled=is_array($_POST['event_field_enabled']??null)?wp_unslash($_POST['event_field_enabled']):[];$required=is_array($_POST['event_field_required']??null)?wp_unslash($_POST['event_field_required']):[];$card=is_array($_POST['event_field_card']??null)?wp_unslash($_POST['event_field_card']):[];$detail=is_array($_POST['event_field_detail']??null)?wp_unslash($_POST['event_field_detail']):[];"
    event_admin = replace_once(event_admin, old_sets, new_sets, 'indexed event field checkbox arrays')
    old_flags = "'enabled'=>$id===''?true:isset($enabled[$id]),'required'=>$id!==''&&isset($required[$id]),'showCard'=>$id!==''&&isset($card[$id]),'showDetail'=>$id===''?true:isset($detail[$id])"
    new_flags = "'enabled'=>isset($enabled[$i]),'required'=>isset($required[$i]),'showCard'=>isset($card[$i]),'showDetail'=>isset($detail[$i])"
    event_admin = replace_once(event_admin, old_flags, new_flags, 'indexed event field flags')
write(event_admin_path, event_admin)

admin_js_path = Path('clean/hangar18-manager/assets/admin-v0178-events.js')
admin_js = read(admin_js_path)
if 'data-event-field-index' not in admin_js:
    admin_js = """(function(){'use strict';
function rowHtml(index,order){return '<div class="h18-vd-field-row" data-event-field-row data-event-field-index="'+index+'"><input type="hidden" name="event_field_id['+index+']" value=""><label>Navn<input required type="text" name="event_field_label['+index+']"></label><label>Type<select name="event_field_type['+index+']"><option value="richtext">Rich text</option><option value="text">Tekst</option><option value="textarea">Flere linjer</option><option value="number">Tal</option><option value="integer">Heltal</option><option value="boolean">Ja/nej</option><option value="date">Dato</option><option value="datetime">Dato/tid</option><option value="url">Link</option></select></label><label>Rækkefølge<input type="number" name="event_field_order['+index+']" value="'+order+'"></label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_enabled['+index+']" value="1" checked> Aktiv</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_required['+index+']" value="1"> Påkrævet</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_card['+index+']" value="1"> På kort</label><label class="h18-clean-checkbox"><input type="checkbox" name="event_field_detail['+index+']" value="1" checked> På detalje</label><button type="button" class="button-link-delete h18-vd-remove-event-field">Fjern</button></div>';}
function nextIndex(host){let max=-1;host.querySelectorAll('[data-event-field-index]').forEach(function(row){max=Math.max(max,parseInt(row.getAttribute('data-event-field-index')||'-1',10)||0);});return max+1;}
document.addEventListener('click',function(e){const add=e.target&&e.target.closest?e.target.closest('#h18-vd-add-event-field'):null;if(add){e.preventDefault();const host=document.getElementById('h18-vd-event-field-rows');if(!host)return;const index=nextIndex(host);host.insertAdjacentHTML('beforeend',rowHtml(index,(host.children.length+1)*10));const row=host.querySelector('[data-event-field-index="'+index+'"]');const input=row?row.querySelector('input[name^="event_field_label["]'):null;if(input)input.focus();return;}const remove=e.target&&e.target.closest?e.target.closest('.h18-vd-remove-event-field'):null;if(remove){e.preventDefault();const row=remove.closest('[data-event-field-row]');if(row)row.remove();}});
}());
"""
write(admin_js_path, admin_js)


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
editor_controller_path = Path('clean/hangar18-manager/src/Admin/EditorController.php')
editor_controller = read(editor_controller_path)
if "'eventfacts' => 'Eventfaktabånd'" not in editor_controller:
    editor_controller = replace_once(
        editor_controller,
        "'eventlist' => 'Eventliste', 'eventvalue' => 'Eventværdi', 'eventimage' => 'Eventbillede',\n                'gallerylist'",
        "'eventlist' => 'Eventliste', 'eventvalue' => 'Eventværdi', 'eventimage' => 'Eventbillede', 'eventfacts' => 'Eventfaktabånd',\n                'gallerylist'",
        'Editor palette event facts',
    )
write(editor_controller_path, editor_controller)


# ---------------------------------------------------------------------------
# Editor runtime
# ---------------------------------------------------------------------------
editor_path = Path('clean/hangar18-manager/assets/editor-v018-core.js')
editor = read(editor_path)
if "'eventfacts'" not in editor.split('const PARENT_TYPES', 1)[0]:
    editor = replace_once(editor, "'eventvalue', 'eventimage', 'gallerylist'", "'eventvalue', 'eventimage', 'eventfacts', 'gallerylist'", 'editor TYPES eventfacts')

editor = editor.replace("eventimage:'Eventbillede',gallerylist", "eventimage:'Eventbillede',eventfacts:'Eventfaktabånd',gallerylist")
editor = editor.replace("eventimage:'EVENTBILLEDE',eventfield:'EVENTFELT'", "eventimage:'EVENTBILLEDE',eventfacts:'EVENTFAKTABÅND',eventfield:'EVENTFELT'")

if "if (type === 'eventfacts')" not in editor:
    anchor = """        if (type === 'eventfield') {
"""
    block = """        if (type === 'eventfacts') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{recordId:recordId,showDate:raw.showDate!==false,showTime:raw.showTime!==false,showLocation:raw.showLocation!==false,showAddress:raw.showAddress!==false,showContact:raw.showContact!==false,gap:clamp(parseInt(raw.gap||12,10)||12,0,80),minCardWidth:clamp(parseInt(raw.minCardWidth||150,10)||150,100,360),cardBackground:normalizeColor(raw.cardBackground||'#f4f1e8'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),labelColor:normalizeColor(raw.labelColor||'#30382a'),valueColor:normalizeColor(raw.valueColor||'#30382a'),paddingX:clamp(parseInt(raw.paddingX||16,10)||16,0,80),paddingY:clamp(parseInt(raw.paddingY||16,10)||16,0,80),radius:clamp(parseInt(raw.radius||0,10)||0,0,60),labelFontFamily:normalizeFontToken(raw.labelFontFamily||'system',false),labelFontSize:clamp(parseInt(raw.labelFontSize||16,10)||16,8,80),labelFontWeight:clamp(parseInt(raw.labelFontWeight||700,10)||700,100,900),valueFontFamily:normalizeFontToken(raw.valueFontFamily||'system',false),valueFontSize:clamp(parseInt(raw.valueFontSize||16,10)||16,8,80),valueFontWeight:clamp(parseInt(raw.valueFontWeight||400,10)||400,100,900),lineHeight:Math.max(0.8,Math.min(3,parseFloat(raw.lineHeight||1.35)||1.35))});
        }

"""
    editor = replace_once(editor, anchor, block + anchor, 'editor eventfacts normalize')

old_eventfield_norm = "return Object.assign(common,{fieldKey:key||'about',recordId:recordId,showHeading:raw.showHeading!==false,background:/^#[0-9a-f]{6}$/i.test(String(raw.background||''))?String(raw.background).toLowerCase():'',textColor:normalizeColor(raw.textColor||'#30382a'),padding:clamp(parseInt(raw.padding||0,10)||0,0,80),radius:clamp(parseInt(raw.radius||0,10)||0,0,60)});"
new_eventfield_norm = "return Object.assign(common,{fieldKey:key||'about',recordId:recordId,showHeading:raw.showHeading!==false,showWhenEmpty:raw.showWhenEmpty===true,background:/^#[0-9a-f]{6}$/i.test(String(raw.background||''))?String(raw.background).toLowerCase():'',textColor:normalizeColor(raw.textColor||'#30382a'),fontFamily:normalizeFontToken(raw.fontFamily||'system',false),fontSize:clamp(parseInt(raw.fontSize||16,10)||16,8,120),fontWeight:clamp(parseInt(raw.fontWeight||400,10)||400,100,900),lineHeight:Math.max(0.8,Math.min(3,parseFloat(raw.lineHeight||1.5)||1.5)),headingColor:normalizeColor(raw.headingColor||'#30382a'),headingFontFamily:normalizeFontToken(raw.headingFontFamily||'body',true),headingFontSize:clamp(parseInt(raw.headingFontSize||40,10)||40,8,160),headingFontWeight:clamp(parseInt(raw.headingFontWeight||400,10)||400,100,900),headingLineHeight:Math.max(0.8,Math.min(3,parseFloat(raw.headingLineHeight||1.15)||1.15)),headingGap:clamp(parseInt(raw.headingGap||12,10)||12,0,80),padding:clamp(parseInt(raw.padding||0,10)||0,0,80),radius:clamp(parseInt(raw.radius||0,10)||0,0,60)});"
if 'showWhenEmpty:raw.showWhenEmpty===true' not in editor:
    editor = replace_once(editor, old_eventfield_norm, new_eventfield_norm, 'editor eventfield normalize typography')

if 'eventfacts: 12' not in editor:
    editor = replace_once(editor, 'eventvalue: 10, eventimage: 40, eventfield: 18', 'eventvalue: 10, eventimage: 40, eventfacts: 12, eventfield: 18', 'editor eventfacts default rows')

if "node.type === 'eventfacts'" not in editor:
    preview_anchor = """        } else if (node.type === 'eventfield') {
            wrap.classList.add('h18-clean-node-preview--eventfield');
"""
    preview = """        } else if (node.type === 'eventfacts') {
            wrap.classList.add('h18-clean-node-preview--eventfacts'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const start=String(fields.start||''); const end=String(fields.end||''); const dateOnly=function(value){const m=String(value||'').match(/^(\\d{4})-(\\d{2})-(\\d{2})T/);return m?m[3]+'-'+m[2]+'-'+m[1]:'';}; const timeOnly=function(value){const m=String(value||'').match(/^\\d{4}-\\d{2}-\\d{2}T(\\d{2}:\\d{2})/);return m?m[1]:'';}; const sd=dateOnly(start),ed=dateOnly(end),st=timeOnly(start),et=timeOnly(end); const facts=[]; if(node.props.showDate!==false)facts.push(['Dato',sd&&ed&&ed!==sd?sd+' – '+ed:(sd||ed)]);if(node.props.showTime!==false)facts.push(['Tid',st?(et?st+' – '+et:st):et]);if(node.props.showLocation!==false)facts.push(['Sted',String(fields.location||'')]);if(node.props.showAddress!==false)facts.push(['Adresse',String(fields.address||'')]);if(node.props.showContact!==false)facts.push(['Kontakt',String(fields.contact||'')]); const grid=document.createElement('div');grid.style.display='grid';grid.style.gridTemplateColumns='repeat(auto-fit,minmax('+String(node.props.minCardWidth||150)+'px,1fr))';grid.style.gap=String(node.props.gap||12)+'px';facts.forEach(function(fact){const card=document.createElement('div');card.style.minWidth='0';card.style.background=node.props.cardBackground||'#f4f1e8';card.style.borderLeft='4px solid '+String(node.props.accentColor||'#c3ae83');card.style.padding=String(node.props.paddingY||16)+'px '+String(node.props.paddingX||16)+'px';card.style.borderRadius=String(node.props.radius||0)+'px';const label=document.createElement('strong');label.textContent=fact[0];label.style.display='block';label.style.marginBottom='4px';label.style.color=node.props.labelColor||'#30382a';label.style.fontFamily=fontCss(node.props.labelFontFamily||'system');label.style.fontSize=String(node.props.labelFontSize||16)+'px';label.style.fontWeight=String(node.props.labelFontWeight||700);label.style.lineHeight=String(node.props.lineHeight||1.35);const value=document.createElement('span');value.textContent=fact[1]||'';value.style.display='block';value.style.color=node.props.valueColor||'#30382a';value.style.fontFamily=fontCss(node.props.valueFontFamily||'system');value.style.fontSize=String(node.props.valueFontSize||16)+'px';value.style.fontWeight=String(node.props.valueFontWeight||400);value.style.lineHeight=String(node.props.lineHeight||1.35);card.appendChild(label);card.appendChild(value);grid.appendChild(card);});if(!record){const hint=document.createElement('div');hint.textContent='Eventfaktabånd · vælg preview-event';grid.appendChild(hint);}wrap.appendChild(grid);

"""
    editor = replace_once(editor, preview_anchor, preview + preview_anchor, 'editor eventfacts preview')

# Enrich eventfield preview styling without changing the underlying record contract.
if "box.style.fontFamily=fontCss(node.props.fontFamily||'system')" not in editor:
    editor = replace_once(
        editor,
        "box.style.color=node.props.textColor||'#30382a';if(node.props.background){box.style.background=node.props.background;}",
        "box.style.color=node.props.textColor||'#30382a';box.style.fontFamily=fontCss(node.props.fontFamily||'system');box.style.fontSize=String(node.props.fontSize||16)+'px';box.style.fontWeight=String(node.props.fontWeight||400);box.style.lineHeight=String(node.props.lineHeight||1.5);if(node.props.background){box.style.background=node.props.background;}",
        'editor eventfield body preview typography',
    )
    editor = replace_once(
        editor,
        "const h=document.createElement('h3');h.textContent=String(def&&def.label||attr.label||node.props.fieldKey);box.appendChild(h);",
        "const h=document.createElement('h3');h.textContent=String(def&&def.label||attr.label||node.props.fieldKey);h.style.margin='0 0 '+String(node.props.headingGap||12)+'px';h.style.color=node.props.headingColor||'#30382a';h.style.fontFamily=fontCss(node.props.headingFontFamily||'body');h.style.fontSize=String(node.props.headingFontSize||40)+'px';h.style.fontWeight=String(node.props.headingFontWeight||400);h.style.lineHeight=String(node.props.headingLineHeight||1.15);box.appendChild(h);",
        'editor eventfield heading preview typography',
    )
    old_empty = "if(!record||!attr||String(attr.value==null?'':attr.value)===''){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{if(node.props.showHeading!==false){"
    new_empty = "if(!record){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{const empty=!attr||String(attr.value==null?'':attr.value)==='';if(empty&&node.props.showWhenEmpty!==true){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{if(node.props.showHeading!==false){"
    editor = replace_once(editor, old_empty, new_empty, 'editor eventfield empty preview open')
    old_close = "if(String(def&&def.type||attr.type)==='richtext'){value.innerHTML=richPreviewHtml(String(attr.value||''));}else{value.textContent=typeof attr.value==='boolean'?(attr.value?'Ja':'Nej'):String(attr.value);}box.appendChild(value);}wrap.appendChild(box);"
    new_close = "if(!empty){if(String(def&&def.type||(attr&&attr.type)||'text')==='richtext'){value.innerHTML=richPreviewHtml(String(attr&&attr.value||''));}else{value.textContent=typeof (attr&&attr.value)==='boolean'?(attr.value?'Ja':'Nej'):String(attr&&attr.value||'');}box.appendChild(value);}}}wrap.appendChild(box);"
    editor = replace_once(editor, old_close, new_close, 'editor eventfield empty preview close')

# Inspector: Eventfaktabånd before Eventfelt.
if '<h3>Eventfaktabånd</h3>' not in editor:
    inspector_anchor = """        } else if (node.type === 'eventfield') {
            const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[];
"""
    inspector = """        } else if (node.type === 'eventfacts') {
            html += '<div class="h18-vd-menu-group"><h3>Eventfaktabånd</h3><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><div class="h18-clean-field-grid"><label class="h18-clean-checkbox"><input data-field="eventFactsShowDate" type="checkbox"'+(node.props.showDate!==false?' checked':'')+'> Dato</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowTime" type="checkbox"'+(node.props.showTime!==false?' checked':'')+'> Tid</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowLocation" type="checkbox"'+(node.props.showLocation!==false?' checked':'')+'> Sted</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowAddress" type="checkbox"'+(node.props.showAddress!==false?' checked':'')+'> Adresse</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowContact" type="checkbox"'+(node.props.showContact!==false?' checked':'')+'> Kontakt</label></div><h4>Layout</h4><div class="h18-clean-field-grid"><label>Afstand<input data-field="eventFactsGap" type="number" min="0" max="80" value="'+String(node.props.gap||12)+'"></label><label>Min. kortbredde<input data-field="eventFactsMinCardWidth" type="number" min="100" max="360" value="'+String(node.props.minCardWidth||150)+'"></label><label>Padding X<input data-field="eventFactsPaddingX" type="number" min="0" max="80" value="'+String(node.props.paddingX||16)+'"></label><label>Padding Y<input data-field="eventFactsPaddingY" type="number" min="0" max="80" value="'+String(node.props.paddingY||16)+'"></label><label>Hjørner<input data-field="eventFactsRadius" type="number" min="0" max="60" value="'+String(node.props.radius||0)+'"></label></div><h4>Farver</h4><div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="eventFactsCardBackground" type="color" value="'+escapeAttr(node.props.cardBackground||'#f4f1e8')+'"></label><label>Accent<input data-field="eventFactsAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label><label>Label<input data-field="eventFactsLabelColor" type="color" value="'+escapeAttr(node.props.labelColor||'#30382a')+'"></label><label>Værdi<input data-field="eventFactsValueColor" type="color" value="'+escapeAttr(node.props.valueColor||'#30382a')+'"></label></div><h4>Typografi</h4><div class="h18-clean-field-grid"><label>Label skrifttype<select data-field="eventFactsLabelFontFamily">'+fontOptions(node.props.labelFontFamily||'system',false)+'</select></label><label>Label størrelse<input data-field="eventFactsLabelFontSize" type="number" min="8" max="80" value="'+String(node.props.labelFontSize||16)+'"></label><label>Label tykkelse<input data-field="eventFactsLabelFontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.labelFontWeight||700)+'"></label><label>Værdi skrifttype<select data-field="eventFactsValueFontFamily">'+fontOptions(node.props.valueFontFamily||'system',false)+'</select></label><label>Værdi størrelse<input data-field="eventFactsValueFontSize" type="number" min="8" max="80" value="'+String(node.props.valueFontSize||16)+'"></label><label>Værdi tykkelse<input data-field="eventFactsValueFontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.valueFontWeight||400)+'"></label><label>Linjeafstand<input data-field="eventFactsLineHeight" type="number" min="0.8" max="3" step="0.05" value="'+String(node.props.lineHeight||1.35)+'"></label></div><p class="description">Dato og tid kommer fra Start/Slut. Sted, Adresse og Kontakt redigeres på eventet.</p></div>';

"""
    editor = replace_once(editor, inspector_anchor, inspector + inspector_anchor, 'editor eventfacts inspector')

old_field_inspector = "const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; html += '<div class=\"h18-vd-menu-group\"><h3>Eventfelt</h3><label>Felt<select data-field=\"eventFieldKey\">'+defs.map(function(row){return '<option value=\"'+escapeAttr(String(row.id||''))+'\"'+(String(node.props.fieldKey||'')===String(row.id||'')?' selected':'')+'>'+escapeHtml(String(row.label||row.id||'Felt'))+'</option>';}).join('')+'</select></label><label>Preview-event<select data-field=\"eventRecordId\"><option value=\"\">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value=\"'+escapeAttr(String(record.id||''))+'\"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label class=\"h18-clean-checkbox\"><input data-field=\"eventFieldShowHeading\" type=\"checkbox\"'+(node.props.showHeading!==false?' checked':'')+'> Vis feltoverskrift</label><div class=\"h18-clean-field-grid\"><label>Padding<input data-field=\"padding\" type=\"number\" min=\"0\" max=\"80\" value=\"'+String(node.props.padding||0)+'\"></label><label>Hjørner<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"60\" value=\"'+String(node.props.radius||0)+'\"></label><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"'+escapeAttr(node.props.background||'#ffffff')+'\"></label><label>Tekst<input data-field=\"textColor\" type=\"color\" value=\"'+escapeAttr(node.props.textColor||'#30382a')+'\"></label></div></div>';"
new_field_inspector = "const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; html += '<div class=\"h18-vd-menu-group\"><h3>Eventfelt</h3><label>Felt<select data-field=\"eventFieldKey\">'+defs.map(function(row){return '<option value=\"'+escapeAttr(String(row.id||''))+'\"'+(String(node.props.fieldKey||'')===String(row.id||'')?' selected':'')+'>'+escapeHtml(String(row.label||row.id||'Felt'))+'</option>';}).join('')+'</select></label><label>Preview-event<select data-field=\"eventRecordId\"><option value=\"\">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value=\"'+escapeAttr(String(record.id||''))+'\"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label class=\"h18-clean-checkbox\"><input data-field=\"eventFieldShowHeading\" type=\"checkbox\"'+(node.props.showHeading!==false?' checked':'')+'> Vis feltoverskrift</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventFieldShowWhenEmpty\" type=\"checkbox\"'+(node.props.showWhenEmpty===true?' checked':'')+'> Vis overskrift selv når feltet er tomt</label><h4>Overskrift</h4><div class=\"h18-clean-field-grid\"><label>Skrifttype<select data-field=\"headingFontFamily\">'+fontOptions(node.props.headingFontFamily||'body',true)+'</select></label><label>Størrelse px<input data-field=\"headingFontSize\" type=\"number\" min=\"8\" max=\"160\" value=\"'+String(node.props.headingFontSize||40)+'\"></label><label>Tykkelse<input data-field=\"headingFontWeight\" type=\"number\" min=\"100\" max=\"900\" step=\"100\" value=\"'+String(node.props.headingFontWeight||400)+'\"></label><label>Linjeafstand<input data-field=\"headingLineHeight\" type=\"number\" min=\"0.8\" max=\"3\" step=\"0.05\" value=\"'+String(node.props.headingLineHeight||1.15)+'\"></label><label>Afstand efter<input data-field=\"eventFieldHeadingGap\" type=\"number\" min=\"0\" max=\"80\" value=\"'+String(node.props.headingGap||12)+'\"></label><label>Farve<input data-field=\"headingColor\" type=\"color\" value=\"'+escapeAttr(node.props.headingColor||'#30382a')+'\"></label></div><h4>Indhold</h4><div class=\"h18-clean-field-grid\"><label>Skrifttype<select data-field=\"fontFamily\">'+fontOptions(node.props.fontFamily||'system',false)+'</select></label><label>Størrelse px<input data-field=\"fontSize\" type=\"number\" min=\"8\" max=\"120\" value=\"'+String(node.props.fontSize||16)+'\"></label><label>Tykkelse<input data-field=\"fontWeight\" type=\"number\" min=\"100\" max=\"900\" step=\"100\" value=\"'+String(node.props.fontWeight||400)+'\"></label><label>Linjeafstand<input data-field=\"lineHeight\" type=\"number\" min=\"0.8\" max=\"3\" step=\"0.05\" value=\"'+String(node.props.lineHeight||1.5)+'\"></label><label>Tekstfarve<input data-field=\"textColor\" type=\"color\" value=\"'+escapeAttr(node.props.textColor||'#30382a')+'\"></label><label>Padding<input data-field=\"padding\" type=\"number\" min=\"0\" max=\"80\" value=\"'+String(node.props.padding||0)+'\"></label><label>Hjørner<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"60\" value=\"'+String(node.props.radius||0)+'\"></label><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"'+escapeAttr(node.props.background||'#ffffff')+'\"></label></div></div>';"
if 'eventFieldShowWhenEmpty' not in editor:
    editor = replace_once(editor, old_field_inspector, new_field_inspector, 'editor eventfield typography inspector')

if "field === 'eventFactsShowDate'" not in editor:
    handler_anchor = """                else if (field === 'eventFieldKey') { current.props.fieldKey=String(control.value||'about'); }
"""
    handlers = """                else if (field === 'eventFactsShowDate') { current.props.showDate=!!control.checked; }
                else if (field === 'eventFactsShowTime') { current.props.showTime=!!control.checked; }
                else if (field === 'eventFactsShowLocation') { current.props.showLocation=!!control.checked; }
                else if (field === 'eventFactsShowAddress') { current.props.showAddress=!!control.checked; }
                else if (field === 'eventFactsShowContact') { current.props.showContact=!!control.checked; }
                else if (field === 'eventFactsGap') { current.props.gap=clamp(parseInt(control.value||12,10)||12,0,80); }
                else if (field === 'eventFactsMinCardWidth') { current.props.minCardWidth=clamp(parseInt(control.value||150,10)||150,100,360); }
                else if (field === 'eventFactsPaddingX') { current.props.paddingX=clamp(parseInt(control.value||16,10)||16,0,80); }
                else if (field === 'eventFactsPaddingY') { current.props.paddingY=clamp(parseInt(control.value||16,10)||16,0,80); }
                else if (field === 'eventFactsRadius') { current.props.radius=clamp(parseInt(control.value||0,10)||0,0,60); }
                else if (field === 'eventFactsCardBackground') { current.props.cardBackground=normalizeColor(control.value||'#f4f1e8'); }
                else if (field === 'eventFactsAccentColor') { current.props.accentColor=normalizeColor(control.value||'#c3ae83'); }
                else if (field === 'eventFactsLabelColor') { current.props.labelColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'eventFactsValueColor') { current.props.valueColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'eventFactsLabelFontFamily') { current.props.labelFontFamily=normalizeFontToken(control.value,false); }
                else if (field === 'eventFactsLabelFontSize') { current.props.labelFontSize=clamp(parseInt(control.value||16,10)||16,8,80); }
                else if (field === 'eventFactsLabelFontWeight') { current.props.labelFontWeight=clamp(parseInt(control.value||700,10)||700,100,900); }
                else if (field === 'eventFactsValueFontFamily') { current.props.valueFontFamily=normalizeFontToken(control.value,false); }
                else if (field === 'eventFactsValueFontSize') { current.props.valueFontSize=clamp(parseInt(control.value||16,10)||16,8,80); }
                else if (field === 'eventFactsValueFontWeight') { current.props.valueFontWeight=clamp(parseInt(control.value||400,10)||400,100,900); }
                else if (field === 'eventFactsLineHeight') { current.props.lineHeight=Math.max(0.8,Math.min(3,parseFloat(control.value||1.35)||1.35)); }
"""
    editor = replace_once(editor, handler_anchor, handlers + handler_anchor, 'editor eventfacts handlers')
    editor = replace_once(editor, "else if (field === 'eventFieldShowHeading') { current.props.showHeading=!!control.checked; }", "else if (field === 'eventFieldShowHeading') { current.props.showHeading=!!control.checked; }\n                else if (field === 'eventFieldShowWhenEmpty') { current.props.showWhenEmpty=!!control.checked; }\n                else if (field === 'eventFieldHeadingGap') { current.props.headingGap=clamp(parseInt(control.value||12,10)||12,0,80); }", 'editor eventfield extra handlers')
write(editor_path, editor)


# ---------------------------------------------------------------------------
# New safe migration for existing v0.1.80 event detail template
# ---------------------------------------------------------------------------
migration_path = Path('clean/hangar18-manager/src/Migration/EventDetailFactsMigration.php')
migration_path.write_text(r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class EventDetailFactsMigration
{
    private const META = '_h18_vd_event_detail_facts_v0185';
    private const BACKUP_META = '_h18_vd_event_detail_facts_backup_v0185';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'ensure'], 28);
    }

    public static function ensure(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        $page = get_page_by_path('event-detalje', OBJECT, 'page');
        if (!$page instanceof \WP_Post) { return; }
        $postId = (int) $page->ID;
        if (get_post_meta($postId, self::META, true)) { return; }

        $before = LayoutModel::get($postId);
        $nodes = isset($before['nodes']) && is_array($before['nodes']) ? array_values($before['nodes']) : [];
        $ids = [];
        foreach ($nodes as $node) {
            if (is_array($node)) { $ids[(string) ($node['id'] ?? '')] = true; }
        }
        // Only replace the known v0.1.80 composable pair. Custom detail pages are left untouched.
        if (empty($ids['event-date']) || empty($ids['event-location']) || empty($ids['event-title']) || empty($ids['detail-section'])) {
            update_post_meta($postId, self::META, ['status' => 'skipped-custom-layout', 'checkedUtc' => gmdate('c')]);
            return;
        }

        update_post_meta($postId, self::BACKUP_META, $before);
        $next = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            if ($id === 'event-date' || $id === 'event-location') { continue; }
            if (in_array($id, ['eventfield-about', 'eventfield-program', 'eventfield-practical'], true)) {
                if (!isset($node['props']) || !is_array($node['props'])) { $node['props'] = []; }
                $node['props']['showHeading'] = true;
                $node['props']['showWhenEmpty'] = true;
                if (!array_key_exists('headingFontSize', $node['props'])) { $node['props']['headingFontSize'] = 40; }
                if (!array_key_exists('headingFontWeight', $node['props'])) { $node['props']['headingFontWeight'] = 400; }
                if (!array_key_exists('headingLineHeight', $node['props'])) { $node['props']['headingLineHeight'] = 1.15; }
                if (!array_key_exists('headingGap', $node['props'])) { $node['props']['headingGap'] = 12; }
                if (!array_key_exists('fontSize', $node['props'])) { $node['props']['fontSize'] = 16; }
                if (!array_key_exists('fontWeight', $node['props'])) { $node['props']['fontWeight'] = 400; }
                if (!array_key_exists('lineHeight', $node['props'])) { $node['props']['lineHeight'] = 1.5; }
            }
            $next[] = $node;
        }
        $next[] = [
            'id' => 'event-facts',
            'type' => 'eventfacts',
            'parentId' => 'detail-section',
            'order' => 30,
            'geometry' => self::geometry(3, 22, 114, 12),
            'props' => [
                'recordId' => '',
                'showDate' => true,
                'showTime' => true,
                'showLocation' => true,
                'showAddress' => true,
                'showContact' => true,
                'gap' => 12,
                'minCardWidth' => 150,
                'cardBackground' => '#f4f1e8',
                'accentColor' => '#c3ae83',
                'labelColor' => '#30382a',
                'valueColor' => '#30382a',
                'paddingX' => 16,
                'paddingY' => 16,
                'radius' => 0,
                'labelFontFamily' => 'system',
                'labelFontSize' => 16,
                'labelFontWeight' => 700,
                'valueFontFamily' => 'system',
                'valueFontSize' => 16,
                'valueFontWeight' => 400,
                'lineHeight' => 1.35,
            ],
        ];
        $model = $before;
        $model['nodes'] = $next;
        $version = LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'v0.1.85: Eventfaktabånd + justerbar Eventfelt-typografi');
        update_post_meta($postId, self::META, ['status' => 'migrated', 'version' => $version, 'migratedUtc' => gmdate('c')]);
    }

    /** @return array<string,mixed> */
    private static function geometry(int $x, int $y, int $w, int $h): array
    {
        return [
            'desktop' => ['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],
            'laptop' => ['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
            'tablet' => ['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
            'mobile' => ['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false],
        ];
    }

    private function __construct() {}
}
''', encoding='utf-8')


# ---------------------------------------------------------------------------
# Release metadata
# ---------------------------------------------------------------------------
history_path = Path('clean/hangar18-manager/release-history.json')
history = json.loads(read(history_path))
versions = history.setdefault('versions', [])
if not any(isinstance(row, dict) and str(row.get('version')) == VERSION for row in versions):
    versions.insert(0, {
        'version': VERSION,
        'date': '2026-09-02',
        'items': [
            'EVENT-FACTS-001: nyt Eventfaktabånd i Visual Designer med Dato, Tid, Sted, Adresse og Kontakt i responsive accentkort.',
            'Events har nu kanoniske Adresse- og Kontaktfelter, som gemmes sammen med Start/Slut og Sted.',
            'Eventfelt har justerbar overskrifts- og brødteksttypografi samt valgfri visning af overskrift ved tomt felt.',
            'Den kendte v0.1.80 Eventdetalje migreres sikkert til faktabåndet med layoutbackup og ny Designer-version.',
            'Eventfelter-admin bruger stabile rækkenøgler, så Aktiv/Påkrævet/På kort/På detalje virker korrekt allerede ved første gem af nye felter.'
        ]
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes_path = Path('clean-release-notes.html')
notes = read(notes_path) if notes_path.exists() else ''
section = ('<section data-version="0.1.85"><h2>0.1.85</h2><ul>'
           '<li>Nyt <strong>Eventfaktabånd</strong> med Dato, Tid, Sted, Adresse og Kontakt i samme kompakte kortstil som den tidligere eventside.</li>'
           '<li>Faktabåndet er et rigtigt Designer-element med justerbar afstand, kortbredde, padding, farver og typografi.</li>'
           '<li><strong>Eventfelt</strong> har nu separat størrelse, vægt, skrifttype og linjeafstand for overskrift og indhold.</li>'
           '<li>Om arrangementet, Program og Praktiske oplysninger kan vise overskriften selv uden indhold og kan styles individuelt.</li>'
           '<li>Adresse og Kontakt er tilføjet som kanoniske Event-datafelter.</li>'
           '<li>Nye Eventfelters checkbox-indstillinger gemmes korrekt allerede ved første gem.</li>'
           '</ul></section>\n')
if 'data-version="0.1.85"' not in notes:
    notes = section + notes
write(notes_path, notes)

status_path = Path('docs/v0185-status.md')
status_path.write_text('''# Visual Designer Manager v0.1.85 – Eventfaktabånd og typografi

Status: release candidate

## Leverance

- Nyt Designer-element: Eventfaktabånd.
- Dato, Tid, Sted, Adresse og Kontakt i fem responsive accentkort.
- Separat typografi for labels og værdier i faktabåndet.
- Nye kanoniske Event-felter: Adresse og Kontakt.
- Eventfelt: separat overskrifts- og brødteksttypografi.
- Eventfelt: valgfri overskrift selv ved tomt felt.
- Sikker migration af den kendte v0.1.80 Eventdetalje med layoutbackup.
- Row-index-fix i Eventfelter-admin, så checkbox-flags virker ved første gem.
''', encoding='utf-8')
