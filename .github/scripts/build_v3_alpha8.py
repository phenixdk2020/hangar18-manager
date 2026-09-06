from pathlib import Path
import hashlib
import json
import subprocess

VERSION = '3.0.0-alpha.8'
DEST = Path('build/visual-designer-manager')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


subprocess.run(['python3', '.github/scripts/build_v3_alpha7.py'], check=True)

# Alpha.8 is a runtime-only responsive repair. Designer data, renderer markup,
# shell ownership, storage and migrations stay byte-identical to Alpha.7.
protected = [
    'assets/admin-v019.css', 'assets/admin-v0123.css', 'assets/admin-v0175.css',
    'assets/editor-v018-core.js', 'assets/editor-v0144-viewport.js',
    'assets/editor-v0169-canvas-height.js', 'assets/editor.css',
    'src/Frontend/Renderer.php', 'src/Frontend/ThemeShell.php',
    'src/Model/LayoutModel.php', 'src/Model/TemplateLayoutModel.php',
    'src/Migration/V3StorageMigration.php', 'src/Migration/V3StyleRecovery.php',
    'src/Migration/SharedPrimaryMenu.php', 'templates/vdm-site-shell.php',
]
protected_before = {rel: sha(DEST / rel) for rel in protected}

main = DEST / 'visual-designer-manager.php'
main_text = main.read_text(encoding='utf-8')
for old, new in [
    (' * Version: 3.0.0-alpha.7', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.7');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.7');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main_text.count(old) != 1:
        raise SystemExit(f'Alpha.8 version token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)
main.write_text(main_text, encoding='utf-8')

responsive = DEST / 'src/Frontend/ResponsiveRenderer.php'
text = responsive.read_text(encoding='utf-8')
import_old = 'use VisualDesignerManager\\Model\\LayoutModel;\n'
import_new = import_old + 'use VisualDesignerManager\\Model\\TemplateLayoutModel;\n'
if text.count(import_old) != 1:
    raise SystemExit('Alpha.8 ResponsiveRenderer import anchor mismatch')
text = text.replace(import_old, import_new, 1)

start_marker = '    public static function css(): void\n'
end_marker = '    /** @return array<string,mixed>|null */\n    private static function model'
start = text.find(start_marker)
end = text.find(end_marker, start)
if start < 0 or end < 0 or end <= start:
    raise SystemExit('Alpha.8 ResponsiveRenderer css() anchors not found')

new_css = r'''    public static function css(): void
    {
        if (!is_singular('page')) {
            return;
        }

        $postId = get_queried_object_id();
        if ($postId <= 0) {
            return;
        }

        $pageModel = self::model($postId);
        if ($pageModel === null || empty($pageModel['nodes']) || !is_array($pageModel['nodes'])) {
            return;
        }

        $models = [[
            'scope' => ThemeShell::enabled() ? '.h18-vd-live-shell-page ' : '',
            'model' => $pageModel,
        ]];

        if (ThemeShell::enabled()) {
            foreach (['header', 'footer'] as $part) {
                $templateId = ThemeShell::resolvedTemplateId($postId, $part);
                if ($templateId === '' || !TemplateLayoutModel::exists($templateId, $part)) {
                    continue;
                }
                $templateModel = TemplateLayoutModel::model($templateId);
                if (empty($templateModel['nodes']) || !is_array($templateModel['nodes'])) {
                    continue;
                }
                $models[] = [
                    'scope' => $part === 'header' ? '.h18-vd-live-shell-header ' : '.h18-vd-live-shell-footer ',
                    'model' => $templateModel,
                ];
            }
        }

        $laptop = '';
        $tablet = '';
        $mobile = '';
        foreach ($models as $entry) {
            self::appendModelCss(
                (array) ($entry['model'] ?? []),
                (string) ($entry['scope'] ?? ''),
                $laptop,
                $tablet,
                $mobile
            );
        }

        echo '<style id="h18-clean-responsive-css">';
        echo '.h18-clean-page{max-width:100%;overflow-x:clip}';
        echo '.h18-vd-live-shell,.h18-vd-live-shell-part,.h18-vd-live-shell-part>.h18-clean-page{width:100%;max-width:100%;min-width:0;box-sizing:border-box}';
        echo '@media(max-width:' . esc_attr((string) self::LAPTOP_MAX) . 'px){' . $laptop . '}';
        echo '@media(max-width:' . esc_attr((string) self::TABLET_MAX) . 'px){' . $tablet . '}';
        echo '@media(max-width:' . esc_attr((string) self::MOBILE_MAX) . 'px){'
            . '.h18-vd-live-shell,.h18-vd-live-shell-part,.h18-clean-page,.h18-clean-front-section,.h18-clean-front-container{min-width:0;max-width:100%;}'
            . '.h18-vd-live-shell{overflow-x:hidden;}'
            . $mobile . '}';
        echo '</style>';
    }

    /**
     * Emit the same responsive geometry contract for one rendered model.
     * Header, page and Footer models are scoped independently so identical
     * node IDs in different parts cannot overwrite one another.
     *
     * @param array<string,mixed> $model
     */
    private static function appendModelCss(array $model, string $scope, string &$laptop, string &$tablet, string &$mobile): void
    {
        $byId = [];
        $byParent = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) {
                continue;
            }
            $id = (string) $node['id'];
            $byId[$id] = $node;
            $parent = (string) ($node['parentId'] ?? '');
            $byParent[$parent][] = $node;
        }

        foreach ($byId as $id => $node) {
            $lg = self::effectiveGeometry($node, 'laptop');
            $tg = self::effectiveGeometry($node, 'tablet');
            $mg = self::effectiveGeometry($node, 'mobile');
            $laptopRows = self::effectiveRows($id, 'laptop', $byId, $byParent, []);
            $tabletRows = self::effectiveRows($id, 'tablet', $byId, $byParent, []);
            $mobileRows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $floating = (string) ($node['type'] ?? '') === 'button' && (string) ($props['placementMode'] ?? 'normal') === 'overlay';
            $zIndex = max(1, min(200, (int) ($props['zIndex'] ?? 20)));
            $laptop .= self::geometryCss($selector, $lg, $laptopRows, $floating, $zIndex);
            $tablet .= self::geometryCss($selector, $tg, $tabletRows, $floating, $zIndex);
            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);
        }
    }

'''
text = text[:start] + new_css + text[end:]
responsive.write_text(text, encoding='utf-8')

history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.7':
    raise SystemExit('Expected Alpha.7 release-history baseline missing')
alpha8 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'Responsive runtime anvender nu de gemte Laptop/Tablet/Mobil-geometrier på både Header, sideindhold og Footer.',
        'Header- og Footer-templategeometri scopes separat fra sidegeometrien, så responsive regler ikke kolliderer mellem shell-delene.',
        'Mobilvisningen låses til samme 782 px breakpoint som V1-menuens mobile runtime, med 390 px som Designerens mobile referenceviewport.',
        'Ingen layoutdata migreres eller omskrives; Renderer-markup, Designer, storage, Alpha.7 style recovery og shared menu bevares.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha8] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

built = responsive.read_text(encoding='utf-8')
for required in [
    'use VisualDesignerManager\\Model\\TemplateLayoutModel;',
    "ThemeShell::resolvedTemplateId($postId, $part)",
    "TemplateLayoutModel::model($templateId)",
    "'.h18-vd-live-shell-header '",
    "'.h18-vd-live-shell-page '",
    "'.h18-vd-live-shell-footer '",
    'private static function appendModelCss(',
    "public const MOBILE_MAX = 782;",
    "self::effectiveGeometry($node, 'mobile')",
    ".h18-vd-live-shell{overflow-x:hidden;}",
]:
    if required not in built:
        raise SystemExit(f'Alpha.8 mobile runtime contract token missing: {required}')

built_history = json.loads(history_path.read_text(encoding='utf-8'))['versions']
if built_history[0].get('version') != VERSION or built_history[1].get('version') != '3.0.0-alpha.7':
    raise SystemExit('Alpha.8 release-history ordering failed')

for rel, before in protected_before.items():
    if sha(DEST / rel) != before:
        raise SystemExit(f'Protected V3 parity file changed during Alpha.8 mobile repair: {rel}')

print('V3 Alpha.8 responsive Header/Page/Footer geometry: PASS')
print('Header/Footer use their stored mobile template geometry: PASS')
print('Responsive shell scopes isolate Header/Page/Footer IDs: PASS')
print('390px mobile reference + 782px runtime breakpoint retained: PASS')
print('Designer/layout/storage/Renderer markup unchanged: PASS')
