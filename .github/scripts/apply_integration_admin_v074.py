from pathlib import Path

php_path = Path('hangar18-manager.php')
css_path = Path('assets/admin.css')
text = php_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

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
if old in text:
    if text.count(old) != 1:
        raise SystemExit(f'bootstrap anchor count: {text.count(old)}')
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('integration bootstrap anchor missing')

marker = '/* v0.7.4 – Ultimate Designer integration dashboard */'
styles = """
/* v0.7.4 – Ultimate Designer integration dashboard */
.h18-ud-integration-admin{max-width:none!important;margin-right:20px}
.h18-ud-status-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:18px 0 26px}
.h18-ud-status-card{background:#fff;border:1px solid #dcdcde;border-left:5px solid var(--h18-sand);border-radius:8px;padding:18px;min-width:0}
.h18-ud-status-card h3{margin:0 0 10px;color:var(--h18-olive)}
.h18-ud-status-card strong{display:block;font-size:18px;line-height:1.3;overflow-wrap:anywhere}
.h18-ud-status-card p{margin:8px 0 0;color:var(--h18-steel)}
.h18-ud-backlog td:first-child{width:70px}.h18-ud-backlog td:nth-child(2){width:100px;font-weight:600}
"""
if marker not in css:
    css += '\n\n' + styles.strip() + '\n'

php_path.write_text(text, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
