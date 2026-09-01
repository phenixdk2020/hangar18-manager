from __future__ import annotations

from pathlib import Path
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
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    if new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one anchor, found {count}: {old[:140]!r}')
    write(rel, value.replace(old, new, 1))


EDITOR = 'clean/hangar18-manager/src/Admin/EditorController.php'
COLLECTION = 'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php'
ADMIN_CSS = 'clean/hangar18-manager/assets/admin-v0175.css'
BACKLOG = 'docs/clean-backlog-v0100.md'
STATUS = 'docs/vd-module-visual-parity-002-status.md'
PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
MANIFEST = 'clean-update.json'

# This task is deliberately post-v0.1.75 source work. It must not bump or publish a version.
plugin = read(PLUGIN)
manifest = read(MANIFEST)
if 'Version: 0.1.75' not in plugin or "H18_CLEAN_VERSION', '0.1.75'" not in plugin:
    raise SystemExit('Expected current plugin runtime to remain v0.1.75')
if '"version": "0.1.75"' not in manifest:
    raise SystemExit('Expected release manifest to remain v0.1.75')

# Collection pages get one canonical Designer preview: the actual frontend renderer in a same-origin iframe.
replace_once(
    EDITOR,
    'use VisualDesignerManager\\Frontend\\Renderer;',
    'use VisualDesignerManager\\Frontend\\CollectionPageRenderer;\nuse VisualDesignerManager\\Frontend\\Renderer;',
)
replace_once(
    EDITOR,
    "        add_action('admin_post_' . self::VERSION_PREVIEW_ACTION, [self::class, 'previewVersion']);",
    "        add_action('admin_post_' . self::VERSION_PREVIEW_ACTION, [self::class, 'previewVersion']);\n        add_filter('show_admin_bar', [self::class, 'hideModulePreviewAdminBar']);",
)
replace_once(
    EDITOR,
    '        TemplateLayoutModel::ensureMigrated();\n        $model = LayoutModel::get($postId);',
    '        TemplateLayoutModel::ensureMigrated();\n        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $model = LayoutModel::get($postId);',
)

editor = read(EDITOR)
if 'h18-vd-module-canonical-preview' not in editor:
    workspace_anchor = "        echo '<div class=\"h18-clean-workspace\">';\n"
    pos = editor.find(workspace_anchor)
    if pos < 0:
        raise SystemExit('Editor workspace anchor missing')
    opening = r'''        if ($isCollectionPage) {
            $moduleSlug = sanitize_title((string) get_post_field('post_name', $postId));
            $moduleAdminPage = $moduleSlug === 'events'
                ? 'h18-clean-events'
                : ($moduleSlug === 'billedgalleri' ? 'h18-clean-gallery' : 'h18-clean-vehicles');
            $moduleLabel = $moduleSlug === 'events'
                ? 'Events'
                : ($moduleSlug === 'billedgalleri' ? 'Billedgalleri' : 'Køretøjer');
            $previewUrl = add_query_arg([
                'h18_vd_module_preview' => '1',
                'h18_vd_module_preview_version' => H18_CLEAN_VERSION,
            ], get_permalink($postId));
            echo '<section class="h18-vd-module-canonical-preview">';
            echo '<div class="h18-vd-module-canonical-preview-head"><div><strong>Canonical modul-preview · ' . esc_html($moduleLabel) . '</strong><p>Dette er den samme frontend-rendering som den offentlige side. Moduldata redigeres i Manageren, så Designer og frontend ikke kan drive visuelt fra hinanden.</p></div><div class="h18-vd-module-canonical-preview-actions"><a class="button button-primary" href="' . esc_url(admin_url('admin.php?page=' . $moduleAdminPage)) . '">Redigér ' . esc_html($moduleLabel) . '</a><a class="button" target="_blank" rel="noopener" href="' . esc_url(get_permalink($postId)) . '">Åbn offentlig side</a></div></div>';
            echo '<iframe class="h18-vd-module-canonical-frame" title="Canonical frontend-preview" src="' . esc_url($previewUrl) . '" loading="eager"></iframe>';
            echo '</section>';
        } else {
'''
    editor = editor[:pos] + opening + editor[pos:]
    close_anchor = "        echo '<aside class=\"h18-clean-inspector\"><h2>Inspector</h2><div id=\"h18-clean-inspector\"><p class=\"description\">Vælg et element på canvas.</p></div></aside>';\n        echo '</div>';\n        echo '</form>';"
    close_replacement = "        echo '<aside class=\"h18-clean-inspector\"><h2>Inspector</h2><div id=\"h18-clean-inspector\"><p class=\"description\">Vælg et element på canvas.</p></div></aside>';\n        echo '</div>';\n        }\n        echo '</form>';"
    if close_anchor not in editor:
        raise SystemExit('Editor workspace close anchor missing')
    editor = editor.replace(close_anchor, close_replacement, 1)
    write(EDITOR, editor)

editor = read(EDITOR)
if 'public static function hideModulePreviewAdminBar' not in editor:
    class_end = editor.rfind('\n}')
    if class_end < 0:
        raise SystemExit('Editor class end missing')
    method = r'''

    public static function hideModulePreviewAdminBar(bool $show): bool
    {
        if (isset($_GET['h18_vd_module_preview']) && current_user_can('edit_pages')) {
            return false;
        }
        return $show;
    }
'''
    editor = editor[:class_end] + method + editor[class_end:]
    write(EDITOR, editor)

# Parity styling: the old pages used a 90% white page frame, full-width images and beige card bodies.
collection = read(COLLECTION)
style_pattern = re.compile(r"    private static function style\(\): string\n    \{.*?\n    \}\n\n    private function __construct", re.S)
style_replacement = r'''    private static function style(): string
    {
        return '<style id="h18-module-page-style-parity-002">'
            . '.h18-module-page{width:90%;max-width:none;margin:0 auto;padding:36px 0 58px;color:#30382a;box-sizing:border-box}.h18-module-page h1{margin:0 0 30px;font-size:clamp(30px,3vw,44px);line-height:1.08}.h18-module-section{margin:0 0 44px}.h18-module-section h2{margin:0 0 18px;font-size:clamp(23px,2vw,31px);line-height:1.15}'
            . '.h18-module-intro{margin:-6px 0 22px;max-width:900px}.h18-module-card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;align-items:start}.h18-module-card{background:transparent;border:0;border-radius:6px;overflow:hidden;box-shadow:none;min-width:0}.h18-module-card-image{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}.h18-module-card-body{background:#eee8dc;padding:18px 20px 20px;min-height:100%;box-sizing:border-box}.h18-module-card h3{font-size:21px;line-height:1.18;margin:0 0 10px}.h18-module-card h3 a{color:inherit;text-decoration:none}.h18-module-card p{margin:8px 0}.h18-module-meta{font-size:14px;line-height:1.45}.h18-module-more{font-weight:700;color:#536243;text-decoration:none}.h18-module-more:hover,.h18-module-more:focus-visible{text-decoration:underline}.h18-module-card-actions{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:14px}.h18-module-description>*:first-child{margin-top:0}.h18-module-description>*:last-child{margin-bottom:0}'
            . '.h18-module-spec-table{width:100%;border-collapse:collapse;margin:14px 0}.h18-module-spec-table th,.h18-module-spec-table td{padding:7px 8px;border-bottom:1px solid rgba(48,56,42,.18);text-align:left;vertical-align:top}.h18-module-spec-table th{width:44%;font-weight:700}.h18-module-count{font-size:14px;margin-top:14px!important}.h18-module-detail-image{display:block;width:min(100%,1100px);height:auto;max-height:620px;aspect-ratio:16/9;object-fit:cover;border-radius:6px;margin:15px 0 20px}.h18-module-detail-text{max-width:950px;margin:18px 0}.h18-module-back{font-weight:700;text-decoration:none;color:#536243}.h18-module-back:hover,.h18-module-back:focus-visible{text-decoration:underline}.h18-module-image-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:24px}.h18-module-gallery-image{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border-radius:5px}'
            . '.h18-module-controls{display:flex;align-items:end;gap:12px;flex-wrap:wrap;margin:-6px 0 30px;padding:0 0 18px;border-bottom:1px solid rgba(48,56,42,.16);background:transparent}.h18-module-controls label{display:flex;flex-direction:column;gap:5px;font-weight:700}.h18-module-search{flex:1 1 300px}.h18-module-controls input,.h18-module-controls select{min-height:40px;border:1px solid #aaa99f;border-radius:4px;background:#fff;padding:7px 10px;font:inherit}.h18-module-controls button{min-height:40px;border:0;border-radius:4px;padding:8px 16px;background:#30382a;color:#fff;font-weight:700;cursor:pointer}.h18-module-reset{padding:9px 4px;font-weight:700;color:#536243}.h18-module-empty{padding:18px;background:#eee8dc;border-radius:6px}'
            . '@media(max-width:980px){.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.h18-module-page{width:92%;padding-top:24px}.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:1fr}.h18-module-controls{align-items:stretch}.h18-module-controls label,.h18-module-controls button{width:100%}}'
            . '</style>';
    }

    private function __construct'''
if 'h18-module-page-style-parity-002' not in collection:
    collection, count = style_pattern.subn(style_replacement, collection, count=1)
    if count != 1:
        raise SystemExit('Collection style method anchor missing')
    write(COLLECTION, collection)

# Designer chrome for the canonical frontend iframe.
css = read(ADMIN_CSS)
if 'VD-MODULE-VISUAL-PARITY-002' not in css:
    css += r'''
/* VD-MODULE-VISUAL-PARITY-002 - collection pages use the actual frontend renderer in Designer. */
.h18-vd-module-canonical-preview{margin:18px 0 24px;background:#fff;border:1px solid #c3c4c7;border-radius:8px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.h18-vd-module-canonical-preview-head{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:14px 16px;border-bottom:1px solid #dcdcde;background:#f6f7f7}
.h18-vd-module-canonical-preview-head p{margin:4px 0 0;color:#50575e}.h18-vd-module-canonical-preview-actions{display:flex;gap:8px;flex-wrap:wrap;flex:0 0 auto}
.h18-vd-module-canonical-frame{display:block;width:100%;height:min(900px,75vh);min-height:680px;border:0;background:#fff}
@media(max-width:782px){.h18-vd-module-canonical-preview-head{align-items:flex-start;flex-direction:column}.h18-vd-module-canonical-preview-actions{width:100%}.h18-vd-module-canonical-frame{min-height:560px;height:70vh}}
'''
    write(ADMIN_CSS, css)

# Correct the historical documentation: v0.1.74 solved flow/cutover, not final visual parity.
backlog = read(BACKLOG)
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.74', '## Aktuel milepælsstatus · v0.1.75 + efterfølgende source-opgaver')
backlog = backlog.replace(
    '- **VD-MODULE-CUTOVER-001 — IMPLEMENTERET I v0.1.74:** Events, Billedgalleri og Køretøjer/materiel bruger dynamisk flow-rendering efter `_old`-referencerne; Header/Footer forbliver globale.',
    '- **VD-MODULE-CUTOVER-001 — IMPLEMENTERET I v0.1.74:** Events, Billedgalleri og Køretøjer/materiel bruger dynamisk flow-rendering og naturlig indholdshøjde; `_old` er reference, mens den endelige visuelle paritet håndteres særskilt.',
)
backlog = backlog.replace(
    '6. **v0.1.74 – Modul-cutover — FÆRDIG:** de tre dynamiske samlingssider følger `_old`-layoutet og har flow-højde; versionshistorik og Save-feedback er rettet.\n7. **v0.1.75 – Formularer, søgning og eventarkiv — FÆRDIG:** Kontakt/Bliv medlem-formularer, sideprovisionering, søgning/sortering, event→album og end-of-day arkivregel.',
    '6. **v0.1.74 – Modul-cutover — FÆRDIG FUNKTIONELT:** de tre dynamiske samlingssider fik data-flow og naturlig flow-højde; 1:1-visuel `_old`-paritet var ikke afsluttet her.\n7. **v0.1.75 – Formularer, søgning og eventarkiv — FÆRDIG:** Kontakt/Bliv medlem-formularer, sideprovisionering, søgning/sortering, event→album og end-of-day arkivregel.\n8. **VD-MODULE-VISUAL-PARITY-002 — IMPLEMENTERET EFTER v0.1.75 / AFVENTER NÆSTE RELEASE:** Events, Billedgalleri og Køretøjer bruger samme canonical frontend-rendering i Designer-preview; kortgeometri, billeder, beige kortkrop, spacing og responsive regler er justeret mod `_old`.',
)
if '### VD-MODULE-VISUAL-PARITY-002' not in backlog:
    marker = '### CLEAN-RESPONSIVE-009 — DELVIST / MANUEL QA'
    addition = '''### VD-MODULE-VISUAL-PARITY-002 — IMPLEMENTERET EFTER v0.1.75 / AFVENTER NÆSTE RELEASE\n- Gælder `events`, `billedgalleri` og `koeretoejer-og-materiel`.\n- Designer viser en same-origin iframe med den rigtige offentlige CollectionPageRenderer i stedet for tre separate JS-efterligninger.\n- Dermed er kort, billeder, typografi, søgning/sortering og responsive regler den samme rendering i Designer og frontend.\n- Frontend-kort er justeret mod `_old`: 90% frame uden kunstigt max-width-loft, 3/2/1 kolonner, fuldbredde 16:9 cover, beige kortkrop, ingen kunstig skygge og mere kompakt spacing.\n- Opgaven ændrer ikke plugin-version eller updater-manifest; den skal med i næste eksplicit bestilte release.\n\n'''
    if marker not in backlog:
        raise SystemExit('Backlog insertion marker missing')
    backlog = backlog.replace(marker, addition + marker, 1)
write(BACKLOG, backlog)

write(STATUS, '''# VD-MODULE-VISUAL-PARITY-002 – status\n\n**Dato:** 1. september 2026  \n**Status:** Implementeret i source efter v0.1.75; afventer næste eksplicit bestilte release.\n\n## Scope\n- Events, Billedgalleri og Køretøjer og materiel.\n- `_old` er visuel reference.\n- Frontend beholder dynamisk flow-rendering og eksisterende søgning/sortering.\n- Kortlayout er justeret mod `_old` med 90% frame, 3/2/1 grid, fuldbredde 16:9-billeder, beige kortkrop og kompakt spacing.\n- Designer bruger den faktiske offentlige CollectionPageRenderer i en same-origin iframe i stedet for en separat JS-approximation.\n- WordPress admin-bar skjules kun i iframe-previewet for redaktører, så preview-geometrien svarer til offentlig visning.\n\n## Releasegrænse\n- Plugin header/runtime forbliver `0.1.75`.\n- `clean-update.json` forbliver `0.1.75`.\n- Ingen ZIP, manifest eller release-trigger ændres af denne opgave.\n''')

print('Applied VD-MODULE-VISUAL-PARITY-002 without version/release changes.')
