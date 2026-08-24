#!/usr/bin/env python3
"""Build a conservative reference graph for Hangar18 legacy/migration code.

A class is never deleted by this tool. It reports external references and marks
only definition-only classes as review candidates. It also inventories the old
admin_init repair hooks in hangar18-manager.php so LEGACY-007/008 remain tied to
explicit migration evidence rather than filename/version heuristics.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass

CLASS_RE = re.compile(r'\b(?:(?:final|abstract)\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\b')
INTEREST_RE = re.compile(r'(Legacy|Migration|Import|Conversion|Shadow)', re.I)
ADMIN_INIT_REPAIR_RE = re.compile(
    r"add_action\(\s*['\"]admin_init['\"]\s*,\s*\[\s*\$this\s*,\s*['\"]([^'\"]+)['\"]\s*\]\s*,\s*(\d+)\s*\)",
    re.M,
)
REPAIR_NAME_RE = re.compile(r'(repair|cleanup|restore|migration|import)', re.I)
OPTION_CONST_RE = re.compile(
    r"const\s+([A-Z0-9_]*(?:REPAIR|CLEANUP|IMPORT|BASELINE)[A-Z0-9_]*)\s*=\s*['\"]([^'\"]+)['\"]\s*;",
    re.I,
)
IGNORE_DIRS = {'.git', 'build', 'dist', 'node_modules', '__pycache__'}
ACTIVE_EXPECTED = {
    'LegacyShellShadowAdminController',
    'LegacyShellSnapshotService',
    'ConversionAdminController',
}


@dataclass(frozen=True)
class Definition:
    name: str
    path: pathlib.Path
    line: int


def php_files(root: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    main = root / 'hangar18-manager.php'
    if main.is_file():
        files.append(main)
    src = root / 'src'
    if src.is_dir():
        for path in src.rglob('*.php'):
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def line_number(text: str, offset: int) -> int:
    return text.count('\n', 0, offset) + 1


def build(root: pathlib.Path) -> dict:
    files = php_files(root)
    texts = {path: path.read_text(encoding='utf-8') for path in files}
    definitions: list[Definition] = []

    for path, text in texts.items():
        for match in CLASS_RE.finditer(text):
            name = match.group(1)
            if INTEREST_RE.search(name):
                definitions.append(Definition(name, path, line_number(text, match.start())))

    classes: list[dict] = []
    for definition in sorted(definitions, key=lambda item: (item.name.lower(), item.path.as_posix())):
        token_re = re.compile(r'\b' + re.escape(definition.name) + r'\b')
        refs: list[dict] = []
        for path, text in texts.items():
            for match in token_re.finditer(text):
                line = line_number(text, match.start())
                if path == definition.path and line == definition.line:
                    continue
                refs.append({
                    'path': path.relative_to(root).as_posix(),
                    'line': line,
                })
        external = [ref for ref in refs if ref['path'] != definition.path.relative_to(root).as_posix()]
        status = 'active-reference' if external else 'definition-only-review-candidate'
        classes.append({
            'class': definition.name,
            'definition': {
                'path': definition.path.relative_to(root).as_posix(),
                'line': definition.line,
            },
            'reference_count': len(refs),
            'external_reference_count': len(external),
            'references': refs,
            'status': status,
            'expected_active': definition.name in ACTIVE_EXPECTED,
        })

    missing_expected = [
        name for name in sorted(ACTIVE_EXPECTED)
        if not any(row['class'] == name and row['external_reference_count'] > 0 for row in classes)
    ]

    main_path = root / 'hangar18-manager.php'
    main = main_path.read_text(encoding='utf-8') if main_path.is_file() else ''
    repair_hooks = []
    for match in ADMIN_INIT_REPAIR_RE.finditer(main):
        method = match.group(1)
        if not REPAIR_NAME_RE.search(method):
            continue
        repair_hooks.append({
            'method': method,
            'priority': int(match.group(2)),
            'line': line_number(main, match.start()),
            'status': 'one-time-hook-live-evidence-required',
        })

    migration_options = [
        {'constant': match.group(1), 'option': match.group(2), 'line': line_number(main, match.start())}
        for match in OPTION_CONST_RE.finditer(main)
    ]

    return {
        'schema_version': '1.0',
        'php_file_count': len(files),
        'class_count': len(classes),
        'definition_only_candidate_count': sum(row['status'] == 'definition-only-review-candidate' for row in classes),
        'classes': classes,
        'expected_active_missing_references': missing_expected,
        'admin_init_repair_hooks': repair_hooks,
        'migration_option_constants': migration_options,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--output')
    parser.add_argument('--require-expected-active', action='store_true')
    args = parser.parse_args()

    try:
        report = build(pathlib.Path(args.root).resolve())
        payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            pathlib.Path(args.output).write_text(payload, encoding='utf-8')
        else:
            sys.stdout.write(payload)
        if args.require_expected_active and report['expected_active_missing_references']:
            raise RuntimeError(
                'Expected active legacy classes lost references: ' +
                ', '.join(report['expected_active_missing_references'])
            )
        return 0
    except Exception as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
