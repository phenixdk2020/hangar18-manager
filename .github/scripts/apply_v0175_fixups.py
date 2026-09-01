from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit(f'Missing file: {rel}')
    return p.read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    (ROOT / rel).write_text(value, encoding='utf-8')

# The primary apply script first extends the allowed type list. Ensure the
# corresponding canonical form props block is also present after that change.
layout_rel = 'clean/hangar18-manager/src/Model/LayoutModel.php'
layout = read(layout_rel)
form_block = r'''        if (in_array($type, ['contactform', 'membershipform'], true)) {
            $membership = $type === 'membershipform';
            return array_merge([
                'heading' => sanitize_text_field((string) ($raw['heading'] ?? ($membership ? 'Bliv medlem' : 'Kontakt os'))),
                'intro' => sanitize_textarea_field((string) ($raw['intro'] ?? ($membership ? 'Udfyld formularen, så kontakter vi dig om medlemskab.' : 'Har du spørgsmål, er du velkommen til at kontakte os.'))),
                'buttonText' => sanitize_text_field((string) ($raw['buttonText'] ?? ($membership ? 'Send indmeldelse' : 'Send besked'))),
                'recipient' => sanitize_email((string) ($raw['recipient'] ?? '')),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#f4f1e8')) ?: '#f4f1e8',
                'fieldBackground' => sanitize_hex_color((string) ($raw['fieldBackground'] ?? '#ffffff')) ?: '#ffffff',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#30382a')) ?: '#30382a',
                'padding' => self::clamp($raw['padding'] ?? 24, 0, 80, 24),
                'radius' => self::clamp($raw['radius'] ?? 6, 0, 60, 6),
                'showPhone' => array_key_exists('showPhone', $raw) ? (bool) $raw['showPhone'] : true,
                'requireConsent' => array_key_exists('requireConsent', $raw) ? (bool) $raw['requireConsent'] : true,
            ], $border);
        }
'''
if "if (in_array($type, ['contactform', 'membershipform'], true))" not in layout:
    marker = "        if ($type === 'image') {"
    pos = layout.find(marker)
    if pos < 0:
        raise SystemExit('LayoutModel image marker missing')
    layout = layout[:pos] + form_block + layout[pos:]
    write(layout_rel, layout)

# The first apply inserts the two new JS branches at a shared `} else if
# (image)` marker. Normalize the branch boundary before syntax QA.
js_rel = 'clean/hangar18-manager/assets/editor-v018-core.js'
js = read(js_rel)
js = js.replace("\n else if (node.type === 'image') {", "\n        } else if (node.type === 'image') {")
write(js_rel, js)

print('Applied v0.1.75 post-patch fixups.')
