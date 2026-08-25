from pathlib import Path

root = Path('.')

# EditorController: unsaved preview, save verification, Save & View.
p = root / 'clean/hangar18-manager/src/Admin/EditorController.php'
s = p.read_text(encoding='utf-8')
s = s.replace("use Hangar18\\Clean\\Diagnostics\\DiagnosticStore;\nuse Hangar18\\Clean\\Model\\LayoutModel;", "use Hangar18\\Clean\\Diagnostics\\DiagnosticStore;\nuse Hangar18\\Clean\\Frontend\\Renderer;\nuse Hangar18\\Clean\\Model\\LayoutModel;")
s = s.replace("    private const RESTORE_ACTION = 'h18_clean_restore';\n    private const NONCE_SAVE = 'h18_clean_save';\n    private const NONCE_RESTORE = 'h18_clean_restore';", "    private const RESTORE_ACTION = 'h18_clean_restore';\n    private const PREVIEW_ACTION = 'h18_clean_preview';\n    private const NONCE_SAVE = 'h18_clean_save';\n    private const NONCE_RESTORE = 'h18_clean_restore';\n    private const NONCE_PREVIEW = 'h18_clean_preview';")
s = s.replace("        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);\n        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);", "        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);\n        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);\n        add_action('admin_post_' . self::PREVIEW_ACTION, [self::class, 'preview']);")
old_toolbar = "        echo '<span class=\"h18-clean-grid-label\">120 units · 8 px lodret snap</span>';\n        echo '<button type=\"submit\" class=\"button button-primary h18-clean-save\">Gem som ny version</button>';"
new_toolbar = "        echo '<span class=\"h18-clean-grid-label\">120 units · 8 px lodret snap</span>';\n        echo '<button type=\"button\" class=\"button\" id=\"h18-clean-preview\" data-url=\"' . esc_attr(admin_url('admin-post.php')) . '\" data-nonce=\"' . esc_attr(wp_create_nonce(self::NONCE_PREVIEW)) . '\" data-post-id=\"' . esc_attr((string) $postId) . '\">Forhåndsvis</button>';\n        echo '<button type=\"submit\" class=\"button\" name=\"after_save\" value=\"preview\" formtarget=\"_blank\">Gem &amp; vis</button>';\n        echo '<button type=\"submit\" class=\"button button-primary h18-clean-save\">Gem som ny version</button>';"
if old_toolbar not in s:
    raise SystemExit('Editor toolbar anchor missing')
s = s.replace(old_toolbar, new_toolbar)
old_save = "            $saved = LayoutModel::get($postId);\n            DiagnosticStore::append($postId, 'save_result', [\n                'version' => $version,\n                'saved' => DiagnosticStore::modelSummary($saved),\n            ]);\n            self::redirect($postId, 'success', 'Clean layout gemt som version v' . $version . '.');"
new_save = "            $saved = LayoutModel::get($postId);\n            $incomingDigest = LayoutModel::structuralDigest($normalized);\n            $savedDigest = LayoutModel::structuralDigest($saved);\n            if (!hash_equals($incomingDigest, $savedDigest)) {\n                throw new \\RuntimeException('Save-verifikation fejlede: den gemte canonical model matcher ikke den indsendte model.');\n            }\n            DiagnosticStore::append($postId, 'save_result', [\n                'version' => $version,\n                'digest' => $savedDigest,\n                'saved' => DiagnosticStore::modelSummary($saved),\n            ]);\n            if (isset($_POST['after_save']) && sanitize_key((string) wp_unslash($_POST['after_save'])) === 'preview') {\n                $permalink = get_permalink($postId);\n                if (is_string($permalink) && $permalink !== '') {\n                    wp_safe_redirect($permalink);\n                    exit;\n                }\n            }\n            self::redirect($postId, 'success', 'Clean layout gemt og verificeret som version v' . $version . '.');"
if old_save not in s:
    raise SystemExit('Save anchor missing')
s = s.replace(old_save, new_save)
restore_anchor = "    public static function restore(): void\n    {"
preview_method = "    public static function preview(): void\n    {\n        if (!current_user_can('edit_pages')) {\n            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));\n        }\n        check_admin_referer(self::NONCE_PREVIEW);\n        $postId = absint($_POST['post_id'] ?? 0);\n        if ($postId <= 0 || get_post_type($postId) !== 'page') {\n            wp_die(esc_html__('Ugyldig side.', 'hangar18-manager-clean'));\n        }\n        $rawJson = isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '';\n        if ($rawJson === '' || strlen($rawJson) > 2 * 1024 * 1024) {\n            wp_die(esc_html__('Preview-modellen mangler eller er for stor.', 'hangar18-manager-clean'));\n        }\n        $decoded = json_decode($rawJson, true);\n        if (!is_array($decoded)) {\n            wp_die(esc_html__('Preview-modellen er ikke gyldig JSON.', 'hangar18-manager-clean'));\n        }\n        try {\n            $normalized = LayoutModel::normalize($decoded);\n            $token = strtolower(wp_generate_password(24, false, false));\n            set_transient(Renderer::previewKey(get_current_user_id(), $postId, $token), $normalized, 10 * MINUTE_IN_SECONDS);\n            DiagnosticStore::append($postId, 'preview_open', [\n                'digest' => LayoutModel::structuralDigest($normalized),\n                'state' => DiagnosticStore::modelSummary($normalized),\n            ]);\n            $permalink = get_permalink($postId);\n            if (!is_string($permalink) || $permalink === '') {\n                throw new \\RuntimeException('Siden har ingen gyldig permalink.');\n            }\n            wp_safe_redirect(add_query_arg('h18_clean_preview', rawurlencode($token), $permalink));\n            exit;\n        } catch (\\Throwable $error) {\n            DiagnosticStore::append($postId, 'preview_error', ['errorType' => get_class($error), 'message' => $error->getMessage()]);\n            wp_die(esc_html('Forhåndsvisning fejlede: ' . $error->getMessage()));\n        }\n    }\n\n"
if restore_anchor not in s:
    raise SystemExit('Restore anchor missing')
s = s.replace(restore_anchor, preview_method + restore_anchor)
p.write_text(s, encoding='utf-8')

# Renderer: current-user temporary preview through real theme/front end.
p = root / 'clean/hangar18-manager/src/Frontend/Renderer.php'
s = p.read_text(encoding='utf-8')
s = s.replace("        add_action('wp_head', [self::class, 'css'], 1000);", "        add_action('wp_head', [self::class, 'css'], 1000);\n        add_action('wp_footer', [self::class, 'previewBadge'], 1000);")
old_content = "        $postId = get_the_ID();\n        if ($postId <= 0 || !metadata_exists('post', $postId, LayoutModel::META)) {\n            return $content;\n        }\n        $model = LayoutModel::get($postId);"
new_content = "        $postId = get_the_ID();\n        if ($postId <= 0) {\n            return $content;\n        }\n        $preview = self::previewModel($postId);\n        if ($preview !== null) {\n            return self::renderModel($preview);\n        }\n        if (!metadata_exists('post', $postId, LayoutModel::META)) {\n            return $content;\n        }\n        $model = LayoutModel::get($postId);"
if old_content not in s:
    raise SystemExit('Renderer content anchor missing')
s = s.replace(old_content, new_content)
old_css_guard = "        $postId = get_queried_object_id();\n        if ($postId <= 0 || !metadata_exists('post', $postId, LayoutModel::META)) {\n            return;\n        }"
new_css_guard = "        $postId = get_queried_object_id();\n        if ($postId <= 0 || (!metadata_exists('post', $postId, LayoutModel::META) && self::previewModel($postId) === null)) {\n            return;\n        }"
if old_css_guard not in s:
    raise SystemExit('Renderer CSS guard missing')
s = s.replace(old_css_guard, new_css_guard)
insert_before_render = "    /** @param array<string,mixed> $model */\n    private static function renderModel(array $model): string"
preview_helpers = "    public static function previewKey(int $userId, int $postId, string $token): string\n    {\n        return 'h18_clean_preview_' . max(0, $userId) . '_' . max(0, $postId) . '_' . sanitize_key($token);\n    }\n\n    public static function previewBadge(): void\n    {\n        if (!is_singular('page')) {\n            return;\n        }\n        $postId = get_queried_object_id();\n        if ($postId <= 0 || self::previewModel($postId) === null) {\n            return;\n        }\n        echo '<div style=\"position:fixed;right:16px;bottom:16px;z-index:2147483647;padding:8px 12px;border:1px solid #2271b1;border-radius:6px;background:#fff;color:#1d2327;box-shadow:0 4px 18px rgba(0,0,0,.2);font:600 13px/1.3 system-ui,sans-serif;pointer-events:none\">Forhåndsvisning · ikke gemt</div>';\n    }\n\n    /** @return array<string,mixed>|null */\n    private static function previewModel(int $postId): ?array\n    {\n        if (!is_user_logged_in() || !current_user_can('edit_pages')) {\n            return null;\n        }\n        $token = isset($_GET['h18_clean_preview']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_preview'])) : '';\n        if ($token === '' || !preg_match('/^[a-z0-9]{12,64}$/', $token)) {\n            return null;\n        }\n        $raw = get_transient(self::previewKey(get_current_user_id(), $postId, $token));\n        if (!is_array($raw)) {\n            return null;\n        }\n        try {\n            return LayoutModel::normalize($raw);\n        } catch (\\Throwable $error) {\n            return null;\n        }\n    }\n\n    /** @param array<string,mixed> $model */\n    private static function renderModel(array $model): string"
if insert_before_render not in s:
    raise SystemExit('Renderer renderModel anchor missing')
s = s.replace(insert_before_render, preview_helpers)
p.write_text(s, encoding='utf-8')

# Layout digest now represents the full canonical normalized model, including text, gaps and style props.
p = root / 'clean/hangar18-manager/src/Model/LayoutModel.php'
s = p.read_text(encoding='utf-8')
start = s.index('    public static function structuralDigest(array $model): string\n    {')
end = s.index('\n    /** @param array<string,array<string,mixed>> $nodes */', start)
replacement = "    public static function structuralDigest(array $model): string\n    {\n        $normalized = self::normalize($model);\n        $json = wp_json_encode($normalized, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);\n        if (!is_string($json)) {\n            throw new \\RuntimeException('Canonical layout kunne ikke serialiseres til digest.');\n        }\n        return hash('sha256', $json);\n    }\n"
s = s[:start] + replacement + s[end:]
p.write_text(s, encoding='utf-8')

# Main plugin version + assets.
p = root / 'clean/hangar18-manager/hangar18-manager.php'
s = p.read_text(encoding='utf-8')
s = s.replace('Version: 0.1.13', 'Version: 0.1.14').replace("H18_CLEAN_VERSION', '0.1.13'", "H18_CLEAN_VERSION', '0.1.14'")
s = s.replace("     * 0.1.12 separates selection from overlap diagnostics, localises editor\n     * labels and keeps editor chrome outside canonical element geometry.", "     * 0.1.14 adds theme-accurate unsaved preview, verified Save and collision-free\n     * contextual labels while preserving canonical element geometry.")
anchor = "    wp_enqueue_style(\n        'h18-clean-editor-v0112',\n        H18_CLEAN_URL . 'assets/editor-v0112.css',\n        ['h18-clean-editor-v0110'],\n        H18_CLEAN_VERSION\n    );\n"
addition = anchor + "    wp_enqueue_style(\n        'h18-clean-editor-v0114',\n        H18_CLEAN_URL . 'assets/editor-v0114.css',\n        ['h18-clean-editor-v0112'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0114',\n        H18_CLEAN_URL . 'assets/editor-v0114.js',\n        ['h18-clean-editor-v018-core'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"
if anchor not in s:
    raise SystemExit('Main asset anchor missing')
s = s.replace(anchor, addition)
p.write_text(s, encoding='utf-8')

# New contextual label CSS: only active/direct-hover label is shown; ancestor labels yield to descendants.
(root / 'clean/hangar18-manager/assets/editor-v0114.css').write_text("""/* Clean 0.1.14: contextual editor labels avoid parent/child label collisions. */
.h18-clean-node>.h18-clean-node-header{display:none!important;z-index:85!important}
.h18-clean-node.is-selected>.h18-clean-node-header,
.h18-clean-node.is-dragging>.h18-clean-node-header,
.h18-clean-node:hover>.h18-clean-node-header{display:flex!important}
.h18-clean-node:hover:has(.h18-clean-node:hover)>.h18-clean-node-header,
.h18-clean-node.is-selected:has(.h18-clean-node:hover)>.h18-clean-node-header{display:none!important}
""", encoding='utf-8')

# Preview button posts the current unsaved canonical JSON to a short-lived front-end preview in a new tab.
(root / 'clean/hangar18-manager/assets/editor-v0114.js').write_text("""(function () {
    'use strict';
    function hidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden'; input.name = name; input.value = value;
        form.appendChild(input);
    }
    document.addEventListener('DOMContentLoaded', function () {
        var button = document.getElementById('h18-clean-preview');
        var model = document.getElementById('h18-clean-model-json');
        if (!button || !model) { return; }
        button.addEventListener('click', function () {
            var form = document.createElement('form');
            form.method = 'post';
            form.action = button.getAttribute('data-url') || '';
            form.target = '_blank';
            form.style.display = 'none';
            hidden(form, 'action', 'h18_clean_preview');
            hidden(form, '_wpnonce', button.getAttribute('data-nonce') || '');
            hidden(form, 'post_id', button.getAttribute('data-post-id') || '0');
            hidden(form, 'model_json', model.value || '{}');
            document.body.appendChild(form);
            form.submit();
            window.setTimeout(function () { form.remove(); }, 1000);
        });
    });
})();
""", encoding='utf-8')

# Readme and release notes.
p = root / 'clean/hangar18-manager/readme.txt'
s = p.read_text(encoding='utf-8')
s = s.replace('Version: 0.1.13', 'Version: 0.1.14')
marker = '== 0.1.13 ==\n'
notes = "== 0.1.14 ==\n* Kasse-/barn-labels kolliderer ikke længere: labels er kontekstuelle og ancestor-label skjules, når et barn er det direkte hover/valgte element.\n* Forhåndsvis åbner den aktuelle ikke-gemte canonical model i den rigtige frontend/theme via et 10-minutters brugerspecifikt preview-token.\n* Gem & vis gemmer en ny version og åbner den offentlige side i en ny fane.\n* Save læser canonical model tilbage og verificerer fuld digest før success.\n* Structural digest dækker nu hele den normaliserede model inkl. tekst, gaps og style props.\n\n"
if marker not in s:
    raise SystemExit('Readme marker missing')
s = s.replace(marker, notes + marker)
p.write_text(s, encoding='utf-8')

(root / 'clean-release-notes.html').write_text("<h4>0.1.14</h4><ul><li>Kontekstuelle labels fjerner Kasse/barn-label-kollision uden at ændre fysisk geometri.</li><li>Forhåndsvis viser den aktuelle usavede model i den rigtige frontend/theme via et kortlivet brugerspecifikt token.</li><li>Gem &amp; vis gemmer en ny version og åbner den offentlige side i en ny fane.</li><li>Save verificerer den fulde canonical digest efter reload, og digest inkluderer nu alle normaliserede props.</li></ul>\n", encoding='utf-8')
