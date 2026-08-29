from pathlib import Path
import json

ROOT = Path('.')

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/hangar18-manager.php'
s=read(path)
s=replace_once(s,' * Version: 0.1.46',' * Version: 0.1.47','version header')
s=replace_once(s,"define('H18_CLEAN_VERSION', '0.1.46');","define('H18_CLEAN_VERSION', '0.1.47');",'version constant')
write(path,s)

# ---------------------------------------------------------------------------
# BUG-18: root virtual page has zero internal editor padding/border.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/assets/editor.css'
s=read(path)
s=replace_once(s,'.h18-clean-root{background:#fff;min-height:650px;padding:8px;border:1px solid #a7aaad}',
                  '.h18-clean-root{background:#fff;min-height:650px;padding:0;border:0}',
                  'root padding')
write(path,s)

path='clean/hangar18-manager/assets/editor-v0144.css'
s=read(path)
s=replace_once(s,'    box-sizing:border-box;\n}',
                  '    box-sizing:border-box;\n    background:#fff;\n    box-shadow:0 0 0 1px #a7aaad;\n}',
                  'stage chrome')
write(path,s)

# ---------------------------------------------------------------------------
# BUG-17: frontend vertical alignment owns one content wrapper, not every
# inline STRONG/EM/U fragment as a flex item.
# Also expose a standalone canonical document for composite preview.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/src/Frontend/Renderer.php'
s=read(path)
s=replace_once(s,'final class Renderer\n{\n', 'final class Renderer\n{\n    private static bool $forceStandaloneCss = false;\n\n', 'renderer force flag')
old_css_guard="""    public static function css(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $postId = get_queried_object_id();
        if ($postId <= 0 || (!metadata_exists('post', $postId, LayoutModel::META) && self::previewModel($postId) === null)) {
            return;
        }
"""
new_css_guard="""    public static function css(): void
    {
        if (!self::$forceStandaloneCss) {
            if (!is_singular('page')) {
                return;
            }
            $postId = get_queried_object_id();
            if ($postId <= 0 || (!metadata_exists('post', $postId, LayoutModel::META) && self::previewModel($postId) === null)) {
                return;
            }
        }
"""
s=replace_once(s,old_css_guard,new_css_guard,'renderer css guard')
old_return="""            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-text\" style=\"' . esc_attr($textStyle) . '\">' . $headingHtml . $bodyHtml . '</div>';
"""
new_return="""            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-text\" style=\"' . esc_attr($textStyle) . '\"><div class=\"h18-clean-front-text-content\">' . $headingHtml . $bodyHtml . '</div></div>';
"""
s=replace_once(s,old_return,new_return,'rich text content wrapper')
anchor='''    public static function menuScript(): void
    {
'''
standalone=r'''    /**
     * Standalone canonical preview used by the Designer while Theme Shell is OFF.
     * Header, page and Footer are rendered by the same PHP renderer as frontend.
     *
     * @param array<string,mixed> $pageModel
     * @param array<string,mixed>|null $headerModel
     * @param array<string,mixed>|null $footerModel
     */
    public static function standaloneDocument(array $pageModel, ?array $headerModel, ?array $footerModel, string $title = 'Visual Designer preview'): string
    {
        $previous = self::$forceStandaloneCss;
        self::$forceStandaloneCss = true;
        ob_start();
        self::css();
        $style = (string) ob_get_clean();
        self::$forceStandaloneCss = $previous;

        $header = $headerModel !== null ? self::renderModel(LayoutModel::normalize($headerModel)) : '';
        $page = self::renderModel(LayoutModel::normalize($pageModel));
        $footer = $footerModel !== null ? self::renderModel(LayoutModel::normalize($footerModel)) : '';
        $safeTitle = esc_html($title);

        return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' . $safeTitle . '</title>'
            . $style
            . '<style>html,body{margin:0;padding:0;background:#fff;color:#1d2327}body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.h18-vd-composite-part{width:100%;margin:0;padding:0}.h18-vd-composite-main{min-height:320px}.h18-clean-front-text-content{display:block;min-width:0}.h18-clean-front-text-content>p:first-child{margin-top:0!important}.h18-clean-front-text-content>p:last-child{margin-bottom:0!important}</style>'
            . '</head><body><header class="h18-vd-composite-part h18-vd-composite-header">' . $header . '</header><main class="h18-vd-composite-part h18-vd-composite-main">' . $page . '</main><footer class="h18-vd-composite-part h18-vd-composite-footer">' . $footer . '</footer>'
            . '<script>document.addEventListener("click",function(e){var b=e.target.closest(".h18-clean-front-menu-toggle");if(!b)return;var n=b.closest(".h18-clean-front-menu");if(!n)return;var open=!n.classList.contains("is-open");n.classList.toggle("is-open",open);b.setAttribute("aria-expanded",open?"true":"false");});</script></body></html>';
    }

'''
s=replace_once(s,anchor,standalone+anchor,'standalone renderer')
write(path,s)

# ---------------------------------------------------------------------------
# BUG-02 regression: strengthen native selection ownership and make the
# permanent QA marker explicit.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/assets/editor-v0125.js'
s=read(path)
s=replace_once(s,'    var selectionGeneration = 0;\n', '    var selectionGeneration = 0;\n    var selectionHoldUntil = 0;\n', 'selection hold state')
s=replace_once(s,"""        window.setTimeout(restore, 0);
        window.setTimeout(restore, 24);
        if (window.requestAnimationFrame) { window.requestAnimationFrame(restore); }
""","""        window.setTimeout(restore, 0);
        window.setTimeout(restore, 24);
        window.setTimeout(restore, 80);
        window.setTimeout(restore, 180);
        window.setTimeout(restore, 320);
        if (window.requestAnimationFrame) { window.requestAnimationFrame(restore); }
""",'selection restore burst')
s=replace_once(s,"""        if (logicalSelection) { active.savedLogical = captureLogicalSelection(active.editor) || logicalSelection; }
        active.dirty = true;
""","""        if (logicalSelection) { active.savedLogical = captureLogicalSelection(active.editor) || logicalSelection; }
        selectionHoldUntil = Date.now() + 360;
        active.dirty = true;
""",'selection hold after command')
s=replace_once(s,"""        button.type = 'button';
        button.className = 'button h18-vd-rich-button';
""","""        button.type = 'button';
        button.tabIndex = -1;
        button.className = 'button h18-vd-rich-button';
""",'toolbar tabindex')
s=replace_once(s,"""        button.addEventListener('mousedown', function (event) { event.preventDefault(); });
        button.addEventListener('click', function (event) {
""","""        button.addEventListener('mousedown', function (event) { event.preventDefault(); });
        button.addEventListener('pointerup', function (event) { event.preventDefault(); });
        button.addEventListener('click', function (event) {
""",'toolbar pointerup')
# Add a short-lived guard against Firefox/Chrome toolbar focus collapsing the
# native selection after the command has already succeeded.
insert_before='''    function toolbarButton(label, title, handler) {
'''
selection_guard=r'''    document.addEventListener('selectionchange', function () {
        if (!active || !active.editor || active.formatting || !markerSelectionValid()) { return; }
        if (Date.now() > selectionHoldUntil) { return; }
        var selection = window.getSelection && window.getSelection();
        var valid = false;
        if (selection && selection.rangeCount && !selection.getRangeAt(0).collapsed) {
            var range = selection.getRangeAt(0);
            var common = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;
            valid = !!(common && active.editor.contains(common));
        }
        if (!valid) {
            window.setTimeout(function () {
                if (Date.now() <= selectionHoldUntil && markerSelectionValid()) { restoreMarkerSelection(); }
            }, 0);
        }
    });

'''
s=replace_once(s,insert_before,selection_guard+insert_before,'selectionchange guard')
s=replace_once(s,"""        selectionSessionMode: 'prearmed-v0138',
""","""        selectionSessionMode: 'prearmed-v0138',
        selectionRegressionGate: 'bug02-v0147-persistent',
""",'selection QA marker')

# Composite landing preview overlay in page Designer.
install_anchor='''    function install() {
'''
composite=r'''    function ensureCompositeOverlay() {
        var overlay = document.getElementById('h18-vd-composite-overlay');
        if (overlay) { return overlay; }
        overlay = document.createElement('div');
        overlay.id = 'h18-vd-composite-overlay';
        overlay.className = 'h18-vd-composite-overlay';
        overlay.hidden = true;
        overlay.innerHTML = '<div class="h18-vd-composite-dialog" role="dialog" aria-modal="true"><div class="h18-vd-composite-bar"><strong>Visual Designer · Header + landingsside + Footer</strong><button type="button" class="button" data-vd-composite-close>Luk</button></div><div class="h18-vd-composite-frame-wrap"><div class="h18-vd-composite-loading">Renderer samlet preview…</div><iframe class="h18-vd-composite-frame" title="Samlet Visual Designer preview"></iframe></div></div>';
        document.body.appendChild(overlay);
        overlay.addEventListener('click', function (event) {
            if (event.target === overlay || (event.target && event.target.closest && event.target.closest('[data-vd-composite-close]'))) {
                overlay.hidden = true;
                document.body.classList.remove('h18-vd-composite-open');
            }
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !overlay.hidden) {
                overlay.hidden = true;
                document.body.classList.remove('h18-vd-composite-open');
            }
        });
        return overlay;
    }

    function openCompositePreview() {
        var button = document.getElementById('h18-clean-composite-preview');
        var model = document.getElementById('h18-clean-model-json');
        if (!button || !model) { return; }
        sync();
        if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') { window.H18CleanV0120.sync(); }
        var overlay = ensureCompositeOverlay();
        var loading = overlay.querySelector('.h18-vd-composite-loading');
        var frame = overlay.querySelector('.h18-vd-composite-frame');
        overlay.hidden = false;
        document.body.classList.add('h18-vd-composite-open');
        if (loading) { loading.hidden = false; loading.textContent = 'Renderer samlet preview…'; }
        if (frame) { frame.hidden = true; frame.removeAttribute('src'); }

        var body = new URLSearchParams();
        body.set('action', 'h18_clean_composite_preview');
        body.set('_wpnonce', String(button.getAttribute('data-nonce') || ''));
        body.set('post_id', String(button.getAttribute('data-post-id') || '0'));
        body.set('model_json', model.value || '{}');
        var header = document.querySelector('select[name="header_template_choice"]');
        var footer = document.querySelector('select[name="footer_template_choice"]');
        body.set('header_template_choice', header ? String(header.value || 'auto') : 'auto');
        body.set('footer_template_choice', footer ? String(footer.value || 'auto') : 'auto');

        fetch(String(button.getAttribute('data-url') || ''), {
            method: 'POST', credentials: 'same-origin', cache: 'no-store',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            body: body.toString()
        }).then(function (response) {
            return response.text().then(function (html) { return { ok: response.ok, html: html }; });
        }).then(function (result) {
            if (!frame) { return; }
            frame.srcdoc = result.html;
            frame.hidden = false;
            if (loading) { loading.hidden = true; }
        }).catch(function (error) {
            if (loading) { loading.hidden = false; loading.textContent = 'Samlet preview fejlede: ' + String(error && error.message || error); }
        });
    }

'''
s=replace_once(s,install_anchor,composite+install_anchor,'composite preview functions')
s=replace_once(s,"""        initialShellChoices = currentShellChoices();
        enhance();
""","""        initialShellChoices = currentShellChoices();
        enhance();
        var compositeButton = document.getElementById('h18-clean-composite-preview');
        if (compositeButton) { compositeButton.addEventListener('click', openCompositePreview); }
""",'composite install')
write(path,s)

path='clean/hangar18-manager/assets/editor-v0125.css'
s=read(path)
s += '''\n\n/* 0.1.47 canonical Header + page + Footer composite preview */\nbody.h18-vd-composite-open{overflow:hidden!important}.h18-vd-composite-overlay[hidden]{display:none!important}.h18-vd-composite-overlay{position:fixed;inset:0;z-index:1000001;background:rgba(0,0,0,.68);display:flex;padding:18px;box-sizing:border-box}.h18-vd-composite-dialog{display:flex;flex-direction:column;width:100%;min-width:0;min-height:0;background:#f0f0f1;border-radius:8px;overflow:hidden;box-shadow:0 14px 52px rgba(0,0,0,.38)}.h18-vd-composite-bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 14px;background:#fff;border-bottom:1px solid #dcdcde}.h18-vd-composite-frame-wrap{position:relative;flex:1 1 auto;min-height:0;padding:12px;background:#dcdcde}.h18-vd-composite-frame{width:100%;height:100%;min-height:520px;border:0;background:#fff}.h18-vd-composite-loading{padding:30px;text-align:center;font-weight:600;color:#50575e}\n'''
write(path,s)

# ---------------------------------------------------------------------------
# Page Designer: no-op save gate + canonical composite preview endpoint.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/src/Admin/EditorController.php'
s=read(path)
s=replace_once(s,"""    private const PREVIEW_ACTION = 'h18_clean_preview';
""","""    private const PREVIEW_ACTION = 'h18_clean_preview';
    private const COMPOSITE_PREVIEW_ACTION = 'h18_clean_composite_preview';
""",'composite action constant')
s=replace_once(s,"""    private const NONCE_PREVIEW = 'h18_clean_preview';
""","""    private const NONCE_PREVIEW = 'h18_clean_preview';
    private const NONCE_COMPOSITE_PREVIEW = 'h18_clean_composite_preview';
""",'composite nonce constant')
s=replace_once(s,"""        add_action('admin_post_' . self::PREVIEW_ACTION, [self::class, 'preview']);
""","""        add_action('admin_post_' . self::PREVIEW_ACTION, [self::class, 'preview']);
        add_action('admin_post_' . self::COMPOSITE_PREVIEW_ACTION, [self::class, 'compositePreview']);
""",'composite action register')
s=replace_once(s,"""        echo '<button type=\"button\" class=\"button\" id=\"h18-clean-preview\" data-url=\"' . esc_attr(admin_url('admin-post.php')) . '\" data-nonce=\"' . esc_attr(wp_create_nonce(self::NONCE_PREVIEW)) . '\" data-post-id=\"' . esc_attr((string) $postId) . '\">Forhåndsvis</button>';
""","""        echo '<button type=\"button\" class=\"button\" id=\"h18-clean-preview\" data-url=\"' . esc_attr(admin_url('admin-post.php')) . '\" data-nonce=\"' . esc_attr(wp_create_nonce(self::NONCE_PREVIEW)) . '\" data-post-id=\"' . esc_attr((string) $postId) . '\">Forhåndsvis</button>';
        echo '<button type=\"button\" class=\"button\" id=\"h18-clean-composite-preview\" data-url=\"' . esc_attr(admin_url('admin-post.php')) . '\" data-nonce=\"' . esc_attr(wp_create_nonce(self::NONCE_COMPOSITE_PREVIEW)) . '\" data-post-id=\"' . esc_attr((string) $postId) . '\">Vis med Header + Footer</button>';
""",'composite toolbar button')
old_save=r'''            $note = isset($_POST['change_note']) ? sanitize_text_field((string) wp_unslash($_POST['change_note'])) : '';
            $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');
            TemplateLayoutModel::ensureMigrated();
            TemplateLayoutModel::setPageChoice($postId, 'header', sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto')));
            TemplateLayoutModel::setPageChoice($postId, 'footer', sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto')));
'''
new_save=r'''            $note = isset($_POST['change_note']) ? sanitize_text_field((string) wp_unslash($_POST['change_note'])) : '';
            TemplateLayoutModel::ensureMigrated();
            $headerChoice = sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto'));
            $footerChoice = sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto'));
            $currentVersion = max(0, (int) get_post_meta($postId, LayoutModel::VERSION_META, true));
            $sameModel = hash_equals(LayoutModel::structuralDigest(LayoutModel::get($postId)), LayoutModel::structuralDigest($normalized));
            $sameShell = TemplateLayoutModel::pageChoice($postId, 'header') === ($headerChoice !== '' ? $headerChoice : 'auto')
                && TemplateLayoutModel::pageChoice($postId, 'footer') === ($footerChoice !== '' ? $footerChoice : 'auto');
            if ($currentVersion > 0 && $sameModel && $sameShell) {
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-and-shell-unchanged']);
                self::redirect($postId, 'success', 'Ingen ændringer siden seneste gemte version. Der blev ikke oprettet en ny version.');
            }
            $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');
            TemplateLayoutModel::setPageChoice($postId, 'header', $headerChoice);
            TemplateLayoutModel::setPageChoice($postId, 'footer', $footerChoice);
'''
s=replace_once(s,old_save,new_save,'page no-op save')
preview_anchor='''    public static function preview(): void
    {
'''
composite_method=r'''    public static function compositePreview(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
        check_admin_referer(self::NONCE_COMPOSITE_PREVIEW);
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            wp_die(esc_html__('Ugyldig side.', 'hangar18-manager-clean'));
        }
        $decoded = json_decode(isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '', true);
        if (!is_array($decoded)) {
            wp_die(esc_html__('Preview-modellen er ikke gyldig JSON.', 'hangar18-manager-clean'));
        }
        try {
            $pageModel = LayoutModel::normalize($decoded);
            TemplateLayoutModel::ensureMigrated();
            $headerChoice = sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto'));
            $footerChoice = sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto'));
            $headerModel = self::templateModelForPreview('header', $headerChoice);
            $footerModel = self::templateModelForPreview('footer', $footerChoice);
            nocache_headers();
            header('Content-Type: text/html; charset=utf-8');
            echo Renderer::standaloneDocument($pageModel, $headerModel, $footerModel, 'Visual Designer · samlet preview');
            exit;
        } catch (\Throwable $error) {
            wp_die(esc_html('Samlet preview fejlede: ' . $error->getMessage()));
        }
    }

'''
s=replace_once(s,preview_anchor,composite_method+preview_anchor,'composite preview method')
redirect_anchor='''    private static function redirect(int $postId, string $status, string $message): void
    {
'''
helper=r'''    /** @return array<string,mixed>|null */
    private static function templateModelForPreview(string $part, string $choice): ?array
    {
        $part = sanitize_key($part) === 'footer' ? 'footer' : 'header';
        $choice = sanitize_key($choice);
        if ($choice === 'none') { return null; }
        $id = $choice !== '' && $choice !== 'auto' && TemplateLayoutModel::exists($choice, $part)
            ? $choice
            : TemplateLayoutModel::defaultId($part);
        if ($id === '' || !TemplateLayoutModel::exists($id, $part)) { return null; }
        return TemplateLayoutModel::model($id);
    }

'''
s=replace_once(s,redirect_anchor,helper+redirect_anchor,'preview template helper')
write(path,s)

# ---------------------------------------------------------------------------
# Global Header/Footer save: no new version when model/settings/active unchanged.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
s=read(path)
old_global=r'''            $normalized = LayoutModel::normalize($decoded);
            $settings = ['sticky' => !empty($_POST['global_sticky']), 'overlay' => !empty($_POST['global_overlay']), 'contentWidth' => absint($_POST['global_content_width'] ?? 1440)];
            $note = sanitize_text_field((string) wp_unslash($_POST['change_note'] ?? '')); if ($note === '') { $note = 'Opdateret ' . ($part === 'header' ? 'Header' : 'Footer') . '-template'; }
            TemplateLayoutModel::setActive($id, !empty($_POST['template_active']));
            $version = TemplateLayoutModel::saveVersion($id, $normalized, $settings, get_current_user_id(), $note);
'''
new_global=r'''            $normalized = LayoutModel::normalize($decoded);
            $settings = ['sticky' => !empty($_POST['global_sticky']), 'overlay' => !empty($_POST['global_overlay']), 'contentWidth' => absint($_POST['global_content_width'] ?? 1440)];
            $normalizedSettings = TemplateLayoutModel::normalizeSettings($part, $settings);
            $note = sanitize_text_field((string) wp_unslash($_POST['change_note'] ?? '')); if ($note === '') { $note = 'Opdateret ' . ($part === 'header' ? 'Header' : 'Footer') . '-template'; }
            $newActive = !empty($_POST['template_active']);
            $meta = TemplateLayoutModel::meta($id);
            $sameActive = is_array($meta) && (!empty($meta['active']) === $newActive);
            $sameState = hash_equals(
                TemplateLayoutModel::digest(TemplateLayoutModel::model($id), TemplateLayoutModel::settings($id)),
                TemplateLayoutModel::digest($normalized, $normalizedSettings)
            );
            if (TemplateLayoutModel::version($id) > 0 && $sameState && $sameActive) {
                self::redirect($part, $id, 'success', 'Ingen ændringer siden seneste gemte version. Der blev ikke oprettet en ny version.');
            }
            TemplateLayoutModel::setActive($id, $newActive);
            $version = TemplateLayoutModel::saveVersion($id, $normalized, $normalizedSettings, get_current_user_id(), $note);
'''
s=replace_once(s,old_global,new_global,'global no-op save')
write(path,s)

# ---------------------------------------------------------------------------
# Footer parity iteration + force one fresh migration on 0.1.47.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/src/Migration/LegacyFooterConverter.php'
s=read(path)
s=s.replace('h18_vd_legacy_footer_converted_v0146','h18_vd_legacy_footer_converted_v0147')
s=s.replace('h18_vd_legacy_footer_status_v0146','h18_vd_legacy_footer_status_v0147')
s=s.replace('Footer-reference fra godkendt Desktop-screenshot · v0.1.46','Footer-reference fra godkendt Desktop-screenshot · v0.1.47')
s=s.replace('-v0146', '-v0147')
s=replace_once(s,"'lineHeight'=>2.05", "'lineHeight'=>1.75", 'footer shortcut line height')
s=replace_once(s,"['background'=>'#596052','radius'=>0,'padding'=>0,'minHeightRows'=>1,'borderWidth'=>0,'borderColor'=>'#596052','gapX'=>0,'gapY'=>0]",
                  "['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>1,'borderWidth'=>1,'borderColor'=>'#596052','gapX'=>0,'gapY'=>0]",
                  'footer divider')
write(path,s)

# Global preview should Fit and hide editor-only leaf-card chrome.
path='clean/hangar18-manager/assets/global-designer-v0123.js'
s=read(path)
old=r'''        var overlay=ensurePreviewOverlay(); var host=overlay.querySelector('.h18-global-preview-host'); if(!host)return;
        host.innerHTML=''; host.style.width=virtualWidth+'px'; host.appendChild(copy); overlay.hidden=false; document.body.classList.add('h18-global-preview-open');
        var scroller=overlay.querySelector('.h18-global-preview-scroll'); if(scroller){scroller.scrollTop=0;scroller.scrollLeft=0;}
'''
new=r'''        var overlay=ensurePreviewOverlay(); var host=overlay.querySelector('.h18-global-preview-host'); if(!host)return;
        host.innerHTML=''; host.appendChild(copy); overlay.hidden=false; document.body.classList.add('h18-global-preview-open');
        var scroller=overlay.querySelector('.h18-global-preview-scroll');
        var fit=function(){
            if(!scroller||!copy||!host)return;
            var available=Math.max(160,scroller.clientWidth-48);
            var scale=Math.min(1,available/Math.max(1,virtualWidth));
            copy.style.transform='scale('+scale+')'; copy.style.transformOrigin='0 0';
            host.style.width=Math.ceil(virtualWidth*scale)+'px';
            host.style.height=Math.max(120,Math.ceil((copy.scrollHeight||copy.offsetHeight||120)*scale))+'px';
        };
        if(scroller){scroller.scrollTop=0;scroller.scrollLeft=0;}
        window.requestAnimationFrame(function(){fit();window.requestAnimationFrame(fit);});
'''
s=replace_once(s,old,new,'global preview fit')
write(path,s)

path='clean/hangar18-manager/assets/global-designer-v0123.css'
s=read(path)
s += '''\n/* 0.1.47 frontend-like local template preview */\n.h18-global-preview-host{margin:0 auto;transform-origin:0 0}.vd-global-preview-canvas .h18-clean-node:not([data-h18-parent-painted-box="1"]){background:transparent!important;border-color:transparent!important}.vd-global-preview-canvas .h18-clean-node-preview{min-height:0!important;padding:0!important;overflow:visible!important}.vd-global-preview-canvas .h18-clean-node-preview--text{overflow:visible!important}.vd-global-preview-canvas .h18-clean-text-body{overflow:visible!important}\n'''
write(path,s)

# ---------------------------------------------------------------------------
# Separate new Visual Designer landing page. Never changes page_on_front.
# ---------------------------------------------------------------------------
path='clean/hangar18-manager/src/Admin/AdminController.php'
s=read(path)
s=replace_once(s,'use Hangar18\\Clean\\Model\\LayoutModel;\n', 'use Hangar18\\Clean\\Model\\LayoutModel;\nuse Hangar18\\Clean\\Model\\TemplateLayoutModel;\n', 'TemplateLayoutModel import')
s=replace_once(s,"""    private const BLANK_SLUG_REPAIR_OPTION = 'h18_vd_blank_page_slugs_repaired_v0141';
""","""    private const BLANK_SLUG_REPAIR_OPTION = 'h18_vd_blank_page_slugs_repaired_v0141';
    private const LANDING_PAGE_OPTION = 'h18_vd_landing_page_v0147';
    private const LANDING_PAGE_META = '_h18_vd_landing_page_v0147';
""",'landing constants')
s=replace_once(s,"""        add_action('admin_init', [self::class, 'repairBlankPageSlugs'], 20);
""","""        add_action('admin_init', [self::class, 'repairBlankPageSlugs'], 20);
        add_action('admin_init', [self::class, 'ensureLandingPage'], 25);
""",'landing init')
# Landing card on Pages screen.
needle="""        if ($message !== '') { echo '<div class=\"notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible\"><p>' . esc_html($message) . '</p></div>'; }
"""
replacement=needle+"""        $landingId = absint(get_option(self::LANDING_PAGE_OPTION, 0));
        if ($landingId > 0 && get_post_type($landingId) === 'page') {
            echo '<div class=\"h18-manager-card\"><h2>Ny Visual Designer-landingsside</h2><p>Separat kladde til Header + indhold + Footer. Den gamle Hjem-side og WordPress-forsiden er ikke ændret.</p><p><a class=\"button button-primary\" href=\"' . esc_url(self::designerUrl($landingId)) . '\">Åbn Hjem – Visual Designer</a> <a class=\"button\" href=\"' . esc_url(self::url('h18-clean-menu')) . '\">Menu · næste arbejdsspor</a></p></div>';
        }
"""
s=replace_once(s,needle,replacement,'landing pages card')
create_anchor='''    public static function repairBlankPageSlugs(): void
    {
'''
landing_method=r'''    public static function ensureLandingPage(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        $stored = absint(get_option(self::LANDING_PAGE_OPTION, 0));
        if ($stored > 0 && get_post_type($stored) === 'page') { return; }

        $existing = get_posts([
            'post_type' => 'page', 'post_status' => ['publish','draft','pending','private','future'],
            'meta_key' => self::LANDING_PAGE_META, 'meta_value' => '1', 'fields' => 'ids',
            'posts_per_page' => 1, 'no_found_rows' => true, 'suppress_filters' => true,
        ]);
        if (is_array($existing) && !empty($existing)) {
            update_option(self::LANDING_PAGE_OPTION, (int) $existing[0], false);
            return;
        }

        $postId = wp_insert_post([
            'post_type' => 'page',
            'post_title' => 'Hjem – Visual Designer',
            'post_name' => self::uniquePageSlug('hjem-visual-designer'),
            'post_status' => 'draft',
            'post_content' => '',
            'post_author' => get_current_user_id(),
        ], true);
        if (is_wp_error($postId) || (int) $postId <= 0) { return; }
        $postId = (int) $postId;
        update_post_meta($postId, self::LANDING_PAGE_META, '1');
        LayoutModel::saveVersion($postId, self::landingPageModel(), get_current_user_id(), 'Oprettet ny Visual Designer-landingsside · gammel Hjem-side urørt');
        TemplateLayoutModel::ensureMigrated();
        TemplateLayoutModel::setPageChoice($postId, 'header', 'auto');
        TemplateLayoutModel::setPageChoice($postId, 'footer', 'auto');
        update_option(self::LANDING_PAGE_OPTION, $postId, false);
    }

    /** @return array<string,mixed> */
    private static function landingPageModel(): array
    {
        $g = static function (int $x,int $y,int $w,int $h): array {
            return [
                'desktop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],
                'laptop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
                'tablet'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
                'mobile'=>['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false],
            ];
        };
        return LayoutModel::normalize(['nodes'=>[
            ['id'=>'section-landing-v0147','type'=>'section','parentId'=>'','order'=>10,'geometry'=>$g(6,0,108,42),'props'=>['background'=>'#ffffff','padding'=>0,'minHeightRows'=>42,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]],
            ['id'=>'container-landing-v0147','type'=>'container','parentId'=>'section-landing-v0147','order'=>10,'geometry'=>$g(0,0,120,42),'props'=>['background'=>'#ffffff','padding'=>0,'minHeightRows'=>42,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]],
            ['id'=>'text-landing-v0147','type'=>'text','parentId'=>'container-landing-v0147','order'=>10,'geometry'=>$g(6,10,108,14),'props'=>['heading'=>'Ny Visual Designer-landingsside','headingLevel'=>'h2','text'=>'Denne kladde er oprettet som et rent udgangspunkt. Header og Footer vises i Samlet preview. Den gamle Hjem-side konverteres først senere.','align'=>'center','verticalAlign'=>'center','background'=>'#ffffff','backgroundTransparent'=>true,'textColor'=>'#30382a','headingColor'=>'#30382a','fontFamily'=>'system','fontSize'=>18,'fontWeight'=>400,'lineHeight'=>1.5,'letterSpacing'=>0,'headingFontFamily'=>'body','headingFontSize'=>36,'headingFontWeight'=>700,'headingLineHeight'=>1.2,'headingLetterSpacing'=>0,'padding'=>16,'radius'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]],
        ]]);
    }

'''
s=replace_once(s,create_anchor,landing_method+create_anchor,'landing seed methods')
# Make Menu card explicit as the next UX workstream, without changing menu data.
s=replace_once(s,"self::card('Menu', 'Se WordPress-navigation og aktive menulocations uden at ændre Visual Designer-layoutdata.', self::url('h18-clean-menu'), 'Vis menu');",
                  "self::card('Menu · næste arbejdsspor', 'Menu-redesignet er næste UX-opgave. Eksisterende WordPress-menuer forbliver datakilden, mens vi gør valg, struktur og mobiladfærd mere brugervenlig.', self::url('h18-clean-menu'), 'Forbered Menu');",
                  'menu next track card')
write(path,s)

# ---------------------------------------------------------------------------
# Permanent model/release gates for 0.1.47.
# ---------------------------------------------------------------------------
path='.github/scripts/v0125_model_qa.php'
s=read(path)
old='echo "Visual Designer Manager 0.1.46 model QA PASS\\n";'
new=r'''/* 0.1.47 stabilization gates */
$richJs=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/editor-v0125.js');
$editorCss=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/editor.css');
$globalController=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/src/Admin/GlobalDesignerController.php');
$pageController=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/src/Admin/EditorController.php');
$adminController=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/src/Admin/AdminController.php');
$globalPreviewCss=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/global-designer-v0123.css');
vdAssert(str_contains((string)$richJs,"selectionOwner: 'v0125-authoritative'") && str_contains((string)$richJs,"selectionSessionMode: 'prearmed-v0138'") && str_contains((string)$richJs,"selectionRegressionGate: 'bug02-v0147-persistent'"),'BUG-02 permanent selection gate is missing.');
vdAssert(str_contains((string)$richJs,'window.setTimeout(restore, 320)') && str_contains((string)$richJs,"addEventListener('selectionchange'"),'BUG-02 restore burst/selection guard regressed.');
$renderer147=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/src/Frontend/Renderer.php');
vdAssert(str_contains((string)$renderer147,'h18-clean-front-text-content'),'BUG-17 rich-text content wrapper is missing.');
vdAssert(str_contains((string)$editorCss,'.h18-clean-root{background:#fff;min-height:650px;padding:0;border:0}'),'BUG-18 root padding/border still alters X/Y=0.');
vdAssert(str_contains((string)$pageController,'canonical-model-and-shell-unchanged') && str_contains((string)$globalController,'Ingen ændringer siden seneste gemte version'),'No-op version gate is missing.');
vdAssert(str_contains((string)$pageController,'h18_clean_composite_preview') && str_contains((string)$renderer147,'standaloneDocument'),'Composite Header/page/Footer preview contract is missing.');
vdAssert(str_contains((string)$adminController,"Hjem – Visual Designer") && str_contains((string)$adminController,"LANDING_PAGE_OPTION"),'Separate landing page seed is missing.');
vdAssert(str_contains((string)$globalPreviewCss,'h18-clean-node-preview--text{overflow:visible!important}'),'Footer local-preview leaf chrome reset is missing.');
vdAssert(str_contains((string)$footerPhp,'h18_vd_legacy_footer_converted_v0147') && str_contains((string)$footerPhp,"'lineHeight'=>1.75"),'Footer 0.1.47 parity migration did not advance.');

echo "Visual Designer Manager 0.1.47 model QA PASS\n";'''
s=replace_once(s,old,new,'0.1.47 QA append')
write(path,s)

# Release metadata ------------------------------------------------------------
path='clean/hangar18-manager/release-history.json'
history=json.loads(read(path))
if not any(str(x.get('version'))=='0.1.47' for x in history if isinstance(x,dict)):
    history.insert(0,{
        'version':'0.1.47','date':'2026-08-29','items':[
            'BUG-02: rich-text selection er igen release-gated; Fed/Kursiv/Understregning får længere restore-burst og kort selectionchange-beskyttelse.',
            'BUG-17: frontend Tekst bruger én content-wrapper, så EM/STRONG/U ikke bliver separate flex-items ved lodret justering.',
            'BUG-18: virtuel side har ingen intern root-padding/border; X=0/Y=0/W=120 rammer de faktiske sidekanter.',
            'Footer parity: Genveje-spacing reduceret, divider er baggrundsneutral med tynd ramme, og lokal Header/Footer preview Fit-skalerer hele den virtuelle bredde.',
            'Versionshistorik: Side/Header/Footer opretter ikke en ny version, når canonical model og relevante valg/settings er uændrede.',
            'Ny separat kladde Hjem – Visual Designer oprettes én gang med Auto Header/Footer; eksisterende Hjem og page_on_front ændres ikke.',
            'Ny samlet canonical preview viser Header + aktuel side + Footer inde i Designer mens Theme Shell er OFF.',
            'Menu markeres som næste UX-arbejdsspor; eksisterende WordPress-menuer ændres ikke i denne release.'
        ]
    })
write(path,json.dumps(history,ensure_ascii=False,indent=2)+'\n')

write('docs/v0147-status.md','''# Visual Designer Manager 0.1.47 – status\n\nDato: 2026-08-29\n\n## Implementeret\n- BUG-02 regression-gate: v0125 er eneste selection-owner; prearmed v0138 bevares og restore-burst er styrket.\n- BUG-17: rich-text frontend wrapper beskytter inline EM/STRONG/U mod flex-split.\n- BUG-18: root virtual page har 0 intern padding/border; editor-chrome ligger udenfor siden.\n- Footer parity iteration og Fit i lokal Header/Footer preview.\n- No-op Save på Side/Header/Footer.\n- Separat Hjem – Visual Designer-kladdeside, uden ændring af gammel Hjem eller WordPress page_on_front.\n- Samlet canonical Header + Side + Footer preview mens Theme Shell er OFF.\n- Menu er næste UX-arbejdsspor; ingen menu-data ændres i 0.1.47.\n\n## QA\nPHP/JS syntax, hierarchy/model QA og 0.1.47 kontrakt-gates skal være grønne før release. Bruger-QA af selection, Footer parity og samlet landingsside-preview følger efter installation.\n''')
write('clean-release-notes.html','''<h4>0.1.47</h4><ul><li><strong>Rich text:</strong> BUG-02 selection-regression er permanent release-gated, og frontend inline-formatering splittes ikke længere af vertical-align.</li><li><strong>WYSIWYG:</strong> X=0/Y=0/W=120 rammer den faktiske virtuelle sidekant.</li><li><strong>Footer:</strong> næste parity-runde samt Fit i lokal template-preview.</li><li><strong>Versioner:</strong> ingen ny Side/Header/Footer-version uden reel canonical ændring.</li><li><strong>Landingsside:</strong> separat Hjem – Visual Designer-kladdeside med Auto Header/Footer og samlet canonical preview.</li><li><strong>Menu:</strong> næste UX-arbejdsspor er gjort tydeligt; menu-data ændres ikke endnu.</li><li><strong>Theme Shell:</strong> fortsat OFF.</li></ul>''')

# Technical manual additive record.
path='CLEAN-TECHNICAL-MANUAL.md'
s=read(path)
section='''\n\n## 0.1.47 – stabilisering før Menu-UX\n\n- **VD-TEXT-SEL-001:** BUG-02 er permanent release-gate. `v0125-authoritative` + `prearmed-v0138` må ikke fjernes; første og kædede Fed/Kursiv/Understregning skal bevare native selection.\n- **VD-TEXT-FLEX-001:** lodret Tekst-justering arbejder på én samlet content-wrapper. Inline `EM`, `STRONG`, `U` og `A` må aldrig blive selvstændige flex-items.\n- **VD-VIEWPORT-EDGE-001:** X=0/Y=0/W=120 refererer til den faktiske virtuelle side. Editor-padding/border er chrome uden for canonical sidegeometri.\n- **VD-SAVE-NOOP-001:** brugerens Gem må ikke oprette ny Side/Header/Footer-version, hvis canonical model og relevante settings/valg er identiske med seneste gemte state. En ændringsnote alene er ikke en ændring. Restore/konvertering kan fortsat være eksplicit non-destruktive versionshandlinger.\n- **VD-LANDING-PREVIEW-001:** en separat Visual Designer Hjem-kladdeside kan bruges til Header + Side + Footer parity uden at ændre gammel Hjem eller `page_on_front`. Samlet preview bruger canonical modeller og Theme Shell forbliver OFF.\n- **VD-MENU-UX-NEXT:** næste hovedarbejdsspor er en mere brugervenlig Menu-oplevelse; WordPress-menu-ID forbliver canonical datakilde.\n'''
if '## 0.1.47 – stabilisering før Menu-UX' not in s:
    s += section
write(path,s)

print('0.1.47 stabilization + landing patch applied')
