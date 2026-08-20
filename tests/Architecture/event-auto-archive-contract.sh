#!/usr/bin/env bash
set -euo pipefail

RUNTIME='src/Event/EventArchiveRuntime.php'
AUTOLOAD='src/Autoload.php'
SMOKE='tests/Architecture/event-auto-archive-smoke.php'

for file in "$RUNTIME" "$AUTOLOAD" "$SMOKE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

grep -F "add_filter('the_content'" "$RUNTIME" >/dev/null
grep -F "private const EVENT_PARENT_SLUG = 'events';" "$RUNTIME" >/dev/null
grep -F "private const EVENT_MARKER = 'HANGAR18-EVENT-DATA';" "$RUNTIME" >/dev/null
grep -F "current_time('Y-m-d')" "$RUNTIME" >/dev/null
grep -F "current_time('H:i')" "$RUNTIME" >/dev/null
grep -F 'if ($endTime ===' "$RUNTIME" >/dev/null
grep -F 'return $endTime <=' "$RUNTIME" >/dev/null
grep -F "eventskabelon" "$RUNTIME" >/dev/null
grep -F "EventArchiveRuntime::register();" "$AUTOLOAD" >/dev/null

grep -F "Today event must archive once explicit EndTime has passed." "$SMOKE" >/dev/null
grep -F "Event without EndTime must stay upcoming for the rest of its date." "$SMOKE" >/dev/null

# Render-time reclassification must never persist, save or mutate Events/pages.
if grep -Ei 'wp_update_post\s*\(|wp_insert_post\s*\(|update_option\s*\(|delete_option\s*\(|update_post_meta\s*\(|delete_post_meta\s*\(|file_put_contents\s*\(|admin_post_|wp_ajax_' "$RUNTIME" >/dev/null; then
  echo 'FAIL: EVENT-001 introduced persistence/mutation in frontend runtime'
  exit 1
fi

php -l "$RUNTIME" >/dev/null
php -l "$SMOKE" >/dev/null
php "$SMOKE"
echo 'EVENT-001 automatic archive contract: PASS'
