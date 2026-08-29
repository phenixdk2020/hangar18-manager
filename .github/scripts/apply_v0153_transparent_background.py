from pathlib import Path
import json

ROOT = Path('clean/hangar18-manager')
CORE = ROOT / 'assets/editor-v018-core.js'
PLUGIN = ROOT / 'hangar18-manager.php'
HISTORY = ROOT / 'release-history.json'
NOTES = Path('clean-release-notes.html')
STATUS = Path('docs/v0153-status.md')
CSS = ROOT / 'assets/editor-v0153-transparent.css'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

core = CORE.read_text(encoding='utf-8')
old = """        if (PARENT_TYPES.includes(node.type)) {\n            const background = /^#[0-9a-f]{6}$/i.test(String(props.background || '')) ? String(props.background).toLowerCase() : 'transparent';\n            card.style.background = background;\n            card.style.borderRadius = clamp(parseInt(props.radius || 0, 10) || 0, 0, 100) + 'px';\n            card.setAttribute('data-h18-parent-painted-box', '1');\n        }\n"""
new = """        if (PARENT_TYPES.includes(node.type)) {\n            const background = /^#[0-9a-f]{6}$/i.test(String(props.background || '')) ? String(props.background).toLowerCase() : 'transparent';\n            card.style.background = background;\n            card.style.borderRadius = clamp(parseInt(props.radius || 0, 10) || 0, 0, 100) + 'px';\n            card.setAttribute('data-h18-parent-painted-box', '1');\n            card.removeAttribute('data-h18-leaf-transparent');\n        } else if (node.type === 'text' || node.type === 'menu' || node.type === 'image') {\n            const transparent = node.type === 'image' ? props.boxTransparent !== false : props.backgroundTransparent !== false;\n            const fallback = node.type === 'image' ? '#ffffff' : (node.type === 'menu' ? '#30382a' : '#ffffff');\n            const requested = node.type === 'image' ? props.boxBackground : props.background;\n            const background = transparent ? 'transparent' : (/^#[0-9a-f]{6}$/i.test(String(requested || '')) ? String(requested).toLowerCase() : fallback);\n            card.style.background = background;\n            card.style.borderRadius = clamp(parseInt(props.radius || 0, 10) || 0, 0, 100) + 'px';\n            card.setAttribute('data-h18-leaf-transparent', transparent ? '1' : '0');\n        } else {\n            card.removeAttribute('data-h18-leaf-transparent');\n        }\n"""
core = replace_once(core, old, new, 'applyVisualStyle transparent leaf')
CORE.write_text(core, encoding='utf-8')

CSS.write_text("""/* Visual Designer Manager 0.1.53 · transparent leaf parity.\n * A transparent leaf must reveal its nearest painted parent in Designer,\n * just as canonical Preview/frontend already do. Selection/hover outlines\n * remain visible; only the physical paint surface becomes transparent. */\n.h18-clean-node[data-h18-leaf-transparent=\"1\"]{background:transparent!important}\n.h18-clean-node[data-h18-leaf-transparent=\"1\"]>.h18-clean-node-preview{background-color:transparent!important}\n.h18-clean-node[data-h18-leaf-transparent=\"0\"]{background-clip:border-box!important}\n""", encoding='utf-8')

plugin = PLUGIN.read_text(encoding='utf-8')
plugin = plugin.replace('Version: 0.1.52', 'Version: 0.1.53', 1)
plugin = plugin.replace("H18_CLEAN_VERSION', '0.1.52'", "H18_CLEAN_VERSION', '0.1.53'", 1)
anchor = """    wp_enqueue_style(\n        'h18-clean-editor-v0148-layers',\n        H18_CLEAN_URL . 'assets/editor-v0148-layers.css',\n        ['h18-clean-editor-v0144'],\n        H18_CLEAN_VERSION\n    );\n"""
insert = anchor + """    wp_enqueue_style(\n        'h18-clean-editor-v0153-transparent',\n        H18_CLEAN_URL . 'assets/editor-v0153-transparent.css',\n        ['h18-clean-editor-v0148-layers'],\n        H18_CLEAN_VERSION\n    );\n"""
plugin = replace_once(plugin, anchor, insert, 'enqueue transparent css')
PLUGIN.write_text(plugin, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history.setdefault('versions', [])
if not any(str(v.get('version')) == '0.1.53' for v in versions):
    versions.insert(0, {
        'version': '0.1.53',
        'date': '2026-08-29',
        'items': [
            'BUG-18: Gennemsigtig baggrund på Tekst viser nu den nærmeste Kasse/Sektions baggrund igennem i Designer.',
            'Samme paint-regel gælder Menu og gennemsigtig Billede-boks, så leaf-transparens er ensartet.',
            'Transparent paint ændrer ikke canonical geometri, selection/hover-outline eller parent-baggrund.',
            'Preview/frontend-behavior regression-gates mod Rendererens eksisterende transparent-kontrakt.',
            'Rettelsen gælder både almindelige sider og Global Header/Footer Designer, som deler v018-core.'
        ]
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

old_notes = NOTES.read_text(encoding='utf-8').strip() if NOTES.exists() else ''
head = """<h4>0.1.53 – Gennemsigtig elementbaggrund</h4><ul><li><strong>BUG-18:</strong> Når <em>Gennemsigtig baggrund</em> er slået til på Tekst, males Designer-elementet nu fysisk transparent, så den nærmeste Kasse/Sektions farve ses igennem.</li><li>Samme regel gælder Menu og gennemsigtig Billede-boks.</li><li>Markering, hover, resize og canonical geometri ændres ikke.</li><li>Preview og frontend bevarer Rendererens eksisterende transparente paint-kontrakt.</li></ul>"""
NOTES.write_text(head + ('\n' + old_notes if old_notes else '') + '\n', encoding='utf-8')

STATUS.write_text("""# Visual Designer Manager 0.1.53 status\n\n## BUG-18 – gennemsigtig elementbaggrund\n\n- Designer leaf-card må ikke have hvid paint når canonical transparent-flag er aktivt.\n- Tekst/Menu bruger `backgroundTransparent`; Billede bruger `boxTransparent`.\n- Nærmeste forælder (Kasse/Sektion) skal kunne ses igennem.\n- Selection/hover/resize-chrome bevares.\n- Samme v018-core bruges af side-Designer og Global Header/Footer Designer.\n- Preview/frontend skal fortsat bruge canonical Rendererens `transparent` paint.\n""", encoding='utf-8')

print('Applied Visual Designer Manager 0.1.53 transparent background patch')
