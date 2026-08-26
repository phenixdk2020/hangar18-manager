from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def patch(path, old, new, expected=1):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f'{path}: expected {expected} matches for {old!r}, found {count}')
    target.write_text(text.replace(old, new), encoding='utf-8')


# Automatic system notes must not mark themselves as manually entered.
patch(
    'clean/hangar18-manager/assets/editor-v0123-ux.js',
    "if (userEntered) { userEntered.value = '1'; }",
    "if (userEntered) { userEntered.value = '0'; }",
)

# Augment automatic notes synchronously before form serialization, and never
# append system-generated detail to a note the administrator wrote manually.
patch(
    'clean/hangar18-manager/assets/editor-v0125.js',
    "    function augmentAutomaticNote() {\n        var input = document.getElementById('h18-clean-change-note');\n        if (!input) { return; }\n",
    "    function augmentAutomaticNote() {\n        var input = document.getElementById('h18-clean-change-note');\n        if (!input) { return; }\n        var userEntered = document.querySelector('[name=\"change_note_user_entered\"]');\n        if (userEntered && String(userEntered.value || '') === '1') { return; }\n",
)
patch(
    'clean/hangar18-manager/assets/editor-v0125.js',
    "                window.setTimeout(augmentAutomaticNote, 0);",
    "                augmentAutomaticNote();",
)

# Public naming cleanup must never rename internal CSS compatibility IDs.
patch(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    'h18-Visual Designer-version-actions',
    'h18-clean-version-actions',
)

# mbstring is not a declared plugin requirement. Preserve Unicode-aware
# truncation when available, with a safe PHP-core fallback.
patch(
    'clean/hangar18-manager/src/Model/TemplateLayoutModel.php',
    "return $name !== '' ? mb_substr($name, 0, 120) : $fallback;",
    "return $name !== '' ? (function_exists('mb_substr') ? mb_substr($name, 0, 120) : substr($name, 0, 120)) : $fallback;",
)

print('0.1.25 integration follow-up fixes applied.')
