#!/usr/bin/env python3
"""Classify Hangar18 backlog files as canonical or historical snapshots."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

POINTER_RE = re.compile(r"^\*\*Canonical backlog:\*\*\s+`([^`]+)`\s*$", re.M)
VERSION_RE = re.compile(r"active-backlog-v(\d+)\.md$", re.I)


def version_key(path: pathlib.Path) -> int:
    match = VERSION_RE.search(path.name)
    if not match:
        raise ValueError(f'not a versioned backlog: {path}')
    return int(match.group(1))


def build(root: pathlib.Path, pointer_path: pathlib.Path) -> dict:
    pointer = pointer_path.read_text(encoding='utf-8')
    match = POINTER_RE.search(pointer)
    if not match:
        raise RuntimeError('BACKLOG-CANONICAL.md mangler en Canonical backlog pointer.')

    canonical_rel = pathlib.Path(match.group(1))
    canonical = root / canonical_rel
    if not canonical.is_file():
        raise RuntimeError(f'Canonical backlog findes ikke: {canonical_rel.as_posix()}')

    files = sorted((root / 'docs').glob('active-backlog-v*.md'), key=version_key)
    if not files:
        raise RuntimeError('Ingen active-backlog-v*.md filer fundet.')
    latest = max(files, key=version_key)
    if canonical.resolve() != latest.resolve():
        raise RuntimeError(
            'Canonical pointer er ikke højeste backlogversion: '
            f'{canonical_rel.as_posix()} vs {latest.relative_to(root).as_posix()}'
        )

    entries = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        is_canonical = path.resolve() == canonical.resolve()
        entries.append({
            'path': rel,
            'version_key': version_key(path),
            'role': 'canonical' if is_canonical else 'historical_snapshot',
            'historical_snapshot': not is_canonical,
        })

    return {
        'schema_version': '1.0',
        'canonical_backlog': canonical_rel.as_posix(),
        'file_count': len(entries),
        'historical_snapshot_count': sum(1 for entry in entries if entry['historical_snapshot']),
        'entries': entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--pointer', default='docs/BACKLOG-CANONICAL.md')
    parser.add_argument('--output')
    args = parser.parse_args()

    try:
        root = pathlib.Path(args.root).resolve()
        pointer = root / args.pointer
        report = build(root, pointer)
        payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            pathlib.Path(args.output).write_text(payload, encoding='utf-8')
        else:
            sys.stdout.write(payload)
        return 0
    except Exception as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
