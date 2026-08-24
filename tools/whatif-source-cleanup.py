#!/usr/bin/env python3
"""Deterministically remove legacy WhatIf runtime from Hangar18 source.

The migration is fail-closed. Pure WhatIf UI blocks are removed, while legacy
wrappers that also contain real controls are preserved under a neutral class.
After mutation the primary runtime must contain zero case-insensitive WhatIf
references and the compatibility shim files must be gone.
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
NAME_PATTERN = re.compile(r'name\s*=\s*["\']([^"\']+)["\']', re.I)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding='utf-8')


def brace_delta(line: str) -> int:
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


def collect_html_block(lines: list[str], start: int, tag: str) -> tuple[list[str], int]:
    block: list[str] = []
    depth = 0
    i = start
    open_re = re.compile(r'<' + re.escape(tag) + r'\b', re.I)
    close_re = re.compile(r'</' + re.escape(tag) + r'\s*>', re.I)
    while i < len(lines):
        line = lines[i]
        block.append(line)
        depth += len(open_re.findall(line)) - len(close_re.findall(line))
        i += 1
        if depth <= 0:
            return block, i
    raise RuntimeError(f'Unbalanced HTML <{tag}> block starting at line {start + 1}')


def non_whatif_names(text: str) -> list[str]:
    return [name for name in NAME_PATTERN.findall(text) if name.lower() != 'whatif']


def clean_help_wrappers(lines: list[str]) -> tuple[list[str], int, int]:
    """Remove pure simulation help; preserve mixed blocks such as Pin menu."""
    result: list[str] = []
    removed = 0
    preserved = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'h18-whatif-help' not in line.lower() or '<div' not in line.lower():
            result.append(line)
            i += 1
            continue
        block, i = collect_html_block(lines, i, 'div')
        text = ''.join(block)
        if non_whatif_names(text):
            block[0] = re.sub(r'h18-whatif-help', 'h18-action-options', block[0], flags=re.I)
            result.extend(block)
            preserved += 1
        else:
            removed += 1
    return result, removed, preserved


def clean_safe_switch_labels(lines: list[str]) -> tuple[list[str], int]:
    """Remove only safe-switch labels whose control is the WhatIf checkbox."""
    result: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'h18-safe-switch' not in line.lower() or '<label' not in line.lower():
            result.append(line)
            i += 1
            continue
        block, i = collect_html_block(lines, i, 'label')
        text = ''.join(block)
        names = NAME_PATTERN.findall(text)
        has_whatif = any(name.lower() == 'whatif' for name in names)
        has_other = any(name.lower() != 'whatif' for name in names)
        if has_whatif and not has_other:
            removed += 1
            continue
        result.extend(block)
    return result, removed


def clean_primary_php(text: str) -> tuple[str, dict[str, int]]:
    lines = text.splitlines(keepends=True)
    counts: dict[str, int] = {}

    lines, removed_help, preserved_help = clean_help_wrappers(lines)
    counts['help_blocks_removed'] = removed_help
    counts['mixed_help_blocks_preserved'] = preserved_help

    lines, safe_switches = clean_safe_switch_labels(lines)
    counts['whatif_safe_switches_removed'] = safe_switches

    # Handles isolated menu/action checkboxes outside the old help wrapper.
    whatif_input = re.compile(r'^\s*.*<input\b[^>]*name=["\']whatif["\'][^>]*>.*$', re.I)
    before = len(lines)
    lines = [line for line in lines if not whatif_input.search(line)]
    counts['standalone_input_lines_removed'] = before - len(lines)

    assignment = re.compile(r"^\s*\$whatif\s*=\s*!empty\(\$_POST\[['\"]whatif['\"]\]\);\s*$", re.I)
    before = len(lines)
    lines = [line for line in lines if not assignment.search(line)]
    counts['assignments_removed'] = before - len(lines)

    branch_patterns = [
        re.compile(r"^\s*if\s*\(\s*\$whatif\s*\)\s*\{\s*$", re.I),
        re.compile(r"^\s*if\s*\(\s*!empty\(\$_POST\[['\"]whatif['\"]\]\)\s*\)\s*\{\s*$", re.I),
    ]
    lines, branch_count = remove_php_if_blocks(lines, branch_patterns)
    counts['backend_branches_removed'] = branch_count

    out = ''.join(lines)
    legacy_copy = [
        ('WhatIf er FRA som standard', 'Ændringer gemmes kun ved en eksplicit Gem-handling'),
        ('Web-managerens checkpoints, WhatIf, fejl og succeser.', 'Web-managerens checkpoints, fejl og succeser.'),
        ('Vælg et eksisterende køretøj eller opret et nyt. WhatIf er slået fra som standard.', 'Vælg et eksisterende køretøj eller opret et nyt.'),
        ('Hver rigtig gemning får sit eget versionsnummer og en beskrivelse. WhatIf opretter ingen historik.', 'Hver gemning får sit eget versionsnummer og en beskrivelse.'),
        ('Først når WhatIf slås fra og du trykker <strong>Gem menu</strong>,', 'Når du trykker <strong>Gem menu</strong>,'),
    ]
    copy_count = 0
    for old, new in legacy_copy:
        hits = out.count(old)
        out = out.replace(old, new)
        copy_count += hits
    counts['legacy_copy_rewritten'] = copy_count

    return out, counts


def clean_admin_js(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    patterns = [
        (
            r'''(?m)^\s*const \$pageWhatIf = \$pageEditorForm\.find\('\[name="whatif"\]'\);\s*\n''',
            '',
            'page_whatif_var_removed',
        ),
        (
            r'''(?m)^\s*\$pageWhatIf\.on\('change',\s*syncPageChangeNoteRequirement\);\s*\n''',
            '',
            'page_whatif_change_handler_removed',
        ),
        (
            r'''editorDraftSaveNow\(!\$pageWhatIf\.is\(':checked'\)\);''',
            'editorDraftSaveNow(true);',
            'draft_save_rewritten',
        ),
        (
            r'''(?m)^\s*const whatIf = \$h18PageEditorFormV064\.find\('\[name="whatif"\]'\)\.is\(':checked'\);\s*\n''',
            '',
            'submit_whatif_var_removed',
        ),
        (
            r'''h18EditorSetSaveStatusV064\(whatIf \? 'Simulerer…' : 'Gemmer…', 'saving'\);''',
            "h18EditorSetSaveStatusV064('Gemmer…', 'saving');",
            'submit_status_rewritten',
        ),
    ]
    out = text
    for pattern, repl, name in patterns:
        out, count = re.subn(pattern, repl, out)
        counts[name] = count
    return out, counts


def clean_admin_css(text: str) -> tuple[str, dict[str, int]]:
    """Rename the old wrapper styling for the real controls we preserve."""
    out = text
    counts: dict[str, int] = {}
    replacements = [
        (r'\.h18-whatif-help,\.h18-action-submit\{', '.h18-action-options,.h18-action-submit{', 'combined_wrapper_renamed'),
        (r'\.h18-whatif-help\{', '.h18-action-options{', 'wrapper_rule_renamed'),
        (r'\.h18-whatif-help label\{', '.h18-action-options label{', 'wrapper_label_rule_renamed'),
        (r'\.h18-whatif-help input\{', '.h18-action-options input{', 'wrapper_input_rule_renamed'),
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
    pre_hits = assert_clean(root)
    if not pre_hits:
        return {
            'schema_version': '1.5',
            'already_clean': True,
            'changed': [],
            'removed': [],
            'remaining_active_hits': [],
        }

    report: dict[str, object] = {
        'schema_version': '1.5',
        'already_clean': False,
        'pre_cleanup_hit_count': len(pre_hits),
        'changed': [],
        'removed': [],
    }

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

    if php_counts['help_blocks_removed'] < 1:
        raise RuntimeError('Expected at least one pure h18-whatif-help block')
    if php_counts['whatif_safe_switches_removed'] < 1:
        raise RuntimeError('Expected at least one WhatIf safe-switch label')
    if php_counts['standalone_input_lines_removed'] < 1:
        raise RuntimeError('Expected at least one standalone WhatIf input line')
    if php_counts['backend_branches_removed'] < 1:
        raise RuntimeError('Expected at least one WhatIf backend branch')
    if php_counts['legacy_copy_rewritten'] < 5:
        raise RuntimeError(f"Expected at least five legacy WhatIf copy rewrites, got {php_counts['legacy_copy_rewritten']}")
    if bootstrap_count != 1:
        raise RuntimeError(f'Expected exactly one NoWhatIf registration, got {bootstrap_count}')
    if js_counts['page_whatif_change_handler_removed'] != 1:
        raise RuntimeError(f"Expected one Page Editor WhatIf change handler, got {js_counts['page_whatif_change_handler_removed']}")
    if js_counts['draft_save_rewritten'] != 1:
        raise RuntimeError(f"Expected one WhatIf-gated draft save, got {js_counts['draft_save_rewritten']}")
    if js_counts['submit_status_rewritten'] != 1:
        raise RuntimeError(f"Expected one Page Editor WhatIf save status, got {js_counts['submit_status_rewritten']}")

    hits = assert_clean(root)
    report['remaining_active_hits'] = hits
    if hits:
        raise RuntimeError('Active WhatIf runtime remains:\n' + '\n'.join(hits[:120]))
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
            report = {'schema_version': '1.5', 'remaining_active_hits': hits}
            if args.assert_clean and hits:
                raise RuntimeError('Active WhatIf runtime remains:\n' + '\n'.join(hits[:120]))
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
