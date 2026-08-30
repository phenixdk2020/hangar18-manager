from pathlib import Path

HIERARCHY = Path('clean/hangar18-manager/src/Model/HierarchyNormalizer.php')

text = HIERARCHY.read_text(encoding='utf-8')
old = """            'gapX' => $gapX,
            'gapY' => $gapY,
        ];
"""
new = """            'gapX' => $gapX,
            'gapY' => $gapY,
            'offsetX' => 0,
            'offsetY' => 0,
        ];
"""
count = text.count(old)
if count != 1:
    raise SystemExit(f'neutral Section offset defaults: expected exactly 1 match, got {count}')
HIERARCHY.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Added canonical zero pixel offsets to migrated wrapper Sections.')
