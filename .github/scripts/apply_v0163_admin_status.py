from pathlib import Path

# v0.1.63 patch runner; v0.1.62 feature QA is intentionally forward-compatible.
ROOT = Path('.')
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
ADMIN_JS = ROOT / 'clean/hangar18-manager/assets/admin-v0123.js'
NOTES = ROOT / 'clean-release-notes.html'
RELEASE_WORKFLOW = ROOT / '.github/workflows/visual-designer-release.yml'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old, new, 1)

plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, 'Version: 0.1.62', 'Version: 0.1.63', 'plugin header version')
plugin = replace_once(plugin, "H18_CLEAN_VERSION', '0.1.62'", "H18_CLEAN_VERSION', '0.1.63'", 'runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')

admin = ADMIN_JS.read_text(encoding='utf-8')
admin = replace_once(admin, "'h18-clean-menu': ['Under udvikling', 'partial']", "'h18-clean-menu': ['Klar', 'ready']", 'Menu status')
admin = replace_once(admin, "'h18-clean-header-footer': ['Under udvikling', 'partial']", "'h18-clean-header-footer': ['Klar', 'ready']", 'Header Footer status')
ADMIN_JS.write_text(admin, encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8')
entry = '<h4>0.1.63 – Admin-status for Menu og Header/Footer</h4><ul><li><strong>Menu</strong> vises nu som <strong>Klar</strong> i Visual Designer Manager-sidebar.</li><li><strong>Header / Footer</strong> vises nu som <strong>Klar</strong> i Visual Designer Manager-sidebar.</li><li>Ingen funktionel Designer-, Menu- eller Header/Footer-logik er ændret i denne patch.</li></ul>\n'
if not notes.startswith('<h4>0.1.63'):
    notes = entry + notes
NOTES.write_text(notes, encoding='utf-8')

workflow = RELEASE_WORKFLOW.read_text(encoding='utf-8')
anchor = "          grep -Fq 'h18-manager-badge is-ok\">Klar' clean/hangar18-manager/src/Admin/GlobalDesignerController.php\n"
addition = anchor + "          grep -Fq \"'h18-clean-menu': ['Klar', 'ready']\" clean/hangar18-manager/assets/admin-v0123.js\n          grep -Fq \"'h18-clean-header-footer': ['Klar', 'ready']\" clean/hangar18-manager/assets/admin-v0123.js\n"
if "'h18-clean-menu': ['Klar', 'ready']" not in workflow:
    workflow = replace_once(workflow, anchor, addition, 'release admin status gates')
RELEASE_WORKFLOW.write_text(workflow, encoding='utf-8')
