#!/usr/bin/env python3
"""Read-only repository audit for Hangar18 WhatIf/legacy cleanup."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

RUNTIME_EXTENSIONS = {'.php', '.js', '.css'}
IGNORE_DIRS = {'.git', 'build', 'dist', 'node_modules', '__pycache__'}
BOOTSTRAP_RE = re.compile(r'(?:vehicleregister|vehicle[-_ ]?register|bootstrap).*\.json$', re.I)
WHATIF_RE = re.compile(r'whatif', re.I)
SHIM_NAMES = {'NoWhatIfAdminController.php', 'hangar18-no-whatif-v0858.js', 'hangar18-no-whatif-v0858.css'}


def iter_files(root: pathlib.Path):
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        yield path


def audit(root: pathlib.Path) -> dict:
    powershell: list[str] = []
    bootstrap: list[str] = []
    whatif_files: list[dict] = []
    shim: list[str] = []

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix == '.ps1':
            powershell.append(rel)
        if BOOTSTRAP_RE.search(path.name):
            bootstrap.append(rel)
        if path.name in SHIM_NAMES:
            shim.append(rel)
        if suffix not in RUNTIME_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        count = len(WHATIF_RE.findall(text))
        if count:
            whatif_files.append({'path': rel, 'matches': count, 'shim': path.name in SHIM_NAMES})

    runtime_nonshim = [entry for entry in whatif_files if not entry['shim']]
    return {
        'schema_version': '1.0',
        'powershell_count': len(powershell),
        'powershell': sorted(powershell),
        'bootstrap_json_count': len(bootstrap),
        'bootstrap_json': sorted(bootstrap),
        'whatif_runtime_file_count': len(whatif_files),
        'whatif_runtime_matches': sum(entry['matches'] for entry in whatif_files),
        'whatif_nonshim_file_count': len(runtime_nonshim),
        'whatif_nonshim_matches': sum(entry['matches'] for entry in runtime_nonshim),
        'whatif_files': sorted(whatif_files, key=lambda item: item['path']),
        'shim_files': sorted(shim),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--output')
    parser.add_argument('--require-no-powershell', action='store_true')
    parser.add_argument('--require-no-bootstrap-json', action='store_true')
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    result = audit(root)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        pathlib.Path(args.output).write_text(payload, encoding='utf-8')
    else:
        sys.stdout.write(payload)

    errors: list[str] = []
    if args.require_no_powershell and result['powershell_count']:
        errors.append(f"PowerShell artifacts found: {result['powershell']}")
    if args.require_no_bootstrap_json and result['bootstrap_json_count']:
        errors.append(f"Legacy bootstrap JSON artifacts found: {result['bootstrap_json']}")
    for error in errors:
        print('ERROR: ' + error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
