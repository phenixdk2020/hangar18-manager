from pathlib import Path
p = Path('clean/hangar18-manager/assets/editor-v018-core.js')
s = p.read_text(encoding='utf-8')
s = s.replace("title.textContent = node.type.toUpperCase() + ' · ' + node.id.slice(-8);", "title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);")
s = s.replace("                    const a = list[i].geometry.desktop;\n                    const b = list[j].geometry.desktop;", "                    if (PARENT_TYPES.includes(list[i].type) || PARENT_TYPES.includes(list[j].type)) { continue; }\n                    const a = list[i].geometry.desktop;\n                    const b = list[j].geometry.desktop;")
p.write_text(s, encoding='utf-8')
