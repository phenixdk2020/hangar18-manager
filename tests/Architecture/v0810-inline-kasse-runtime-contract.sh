#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
NEST='assets/ultimate-designer-nesting-tools.js'
for file in "$CTRL" "$NEST"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# v0.8.10 is historical only. It must not be enqueued beside the direct runtime.
if grep -F 'self::enqueueV0810KasseRuntime();' "$CTRL" >/dev/null; then
  echo 'FAIL: obsolete v0.8.10 inline Kasse runtime is still active'
  exit 1
fi
if grep -F 'data-h18-v0810-kasse-runtime' "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.10 runtime payload still lives in the active controller'
  exit 1
fi
if grep -F "wp_add_inline_script('hangar18-ultimate-designer-box-content-layout'" "$CTRL" >/dev/null; then
  echo 'FAIL: obsolete Kasse placement JS is still attached to box-content-layout'
  exit 1
fi

# The successor remains the single LayoutParentKey-based Kasse composer.
grep -F 'data-h18-v0813-kasse-runtime' "$NEST" >/dev/null
grep -F "const BOX_LABEL = 'Kasse';" "$NEST" >/dev/null
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$NEST" >/dev/null
grep -F '.h18-layout-parent-key' "$NEST" >/dev/null
grep -F 'function placeBoxBeside($source, $target, side)' "$NEST" >/dev/null

php -l "$CTRL" >/dev/null
node --check "$NEST"
echo 'v0.8.10 inline Kasse runtime retirement contract: PASS'
