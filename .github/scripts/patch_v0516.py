from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 anchor, found {count}')
    return text.replace(old, new, 1)

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')
readme_path = Path('readme.txt')
php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

php = replace_once(php, ' * Version: 0.5.15', ' * Version: 0.5.16', 'plugin header')
php = replace_once(php, "    const VERSION = '0.5.15';", "    const VERSION = '0.5.16';", 'plugin const')

labels_old = """            'highlight'  => 'Fremhævet tekst',
            'spacer'     => 'Afstand',
            'html'       => 'Importeret blok / HTML',
            'css'        => 'Side-CSS (avanceret)',
"""
labels_new = """            'highlight'  => 'Fremhævet tekst',
            'icon'       => 'Ikon / SVG',
            'divider'    => 'Skillelinje',
            'list'       => 'Liste',
            'badge'      => 'Badge / mærkat',
            'quote'      => 'Citat',
            'embed'      => 'Embed / medie-URL',
            'shortcode'  => 'Shortcode (avanceret)',
            'spacer'     => 'Afstand',
            'html'       => 'Importeret blok / HTML',
            'css'        => 'Side-CSS (avanceret)',
"""
php = replace_once(php, labels_old, labels_new, 'type labels')

helper_anchor = """    private function looks_like_page_css($content) {
"""
helper_block = r'''    private function page_primitive_variant_options($type) {
        $type = sanitize_key((string) $type);
        $map = [
            'icon' => [
                'check' => 'Flueben', 'star' => 'Stjerne', 'info' => 'Info', 'location' => 'Placering',
                'calendar' => 'Kalender', 'phone' => 'Telefon', 'mail' => 'E-mail', 'wrench' => 'Værktøj',
                'shield' => 'Skjold', 'arrow' => 'Pil',
            ],
            'divider' => ['solid' => 'Hel linje', 'dashed' => 'Stiplet', 'dotted' => 'Prikket', 'double' => 'Dobbelt'],
            'list' => ['bullets' => 'Punkter', 'numbers' => 'Numre', 'checks' => 'Flueben'],
            'badge' => ['solid' => 'Fyldt', 'outline' => 'Outline'],
            'quote' => ['standard' => 'Standard', 'large' => 'Stort citat'],
        ];
        return $map[$type] ?? ['default' => 'Standard'];
    }

    private function page_editor_safe_icon_svg($name) {
        $name = sanitize_key((string) $name);
        $icons = [
            'check' => '<path d="M20 6 9 17l-5-5"/>',
            'star' => '<path d="m12 2 3.1 6.3 6.9 1-5 4.8 1.2 6.9-6.2-3.3L5.8 21 7 14.1l-5-4.8 6.9-1Z"/>',
            'info' => '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
            'location' => '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
            'calendar' => '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
            'phone' => '<path d="M5 3h4l2 5-2.5 1.8a15 15 0 0 0 5.7 5.7L16 13l5 2v4c0 1.1-.9 2-2 2C10.2 21 3 13.8 3 5c0-1.1.9-2 2-2Z"/>',
            'mail' => '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
            'wrench' => '<path d="M14.5 6.5a4 4 0 0 0-5-5L7 4l3 3-3 3-3-3-2.5 2.5a4 4 0 0 0 5 5L15 23l3-3-8.5-8.5a4 4 0 0 0 5-5Z"/>',
            'shield' => '<path d="M12 2 20 5v6c0 5.2-3.4 9.8-8 11-4.6-1.2-8-5.8-8-11V5Z"/><path d="m8 12 2.5 2.5L16 9"/>',
            'arrow' => '<path d="M5 12h14M14 7l5 5-5 5"/>',
        ];
        $shape = $icons[$name] ?? $icons['check'];
        return '<svg class="h18-safe-icon-svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' . $shape . '</svg>';
    }

    private function render_page_editor_list_primitive(array $section) {
        $content = trim((string) ($section['Content'] ?? ''));
        $variant = (string) ($section['PrimitiveVariant'] ?? 'bullets');
        if ($content === '') {
            return '';
        }
        if (preg_match('/<(?:ul|ol)\b/i', $content)) {
            $html = wp_kses_post($content);
            if ($variant === 'checks') {
                $html = preg_replace('/<ul\b/i', '<ul class="h18-editor-list-checks"', $html, 1);
            }
            return $html;
        }
        $plain = wp_strip_all_tags($content);
        $items = preg_split('/\r\n|\r|\n/', $plain);
        $items = array_values(array_filter(array_map('trim', (array) $items), static function($value) { return $value !== ''; }));
        if (!$items) { return ''; }
        $tag = $variant === 'numbers' ? 'ol' : 'ul';
        $class = $variant === 'checks' ? ' class="h18-editor-list-checks"' : '';
        $html = '<' . $tag . $class . '>';
        foreach (array_slice($items, 0, 100) as $item) {
            $html .= '<li>' . esc_html($item) . '</li>';
        }
        return $html . '</' . $tag . '>';
    }

'''
php = replace_once(php, helper_anchor, helper_block + helper_anchor, 'primitive helpers')

php = replace_once(php, """            'Content'               => '',
            'MediaId'               => 0,
""", """            'Content'               => '',
            'PrimitiveVariant'      => 'default',
            'AdvancedContentAuthorized' => false,
            'MediaId'               => 0,
""", 'default primitive fields')

normalize_anchor = """        $imported_group_type = sanitize_key((string) ($raw['ImportedGroupType'] ?? ''));
        if (!in_array($imported_group_type, ['', 'columns'], true)) {
            $imported_group_type = '';
        }

        $design_mode = (string) ($raw['DesignMode'] ?? 'Global');
"""
normalize_insert = """        $imported_group_type = sanitize_key((string) ($raw['ImportedGroupType'] ?? ''));
        if (!in_array($imported_group_type, ['', 'columns'], true)) {
            $imported_group_type = '';
        }
        $primitive_options = $this->page_primitive_variant_options($type);
        $primitive_variant = sanitize_key((string) ($raw['PrimitiveVariant'] ?? ''));
        if ($primitive_variant === '' || !isset($primitive_options[$primitive_variant])) {
            $primitive_variant = (string) array_key_first($primitive_options);
        }
        $advanced_content_authorized = array_key_exists('AdvancedContentAuthorized', $raw)
            ? $this->bool_value($raw['AdvancedContentAuthorized'], false)
            : false;

        $design_mode = (string) ($raw['DesignMode'] ?? 'Global');
"""
php = replace_once(php, normalize_anchor, normalize_insert, 'normalize primitive fields')

content_old = """            'Title'                 => $title,
            'Content'               => $type === 'css'
                ? $this->sanitize_page_section_css((string) ($raw['Content'] ?? ''))
                : wp_kses_post((string) ($raw['Content'] ?? '')),
            'MediaId'               => absint($raw['MediaId'] ?? 0),
"""
content_new = """            'Title'                 => $title,
            'Content'               => $type === 'css'
                ? $this->sanitize_page_section_css((string) ($raw['Content'] ?? ''))
                : ($type === 'shortcode'
                    ? sanitize_textarea_field((string) ($raw['Content'] ?? ''))
                    : ($type === 'embed'
                        ? esc_url_raw(trim((string) ($raw['Content'] ?? '')))
                        : wp_kses_post((string) ($raw['Content'] ?? '')))),
            'PrimitiveVariant'      => $primitive_variant,
            'AdvancedContentAuthorized' => $advanced_content_authorized,
            'MediaId'               => absint($raw['MediaId'] ?? 0),
"""
php = replace_once(php, content_old, content_new, 'normalized content primitive fields')

# Schema 1.13 in all active page-editor payloads, but do not touch historical readme text here.
if php.count("'Version'        => '1.12'") != 3:
    raise SystemExit("Expected 3 active page schema 1.12 payloads")
php = php.replace("'Version'        => '1.12'", "'Version'        => '1.13'")

# Keep central Hangar18-Pages manifest aligned with page editor schema.
php = php.replace("'Version' => '1.11',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,", "'Version' => '1.13',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php = php.replace("'Version' => '1.11',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,", "'Version' => '1.13',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

# Gutenberg semantic import upgrades.
import_old = """        if (in_array($name, ['core/paragraph', 'core/list', 'core/quote', 'core/table', 'core/preformatted'], true)) {
            $this->page_import_append_text($sections, $html);
            return;
        }
"""
import_new = """        if ($name === 'core/list') {
            $sections[] = $this->page_import_section('list', (count($sections) + 1) * 10, [
                'Content' => $html,
                'PrimitiveVariant' => !empty($attrs['ordered']) ? 'numbers' : 'bullets',
            ]);
            return;
        }
        if ($name === 'core/quote') {
            $sections[] = $this->page_import_section('quote', (count($sections) + 1) * 10, [
                'Content' => $html,
                'PrimitiveVariant' => 'standard',
            ]);
            return;
        }
        if (in_array($name, ['core/paragraph', 'core/table', 'core/preformatted'], true)) {
            $this->page_import_append_text($sections, $html);
            return;
        }
"""
php = replace_once(php, import_old, import_new, 'Gutenberg list/quote import')

separator_old = """        if ($name === 'core/spacer' || $name === 'core/separator') {
            $height = $name === 'core/separator' ? 24 : $this->clamp_int($attrs['height'] ?? 32, 0, 200, 32);
            $sections[] = $this->page_import_section('spacer', (count($sections) + 1) * 10, [
                'SpacerPx'       => $height,
                'MobileSpacerPx' => min($height, 140),
            ]);
            return;
        }
"""
separator_new = """        if ($name === 'core/separator') {
            $sections[] = $this->page_import_section('divider', (count($sections) + 1) * 10, [
                'PrimitiveVariant' => 'solid',
                'BottomSpacingPx' => 24,
                'MobileBottomSpacingPx' => 18,
            ]);
            return;
        }
        if ($name === 'core/spacer') {
            $height = $this->clamp_int($attrs['height'] ?? 32, 0, 200, 32);
            $sections[] = $this->page_import_section('spacer', (count($sections) + 1) * 10, [
                'SpacerPx'       => $height,
                'MobileSpacerPx' => min($height, 140),
            ]);
            return;
        }
"""
php = replace_once(php, separator_old, separator_new, 'Gutenberg separator import')

# Renderer content behavior: explicit shortcode type owns shortcode execution; HTML remains sanitized compatibility content.
render_content_old = """        $content = $section['Type'] === 'html'
            ? do_shortcode(wp_kses_post($content_source))
            : $this->format_page_section_content($content_source);
        $inner = $title . $content;

        if ($section['Type'] === 'hero') {
"""
render_content_new = """        if ($section['Type'] === 'html') {
            $content = wp_kses_post($content_source);
        } elseif ($section['Type'] === 'shortcode') {
            $content = !empty($section['AdvancedContentAuthorized'])
                ? do_shortcode((string) $content_source)
                : '<pre class=\"h18-editor-shortcode-locked\"><code>' . esc_html((string) $content_source) . '</code></pre>';
        } else {
            $content = $this->format_page_section_content($content_source);
        }
        $inner = $title . $content;

        if ($section['Type'] === 'icon') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'check');
            $label = $section['Title'] !== '' ? $section['Title'] : ($this->page_primitive_variant_options('icon')[$variant] ?? 'Ikon');
            $inner = '<div class=\"h18-editor-icon\" role=\"img\" aria-label=\"' . esc_attr($label) . '\">' . $this->page_editor_safe_icon_svg($variant) . '</div>' .
                ($section['Content'] !== '' ? '<div class=\"h18-editor-icon-copy\">' . $this->format_page_section_content($section['Content']) . '</div>' : '');
        } elseif ($section['Type'] === 'divider') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'solid');
            $inner = '<hr class=\"h18-editor-divider h18-editor-divider--' . esc_attr($variant) . '\" aria-hidden=\"true\" />';
        } elseif ($section['Type'] === 'list') {
            $inner = $title . '<div class=\"h18-editor-list\">' . $this->render_page_editor_list_primitive($section) . '</div>';
        } elseif ($section['Type'] === 'badge') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'solid');
            $badge_text = $section['Title'] !== '' ? $section['Title'] : wp_strip_all_tags((string) $section['Content']);
            $inner = '<span class=\"h18-editor-badge h18-editor-badge--' . esc_attr($variant) . '\">' . esc_html($badge_text) . '</span>';
        } elseif ($section['Type'] === 'quote') {
            $variant = (string) ($section['PrimitiveVariant'] ?? 'standard');
            $inner = '<figure class=\"h18-editor-quote h18-editor-quote--' . esc_attr($variant) . '\"><blockquote>' . $this->format_page_section_content($section['Content']) . '</blockquote>' .
                ($section['Title'] !== '' ? '<figcaption>— ' . esc_html($section['Title']) . '</figcaption>' : '') . '</figure>';
        } elseif ($section['Type'] === 'embed') {
            $embed_url = esc_url_raw(trim((string) $section['Content']));
            $embed_html = $embed_url !== '' ? wp_oembed_get($embed_url) : '';
            if (!$embed_html && $embed_url !== '') {
                $embed_html = '<p><a href=\"' . esc_url($embed_url) . '\">' . esc_html($embed_url) . '</a></p>';
            }
            $inner = $title . '<div class=\"h18-editor-embed\">' . (string) $embed_html . '</div>';
        } elseif ($section['Type'] === 'hero') {
"""
php = replace_once(php, render_content_old, render_content_new, 'primitive frontend renderer')

# Frontend primitive CSS before spacer rule.
css_php_old = """            '.h18-editor-spacer{height:var(--h18-spacer,32px)}' .
"""
css_php_new = """            '.h18-editor-icon{display:inline-flex;align-items:center;justify-content:center;font-size:clamp(42px,6vw,84px);line-height:1;color:var(--h18-section-heading,currentColor)}.h18-safe-icon-svg{display:block;width:1em;height:1em}.h18-editor-icon-copy{margin-top:12px}.h18-editor-divider{width:100%;height:0;margin:0;border:0;border-top:var(--h18-section-border-width,2px) solid var(--h18-section-border,#c3ae83)}.h18-editor-divider--dashed{border-top-style:dashed}.h18-editor-divider--dotted{border-top-style:dotted}.h18-editor-divider--double{border-top-style:double;border-top-width:max(3px,var(--h18-section-border-width,3px))}.h18-editor-list>ul,.h18-editor-list>ol{margin:0;padding-left:1.5em}.h18-editor-list-checks{list-style:none!important;padding-left:0!important}.h18-editor-list-checks li{position:relative;padding-left:1.7em}.h18-editor-list-checks li:before{position:absolute;left:0;content:\"✓\";font-weight:800}.h18-editor-badge{display:inline-flex;align-items:center;min-height:30px;padding:5px 12px;border-radius:999px;background:var(--h18-section-heading,#30382a);color:var(--h18-section-bg,#fff);font-size:.88em;font-weight:700;line-height:1.2}.h18-editor-badge--outline{background:transparent;color:inherit;border:1px solid currentColor}.h18-editor-quote{margin:0;padding:18px 22px;border-left:4px solid var(--h18-section-border,#c3ae83)}.h18-editor-quote blockquote{margin:0;font-size:1.15em}.h18-editor-quote--large blockquote{font-size:clamp(1.35em,2.6vw,2em);line-height:1.35}.h18-editor-quote figcaption{margin-top:12px;font-weight:600}.h18-editor-embed{position:relative;max-width:100%;overflow:hidden}.h18-editor-embed iframe,.h18-editor-embed video{max-width:100%}.h18-editor-shortcode-locked{white-space:pre-wrap;padding:12px;border:1px dashed #b32d2e;background:#fcf0f1}' .
            '.h18-editor-spacer{height:var(--h18-spacer,32px)}' .
"""
php = replace_once(php, css_php_old, css_php_new, 'primitive frontend css')

# Admin title/content fields include new semantic types.
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid highlight html mail_form poll"',
    'data-types="hero text text_image image buttons card card_grid highlight icon list badge quote html mail_form poll"',
    'admin title types')
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid highlight html css mail_form poll"',
    'data-types="hero text text_image image buttons card card_grid highlight icon list quote embed shortcode html css mail_form poll"',
    'admin content types')
# The mini toolbar occurrence is separate and identical to title list in current source; replace next exact remaining occurrence.
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid highlight html mail_form poll"><button type="button" class="button h18-mini-format"',
    'data-types="hero text text_image image buttons card card_grid highlight list quote html mail_form poll"><button type="button" class="button h18-mini-format"',
    'mini toolbar types')

content_help_anchor = """                            <p class=\"description h18-section-type-field\" data-types=\"css\"><strong>Avanceret side-CSS:</strong> Bevarer den eksisterende sides farver, kolonner og responsive regler. Ret kun feltet, hvis du kender CSS.</p>
                        </div>
                    </div>

                    <div class=\"h18-section-type-field h18-section-module-box\" data-types=\"hero text_image image\">
"""
primitive_admin = """                            <p class=\"description h18-section-type-field\" data-types=\"css\"><strong>Avanceret side-CSS:</strong> Bevarer den eksisterende sides farver, kolonner og responsive regler. Ret kun feltet, hvis du kender CSS.</p>
                            <p class=\"description h18-section-type-field\" data-types=\"embed\"><strong>Embed:</strong> Indsæt kun en HTTPS-URL fra en WordPress oEmbed-understøttet tjeneste. Ukendte URL'er vises som et almindeligt link.</p>
                            <p class=\"description h18-section-type-field\" data-types=\"shortcode\"><strong>Shortcode:</strong> Koden udføres kun, når den er gemt af en bruger med avanceret indholdsrettighed. Ellers vises den som kode på siden.</p>
                        </div>
                        <div class=\"h18-field h18-section-type-field\" data-types=\"icon divider list badge quote\">
                            <label><strong>Variant</strong></label>
                            <select class=\"h18-primitive-variant\" name=\"<?php echo esc_attr($prefix); ?>[PrimitiveVariant]\">
                                <?php foreach ($this->page_primitive_variant_options($section['Type']) as $variant_value => $variant_label) : ?>
                                    <option value=\"<?php echo esc_attr($variant_value); ?>\" <?php selected($section['PrimitiveVariant'], $variant_value); ?>><?php echo esc_html($variant_label); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                        <input class=\"h18-advanced-content-authorized\" type=\"hidden\" name=\"<?php echo esc_attr($prefix); ?>[AdvancedContentAuthorized]\" value=\"<?php echo !empty($section['AdvancedContentAuthorized']) ? '1' : '0'; ?>\" />
                    </div>

                    <div class=\"h18-section-type-field h18-section-module-box\" data-types=\"hero text_image image\">
"""
php = replace_once(php, content_help_anchor, primitive_admin, 'primitive admin controls')

# Permission-safe shortcode authorization on save. Preserve an existing authorized shortcode for lower roles only if its content is unchanged.
existing_old = """        $legacy_by_key = [];
        foreach ($current['Sections'] as $existing) {
            if ($existing['Type'] === 'legacy') {
                $legacy_by_key[$existing['Key']] = $existing;
            }
        }
"""
existing_new = """        $legacy_by_key = [];
        $current_by_key = [];
        foreach ($current['Sections'] as $existing) {
            if (!empty($existing['Key'])) {
                $current_by_key[(string) $existing['Key']] = $existing;
            }
            if ($existing['Type'] === 'legacy') {
                $legacy_by_key[$existing['Key']] = $existing;
            }
        }
"""
php = replace_once(php, existing_old, existing_new, 'current section index')

save_key_old = """            $key = sanitize_key((string) ($raw['Key'] ?? ''));
            $legacy = isset($legacy_by_key[$key]) ? $legacy_by_key[$key] : [];
            $section = $this->normalize_page_section($raw, $index, $legacy);
"""
save_key_new = """            $key = sanitize_key((string) ($raw['Key'] ?? ''));
            $existing_section = isset($current_by_key[$key]) && is_array($current_by_key[$key]) ? $current_by_key[$key] : [];
            $submitted_type = sanitize_key((string) ($raw['Type'] ?? 'text'));
            if ($submitted_type === 'shortcode') {
                $can_author_advanced = current_user_can('unfiltered_html') || current_user_can('manage_options');
                $same_existing_shortcode = !empty($existing_section) &&
                    ($existing_section['Type'] ?? '') === 'shortcode' &&
                    !empty($existing_section['AdvancedContentAuthorized']) &&
                    (string) ($existing_section['Content'] ?? '') === sanitize_textarea_field((string) ($raw['Content'] ?? ''));
                $raw['AdvancedContentAuthorized'] = $can_author_advanced || $same_existing_shortcode;
            } else {
                $raw['AdvancedContentAuthorized'] = false;
            }
            $legacy = isset($legacy_by_key[$key]) ? $legacy_by_key[$key] : [];
            $section = $this->normalize_page_section($raw, $index, $legacy);
"""
php = replace_once(php, save_key_old, save_key_new, 'shortcode save authorization')

# JS type labels.
labels_js_old = """            buttons: 'Handlingsknapper', card: 'Indholdskort', card_grid: 'Kort-række / kolonner', highlight: 'Fremhævet tekst',
            spacer: 'Afstand', html: 'Importeret blok / HTML', css: 'Side-CSS', mail_form: 'Mailformular', poll: 'Afstemning', legacy: 'Eksisterende indhold'
"""
labels_js_new = """            buttons: 'Handlingsknapper', card: 'Indholdskort', card_grid: 'Kort-række / kolonner', highlight: 'Fremhævet tekst',
            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',
            spacer: 'Afstand', html: 'Importeret blok / HTML', css: 'Side-CSS', mail_form: 'Mailformular', poll: 'Afstemning', legacy: 'Eksisterende indhold'
"""
js = replace_once(js, labels_js_old, labels_js_new, 'JS labels')

# Primitive variant options are rebuilt when type changes.
variant_js_anchor = """    function setInspectorPanel(panel) {
"""
variant_js = r'''    const primitiveVariantOptionsV0516 = {
        icon: { check: 'Flueben', star: 'Stjerne', info: 'Info', location: 'Placering', calendar: 'Kalender', phone: 'Telefon', mail: 'E-mail', wrench: 'Værktøj', shield: 'Skjold', arrow: 'Pil' },
        divider: { solid: 'Hel linje', dashed: 'Stiplet', dotted: 'Prikket', double: 'Dobbelt' },
        list: { bullets: 'Punkter', numbers: 'Numre', checks: 'Flueben' },
        badge: { solid: 'Fyldt', outline: 'Outline' },
        quote: { standard: 'Standard', large: 'Stort citat' }
    };

    function refreshPrimitiveVariantV0516($row) {
        if (!$row || !$row.length) { return; }
        const type = String($row.attr('data-section-type') || 'text');
        const options = primitiveVariantOptionsV0516[type];
        const $select = pageSectionControls($row, '.h18-primitive-variant').first();
        if (!$select.length || !options) { return; }
        const current = String($select.val() || '');
        $select.empty();
        Object.keys(options).forEach(function (value) {
            $select.append($('<option>', { value: value, text: options[value] }));
        });
        $select.val(Object.prototype.hasOwnProperty.call(options, current) ? current : Object.keys(options)[0]);
    }

'''
js = replace_once(js, variant_js_anchor, variant_js + variant_js_anchor, 'JS primitive variant helper')

# Hook variant refresh into type refresh using an existing stable tail call.
refresh_old = """        refreshSectionDesignMode($row);
        refreshSectionBackgroundEffect($row);
        refreshHoverStyleMode($row);
        rebuildPageNavigator();
"""
refresh_new = """        refreshSectionDesignMode($row);
        refreshSectionBackgroundEffect($row);
        refreshHoverStyleMode($row);
        refreshPrimitiveVariantV0516($row);
        rebuildPageNavigator();
"""
js = replace_once(js, refresh_old, refresh_new, 'type refresh hook')

# New section sensible defaults.
defaults_anchor = """        } else if (type === 'card') {
            setValue('Background', 'OffWhite');
"""
defaults_new = """        } else if (type === 'icon') {
            setValue('PrimitiveVariant', 'check');
            setValue('DesktopAlignment', 'Center');
            setValue('MobileAlignment', 'Center');
        } else if (type === 'divider') {
            setValue('PrimitiveVariant', 'solid');
            setValue('BorderWidthPx', 2);
            setValue('BottomSpacingPx', 24);
        } else if (type === 'list') {
            setValue('PrimitiveVariant', 'bullets');
        } else if (type === 'badge') {
            setValue('PrimitiveVariant', 'solid');
            setValue('DesktopAlignment', 'Left');
        } else if (type === 'quote') {
            setValue('PrimitiveVariant', 'standard');
            setValue('BorderWidthPx', 4);
        } else if (type === 'card') {
            setValue('Background', 'OffWhite');
"""
js = replace_once(js, defaults_anchor, defaults_new, 'new primitive defaults')

# Canvas cases before buttons.
canvas_anchor = """        } else if (type === 'buttons') {
            addTitle('Handling');
"""
canvas_new = r'''        } else if (type === 'icon') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'check'));
            const symbols = { check: '✓', star: '★', info: 'ⓘ', location: '⌖', calendar: '▣', phone: '☎', mail: '✉', wrench: '⌕', shield: '◆', arrow: '→' };
            $inner.append($('<div>', { class: 'h18-canvas-primitive-icon', text: symbols[variant] || '✓', title: title || inspectorTypeLabel(type) }));
            if (content) { canvasAddBodyText($inner, content); }
        } else if (type === 'divider') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'solid'));
            $inner.append($('<hr>', { class: 'h18-canvas-primitive-divider h18-canvas-primitive-divider--' + variant }));
        } else if (type === 'list') {
            addTitle('Liste');
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'bullets'));
            const text = $('<div>').html(content).text();
            const items = text.split(/\r?\n|•/).map(function (item) { return item.trim(); }).filter(Boolean).slice(0, 8);
            const $list = $(variant === 'numbers' ? '<ol>' : '<ul>', { class: variant === 'checks' ? 'h18-canvas-list-checks' : '' });
            (items.length ? items : ['Listepunkt']).forEach(function (item) { $list.append($('<li>', { text: item })); });
            $inner.append($list);
        } else if (type === 'badge') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'solid'));
            $inner.append($('<span>', { class: 'h18-canvas-primitive-badge h18-canvas-primitive-badge--' + variant, text: title || $('<div>').html(content).text() || 'Badge' }));
        } else if (type === 'quote') {
            const variant = String(canvasFieldValue($row, 'PrimitiveVariant', 'standard'));
            const $quote = $('<figure>', { class: 'h18-canvas-primitive-quote h18-canvas-primitive-quote--' + variant });
            $quote.append($('<blockquote>', { text: $('<div>').html(content).text() || 'Citat' }));
            if (title) { $quote.append($('<figcaption>', { text: '— ' + title })); }
            $inner.append($quote);
        } else if (type === 'embed') {
            addTitle('Embed');
            $inner.append($('<div>', { class: 'h18-canvas-embed-placeholder' }).append($('<span>', { class: 'dashicons dashicons-video-alt3' }), $('<code>', { text: content || 'Indsæt en medie-URL' })));
        } else if (type === 'shortcode') {
            addTitle('Shortcode');
            $inner.append($('<pre>', { class: 'h18-canvas-shortcode-placeholder' }).append($('<code>', { text: content || '[shortcode]' })));
        } else if (type === 'buttons') {
            addTitle('Handling');
'''
js = replace_once(js, canvas_anchor, canvas_new, 'canvas primitive cases')

# Canvas/admin primitive styles.
css_block = r'''

/* v0.5.16 – E2 element primitives */
.h18-canvas-primitive-icon{font-size:58px;line-height:1;text-align:center;padding:12px}
.h18-canvas-primitive-divider{width:100%;border:0;border-top:2px solid currentColor;opacity:.55}.h18-canvas-primitive-divider--dashed{border-top-style:dashed}.h18-canvas-primitive-divider--dotted{border-top-style:dotted}.h18-canvas-primitive-divider--double{border-top-style:double;border-top-width:4px}
.h18-canvas-list-checks{list-style:none;padding-left:0}.h18-canvas-list-checks li:before{content:'✓';font-weight:800;margin-right:.55em}
.h18-canvas-primitive-badge{display:inline-flex;padding:5px 12px;border-radius:999px;background:currentColor;font-weight:700}.h18-canvas-primitive-badge--outline{background:transparent;border:1px solid currentColor}
.h18-canvas-primitive-quote{margin:0;padding:14px 18px;border-left:4px solid currentColor}.h18-canvas-primitive-quote blockquote{margin:0}.h18-canvas-primitive-quote--large blockquote{font-size:1.5em}.h18-canvas-primitive-quote figcaption{margin-top:9px;font-weight:600}
.h18-canvas-embed-placeholder,.h18-canvas-shortcode-placeholder{box-sizing:border-box;width:100%;padding:16px;border:1px dashed #8c8f94;border-radius:6px;background:rgba(255,255,255,.72);overflow-wrap:anywhere}.h18-canvas-embed-placeholder{display:flex;align-items:center;gap:9px}.h18-canvas-shortcode-placeholder{white-space:pre-wrap}
'''
if '/* v0.5.16 – E2 element primitives */' in css:
    raise SystemExit('v0.5.16 CSS already present')
css = css.rstrip() + css_block + '\n'

readme = replace_once(readme, 'Version: 0.5.15', 'Version: 0.5.16', 'readme version')
readme_anchor = "== Version 0.5.15 – Multi-select, canvas workspace og context menu ==\n"
readme_new = """== Version 0.5.16 – E2 element primitives og sikre embeds ==

Nyt:
- UD-028: sikkert Icon/SVG-element med indbygget allowlist-baseret ikonbibliotek uden rå bruger-SVG
- UD-029: nye semantiske elementer for skillelinje, liste, badge og citat
- Divider-varianter: hel, stiplet, prikket og dobbelt; List-varianter: punkter, numre og flueben
- Badge kan være fyldt/outline, og Quote kan være standard/stort citat
- UD-032: separat Embed-element via WordPress oEmbed og separat avanceret Shortcode-element
- Shortcode autoriseres kun ved gemning af brugere med unfiltered_html/manage_options; lavere roller kan ikke ændre eller indsætte ny eksekverbar shortcode
- eksisterende autoriseret shortcode kan bevares af lavere roller, når selve shortcode-indholdet er uændret
- importerede Gutenberg lister/citater/separatorer konverteres til de nye semantiske elementer
- HTML-elementet udfører ikke længere nye shortcodes implicit; eksplicit Shortcode-element er sikkerhedsgrænsen
- page-editor schema løftes bagudkompatibelt til 1.13

""" + readme_anchor
readme = replace_once(readme, readme_anchor, readme_new, 'readme v0.5.15 anchor')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
print('v0.5.16 patch applied')
