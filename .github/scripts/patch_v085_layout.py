from pathlib import Path

js_path = Path('assets/ultimate-designer-layout-tools.js')
js = js_path.read_text(encoding='utf-8')
old = '''    function controls($row, selector) {\n        if (!$row || !$row.length) { return $(); }\n        let $result = $row.find(selector);\n        const index = String($row.attr('data-section-index') || '');\n        if (index) {\n            $result = $result.add($('#h18-page-inspector-target .h18-page-section-body').filter(function () {\n                return String($(this).closest('.h18-page-section-row').attr('data-section-index') || '') === index;\n            }).find(selector));\n        }\n        return $result;\n    }\n'''
new = '''    function controls($row, selector) {\n        if (!$row || !$row.length) { return $(); }\n        let $result = $row.find(selector);\n        // The legacy editor physically moves the selected row's body into the\n        // Inspector. The source row keeps .is-selected, so include Inspector\n        // controls only for that exact row. This avoids leaking values between\n        // elements while keeping Auto-kasser/Table compatible with Inspector.\n        if ($row.hasClass('is-selected')) {\n            $result = $result.add($('#h18-page-inspector-target').find(selector));\n        }\n        return $result;\n    }\n'''
if old in js:
    js = js.replace(old, new, 1)
elif new not in js:
    raise SystemExit('controls() anchor not found')
js_path.write_text(js, encoding='utf-8')

boot_path = Path('src/Admin/IntegrationAdminBootstrap.php')
boot = boot_path.read_text(encoding='utf-8')
old_boot = '        SideHealthAdminController::register();\n        AssetManagerAdminController::register();'
new_boot = '        SideHealthAdminController::register();\n        LayoutToolsAdminController::register();\n        AssetManagerAdminController::register();'
if old_boot in boot:
    boot = boot.replace(old_boot, new_boot, 1)
elif 'LayoutToolsAdminController::register();' not in boot:
    raise SystemExit('IntegrationAdminBootstrap registration anchor not found')
boot_path.write_text(boot, encoding='utf-8')
