from pathlib import Path

root = Path('.')

# Selection palette: green selected/resize, blue hover, red overlap.
p = root / 'clean/hangar18-manager/assets/editor-v0114.css'
s = p.read_text(encoding='utf-8')
s += """

/* Clean 0.1.15: semantic editor state colours.
   Blue = hover, green = selected/active, red = overlap warning. */
.h18-clean-node.is-selected{
    outline:2px solid #00a32a!important;
    outline-offset:1px!important;
}
.h18-clean-node.is-selected>.h18-clean-resize{
    background:#00a32a!important;
}
.h18-clean-node.is-resizing{
    box-shadow:0 0 0 2px #00a32a!important;
}
.h18-clean-node.is-selected.has-layout-overlap{
    outline:2px solid #00a32a!important;
    outline-offset:2px!important;
    box-shadow:0 0 0 4px rgba(214,54,56,.75)!important;
}
"""
p.write_text(s, encoding='utf-8')

# Version bump.
p = root / 'clean/hangar18-manager/hangar18-manager.php'
s = p.read_text(encoding='utf-8')
s = s.replace('Version: 0.1.14', 'Version: 0.1.15').replace("H18_CLEAN_VERSION', '0.1.14'", "H18_CLEAN_VERSION', '0.1.15'")
p.write_text(s, encoding='utf-8')

# Readme.
p = root / 'clean/hangar18-manager/readme.txt'
s = p.read_text(encoding='utf-8')
s = s.replace('Version: 0.1.14', 'Version: 0.1.15')
marker = '== 0.1.14 ==\n'
notes = "== 0.1.15 ==\n* Valgt/aktivt element markeres grønt i stedet for blåt.\n* Resize-punkter og aktiv resize følger den grønne selection-farve.\n* Blå er fortsat hover/drop-kontekst, mens rød fortsat udelukkende betyder overlap/advarsel.\n* Et valgt element med overlap har grøn selection plus separat rød overlap-markering.\n\n"
if marker not in s:
    raise SystemExit('Readme marker missing')
s = s.replace(marker, notes + marker)
p.write_text(s, encoding='utf-8')

(root / 'clean-release-notes.html').write_text("<h4>0.1.15</h4><ul><li>Selection er nu grøn i stedet for blå.</li><li>Resize-punkter og aktiv resize er grønne.</li><li>Blå bruges til hover/drop-kontekst, mens rød fortsat kun betyder overlap/advarsel.</li><li>Valgt + overlap vises som grøn selection med separat rød overlap-markering.</li></ul>\n", encoding='utf-8')
