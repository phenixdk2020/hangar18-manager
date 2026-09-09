from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.29'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha28.py'], check=True)

def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')

def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')

def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))

# ---------------------------------------------------------------------------
# Version cutover.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.28', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.28');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.28');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.29 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Event detail: preserve Program line breaks, including legacy escaped CR/LF
# and the old "rn" delimiter seen immediately before timetable entries.
# ---------------------------------------------------------------------------
renderer_rel = 'src/Frontend/Renderer.php'
renderer = read(renderer_rel)
old = "$rendered=$atype==='richtext'?self::renderStoredRichText((string)$value):($atype==='boolean'?($value?'Ja':'Nej'):self::renderPlainMultiline((string)$value));"
new = "$rendered=$atype==='richtext'?($key==='program'?self::renderEventProgramText((string)$value):self::renderStoredRichText((string)$value)):($atype==='boolean'?($value?'Ja':'Nej'):self::renderPlainMultiline((string)$value));"
if renderer.count(old) != 1:
    raise SystemExit(f'Alpha.29 eventdetail program anchor mismatch: {renderer.count(old)}')
renderer = renderer.replace(old, new, 1)

old = "$label=(string)($def['label']??($attribute['label']??$fieldKey));$type=(string)($def['type']??($attribute['type']??'text'));$content=$empty?'':($type==='richtext'?self::renderStoredRichText((string)$value):($type==='boolean'?($value?'Ja':'Nej'):self::renderPlainMultiline((string)$value)));"
new = "$label=(string)($def['label']??($attribute['label']??$fieldKey));$type=(string)($def['type']??($attribute['type']??'text'));$content=$empty?'':($type==='richtext'?($fieldKey==='program'?self::renderEventProgramText((string)$value):self::renderStoredRichText((string)$value)):($type==='boolean'?($value?'Ja':'Nej'):self::renderPlainMultiline((string)$value)));"
if renderer.count(old) != 1:
    raise SystemExit(f'Alpha.29 eventfield program anchor mismatch: {renderer.count(old)}')
renderer = renderer.replace(old, new, 1)

# Event gallery action belongs after the last canonical event field. The event
# already stores galleryRecordId through Manager -> Events; Alpha.29 exposes it
# on the V3 detail page without adding a second gallery relationship.
old = "$headingStyle='margin:0 0 '.$headingGap.'px;color:'.$headingColor.';font-family:'.self::fontCss((string)($props['headingFontFamily']??'body')).';font-size:'.$headingSize.'px;font-weight:'.$headingWeight.';line-height:'.$headingLineHeight.';';$heading=!empty($props['showHeading'])?'<h3 class=\"h18-clean-front-event-field-heading\" style=\"'.esc_attr($headingStyle).'\">'.esc_html($label).'</h3>':'';$valueHtml=$content!==''?'<div class=\"h18-clean-front-event-field-value\">'.$content.'</div>':'';\n            return '<section id=\"h18-clean-'.$id.'\" class=\"h18-clean-front-node h18-clean-front-event-field\" style=\"'.esc_attr($style.$borderStyle.$spacingStyle.$extra).'\">'.$heading.$valueHtml.'</section>';"
new = "$headingStyle='margin:0 0 '.$headingGap.'px;color:'.$headingColor.';font-family:'.self::fontCss((string)($props['headingFontFamily']??'body')).';font-size:'.$headingSize.'px;font-weight:'.$headingWeight.';line-height:'.$headingLineHeight.';';$heading=!empty($props['showHeading'])?'<h3 class=\"h18-clean-front-event-field-heading\" style=\"'.esc_attr($headingStyle).'\">'.esc_html($label).'</h3>':'';$valueHtml=$content!==''?'<div class=\"h18-clean-front-event-field-value\">'.$content.'</div>':'';\n            $galleryAction=$fieldKey==='practical'?self::eventGalleryButton($record):'';\n            return '<section id=\"h18-clean-'.$id.'\" class=\"h18-clean-front-node h18-clean-front-event-field\" style=\"'.esc_attr($style.$borderStyle.$spacingStyle.$extra).'\">'.$heading.$valueHtml.$galleryAction.'</section>';"
if renderer.count(old) != 1:
    raise SystemExit(f'Alpha.29 event gallery field anchor mismatch: {renderer.count(old)}')
renderer = renderer.replace(old, new, 1)

# The practical field may be empty while an album is linked. Keep that node so
# the gallery action remains visible instead of returning early.
old = "$value=$attribute['value']??'';if(is_bool($value)){$empty=!$value;}else{$empty=trim((string)$value)==='';}if($empty&&empty($props['showWhenEmpty'])){return '';}"
new = "$value=$attribute['value']??'';if(is_bool($value)){$empty=!$value;}else{$empty=trim((string)$value)==='';}$hasGallery=$fieldKey==='practical'&&self::eventHasPublishedGallery($record);if($empty&&empty($props['showWhenEmpty'])&&!$hasGallery){return '';}"
if renderer.count(old) != 1:
    raise SystemExit(f'Alpha.29 empty practical anchor mismatch: {renderer.count(old)}')
renderer = renderer.replace(old, new, 1)

helper_anchor = """    private static function renderStoredRichText(string $raw): string\n    {\n        return strpos($raw, '<') === false ? nl2br(esc_html($raw), false) : wp_kses_post($raw);\n    }\n"""
helpers = r'''    private static function normalizeStoredLineBreaks(string $raw): string
    {
        $raw = str_replace(["\r\n", "\r"], "\n", $raw);
        return str_replace(['\\r\\n', '\\n', '\\r'], "\n", $raw);
    }

    private static function renderEventProgramText(string $raw): string
    {
        $raw = self::normalizeStoredLineBreaks($raw);
        // Historical event imports could leave the letters "rn" where CR/LF
        // belonged. Repair only the timetable delimiter before a clock value;
        // never replace normal "rn" text globally.
        $raw = preg_replace('/rn(?=\\s*\\d{1,2}(?:[.:]\\d{2})\\b)/i', "\n", $raw) ?? $raw;
        if (strpos($raw, '<') === false) {
            return nl2br(esc_html($raw), false);
        }
        return wp_kses_post(wpautop($raw, true));
    }

    /** @param array<string,mixed> $record */
    private static function eventGalleryRecord(array $record): ?array
    {
        $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
        $galleryId = strtolower(trim((string) ($fields['galleryRecordId'] ?? '')));
        if ($galleryId === '' || preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $galleryId) !== 1) { return null; }
        $found = ModuleStore::findByRecordId('galleries', $galleryId);
        $gallery = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
        if ($gallery === null || (string) ($gallery['status'] ?? '') !== 'publish') { return null; }
        return $gallery;
    }

    /** @param array<string,mixed> $record */
    private static function eventHasPublishedGallery(array $record): bool
    {
        return self::eventGalleryRecord($record) !== null;
    }

    /** @param array<string,mixed> $record */
    private static function eventGalleryButton(array $record): string
    {
        $gallery = self::eventGalleryRecord($record);
        if ($gallery === null) { return ''; }
        $galleryId = (string) ($gallery['id'] ?? '');
        if ($galleryId === '') { return ''; }
        $page = get_page_by_path('billedgalleri', OBJECT, 'page');
        if (!$page instanceof \WP_Post) { return ''; }
        $url = add_query_arg('h18_gallery', rawurlencode($galleryId), get_permalink((int) $page->ID));
        $eventTitle = trim((string) ($record['title'] ?? ''));
        $label = 'Se billeder fra arrangementet' . ($eventTitle !== '' ? ' – ' . $eventTitle : '');
        $style = '--h18-btn-bg:#30382a;--h18-btn-color:#ffffff;--h18-btn-hover-bg:#3b4634;--h18-btn-hover-color:#ffffff;--h18-btn-focus:#c3ae83;margin-top:24px;max-width:420px;border-radius:5px;overflow:hidden;';
        return '<div class="h18-clean-front-event-gallery-action h18-clean-front-button" style="' . esc_attr($style) . '"><a class="h18-clean-front-button-link" href="' . esc_url($url) . '" style="padding:12px 20px;min-height:44px;font-weight:700;">' . esc_html($label) . '</a></div>';
    }

    private static function renderStoredRichText(string $raw): string
    {
        $raw = self::normalizeStoredLineBreaks($raw);
        return strpos($raw, '<') === false ? nl2br(esc_html($raw), false) : wp_kses_post($raw);
    }
'''
if renderer.count(helper_anchor) != 1:
    raise SystemExit(f'Alpha.29 richtext helper anchor mismatch: {renderer.count(helper_anchor)}')
renderer = renderer.replace(helper_anchor, helpers, 1)
write(renderer_rel, renderer)

# ---------------------------------------------------------------------------
# Footer mobile grouping. Alpha.28 intentionally made Desktop placement the
# master, but a three-column desktop Footer cannot be stacked by global y-order
# (that interleaves Genveje, Foreningen, menu, description and CTAs). Stack the
# canonical Desktop columns as semantic groups while keeping menu contents live.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
old = """        return $css;\n    }\n\n    /** @return array<string,mixed>|null */\n    private static function legacyPageModel(int $postId): ?array\n"""
new = """        // Alpha.29: stack the canonical three Desktop Footer columns as\n        // complete groups on phones. Alpha.28's global Desktop y-sort is correct\n        // for page content, but would interleave nodes from parallel Footer columns.\n        $footerStack = [\n            'text-footer-brand-v0147' => [10, 0],\n            'text-footer-description-v0147' => [20, 12],\n            'text-footer-shortcuts-heading-v0147' => [30, 24],\n            'menu-footer-shortcuts-v3' => [40, 8],\n            'text-footer-association-heading-v0147' => [50, 24],\n            'button-footer-join-v0147' => [60, 12],\n            'button-footer-contact-v0147' => [70, 12],\n            'container-footer-divider-v0147' => [80, 24],\n            'text-footer-copyright-v0147' => [90, 16],\n        ];\n        foreach ($footerStack as $footerId => $stack) {\n            if (!isset($byId[$footerId])) { continue; }\n            $css .= $scope . '#h18-clean-' . self::cssId($footerId)\n                . '{order:' . $stack[0] . '!important;margin-top:' . $stack[1] . 'px!important;}';\n        }\n        return $css;\n    }\n\n    /** @return array<string,mixed>|null */\n    private static function legacyPageModel(int $postId): ?array\n"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.29 footer stack anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)
write(rr_rel, rr)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.28':
    raise SystemExit('Expected Alpha.28 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Event Program linjeskift: normaliserer CR/LF, escaped \\r\\n/\\n og den historiske rn-tidsseparator uden at ændre almindelig tekst.',
        'Eventgalleri: Managerens eksisterende Tilknyttet album vises nu som knappen “Se billeder fra arrangementet – [eventtitel]” efter Praktiske oplysninger, når albummet er publiceret.',
        'Footer mobilgruppering: Desktopens tre Footer-kolonner stackes som Brand/Beskrivelse → Genveje/menu → Foreningen/CTA → copyright i stedet for at blive flettet efter global y-position.',
        'Footer Genveje følger fortsat den valgte Website-menu dynamisk og i menuens rækkefølge.',
        'Alpha.28 Desktop-master layout, Alpha.27 fælles paint source og Alpha.22 Header-menu bevares.'
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
renderer = read(renderer_rel)
rr = read(rr_rel)
history_text = read('release-history.json')
for token in ['Version: 3.0.0-alpha.29', "define('VDM_VERSION', '3.0.0-alpha.29');"]:
    if token not in main: raise SystemExit(f'Alpha.29 main token missing: {token}')
for token in [
    'private static function renderEventProgramText(',
    "preg_replace('/rn(?=\\\\s*\\\\d{1,2}(?:[.:]\\\\d{2})\\\\b)/i'",
    'private static function eventGalleryButton(',
    "'Se billeder fra arrangementet'",
    "$fieldKey==='practical'?self::eventGalleryButton($record):''",
    "if ($id === 'menu-footer-shortcuts-v3')",
    "$props['menuSource'] = 'website';",
    'h18-clean-front-menu-summary',
    'is-open',
]:
    if token not in renderer: raise SystemExit(f'Alpha.29 renderer token missing: {token}')
for token in [
    "$footerStack = [",
    "'menu-footer-shortcuts-v3' => [40, 8]",
    "'button-footer-join-v0147' => [60, 12]",
    "'text-footer-copyright-v0147' => [90, 16]",
    'Alpha.29: stack the canonical three Desktop Footer columns',
    'Mobile is a responsive projection of the Desktop Designer layout.',
]:
    if token not in rr: raise SystemExit(f'Alpha.29 responsive token missing: {token}')
if 'self::v1PaintCss($pageModel, $legacyPageModel, $pageScope)' in rr:
    raise SystemExit('Alpha.27 mobile-only paint regression')
if '3.0.0-alpha.29' not in history_text: raise SystemExit('Alpha.29 history token missing')
print('PASS')
