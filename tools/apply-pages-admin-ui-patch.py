from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


php_path = Path('hangar18-manager.php')
php = php_path.read_text(encoding='utf-8')

action_line = "        add_action('wp_ajax_h18_create_page_from_template', [$this, 'ajax_create_page_from_template']);"
php = replace_once(
    php,
    action_line,
    action_line + "\n        add_action('wp_ajax_h18_create_blank_page', [$this, 'ajax_create_blank_page']);",
    'blank page ajax action',
)

# A new template-created page must be marked as managed before its slug is
# normalized, otherwise a new slug can fall back to the Home definition.
template_page_marker = "$page=get_post($post_id);\n        try{$sections=$this->instantiate_page_template_sections"
template_page_fixed = "$page=get_post($post_id);update_post_meta($post_id,'_h18_page_editor_managed','1');\n        try{$sections=$this->instantiate_page_template_sections"
php = replace_once(php, template_page_marker, template_page_fixed, 'template managed-before-normalize fix')

help_box = '            <div class="h18-help-box"><strong>Hangar18 sideeditor:</strong> Byg almindelige sider af indholdssektioner og funktionsmoduler. Header og footer ligger uden for editoren og kan derfor ikke slettes her. Køretøjer, Events og Billedgalleri har fortsat deres egne redigeringssider.</div>'
create_bar = '''            <div class="h18-pages-create-bar">
                <div class="h18-pages-create-copy">
                    <strong>Opret ny side</strong>
                    <span>Start med en tom Hangar18-side, eller brug en gemt Page Template.</span>
                </div>
                <div class="h18-pages-create-actions">
                    <button type="button" class="button button-primary" id="h18-create-blank-page"><span class="dashicons dashicons-plus-alt2" aria-hidden="true"></span> Ny tom side</button>
                    <button type="button" class="button" id="h18-create-from-template"><span class="dashicons dashicons-layout" aria-hidden="true"></span> Fra Page Template…</button>
                </div>
            </div>'''
php = replace_once(php, help_box, help_box + "\n\n" + create_bar, 'pages create bar')

method_marker = "    public function ajax_create_page_from_template() {"
blank_method = '''    public function ajax_create_blank_page() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at oprette sider.'], 403);
        }
        check_ajax_referer('h18_page_templates_v0522', 'nonce');

        $title = sanitize_text_field((string) wp_unslash($_POST['page_title'] ?? ''));
        $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));

        if ($title === '' || $slug === '') {
            wp_send_json_error(['message' => 'Ny side skal have titel og slug.'], 400);
        }
        if (get_page_by_path($slug, OBJECT, 'page')) {
            wp_send_json_error(['message' => 'Der findes allerede en side med denne slug.'], 409);
        }

        $post_id = wp_insert_post([
            'post_type' => 'page',
            'post_status' => 'draft',
            'post_title' => $title,
            'post_name' => $slug,
            'post_content' => '',
        ], true);

        if (is_wp_error($post_id)) {
            wp_send_json_error(['message' => $post_id->get_error_message()], 400);
        }

        $page = get_post($post_id);
        update_post_meta($post_id, '_h18_page_editor_managed', '1');

        try {
            $data = $this->normalize_page_editor_data([
                'Version' => '1.22',
                'PageSlug' => $slug,
                'PageTitle' => $title,
                'ContentVersion' => 1,
                'DataContextType' => '',
                'DataContextEntryId' => 0,
                'Sections' => [],
            ], $page);

            $this->save_page_editor_data($slug, $data);
            $result = wp_update_post([
                'ID' => $post_id,
                'page_template' => 'default',
                'post_content' => $this->wrap_with_shell($this->build_page_editor_core($slug, $data), $post_id),
            ], true);

            if (is_wp_error($result)) {
                throw new RuntimeException($result->get_error_message());
            }

            $this->log('INFO', 'PAGE_CREATE_BLANK', "Ny Hangar18-side '{$title}' ({$slug}) oprettet som kladde.");
            wp_send_json_success([
                'page_id' => $post_id,
                'page_slug' => $slug,
                'manager_url' => admin_url('admin.php?page=hangar18-pages&page_slug=' . rawurlencode($slug)),
                'edit_url' => get_edit_post_link($post_id, 'raw'),
            ]);
        } catch (Throwable $e) {
            wp_delete_post($post_id, true);
            wp_send_json_error(['message' => $e->getMessage()], 400);
        }
    }

'''
php = replace_once(php, method_marker, blank_method + method_marker, 'blank page ajax method')
php_path.write_text(php, encoding='utf-8')

css_path = Path('assets/admin.css')
css = css_path.read_text(encoding='utf-8')
css_marker = '/* v0.5.31 – Sider: full-width workspace og tydelig sideoprettelse */'
if css_marker in css:
    raise SystemExit('admin.css UI patch already present')
css += '''\n\n/* v0.5.31 – Sider: full-width workspace og tydelig sideoprettelse */
.h18-pages-admin{max-width:none!important;margin-right:20px}
.h18-pages-create-bar{display:flex;align-items:center;justify-content:space-between;gap:18px;margin:16px 0;padding:16px 18px;border:1px solid #c3c4c7;border-left:5px solid #3858e9;border-radius:9px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.h18-pages-create-copy{display:flex;min-width:0;flex-direction:column;gap:3px}.h18-pages-create-copy strong{font-size:15px;color:#1d2327}.h18-pages-create-copy span{color:#646970}
.h18-pages-create-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.h18-pages-create-actions .button{display:inline-flex;align-items:center;gap:6px;min-height:38px}.h18-pages-create-actions .dashicons{width:18px;height:18px;font-size:18px}
.h18-pages-admin .h18-visual-builder{grid-template-columns:minmax(220px,250px) minmax(700px,1fr) minmax(320px,380px);gap:18px}
.h18-pages-admin .h18-builder-canvas{min-width:0;min-height:calc(100vh - 255px)}
.h18-pages-admin .h18-builder-palette,.h18-pages-admin .h18-builder-inspector{min-width:0}
@media(max-width:1500px){.h18-pages-admin .h18-visual-builder{grid-template-columns:210px minmax(480px,1fr) 330px}}
@media(max-width:1180px){.h18-pages-admin .h18-visual-builder{grid-template-columns:200px minmax(0,1fr)}.h18-pages-admin .h18-builder-inspector{position:static;grid-column:1/-1;max-height:none}}
@media(max-width:782px){.h18-pages-admin{margin-right:10px}.h18-pages-create-bar{align-items:stretch;flex-direction:column}.h18-pages-create-actions{display:grid;grid-template-columns:1fr}.h18-pages-create-actions .button{justify-content:center}.h18-pages-admin .h18-visual-builder{grid-template-columns:1fr}.h18-pages-admin .h18-builder-palette{position:static}.h18-pages-admin .h18-builder-inspector{grid-column:auto}}
'''
css_path.write_text(css, encoding='utf-8')

js_path = Path('assets/admin.js')
js = js_path.read_text(encoding='utf-8')
js_marker = '/* v0.5.31 – tydelig oprettelse af sider */'
if js_marker in js:
    raise SystemExit('admin.js UI patch already present')
close_at = js.rfind('\n});')
if close_at < 0:
    raise SystemExit('Could not find final jQuery wrapper close in admin.js')
js_insert = r'''

    /* v0.5.31 – tydelig oprettelse af sider */
    function h18PromptNewPageIdentity(defaultTitle) {
        const title = window.prompt('Titel på den nye WordPress-side:', defaultTitle || 'Ny side');
        if (!title || !String(title).trim()) { return null; }
        const suggested = slugify(String(title));
        const slug = window.prompt('Slug til den nye side:', suggested);
        if (!slug || !String(slug).trim()) { return null; }
        return { title: String(title).trim(), slug: slugify(String(slug)) };
    }

    $(document).on('click', '#h18-create-blank-page', function () {
        const identity = h18PromptNewPageIdentity('Ny side');
        if (!identity || !identity.slug) { return; }
        const $button = $(this);
        const originalText = $button.text();
        $button.prop('disabled', true).text('Opretter…');
        $.post(Hangar18Manager.ajaxUrl || window.ajaxurl, {
            action: 'h18_create_blank_page',
            nonce: Hangar18Manager.pageTemplateNonce,
            page_title: identity.title,
            page_slug: identity.slug
        }).done(function (response) {
            if (!response || !response.success || !response.data) {
                window.alert((response && response.data && response.data.message) || 'Siden kunne ikke oprettes.');
                return;
            }
            if (response.data.manager_url) { window.location.href = response.data.manager_url; }
        }).fail(function (xhr) {
            window.alert((xhr.responseJSON && xhr.responseJSON.data && xhr.responseJSON.data.message) || 'Siden kunne ikke oprettes.');
        }).always(function () {
            $button.prop('disabled', false).text(originalText);
        });
    });

    $(document).on('click', '#h18-create-from-template', function () {
        $('.h18-builder-sidebar-tab[data-builder-tab="components"]').trigger('click');
        const target = document.getElementById('h18-page-templates-list');
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        if (typeof pageTemplatesV0522 !== 'undefined' && !Object.keys(pageTemplatesV0522).length) {
            window.alert('Der er ingen Page Templates endnu. Du kan oprette en tom side nu eller gemme den aktuelle side som template først.');
        }
    });
'''
js = js[:close_at] + js_insert + js[close_at:]
js_path.write_text(js, encoding='utf-8')
