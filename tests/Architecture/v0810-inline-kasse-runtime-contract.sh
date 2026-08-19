#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
test -f "$CTRL" || { echo "FAIL: missing $CTRL"; exit 1; }

require_text() {
  local needle="$1"
  local label="$2"
  if ! grep -F -- "$needle" "$CTRL" >/dev/null; then
    echo "FAIL: missing $label"
    echo "Needle: $needle"
    exit 1
  fi
}

require_text 'enqueueV0810KasseRuntime' 'v0.8.10 runtime method'
require_text "wp_add_inline_script('hangar18-ultimate-designer-box-content-layout'" 'inline JS binding to proven box-content handle'
require_text "wp_add_inline_style('hangar18-ultimate-designer-nesting-tools'" 'inline CSS binding to proven nesting handle'
require_text 'data-h18-v0810-kasse-runtime' 'runtime DOM marker'
require_text 'h18-v0810-child-source' 'hidden child-source class'
require_text 'h18-v0810-runtime-badge' 'visible v0.8.10 runtime badge'
require_text 'Sæt Kasse ved siden af' 'left/right Kasse side-drop copy'
require_text 'data-section-type="container"' 'ordinary Container palette recognition'
require_text 'data-section-type="grid"' 'existing Grid creation path'
require_text "var BOX='Kasse',AUTO='Auto-kasser'" 'Kasse/Auto-kasser runtime labels'
require_text 'setParent($t,gk);setParent($n,gk);' 'two-box grouping into one Grid parent'

if grep -F "'hangar18-ultimate-designer-visual-composition'" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.10 controller still references the separate visual-composition handle'
  exit 1
fi

cat > /tmp/h18-v0810-extract.php <<'PHP'
<?php
$source = file_get_contents('src/Admin/EditorLayoutToolsAdminController.php');
$marker = '$js = <<<' . "'JS'" . "\n";
$start = strpos($source, $marker);
if ($start === false) {
    fwrite(STDERR, "FAIL: inline JS block start not found\n");
    exit(1);
}
$start += strlen($marker);
$end = strpos($source, "\nJS;", $start);
if ($end === false) {
    fwrite(STDERR, "FAIL: inline JS block end not found\n");
    exit(1);
}
$js = substr($source, $start, $end - $start);
if ($js === '') {
    fwrite(STDERR, "FAIL: inline JS block is empty\n");
    exit(1);
}
file_put_contents('/tmp/h18-v0810-inline.js', $js);
echo 'Extracted v0.8.10 inline JS: ' . strlen($js) . " bytes\n";
PHP

php /tmp/h18-v0810-extract.php
node --check /tmp/h18-v0810-inline.js
php -l "$CTRL" >/dev/null

echo 'v0.8.10 inline Kasse runtime contract: PASS'
