from pathlib import Path
import json

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
PLUGIN = PLUGIN_ROOT / 'hangar18-manager.php'
NAV = PLUGIN_ROOT / 'src/Admin/NavigationController.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = PLUGIN_ROOT / 'release-history.json'
STATUS = ROOT / 'docs/v0157-status.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# 1) BUG-19: WordPress expects menu-item-classes as a whitespace separated string.
nav = NAV.read_text(encoding='utf-8')
nav = replace_once(
    nav,
    "'menu-item-classes' => ['vd-menu-heading'],",
    "'menu-item-classes' => 'vd-menu-heading',",
    'heading classes serialization',
)
nav = replace_once(
    nav,
    "'menu-item-classes' => is_array($item->classes) ? $item->classes : [],",
    "'menu-item-classes' => self::menuItemClasses($item->classes),",
    'saveMenu classes serialization',
)
nav = replace_once(
    nav,
    "'menu-item-classes' => isset($item['classes']) && is_array($item['classes']) ? array_map('sanitize_html_class', $item['classes']) : [],",
    "'menu-item-classes' => self::menuItemClasses($item['classes'] ?? []),",
    'snapshot classes serialization',
)

helper_marker = "    /** @return array<mixed> */\n    private static function postedArray(string $key): array\n"
if helper_marker not in nav:
    raise SystemExit('Could not find postedArray marker for menuItemClasses helper')
helper = r'''    /** @param mixed $classes */
    private static function menuItemClasses($classes): string
    {
        if (is_string($classes)) {
            $classes = preg_split('/\s+/', trim($classes)) ?: [];
        }
        if (!is_array($classes)) {
            $classes = [];
        }

        $clean = [];
        foreach ($classes as $className) {
            $className = sanitize_html_class((string) $className);
            if ($className !== '') {
                $clean[] = $className;
            }
        }
        return implode(' ', array_values(array_unique($clean)));
    }

'''
nav = nav.replace(helper_marker, helper + helper_marker, 1)
NAV.write_text(nav, encoding='utf-8')

# 2) CLEANUP-02: active PHP runtime identity becomes VisualDesignerManager.
# Persisted option/meta/action/page slugs named h18_clean / h18-clean are intentionally untouched.
php_files = sorted(PLUGIN_ROOT.rglob('*.php'))
if PLUGIN not in php_files:
    php_files.append(PLUGIN)

old_namespace_hits = 0
old_domain_hits = 0
for path in php_files:
    text = path.read_text(encoding='utf-8')
    old_namespace_hits += text.count('Hangar18\\Clean')
    old_domain_hits += text.count('hangar18-manager-clean')

    text = text.replace('namespace Hangar18\\Clean', 'namespace VisualDesignerManager')
    text = text.replace('\\Hangar18\\Clean\\', '\\VisualDesignerManager\\')
    text = text.replace('Hangar18\\Clean\\', 'VisualDesignerManager\\')
    text = text.replace('hangar18-manager-clean', 'visual-designer-manager')

    if path == PLUGIN:
        text = text.replace('Current Clean core provides', 'Current Visual Designer Manager core provides')
        text = text.replace('Clean deliberately does not load the', 'Visual Designer Manager deliberately does not load the')
        text = text.replace('while the clean architecture remains isolated.', 'while the current architecture remains isolated.')

    path.write_text(text, encoding='utf-8')

if old_namespace_hits < 10:
    raise SystemExit(f'Namespace migration hit count unexpectedly low: {old_namespace_hits}')
if old_domain_hits < 1:
    raise SystemExit('Text-domain migration found no old domain')

# 3) Version bump.
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.56', ' * Version: 0.1.57', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.56');", "define('H18_CLEAN_VERSION', '0.1.57');", 'runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')

# 4) Technical contract and release documentation.
tech = TECH.read_text(encoding='utf-8')
contract = r'''

## 0.1.57 – Menu-save og runtime-identitet

### VD-MENU-CLASS-SERIALIZATION-001
- Alle kald til WordPress `wp_update_nav_menu_item()` skal sende `menu-item-classes` som en whitespace-separeret streng, aldrig som PHP-array.
- Eksisterende CSS-klasser normaliseres med `sanitize_html_class`, dubletter fjernes, og tomme værdier udelades.
- Reglen gælder både almindelig Gem menu, oprettelse af overskrift/gruppe og gendannelse fra navigation-snapshot.
- En eksisterende menu med én eller flere CSS-klasser må ikke kunne udløse PHP `TypeError` i WordPress `nav-menu.php`.

### VD-RUNTIME-IDENTITY-001
- Aktiv PHP-runtime bruger namespace-roden `VisualDesignerManager\\...`; nye stacktraces må ikke vise `Hangar18\\Clean\\...`.
- WordPress Text Domain er `visual-designer-manager`.
- Persistente kompatibilitets-ID'er som eksisterende option/meta/action/page-slugs med `h18_clean` / `h18-clean` ændres ikke i denne migration. De er data-/URL-kompatibilitet og må ikke masseomdøbes uden en særskilt migrationskontrakt.
- Den historiske `Hangar18_Manager` compatibility marker bevares, så eksisterende theme-integration ikke brydes.
'''
if '## 0.1.57 – Menu-save og runtime-identitet' not in tech:
    tech += contract
TECH.write_text(tech, encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8')
release_notes = '''<h4>0.1.57 – Menu-save og runtime-identitet</h4><ul><li><strong>BUG-19:</strong> Menu → Gem serialiserer nu WordPress menu-item CSS-klasser som streng og kan derfor ikke længere sende et array ind i WordPress <code>explode()</code>.</li><li>Samme klasseserialisering bruges ved menuoverskrifter og navigation-snapshot restore.</li><li><strong>VD-RUNTIME-IDENTITY-001:</strong> aktive PHP-klasser bruger nu <code>VisualDesignerManager\\…</code> i stedet for <code>Hangar18\\Clean\\…</code>, og Text Domain er <code>visual-designer-manager</code>.</li><li>Eksisterende <code>h18_clean</code>/<code>h18-clean</code> option-, meta-, action- og side-slugs bevares med vilje for data- og URL-kompatibilitet.</li></ul>\n'''
if not notes.startswith('<h4>0.1.57'):
    notes = release_notes + notes
NOTES.write_text(notes, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history.setdefault('versions', [])
if not versions or versions[0].get('version') != '0.1.57':
    versions.insert(0, {
        'version': '0.1.57',
        'date': '2026-08-30',
        'items': [
            'BUG-19: menu-item-classes serialiseres som WordPress-kompatibel whitespace-streng ved Gem menu, overskrift og snapshot-restore.',
            'CSS-klasser saniteres, tomme værdier filtreres og dubletter fjernes før wp_update_nav_menu_item().',
            'VD-RUNTIME-IDENTITY-001: aktiv PHP namespace-rod er VisualDesignerManager i stedet for Hangar18\\Clean.',
            'WordPress Text Domain er visual-designer-manager.',
            'Persistente h18_clean/h18-clean kompatibilitets-IDer bevares uændret for at beskytte eksisterende data og URLs.'
        ],
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text('''# Visual Designer Manager 0.1.57 status\n\n- BUG-19: WordPress menu-item CSS-klasser serialiseres som streng i alle aktive skriveveje.\n- CLEANUP-02: aktiv PHP runtime namespace er `VisualDesignerManager\\...`.\n- Text Domain er `visual-designer-manager`.\n- Persistente `h18_clean` / `h18-clean` option/meta/action/page-slugs er med vilje bevaret som kompatibilitets-IDer.\n- Historisk `Hangar18_Manager` theme-compatibility marker er bevaret.\n- Ingen database-/meta-massenavngivning udføres i 0.1.57.\n''', encoding='utf-8')

print(f'Applied 0.1.57: migrated {old_namespace_hits} active namespace references and {old_domain_hits} text-domain references.')
