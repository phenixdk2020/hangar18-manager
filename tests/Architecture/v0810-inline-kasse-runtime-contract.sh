#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
test -f "$CTRL" || { echo "FAIL: missing $CTRL"; exit 1; }

grep -F 'enqueueV0810KasseRuntime' "$CTRL" >/dev/null
grep -F "wp_add_inline_script('hangar18-ultimate-designer-box-content-layout'" "$CTRL" >/dev/null
grep -F "wp_add_inline_style('hangar18-ultimate-designer-nesting-tools'" "$CTRL" >/dev/null
grep -F 'data-h18-v0810-kasse-runtime' "$CTRL" >/dev/null
grep -F 'h18-v0810-child-source' "$CTRL" >/dev/null
grep -F 'h18-v0810-runtime-badge' "$CTRL" >/dev/null
grep -F 'Sæt Kasse ved siden af' "$CTRL" >/dev/null
grep -F 'data-section-type=\"container\"' "$CTRL" >/dev/null
grep -F 'data-section-type=\"grid\"' "$CTRL" >/dev/null
grep -F "var BOX='Kasse',AUTO='Auto-kasser'" "$CTRL" >/dev/null
grep -F 'setParent($t,gk);setParent($n,gk);' "$CTRL" >/dev/null

# v0.8.10 no longer depends on the separate v0.8.9 composition asset being
# enqueued. The behavior is attached to handles already proven active in Sider.
if grep -F "wp_enqueue_script(\n            'hangar18-ultimate-designer-visual-composition'" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.10 still enqueues the separate visual-composition JS'
  exit 1
fi

php -r '
$s=file_get_contents("src/Admin/EditorLayoutToolsAdminController.php");
if(!preg_match("/\\$js = <<<'\''JS'\''\\n(.*?)\\nJS;/s",$s,$m)){fwrite(STDERR,"FAIL: inline JS block not found\n");exit(1);} 
file_put_contents("/tmp/h18-v0810-inline.js",$m[1]);
'
node --check /tmp/h18-v0810-inline.js
php -l "$CTRL" >/dev/null

echo 'v0.8.10 inline Kasse runtime contract: PASS'
