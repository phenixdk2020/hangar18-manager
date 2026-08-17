from pathlib import Path

p = Path('hangar18-manager.php')
j = Path('assets/admin.js')
c = Path('assets/admin.css')
r = Path('readme.txt')
php = p.read_text(encoding='utf-8')
js = j.read_text(encoding='utf-8')
css = c.read_text(encoding='utf-8')
readme = r.read_text(encoding='utf-8')

def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(label + ': anchor not found')
    return text.replace(old, new, 1)

php = rep(php, ' * Version: 0.5.1', ' * Version: 0.5.2', 'version')
php = rep(php, "const VERSION = '0.5.1';", "const VERSION = '0.5.2';", 'constant')
php = php.replace("'Version'        => '1.5'", "'Version'        => '1.6'")
php = php.replace("'Version' => '1.5'", "'Version' => '1.6'")

php = rep(php,
"            'OverlayOpacityPercent' => 35,\n            'ImportedGroupType'     => '',",
"            'OverlayOpacityPercent' => 35,\n            'DesignMode'             => 'Global',\n            'CustomBackgroundColor'  => '#ffffff',\n            'CustomTextColor'        => '#30382a',\n            'CustomHeadingColor'     => '#30382a',\n            'BorderWidthPx'          => 0,\n            'CustomBorderColor'      => '#c3ae83',\n            'ShadowStyle'            => 'None',\n            'ImportedGroupType'     => '',",
'default design fields')

anchor = "        $imported_group_type = sanitize_key((string) ($raw['ImportedGroupType'] ?? ''));\n        if (!in_array($imported_group_type, ['', 'columns'], true)) {\n            $imported_group_type = '';\n        }\n\n        $cards = [];"
insert = "        $imported_group_type = sanitize_key((string) ($raw['ImportedGroupType'] ?? ''));\n        if (!in_array($imported_group_type, ['', 'columns'], true)) {\n            $imported_group_type = '';\n        }\n\n        $design_mode = (string) ($raw['DesignMode'] ?? 'Global');\n        if (!in_array($design_mode, ['Global', 'Custom'], true)) { $design_mode = 'Global'; }\n        $shadow_style = (string) ($raw['ShadowStyle'] ?? 'None');\n        if (!in_array($shadow_style, ['None', 'Soft', 'Medium', 'Strong'], true)) { $shadow_style = 'None'; }\n        $custom_background = sanitize_hex_color((string) ($raw['CustomBackgroundColor'] ?? '#ffffff')) ?: '#ffffff';\n        $custom_text = sanitize_hex_color((string) ($raw['CustomTextColor'] ?? '#30382a')) ?: '#30382a';\n        $custom_heading = sanitize_hex_color((string) ($raw['CustomHeadingColor'] ?? '#30382a')) ?: '#30382a';\n        $custom_border = sanitize_hex_color((string) ($raw['CustomBorderColor'] ?? '#c3ae83')) ?: '#c3ae83';\n\n        $cards = [];"
php = rep(php, anchor, insert, 'normalize design fields')

php = rep(php,
"            'OverlayOpacityPercent' => $this->clamp_int($raw['OverlayOpacityPercent'] ?? 35, 0, 90, 35),\n            'ImportedGroupType'     => $imported_group_type,",
"            'OverlayOpacityPercent' => $this->clamp_int($raw['OverlayOpacityPercent'] ?? 35, 0, 90, 35),\n            'DesignMode'             => $design_mode,\n            'CustomBackgroundColor'  => $custom_background,\n            'CustomTextColor'        => $custom_text,\n            'CustomHeadingColor'     => $custom_heading,\n            'BorderWidthPx'          => $this->clamp_int($raw['BorderWidthPx'] ?? 0, 0, 12, 0),\n            'CustomBorderColor'      => $custom_border,\n            'ShadowStyle'            => $shadow_style,\n            'ImportedGroupType'     => $imported_group_type,",
'return design fields')

old = """    private function page_editor_section_style(array $section) {
        return '--h18-top:' . (int) $section['TopSpacingPx'] . 'px;' .
            '--h18-bottom:' . (int) $section['BottomSpacingPx'] . 'px;' .
            '--h18-mobile-top:' . (int) $section['MobileTopSpacingPx'] . 'px;' .
            '--h18-mobile-bottom:' . (int) $section['MobileBottomSpacingPx'] . 'px;' .
            '--h18-pad:' . (int) $section['PaddingPx'] . 'px;' .
            '--h18-pad-x:' . (int) $section['HorizontalPaddingPx'] . 'px;' .
            '--h18-mobile-pad:' . (int) $section['MobilePaddingPx'] . 'px;' .
            '--h18-mobile-pad-x:' . (int) $section['MobileHorizontalPaddingPx'] . 'px;' .
            '--h18-radius:' . (int) $section['RadiusPx'] . 'px;' .
            '--h18-align:' . ($section['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
            '--h18-mobile-align:' . ($section['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';' .
            '--h18-justify:' . ($section['DesktopAlignment'] === 'Center' ? 'center' : 'flex-start') . ';' .
            '--h18-mobile-justify:' . ($section['MobileAlignment'] === 'Center' ? 'center' : 'flex-start') . ';';
    }"""
new = """    private function page_editor_section_style(array $section) {
        $preset = (string) ($section['Background'] ?? 'White');
        $backgrounds = [
            'White' => 'var(--h18-color-background,#ffffff)',
            'OffWhite' => 'var(--h18-color-surface,#f2f0e8)',
            'Sand' => 'var(--h18-color-accent,#c3ae83)',
            'Olive' => 'var(--h18-color-primary,#30382a)',
            'Steel' => 'var(--h18-color-secondary,#525a5f)',
        ];
        $dark = in_array($preset, ['Olive', 'Steel'], true);
        if (($section['DesignMode'] ?? 'Global') === 'Custom') {
            $bg = (string) $section['CustomBackgroundColor'];
            $text = (string) $section['CustomTextColor'];
            $heading = (string) $section['CustomHeadingColor'];
        } else {
            $bg = $backgrounds[$preset] ?? $backgrounds['White'];
            $text = $dark ? 'var(--h18-color-light,#ffffff)' : 'var(--h18-color-text,#30382a)';
            $heading = $text;
        }
        $shadows = [
            'None' => 'none',
            'Soft' => '0 6px 18px rgba(0,0,0,.08)',
            'Medium' => '0 12px 30px rgba(0,0,0,.14)',
            'Strong' => '0 18px 44px rgba(0,0,0,.22)',
        ];
        $shadow = $shadows[$section['ShadowStyle'] ?? 'None'] ?? 'none';
        return '--h18-top:' . (int) $section['TopSpacingPx'] . 'px;' .
            '--h18-bottom:' . (int) $section['BottomSpacingPx'] . 'px;' .
            '--h18-mobile-top:' . (int) $section['MobileTopSpacingPx'] . 'px;' .
            '--h18-mobile-bottom:' . (int) $section['MobileBottomSpacingPx'] . 'px;' .
            '--h18-pad:' . (int) $section['PaddingPx'] . 'px;' .
            '--h18-pad-x:' . (int) $section['HorizontalPaddingPx'] . 'px;' .
            '--h18-mobile-pad:' . (int) $section['MobilePaddingPx'] . 'px;' .
            '--h18-mobile-pad-x:' . (int) $section['MobileHorizontalPaddingPx'] . 'px;' .
            '--h18-radius:' . (int) $section['RadiusPx'] . 'px;' .
            '--h18-align:' . ($section['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
            '--h18-mobile-align:' . ($section['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';' .
            '--h18-justify:' . ($section['DesktopAlignment'] === 'Center' ? 'center' : 'flex-start') . ';' .
            '--h18-mobile-justify:' . ($section['MobileAlignment'] === 'Center' ? 'center' : 'flex-start') . ';' .
            '--h18-section-bg:' . $bg . ';' .
            '--h18-section-text:' . $text . ';' .
            '--h18-section-heading:' . $heading . ';' .
            '--h18-section-border:' . (string) $section['CustomBorderColor'] . ';' .
            '--h18-section-border-width:' . (int) $section['BorderWidthPx'] . 'px;' .
            '--h18-section-shadow:' . $shadow . ';';
    }"""
php = rep(php, old, new, 'runtime style')

old_ui = """                        <div class=\"h18-module-fields-grid\"><div class=\"h18-field\"><label><strong>Baggrund</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[Background]\"><option value=\"White\" <?php selected($section['Background'], 'White'); ?>>Hvid</option><option value=\"OffWhite\" <?php selected($section['Background'], 'OffWhite'); ?>>Knækket hvid</option><option value=\"Sand\" <?php selected($section['Background'], 'Sand'); ?>>Sandfarvet</option><option value=\"Olive\" <?php selected($section['Background'], 'Olive'); ?>>Mørk olivengrøn</option><option value=\"Steel\" <?php selected($section['Background'], 'Steel'); ?>>Stålgrå</option></select><p class=\"description\">Farven på hele sektionen. De samme designfarver bruges på tværs af siderne.</p></div><div class=\"h18-field\"><label><strong>Hjørneafrunding (px)</strong></label><input type=\"number\" min=\"0\" max=\"30\" name=\"<?php echo esc_attr($prefix); ?>[RadiusPx]\" value=\"<?php echo esc_attr($section['RadiusPx']); ?>\" /><p class=\"description\">0 giver lige kanter som på den oprindelige Hjem-side.</p></div></div>
                    </details>"""
new_ui = """                        <div class=\"h18-module-fields-grid\"><div class=\"h18-field\"><label><strong>Baggrund</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[Background]\"><option value=\"White\" <?php selected($section['Background'], 'White'); ?>>Hvid</option><option value=\"OffWhite\" <?php selected($section['Background'], 'OffWhite'); ?>>Knækket hvid</option><option value=\"Sand\" <?php selected($section['Background'], 'Sand'); ?>>Sandfarvet</option><option value=\"Olive\" <?php selected($section['Background'], 'Olive'); ?>>Mørk olivengrøn</option><option value=\"Steel\" <?php selected($section['Background'], 'Steel'); ?>>Stålgrå</option></select><p class=\"description\">Bruges når elementet følger Globalt design.</p></div><div class=\"h18-field\"><label><strong>Hjørneafrunding (px)</strong></label><input type=\"number\" min=\"0\" max=\"30\" name=\"<?php echo esc_attr($prefix); ?>[RadiusPx]\" value=\"<?php echo esc_attr($section['RadiusPx']); ?>\" /></div></div>
                        <div class=\"h18-element-design-box\">
                            <h4>Individuelt elementdesign</h4>
                            <div class=\"h18-module-fields-grid h18-module-fields-grid--four\">
                                <div class=\"h18-field\"><label><strong>Farvetilstand</strong></label><select class=\"h18-section-design-mode\" name=\"<?php echo esc_attr($prefix); ?>[DesignMode]\"><option value=\"Global\" <?php selected($section['DesignMode'], 'Global'); ?>>Globalt design</option><option value=\"Custom\" <?php selected($section['DesignMode'], 'Custom'); ?>>Tilpasset</option></select></div>
                                <div class=\"h18-field\"><label><strong>Kantbredde (px)</strong></label><input type=\"number\" min=\"0\" max=\"12\" name=\"<?php echo esc_attr($prefix); ?>[BorderWidthPx]\" value=\"<?php echo esc_attr($section['BorderWidthPx']); ?>\" /></div>
                                <div class=\"h18-field\"><label><strong>Kantfarve</strong></label><input type=\"color\" name=\"<?php echo esc_attr($prefix); ?>[CustomBorderColor]\" value=\"<?php echo esc_attr($section['CustomBorderColor']); ?>\" /></div>
                                <div class=\"h18-field\"><label><strong>Skygge</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[ShadowStyle]\"><option value=\"None\" <?php selected($section['ShadowStyle'], 'None'); ?>>Ingen</option><option value=\"Soft\" <?php selected($section['ShadowStyle'], 'Soft'); ?>>Blød</option><option value=\"Medium\" <?php selected($section['ShadowStyle'], 'Medium'); ?>>Mellem</option><option value=\"Strong\" <?php selected($section['ShadowStyle'], 'Strong'); ?>>Kraftig</option></select></div>
                            </div>
                            <div class=\"h18-custom-design-fields\">
                                <div class=\"h18-module-fields-grid h18-module-fields-grid--four\">
                                    <div class=\"h18-field\"><label><strong>Baggrund</strong></label><input type=\"color\" name=\"<?php echo esc_attr($prefix); ?>[CustomBackgroundColor]\" value=\"<?php echo esc_attr($section['CustomBackgroundColor']); ?>\" /></div>
                                    <div class=\"h18-field\"><label><strong>Tekst</strong></label><input type=\"color\" name=\"<?php echo esc_attr($prefix); ?>[CustomTextColor]\" value=\"<?php echo esc_attr($section['CustomTextColor']); ?>\" /></div>
                                    <div class=\"h18-field\"><label><strong>Overskrifter</strong></label><input type=\"color\" name=\"<?php echo esc_attr($prefix); ?>[CustomHeadingColor]\" value=\"<?php echo esc_attr($section['CustomHeadingColor']); ?>\" /></div>
                                </div>
                            </div>
                        </div>
                    </details>"""
php = rep(php, old_ui, new_ui, 'admin design controls')

css_anchor = "            '.h18-editor-spacer{height:var(--h18-spacer,32px)}' .\n            '@media(max-width:782px){"
css_new = "            '.h18-editor-spacer{height:var(--h18-spacer,32px)}' .\n            'body.page .h18-editor-page>.h18-editor-section{background:var(--h18-section-bg)!important;color:var(--h18-section-text)!important;border:var(--h18-section-border-width,0) solid var(--h18-section-border,transparent);box-shadow:var(--h18-section-shadow,none)}' .\n            'body.page .h18-editor-page>.h18-editor-section h1,body.page .h18-editor-page>.h18-editor-section h2,body.page .h18-editor-page>.h18-editor-section h3{color:var(--h18-section-heading)!important}' .\n            'body.page .h18-editor-page>.h18-editor-section .h18-editor-grid-card h3{color:inherit!important}' .\n            '@media(max-width:782px){"
php = rep(php, css_anchor, css_new, 'frontend design css')

helper_anchor = "    function refreshPageSectionType($row) {"
helper = """    function refreshSectionDesignMode($row) {
        if (!$row || !$row.length) { return; }
        const custom = String(pageSectionControls($row, '.h18-section-design-mode').val() || 'Global') === 'Custom';
        pageSectionControls($row, '.h18-custom-design-fields').toggle(custom);
    }

"""
js = rep(js, helper_anchor, helper + helper_anchor, 'js design helper')
js = rep(js,
"        refreshInspectorMeta($row);\n        rebuildPageNavigator();\n    }",
"        refreshInspectorMeta($row);\n        refreshSectionDesignMode($row);\n        rebuildPageNavigator();\n    }",
'refresh custom controls')
js = rep(js,
"    $(document).on('change', '.h18-section-active', rebuildPageNavigator);",
"    $(document).on('change', '.h18-section-active', rebuildPageNavigator);\n    $(document).on('change', '.h18-section-design-mode', function () { refreshSectionDesignMode(pageSectionForElement(this)); });",
'design mode event')

css += """

/* v0.5.2 – individuelt elementdesign */
.h18-element-design-box{margin-top:18px;padding-top:16px;border-top:1px solid #dcdcde}
.h18-element-design-box h4{margin:0 0 10px}
.h18-custom-design-fields{margin-top:12px;padding:12px;border:1px solid #dcdcde;border-radius:7px;background:#f6f7f7}
.h18-custom-design-fields input[type=color]{width:100%;min-height:38px;padding:2px}
"""

if 'Version: 0.5.1' not in readme:
    raise SystemExit('readme version missing')
readme = readme.replace('Version: 0.5.1', 'Version: 0.5.2', 1)
readme += """

== Version 0.5.2 – Individuelt elementdesign ==

- Hver editorsektion kan følge Globalt design eller bruge Tilpasset farvetilstand.
- Tilpasset tilstand giver egne farver for baggrund, tekst og overskrifter.
- Hvert element kan få egen kantbredde, kantfarve og skygge.
- Globalt design er fortsat standard, så eksisterende sider beholder deres udseende efter opdatering.
- Page-editor dataformatet er kompatibelt løftet fra schema 1.5 til 1.6.
"""

p.write_text(php, encoding='utf-8')
j.write_text(js, encoding='utf-8')
c.write_text(css, encoding='utf-8')
r.write_text(readme, encoding='utf-8')
