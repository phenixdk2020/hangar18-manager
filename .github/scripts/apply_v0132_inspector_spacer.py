from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
CSS = ROOT / 'clean/hangar18-manager/assets/editor-v0132.css'
README = ROOT / 'clean/hangar18-manager/readme.txt'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
NOTES = ROOT / 'clean-release-notes.html'
RELEASE_WORKFLOW = ROOT / '.github/workflows/clean-release.yml'

css = '''/* Visual Designer Manager 0.1.32 */

/*
 * Inspector scroll buffer.
 * The Inspector is a viewport-bound scroll container. A real block pseudo-element
 * is deliberately added after the dynamic Inspector content so the scrollbar can
 * move well past the final control. This is editor chrome only and never affects
 * canonical element geometry or frontend output.
 */
.h18-clean-inspector:not(.is-collapsed)::after{
    content:"";
    display:block;
    width:100%;
    height:360px;
    min-height:360px;
    clear:both;
    pointer-events:none;
}
'''
CSS.write_text(css, encoding='utf-8')

plugin = PLUGIN.read_text(encoding='utf-8')
if "Version: 0.1.31" not in plugin or "H18_CLEAN_VERSION', '0.1.31'" not in plugin:
    raise SystemExit('Expected 0.1.31 plugin version not found')
plugin = plugin.replace('Version: 0.1.31', 'Version: 0.1.32', 1)
plugin = plugin.replace("H18_CLEAN_VERSION', '0.1.31'", "H18_CLEAN_VERSION', '0.1.32'", 1)

anchor = """    wp_enqueue_style(\n        'h18-clean-editor-v0131',\n        H18_CLEAN_URL . 'assets/editor-v0131.css',\n        ['h18-clean-editor-v0125'],\n        H18_CLEAN_VERSION\n    );\n"""
addition = anchor + """    wp_enqueue_style(\n        'h18-clean-editor-v0132',\n        H18_CLEAN_URL . 'assets/editor-v0132.css',\n        ['h18-clean-editor-v0131'],\n        H18_CLEAN_VERSION\n    );\n"""
if "h18-clean-editor-v0132" not in plugin:
    if anchor not in plugin:
        raise SystemExit('0.1.31 stylesheet enqueue anchor not found')
    plugin = plugin.replace(anchor, addition, 1)
PLUGIN.write_text(plugin, encoding='utf-8')

readme = README.read_text(encoding='utf-8')
readme = readme.replace('Version: 0.1.31', 'Version: 0.1.32', 1)
section = '''== 0.1.32 ==
* Inspector får en ekstra usynlig scroll-buffer på 360 px efter sidste kontrol, så man kan rulle tydeligt forbi nederste felt.
* Bufferen findes kun i editorens Inspector og påvirker ikke canonical layout, elementhøjder, Preview eller frontend.
* Den eksisterende viewport-bundne Inspector-scroll fra 0.1.30 bevares.

'''
if '== 0.1.32 ==' not in readme:
    marker = '== 0.1.31 ==\n'
    if marker not in readme:
        raise SystemExit('0.1.31 readme section not found')
    readme = readme.replace(marker, section + marker, 1)
README.write_text(readme, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
if not any(str(row.get('version', '')) == '0.1.32' for row in history if isinstance(row, dict)):
    history.insert(0, {
        'version': '0.1.32',
        'date': '2026-08-27',
        'items': [
            'Inspector har nu en ekstra 360 px usynlig scroll-buffer efter det sidste kontrolfelt, så nederste indstillinger kan rulles helt fri af viewport-kanten.',
            'Scroll-bufferen er ren editor-chrome og ændrer ikke canonical geometri, Preview eller frontend.'
        ]
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

NOTES.write_text(
    '<h4>0.1.32</h4><ul>'
    '<li><strong>Inspector scroll-buffer:</strong> Inspector får 360 px ekstra usynlig plads efter sidste kontrol, så man kan rulle tydeligt længere ned og få de nederste felter helt fri af viewport-kanten.</li>'
    '<li><strong>Kun editor:</strong> den ekstra plads er ren Inspector/editor-chrome og påvirker ikke canonical layout, elementhøjder, Preview eller frontend.</li>'
    '<li><strong>Eksisterende scroll bevares:</strong> viewport-bundet Inspector med egen scrollbar fra 0.1.30 fortsætter uændret.</li>'
    '</ul>',
    encoding='utf-8'
)

workflow = RELEASE_WORKFLOW.read_text(encoding='utf-8')
qa_anchor = "          test -s clean/hangar18-manager/assets/editor-v0125.css\n"
qa_lines = qa_anchor + "          test -s clean/hangar18-manager/assets/editor-v0132.css\n          grep -q 'height:360px' clean/hangar18-manager/assets/editor-v0132.css\n          grep -q 'h18-clean-editor-v0132' clean/hangar18-manager/hangar18-manager.php\n"
if "grep -q 'height:360px' clean/hangar18-manager/assets/editor-v0132.css" not in workflow:
    if qa_anchor not in workflow:
        raise SystemExit('Release QA anchor not found')
    workflow = workflow.replace(qa_anchor, qa_lines, 1)
RELEASE_WORKFLOW.write_text(workflow, encoding='utf-8')

print('Applied Visual Designer Manager 0.1.32 Inspector scroll spacer patch.')
