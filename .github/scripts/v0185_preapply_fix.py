from pathlib import Path

path = Path('.github/scripts/apply_v0185_event_facts_typography.py')
s = path.read_text(encoding='utf-8')

old = "    preview_anchor = \"\"\"        } else if (node.type === 'eventfield') {\n            wrap.classList.add('h18-clean-node-preview--eventfield');\n\"\"\"\n"
new = "    preview_anchor = \"\"\"        } else if (node.type === 'eventfield') {\n            wrap.classList.add('h18-clean-node-preview--eventfield');\"\"\"\n"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('v0.1.85 preview anchor definition not found')

old = "    inspector_anchor = \"\"\"        } else if (node.type === 'eventfield') {\n            const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[];\n\"\"\"\n"
new = "    inspector_anchor = \"\"\"        } else if (node.type === 'eventfield') {\n            const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[];\"\"\"\n"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('v0.1.85 inspector anchor definition not found')

path.write_text(s, encoding='utf-8')
