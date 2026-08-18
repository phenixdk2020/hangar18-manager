from pathlib import Path

path = Path('hangar18-manager.php')
text = path.read_text(encoding='utf-8')
old = "}\n\nHangar18_Manager::instance();\n"
new = """}

/*
 * Ultimate Designer architecture integration bridge.
 * Admin-only registration: no frontend renderer or existing page/domain is switched here.
 */
$h18_ud_autoload = __DIR__ . '/src/Autoload.php';
if (is_readable($h18_ud_autoload)) {
    require_once $h18_ud_autoload;
    \\Hangar18\\UltimateDesigner\\Autoload::register();
    if (is_admin()) {
        \\Hangar18\\UltimateDesigner\\Admin\\IntegrationAdminBootstrap::register();
    }
}

Hangar18_Manager::instance();
"""
if text.count(old) != 1:
    raise SystemExit(f'bootstrap anchor count: {text.count(old)}')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
