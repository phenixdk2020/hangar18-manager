from pathlib import Path
p = Path('clean/hangar18-manager/assets/editor-v018-core.js')
s = p.read_text(encoding='utf-8')
old = "title.textContent = node.type.toUpperCase() + ' · ' + node.id.slice(-8);"
new = "title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);"
if old not in s:
    raise SystemExit('card label anchor missing')
s = s.replace(old, new, 1)
old = "        let html = '<div class=\"h18-clean-inspector-head\"><strong>' + escapeHtml(node.type) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';"
new = "        let html = '<div class=\"h18-clean-inspector-head\"><strong>' + escapeHtml(({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type] || node.type.toUpperCase())) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';"
if old not in s:
    raise SystemExit('inspector label anchor missing')
s = s.replace(old, new, 1)
old = "                    const a = list[i].geometry.desktop;\n                    const b = list[j].geometry.desktop;"
new = "                    // Kasse/Sektion are layout wrappers and do not participate in leaf overlap warnings.\n                    if (PARENT_TYPES.includes(list[i].type) || PARENT_TYPES.includes(list[j].type)) { continue; }\n                    const a = list[i].geometry.desktop;\n                    const b = list[j].geometry.desktop;"
if old not in s:
    raise SystemExit('overlap anchor missing')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
