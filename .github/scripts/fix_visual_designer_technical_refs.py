#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REPLACEMENTS = {
    'docs/Visual Designer-backlog-v0120.md': 'docs/clean-backlog-v0120.md',
    'Visual Designer-update.json': 'clean-update.json',
    'Visual Designer-release-notes.html': 'clean-release-notes.html',
    'Visual Designer-release-now.txt': 'clean-release-now.txt',
    'Visual Designer-artifact-now.txt': 'clean-artifact-now.txt',
    'Visual Designer/hangar18-manager/': 'clean/hangar18-manager/',
}

FILES = [
    'CLEAN-DESIGN-MANUAL.md',
    'CLEAN-USER-MANUAL.md',
    'docs/CLEAN-HANDOVER.md',
    'docs/clean-backlog-v0120.md',
    'docs/PRODUCT-NAMING.md',
    'docs/HEADER-FOOTER-SPEC.md',
    'docs/PARALLEL-MANAGER-WORK.md',
    'docs/EXPORT-SPEC.md',
]

for rel in FILES:
    path = ROOT / rel
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    original = text
    for wrong, right in REPLACEMENTS.items():
        text = text.replace(wrong, right)
    if text != original:
        path.write_text(text, encoding='utf-8')
        print(f'fixed technical references: {rel}')

# Hard gate: these names are not files and must never appear after the public rename.
for rel in FILES:
    path = ROOT / rel
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    for wrong in REPLACEMENTS:
        if wrong in text:
            raise SystemExit(f'{rel}: invalid renamed technical reference remains: {wrong}')

print('Technical reference QA PASS')
