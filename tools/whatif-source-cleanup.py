#!/usr/bin/env python3
"""Deterministically remove legacy WhatIf runtime from Hangar18 source.

The script is intentionally conservative: it only removes known markup/control
shapes and exact PHP WhatIf branches. It then refuses success while the word
WhatIf remains anywhere in the primary runtime files. Diagnostic/docs files are
outside that assertion by design.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Iterable

PRIMARY_PHP = pathlib.Path('hangar18-manager.php')
ADMIN_JS = pathlib.Path('assets/admin.js')
ADMIN_CSS = pathlib.Path('assets/admin.css')
BOOTSTRAP = pathlib.Path('src/Admin/IntegrationAdminBootstrap.php')
SHIM_FILES = [
    pathlib.Path('src/Admin/NoWhatIfAdminController.php'),
    pathlib.Path('assets/hangar18-no-whatif-v0858.js'),
    pathlib.Path('assets/hangar18-no-whatif-v0858.css'),
]

ACTIVE_PATTERN = re.compile(r'whatif', re.I)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding='utf-8')


def brace_delta(line: str) -> int:
    """Brace counter for the exact legacy PHP branches targeted here."""
    cleaned = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", '', line)
    return cleaned.count('{') - cleaned.count('}')


def remove_php_if_blocks(lines: list[str], patterns: Iterable[re.Pattern[str]]) -> tuple[list[str], int]:
    result: list[str] = []
    removed = 0
    i = 0
    patterns = list(patterns)
    while i < len(lines):
        line = lines[i]
        if any(p.search(line) for p in patterns):
            depth = brace_delta(line)
            if depth <= 0:
                raise RuntimeError(f'WhatIf branch did not open a block at line {i + 1}: {line.rstrip()}')
            removed += 1
            i += 1
            while i < len(lines) and depth > 0:
                depth += brace_delta(lines[i])
                i += 1
            if depth != 0:
                raise RuntimeError('Unbalanced braces while removing WhatIf branch')
            continue
        result.append(line)
        i += 1
    return result, removed


def remove_html_div_blocks(lines: list[str]) -> tuple[list[str], int]:
    result: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'h18-whatif-help' not in line.lower():
            result.append(line)
            i += 1
            continue
        if '<div' not in line.lower():
            result.append(line)
            i += 1
            continue
        depth = len(re.findall(r'<div\b', line, re.I)) - len(re.findall(r'</div\s*>', line, re.I))
        removed += 1
        i += 1
        while i < len(lines) and depth > 0:
            depth += len(re.findall(r'<div\b', lines[i], re.I))
            depth -= len(re.findall(r'</div\s*>', lines[i], re.I))
            i += 1
        if depth != 0:
            raise RuntimeError('Unbalanced HTML divs while removing h18-whatif-help')
    return result, removed


def clean_primary_php(text: str) -> tuple[str, dict[str, int]]:
    lines = text.splitlines(keepends=True)
    counts: dict[str, int] = {}

    safe_switch = re.compile(
        r'^\s*<label\s+class=["\']h18-safe-switch["\'][^\n]*name=["\']whatif["\'][^\n]*</label>\s*$',
        re.I,
    )
    before = len(lines)
    lines = [line for line in lines if not safe_switch.search(line)]
    counts['safe_switch_lines'] = before - len(lines)

    lines, removed_html = remove_html_div_blocks(lines)
    counts['help_blocks'] = removed_html

    assignment = re.compile(r"^\s*\$whatif\s*=\s*!empty\(\$_POST\[['\"]whatif['\"]\]\);\s*$", re.I)
    before = len(lines)
    lines = [line for line in lines if not assignment.search(line)]
    counts['assignments'] = before - len(lines)

    branch_patterns = [
        re.compile(r"^\s*if\s*\(\s*\$whatif\s*\)\s*\{\s*$", re.I),
        re.compile(r"^\s*if\s*\(\s*!empty\(\$_POST\[['\"]whatif['\"]\]\)\s*\)\s*\{\s*$", re.I),
    ]
    lines, branch_count = remove_php_if_blocks(lines, branch_patterns)
    counts['backend_branches'] = branch_count

    return ''.join(lines), counts


def clean_admin_js(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    patterns = [
        (
            r'''(?m)^\s*const \$pageWhatIf = \$pageEditorForm\.find\('\[name="whatif"\]'\);\s*\n''',
            '',
            'page_whatif_var',
        ),
        (
            r'''(?m)^\s*const whatIf = \$h18PageEditorFormV064\.find\('\[name="whatif"\]'\)\.is\(':checked'\);\s*\n''',
            '',
            'submit_whatif_var',
        ),
        (
            r'''h18EditorSetSaveStatusV064\(whatIf \? 'Simulerer…' : 'Gemmer…', 'saving'\);''',
            "h18EditorSetSaveStatusV064('Gemmer…', 'saving');",
            'submit_status',
        ),
    ]
    out = text
    for pattern, repl, name in patterns:
        out, count = re.subn(pattern, repl, out)
        counts[name] = count
    return out, counts


def clean_admin_css(text: str) -> tuple[str, dict[str, int]]:
    out = text
    counts: dict[str, int] = {}
    replacements = [
        (r'\.h18-safe-badge,\.h18-safe-switch\{', '.h18-safe-badge{', 'safe_switch_combined'),
        (r'\.h18-whatif-help,\.h18-action-submit\{', '.h18-action-submit{', 'combined_help_submit'),
        (r'\.h18-whatif-help\{[^{}]*\}', '', 'help_rule'),
        (r'\.h18-whatif-help label\{[^{}]*\}', '', 'help_label_rule'),
        (r'\.h18-whatif-help input\{[^{}]*\}', '', 'help_input_rule'),
    ]
    for pattern, repl, name in replacements:
        out, count = re.subn(pattern, repl, out)
        counts[name] = count
    return out, counts


def clean_bootstrap(text: str) -> tuple[str, int]:
    return re.subn(r'(?m)^\s*NoWhatIfAdminController::register\(\);\s*\n', '', text)


def active_hits(path: pathlib.Path, text: str) -> list[str]:
    return [
        f'{path.as_posix()}:{number}:{line.strip()}'
        for number, line in enumerate(text.splitlines(), start=1)
        if ACTIVE_PATTERN.search(line)
    ]


def assert_clean(root: pathlib.Path) -> list[str]:
    hits: list[str] = []
    for rel in [PRIMARY_PHP, ADMIN_JS, ADMIN_CSS, BOOTSTRAP]:
        path = root / rel
        if path.exists():
            hits.extend(active_hits(rel, read(path)))
    for rel in SHIM_FILES:
        if (root / rel).exists():
            hits.append(f'{rel.as_posix()}:legacy shim still exists')
    return hits


def apply(root: pathlib.Path) -> dict:
    report: dict[str, object] = {'schema_version': '1.1', 'changed': [], 'removed': []}

    php_path = root / PRIMARY_PHP
    php, php_counts = clean_primary_php(read(php_path))
    write(php_path, php)
    report['primary_php'] = php_counts
    report['changed'].append(PRIMARY_PHP.as_posix())

    js_path = root / ADMIN_JS
    js, js_counts = clean_admin_js(read(js_path))
    write(js_path, js)
    report['admin_js'] = js_counts
    report['changed'].append(ADMIN_JS.as_posix())

    css_path = root / ADMIN_CSS
    css, css_counts = clean_admin_css(read(css_path))
    write(css_path, css)
    report['admin_css'] = css_counts
    report['changed'].append(ADMIN_CSS.as_posix())

    bootstrap_path = root / BOOTSTRAP
    bootstrap, bootstrap_count = clean_bootstrap(read(bootstrap_path))
    write(bootstrap_path, bootstrap)
    report['bootstrap_registration_removed'] = bootstrap_count
    report['changed'].append(BOOTSTRAP.as_posix())

    for rel in SHIM_FILES:
        path = root / rel
        if path.exists():
            path.unlink()
            report['removed'].append(rel.as_posix())

    if php_counts['help_blocks'] < 1:
        raise RuntimeError('Expected at least one h18-whatif-help block')
    if php_counts['backend_branches'] < 1:
        raise RuntimeError('Expected at least one WhatIf backend branch')
    if bootstrap_count != 1:
        raise RuntimeError(f'Expected exactly one NoWhatIf registration, got {bootstrap_count}')
    if js_counts['submit_status'] != 1:
        raise RuntimeError(f"Expected one Page Editor WhatIf save status, got {js_counts['submit_status']}")

    hits = assert_clean(root)
    report['remaining_active_hits'] = hits
    if hits:
        raise RuntimeError('Active WhatIf runtime remains:\n' + '\n'.join(hits[:80]))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--assert-clean', action='store_true')
    parser.add_argument('--report')
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()

    try:
        if args.apply:
            report = apply(root)
        else:
            hits = assert_clean(root)
            report = {'schema_version': '1.1', 'remaining_active_hits': hits}
            if args.assert_clean and hits:
                raise RuntimeError('Active WhatIf runtime remains:\n' + '\n'.join(hits[:80]))
        payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.report:
            pathlib.Path(args.report).write_text(payload, encoding='utf-8')
        else:
            sys.stdout.write(payload)
        return 0
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
