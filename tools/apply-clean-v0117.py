from pathlib import Path

root = Path('.')

def replace(path, old, new):
    p = root / path
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'Pattern not found in {path}: {old[:100]!r}')
    p.write_text(s.replace(old, new, 1), encoding='utf-8')

# Version + editor CSS.
replace('clean/hangar18-manager/hangar18-manager.php', 'Version: 0.1.16', 'Version: 0.1.17')
replace('clean/hangar18-manager/hangar18-manager.php', "define('H18_CLEAN_VERSION', '0.1.16');", "define('H18_CLEAN_VERSION', '0.1.17');")
replace(
    'clean/hangar18-manager/hangar18-manager.php',
    "    wp_enqueue_script(\n        'h18-clean-editor-v0114',",
    "    wp_enqueue_style(\n        'h18-clean-editor-v0117',\n        H18_CLEAN_URL . 'assets/editor-v0117.css',\n        ['h18-clean-editor-v0114'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0114',"
)

# Canonical text props.
replace(
    'clean/hangar18-manager/src/Model/LayoutModel.php',
    "                'text' => wp_kses_post((string) ($raw['text'] ?? 'Ny tekst')),\n                'align' => in_array((string) ($raw['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $raw['align'] : 'left',",
    "                'heading' => sanitize_text_field((string) ($raw['heading'] ?? '')),\n                'headingLevel' => in_array((string) ($raw['headingLevel'] ?? 'h2'), ['h2', 'h3', 'h4', 'h5', 'h6'], true) ? (string) $raw['headingLevel'] : 'h2',\n                'text' => wp_kses_post((string) ($raw['text'] ?? 'Ny tekst')),\n                'align' => in_array((string) ($raw['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $raw['align'] : 'left',"
)

# Frontend rendering.
replace(
    'clean/hangar18-manager/src/Frontend/Renderer.php',
    "        echo '.h18-clean-front-text{overflow-wrap:anywhere}';",
    "        echo '.h18-clean-front-text{overflow-wrap:anywhere}';\n        echo '.h18-clean-front-text-heading{margin:0 0 8px;line-height:1.2}';"
)
replace(
    'clean/hangar18-manager/src/Frontend/Renderer.php',
    "        if ($type === 'text') {\n            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-text\" style=\"' . esc_attr($style . $borderStyle . $spacingStyle . 'text-align:' . (string) ($props['align'] ?? 'left') . ';') . '\">' . wpautop(wp_kses_post((string) ($props['text'] ?? ''))) . '</div>';\n        }",
    "        if ($type === 'text') {\n            $heading = trim((string) ($props['heading'] ?? ''));\n            $headingLevel = in_array((string) ($props['headingLevel'] ?? 'h2'), ['h2', 'h3', 'h4', 'h5', 'h6'], true) ? (string) $props['headingLevel'] : 'h2';\n            $headingHtml = $heading !== ''\n                ? '<' . $headingLevel . ' class=\"h18-clean-front-text-heading\">' . esc_html($heading) . '</' . $headingLevel . '>'\n                : '';\n            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-text\" style=\"' . esc_attr($style . $borderStyle . $spacingStyle . 'text-align:' . (string) ($props['align'] ?? 'left') . ';') . '\">' . $headingHtml . wpautop(wp_kses_post((string) ($props['text'] ?? ''))) . '</div>';\n        }"
)

# Editor normalize.
replace(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "            return Object.assign(common, {\n                text: String(raw.text || 'Ny tekst'),\n                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left'\n            });",
    "            return Object.assign(common, {\n                heading: String(raw.heading || ''),\n                headingLevel: ['h2', 'h3', 'h4', 'h5', 'h6'].includes(String(raw.headingLevel || '').toLowerCase()) ? String(raw.headingLevel).toLowerCase() : 'h2',\n                text: String(raw.text || 'Ny tekst'),\n                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left'\n            });"
)

# Editor canvas preview.
replace(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "            wrap.classList.add('h18-clean-node-preview--text');\n            wrap.style.textAlign = node.props.align || 'left';\n            wrap.textContent = String(node.props.text || 'Ny tekst').replace(/<[^>]+>/g, '').slice(0, 220) || 'Tekst';",
    "            wrap.classList.add('h18-clean-node-preview--text');\n            wrap.style.textAlign = node.props.align || 'left';\n            const heading = String(node.props.heading || '').trim();\n            if (heading) {\n                const headingLevel = ['h2', 'h3', 'h4', 'h5', 'h6'].includes(node.props.headingLevel) ? node.props.headingLevel : 'h2';\n                const title = document.createElement(headingLevel);\n                title.className = 'h18-clean-text-heading';\n                title.textContent = heading;\n                wrap.appendChild(title);\n            }\n            const body = document.createElement('div');\n            body.className = 'h18-clean-text-body';\n            body.textContent = String(node.props.text || 'Ny tekst').replace(/<[^>]+>/g, '').slice(0, 220) || 'Tekst';\n            wrap.appendChild(body);"
)

# Inspector fields.
replace(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "        if (node.type === 'text') {\n            html += '<label>Tekst<textarea data-field=\"text\" rows=\"8\">' + escapeHtml(node.props.text || '') + '</textarea></label>';\n            html += '<label>Justering<select data-field=\"align\"><option value=\"left\"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value=\"center\"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value=\"right\"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';",
    "        if (node.type === 'text') {\n            html += '<label>Overskrift <span class=\"description\">(valgfri)</span><input data-field=\"heading\" type=\"text\" value=\"' + escapeAttr(node.props.heading || '') + '\"></label>';\n            html += '<label>Overskrifttype<select data-field=\"headingLevel\"><option value=\"h2\"' + (node.props.headingLevel === 'h2' ? ' selected' : '') + '>H2</option><option value=\"h3\"' + (node.props.headingLevel === 'h3' ? ' selected' : '') + '>H3</option><option value=\"h4\"' + (node.props.headingLevel === 'h4' ? ' selected' : '') + '>H4</option><option value=\"h5\"' + (node.props.headingLevel === 'h5' ? ' selected' : '') + '>H5</option><option value=\"h6\"' + (node.props.headingLevel === 'h6' ? ' selected' : '') + '>H6</option></select></label>';\n            html += '<label>Tekst<textarea data-field=\"text\" rows=\"8\">' + escapeHtml(node.props.text || '') + '</textarea></label>';\n            html += '<label>Justering<select data-field=\"align\"><option value=\"left\"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value=\"center\"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value=\"right\"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';"
)

# Inspector mutations.
replace(
    'clean/hangar18-manager/assets/editor-v018-core.js',
    "                else if (field === 'text') { current.props.text = String(control.value || ''); }\n                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }",
    "                else if (field === 'heading') { current.props.heading = String(control.value || ''); }\n                else if (field === 'headingLevel') { current.props.headingLevel = ['h2', 'h3', 'h4', 'h5', 'h6'].includes(control.value) ? control.value : 'h2'; }\n                else if (field === 'text') { current.props.text = String(control.value || ''); }\n                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }"
)

(root / 'clean/hangar18-manager/assets/editor-v0117.css').write_text(
    ".h18-clean-node-preview--text .h18-clean-text-heading{margin:0 0 6px;font-size:1.25em;line-height:1.2;font-weight:700}\n"
    ".h18-clean-node-preview--text .h18-clean-text-body{min-height:1em}\n",
    encoding='utf-8'
)

(root / 'clean-release-notes.html').write_text(
    '<h4>0.1.17</h4><ul>'
    '<li>Tekst-elementet har nu en valgfri Overskrift i samme element.</li>'
    '<li>Overskrifttype kan vælges som H2-H6; standard er H2.</li>'
    '<li>Tom Overskrift giver kun brødtekst og ændrer ikke eksisterende layouts.</li>'
    '<li>Overskrift vises både på canvas, i usavet forhåndsvisning og på gemt frontend.</li>'
    '<li>Border, Afstand X/Y, resize og canonical geometri gælder fortsat for hele Tekst-elementet.</li>'
    '</ul>\n',
    encoding='utf-8'
)
