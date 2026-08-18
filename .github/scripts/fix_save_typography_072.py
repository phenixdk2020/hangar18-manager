from pathlib import Path

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')
php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# 1) Make the optional save note explicit in markup and expose active editor version.
old = '''                    <div class="h18-form-header">
                        <div><h2><?php echo esc_html($definitions[$slug]); ?></h2><p>Tilføj sektioner, træk dem i den ønskede rækkefølge, og kontrollér desktop- og mobilvisningen.</p></div>
                        <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                    </div>'''
new = '''                    <div class="h18-form-header">
                        <div><h2><?php echo esc_html($definitions[$slug]); ?></h2><p>Tilføj sektioner, træk dem i den ønskede rækkefølge, og kontrollér desktop- og mobilvisningen.</p><small class="h18-editor-version">Editor v<?php echo esc_html(self::VERSION); ?></small></div>
                        <label class="h18-safe-switch"><input type="checkbox" name="whatif" value="1" /> <span>WhatIf / simulering</span></label>
                    </div>'''
if php.count(old) != 1:
    raise SystemExit(f'form header anchor count={php.count(old)}')
php = php.replace(old, new, 1)

old = '<textarea name="page_change_note" rows="3" maxlength="500" placeholder="Valgfrit: skriv evt. hvorfor du lavede ændringen eller noget systemet ikke selv kan se."></textarea>'
new = '<textarea name="page_change_note" rows="3" maxlength="500" aria-required="false" placeholder="Valgfrit: skriv evt. hvorfor du lavede ændringen eller noget systemet ikke selv kan se."></textarea>'
if php.count(old) != 1:
    raise SystemExit(f'optional textarea anchor count={php.count(old)}')
php = php.replace(old, new, 1)

# 2) Strong cache-busting for admin JS/CSS, including development/hotfix file changes.
old = '''        wp_enqueue_style(
            'hangar18-manager-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.css',
            [],
            self::VERSION
        );

        wp_enqueue_script(
            'hangar18-manager-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.js',
            ['jquery', 'jquery-ui-sortable'],
            self::VERSION,
            true
        );'''
new = '''        $admin_css_path = plugin_dir_path(__FILE__) . 'assets/admin.css';
        $admin_js_path = plugin_dir_path(__FILE__) . 'assets/admin.js';
        $admin_css_version = self::VERSION . '-' . (is_file($admin_css_path) ? (string) filemtime($admin_css_path) : '0');
        $admin_js_version = self::VERSION . '-' . (is_file($admin_js_path) ? (string) filemtime($admin_js_path) : '0');

        wp_enqueue_style(
            'hangar18-manager-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.css',
            [],
            $admin_css_version
        );

        wp_enqueue_script(
            'hangar18-manager-admin',
            plugin_dir_url(__FILE__) . 'assets/admin.js',
            ['jquery', 'jquery-ui-sortable'],
            $admin_js_version,
            true
        );'''
if php.count(old) != 1:
    raise SystemExit(f'asset enqueue anchor count={php.count(old)}')
php = php.replace(old, new, 1)

# 3) Defensive client-side optional-note guard. This also clears custom validity if stale markup/scripts set it.
old = '''    let h18EditorDirtyV064 = false;
    let h18EditorSubmittingV064 = false;

    // v0.7.1: deterministic automatic change summary; manual note remains optional.'''
new = '''    let h18EditorDirtyV064 = false;
    let h18EditorSubmittingV064 = false;
    const $h18PageChangeNoteV072 = $h18PageEditorFormV064.find('[name="page_change_note"]');

    function h18MakeChangeNoteOptionalV072() {
        $h18PageChangeNoteV072.prop('required', false).removeAttr('required').attr('aria-required', 'false').each(function () {
            if (typeof this.setCustomValidity === 'function') { this.setCustomValidity(''); }
        });
    }

    // v0.7.1: deterministic automatic change summary; manual note remains optional.'''
if js.count(old) != 1:
    raise SystemExit(f'JS variable anchor count={js.count(old)}')
js = js.replace(old, new, 1)

old = '''    if ($h18PageEditorFormV064.length) {
        h18AutoSummaryBaselineV071 = h18CollectChangeSummaryModelV071();'''
new = '''    if ($h18PageEditorFormV064.length) {
        h18MakeChangeNoteOptionalV072();
        h18AutoSummaryBaselineV071 = h18CollectChangeSummaryModelV071();'''
if js.count(old) != 1:
    raise SystemExit(f'JS form init anchor count={js.count(old)}')
js = js.replace(old, new, 1)

old = '''        $h18PageEditorFormV064.on('submit', function (event) {
            h18RefreshAutomaticSummaryV071();'''
new = '''        $h18PageEditorFormV064.on('submit', function (event) {
            h18MakeChangeNoteOptionalV072();
            h18RefreshAutomaticSummaryV071();'''
if js.count(old) != 1:
    raise SystemExit(f'JS submit anchor count={js.count(old)}')
js = js.replace(old, new, 1)

# 4) Typography tab bug: the typography box is nested inside element-design-box.
# The old selector hid the parent, therefore the child could never become visible.
old = '''/* v0.6.2 – rich-text toggle og tydelig typografi-fane */
.h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(2,minmax(0,1fr))}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>*{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout{display:block!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>summary{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>*:not(.h18-element-typography-box):not(summary){display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target .h18-element-typography-box{display:block!important;margin:0;padding:0;border-top:0}
.h18-builder-inspector[data-inspector-panel="design"] #h18-page-inspector-target .h18-element-typography-box{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] .h18-module-fields-grid--four{grid-template-columns:1fr 1fr}
.h18-builder-inspector[data-inspector-panel="typography"] .h18-field{min-width:0}'''
new = '''/* v0.7.2 – Typografi-fanen viser det eksisterende typography-panel korrekt. */
.h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(2,minmax(0,1fr))}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>*{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout{display:block!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>summary{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>*:not(.h18-element-design-box):not(summary){display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>.h18-element-design-box{display:block!important;margin:0;padding:0;border:0;background:transparent;box-shadow:none}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target .h18-element-design-box>*{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target .h18-element-design-box>.h18-element-typography-box{display:block!important;margin:0;padding:0;border-top:0}
.h18-builder-inspector[data-inspector-panel="design"] #h18-page-inspector-target .h18-element-typography-box{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] .h18-element-typography-box .h18-module-fields-grid--four{display:grid!important;grid-template-columns:1fr 1fr}
.h18-builder-inspector[data-inspector-panel="typography"] .h18-element-typography-box .h18-field{display:block!important;min-width:0}
.h18-editor-version{display:inline-block;margin-top:5px;color:#646970;font-size:11px}'''
if css.count(old) != 1:
    raise SystemExit(f'typography CSS anchor count={css.count(old)}')
css = css.replace(old, new, 1)

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
